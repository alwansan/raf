"""T2: original SHA-pinned 40 Unity level-scene component PPtr graph.

Unlike the previous 40 sharedassets Material census, this scans scene
Material.m_Shader and typed serialized MonoBehaviour/renderer PPtr structures.
Opaque component trees are counted as unparsed: never call missing link proven.
No game source names/paths/GUIDs/raw object bytes leave isolated runner.
"""
import argparse
import gc
import hashlib
import json
import re
import subprocess
from pathlib import Path

from scripts.w1_stage_zip2_owners import (
    ZIP2_SHA, PINS, fingerprint, safe, stage,
)
from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
from scripts.t2_foam_original_external_pptr_graph import (
    FOAM_OWNER, FOAM_PATHID, FOAM_RAW_SHA256,
    MAX_EXTERNALS, MAX_OBJECTS, MAX_MATERIALS,
)

SCENE_REGEX = re.compile(r"^Raft_Data/level[0-9]+$")
EXPECTED_SCENES = 40
EXPECTED_BYTES = 233237972
MAX_STAGED_BYTES = 256 * 1024**2
MAX_TREE_NODES = 50000
MAX_TREE_DEPTH = 24
COMPONENT_TYPES = {
    "MonoBehaviour", "MeshRenderer", "SkinnedMeshRenderer",
    "ParticleSystemRenderer", "LineRenderer", "TrailRenderer",
    "SpriteRenderer", "Renderer",
}


def select_original_levels(manifest):
    if not isinstance(manifest, list):
        raise ValueError("original_manifest_not_list")
    out = [r for r in manifest if isinstance(r, dict)
           and SCENE_REGEX.fullmatch(r.get("path", ""))]
    if len(out) != EXPECTED_SCENES:
        raise ValueError("original_level_count_drift")
    if (sum(r["bytes"] for r in out) != EXPECTED_BYTES
            or EXPECTED_BYTES > MAX_STAGED_BYTES):
        raise ValueError("original_level_total_byte_budget_drift")
    if len({r["path"] for r in out}) != EXPECTED_SCENES:
        raise ValueError("original_level_duplicate")
    if any(r["kind"] not in ("plain", "split") for r in out):
        raise ValueError("original_level_kind_malformed")
    return sorted(out, key=lambda x: int(x["path"].rsplit("level", 1)[1]))


def walk_tree_pptrs(tree):
    """Only structurally exact PPtrs; no raw binary filename heuristics.

    Keep node/depth budgets to bound broken/custom Unity typetrees.
    """
    stack = [(tree, 0)]
    count = 0
    while stack:
        node, depth = stack.pop()
        count += 1
        if count > MAX_TREE_NODES or depth > MAX_TREE_DEPTH:
            raise ValueError("unity_typetree_complexity_unbounded")
        if isinstance(node, dict):
            # The pair is sufficient for a *candidate*, only if both values
            # are typed exact int. Never serialize field names or values.
            if {"m_FileID", "m_PathID"} <= node.keys():
                f, p = node["m_FileID"], node["m_PathID"]
                if type(f) is int and type(p) is int:
                    yield f, p
                else:
                    raise ValueError("serialized_PPtr_value_type_invalid")
            for value in node.values():
                if isinstance(value, (dict, list, tuple)):
                    stack.append((value, depth + 1))
        elif isinstance(node, (list, tuple)):
            for value in node:
                if isinstance(value, (dict, list, tuple)):
                    stack.append((value, depth + 1))


