"""B25 WATER-001: SHA-authentic Foam partial CB original name-index bridge.

Original property/CB names and source stay in private original-data CI memory.
Aggregate reports expose SHA-256 commitments, indices and verified numeric shapes
only. Complements B24 authentic compiled programs; no ShaderLab installed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.b24_original_foam_stage_translation import (
    TARGET, OBJECT_ID, ORIGINAL_OBJECT_SHA256, validate_stage,
)
from scripts.w1_stage_zip2_owners import PINS, fingerprint

OWNER = "Raft_Data/sharedassets0.assets"
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def original_name_registry(raw, diagnostic=None):
    diagnostic = {} if diagnostic is None else diagnostic
    if not isinstance(raw, list) or not 1 <= len(raw) <= 8192:
        diagnostic["registry_rejection"] = "invalid-container-bounds"
        raise ValueError("Original Foam name registry absent/oversized")
    names = {}
    seen_values = set()
    for row_index, row in enumerate(raw):
        diagnostic["registry_rejection_row_index"] = row_index
        if isinstance(row, (list, tuple)) and len(row) == 2:
            name, idx = row
        elif isinstance(row, dict) and set(row) == {"first", "second"}:
            name, idx = row["first"], row["second"]
        else:
            diagnostic["registry_rejection"] = "row-schema"
            raise ValueError("Original Foam name row schema unsupported")
        diagnostic["registry_name_value_type"] = type(name).__name__
        diagnostic["registry_index_value_type"] = type(idx).__name__
        # m_NameIndices is the *whole* original property registry, not a CB-only
        # table; non-CB entries may contain punctuation and are never emitted
        # as HLSL CB identifiers. Check HLSL identifier grammar only at an
        # authenticated CB m_NameIndex reference below.
        if (not isinstance(name, str) or not 0 < len(name) <= 256
                or any(ch in name for ch in (chr(0), chr(13), chr(10)))):
            diagnostic["registry_rejection"] = "invalid-registry-name"
            raise ValueError("Original Foam property registry string malformed")
        if type(idx) is not int or idx < 0 or idx >= 1 << 20 or idx in names:
            diagnostic["registry_rejection"] = "invalid-duplicate-index"
            raise ValueError("Original Foam ambiguous name index")
        if name in seen_values:
            diagnostic["registry_rejection"] = "duplicate-name"
            raise ValueError("Original Foam duplicate CB name")
        names[idx] = name
        seen_values.add(name)
    diagnostic["registry_rejection"] = None
    return names


def inspect_parsed(parsed, diag=None):
    diag = {} if diag is None else diag
    diag["phase"] = "original-foam-identity"
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Foam original Shader identity changed")
    subs = parsed.get("m_SubShaders")
    if not isinstance(subs, list) or len(subs) != 1 or not isinstance(subs[0], dict):
        raise ValueError("Foam original subshader topology changed")
    passes = subs[0].get("m_Passes")
    if not isinstance(passes, list) or len(passes) != 2:
        raise ValueError("Foam original two-pass count changed")
    results = []
    for pi, p in enumerate(passes):
        diag.update(phase="original-name-registry", pass_index=pi)
        if not isinstance(p, dict) or p.get("m_Type") != 0:
            raise ValueError("Foam original pass type unsupported")
        source_names = p.get("m_NameIndices")
        # Safe schema-only diagnostics; never log original CB names/values.
        diag["registry_container_type"] = type(source_names).__name__
        diag["registry_record_count"] = len(source_names) if isinstance(source_names, (list, dict)) else None
        diag["registry_first_row_type"] = (
            type(source_names[0]).__name__ if isinstance(source_names, list) and source_names else None)
        diag["registry_first_row_length"] = (
            len(source_names[0]) if isinstance(source_names, list) and source_names
            and isinstance(source_names[0], (list, dict, tuple)) else None)
        names = original_name_registry(source_names, diagnostic=diag)
        stage_rows = []
        for stage, field in ((1, "progVertex"), (0, "progFragment")):
            diag.update(phase="original-CB-index-resolution", stage_code=stage)
            program = p.get(field)
            if not isinstance(program, dict):
                raise ValueError("Foam original stage missing")
            # Reuse independently source-authenticated B24 partial-CB and
            # variant invariants, including pass1 CB0's one vector member.
            validate_stage(program, stage, {"original_pass": pi})
            common = program["m_CommonParameters"]
            buffers = common["m_ConstantBuffers"]
            bindings = common["m_ConstantBufferBindings"]
            cb_rows = []
            for slot, (buf, bind) in enumerate(zip(buffers, bindings)):
                diag["cb_slot"] = slot
                idx = buf["m_NameIndex"]
                if type(idx) is not int or idx not in names:
                    raise ValueError("Foam original CB name index missing from registry")
                if bind["m_NameIndex"] != idx or bind["m_Index"] != slot:
                    raise ValueError("Foam original CB register identity changed")
                name = names[idx]
                # Original compiled constant-buffer symbols are opaque (some
                # are compiler-generated and cannot be used literally as HLSL
                # identifiers). Preserve their EXACT SHA identity and register
                # relationship; a future private rebind must use a validated
                # alias. Never emit the raw name or invent a Unity property.
                safe_identifier = IDENT.fullmatch(name) is not None
                cb_rows.append({
                    "literal_hlsl_identifier_usable": safe_identifier,
                    "requires_verified_shaderlab_alias": not safe_identifier,
                    "register_slot": slot,
                    "original_name_index": idx,
                    "name_sha256": hashlib.sha256(name.encode("utf-8")).hexdigest(),
                    "constant_buffer_size": buf["m_Size"],
                    "vector_member_count": len(buf["m_VectorParams"]),
                    "matrix_member_count": len(buf["m_MatrixParams"]),
                })
            stage_rows.append({"stage_code": stage, "constant_buffers": cb_rows})
        results.append({"pass_index": pi, "registry_records": len(names), "stages": stage_rows})
    return {
        "original_passes": 2,
        "authenticated_stage_count": 4,
        "matched_constant_buffer_bindings": sum(
            len(s["constant_buffers"]) for p in results for s in p["stages"]),
        "referenced_cb_names_requiring_alias": sum(
            int(row["requires_verified_shaderlab_alias"])
            for p in results for s in p["stages"] for row in s["constant_buffers"]),
        "passes": results,
        "private_name_values_published": False,
        "shaderlab_cb_rebinding_installed": False,
        "original_material_guid_verified": False,
        "unity_or_android_verified": False,
    }


def physical(path):
    return not any(part.is_symlink() for part in (path, *path.parents))


def probe(source, diagnostic=None):
    diagnostic = {} if diagnostic is None else diagnostic
    diagnostic["phase"] = "original-source-sha"
    if not physical(source) or not source.is_dir():
        raise ValueError("Original source directory missing/linked")
    path = source / OWNER
    if not physical(path) or not path.is_file() or fingerprint(path) != PINS[OWNER]:
        raise ValueError("Original source SHA/size mismatch")
    import UnityPy
    diagnostic["phase"] = "original-shader-object-sha"
    env = UnityPy.load(str(path))
    objects = [o for o in env.file.objects.values()
               if o.type.name == "Shader" and int(o.path_id) == OBJECT_ID]
    if len(objects) != 1:
        raise ValueError("Original Foam object absent/ambiguous")
    obj = objects[0]
    if hashlib.sha256(obj.get_raw_data()).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original Foam object raw SHA mismatch")
    result = inspect_parsed(obj.read_typetree().get("m_ParsedForm"), diag=diagnostic)
    return {"status": "original_binding_names_verified", "original_source_sha256": PINS[OWNER][1],
            "original_object_sha256": ORIGINAL_OBJECT_SHA256, **result}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    args = p.parse_args()
    diag = {}
    try:
        report, code = probe(args.source, diag), 0
    except Exception as exc:
        # Only bounded indices/phase/type; never original private names/paths.
        report, code = {"status": "incomplete", "exception_type": type(exc).__name__,
                        "failure_phase": diag.get("phase", "unknown"),
                        "failure_pass": diag.get("pass_index"),
                        "failure_stage": diag.get("stage_code"),
                        "failure_cb_slot": diag.get("cb_slot"),
                        "registry_container_type": diag.get("registry_container_type"),
                        "registry_record_count": diag.get("registry_record_count"),
                        "registry_first_row_type": diag.get("registry_first_row_type"),
                        "registry_first_row_length": diag.get("registry_first_row_length"),
                        "registry_rejection": diag.get("registry_rejection"),
                        "registry_rejection_row_index": diag.get("registry_rejection_row_index"),
                        "registry_name_value_type": diag.get("registry_name_value_type"),
                        "registry_index_value_type": diag.get("registry_index_value_type"),
                        "cb_rejection": diag.get("cb_rejection"),
                        "private_name_values_published": False,
                        "unity_or_android_verified": False}, 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, sort_keys=True) + "\n")
    print("B25_FOAM_CB_NAMES " + json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
