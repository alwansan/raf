"""Find the original underwater shader and inventory serialized pass topology."""
import argparse
import json
from pathlib import Path
import subprocess

from gfxlab.tools.water_scene_links import select_asset_owners, OWNER, OWNER_PIN

TARGET = "UltimateWater/Underwater/Base IME"


def inspect(zip2, scratch):
    import UnityPy
    from scripts.t2_original_scene_foam_component_scan import select_original_levels
    from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
    from scripts.w1_stage_zip2_owners import ZIP2_SHA, stage

    head = subprocess.check_output(["git", "-C", str(zip2), "rev-parse", "HEAD"], text=True).strip()
    if head != ZIP2_SHA:
        raise ValueError("ZIP2 revision mismatch")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    rows = select_asset_owners(manifest) + select_original_levels(manifest)
    paths = ["/Raft/" + row["path"] + ("/*" if row["kind"] == "split" else "") for row in rows]
    subprocess.run(["git", "-C", str(zip2), "sparse-checkout", "set", "--no-cone",
                    "/RAFT_FILE_MANIFEST.tsv", "/Raft/" + OWNER, *paths], check=True, timeout=300)
    pins = {row["path"]: (row["bytes"], row["sha256"]) for row in rows}
    pins[OWNER] = OWNER_PIN
    staged = stage(zip2, scratch, pins)
    if staged["verified_bytes"] != sum(size for size, _ in pins.values()) or staged["lfs_used"]:
        raise ValueError("Source coverage mismatch")

    candidates = []
    shaders = 0
    for owner in pins:
        env = UnityPy.load(str(scratch / owner))
        for obj in env.file.objects.values():
            if obj.type.name != "Shader":
                continue
            shaders += 1
            tree = obj.read_typetree(check_read=False)
            form = tree.get("m_ParsedForm")
            if not isinstance(form, dict):
                raise ValueError("Serialized shader form missing")
            if form.get("m_Name") != TARGET and tree.get("m_Name") != TARGET:
                continue
            passes = [sub["m_Passes"] for sub in form["m_SubShaders"]]
            candidates.append({
                "subshader_pass_counts": [len(group) for group in passes],
                "pass_types": [[item["m_Type"] for item in group] for group in passes],
                "device_indices": [1, 3],
                "subshaders_with_both_indices": sum(len(group) >= 4 for group in passes),
            })
    if len(candidates) != 1:
        raise ValueError("Original underwater shader missing or ambiguous")
    return {"zip2_sha": head, "serialized_owners": len(pins), "shader_objects": shaders,
            "original_topology": candidates[0], "unity_runtime_verified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("zip2", "scratch", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(inspect(args.zip2, args.scratch), indent=2) + "\n")
