"""T2 original Unity FileIdentifier GUID evidence for two external Shader PPtrs.

Input contains proprietary source Unity bytes. Keep GUID/path and raw objects in
private runner staging, never print or return them. FileIdentifier.guid alone
does not give the immutable target asset's independently authenticated GUID.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
from collections import defaultdict

from scripts.t2_foam_original_external_pptr_graph import FOAM_OWNER, FOAM_PATHID, MAX_EXTERNALS, MAX_MATERIALS, MAX_OBJECTS, external_provider_key
from scripts.t2_foam_original_manifest_pptr import (
    run as original_source_stage,
    parse_original_manifest,
    resolve_unmapped_external_materials,
    load_original_foam_material_edges,
)
from scripts.w1_stage_zip2_owners import PINS, safe, fingerprint


def normalized_guid(value):
    """The binary GUID is a 16-byte opaque value; never interpret as name."""
    if type(value) is not bytes or len(value) != 16:
        raise ValueError("external_file_identifier_GUID_not_16_bytes")
    return value


def classify_guid_edges(rows):
    """Return safe aggregates; file IDs, GUID values and paths stay private.

    Input each row: (file_id, private_target_key, 16_bytes_GUID, type_int).
    """
    if not isinstance(rows, list) or len(rows) != 2:
        raise ValueError("original_two_target_rows_required")
    by_file_id = {}
    by_target = defaultdict(set)
    type_counts = {n: 0 for n in range(4)}
    zero = 0
    for row in rows:
        if not isinstance(row, (tuple, list)) or len(row) != 4:
            raise ValueError("external_GUID_row_shape")
        file_id, target, raw_guid, target_type = row
        if (type(file_id) is not int or file_id <= 0 or
                not isinstance(target, str) or not 0 < len(target) <= 1024 or
                type(target_type) is not int or target_type not in type_counts):
            raise ValueError("external_GUID_row_value")
        guid = normalized_guid(raw_guid)
        signature = (target, guid, target_type)
        if file_id in by_file_id and by_file_id[file_id] != signature:
            raise ValueError("same_fileID_has_different_identifiers")
        by_file_id[file_id] = signature
        by_target[target].add(guid)
        type_counts[target_type] += 1
        zero += guid == b"\x00" * 16
    nonzero = {g for _, g, _ in by_file_id.values() if g != b"\x00" * 16}
    return {
        "external_original_Shader_refs": len(rows),
        "external_unique_fileIDs": len(by_file_id),
        "external_unique_filename_targets": len(by_target),
        "external_GUID_zero_rows": zero,
        "external_GUID_nonzero_rows": len(rows) - zero,
        "external_distinct_nonzero_GUIDs": len(nonzero),
        "external_same_target_distinct_GUID_conflicts":
            sum(max(0, len(values) - 1) for values in by_target.values()),
        "external_type_0_rows": type_counts[0],
        "external_type_1_rows": type_counts[1],
        "external_type_2_rows": type_counts[2],
        "external_type_3_rows": type_counts[3],
        "original_file_identifier_values_published": False,
        "GUID_is_independent_original_target_authority": False,
    }


def target_recipient_catalog(file, original_foam_owner=FOAM_OWNER):
    """Count only target SerializedFile reciprocal *candidate* edges."""
    if not hasattr(file, "externals") or not hasattr(file, "objects"):
        raise ValueError("target_serialized_file_shape")
    externals = list(file.externals)
    objs = list(file.objects.values())
    if len(externals) > MAX_EXTERNALS or len(objs) > MAX_OBJECTS:
        raise ValueError("target_source_unbounded")
    basename = PurePosixPath(original_foam_owner).name.casefold()
    local_source_fileids = set()
    nonzero_guids = 0
    for idx, external in enumerate(externals, 1):
        name = getattr(external, "path", None)
        if not isinstance(name, str) or not 0 < len(name) <= 1024 or "\x00" in name:
            raise ValueError("original_target_external_path_invalid")
        raw = normalized_guid(getattr(external, "guid", None))
        t = getattr(external, "type", None)
        if type(t) is not int or t not in (0, 1, 2, 3):
            raise ValueError("original_target_external_type_invalid")
        if name.replace("\\", "/").rsplit("/", 1)[-1].casefold() == basename:
            local_source_fileids.add(idx)
            nonzero_guids += raw != b"\x00" * 16
    materials, exact_foam_ptrs = 0, 0
    for obj in objs:
        if obj.type.name != "Material":
            continue
        materials += 1
        if materials > MAX_MATERIALS:
            raise ValueError("target_materials_unbounded")
        ptr = obj.read_typetree()["m_Shader"]
        f, p = ptr["m_FileID"], ptr["m_PathID"]
        if type(f) is not int or type(p) is not int or f < 0 or p < 0:
            raise ValueError("original_target_material_pointer_malformed")
        if f in local_source_fileids and p == FOAM_PATHID:
            exact_foam_ptrs += 1
    return {
        "target_file_external_identifier_count": len(externals),
        "target_file_material_count": materials,
        "target_reciprocal_original_Foam_owner_name_candidates": len(local_source_fileids),
        "target_reciprocal_original_Foam_owner_nonzero_GUID_count": nonzero_guids,
        "target_material_to_Foam_owner_and_PathID_candidates": exact_foam_ptrs,
        "reciprocal_owner_name_is_independent_GUID_proof": False,
    }


def inspect_original(zip2, owner, target_dir, phase=lambda _: None):
    import UnityPy
    zip2, owner, target_dir = [Path(v).absolute() for v in (zip2, owner, target_dir)]
    safe(zip2)
    safe(owner)
    safe(target_dir)
    phase("original_sha_target_staging")
    baseline = original_source_stage(zip2, owner, target_dir)
    if any(baseline.get(k) != value for k, value in (
        ("original_zip2_commit_authenticated", True),
        ("original_Foam_Shader_object_SHA_authenticated", True),
        ("original_sharedassets0_SHA_authenticated", True),
        ("unmapped", 2),
        ("verified_typed_Shader_PPtrs", 2),
        ("verified_bytes_staged", 758412),
    )):
        raise ValueError("original_source_or_external_target_attestation_drift")
    phase("original_sharedassets0_FileIdentifier_Guids")
    original_file = owner / FOAM_OWNER
    safe(original_file)
    if fingerprint(original_file) != PINS[FOAM_OWNER]:
        raise ValueError("original_foam_owner_sha_mismatch")
    file = UnityPy.load(str(original_file)).file
    pointers = []
    for obj in file.objects.values():
        if obj.type.name != "Material":
            continue
        ptr = obj.read_typetree()["m_Shader"]
        pointers.append((ptr["m_FileID"], ptr["m_PathID"]))
    if len(pointers) != 351 or len(file.externals) > MAX_EXTERNALS:
        raise ValueError("original_Material_file_table_baseline_drift")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    private_table = [x.path for x in file.externals]
    counts, target_candidates = resolve_unmapped_external_materials(
        private_table, pointers, manifest)
    if (counts["total_external"] != 7 or counts["known_four_owner"] != 5 or
            len(target_candidates) != 2):
        raise ValueError("original_external_material_counts_drift")
    target_paths = {x[0] for x in target_candidates}
    if len(target_paths) != 1:
        raise ValueError("original_target_not_one_SHA_owner")
    # Resolve to *original* fileIDs by checking Material PPtrs and typed target.
    # Filename names are held only in memory. This step does not print them.
    rows = []
    for fid, pathid in pointers:
        if fid <= 0 or pathid <= 0:
            continue
        ext = file.externals[fid - 1]
        name = str(ext.path).replace("\\", "/").rsplit("/", 1)[-1]
        candidates = [m for m in manifest if
                      PurePosixPath(m["path"]).name.casefold() == name.casefold()]
        if (len(candidates) != 1 or candidates[0]["path"] not in target_paths
                or (candidates[0]["path"], candidates[0]["sha256"], pathid)
                not in target_candidates):
            continue
        rows.append((fid, candidates[0]["path"], ext.guid, ext.type))
    result = classify_guid_edges(rows)

    phase("original_target_reciprocal_FileIdentifier_catalog")
    only_target = next(iter(target_paths))
    candidate = next((r for r in manifest if r["path"] == only_target), None)
    path = target_dir / only_target
    safe(path)
    if (candidate is None or not path.is_file() or
            fingerprint(path) != (candidate["bytes"], candidate["sha256"])):
        raise ValueError("original_target_byte_hash_drift")
    file_target = UnityPy.load(str(path)).file
    reciprocal = target_recipient_catalog(file_target)
    return {
        "status": "original_SHA_verified_external_GUID_shape_and_reciprocal_graph",
        "original_ZIP2_SHA_verified": True,
        "original_Foam_owner_object_and_source_SHA_verified": True,
        "original_target_file_758412_bytes_SHA_verified": True,
        **result,
        **reciprocal,
        "original_Unity_target_file_GUID_independently_authenticated": False,
        "Foam_render_material_binding_verified": False,
        "Unity_ShaderLab_Adreno_pixels_verified": False,
        "private_original_names_GUIDs_paths_raw_published": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    phase = "input_guard"
    def checkpoint(value):
        nonlocal phase
        phase = value
    try:
        out = a.out.absolute()
        safe(out)
        if (out.exists() or not out.parent.is_dir() or
            any(out.is_relative_to(x.absolute()) for x in
                (a.zip2, a.source, a.target))):
            raise ValueError("unsafe_output_path")
        result = inspect_original(a.zip2, a.source, a.target, checkpoint)
        out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf8")
        print("T2_ORIGINAL_EXTERNAL_GUID_SAFE " + json.dumps(result, sort_keys=True))
        return 0
    except BaseException:
        print("T2_ORIGINAL_EXTERNAL_GUID_SAFE " + json.dumps({
            "status": "blocked", "safe_phase": phase,
            "private_original_data_disclosed": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
