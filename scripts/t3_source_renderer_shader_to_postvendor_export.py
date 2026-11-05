#!/usr/bin/env python3
"""T3: authentic original Renderer Shader48 use vs same-export postvendor shader.

Original 6 ZIP2 scenes, their 3 typed Material owners, 4 typed Shader owners,
a pinned same-instance AssetRipper W1 Shader48 Material21 + B02 Texture2D28
private trace, and current actual .shader/.shader.meta AFTER official vendor
restoration. The full private join happens in memory; only numeric priority
bands leave the runner. It does NOT prove original-to-export Renderer links,
original compiled program equivalence, Adreno pixels or white-object counts.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import t3_original_renderer_shader_impact as original
from scripts import t3_material_shader_same_export as source_to_export
from scripts import t3_audit_exported_material_programs as actual_export
from scripts.probe_a13_exported_material_shader_guids import BUILTIN
from scripts.verify_export_lineage import identity,pointer

EXPECTED_TYPED_SOURCES=21
EXPECTED_TYPED_SLOT_USE=1633
EXPECTED_UNKNOWN_SHADER_SLOTS=2
EXPECTED_TOP_ORIGINAL_SH=921
STATUS="SIX_SCENE_SOURCE_SHADER_TO_POSTVENDOR_ACTUAL_GUID_JOIN_VERIFIED"


def join(source_use:dict, w1:dict, shader_profiles:dict, *,
         verified_source_report:dict):
    if (not isinstance(source_use,dict) or len(source_use)!=EXPECTED_TYPED_SOURCES
        or sum(source_use.values())!=EXPECTED_TYPED_SLOT_USE
        or not isinstance(w1,dict) or not isinstance(w1.get("objects"),list)
        or not isinstance(shader_profiles,dict)
        or verified_source_report.get("status")!=original.STATUS
        or verified_source_report.get("counts",{}).get("original_slots_to_verified_Shader48", -1)!=EXPECTED_TYPED_SLOT_USE):
        raise ValueError("untrusted_original_scene_Shader48_usage_scope")
    # Explicit original typed SourceShader48 identity, never file name matching.
    selected=set(source_use)
    by_original={}
    for row in w1["objects"]:
        if row.get("class_id")!=48:continue
        key=identity(row["source"])
        if key not in selected:continue
        if key in by_original:raise ValueError("duplicate_same_instance_Shader48_trace")
        by_original[key]=pointer(row["export"])
    if set(by_original)!=selected:
        raise ValueError("missing_original_to_actual_Shader48_trace_target")
    counts=Counter()
    shader_count=Counter()
    slots_per_status={"dummy":[],"vendor_non_dummy":[],"unity_builtin":[]}
    exported_custom_guids=set()
    for key,src_slots in source_use.items():
        if type(src_slots) is not int or src_slots<=0:
            raise ValueError("invalid_original_Shader48_renderer_slot_count")
        export=by_original[key]
        if (not isinstance(export,tuple) or len(export)!=3
            or type(export[0]) is not int or not isinstance(export[1],str)
            or not isinstance(export[2],str)):
            raise ValueError("invalid_same_instance_export_Shader_pointer")
        fileid,guid,ptype=export
        if guid in BUILTIN and ptype=="0":
            status="unity_builtin"
        elif fileid==4800000 and ptype=="3" and guid in shader_profiles:
            if guid in exported_custom_guids:
                raise ValueError("separate_source_Shader48_collide_export_GUID")
            exported_custom_guids.add(guid)
            status="dummy" if shader_profiles[guid]["dummy"] else "vendor_non_dummy"
            # One authored-looking Pass does not certify true source HLSL.
            if shader_profiles[guid]["unbalanced"]:
                counts["source_scene_slots_to_unbalanced_ShaderLab"]+=src_slots
            if shader_profiles[guid]["programmed"]==0:
                counts["source_scene_slots_to_ShaderLab_without_complete_program"]+=src_slots
            if shader_profiles[guid]["partial_subshader_coverage"]:
                counts["source_scene_slots_to_incomplete_SubShader_coverage"]+=src_slots
        else:
            raise ValueError("unresolved_or_wrong_actual_original_Shader48_export")
        counts["scene_renderer_material_slots_to_"+status]+=src_slots
        shader_count["source_Shader48_targets_with_"+status]+=1
        slots_per_status[status].append(src_slots)
    if (sum(counts["scene_renderer_material_slots_to_"+v]
            for v in ("dummy","vendor_non_dummy","unity_builtin"))!=EXPECTED_TYPED_SLOT_USE
        or sum(shader_count.values())!=EXPECTED_TYPED_SOURCES):
        raise ValueError("original_shader_use_join_accounting_mismatch")
    top=sorted(source_use.values(),reverse=True)
    if top[0]!=EXPECTED_TOP_ORIGINAL_SH:
        raise ValueError("original_921_slot_Shader_reference_changed")
    maxkey=max(source_use,key=source_use.get)
    high_shader_target=by_original[maxkey]
    if high_shader_target[1] in BUILTIN and high_shader_target[2]=="0":
        high_status="UNITY_BUILTIN_EXPORT_TARGET"
    elif shader_profiles[high_shader_target[1]]["dummy"]:
        high_status="STILL_DUMMY_AFTER_VENDOR_RESTORERS"
    else:
        high_status="NON_DUMMY_AFTER_VENDOR_RESTORERS_NOT_AUTHORED_EQUIVALENCE"
    result={
        "schema_version":1,
        "experiment":"T3-authentic-six-original-scenes-Shader48-to-same-instance-postvendor-ShaderLab",
        "original_renderer_Material_nonnull_slots":verified_source_report["original_nonnull_renderer_material_slots"],
        "original_typed_Shader48_renderer_material_slots":EXPECTED_TYPED_SLOT_USE,
        "original_Shader_refs_to_unstaged_owner_slots":EXPECTED_UNKNOWN_SHADER_SLOTS,
        "true_original_typed_Shader48_targets_used_by_scenes":EXPECTED_TYPED_SOURCES,
        "original_Shader48_source_to_export_pointer_IDs_verified":len(by_original),
        "actual_export_ShaderLab_source_profiles_available":len(shader_profiles),
        "original_scene_slot_use_by_actual_postvendor_shader_status":dict(sorted(counts.items())),
        "source_Shader48_unique_targets_by_actual_postvendor_status":dict(sorted(shader_count.items())),
        "top_ten_original_scene_Shader48_slot_counts_no_identity":top[:10],
        "top_ten_scene_slot_uses_still_Dummy_no_identity":sorted(slots_per_status["dummy"],reverse=True)[:10],
        "top_ten_scene_slot_uses_nonDummy_vendor_no_identity":sorted(slots_per_status["vendor_non_dummy"],reverse=True)[:10],
        "highest_source_921_slot_Shader_export_status":high_status,
        "same_instance_W1_Shader48_original_pointer_and_export_GUID_join_verified":True,
        "exported_original_Renderer_material_assignment_parity_not_verified":True,
        "source_original_compiled_shader_subprogram_equivalence_not_verified":True,
        "actual_Unity_import_or_Android_Adreno_pixels_not_verified":True,
        "private_original_Shader_names_IDs_Guids_exposed":False,
        "status":STATUS,
    }
    return result


def run(original_root:Path,manifest:Path,project:Path,w1path:Path,b02path:Path):
    private={}
    source=original.load_original(original_root,manifest,private_slot_counts=private)
    if (source["original_distinct_typed_Shader48_targets"]!=EXPECTED_TYPED_SOURCES
        or source["original_nonnull_renderer_material_slots"]!=original.SCENE_NONNULL_SLOTS
        or source["counts"]["original_slots_to_unstaged_other_Shader"]!=EXPECTED_UNKNOWN_SHADER_SLOTS):
        raise ValueError("unexpected_original_six_scene_source_Shader_scope")
    # There are 22 original source Shader identities; exactly 21 are class48
    # authenticated by four SHA-pinned serialized owners. Do not guess the
    # non-staged globalgamemanagers Shader type or export from a filename.
    typed={
        key:n for key,n in private.items()
        if key[0] in original.SHADER_OWNERS_SELECTED
    }
    if len(typed)!=EXPECTED_TYPED_SOURCES or sum(typed.values())!=EXPECTED_TYPED_SLOT_USE:
        raise ValueError("incomplete_private_source_Shader48_usage_map")
    lineage=source_to_export.run(original_root,project,w1path,b02path)
    if (lineage["actual_exported_material_shader_fields_exact"]!=41
        or not lineage["original_Material_Shader_pptr_target_preserved"]):
        raise ValueError("same_export_original_Material_Shader_lineage_unproven")
    # Run strict aggregate audit first; it rejects insecure input paths,
    # invalid Material fields or duplicate ShaderImporter GUIDs.
    audit=actual_export.audit(project)
    if (audit["status"]!=actual_export.STATUS or
        not audit["counts"]["material_docs_using_local_custom_Shader"]):
        raise ValueError("actual_export_Material_Shader_program_audit_failed")
    assets=project/"Assets"
    files=sorted(assets.rglob("*"))
    shader_profiles=actual_export._shader_profiles(files)   # PRIVATE GUID keyed
    w1=json.loads(w1path.read_text("utf-8"))
    output=join(typed,w1,shader_profiles,verified_source_report=source)
    output["same_export_original_Material_Shader_reference_checks"]=41
    output["postvendor_export_Material_documents_in_separate_population"]=audit["counts"]["material_documents"]
    output["postvendor_export_custom_Material_documents_in_separate_population"]=audit["counts"]["material_docs_using_local_custom_Shader"]
    output["postvendor_export_custom_Material_documents_still_Dummy_separate_population"]=audit["counts"]["material_docs_using_dummy_Shader"]
    return output


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for flag in ("original","manifest","project","w1-trace","b02-trace","out"):
        p.add_argument("--"+flag,type=Path,required=True)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())
        or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("unsafe_public_original_Shader_identity_report")
    try:out=run(a.original,a.manifest,a.project,a.w1_trace,a.b02_trace)
    except Exception as e:
        out={
            "schema_version":1,
            "experiment":"T3-authentic-six-original-scenes-Shader48-to-same-instance-postvendor-ShaderLab",
            "status":"INCONCLUSIVE","failure_type":type(e).__name__,
            "source_original_compiled_shader_subprogram_equivalence_not_verified":True,
            "actual_Unity_import_or_Android_Adreno_pixels_not_verified":True,
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("T3_ORIGINAL_SCENE_SHADER_TO_VENDOR_EXPORT "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
