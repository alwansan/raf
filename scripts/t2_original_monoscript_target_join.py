"""T2: authenticate actual original external MonoBehaviour.m_Script target objects.

The previous original SHA source run proved all 55,328 opaque scene
MonoBehaviour headers point to other external files, not sharedassets0.
This independent experiment classifies genuine *external paths* through the
immutable original file manifest, SHA-reconstructs bounded target owners, then
checks referenced PathIDs are real MonoScript object types.

No original field/class names, GUIDs, provider paths or raw bytes leave
private runner memory. Basename+typed PathID is still not a Unity GUID or
runtime Foam shader identity. Never write back to original serialized files.
"""
import argparse
import gc
import json
import subprocess
from collections import defaultdict
from pathlib import Path

from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
from scripts.t2_original_opaque_monoscript_head import (
    script_header_ptr, EXPECTED_OPAQUE,
)
from scripts.t2_original_scene_foam_component_scan import (
    select_original_levels, walk_tree_pptrs, EXPECTED_BYTES, COMPONENT_TYPES,
)
from scripts.w1_stage_zip2_owners import (
    ZIP2_SHA, fingerprint, stage, safe,
)
from scripts.t2_foam_original_external_pptr_graph import (
    MAX_EXTERNALS, MAX_OBJECTS,
)

MAX_TARGET_FILES = 12
MAX_TARGET_BYTES = 256 * 1024**2
MAX_ALL_STAGED_BYTES = 560 * 1024**2
MAX_TARGET_PATHIDS = 120000


def match_private_external_to_original_manifest(path, manifest):
    """Return private original manifest row when basename unique; else status.

    A strict manifest candidate is not independent Unity GUID authentication.
    """
    if (not isinstance(path, str) or not 0 < len(path) <= 1024 or
            "\x00" in path or not isinstance(manifest, list)):
        raise ValueError("untrusted_source_external_manifest_argument")
    basename = path.replace("\\", "/").rsplit("/", 1)[-1].casefold()
    if not basename or basename in (".", ".."):
        raise ValueError("unsafe_external_basename")
    matches = [r for r in manifest if isinstance(r, dict)
               and isinstance(r.get("path"), str)
               and r["path"].replace("\\", "/").rsplit("/", 1)[-1].casefold()
               == basename]
    if len(matches) > 1:
        return "ambiguous", None
    if not matches:
        return "missing", None
    row = matches[0]
    if (not isinstance(row.get("bytes"), int) or row["bytes"] <= 0
            or not isinstance(row.get("sha256"), str)
            or len(row["sha256"]) != 64
            or row.get("kind") not in ("plain", "split")):
        raise ValueError("original_manifest_target_shape_invalid")
    return "unique", row


def typecheck_typed_MonoScript_target_ids(pathids, typed_ids):
    """Opaque target IDs remain private; output counts only."""
    if (not isinstance(pathids, list) or len(pathids) > MAX_TARGET_PATHIDS
            or not isinstance(typed_ids, set)
            or any(type(pid) is not int or pid <= 0 for pid in typed_ids)
            or any(type(pid) is not int or pid <= 0 for pid in pathids)):
        raise ValueError("original_typed_MonoScript_target_row_shape")
    typed = sum(pid in typed_ids for pid in pathids)
    return {
        "script_refs_to_SHA_original_typed_MonoScript_objects": typed,
        "script_refs_to_SHA_original_absent_or_other_type_PathIDs": len(pathids)-typed,
        "distinct_referenced_typed_MonoScript_objects": len(set(pathids)&typed_ids),
        "distinct_referenced_non_MonoScript_PathIDs": len(set(pathids)-typed_ids),
    }


def validated_safe_classification(all_refs, manifest):
    """Refs are private (original external path, original PathID) tuples.

    Group by SHA-manifest *candidate* target without exporting original names.
    Return typed-staging jobs separately in private memory.
    """
    if (not isinstance(all_refs, list) or len(all_refs) != EXPECTED_OPAQUE
            or not isinstance(manifest, list)):
        raise ValueError("source_original_script_reference_count_drift")
    grouped, unresolved = defaultdict(list), {"missing": 0, "ambiguous": 0}
    seen_paths = set()
    for row in all_refs:
        if (not isinstance(row, (list, tuple)) or len(row) != 2
                or type(row[1]) is not int or row[1] <= 0):
            raise ValueError("source_original_header_script_row_invalid")
        private_path, pid = row
        seen_paths.add(private_path)
        category, item = match_private_external_to_original_manifest(private_path, manifest)
        if category != "unique":
            unresolved[category] += 1
        else:
            grouped[item["path"]].append(pid)
    if len(seen_paths) > MAX_TARGET_PATHIDS:
        raise ValueError("original_script_source_count_unbounded")
    source_references = {
        "script_refs_from_opaque_original_MonoBehaviours": len(all_refs),
        "source_external_path_variants": len(seen_paths),
        "original_unique_basename_candidate_ref_rows":
            sum(len(x) for x in grouped.values()),
        "original_missing_manifest_candidate_ref_rows": unresolved["missing"],
        "original_ambiguous_manifest_candidate_ref_rows": unresolved["ambiguous"],
        "original_unique_manifest_candidate_target_files": len(grouped),
    }
    if sum(source_references[k] for k in (
        "original_unique_basename_candidate_ref_rows",
        "original_missing_manifest_candidate_ref_rows",
        "original_ambiguous_manifest_candidate_ref_rows",
    )) != EXPECTED_OPAQUE:
        raise ValueError("source_original_manifest_ref_partition_invalid")
    return source_references, grouped


