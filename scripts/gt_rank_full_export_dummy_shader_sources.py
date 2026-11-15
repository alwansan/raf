"""Rank custom Dummy material shaders by genuine same-export Shader48 GUID linkage.

Source authentications: immutable ZIP2 82 serialized-owner manifest plus
original Shader48 tree object identity. Same-instance exporter Shader48 trace
provides actual Unity GUID; current actual Material YAML points to that GUID.
Names are checked only after the source/GUID join, never used to select.
Only aggregate counts and anonymous weights leave runner; no original IDs,
GUIDs, asset labels, shader text, or private paths enter public output.
This is not a shader recovery, device pixel proof, or APK generation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import t3_audit_exported_material_programs as quality
from scripts.gt_stage_serialized_owners import OWNERS, read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.t3_original_renderer_shader_impact import load_original, STATUS as SCENE_STATUS
from scripts.verify_export_lineage import identity, pointer

STATUS="GT_EXACT_ORIGINAL_SHADER48_SAME_EXPORT_DUMMY_MATERIAL_PRIORITY_VERIFIED"
MAX_SOURCE_OWNER_SHADER_TARGETS=512
MAX_TRACE=200000
MAX_MATERIALS=5000


def select_dummy_export_sources(trace, profiles, refs):
    if (not isinstance(trace,dict) or trace.get("schema_version")!=1
            or not isinstance(trace.get("export_instance"),str)
            or len(trace["export_instance"])!=32
            or not isinstance(trace.get("objects"),list)
            or len(trace["objects"])>MAX_TRACE):
        raise ValueError("invalid_same_export_original_Shader48_trace")
    wanted={guid for (fid,guid,kind),count in refs.items()
            if fid==4800000 and kind=="3" and count>0
            and guid in profiles and profiles[guid]["dummy"]}
    if not wanted:
        raise ValueError("no_actual_dummy_shader_material_refs")
    source_by_guid={}
    guid_by_source={}
    for row in trace["objects"]:
        if not isinstance(row,dict) or row.get("class_id")!=48:
            continue
        fid,guid,kind=pointer(row["export"])
        if guid not in wanted:
            continue
        if fid!=4800000 or kind!="3":
            raise ValueError("original_export_guid_does_not_identify_custom_Shader48")
        key=identity(row["source"])
        if (guid in source_by_guid or key in guid_by_source):
            raise ValueError("duplicate_original_Shader48_same_export_guid_or_identity")
        source_by_guid[guid]=key
        guid_by_source[key]=guid
    return wanted,source_by_guid


def compare_exact_sources(profiles, material_refs, sources, names, *,
                          expected_material_documents, original_scene_weights=None):
    """Pure strict source/GUID match. Unmatched targets remain unresolved."""
    if (type(profiles) is not dict or not isinstance(material_refs,Counter)
            or type(sources) is not dict or type(names) is not dict
            or type(expected_material_documents) is not int
            or expected_material_documents<=0
            or len(sources)>MAX_SOURCE_OWNER_SHADER_TARGETS):
        raise ValueError("invalid_exact_same_export_Shader_source_inputs")
    scene_weights=original_scene_weights or {}
    counts=Counter()
    material_frequency={}
    for (fid,guid,kind),refs in material_refs.items():
        if (type(refs) is not int or refs<0 or
                not isinstance(guid,str) or not isinstance(kind,str)):
            raise ValueError("invalid_exported_Material_Shader_pointer_counts")
        if fid==4800000 and kind=="3" and guid in profiles and profiles[guid]["dummy"]:
            material_frequency[guid]=material_frequency.get(guid,0)+refs
    if (sum(material_frequency.values())!=expected_material_documents
            or not material_frequency):
        raise ValueError("wrong_same_export_remaining_Dummy_Material_population")
    recovered=[]
    unmatched=[]
    for guid,links in material_frequency.items():
        key=sources.get(guid)
        if key is None or key[0] not in OWNERS or key not in names:
            unmatched.append(links)
            continue
        if names[key]!=profiles[guid]["identity"]:
            counts["original_name_export_Shader_identity_mismatch"]+=1
            unmatched.append(links)
            continue
        recovered.append({
            "private_original_source_key":key,
            "private_export_GUID":guid,
            "material_links":links,
            "scene_renderer_slots":scene_weights.get(key,0),
        })
    recovered.sort(key=lambda row:(-row["material_links"],-row["scene_renderer_slots"]))
    counts["exact_Guid_verified_source_shader_targets"]=len(recovered)
    counts["exact_Guid_verified_dummy_material_links"]=sum(r["material_links"] for r in recovered)
    counts["remaining_unmatched_original_source_dummy_material_links"]=sum(unmatched)
    if (counts["exact_Guid_verified_dummy_material_links"]+
            counts["remaining_unmatched_original_source_dummy_material_links"]
            !=expected_material_documents):
        raise ValueError("original_and_exported_material_reference_accounting_drift")
    return recovered,{
        "schema_version":1,
        "status":STATUS,
        "actual_dummy_Material_custom_Shader_documents":expected_material_documents,
        "original_source_to_same_export_GUID_matched_Shader48_targets":len(recovered),
        "original_source_to_same_export_GUID_matched_dummy_Material_documents":counts["exact_Guid_verified_dummy_material_links"],
        "remaining_dummy_Material_documents_without_complete_original_Shader48_GUID_join":counts["remaining_unmatched_original_source_dummy_material_links"],
        "remaining_original_export_Shader_identity_mismatch_targets":counts["original_name_export_Shader_identity_mismatch"],
        "actual_source_verified_Shader48_dummy_targets_ranked_by_Material_links":[
            row["material_links"] for row in recovered],
        "actual_source_verified_Shader48_dummy_targets_corresponding_scene_renderer_slots":[
            row["scene_renderer_slots"] for row in recovered],
        "exact_same_export_original_source_Shader48_to_custom_Shader_GUID_join":True,
        "original_source_names_GUIDs_PathIDs_or_shader_text_published":False,
        "original_source_assets_or_export_materials_modified":False,
        "Unity_Android_Vulkan_shader_compilation_or_device_pixels_verified":False,
        "APK_OBB_XAPK_created":False,
    }


def original_names_for_wanted(original, manifest, source_by_guid):
    import UnityPy
    expected=read_expected(manifest)
    grouped={}
    for key in source_by_guid.values():
        if key[0] not in OWNERS:
            continue
        grouped.setdefault(key[0],set()).add(key[1])
    names={}
    for owner,ids in sorted(grouped.items()):
        _,size,digest=expected[owner]
        file=original/"Raft_Data"/owner
        if file.is_symlink() or not file.is_file():
            raise ValueError("original_source_Shader48_provider_missing")
        verify(file,size,digest)
        package=UnityPy.load(str(file)).file
        for pid in ids:
            obj=package.objects.get(pid)
            if obj is None or obj.type.name!="Shader":
                raise ValueError("original_SHA_verified_Shader48_object_missing")
            tree=obj.read_typetree()
            parsed=tree.get("m_ParsedForm",{})
            name=parsed.get("m_Name") if isinstance(parsed,dict) else None
            if not isinstance(name,str) or not name:
                raise ValueError("original_Shader48_parsed_name_invalid")
            names[owner,pid]=name
    return names,len(grouped)


def run(original,manifest,project,trace_path):
    assets=project/"Assets"
    source=original/"Raft_Data"
    if (not assets.is_dir() or assets.is_symlink()
            or not source.is_dir() or source.is_symlink()
            or trace_path.is_symlink() or trace_path.stat().st_size>40*1024*1024):
        raise ValueError("unsafe_full_original_source_or_export")
    entries=sorted(assets.rglob("*"))
    profiles=quality._shader_profiles(entries)
    refs=Counter(quality._material_refs(entries))
    wanted,source_by_guid=select_dummy_export_sources(
        json.loads(trace_path.read_text("utf-8")),profiles,refs)
    names,owner_count=original_names_for_wanted(original,manifest,source_by_guid)
    scene_slots={}
    scene_proof=load_original(original,manifest,private_slot_counts=scene_slots)
    if (scene_proof.get("status")!=SCENE_STATUS or
            scene_proof.get("six_original_scenes_sha_verified") is not True):
        raise ValueError("original_six_scene_priority_source_not_verified")
    dummy=sum(count for (fid,guid,kind),count in refs.items()
              if fid==4800000 and kind=="3" and guid in wanted)
    private,report=compare_exact_sources(profiles,refs,source_by_guid,names,
                                         expected_material_documents=dummy,
                                         original_scene_weights=scene_slots)
    report["original_sha_authenticated_Shader_owner_count"]=owner_count
    report["six_original_scenes_1633_Shader48_material_slots_SHA_verified"]=True
    report["distinct_dummy_Shader_GUIDs_referenced"]=len(wanted)
    report["linked_dummy_Shader_targets_with_exported_trace"]=len(source_by_guid)
    report["full_original_export_material_documents"]=sum(refs.values())
    if (report["full_original_export_material_documents"]!=1536
            or len(wanted)!=report["distinct_dummy_Shader_GUIDs_referenced"]):
        raise ValueError("full_export_Material_or_Shader_scope_changed")
    # Private returned keys never leave this function; published report is numeric.
    del private
    return report


def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    for name in ("original","manifest","project","trace","out"):
        a.add_argument("--"+name,type=Path,required=True)
    args=a.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
            or args.out.resolve().is_relative_to(args.original.resolve())
            or args.out.resolve().is_relative_to(args.project.resolve())):
        raise ValueError("unsafe_original_shader_census_output")
    try:
        result=run(args.original,args.manifest,args.project,args.trace)
    except Exception as error:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "error_type":type(error).__name__,
                "original_source_names_GUIDs_PathIDs_or_shader_text_published":False,
                "APK_OBB_XAPK_created":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_EXACT_SOURCE_EXPORT_REMAINING_DUMMY_SHADER_PRIORITY "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
