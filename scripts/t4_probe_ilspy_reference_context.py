"""T4 LOCAL-005: bounded same-original-DLL decompiler reference-context experiment.

All sources and binary owners stay inside ephemeral authorized CI directories.
Only hash/count aggregates leave this module. It never changes native source pins.
"""
import argparse
import json
from pathlib import Path

from scripts.b07_probe_original_world_callbacks import assert_original_dll
from scripts.t4_compare_private_ilspy_runs import (
    OBSERVED_ORIGINAL_PAIRS,
    source_profile,
)

# This is deliberately a read-only historical source-intake comparison.
# Exact class/body pair whitelist may not be added to the runtime adapter.
OLD_PAIR = (
    "080035c137e446828226ed84a23190656b6f235d274436cafb477feaf93caa03",
    "cbd74c24f1c6a86dd50e8d320f4f4142f5b3f3fc5bf8f64ded04710c30c3a140",
)
NEW_PAIR = (
    "d16c36336a6aec4e23781c135820692a233130a3f1c1d9ab9052d432d76eedef",
    "2bf76a189a69d23444c5ede9f00a5444a48f819c64d87ec298ebeedbf5d9088c",
)

def summarize(a, b, rich, companion_count, *, authentic=True):
    """Compare three independently staged source views, with no source text."""
    if not isinstance(companion_count, int) or companion_count < 1:
        raise ValueError("Reference context must contain verified sibling assemblies")
    data = [a, b, rich]
    pairs = [(x["class_sha256"], x["coroutine_body_sha256"]) for x in data]
    if any(pair not in OBSERVED_ORIGINAL_PAIRS for pair in pairs):
        raise ValueError("Unknown original source-pair fingerprint")
    if pairs[0] != pairs[1]:
        raise ValueError("Isolated same-DLL source views differ before reference experiment")
    if any(x["iterator_return"] != "IEnumerator" or x["original_completion_writes"] != 1
           or x["original_scene_broadcast_calls"] != 1 for x in data):
        raise ValueError("Genuine original coroutine contract drift")
    masks = [x["masked_coroutine_sha256"] for x in data]
    return {
        "isolated_source_pair": list(pairs[0]),
        "isolated_control_matches": True,
        "sibling_source_pair": list(pairs[2]),
        "different_class_hash_with_siblings": pairs[0][0] != pairs[2][0],
        "different_coroutine_body_hash_with_siblings": pairs[0][1] != pairs[2][1],
        "different_masked_executable_body_hash_with_siblings": masks[0] != masks[2],
        "old_B07_source_pair_reproduced_with_siblings": pairs[2] == OLD_PAIR,
        "T4_isolated_source_pair_reproduced": pairs[0] == NEW_PAIR,
        "observed_sibling_assembly_files": companion_count,
        "only_known_original_pairs_accepted": True,
        "same_original_dll_sha_verified": bool(authentic),
        "remaining_confounds": "directory path/context can vary alongside sibling assemblies",
        "production_source_pins_changed": False,
        "unity_compiled": False,
        "device_tested": False,
        "world_playable_or_rgd_roundtrip": False,
        "private_source_published": False,
    }


def probe(dlls, sources, managed_dir):
    if len(dlls) != 3 or len(sources) != 3:
        raise ValueError("Exactly three matched DLL and source roots required")
    if len(set(p.resolve() for p in sources)) != 3:
        raise ValueError("Independent private source directories required")
    # Paths must be regular, nonlinked; no private bytes exposed in errors.
    for p in (*dlls, *sources, managed_dir):
        if p.is_symlink():
            raise ValueError("Linked private input refused")
    for dll in dlls:
        assert_original_dll(dll)
    if not managed_dir.is_dir():
        raise ValueError("Sibling assembly directory missing")
    siblings = [p for p in managed_dir.iterdir()
                if p.is_file() and not p.is_symlink() and p.suffix.lower() == ".dll"
                and p.name != "Assembly-CSharp.dll"]
    # A single arbitrary dummy sibling is not a real original reference context.
    if len(siblings) < 100:
        raise ValueError("Incomplete pinned managed companion input")
    for s in sources:
        if not s.is_dir():
            raise ValueError("Missing private output directory")
    views = [source_profile(s) for s in sources]
    return summarize(*views, companion_count=len(siblings))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--solo-a-dll", type=Path, required=True)
    p.add_argument("--solo-b-dll", type=Path, required=True)
    p.add_argument("--refs-dll", type=Path, required=True)
    p.add_argument("--solo-a-source", type=Path, required=True)
    p.add_argument("--solo-b-source", type=Path, required=True)
    p.add_argument("--refs-source", type=Path, required=True)
    p.add_argument("--managed-dir", type=Path, required=True)
    args = p.parse_args()
    try:
        report = probe(
            [args.solo_a_dll, args.solo_b_dll, args.refs_dll],
            [args.solo_a_source, args.solo_b_source, args.refs_source],
            args.managed_dir,
        )
        report["status"] = "ORIGINAL_CONTEXT_COMPARISON_EXECUTED"
        code = 0
    except Exception:
        # No raw decompiler errors or path names may appear in public logs.
        report = {"status": "ORIGINAL_CONTEXT_UNRESOLVED",
                  "private_source_published": False,
                  "device_tested": False}
        code = 2
    print("T4_ORIGINAL_REFERENCE_CONTEXT " + json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
