"""Private SHA-original Foam CB0 name targets for managed IL caller discovery.

Matches true original serialized CB0 name indexes (not guessed translated HLSL
identifiers) to managed ldstr later. Exact names/hashes stay in runner temp.
This is lexical evidence, never original Unity uniform upload.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.b20_foam_cb_descriptor_lineage import SOURCE_SLOTS
from scripts.b25_foam_cb_namebridge import original_name_registry, inspect_parsed
from scripts.t2_foam_member_abi import STAGES, original_source_tree, original_members, _physical
from scripts.b24_original_foam_stage_translation import TARGET, validate_stage

MAX_NAMES = 128
MAX_INPUT_BYTES = 4096


def _name(registry, idx):
    if type(idx) is not int or idx not in registry:
        return None
    value = registry[idx]
    if not isinstance(value, str) or not 0 < len(value) <= 256 or "\x00" in value:
        raise ValueError("unsafe_private_source_name")
    return value


def build_private_target_set(parsed):
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("not_SHA_original_Foam_parsed_shader")
    attest = inspect_parsed(parsed)
    if attest.get("matched_constant_buffer_bindings") != 8:
        raise ValueError("original_CB_registry_unattested")
    passes = parsed["m_SubShaders"][0]["m_Passes"]
    names = {"buffer": set(), "vector": set(), "matrix": set()}
    counts = {"original_stage_count": 0, "original_cb0_stage_bindings": 0,
              "original_cb0_vector_parameters": 0,
              "original_cb0_matrix_parameters": 0,
              "original_cb0_parameter_name_indices_unresolved": 0}
    seen = set()
    for pi, stage in STAGES:
        if (pi, stage) in seen or 0 not in SOURCE_SLOTS.get((pi, stage), ()):
            raise ValueError("original_CB0_stage_identity_missing")
        seen.add((pi, stage))
        p = passes[pi]
        registry = original_name_registry(p["m_NameIndices"])
        program = p["progVertex" if stage == 1 else "progFragment"]
        validate_stage(program, stage, {"original_pass": pi})
        buffers = program["m_CommonParameters"]["m_ConstantBuffers"]
        if not isinstance(buffers, list) or not buffers:
            raise ValueError("original_CB0_buffer_absent")
        cb0 = buffers[0]
        original_members(cb0)  # same authenticated structural row bounds as T2 ABI
        cbname = _name(registry, cb0.get("m_NameIndex"))
        if cbname is None:
            raise ValueError("original_CB0_buffer_registry_reference_missing")
        names["buffer"].add(cbname)
        for role, key in (("vector", "m_VectorParams"),
                          ("matrix", "m_MatrixParams")):
            rows = cb0.get(key)
            if not isinstance(rows, list) or len(rows) > MAX_NAMES:
                raise ValueError("original_CB0_parameter_list_malformed")
            counts["original_cb0_" + role + "_parameters"] += len(rows)
            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError("original_CB0_parameter_malformed")
                n = _name(registry, row.get("m_NameIndex"))
                if n is None:
                    counts["original_cb0_parameter_name_indices_unresolved"] += 1
                    continue
                names[role].add(n)
        counts["original_stage_count"] += 1
        counts["original_cb0_stage_bindings"] += 1
    if counts["original_stage_count"] != 4 or counts["original_cb0_stage_bindings"] != 4:
        raise ValueError("original_CB0_stage_count_drift")
    all_values = set().union(*names.values())
    if not all_values or sum(map(len, names.values())) > MAX_NAMES:
        raise ValueError("original_CB0_name_target_count_invalid")
    # Per-category hashes only in temporary CI input, never stdout/artifacts.
    targets = {role: sorted(hashlib.sha256(v.encode("utf8")).hexdigest()
                            for v in values)
               for role, values in names.items()}
    return {"schema": 1, "source_kind": "SHA_original_Foam_CB0_source_name_registry",
            "categories_sha256": targets, **counts,
            "distinct_target_names": len(all_values),
            "actual_Unity_upload_proven": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    try:
        source, out = a.source.absolute(), a.out.absolute()
        if (not source.is_dir() or not _physical(source)
                or not out.parent.is_dir() or not _physical(out)
                or out.exists() or out.is_relative_to(source)):
            raise ValueError("unsafe_original_private_input_output")
        r = build_private_target_set(original_source_tree(source))
        out.write_text(json.dumps(r, sort_keys=True) + "\n", encoding="utf8")
        result = {
            "status": "original_CB0_private_name_targets_prepared",
            "original_stages": r["original_stage_count"],
            "CB0_stage_bindings": r["original_cb0_stage_bindings"],
            "original_CB0_parameter_name_indices_unresolved":
                r["original_cb0_parameter_name_indices_unresolved"],
            "exact_name_values_or_hashes_published": False,
            "Unity_CB0_upload_verified": False,
        }
        rc = 0
    except BaseException:
        result = {"status": "blocked_original_CB0_name_targets",
                  "exact_name_values_or_hashes_published": False,
                  "Unity_CB0_upload_verified": False}
        rc = 2
    print("T2_FOAM_CB0_PRIVATE_TARGETS " + json.dumps(result, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
