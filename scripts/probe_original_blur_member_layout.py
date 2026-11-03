"""Private original Blur member-layout observations; never a binding implementation.

m_Index values are published only as numeric serialized observations. The byte
offset model below is explicitly a hypothesis, not evidence of GPU semantics.
"""
import argparse
import hashlib
import json
from pathlib import Path


def observe(common):
    """Bounded known-schema observation without publishing original identifiers."""
    buffers = common["m_ConstantBuffers"]
    bindings = common["m_ConstantBufferBindings"]
    if not isinstance(buffers, list) or not isinstance(bindings, list):
        raise ValueError("schema")
    slots = {}
    for binding in bindings:
        name, slot = binding["m_NameIndex"], binding["m_Index"]
        if type(name) is not int or type(slot) is not int or slot < 0 or name in slots or slot in slots.values():
            raise ValueError("binding")
        slots[name] = slot
    result = []
    seen = set()
    for cb in buffers:
        name, size = cb["m_NameIndex"], cb["m_Size"]
        if name not in slots or name in seen or type(size) is not int or size <= 0:
            raise ValueError("buffer")
        seen.add(name)
        members = []
        for field, kind, dim_field in (("m_MatrixParams", "matrix", "m_RowCount"),
                                       ("m_VectorParams", "vector", "m_Dim")):
            for member in cb[field]:
                index, array, typ, dim = (member[k] for k in ("m_Index", "m_ArraySize", "m_Type", dim_field))
                if any(type(v) is not int for v in (index, array, typ, dim)):
                    raise ValueError("member_schema")
                if index < 0 or array < 0 or not 1 <= dim <= 4:
                    raise ValueError("member_range")
                # Candidate interpretation only: 32-bit scalar/vector lanes,
                # matrix rows 16 bytes, array register stride 16 bytes.
                span = (16 * dim if kind == "matrix" else 4 * dim)
                if array:
                    span = (16 * dim if kind == "matrix" else 16) * array
                members.append({"kind": kind, "serialized_index": index,
                                "serialized_array_size": array, "serialized_type": typ,
                                "serialized_dimension": dim,
                                "candidate_byte_end": index + span,
                                "candidate_within_allocation": index + span <= size})
        structs = cb["m_StructParams"]
        if not isinstance(structs, list):
            raise ValueError("struct_schema")
        ordered = sorted(members, key=lambda m: m["serialized_index"])
        overlaps = sum(a["candidate_byte_end"] > b["serialized_index"] for a, b in zip(ordered, ordered[1:]))
        result.append({"slot": slots[name], "allocation_bytes": size,
                       "serialized_partial_cb": cb.get("m_IsPartialCB"),
                       "members": ordered, "struct_count": len(structs),
                       "candidate_overlapping_adjacent_members": overlaps,
                       "candidate_byte_offset_model_verified": False})
    if set(slots) != seen:
        raise ValueError("unmatched_binding")
    return sorted(result, key=lambda cb: cb["slot"])


def main(source, repo, out):
    from scripts.a12_probe_original_blur_passes import original_shader
    from scripts.w1_recover_depth_passes import stage_variants, linked_program
    from scripts.w1_recover_graphics_programs import decoded_platforms, records
    from scripts.a12r_dx11_cb_declarations import declarations
    report = {"status": "blocked", "original_verified": False,
              "runtime_or_shaderlab_verified": False, "private_names_published": False}
    phase = "source"
    try:
        _, digest, tree = original_shader(source, repo)
        if digest != "c9341848367eaedb12e551ce9061b1eea728f54f2069ef1a3c12c4a4a2e9bb52":
            raise ValueError("fingerprint")
        report["original_verified"] = True
        tables = [records(p) for code, p in decoded_platforms(tree) if code == 4]
        if len(tables) != 1:
            raise ValueError("platform")
        rows = []
        phase = "member_observation"
        passes = tree["m_ParsedForm"]["m_SubShaders"][0]["m_Passes"]
        if len(passes) != 2:
            raise ValueError("topology")
        for pi, p in enumerate(passes):
            for field, st in (("progVertex", 1), ("progFragment", 0)):
                program = p[field]
                variants = stage_variants(program)
                if len(variants) != 1:
                    raise ValueError("variants")
                _, _, meta = variants[0]
                code, _ = linked_program(meta, tables[0], st)
                layout = observe(program["m_CommonParameters"])
                compiled = declarations(code)
                for cb in layout:
                    cb["compiled_declared_bytes"] = compiled.get(cb["slot"])
                    for m in cb["members"]:
                        m["candidate_within_compiled_span"] = (
                            cb["compiled_declared_bytes"] is not None
                            and m["candidate_byte_end"] <= cb["compiled_declared_bytes"])
                rows.append({"pass": pi, "stage": st, "buffers": layout})
        report.update(status="observed", stages=rows, original_object_sha256=digest,
                      member_semantics_verified=False,
                      original_member_layout_preserved=True)
    except Exception as error:
        report.update(failure_phase=phase, failure_type=type(error).__name__)
    out.write_text(json.dumps(report, sort_keys=True) + "\n")
    print("RAFT_BLUR_MEMBER_LAYOUT " + json.dumps(report, sort_keys=True))
    if report["status"] != "observed":
        raise ValueError("private original member observation blocked")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    main(args.source, args.repo, args.out)
