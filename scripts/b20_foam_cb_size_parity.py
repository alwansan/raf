"""B20 compare original typed partial CB m_Size vs recovered SPIR-V block_size.

Consumes safe, source-authenticated B20/B25 NUMERIC reports only. Different
size representations are not proof of lost bytes or wrong game pixels. Never
infer CB0 aliases or mark Unity bindings validated.
"""
import argparse
import hashlib
import json
from pathlib import Path

# Original 2-pass Foam serial m_CommonParameters.m_ConstantBuffers.m_Size,
# pinned to original Shader PathID2420 object SHA in B25 original run41928183838.
ORIGINAL_PARTIAL_CB_SIZE = {
    (0, 1): {0: 160, 1: 176, 2: 368},
    (0, 0): {0: 160},
    (1, 1): {0: 160, 1: 176, 2: 368},
    (1, 0): {0: 160},
}
EXPECTED_KEYS = [(0, 1), (0, 0), (1, 1), (1, 0)]


def compare(data):
    if (not isinstance(data, dict)
            or data.get("status") != "genuine_foam_cb_reflection_observed"
            or data.get("authenticated_original_foam_stage_count") != 4
            or data.get("original_source_cb_links") != 8
            or data.get("all_hlsl_b_slots_numerically_coincide") is not True
            or data.get("all_spirv_set0_bindings_numerically_coincide") is not True
            or data.get("original_cb0_name_to_hlsl_alias_verified") is not False
            or data.get("original_material_constant_buffer_upload_verified") is not False
            or data.get("private_hlsl_spirv_names_or_binaries_published") is not False):
        raise ValueError("Original source/reflection provenance or unverified flags missing")
    stages = data.get("stages")
    if not isinstance(stages, list) or len(stages) != 4:
        raise ValueError("Missing exact four authentic Foam stages")
    rows = []
    for entry, key in zip(stages, EXPECTED_KEYS):
        expected = ORIGINAL_PARTIAL_CB_SIZE[key]
        slots = list(expected)
        if (not isinstance(entry, dict)
                or (entry.get("pass"), entry.get("stage_code")) != key
                or entry.get("original_source_cb_slots") != slots
                or entry.get("hlsl_explicit_cbuffer_b_slots") != slots
                or entry.get("hlsl_source_slot_set_coincides") is not True
                or entry.get("spirv_set0_binding_set_coincides") is not True):
            raise ValueError("Foam original/reflected stage order or slot set changed")
        ubos = entry.get("spirv_reflected_ubos")
        if not isinstance(ubos, list) or len(ubos) != len(expected):
            raise ValueError("Source-to-SPIRV CB cardinality changed")
        seen = set()
        for ubo in ubos:
            if not isinstance(ubo, dict):
                raise ValueError("Invalid reflected UBO")
            slot, dset, size = ubo.get("binding"), ubo.get("set"), ubo.get("bytes")
            if (type(slot) is not int or type(dset) is not int
                    or type(size) is not int or slot not in expected
                    or dset != 0 or not 0 < size <= 65536 or slot in seen):
                raise ValueError("Invalid/duplicate reflected CB register/size")
            seen.add(slot)
            rows.append({
                "pass": key[0], "stage_code": key[1], "slot": slot,
                "original_partial_cb_m_size_bytes": expected[slot],
                "translated_spirv_reflected_block_size_bytes": size,
                "reflected_minus_serialized_bytes": size - expected[slot],
                "same_numeric_block_size": size == expected[slot],
            })
        if seen != set(expected):
            raise ValueError("Missing reflected original CB register")
    exact = sum(row["same_numeric_block_size"] for row in rows)
    return {
        "status": "source_authentic_foam_cb_size_comparison",
        "original_cb_links_compared": len(rows),
        "exact_numeric_size_matches": exact,
        "different_numeric_size_pairs": len(rows) - exact,
        "cb_sizes_checked_at_same_verified_numeric_registers": True,
        "source_and_translated_sizes_are_semantically_interchangeable_proven": False,
        "original_cb0_name_alias_verified": False,
        "unity_game_material_constant_buffer_upload_verified": False,
        "android_gpu_pixels_verified": False,
        "rows": rows,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--safe-source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    if not a.safe_source.is_file() or a.safe_source.stat().st_size > 65536:
        raise SystemExit("Safe source-reflection report missing or out of bounds")
    raw = a.safe_source.read_bytes()
    result = compare(json.loads(raw))
    result["input_safe_reflection_sha256"] = hashlib.sha256(raw).hexdigest()
    if a.out.exists():
        raise SystemExit("Refusing to overwrite safe original CB comparison")
    a.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("B20_FOAM_CB_SIZE " + json.dumps({
        "status": result["status"], "links": result["original_cb_links_compared"],
        "equal_numeric": result["exact_numeric_size_matches"],
        "different_numeric": result["different_numeric_size_pairs"],
        "cb0_alias_proven": False, "android_pixels_proven": False}))


if __name__ == "__main__":
    main()
