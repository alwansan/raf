"""T2: SHA-original sharedassets Material->Foam Shader owner graph census.

Original proprietary bytes, file names, paths, materials, GUIDs and object
names stay in disposable CI scratch. Only bounded counts and booleans may
leave the runner. External filename+PathID is a candidate, not Unity GUID or
runtime binding.
"""
import argparse
import gc
import json
import re
import subprocess
from pathlib import Path

from scripts.t2_foam_original_external_pptr_graph import (
    FOAM_OWNER, FOAM_PATHID, FOAM_RAW_SHA256,
    MAX_EXTERNALS, MAX_MATERIALS, MAX_OBJECTS,
)
from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
from scripts.w1_stage_zip2_owners import PINS, ZIP2_SHA, fingerprint, safe, stage

EXPECTED_COUNT = 40
EXPECTED_BYTES = 474065455
OWNER_RE = re.compile(r"^Raft_Data/sharedassets[0-9]+\.assets$")
MAX_STAGING = 500 * 1024**2


def select_sharedowners(manifest):
    if not isinstance(manifest, list):
        raise ValueError("manifest_shape_invalid")
    rows = [
        row for row in manifest
        if isinstance(row, dict) and OWNER_RE.fullmatch(row.get("path", ""))
    ]
    if len(rows) != EXPECTED_COUNT:
        raise ValueError("sharedassets_original_inventory_count_drift")
    if (sum(row["bytes"] for row in rows) != EXPECTED_BYTES
            or EXPECTED_BYTES > MAX_STAGING):
        raise ValueError("sharedassets_original_inventory_budget_drift")
    if len({row["path"] for row in rows}) != EXPECTED_COUNT:
        raise ValueError("sharedassets_original_inventory_duplicate")
    actual = next((r for r in rows if r["path"] == FOAM_OWNER), None)
    if actual is None or (actual["bytes"], actual["sha256"]) != PINS[FOAM_OWNER]:
        raise ValueError("original_Foam_owner_manifest_pin_drift")
    if any(r["kind"] not in ("plain", "split") for r in rows):
        raise ValueError("original_asset_provider_kind_invalid")
    return rows


def material_shader_edges(owner, externals, pointers):
    """Source-free pure classifier; no original name, fileID or PPtr emitted."""
    if not isinstance(owner, str) or not OWNER_RE.fullmatch(owner):
        raise ValueError("untrusted_original_owner_tag")
    if (not isinstance(externals, list) or len(externals) > MAX_EXTERNALS
            or not isinstance(pointers, list) or len(pointers) > MAX_MATERIALS):
        raise ValueError("original_external_table_or_material_budget_exceeded")
    matched_external_indices = set()
    for i, path in enumerate(externals, 1):
        if (not isinstance(path, str) or not 0 < len(path) <= 1024
                or "\x00" in path):
            raise ValueError("original_unsafe_external_path")
        basename = path.replace("\\", "/").rsplit("/", 1)[-1].casefold()
        if basename == "sharedassets0.assets":
            matched_external_indices.add(i)
    counts = dict(
        material_rows=len(pointers),
        material_parsed=0,
        material_unparsed=0,
        local_foam_material_refs=0,
        external_foam_basename_pathid_candidates=0,
        external_foam_basename_other_pathids=0,
        foreign_local_PathID2420_not_foam=0,
        malformed_external_fileIDs=0,
        external_references_to_foam_owner=len(matched_external_indices),
    )
    for row in pointers:
        if row is None:
            counts["material_unparsed"] += 1
            continue
        if (not isinstance(row, (tuple, list)) or len(row) != 2
                or any(type(v) is not int or v < 0 for v in row)):
            raise ValueError("original_Material_PPtr_type_invalid")
        f, p = row
        counts["material_parsed"] += 1
        if f > len(externals):
            counts["malformed_external_fileIDs"] += 1
        elif f == 0 and p == FOAM_PATHID:
            if owner == FOAM_OWNER:
                counts["local_foam_material_refs"] += 1
            else:
                counts["foreign_local_PathID2420_not_foam"] += 1
        elif f in matched_external_indices and p == FOAM_PATHID:
            counts["external_foam_basename_pathid_candidates"] += 1
        elif f in matched_external_indices and p > 0:
            counts["external_foam_basename_other_pathids"] += 1
    if counts["material_parsed"] + counts["material_unparsed"] != len(pointers):
        raise ValueError("original_Material_pointer_counts_inconsistent")
    return counts