def classify_scene_foam(owner, externals, material_rows, component_rows):
    """Categorize only actual source-owner+PathID candidate Foam references.

    material_rows: list of (fileID,PathID) or None (opaque).
    component_rows: list of lists of structured PPtrs or None (opaque).
    """
    if not isinstance(owner, str) or not SCENE_REGEX.fullmatch(owner):
        raise ValueError("non_scene_provider")
    if not isinstance(externals, list) or len(externals) > MAX_EXTERNALS:
        raise ValueError("original_scene_external_table_unbounded")
    if (not isinstance(material_rows, list) or len(material_rows) > MAX_MATERIALS
            or not isinstance(component_rows, list)
            or len(component_rows) > MAX_OBJECTS):
        raise ValueError("scene_object_count_unbounded")
    source_indices = set()
    for i, name in enumerate(externals, start=1):
        if (not isinstance(name, str) or not 0 < len(name) <= 1024
                or "\x00" in name):
            raise ValueError("original_source_path_malformed")
        if name.replace("\\", "/").rsplit("/", 1)[-1].casefold() == \
                "sharedassets0.assets":
            source_indices.add(i)
    counts = {
        "scene_Material_records": len(material_rows),
        "scene_Material_parsed": 0,
        "scene_Material_unparsed": 0,
        "scene_Component_records": len(component_rows),
        "scene_Component_parsed": 0,
        "scene_Component_unparsed": 0,
        "scene_Component_structural_PPtrs_examined": 0,
        "scene_foam_Material_Shader_PPtr_candidates": 0,
        "scene_foam_Component_PPtr_candidates": 0,
        "scene_other_Material_PPtrs_to_foam_owner": 0,
        "scene_other_Component_PPtrs_to_foam_owner": 0,
        "scene_foreign_local_PathID2420_not_foam": 0,
        "scene_external_fileID_out_of_range": 0,
        "scene_external_foam_owner_file_tables": len(source_indices),
    }
    def consider(row, source):
        if (not isinstance(row, (list, tuple)) or len(row) != 2
                or any(type(v) is not int for v in row)):
            raise ValueError("original_scene_PPtr_shape")
        f, p = row
        if f < 0 or p < 0 or (f == 0 and p == FOAM_PATHID):
            # Same numerical PathID in levelNN belongs to that scene,
            # not original Foam's sharedassets0 Shader object.
            if f == 0 and p == FOAM_PATHID:
                counts["scene_foreign_local_PathID2420_not_foam"] += 1
            else:
                counts["scene_external_fileID_out_of_range"] += 1
        elif f > len(externals):
            counts["scene_external_fileID_out_of_range"] += 1
        elif f in source_indices and p == FOAM_PATHID:
            counts["scene_foam_" + source + "_PPtr_candidates"] += 1
        elif f in source_indices and p != 0:
            counts["scene_other_" + source + "_PPtrs_to_foam_owner"] += 1
    for row in material_rows:
        if row is None:
            counts["scene_Material_unparsed"] += 1
        else:
            counts["scene_Material_parsed"] += 1
            consider(row, "Material_Shader")
    for refs in component_rows:
        if refs is None:
            counts["scene_Component_unparsed"] += 1
        else:
            if not isinstance(refs, list):
                raise ValueError("original_component_PPtr_list_shape")
            counts["scene_Component_parsed"] += 1
            counts["scene_Component_structural_PPtrs_examined"] += len(refs)
            for row in refs:
                consider(row, "Component")
    return counts


def safe_scene_summary(rows, bytes_verified):
    if not isinstance(rows, list) or len(rows) != EXPECTED_SCENES:
        raise ValueError("original_scene_count_not_complete")
    if bytes_verified != EXPECTED_BYTES:
        raise ValueError("original_scene_sha_staged_total_invalid")
    baseline = set(classify_scene_foam("Raft_Data/level0", [], [], []))
    if any(not isinstance(r, dict) or set(r) != baseline
           or any(type(v) is not int or v < 0 for v in r.values())
           or r["scene_Material_records"] != r["scene_Material_parsed"] + r["scene_Material_unparsed"]
           or r["scene_Component_records"] != r["scene_Component_parsed"] + r["scene_Component_unparsed"]
           for r in rows):
        raise ValueError("original_scene_graph_counts_invalid")
    aggregate = {k: sum(r[k] for r in rows) for k in sorted(baseline)}
    return {
        "status": "source_original_scene_40_Foam_PPtr_census",
        "original_ZIP2_commit_authenticated": True,
        "original_scene_SHA_authenticated_file_count": EXPECTED_SCENES,
        "original_scene_SHA_authenticated_bytes": bytes_verified,
        **aggregate,
        "original_Foam_Shader_asset_SHA_authenticated": True,
        "source_external_basename_proves_Unity_GUID": False,
        "opaque_MonoBehaviour_components_proved_no_Foam": False,
        "actual_rendered_Foam_or_CB0_upload_verified": False,
        "Android_Adreno_water_pixels_verified": False,
        "private_paths_names_GUIDs_raw_asset_bytes_exported": False,
    }