def choose_bounded_SHA_original_targets(grouped, manifest):
    lookup = {row["path"]: row for row in manifest}
    if not isinstance(grouped, dict):
        raise ValueError("target_job_shape")
    staged, skipped, used = {}, 0, 0
    for name in sorted(grouped):
        item = lookup.get(name)
        if item is None or not isinstance(grouped[name], list):
            raise ValueError("manifest_target_job_not_authenticated")
        size = item["bytes"]
        if (len(staged) >= MAX_TARGET_FILES or size > MAX_TARGET_BYTES
                or used + size > MAX_TARGET_BYTES
                or EXPECTED_BYTES + used + size > MAX_ALL_STAGED_BYTES):
            skipped += len(grouped[name])
            continue
        staged[name] = item
        used += size
    return staged, skipped, used


def inspect_sha_original_source(zip2, scratch, checkpoint=lambda _: None):
    import UnityPy
    zip2, scratch = Path(zip2).absolute(), Path(scratch).absolute()
    safe(zip2)
    safe(scratch)
    if scratch.is_relative_to(zip2):
        raise ValueError("original_source_provider_overwrite_refused")
    checkpoint("pin_exact_original_zip2_and_manifest")
    sha = subprocess.check_output(
        ["git", "-C", str(zip2), "rev-parse", "HEAD"],
        text=True, stderr=subprocess.DEVNULL,
    ).strip()
    if sha != ZIP2_SHA:
        raise ValueError("original_source_SHA_drift")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    scenes = select_original_levels(manifest)
    src_patterns = ["/RAFT_FILE_MANIFEST.tsv"]
    for item in scenes:
        src_patterns.append("/Raft/"+item["path"]+(
            "/*" if item["kind"] == "split" else ""))
    checkpoint("private_stage_original_sha_scenes")
    subprocess.run(["git","-C",str(zip2),"sparse-checkout","set","--no-cone",
                    *src_patterns],check=True,stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL,timeout=300)
    original_pins = {r["path"]:(r["bytes"],r["sha256"]) for r in scenes}
    stage_result = stage(zip2,scratch,original_pins)
    if (stage_result["provider_sha"]!=ZIP2_SHA
            or stage_result["verified_bytes"]!=EXPECTED_BYTES
            or stage_result["lfs_used"] is not False):
        raise ValueError("all_original_level_Scene_SHA_stage_failed")
    checkpoint("original_opaque_script_external_source_records")
    script_refs = []
    for info in scenes:
        name = info["path"]
        path = scratch/name
        safe(path)
        if fingerprint(path)!=original_pins[name]:
            raise ValueError("source_scene_SHA_verification_drift")
        env = UnityPy.load(str(path))
        file = env.file
        objs=list(file.objects.values())
        if len(objs)>MAX_OBJECTS or len(file.externals)>MAX_EXTERNALS:
            raise ValueError("source_scene_object_external_budget")
        ext=[x.path for x in file.externals]
        for obj in objs:
            if obj.type.name != "MonoBehaviour":
                continue
            try:
                tree=obj.read_typetree()
                list(walk_tree_pptrs(tree))
                continue
            except Exception:
                pass
            # Unknown custom payload but source class-DB header is proven
            # independently by prior authentic CI, and reread here.
            h=obj.parse_monobehaviour_head()
            f,p=script_header_ptr(h)
            if f<=0 or f>len(ext) or p<=0:
                raise ValueError("source_opaque_script_external_index_baseline_drift")
            script_refs.append((ext[f-1],p))
        del objs,file,env
        gc.collect()
    if len(script_refs)!=EXPECTED_OPAQUE:
        raise ValueError("source_opaque_MonoBehaviour_script_count_drift")

    checkpoint("map_actual_original_script_owner_candidates")
    categories, grouped=validated_safe_classification(script_refs,manifest)
    selected, skipped, byte_budget=choose_bounded_SHA_original_targets(grouped,manifest)
    if not selected and categories["original_unique_basename_candidate_ref_rows"]:
        raise ValueError("original_target_staging_budget_zero_for_unique_candidates")
    # No private source paths or class names are serialized.
    output={
        "status":"source_original_opaque_m_Script_target_type_join",
        "original_zip2_SHA_authenticated":True,
        "original_scene_SHA_authenticated_file_count":len(scenes),
        "original_scene_SHA_authenticated_bytes":stage_result["verified_bytes"],
        **categories,
        "source_target_rows_budget_skipped":skipped,
        "original_typed_target_files_SHA_staged":0,
        "original_typed_target_bytes_SHA_staged":0,
        "original_opaque_m_Script_rows_typed_target_checked":0,
        "script_refs_to_SHA_original_typed_MonoScript_objects":0,
        "script_refs_to_SHA_original_absent_or_other_type_PathIDs":0,
        "sum_per_original_provider_distinct_typed_MonoScript_targets":0,
        "sum_per_original_provider_distinct_non_MonoScript_targets":0,
        "original_MonoScript_source_TypeName_published":False,
        "source_external_basename_proves_Unity_GUID":False,
        "original_MonoScript_field_layout_reconstructed":False,
        "original_Foam_Runtime_Shader_binding_verified":False,
        "Android_water_pixels_verified":False,
        "private_original_script_object_ids_paths_or_hashes_exported":False,
    }

    if selected:
        checkpoint("stage_private_original_script_owners_by_SHA")
        patterns=[*src_patterns]
        for name,item in selected.items():
            patterns.append("/Raft/"+name+("/*" if item["kind"]=="split" else ""))
        subprocess.run(["git","-C",str(zip2),"sparse-checkout","set","--no-cone",
                        *patterns],check=True,stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,timeout=300)
        pins={name:(r["bytes"],r["sha256"]) for name,r in selected.items()}
        original_targets=stage(zip2,scratch,pins)
        if (original_targets["provider_sha"]!=ZIP2_SHA
                or original_targets["verified_bytes"]!=byte_budget
                or original_targets["lfs_used"] is not False):
            raise ValueError("source_script_owner_SHA_stage_invalid")
        checkpoint("inspect_actual_typed_MonoScript_targets")
        for name,item in selected.items():
            path=scratch/name
            safe(path)
            if fingerprint(path)!=pins[name]:
                raise ValueError("source_original_script_target_fingerprint_drift")
            env=UnityPy.load(str(path))
            objs=list(env.file.objects.values())
            if len(objs)>MAX_OBJECTS:
                raise ValueError("source_target_object_count_unbounded")
            typed=set()
            for obj in objs:
                if obj.type.name=="MonoScript":
                    pid=int(obj.path_id)
                    if pid<=0 or pid in typed:
                        raise ValueError("source_target_typed_MonoScript_identity_invalid")
                    typed.add(pid)
            report=typecheck_typed_MonoScript_target_ids(grouped[name],typed)
            output["script_refs_to_SHA_original_typed_MonoScript_objects"]+=report["script_refs_to_SHA_original_typed_MonoScript_objects"]
            output["script_refs_to_SHA_original_absent_or_other_type_PathIDs"]+=report["script_refs_to_SHA_original_absent_or_other_type_PathIDs"]
            output["sum_per_original_provider_distinct_typed_MonoScript_targets"]+=report["distinct_referenced_typed_MonoScript_objects"]
            output["sum_per_original_provider_distinct_non_MonoScript_targets"]+=report["distinct_referenced_non_MonoScript_PathIDs"]
            output["original_opaque_m_Script_rows_typed_target_checked"]+=len(grouped[name])
            del objs,env,typed
            gc.collect()
    output["original_typed_target_files_SHA_staged"]=len(selected)
    output["original_typed_target_bytes_SHA_staged"]=byte_budget
    if (output["original_opaque_m_Script_rows_typed_target_checked"]!=
            output["script_refs_to_SHA_original_typed_MonoScript_objects"]+
            output["script_refs_to_SHA_original_absent_or_other_type_PathIDs"]
            or categories["original_unique_basename_candidate_ref_rows"]!=
            output["original_opaque_m_Script_rows_typed_target_checked"]+skipped):
        raise ValueError("original_typed_script_target_partition_failed")
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--scratch",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    phase="input"
    def ck(v):
        nonlocal phase
        phase=v
    try:
        out=args.out.absolute()
        safe(out)
        if out.exists() or not out.parent.is_dir() or any(
                out.is_relative_to(v.absolute()) for v in
                (args.zip2,args.scratch)):
            raise ValueError("unsafe_source_report_path")
        r=inspect_sha_original_source(args.zip2,args.scratch,ck)
        out.write_text(json.dumps(r,sort_keys=True)+"\n",encoding="utf8")
        print("T2_ORIGINAL_SCRIPT_TARGET_JOIN_SAFE "+json.dumps(r,sort_keys=True))
        return 0
    except BaseException:
        print("T2_ORIGINAL_SCRIPT_TARGET_JOIN_SAFE "+json.dumps({
            "status":"blocked","safe_phase":phase,
            "private_original_script_names_paths_or_bytes_exposed":False,
        },sort_keys=True))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
