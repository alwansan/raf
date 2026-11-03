"""A15: authenticated original Shader parsed-pass topology, CPU only.

Reports aggregate original serialized m_ParsedForm data, not GPU execution,
actual exported ShaderLab correspondence, original source, or shader names.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.w1_stage_zip2_owners import PINS, fingerprint

OWNERS = ("Raft_Data/resources.assets", "Raft_Data/sharedassets0.assets")
EXPECTED_COUNTS = (47, 58)


def _list(value, field):
    if not isinstance(value, list):
        raise ValueError("Invalid original " + field)
    return value


def summarize(rows):
    """Accept (owner, path_id, original parsed form); fail closed on bad shape."""
    if not rows:
        raise ValueError("No original Shader objects")
    counts = Counter()
    by_owner = {owner: Counter() for owner in OWNERS}
    seen = set()
    pass_histogram = Counter()
    subshader_histogram = Counter()
    for owner, path_id, parsed in rows:
        if owner not in OWNERS or type(path_id) is not int or path_id <= 0:
            raise ValueError("Invalid original Shader identity")
        key = (owner, path_id)
        if key in seen:
            raise ValueError("Duplicate original Shader identity")
        seen.add(key)
        if not isinstance(parsed, dict):
            raise ValueError("Missing original Shader parsed form")
        subshaders = _list(parsed.get("m_SubShaders"), "m_SubShaders")
        pass_count = 0
        for subshader in subshaders:
            if not isinstance(subshader, dict):
                raise ValueError("Invalid original SubShader record")
            passes = _list(subshader.get("m_Passes"), "m_Passes")
            if not all(isinstance(p, dict) for p in passes):
                raise ValueError("Invalid original Pass record")
            pass_count += len(passes)
        counts["shader_objects"] += 1
        counts["subshader_records"] += len(subshaders)
        counts["pass_records"] += pass_count
        counts["shaders_with_zero_passes"] += pass_count == 0
        counts["shaders_with_multiple_passes"] += pass_count > 1
        by_owner[owner]["shaders"] += 1
        by_owner[owner]["passes"] += pass_count
        pass_histogram[pass_count] += 1
        subshader_histogram[len(subshaders)] += 1
    return {
        "original_serialized_shader_objects": counts["shader_objects"],
        "original_serialized_subshader_records": counts["subshader_records"],
        "original_serialized_pass_records": counts["pass_records"],
        "original_shaders_with_zero_passes": counts["shaders_with_zero_passes"],
        "original_shaders_with_multiple_passes": counts["shaders_with_multiple_passes"],
        "original_passes_per_shader_histogram": dict(sorted(pass_histogram.items())),
        "original_subshaders_per_shader_histogram": dict(sorted(subshader_histogram.items())),
        "per_owner": {owner.rsplit("/", 1)[-1]: dict(by_owner[owner]) for owner in OWNERS},
        "serialized_not_executable_programs": True,
        "original_to_exported_shader_join_verified": False,
        "unity_gpu_or_device_verified": False,
    }


def probe(root):
    import UnityPy
    source = Path(root)
    records = []
    for owner, expected_count in zip(OWNERS, EXPECTED_COUNTS):
        pin = PINS[owner]
        original = source / owner
        if original.is_symlink() or fingerprint(original) != pin:
            raise ValueError("Original source fingerprint mismatch")
        env = UnityPy.load(str(original))
        owner_count = 0
        for obj in env.objects:
            if obj.type.name != "Shader":
                continue
            tree = obj.read_typetree()
            if not isinstance(tree, dict) or "m_ParsedForm" not in tree:
                raise ValueError("Missing original Shader parsed form")
            records.append((owner, int(obj.path_id), tree["m_ParsedForm"]))
            owner_count += 1
        if owner_count != expected_count:
            raise ValueError("Original Shader inventory drift")
    result = summarize(records)
    if result["original_serialized_shader_objects"] != 105:
        raise ValueError("Original 2-owner Shader inventory drift")
    result.update(
        source_provider="zip2_sha_pinned_original_owners",
        verified_original_bytes=sum(PINS[o][0] for o in OWNERS),
        raw_shader_programs_disclosed=False,
        full_game_original_owner_coverage_verified=False,
        exported_shaderlab_pass_equivalence_verified=False,
        ready_for_build=False,
    )
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    args = cli.parse_args()
    try:
        result = probe(args.source)
        args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print("RAFT_A15_ORIGINAL_SHADER_PASSES " + json.dumps(result, sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Do not leak file paths, object names or proprietary shader data.
        print("RAFT_A15_ORIGINAL_SHADER_PASSES " + json.dumps({
            "status": "REJECTED", "reason": type(exc).__name__,
            "original_to_exported_shader_join_verified": False,
            "ready_for_build": False,
        }, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
