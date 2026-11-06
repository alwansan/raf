"""T2: compare SHA-original typed external Shader names with Foam name privately.

This proves only exact serialized Shader name identity/nonidentity in original
ZIP2 objects, not source GUID binding, Unity runtime Material or water pixels.
Output finite counts; never print/private-store Shader names or raw objects.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.t2_foam_original_external_pptr_graph import (
    FOAM_OWNER, FOAM_PATHID, FOAM_RAW_SHA256, MAX_OBJECTS,
)
from scripts.t2_foam_original_manifest_pptr import (
    parse_original_manifest, resolve_unmapped_external_materials,
    load_original_foam_material_edges, run as authenticated_stage,
)
from scripts.w1_stage_zip2_owners import PINS, fingerprint, safe

MAX_SHADER_NAME = 512


def shader_name(tree):
    """Read real shader parsed name, or count unsupported without guessing."""
    if not isinstance(tree, dict):
        return None
    parsed = tree.get("m_ParsedForm")
    if not isinstance(parsed, dict):
        return None
    name = parsed.get("m_Name")
    if (not isinstance(name, str) or not 0 < len(name) <= MAX_SHADER_NAME
            or "\x00" in name):
        return None
    return name


def safe_name_comparison(foam_name, targets):
    """Pure synthetic/original comparator; never returns source names/hashes."""
    if (not isinstance(foam_name, str) or not 0 < len(foam_name) <= MAX_SHADER_NAME
            or "\x00" in foam_name):
        raise ValueError("original_Foam_name_unavailable")
    if (not isinstance(targets, list) or not 0 < len(targets) <= 16):
        raise ValueError("original_shader_target_count_unbounded")
    seen, equal_names, readable, identical_raw = set(), 0, 0, 0
    for key, candidate_name, raw_equal in targets:
        if (not isinstance(key, tuple) or len(key) != 2
                or not isinstance(key[0], str) or not key[0] or len(key[0]) > 1024
                or type(key[1]) is not int or key[1] <= 0 or key in seen
                or type(raw_equal) is not bool):
            raise ValueError("original_target_identity_duplicate_or_invalid")
        seen.add(key)
        if candidate_name is not None:
            if (not isinstance(candidate_name, str) or not candidate_name
                    or len(candidate_name) > MAX_SHADER_NAME or "\x00" in candidate_name):
                raise ValueError("original_target_name_invalid")
            readable += 1
            equal_names += candidate_name == foam_name
        identical_raw += raw_equal
    return {
        "typed_external_Shader_targets": len(targets),
        "target_original_shader_name_readable": readable,
        "target_original_shader_name_unreadable": len(targets) - readable,
        "target_exact_Foam_name_matches": equal_names,
        "target_exact_Foam_raw_bytes_matches": identical_raw,
        "target_source_file_is_Foam_owner": False,
        "name_match_is_Unity_GUID_runtime_identity": False,
        "target_material_is_Foam_runtime_upload_verified": False,
        "Android_Adreno_water_pixels_verified": False,
        "private_shader_names_or_digests_published": False,
    }


def read_original_shader_name(obj):
    try:
        return shader_name(obj.read_typetree())
    except (ValueError, KeyError, TypeError, AttributeError, EOFError):
        return None


def private_original_relation(zip2, source, scratch, checkpoint=lambda _: None):
    import UnityPy
    zip2, source, scratch = (Path(p).absolute() for p in (zip2, source, scratch))
    safe(source)
    safe(scratch)
    checkpoint("target_original_sha_attestation")
    base = authenticated_stage(zip2, source, scratch)
    for key, expected in (
        ("original_zip2_commit_authenticated", True),
        ("original_sharedassets0_SHA_authenticated", True),
        ("original_Foam_Shader_object_SHA_authenticated", True),
        ("unique_manifest_candidate", 2),
        ("staged_target_files", 1),
        ("verified_typed_Shader_PPtrs", 2),
        ("verified_bytes_staged", 758412),
    ):
        if base.get(key) != expected:
            raise ValueError("original_target_attestation_drift")
    checkpoint("original_source_Shader_name")
    path = source / FOAM_OWNER
    safe(path)
    if fingerprint(path) != PINS[FOAM_OWNER]:
        raise ValueError("original_owner_source_pin_drift")
    foam_obj = next(
        (obj for obj in UnityPy.load(str(path)).file.objects.values()
         if obj.type.name == "Shader" and int(obj.path_id) == FOAM_PATHID),
        None,
    )
    if (foam_obj is None or
            hashlib.sha256(foam_obj.get_raw_data()).hexdigest() != FOAM_RAW_SHA256):
        raise ValueError("original_foam_object_absent_or_drift")
    foam_name = read_original_shader_name(foam_obj)
    if foam_name is None:
        raise ValueError("original_foam_parsed_name_unavailable")

    checkpoint("original_two_Shader_target_name_read")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    external_paths, pointer_rows = load_original_foam_material_edges(source)
    summary, targets = resolve_unmapped_external_materials(
        external_paths, pointer_rows, manifest,
    )
    if summary["unmapped"] != 2 or len(targets) != 2:
        raise ValueError("original_external_PPtr_baseline_drift")
    expected = {}
    for name, sha, path_id in targets:
        if name == FOAM_OWNER:
            raise ValueError("external_candidate_claims_original_Foam_owner")
        expected.setdefault(name, set()).add(path_id)
    if len(expected) != 1 or sum(map(len, expected.values())) != 2:
        raise ValueError("original_target_identity_cardinality_drift")

    rows = []
    for filename, target_ids in expected.items():
        item = next((x for x in manifest if x["path"] == filename), None)
        target_path = scratch / filename
        safe(target_path)
        if (item is None or not target_path.is_file() or
                fingerprint(target_path) != (item["bytes"], item["sha256"])):
            raise ValueError("original_target_sha_drift")
        objects = list(UnityPy.load(str(target_path)).file.objects.values())
        if len(objects) > MAX_OBJECTS:
            raise ValueError("original_target_object_count_unbounded")
        seen = set()
        for obj in objects:
            path_id = int(obj.path_id)
            if path_id not in target_ids:
                continue
            if obj.type.name != "Shader" or path_id in seen:
                raise ValueError("original_target_not_unique_typed_Shader")
            seen.add(path_id)
            rows.append(((filename, path_id), read_original_shader_name(obj),
                         hashlib.sha256(obj.get_raw_data()).hexdigest() == FOAM_RAW_SHA256))
        if seen != target_ids:
            raise ValueError("original_target_Shader_PathID_missing")
    comparison = safe_name_comparison(foam_name, rows)
    return {
        "status": "source_original_Foam_external_Shader_name_relation_verified",
        "zip2_SHA_attested": True,
        "source_owner_and_target_object_SHA_attested": True,
        "verified_target_file_count": len(expected),
        "original_target_bytes": base["verified_bytes_staged"],
        **comparison,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--zip2", required=True, type=Path)
    cli.add_argument("--source", required=True, type=Path)
    cli.add_argument("--scratch", required=True, type=Path)
    cli.add_argument("--out", required=True, type=Path)
    args = cli.parse_args()
    phase = "input_guard"
    def checkpoint(value):
        nonlocal phase
        phase = value
    try:
        out = args.out.absolute()
        safe(out)
        if (out.exists() or not out.parent.is_dir()
                or any(out.is_relative_to(x.absolute()) for x in
                       (args.zip2, args.source, args.scratch))):
            raise ValueError("unsafe_original_result_output")
        result = private_original_relation(
            args.zip2, args.source, args.scratch, checkpoint,
        )
        phase = "safe_aggregate_json_output"
        out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf8")
        print("T2_FOAM_EXTERNAL_TARGET_RELATION_SAFE " + json.dumps(result, sort_keys=True))
        return 0
    except BaseException:
        print("T2_FOAM_EXTERNAL_TARGET_RELATION_SAFE " + json.dumps({
            "status": "blocked", "safe_phase": phase,
            "private_game_source_exposed": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
