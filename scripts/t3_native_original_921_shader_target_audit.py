#!/usr/bin/env python3
"""T3 SHA-original 921-use Shader48 to actual full-native ShaderLab private GUID.

Use on a disposable ORIGINAL source (6 scene SHA + 4 owners) and the SAME
full native AssetRipper export's W1 private trace and post-restorer Assets.
No original IDs, Shader names, GUID, source, HLSL or per-file hashes exported.
This tool does not modify Unity Assets or claim Adreno pixel equivalence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from scripts import t3_original_renderer_shader_impact as source
from scripts import t3_original_top_shader_dxbc_feasibility as top
from scripts import t3_source_renderer_shader_to_postvendor_export as prior
from scripts import t3_audit_exported_material_programs as export
from scripts.verify_export_lineage import identity, pointer
from scripts.probe_a13_exported_material_shader_guids import BUILTIN
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS

STATUS = "ORIGINAL_921_SHA_SOURCE_TO_FULL_NATIVE_EXPORTED_SHADERLAB_GUID_CONFIRMED"
SAFE_TOP_STATUSES = frozenset((
    "DUMMY_AFTER_NATIVE_RESTORERS",
    "NON_DUMMY_NATIVE_PROGRAM_AUTHENTICITY_UNPROVEN",
    "UNITY_BUILTIN_EXPORTED_PROGRAM_AUTHENTICITY_UNPROVEN",
))
GUID = re.compile(r"[0-9a-f]{32}\Z")


def strict_native_top_join(original_counts: dict, source_report: dict,
                           top_key: tuple, private_trace: dict,
                           shader_profiles: dict, *, original_passes: int = 4):
    """Private original Shader48 ID/GUID join; only aggregate output leaves."""
    if (type(original_counts) is not dict or type(source_report) is not dict or
            type(original_passes) is not int or original_passes != 4 or
            not isinstance(private_trace,dict) or
            private_trace.get("schema_version")!=1 or
            type(private_trace.get("export_instance")) is not str or
            not GUID.fullmatch(private_trace["export_instance"]) or
            not isinstance(private_trace.get("objects"),list) or
            not isinstance(shader_profiles,dict)):
        raise ValueError("invalid_native_original_921_private_lineage_inputs")
    if len(private_trace["objects"]) > 200000:
        raise ValueError("oversized_private_native_export_trace")
    if top.selected_high_use(original_counts,source_report)!=top_key:
        raise ValueError("unmatched_original_top921_source_Shader48")
    source_join=prior.join(original_counts,private_trace,shader_profiles,
                           verified_source_report=source_report)
    if source_join.get("status")!=prior.STATUS:
        raise ValueError("private_source_shader_target_join_failed")
    rows=[row for row in private_trace["objects"]
          if isinstance(row,dict) and row.get("class_id")==48
          and identity(row["source"])==top_key]
    if len(rows)!=1:
        raise ValueError("top_original_shader48_not_one_export_source_row")
    fid,guid,typ=pointer(rows[0]["export"])
    if guid in BUILTIN and typ=="0":
        status="UNITY_BUILTIN_EXPORTED_PROGRAM_AUTHENTICITY_UNPROVEN"
        source_pass_count_compared=False
        native_passes=None
        programmed=None
        dummy_marker=None
        balanced=None
        partial=None
    else:
        if (fid!=4800000 or typ!="3" or guid not in shader_profiles
            or not GUID.fullmatch(guid)):
            raise ValueError("top_original_custom_Shader_GUID_unresolved")
        p=shader_profiles[guid]
        keys=("dummy","no_subprograms","unknown_exporter","unbalanced",
              "pass_count","programmed","partial_subshader_coverage")
        if any(k not in p for k in keys) or any(type(p[k]) is not bool for k in
                ("dummy","no_subprograms","unknown_exporter","unbalanced","partial_subshader_coverage")):
            raise ValueError("invalid_actual_native_top_ShaderLab_profile")
        if (type(p["pass_count"]) is not int or type(p["programmed"]) is not int or
            not 0 <= p["programmed"] <= p["pass_count"] <= 512):
            raise ValueError("invalid_native_top_shader_pass_counts")
        status=("DUMMY_AFTER_NATIVE_RESTORERS" if p["dummy"] else
                "NON_DUMMY_NATIVE_PROGRAM_AUTHENTICITY_UNPROVEN")
        source_pass_count_compared=True
        native_passes=p["pass_count"]
        programmed=p["programmed"]
        dummy_marker=p["dummy"]
        balanced=not p["unbalanced"]
        partial=p["partial_subshader_coverage"]
    if status not in SAFE_TOP_STATUSES:
        raise ValueError("unapproved_native_Shader_status")
    native_dummy_slots=source_join[
        "original_scene_slot_use_by_actual_postvendor_shader_status"].get(
            "scene_renderer_material_slots_to_dummy",0)
    native_builtin_slots=source_join[
        "original_scene_slot_use_by_actual_postvendor_shader_status"].get(
            "scene_renderer_material_slots_to_unity_builtin",0)
    native_non_dummy_slots=source_join[
        "original_scene_slot_use_by_actual_postvendor_shader_status"].get(
            "scene_renderer_material_slots_to_vendor_non_dummy",0)
    if (any(type(x) is not int or x<0 for x in
            (native_dummy_slots,native_builtin_slots,native_non_dummy_slots))
        or native_dummy_slots+native_builtin_slots+native_non_dummy_slots!=
            top.EXPECTED_TYPED_SOURCE_SLOTS):
        raise ValueError("native_original_scene_shader_slot_accounting_drift")
    return {
        "schema_version":1, "status":STATUS,
        "source_scope":"SHA_original_six_scenes_four_owner_21_typed_Shader48",
        "source_original_high_use_renderer_material_slots":921,
        "source_original_high_use_Shader48_passes":original_passes,
        "source_original_Shader48_traced_into_native_export":True,
        "source_all_21_typed_Shader48_traced_into_native_export":True,
        "native_high_use_source_shader_export_status":status,
        "native_high_use_shaderlab_pass_count":native_passes,
        "native_high_use_shaderlab_programmed_pass_count":programmed,
        "native_high_use_shaderlab_pass_count_matches_original":(
            native_passes==original_passes if source_pass_count_compared else None),
        "native_high_use_shaderlab_has_dummy_exporter_marker":dummy_marker,
        "native_high_use_shaderlab_braces_balanced":balanced,
        "native_high_use_shaderlab_partial_subshader_coverage":partial,
        "native_original_scene_shader_slots_to_dummy":native_dummy_slots,
        "native_original_scene_shader_slots_to_non_dummy":native_non_dummy_slots,
        "native_original_scene_shader_slots_to_unity_builtin":native_builtin_slots,
        "source_to_export_guid_join_complete":True,
        "original_DXBC_to_native_shader_program_equivalence_proven":False,
        "unity_compile_or_Android_pixels_proven":False,
        "native_assets_or_guid_changed":False,
        "private_original_names_GUIDs_ids_hashes_disclosed":False,
    }


def probe(original:Path, manifest:Path, project:Path, trace_file:Path):
    if any(p.is_symlink() for p in (original,manifest,project,trace_file,
                                     original/"Raft_Data",project/"Assets")):
        raise ValueError("unsafe_original_or_native_export_root")
    private={}
    report=source.load_original(original,manifest,private_slot_counts=private)
    key=top.selected_high_use(private,report)
    owner,pid=key
    path=original/"Raft_Data"/owner
    if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise ValueError("original_top_Shader48_SHA_mismatch")
    import UnityPy
    found=[obj for obj in UnityPy.load(str(path)).file.objects.values()
           if obj.path_id==pid]
    if len(found)!=1 or found[0].type.name!="Shader":
        raise ValueError("source_top_Shader48_not_unique")
    parsed=found[0].read_typetree().get("m_ParsedForm")
    if (type(parsed) is not dict or type(parsed.get("m_SubShaders")) is not list
        or len(parsed["m_SubShaders"])!=1 or
        type(parsed["m_SubShaders"][0].get("m_Passes")) is not list):
        raise ValueError("unexpected_source_high_use_Shader_pass_layout")
    count=len(parsed["m_SubShaders"][0]["m_Passes"])
    if count!=4:
        raise ValueError("original_top_Shader_pass_count_drift")
    if not trace_file.is_file() or trace_file.stat().st_size>40_000_000:
        raise ValueError("missing_or_oversized_private_native_export_trace")
    private_trace=json.loads(trace_file.read_text(encoding="utf-8"))
    assets=project/"Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("native_Assets_not_available")
    files=sorted(assets.rglob("*"))
    if len(files)>export.MAX_INVENTORY or any(x.is_symlink() for x in files):
        raise ValueError("unsafe_native_Assets_inventory")
    profiles=export._shader_profiles(files)
    result=strict_native_top_join(private,report,key,private_trace,profiles,
                                  original_passes=count)
    result.update({
        "source_original_scenes_sha_verified":6,
        "source_original_shader_material_owners_sha_verified":4,
        "actual_postrestorer_ShaderLab_profiles_count":len(profiles),
    })
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","project","w1-trace","out"):
        parser.add_argument("--"+name,required=True,type=Path)
    args=parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve()) or
        args.out.resolve().is_relative_to(args.project.resolve())):
        raise ValueError("unsafe_native_Shader_source_report_destination")
    try:
        result=probe(args.original,args.manifest,args.project,args.w1_trace)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "unity_compile_or_Android_pixels_proven":False,
                "native_assets_or_guid_changed":False,
                "private_original_names_GUIDs_ids_hashes_disclosed":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("T3_ORIGINAL_921_NATIVE_SHADER_TARGET "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
