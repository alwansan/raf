"""A12R independent DXBC RDEF CB audit. Private source names never published."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from scripts.a12_probe_original_blur_passes import original_shader, inspect_shader
from scripts.a12_shader_parameter_decode import parse_parameter_blob
from scripts.w1_recover_depth_passes import linked_program, stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.a12r_dx11_cb_declarations import declarations as dxbc_cb_declarations

def u(b, p):
    if p < 0 or p + 4 > len(b):
        raise ValueError("truncated original reflection")
    return struct.unpack_from("<I", b, p)[0]

def name(b, at, floor):
    if at < floor or at >= len(b):
        raise ValueError("invalid private string")
    end = b.find(b"\0", at, min(at + 256, len(b)))
    if end <= at:
        raise ValueError("invalid private string")
    return b[at:end].decode("utf-8")

def rdef(code):
    if len(code) < 40 or code[:4] != b"DXBC" or u(code, 24) != len(code):
        raise ValueError("invalid DXBC container")
    count = u(code, 28)
    if not 1 <= count <= 128 or 32 + count * 4 > len(code):
        raise ValueError("invalid DXBC chunk table")
    chunks = []
    for n in range(count):
        pos = u(code, 32 + n * 4)
        if pos < 32 + count * 4 or pos + 8 > len(code) or pos + 8 + u(code, pos + 4) > len(code):
            raise ValueError("invalid DXBC chunk range")
        if code[pos:pos + 4] == b"RDEF":
            chunks.append(code[pos + 8:pos + 8 + u(code, pos + 4)])
    if len(chunks) != 1 or len(chunks[0]) < 28:
        raise ValueError("missing unique original RDEF")
    body = chunks[0]
    cb_count, cb_off, bound_count, bound_off = struct.unpack_from("<4I", body, 0)
    if cb_count > 64 or bound_count > 256 or cb_off + cb_count * 24 > len(body) or bound_off + bound_count * 32 > len(body):
        raise ValueError("RDEF table bounds")
    floor = max(28, cb_off + cb_count * 24, bound_off + bound_count * 32)
    cbs, slots = {}, {}
    for n in range(cb_count):
        at, members, _, size, _, _ = struct.unpack_from("<6I", body, cb_off + n * 24)
        key = name(body, at, floor)
        if key in cbs or size > 2097152 or members > 512:
            raise ValueError("RDEF CB invalid")
        cbs[key] = size
    for n in range(bound_count):
        at, kind, _, _, _, slot, extent, _ = struct.unpack_from("<8I", body, bound_off + n * 32)
        if kind == 0:
            key = name(body, at, floor)
            if key in slots or key not in cbs or extent != 1 or slot > 255:
                raise ValueError("RDEF CB slot invalid")
            slots[key] = slot
    return cbs, slots

def serialized_groups(raw):
    info = parse_parameter_blob(raw)
    if info["numeric_parameter_count"] or info["resource_parameter_count"] or info["struct_count"]:
        raise ValueError("exact member recovery required")
    at = 0
    def take():
        nonlocal at
        val = u(raw, at)
        at += 4
        return val
    if take() != 202012090:
        raise ValueError("serializer version drift")
    groups = take()
    if not 1 <= groups <= 32:
        raise ValueError("group count drift")
    result = {}
    for idx in range(groups):
        size = take()
        if size > 2048 or at + size > len(raw):
            raise ValueError("group string overflow")
        key = raw[at:at + size].decode("utf-8")
        at = (at + size + 3) & ~3
        used, members, structs = take(), take(), take()
        if members or structs:
            raise ValueError("unexpected member records")
        if idx:
            if key in result:
                raise ValueError("duplicate group")
            result[key] = used
    if take() or at != len(raw):
        raise ValueError("unparsed resources/trailing bytes")
    return result

def compare(groups, reflection):
    cbs, slots = reflection
    common = set(groups) & set(cbs)
    exact = {k for k in common if groups[k] == cbs[k]}
    return {"serialized_cb_count": len(groups),
            "serialized_cb_nonzero": sum(x > 0 for x in groups.values()),
            "serialized_cb_used_bytes": sum(groups.values()),
            "rdef_cb_count": len(cbs), "rdef_bound_cb_count": len(slots),
            "name_matches": len(common), "name_and_size_matches": len(exact),
            "name_size_and_slot_matches": len(exact & set(slots)),
            "shaderlab_runtime_or_gpu_verified": False}

def public_common_counts(program):
    """Publish only counts of *known* original Unity parameter arrays, never values."""
    common = program.get("m_CommonParameters", {})
    if not isinstance(common, dict):
        raise ValueError("Unknown original common-parameter layout")
    fields = ("m_BufferParams", "m_ConstantBufferBindings", "m_ConstantBuffers",
              "m_MatrixParams", "m_UAVParams", "m_VectorParams",
              "m_Samplers", "m_TextureParams")
    result = {}
    for field in fields:
        values = common.get(field, [])
        if not isinstance(values, list):
            raise ValueError("Unknown original common-parameter array")
        result[field] = len(values)
    return result


def crosscheck_unity_cb(name_indices, common, groups, dxbc_declarations=None):
    """Match exact original Unity CB names, sizes and binding slots privately.

    This verifies source metadata agreement, NOT DXBC register declarations,
    HLSL uniform values or a working Unity ShaderLab program.
    """
    if not isinstance(name_indices, list) or not isinstance(common, dict):
        raise ValueError("unity_cb_bad_original_schema")
    names, seen_names = {}, set()
    for entry in name_indices:
        if not isinstance(entry, (tuple, list)) or len(entry) != 2:
            raise ValueError("unity_cb_bad_name_table")
        value, index = entry
        if not isinstance(value, str) or type(index) is not int or index < 0:
            raise ValueError("unity_cb_bad_name_table")
        if index in names or value in seen_names:
            raise ValueError("unity_cb_ambiguous_name_table")
        names[index] = value
        seen_names.add(value)

    buffers = common.get("m_ConstantBuffers", [])
    bindings = common.get("m_ConstantBufferBindings", [])
    if not isinstance(buffers, list) or not isinstance(bindings, list):
        raise ValueError("unity_cb_bad_original_schema")
    if len(buffers) != len(groups) or len(bindings) != len(groups):
        raise ValueError("unity_cb_count_mismatch")
    declarations, registers = {}, {}
    member_counts = {"m_MatrixParams": 0, "m_VectorParams": 0, "m_StructParams": 0}
    for entry in buffers:
        if not isinstance(entry, dict):
            raise ValueError("unity_cb_bad_definition")
        name_index, size = entry.get("m_NameIndex"), entry.get("m_Size")
        if type(name_index) is not int or name_index not in names or type(size) is not int or size < 0:
            raise ValueError("unity_cb_bad_definition")
        name = names[name_index]
        if name in declarations:
            raise ValueError("unity_cb_duplicate_definition")
        declarations[name] = size
        for field in member_counts:
            values = entry.get(field, [])
            if not isinstance(values, list):
                raise ValueError("unity_cb_bad_members")
            member_counts[field] += len(values)
    for entry in bindings:
        if not isinstance(entry, dict):
            raise ValueError("unity_cb_bad_binding")
        name_index, slot = entry.get("m_NameIndex"), entry.get("m_Index")
        if type(name_index) is not int or name_index not in names or type(slot) is not int or slot < 0 or slot > 255:
            raise ValueError("unity_cb_bad_binding")
        name = names[name_index]
        if name in registers or slot in registers.values():
            raise ValueError("unity_cb_ambiguous_binding")
        registers[name] = slot
    if set(groups) != set(declarations) or set(groups) != set(registers):
        raise ValueError("unity_cb_names_mismatch")
    if any(groups[key] != declarations[key] for key in groups):
        raise ValueError("unity_cb_sizes_mismatch")
    compiled_dcl_verified = False
    if dxbc_declarations is not None:
        if not isinstance(dxbc_declarations, dict) or set(dxbc_declarations) != set(registers.values()):
            raise ValueError("unity_cb_dxbc_registers_mismatch")
        if any(dxbc_declarations[registers[key]] != groups[key] for key in groups):
            raise ValueError("unity_cb_dxbc_sizes_mismatch")
        compiled_dcl_verified = True
    return {
        "unity_serialized_cb_name_size_slot_matches": len(groups),
        "unity_serialized_cb_identity_source_verified": True,
        "unity_cb_binding_slot_count": len(set(registers.values())),
        "unity_cb_member_parameter_counts": member_counts,
        "dxbc_register_or_shaderlab_runtime_verified": False,
        "dxbc_dcl_original_slot_size_verified": compiled_dcl_verified,
    }


def main(source, repo, out):
    # These exact hard-coded error markers contain no original Shader identifiers.
    safe_error_codes = {
        "invalid DXBC container", "invalid DXBC chunk table", "invalid DXBC chunk range",
        "missing unique original RDEF", "RDEF table bounds", "invalid private string",
        "RDEF CB invalid", "RDEF CB slot invalid", "truncated original reflection",
        "exact member recovery required", "serializer version drift", "group count drift",
        "group string overflow", "unexpected member records", "duplicate group",
        "unparsed resources/trailing bytes", "original object fingerprint drift",
        "original platform drift", "original pass topology drift",
        "original stage permutations drift",
    }
    phase = "original_source"
    active_pass = None
    active_stage = None
    report = {"status": "blocked", "original_verified": False,
              "shaderlab_installed": False, "game_ready": False, "private_names_published": False}
    try:
        _, digest, tree = original_shader(source, repo)
        if digest != "c9341848367eaedb12e551ce9061b1eea728f54f2069ef1a3c12c4a4a2e9bb52":
            raise ValueError("original object fingerprint drift")
        report["original_verified"] = True
        phase = "platform_records"
        tables = [records(p) for code, p in decoded_platforms(tree) if code == 4]
        if len(tables) != 1:
            raise ValueError("original platform drift")
        entries = tables[0]
        parsed = tree["m_ParsedForm"]
        phase = "original_graph"
        graph = inspect_shader(parsed, entries)
        if graph["original_pass_count"] != 2 or graph["linked_stage_programs"] != 4:
            raise ValueError("original pass topology drift")
        rows = []
        for pi, p in enumerate(parsed["m_SubShaders"][0]["m_Passes"]):
            active_pass = pi
            for field, st in (("progVertex", 1), ("progFragment", 0)):
                active_stage = st
                phase = "original_stage_links"
                prog = p[field]
                variants = stage_variants(prog)
                if len(variants) != 1:
                    raise ValueError("original stage permutations drift")
                bucket, vi, meta = variants[0]
                raw = entries[prog["m_ParameterBlobIndices"][bucket][vi]][1]
                code, _ = linked_program(meta, entries, st)
                phase = "original_parameter_schema"
                decoded = parse_parameter_blob(raw)
                item = {"pass": pi, "stage": st, "parameter_sha256": hashlib.sha256(raw).hexdigest(),
                        "numeric_members": decoded["numeric_parameter_count"],
                        "resource_records": decoded["resource_parameter_count"],
                        "struct_count": decoded["struct_count"],
                        "original_cb_count": decoded["constant_buffer_count"],
                        "original_cb_used_bytes": decoded["constant_buffer_used_bytes"],
                        "unity_common_array_counts": public_common_counts(prog),
                        "original_name_index_count": len(p["m_NameIndices"]),
                        "shaderlab_binding_verified": False}
                phase = "compiled_dxbc_constant_buffer_declarations"
                try:
                    original_decl = dxbc_cb_declarations(code)
                except ValueError as dcl_error:
                    # A failed compiled-declaration parse cannot be counted as
                    # original register evidence, even if Unity source matches.
                    original_decl = None
                    item["compiled_dxbc_dcl_status"] = "unverified"
                    safe_dcl_errors = {
                        "dxbc_dcl_truncated", "dxbc_dcl_bad_container", "dxbc_dcl_bad_total_size",
                        "dxbc_dcl_bad_chunks", "dxbc_dcl_bad_chunk_offset",
                        "dxbc_dcl_bad_chunk_range", "dxbc_dcl_missing_unique_shader",
                        "dxbc_dcl_bad_token_stream", "dxbc_dcl_bad_declared_tokens",
                        "dxbc_dcl_bad_instruction_size", "dxbc_dcl_unsupported_cb_encoding",
                        "dxbc_dcl_unsupported_cb_operand", "dxbc_dcl_unsafe_cb_declaration",
                        "dxbc_dcl_no_constant_buffers",
                    }
                    item["compiled_dxbc_dcl_blocker"] = (
                        str(dcl_error) if str(dcl_error) in safe_dcl_errors else "unclassified"
                    )
                else:
                    item["compiled_dxbc_dcl_status"] = "decoded"
                    item["compiled_dxbc_dcl_count"] = len(original_decl)
                phase = "compiled_dxbc_rdef"
                try:
                    compiled = rdef(code)
                except ValueError as error:
                    if str(error) != "missing unique original RDEF":
                        raise
                    # Reflection-stripped DXBC is authentic input, not proof of
                    # absent cbuffers. Continue to inspect serialized Unity data.
                    item["rdef_present"] = False
                    compiled = None
                else:
                    item["rdef_present"] = True
                if item["numeric_members"] or item["resource_records"] or item["struct_count"]:
                    item["classification"] = "members_need_exact_recovery"
                else:
                    phase = "original_memberless_groups"
                    original_groups = serialized_groups(raw)
                    item["original_cb_sizes_only"] = sorted(original_groups.values())
                    phase = "unity_serialized_cb_links"
                    try:
                        item.update(crosscheck_unity_cb(p["m_NameIndices"],
                                                      prog["m_CommonParameters"], original_groups,
                                                      dxbc_declarations=original_decl))
                    except ValueError as error:
                        safe_cb_errors = {
                            "unity_cb_bad_original_schema", "unity_cb_bad_name_table",
                            "unity_cb_ambiguous_name_table", "unity_cb_count_mismatch",
                            "unity_cb_bad_definition", "unity_cb_duplicate_definition",
                            "unity_cb_bad_members", "unity_cb_bad_binding",
                            "unity_cb_ambiguous_binding", "unity_cb_names_mismatch",
                            "unity_cb_sizes_mismatch", "unity_cb_dxbc_registers_mismatch",
                            "unity_cb_dxbc_sizes_mismatch",
                        }
                        item["unity_serialized_cb_identity_source_verified"] = False
                        item["unity_serialized_cb_blocker"] = (
                            str(error) if str(error) in safe_cb_errors else "unclassified"
                        )
                    if compiled is None:
                        item["classification"] = "compiled_rdef_stripped_original_cb_names_unresolved"
                    else:
                        item["classification"] = "memberless_original_cb_reflected"
                        phase = "constant_buffer_correlation"
                        item.update(compare(original_groups, compiled))
                rows.append(item)
        if len(rows) != 4:
            raise ValueError("Original stage count changed")
        report.update(status="diagnostic_complete", stage_count=len(rows), stages=rows,
                      compiled_rdef_present_count=sum(row["rdef_present"] for row in rows),
                      compiled_rdef_stripped_count=sum(not row["rdef_present"] for row in rows),
                      original_shaderlab_cb_binding_verified=False,
                      compiled_original_cb_dcl_linked_stages=sum(
                          row.get("dxbc_dcl_original_slot_size_verified") is True for row in rows
                      ),
                      source_only_structural_diagnostic=True)
    except Exception as exc:
        report["failure_type"] = type(exc).__name__
        report["failure_phase"] = phase
        report["failure_pass_index"] = active_pass
        report["failure_stage_code"] = active_stage
        # Never print arbitrary exception text (which may contain original names).
        report["failure_code"] = str(exc) if type(exc) is ValueError and str(exc) in safe_error_codes else "unclassified"
    safe = json.dumps(report, sort_keys=True)
    out.write_text(safe + "\n", encoding="utf-8")
    print("RAFT_A12R_CB " + safe)
    if report["status"] != "diagnostic_complete":
        raise ValueError("original CB probe blocked, see safe summary")
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    main(a.source, a.repo, a.out)
