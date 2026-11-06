"""T2: SHA-original 40-scene m_Script -> exact managed TypeDef subset.
No original source strings, object IDs, GUIDs or bytes in public output.
Provenance is source-structural, NOT runtime Foam rendering or Android proof.
"""
import argparse
import gc
import json
import subprocess
from pathlib import Path

from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
from scripts.t2_original_scene_foam_component_scan import (
    select_original_levels, walk_tree_pptrs, EXPECTED_BYTES, EXPECTED_SCENES,
)
from scripts.t2_original_opaque_monoscript_head import script_header_ptr, EXPECTED_OPAQUE
from scripts.t2_original_monoscript_target_join import match_private_external_to_original_manifest
from scripts.t2_original_monoscript_managed_class_bridge import (
    MONO_OWNER_BYTES, MANAGED_BYTES, unique_original_source_rows,
    normalized_script_record, type_catalog, classify_script_metadata,
)
from scripts.w1_stage_zip2_owners import ZIP2_SHA, fingerprint, safe, stage
from scripts.t2_foam_original_external_pptr_graph import MAX_EXTERNALS, MAX_OBJECTS

EXPECTED_REFERENCED_TARGETS = 473
MAX_REFERENCES = 100000


def exact_private_referenced_targets(refs, manifest, expected_owner):
    """Only original file identity + real PathID, never guessed local IDs."""
    if (type(refs) is not list or not 0 < len(refs) <= MAX_REFERENCES
            or type(expected_owner) is not str or not expected_owner):
        raise ValueError("source_referenced_targets_shape_invalid")
    ids = set()
    for row in refs:
        if (type(row) is not tuple or len(row) != 2
                or type(row[0]) is not str
                or type(row[1]) is not int or row[1] <= 0):
            raise ValueError("source_script_pointer_invalid")
        kind, source = match_private_external_to_original_manifest(row[0], manifest)
        if kind != "unique" or source["path"] != expected_owner:
            raise ValueError("original_script_target_owner_unknown_or_foreign")
        ids.add(row[1])
    return ids


def select_class_records_by_exact_pathid(ref_ids, meta_by_pid):
    if (type(ref_ids) is not set or not ref_ids
            or type(meta_by_pid) is not dict
            or any(type(x) is not int or x <= 0 for x in ref_ids)):
        raise ValueError("original_scene_script_selection_invalid")
    if ref_ids - meta_by_pid.keys():
        raise ValueError("original_scene_script_target_missing_or_mistyped")
    return [meta_by_pid[x] for x in sorted(ref_ids)]


