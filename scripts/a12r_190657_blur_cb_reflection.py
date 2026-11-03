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
                        "struct_count": decoded["struct_count"]}
                if item["numeric_members"] or item["resource_records"] or item["struct_count"]:
                    item["classification"] = "members_need_exact_recovery"
                else:
                    item["classification"] = "memberless_original_cb_reflected"
                    phase = "original_memberless_groups"
                    original_groups = serialized_groups(raw)
                    phase = "compiled_dxbc_rdef"
                    compiled = rdef(code)
                    phase = "constant_buffer_correlation"
                    item.update(compare(original_groups, compiled))
                rows.append(item)
        report.update(status="diagnostic_complete", stage_count=len(rows), stages=rows)
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
