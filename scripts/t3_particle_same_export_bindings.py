#!/usr/bin/env python3
"""T3 actual original 108-use Particle Shader48 Material/Texture same-export join.

Source identity is the exact private 6-scene/4-owner source graph; export
identity comes from ONE AssetRipper invocation's W1 Material21/B02 Texture2D28
traces and real Unity Material YAML. No source PathID, material label, GUID,
export instance ID, private data or game asset is printed or uploaded.
Not Android device pixel or full native Unity import fidelity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path

from scripts import b05_verify_material_texenv_bindings as b05
from scripts import t3_original_particle_material_texenv as original
from scripts import t3_same_export_material_texenv as common

SOURCE_STATUS=original.STATUS
STATUS_MATCH="SAME_INSTANCE_SOURCE_PARTICLE108_5M_3T_10_TEXTURE_PPTR_EXACT"
STATUS_MISMATCH="SAME_INSTANCE_SOURCE_PARTICLE108_SCOPED_EXPORT_MISMATCH_OR_INCOMPLETE"
EXPECTED_MATERIALS=5
EXPECTED_TEXTURES=3
EXPECTED_SLOTS=10

FIELDS=(
    "original_source_materials","original_source_texture_targets",
    "original_source_material_texture_slots",
    "traced_selected_material21","traced_selected_texture2d28",
    "selected_material21_missing_export_trace",
    "selected_texture2d28_missing_export_trace",
    "selected_material21_export_guid_collisions",
    "selected_texture2d28_export_guid_collisions",
    "selected_material21_without_exported_YAML",
    "selected_material21_source_slots_missing_after_export",
    "selected_material21_new_texenv_slots_after_export",
    "selected_source_nonnull_texture_to_null",
    "selected_source_texture_to_other_exported_target",
    "selected_source_texenv_target_unresolved",
    "selected_exact_material_texenv_pointer_matches",
    "selected_uv_scale_offset_matches",
    "selected_uv_missing_or_mismatched",
    "selected_missing_texture_skipped_nonexportable_collection",
    "selected_missing_texture_absent_all_export_collections",
    "selected_missing_texture_reason_unclassified",
)
PRIVACY_FALSE="private_original_export_shader_material_texture_labels_guids_disclosed"


def assess(source_materials:dict,source_texture_targets:dict,
           w1:dict,b02:dict,exported:dict)->dict:
    """Pure private join; only allowlisted integer counts become public."""
    if (type(source_materials) is not dict or len(source_materials)!=EXPECTED_MATERIALS
        or type(source_texture_targets) is not dict
        or len(source_texture_targets)!=EXPECTED_TEXTURES
        or type(exported) is not dict):
        raise ValueError("incomplete_private_original_Particle_shader_material_scope")
    actual_targets=Counter()
    actual_slots=0
    for key,slots in source_materials.items():
        if (type(key) is not tuple or len(key)!=2
            or key[0] not in original.source.MATERIAL_OWNERS
            or type(key[1]) is not int or key[1]<=0
            or type(slots) is not dict or not slots):
            raise ValueError("malformed_private_original_selected_Material21")
        for property_name,slot in slots.items():
            if type(property_name) is not str or not property_name:
                raise ValueError("invalid_original_selected_TexEnv_label")
            ptr,uv=b05._slot(slot)
            if (type(ptr) is not tuple or len(ptr)!=2
                or type(ptr[0]) is not int or ptr[0]!=0
                or type(ptr[1]) is not int or ptr[1]<=0
                or type(uv) is not tuple or len(uv)!=4
                or any(type(x) is not float or not math.isfinite(x) for x in uv)):
                raise ValueError("invalid_private_original_particle_TexEnv_internal_pointer")
            actual_targets[(key[0],ptr[1])]+=1
            actual_slots+=1
    if (actual_slots!=EXPECTED_SLOTS
        or actual_targets!=Counter(source_texture_targets)):
        raise ValueError("untrusted_selected_original_particle_Texture2D_source_linkage")
    common.combine_same_export(w1,b02)  # strict one exporter instance gate
    counts=Counter()
    counts["original_source_materials"]=EXPECTED_MATERIALS
    counts["original_source_texture_targets"]=EXPECTED_TEXTURES
    counts["original_source_material_texture_slots"]=EXPECTED_SLOTS
    selected_materials={}
    selected_textures={}
    export_material_keys=set()
    export_texture_keys=set()
    for row in w1["objects"]:
        if row["class_id"]!=21:continue
        src=b05._trace_source(row)
        if src not in source_materials:continue
        if src in selected_materials:
            raise ValueError("duplicate_selected_original_material_export_trace")
        ptr=b05._trace_export(row)
        if ptr[0]<=0 or ptr[2] not in (2,3):
            raise ValueError("unsupported_selected_material_export_guid")
        selected_materials[src]=ptr[:2]
        if ptr[:2] in export_material_keys:
            counts["selected_material21_export_guid_collisions"]+=1
        export_material_keys.add(ptr[:2])
    for row in b02["objects"]:
        src=b05._trace_source(row)
        if src not in source_texture_targets:continue
        if src in selected_textures:
            raise ValueError("duplicate_selected_original_texture_export_trace")
        ptr=b05._trace_export(row)
        if ptr[0]<=0 or ptr[2] not in (2,3):
            raise ValueError("unsupported_selected_Texture2D_export_guid")
        selected_textures[src]=ptr
        if ptr in export_texture_keys:
            counts["selected_texture2d28_export_guid_collisions"]+=1
        export_texture_keys.add(ptr)
    counts["traced_selected_material21"]=len(selected_materials)
    counts["traced_selected_texture2d28"]=len(selected_textures)
    counts["selected_material21_missing_export_trace"]=EXPECTED_MATERIALS-len(selected_materials)
    counts["selected_texture2d28_missing_export_trace"]=EXPECTED_TEXTURES-len(selected_textures)
    missing=set(source_texture_targets)-set(selected_textures)
    if "nonexportable_texture_sources" in b02:
        candidates=b02["nonexportable_texture_sources"]
        if type(candidates) is not list:
            raise ValueError("malformed_private_B02_nonexportable_collection_trace")
        skipped=set()
        for candidate in candidates:
            # PRIVATE: use only source identity, never expose source IDs/owner.
            src=b05._trace_source(candidate)
            if src in source_texture_targets:
                skipped.add(src)
        if skipped & set(selected_textures):
            raise ValueError("selected_B02_texture_both_exportable_and_nonexportable")
        counts["selected_missing_texture_skipped_nonexportable_collection"]=len(
            missing & skipped)
        counts["selected_missing_texture_absent_all_export_collections"]=len(
            missing-skipped)
    else:
        counts["selected_missing_texture_reason_unclassified"]=len(missing)
    if (sum(counts[k] for k in (
        "selected_missing_texture_skipped_nonexportable_collection",
        "selected_missing_texture_absent_all_export_collections",
        "selected_missing_texture_reason_unclassified"))
            !=counts["selected_texture2d28_missing_export_trace"]):
        raise ValueError("B02_original_texture_missing_causal_category_drift")
    if counts["selected_material21_export_guid_collisions"] or counts["selected_texture2d28_export_guid_collisions"]:
        # No original→export source identity collision can constitute a match.
        raise ValueError("original_particle_export_pointer_alias_collision")

    for src,src_slots in source_materials.items():
        export_key=selected_materials.get(src)
        if export_key is None:
            counts["selected_source_texenv_target_unresolved"]+=len(src_slots)
            counts["selected_uv_missing_or_mismatched"]+=len(src_slots)
            continue
        dst_slots=exported.get(export_key)
        if type(dst_slots) is not dict:
            counts["selected_material21_without_exported_YAML"]+=1
            counts["selected_source_texenv_target_unresolved"]+=len(src_slots)
            counts["selected_uv_missing_or_mismatched"]+=len(src_slots)
            continue
        counts["selected_material21_source_slots_missing_after_export"]+=len(src_slots.keys()-dst_slots.keys())
        counts["selected_material21_new_texenv_slots_after_export"]+=len(dst_slots.keys()-src_slots.keys())
        for label,(src_ptr,src_uv) in src_slots.items():
            if label not in dst_slots:
                counts["selected_source_texenv_target_unresolved"]+=1
                counts["selected_uv_missing_or_mismatched"]+=1
                continue
            dst_ptr,dst_uv=b05._slot(dst_slots[label])
            if not isinstance(dst_ptr,tuple) or len(dst_ptr)!=3:
                raise ValueError("malformed_selected_exported_particle_texture_pointer")
            if not dst_ptr[0]:
                counts["selected_source_nonnull_texture_to_null"]+=1
            else:
                expected=selected_textures.get((src[0],src_ptr[1]))
                if expected is None:
                    counts["selected_source_texenv_target_unresolved"]+=1
                elif expected==dst_ptr:
                    counts["selected_exact_material_texenv_pointer_matches"]+=1
                else:
                    counts["selected_source_texture_to_other_exported_target"]+=1
            if (type(dst_uv) is tuple and len(dst_uv)==4
                and all(type(y) in (int,float) and math.isfinite(y) for y in dst_uv)
                and all(math.isclose(x,float(y),abs_tol=1e-6,rel_tol=1e-6)
                        for x,y in zip(src_uv,dst_uv))):
                counts["selected_uv_scale_offset_matches"]+=1
            else:
                counts["selected_uv_missing_or_mismatched"]+=1

    out={"schema_version":1,"same_export_instance_W1_B02_authenticated":True,
         "original_source_graph_SHA_authenticated_in_caller":True,
         "real_unity_exported_Material_YAML_compared":True,
         "source_scope":"T3-private-original-108Particle5Material3Texture",
         PRIVACY_FALSE:False,
         "compiled_Unity_ShaderLab_or_Android_pixels_verified":False,
         **{k:counts[k] for k in FIELDS}}
    exact=(counts["traced_selected_material21"]==EXPECTED_MATERIALS
           and counts["traced_selected_texture2d28"]==EXPECTED_TEXTURES
           and counts["selected_exact_material_texenv_pointer_matches"]==EXPECTED_SLOTS
           and counts["selected_uv_scale_offset_matches"]==EXPECTED_SLOTS
           and not any(counts[k] for k in FIELDS[5:15]+FIELDS[17:]))
    out["status"]=STATUS_MATCH if exact else STATUS_MISMATCH
    return out


def run(original_root:Path,manifest:Path,project:Path,w1_path:Path,b02_path:Path):
    files=(original_root,manifest,project,w1_path,b02_path)
    if any(x.is_symlink() or any(part.is_symlink() for part in x.parents) for x in files):
        raise ValueError("redirected_source_or_export_sameinstance_input")
    private_slots={}
    private_targets={}
    source_report=original.run(
        original_root,manifest,private_material_texenvs=private_slots,
        private_local_texture_targets=private_targets)
    if (source_report.get("status")!=SOURCE_STATUS
        or source_report.get("six_original_scene_SHA_verified") is not True
        or source_report.get("four_original_shader_Material_owner_SHA_verified") is not True
        or source_report.get("original_108_use_ParticleShader48_reference_authenticated") is not True
        or source_report.get("original_particle_material_objects")!=EXPECTED_MATERIALS
        or source_report.get("original_particle_texenv_slots")!=EXPECTED_SLOTS
        or source_report.get("original_particle_distinct_texture_PPtr_shapes_in_material_owners")!=EXPECTED_TEXTURES):
        raise ValueError("missing_SHA_verified_original_Particle108_source")
    w1=json.loads(w1_path.read_text(encoding="utf8"))
    b02=json.loads(b02_path.read_text(encoding="utf8"))
    exported=b05.exported_texenvs(project)
    return assess(private_slots,private_targets,w1,b02,exported)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","project","w1-trace","b02-trace","out"):
        ap.add_argument("--"+key,type=Path,required=True)
    args=ap.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())
        or args.out.resolve().is_relative_to(args.project.resolve())):
        raise ValueError("unsafe_particle_same_export_aggregate_path")
    try:
        result=run(args.original,args.manifest,args.project,
                   args.w1_trace,args.b02_trace)
    except Exception as error:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(error).__name__,
                "same_export_instance_W1_B02_authenticated":False,
                "real_unity_exported_Material_YAML_compared":False,
                PRIVACY_FALSE:False,
                "compiled_Unity_ShaderLab_or_Android_pixels_verified":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_PARTICLE108_SAMEINSTANCE_EXPORT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STATUS_MATCH,STATUS_MISMATCH) else 2


if __name__=="__main__":
    raise SystemExit(main())
