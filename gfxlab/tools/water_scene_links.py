"""Resolve serialized scene MonoBehaviour links against the original script catalog."""
import argparse
from collections import Counter
import gc
import json
from pathlib import Path, PurePosixPath
import subprocess
import re

from gfxlab.tools.water_managed_census import FAMILIES, ANCHORS

OWNER = "Raft_Data/globalgamemanagers.assets"
OWNER_PIN = (758412, "b549af329d48244d80f28cb3cce6cd0b17769176081c249dc4646e1d62c58e28")


def classify(namespace, name):
    namespace, name = namespace.lower(), name.lower()
    water = ("water" in namespace or "water" in name or name in ANCHORS
             or any(term in name for term in ("buoyan", "gerstner", "wavesrender")))
    return water, [key for key, terms in FAMILIES.items() if water and any(term in name for term in terms)]


def select_asset_owners(manifest):
    pattern = re.compile(r"Raft_Data/(?:sharedassets\d+|resources)\.assets")
    rows = [row for row in manifest if pattern.fullmatch(row['path'])]
    if len(rows) != 41 or len({row['path'] for row in rows}) != 41:
        raise ValueError('Asset owner count mismatch')
    if sum(row['bytes'] for row in rows) != 585598971:
        raise ValueError('Asset owner byte budget mismatch')
    return rows


def scan(zip2, scratch, asset_owners=False):
    import UnityPy
    from scripts.t2_original_scene_foam_component_scan import select_original_levels, EXPECTED_BYTES
    from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
    from scripts.w1_stage_zip2_owners import ZIP2_SHA, fingerprint, stage

    sha = subprocess.check_output(["git", "-C", str(zip2), "rev-parse", "HEAD"], text=True).strip()
    if sha != ZIP2_SHA:
        raise ValueError("ZIP2 drift")
    rows = select_original_levels(parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv"))
    paths = ["/Raft/" + row["path"] + ("/*" if row["kind"] == "split" else "") for row in rows]
    subprocess.run(["git", "-C", str(zip2), "sparse-checkout", "set", "--no-cone",
                    "/RAFT_FILE_MANIFEST.tsv", "/Raft/" + OWNER, *paths], check=True, timeout=300)
    pins = {row["path"]: (row["bytes"], row["sha256"]) for row in rows}
    pins[OWNER] = OWNER_PIN
    result = stage(zip2, scratch, pins)
    if result["verified_bytes"] != EXPECTED_BYTES + OWNER_PIN[0] or result["lfs_used"] is not False:
        raise ValueError("Staged coverage mismatch")

    script_env = UnityPy.load(str(scratch / OWNER))
    catalog = {}
    for obj in script_env.file.objects.values():
        if obj.type.name == "MonoScript":
            script = obj.read()
            catalog[obj.path_id] = classify(script.m_Namespace, script.m_ClassName)
    if not catalog or not any(water for water, _ in catalog.values()):
        raise ValueError("Script catalog empty")
    counts = Counter()
    instances = Counter()
    scenes_by_family = Counter()
    water_scenes = 0
    for row in rows:
        path = scratch / row["path"]
        if fingerprint(path) != pins[row["path"]]:
            raise ValueError("Scene pin mismatch")
        env = UnityPy.load(str(path))
        owners = [PurePosixPath(item.path.replace(chr(92), "/")).name.lower()
                  for item in env.file.externals]
        found = set()
        scene_has_water = False
        for obj in env.file.objects.values():
            if obj.type.name != "MonoBehaviour":
                continue
            counts["components"] += 1
            try:
                pointer = obj.read_typetree(check_read=False)["m_Script"]
                file_id, path_id = pointer["m_FileID"], pointer["m_PathID"]
            except (ValueError, KeyError, TypeError, AttributeError, EOFError, RuntimeError, NotImplementedError):
                counts["unreadable_script_pointer"] += 1
                continue
            if type(file_id) is not int or type(path_id) is not int:
                counts["unreadable_script_pointer"] += 1
            elif path_id == 0:
                counts["null_script_pointer"] += 1
            elif not 1 <= file_id <= len(owners) or owners[file_id - 1] != Path(OWNER).name:
                counts["outside_catalog"] += 1
            elif path_id not in catalog:
                counts["catalog_target_missing"] += 1
            else:
                counts["resolved_catalog"] += 1
                water, families = catalog[path_id]
                if water:
                    counts["water_name_candidates"] += 1
                    scene_has_water = True
                    instances.update(families)
                    found.update(families)
        water_scenes += scene_has_water
        scenes_by_family.update(found)
        del env
        gc.collect()
    if not counts["resolved_catalog"]:
        raise ValueError("No scene scripts resolved")
    return {"zip2_sha": sha, "scenes": len(rows), "catalog_scripts": len(catalog),
            "water_candidate_scenes": water_scenes, "counts": dict(counts),
            "families": {name: {"components": instances[name], "scenes": scenes_by_family[name]}
                         for name in FAMILIES}, "runtime_verified": False}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("zip2", "scratch", "output"):
        cli.add_argument(name, type=Path)
    args = cli.parse_args()
    report = scan(args.zip2, args.scratch)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