def safe_summary(catalog, owner_count, total_bytes):
    if (not isinstance(catalog, list) or len(catalog) != EXPECTED_COUNT
            or owner_count != EXPECTED_COUNT or total_bytes != EXPECTED_BYTES):
        raise ValueError("original_sharedassets_coverage_incomplete")
    keys = (
        "material_rows", "material_parsed", "material_unparsed",
        "local_foam_material_refs",
        "external_foam_basename_pathid_candidates",
        "external_foam_basename_other_pathids",
        "foreign_local_PathID2420_not_foam",
        "malformed_external_fileIDs",
        "external_references_to_foam_owner",
    )
    if any(not isinstance(r, dict) or set(r) != set(keys)
           or any(type(v) is not int or v < 0 for v in r.values())
           or r["material_rows"] != r["material_parsed"] + r["material_unparsed"]
           for r in catalog):
        raise ValueError("original_material_catalog_shape_invalid")
    sums = {key: sum(x[key] for x in catalog) for key in keys}
    return {
        "status": "original_SHA_authenticated_sharedassets_Foam_PPtr_census",
        "original_zip2_provider_SHA_verified": True,
        "original_Foam_owner_and_shader_SHA_verified": True,
        "sharedassets_original_files_SHA_verified": owner_count,
        "sharedassets_original_bytes_SHA_verified": total_bytes,
        **sums,
        "owners_with_local_foam_material_refs":
            sum(r["local_foam_material_refs"] > 0 for r in catalog),
        "owners_with_external_foam_PPtr_candidates":
            sum(r["external_foam_basename_pathid_candidates"] > 0 for r in catalog),
        "basename_candidate_is_original_Unity_GUID_verified": False,
        "Foam_actual_CB0_runtime_binding_verified": False,
        "Android_water_render_pixels_verified": False,
        "private_original_paths_names_GUIDs_or_raw_exported": False,
    }


def pinned_original_census(zip2, destination, checkpoint=lambda _: None):
    import hashlib
    import UnityPy
    zip2 = Path(zip2).absolute()
    destination = Path(destination).absolute()
    safe(zip2)
    safe(destination)
    if destination.is_relative_to(zip2):
        raise ValueError("original_provider_overwrite_refused")
    checkpoint("verify_immutable_provider")
    source_commit = subprocess.check_output(
        ["git", "-C", str(zip2), "rev-parse", "HEAD"], text=True,
        stderr=subprocess.DEVNULL,
    ).strip()
    if source_commit != ZIP2_SHA:
        raise ValueError("ZIP2_immutable_provider_SHA_drift")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    rows = select_sharedowners(manifest)
    # Sparse checkout reconfigures only the immutable original checkout,
    # never user's working branch nor shared worktrees.
    checkpoint("original_sparse_checkout")
    patterns = ["/RAFT_FILE_MANIFEST.tsv"]
    for item in rows:
        name = item["path"]
        patterns.append("/Raft/" + name
                        + ("/*" if item["kind"] == "split" else ""))
    subprocess.run(
        ["git", "-C", str(zip2), "sparse-checkout", "set", "--no-cone", *patterns],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        timeout=240,
    )

    checkpoint("SHA_stage_all_original_sharedassets")
    pins = {r["path"]: (r["bytes"], r["sha256"]) for r in rows}
    verified = stage(zip2, destination, pins)
    if verified.get("verified_bytes") != EXPECTED_BYTES or (
        verified.get("provider_sha") != ZIP2_SHA or verified.get("lfs_used")
    ):
        raise ValueError("original_asset_staging_sha_attestation_failed")

    checkpoint("read_original_Material_Shader_PPtrs")
    per_owner = []
    for row in rows:
        name = row["path"]
        file_path = destination / name
        safe(file_path)
        if fingerprint(file_path) != pins[name]:
            raise ValueError("original_asset_file_hash_drift")
        env = UnityPy.load(str(file_path))
        file = env.file
        objects = list(file.objects.values())
        if len(objects) > MAX_OBJECTS or len(file.externals) > MAX_EXTERNALS:
            raise ValueError("original_serialized_asset_object_budget_exceeded")
        external_names = [x.path for x in file.externals]
        pointer_rows = []
        found_foam = False
        for obj in objects:
            if name == FOAM_OWNER and obj.type.name == "Shader" and obj.path_id == FOAM_PATHID:
                if hashlib.sha256(obj.get_raw_data()).hexdigest() != FOAM_RAW_SHA256:
                    raise ValueError("original_foam_Shader_object_SHA_drift")
                found_foam = True
            elif obj.type.name == "Material":
                if len(pointer_rows) >= MAX_MATERIALS:
                    raise ValueError("original_Material_count_exceeds_budget")
                try:
                    tree = obj.read_typetree()
                    ptr = tree["m_Shader"]
                    pointer_rows.append((ptr["m_FileID"], ptr["m_PathID"]))
                except (ValueError, KeyError, AttributeError, TypeError, EOFError):
                    pointer_rows.append(None)
        if name == FOAM_OWNER and not found_foam:
            raise ValueError("original_Foam_Shader_PathID_not_SHA_authenticated")
        per_owner.append(material_shader_edges(name, external_names, pointer_rows))
        del objects, file, env, pointer_rows
        gc.collect()

    return safe_summary(per_owner, len(rows), verified["verified_bytes"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2", required=True, type=Path)
    p.add_argument("--scratch", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    phase = "input_guard"
    def ck(value):
        nonlocal phase
        phase = value
    try:
        out = args.out.absolute()
        safe(out)
        if (out.exists() or not out.parent.is_dir()
                or any(out.is_relative_to(root.absolute()) for root in
                       (args.zip2, args.scratch))):
            raise ValueError("original_safe_output_rule")
        result = pinned_original_census(args.zip2, args.scratch, ck)
        out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf8")
        print("T2_ORIGINAL_FOAM_HOST_SAFE " + json.dumps(result, sort_keys=True))
        return 0
    except BaseException:
        print("T2_ORIGINAL_FOAM_HOST_SAFE " + json.dumps({
            "status": "blocked",
            "phase": phase,
            "private_game_bytes_names_paths_or_GUID_exported": False
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