def inspect_original_scenes(zip2, scratch, checkpoint=lambda _: None):
    import UnityPy
    zip2, scratch = Path(zip2).absolute(), Path(scratch).absolute()
    safe(zip2)
    safe(scratch)
    if scratch.is_relative_to(zip2):
        raise ValueError("source_original_tree_not_output")
    checkpoint("pin_original_zip2_commit")
    sha = subprocess.check_output(
        ["git", "-C", str(zip2), "rev-parse", "HEAD"], text=True,
        stderr=subprocess.DEVNULL
    ).strip()
    if sha != ZIP2_SHA:
        raise ValueError("source_zip2_sha_drift")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    scenes = select_original_levels(manifest)
    checkpoint("source_sparse_checkout_40_scene_files")
    # Restrict to immutable ZIP2 checkout; other clients' worktrees untouched.
    paths = ["/RAFT_FILE_MANIFEST.tsv"]
    for row in scenes:
        name = row["path"]
        paths.append("/Raft/" + name + ("/*" if row["kind"] == "split" else ""))
    subprocess.run(["git", "-C", str(zip2), "sparse-checkout", "set",
                    "--no-cone", *paths],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   timeout=240)
    checkpoint("original_scene_sha_authentication")
    pins = {r["path"]: (r["bytes"], r["sha256"]) for r in scenes}
    staged = stage(zip2, scratch, pins)
    if (staged["provider_sha"] != ZIP2_SHA
            or staged["verified_bytes"] != EXPECTED_BYTES
            or staged["lfs_used"] is not False):
        raise ValueError("scene_bytes_not_source_authenticated")
    checkpoint("sha_original_foam_shader_independent_pin")
    # The original Foam shader object is authenticated independently by prior
    # 40-sharedasset CI; do not claim an absent stage checks Foam here.
    if PINS[FOAM_OWNER] != (
        115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"
    ) or len(FOAM_RAW_SHA256) != 64:
        raise ValueError("known_original_foam_pin_missing")
    # We only attest *known prior* Foam Shader SHA, not re-stage owner.
    checkpoint("parse_scene_Material_and_component_PPtrs")
    results = []
    for row in scenes:
        name = row["path"]
        path = scratch / name
        safe(path)
        if fingerprint(path) != pins[name]:
            raise ValueError("original_level_bytes_or_sha_mismatch")
        env = UnityPy.load(str(path))
        file = env.file
        objs = list(file.objects.values())
        if len(objs) > MAX_OBJECTS or len(file.externals) > MAX_EXTERNALS:
            raise ValueError("scene_original_object_external_table_budget")
        externals = [x.path for x in file.externals]
        matrows, componentrows = [], []
        for obj in objs:
            type_name = obj.type.name
            if type_name == "Material":
                if len(matrows) >= MAX_MATERIALS:
                    raise ValueError("scene_original_Material_limit")
                try:
                    tree = obj.read_typetree()
                    ptr = tree["m_Shader"]
                    matrows.append((ptr["m_FileID"], ptr["m_PathID"]))
                except (ValueError, KeyError, TypeError, AttributeError, EOFError):
                    matrows.append(None)
            elif type_name in COMPONENT_TYPES:
                try:
                    tree = obj.read_typetree()
                    componentrows.append(list(walk_tree_pptrs(tree)))
                except (ValueError, KeyError, TypeError, AttributeError, EOFError,
                        RecursionError, OverflowError):
                    componentrows.append(None)
        results.append(classify_scene_foam(name, externals, matrows, componentrows))
        del objs, file, env, matrows, componentrows
        gc.collect()
    result = safe_scene_summary(results, staged["verified_bytes"])
    # The checked Foam source pin in this run was metadata, not source bytes.
    result["original_Foam_Shader_asset_SHA_authenticated"] = False
    result["original_Foam_Shader_asset_SHA_attested_previous_CI"] = True
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip2", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    phase = "input"
    def ck(value):
        nonlocal phase
        phase = value
    try:
        output = args.out.absolute()
        safe(output)
        if (output.exists() or not output.parent.is_dir()
                or any(output.is_relative_to(x.absolute()) for x in
                       (args.zip2, args.scratch))):
            raise ValueError("unsafe_report_location")
        result = inspect_original_scenes(args.zip2, args.scratch, ck)
        output.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf8")
        print("T2_ORIGINAL_LEVEL_SCENE_FOAM_SAFE " + json.dumps(result, sort_keys=True))
        return 0
    except BaseException:
        print("T2_ORIGINAL_LEVEL_SCENE_FOAM_SAFE " + json.dumps({
            "status": "blocked", "safe_phase": phase,
            "private_source_paths_GUIDs_bytes_or_names_exposed": False
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