def inspect_sha_original(zip2, scratch, checkpoint=lambda _: None):
    import UnityPy
    import dnfile
    zip2, scratch = Path(zip2).absolute(), Path(scratch).absolute()
    safe(zip2)
    safe(scratch)
    if scratch.is_relative_to(zip2) or not scratch.is_dir():
        raise ValueError("original_scratch_invalid")
    checkpoint("authenticate_immutable_original_manifest")
    sha = subprocess.check_output(
        ["git", "-C", str(zip2), "rev-parse", "HEAD"],
        text=True, stderr=subprocess.DEVNULL).strip()
    if sha != ZIP2_SHA:
        raise ValueError("original_provider_sha_drift")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    scenes = select_original_levels(manifest)
    if len(scenes) != EXPECTED_SCENES:
        raise ValueError("original_40_level_scene_count_drift")
    mono, dll = unique_original_source_rows(manifest)
    owners = [*scenes, mono, dll]
    expected_bytes = EXPECTED_BYTES + MONO_OWNER_BYTES + MANAGED_BYTES
    if len({x["path"] for x in owners}) != len(owners):
        raise ValueError("duplicate_source_owners")
    patterns = ["/RAFT_FILE_MANIFEST.tsv"]
    for entry in owners:
        patterns.append("/Raft/" + entry["path"] +
                        ("/*" if entry["kind"] == "split" else ""))
    checkpoint("private_sparse_checkout")
    subprocess.run(["git", "-C", str(zip2), "sparse-checkout",
                    "set", "--no-cone", *patterns], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    pins = {x["path"]: (x["bytes"], x["sha256"]) for x in owners}
    checkpoint("sha_validate_original_sources")
    staged = stage(zip2, scratch, pins)
    if (staged["provider_sha"] != ZIP2_SHA
            or staged["verified_bytes"] != expected_bytes
            or staged["lfs_used"] is not False):
        raise ValueError("original_combined_SHA_stage_failure")
    for entry in owners:
        if fingerprint(scratch / entry["path"]) != pins[entry["path"]]:
            raise ValueError("original_SHA_owner_drift")

    checkpoint("source_original_scene_script_refs")
    refs = []
    for entry in scenes:
        env = UnityPy.load(str(scratch / entry["path"]))
        file = env.file
        objs = list(file.objects.values())
        if len(objs) > MAX_OBJECTS or len(file.externals) > MAX_EXTERNALS:
            raise ValueError("scene_source_object_budget")
        externals = [x.path for x in file.externals]
        for obj in objs:
            if obj.type.name != "MonoBehaviour":
                continue
            try:
                tree = obj.read_typetree()
                list(walk_tree_pptrs(tree))
                continue
            except Exception:
                pass
            fid, pid = script_header_ptr(obj.parse_monobehaviour_head())
            if not 0 < fid <= len(externals) or pid <= 0:
                raise ValueError("opaque_scene_script_ptr_invalid")
            if len(refs) >= MAX_REFERENCES:
                raise ValueError("scene_script_reference_budget")
            refs.append((externals[fid - 1], pid))
        del objs, file, env
        gc.collect()
    if len(refs) != EXPECTED_OPAQUE:
        raise ValueError("scene_script_references_cardinality_drift")
    referenced = exact_private_referenced_targets(refs, manifest, mono["path"])
    if len(referenced) != EXPECTED_REFERENCED_TARGETS:
        raise ValueError("scene_referenced_script_set_cardinality_drift")
    del refs

    checkpoint("source_original_actual_referenced_script_metadata")
    env = UnityPy.load(str(scratch / mono["path"]))
    objs = list(env.file.objects.values())
    if len(objs) > MAX_OBJECTS:
        raise ValueError("mono_target_object_budget")
    all_scripts, metadata = 0, {}
    for obj in objs:
        if obj.type.name != "MonoScript":
            continue
        all_scripts += 1
        pid = int(obj.path_id)
        if pid <= 0 or (pid in referenced and pid in metadata):
            raise ValueError("typed_target_duplicate_script_ID")
        if pid not in referenced:
            continue
        try:
            metadata[pid] = normalized_script_record(obj.read_typetree())
        except Exception:
            metadata[pid] = None
    selected = select_class_records_by_exact_pathid(referenced, metadata)
    del objs, env, metadata, referenced
    gc.collect()
    if all_scripts != 3827:
        raise ValueError("original_typed_target_total_changed")
    checkpoint("source_original_managed_typedef_exact_class_join")
    pe = dnfile.dnPE(str(scratch / dll["path"]))
    if (pe.net is None or pe.net.mdtables is None
            or pe.net.mdtables.TypeDef is None):
        raise ValueError("original_managed_TypeDef_unreadable")
    type_rows = [(str(x.TypeNamespace), str(x.TypeName))
                 for x in pe.net.mdtables.TypeDef.rows]
    catalog = type_catalog(type_rows)
    counts = classify_script_metadata(selected, catalog)
    if counts["original_typed_MonoScript_objects_total"] != EXPECTED_REFERENCED_TARGETS:
        raise ValueError("source_scene_subset_partition_drift")
    return {
        "status": "source_original_473_scene_MonoScript_managed_TypeDef_subset",
        "original_immutable_zip2_SHA_authenticated": True,
        "original_scene_SHA_file_count": len(scenes),
        "original_scene_SHA_bytes": EXPECTED_BYTES,
        "original_MonoScript_owner_SHA_bytes": MONO_OWNER_BYTES,
        "original_managed_Assembly_SHA_bytes": MANAGED_BYTES,
        "original_combined_SHA_bytes": expected_bytes,
        "original_opaque_scene_m_Script_references": EXPECTED_OPAQUE,
        "original_distinct_scene_referenced_MonoScripts": EXPECTED_REFERENCED_TARGETS,
        "original_full_MonoScript_owner_typed_objects": all_scripts,
        "original_managed_TypeDef_rows": len(type_rows),
        "original_managed_distinct_TypeDef_keys": len(catalog),
        **counts,
        "original_custom_MonoBehaviour_fields_reconstructed": False,
        "original_Foam_material_Shader_or_CB0_bound": False,
        "original_Unity_GUID_runtime_identity_verified": False,
        "Android_water_pixels_verified": False,
        "private_original_names_IDs_or_raw_bytes_exported": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2", required=True, type=Path)
    p.add_argument("--scratch", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args(argv)
    phase = "input"
    def progress(x):
        nonlocal phase
        phase = x
    try:
        out = a.out.absolute()
        safe(out)
        if (out.exists() or not out.parent.is_dir()
                or any(out.is_relative_to(x.absolute()) for x in (a.zip2, a.scratch))):
            raise ValueError("unsafe_private_source_report_path")
        data = inspect_sha_original(a.zip2, a.scratch, progress)
        if any(type(v) not in (int, bool, str) for v in data.values()):
            raise ValueError("unsafe_original_aggregate_shape")
        out.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf8")
        print("T2_ORIGINAL_SCENE_MONO_SUBSET_SAFE " + json.dumps(data, sort_keys=True))
        return 0
    except BaseException:
        print("T2_ORIGINAL_SCENE_MONO_SUBSET_SAFE " + json.dumps({
            "status": "blocked", "safe_phase": phase,
            "original_source_identifiers_or_bytes_exported": False}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
