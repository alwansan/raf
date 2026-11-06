#!/usr/bin/env python3
"""Exact five SHA-original Particle108 Material21 RGBA + scalar same-export values.

One-shot original 5-Material phase diagnosis; source and values never logged.

The 108-use Particle Shader48's five Material identities are selected by
six original scene Renderer→Material→Shader PPtrs, not names. Private W1+B02
same-instance exporter lineage binds each to real Unity exported YAML.
B44 color comparison and B22 float32/int32 comparison are re-used unchanged.
Public reports contain counts only, no Material labels/values/GUIDs/pathIDs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import t3_original_particle_material_texenv as particle
from scripts import t3_same_export_material_texenv as sameexport
from scripts import b44_verify_material_colors as colors
from scripts import b22_verify_material_scalars as scalars
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint

SOURCE_STATUS=particle.STATUS
MATCH="T3_SOURCE_PARTICLE108_5M_SAMEEXPORT_RGBA_FLOAT32_INT32_VALUES_MATCH"
MISMATCH="T3_SOURCE_PARTICLE108_5M_SAMEEXPORT_RGBA_FLOAT32_INT32_VALUES_MISMATCH"
EXPECTED_MATERIALS=5
SAFE_PHASES=frozenset((
    "SOURCE_SELECTED_GRAPH","ORIGINAL_RGBA_VALUES","ORIGINAL_SCALAR_VALUES",
    "SAME_EXPORT_W1_B02","EXPORTED_RGBA_YAML","EXPORTED_SCALAR_YAML",
    "COMPARE_RGBA","COMPARE_SCALARS","COMPARE_SELECTED_MATERIALS",
))
class PrivatePhaseError(ValueError):
    def __init__(self,phase):
        if phase not in SAFE_PHASES:
            raise ValueError("unknown_private_material_value_phase")
        self.phase=phase
        super().__init__("private_material_values_"+phase)

def assess(source_colors,source_scalars,w1,actual_colors,actual_scalars):
    """Compare only selected real Material21 documents; reject inexact ID coverage."""
    if (type(source_colors) is not dict or type(source_scalars) is not dict
        or len(source_colors)!=EXPECTED_MATERIALS
        or set(source_colors)!=set(source_scalars)
        or type(w1) is not dict or type(w1.get("objects")) is not list
        or type(actual_colors) is not dict or type(actual_scalars) is not dict):
        raise ValueError("incomplete_source_5_Material21_value_scope")
    selected=[]
    seen=set()
    for row in w1["objects"]:
        if type(row) is not dict or row.get("class_id")!=21:
            continue
        key=colors._source_id(row.get("source"))
        if key not in source_colors:
            continue
        if key in seen:
            raise ValueError("duplicate_SHA_original_Particle108_material_export_identity")
        seen.add(key)
        selected.append(row)
    if seen!=set(source_colors) or len(selected)!=EXPECTED_MATERIALS:
        raise ValueError("missing_original_particle108_source_to_sameexport_material")
    ptrs=[colors._export_pointer(row["export"]) for row in selected]
    if len(set(ptrs))!=EXPECTED_MATERIALS:
        raise ValueError("colliding_original_particle108_exported_material_pointer")
    wanted=set(ptrs)
    # Public parser may cover hundreds of export objects; filter using exact
    # private source-selected W1 pointer, never a guessed file name or GUID.
    if not wanted.issubset(actual_colors) or not wanted.issubset(actual_scalars):
        raise ValueError("missing_original_particle108_exported_Material_YAML")
    scoped={"schema_version":1,"export_instance":w1.get("export_instance"),
            "objects":selected}
    try:
        c=colors.compare(scoped,source_colors,{k:actual_colors[k] for k in wanted})
    except (ValueError,KeyError,TypeError) as exc:
        raise PrivatePhaseError("COMPARE_RGBA") from None
    try:
        s=scalars.compare(scoped,source_scalars,{k:actual_scalars[k] for k in wanted})
    except (ValueError,KeyError,TypeError) as exc:
        raise PrivatePhaseError("COMPARE_SCALARS") from None
    if (c["source_materials_verified"]!=EXPECTED_MATERIALS
        or c["yaml_materials_compared"]!=EXPECTED_MATERIALS
        or s["original_materials_verified"]!=EXPECTED_MATERIALS
        or s["exported_materials_compared"]!=EXPECTED_MATERIALS
        or any(c[k]!=0 for k in ("engine_material_redirects_excluded",
                                 "font_importer_materials_excluded"))
        or any(s[k]!=0 for k in ("engine_redirects_excluded",
                                 "font_importer_materials_excluded"))):
        raise ValueError("nonexact_Particle108_sameexport_Material_population")
    matched=(c["original_material_color_values_preserved"] is True
             and s["scalar_values_preserved"] is True)
    return {
        "schema_version":1,"status":MATCH if matched else MISMATCH,
        "selected_SHA_original_Particle108_source_Material21_objects":EXPECTED_MATERIALS,
        "original_source_particle_Renderer_Material_use_slots":108,
        "same_instance_true_source_to_export_Material21_PPtrs":EXPECTED_MATERIALS,
        "RGBA_slots_compared":c["color_slots_compared"],
        "original_Materials_with_nonidentity_RGBA":c["materials_with_original_nonidentity_colors"],
        "missing_RGBA_slots":c["missing_color_slots"],
        "extra_RGBA_slots":c["unexpected_color_slots"],
        "changed_RGBA_values":c["changed_color_values"],
        "RGBA_mismatched_Materials":c["mismatched_materials"],
        "float32_slots_compared":s["float_slots_compared"],
        "int32_slots_compared":s["int_slots_compared"],
        "missing_scalar_slots":s["missing_scalar_slots"],
        "extra_scalar_slots":s["extra_scalar_slots"],
        "changed_float32_values":s["changed_float32_values"],
        "changed_int32_values":s["changed_int32_values"],
        "scalar_mismatched_Materials":s["mismatched_materials"],
        "all_selected_RGBA_scalar_values_preserved":matched,
        "original_Shader48_program_or_variant_recovered":False,
        "actual_Unity_import_GPU_color_or_phone_emitter_verified":False,
        "private_Material_names_value_bytes_IDs_Guids_published":False,
    }

def run(original,manifest,project,w1_trace,b02_trace):
    if any(p.is_symlink() or any(a.is_symlink() for a in p.parents)
           for p in (original,manifest,project,w1_trace,b02_trace)):
        raise ValueError("unsafe_source_or_export_private_path")
    selected={}
    try:
        source_result=particle.run(original,manifest,private_material_texenvs=selected)
    except (ValueError,KeyError,TypeError) as exc:
        raise PrivatePhaseError("SOURCE_SELECTED_GRAPH") from None
    if (source_result.get("status")!=SOURCE_STATUS
        or source_result.get("original_108_use_ParticleShader48_reference_authenticated") is not True
        or source_result.get("original_particle_material_objects")!=EXPECTED_MATERIALS
        or len(selected)!=EXPECTED_MATERIALS):
        raise ValueError("unverified_original_five_particle_Materials")
    import UnityPy
    source_colors={}
    source_scalars={}
    by_owner={}
    for owner,pid in selected:
        if owner not in particle.source.MATERIAL_OWNERS or type(pid) is not int or pid<=0:
            raise ValueError("invalid_private_particle_Material_owner_ID")
        by_owner.setdefault(owner,set()).add(pid)
    for owner,ids in by_owner.items():
        path=original/"Raft_Data"/owner
        if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
            raise ValueError("selected_original_particle_Material_SHA_changed")
        for obj in UnityPy.load(str(path)).file.objects.values():
            if obj.path_id not in ids:
                continue
            key=(owner,obj.path_id)
            if obj.type.name!="Material" or key in source_colors:
                raise ValueError("selected_source_particle_material_wrong_Class21")
            saved=obj.read_typetree().get("m_SavedProperties")
            if not isinstance(saved,dict) or "m_Colors" not in saved:
                raise ValueError("selected_source_Particle_material_missing_colors")
            try:
                source_colors[key]=colors.normalize_colors(saved["m_Colors"])
            except (ValueError,KeyError,TypeError) as exc:
                raise PrivatePhaseError("ORIGINAL_RGBA_VALUES") from None
            try:
                source_scalars[key]=scalars.normalize(saved)
            except (ValueError,KeyError,TypeError) as exc:
                raise PrivatePhaseError("ORIGINAL_SCALAR_VALUES") from None
    if set(source_colors)!=set(selected):
        raise ValueError("selected_source_original_Particle_five_Material_coverage")
    w1=json.loads(w1_trace.read_text("utf-8"))
    b02=json.loads(b02_trace.read_text("utf-8"))
    try:
        sameexport.combine_same_export(w1,b02)
    except (ValueError,KeyError,TypeError) as exc:
        raise PrivatePhaseError("SAME_EXPORT_W1_B02") from None
    try:
        exported_color=colors.exported_colors(project)
    except (ValueError,KeyError,TypeError) as exc:
        raise PrivatePhaseError("EXPORTED_RGBA_YAML") from None
    try:
        exported_scalar=scalars.exported_scalars(project)
    except (ValueError,KeyError,TypeError) as exc:
        raise PrivatePhaseError("EXPORTED_SCALAR_YAML") from None
    try:
        result=assess(source_colors,source_scalars,w1,exported_color,exported_scalar)
    except PrivatePhaseError:
        raise
    except (ValueError,KeyError,TypeError) as exc:
        raise PrivatePhaseError("COMPARE_SELECTED_MATERIALS") from None
    result["original_six_scenes_SHA_verified"]=True
    result["original_four_shader_Material_owner_SHA_verified"]=True
    result["one_real_W1_B02_same_export_instance_verified"]=True
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","project","w1-trace","b02-trace","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())
        or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("unsafe_output_inside_private_original_export")
    try:
        report=run(a.original,a.manifest,a.project,a.w1_trace,a.b02_trace)
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "safe_phase":(exc.phase if isinstance(exc,PrivatePhaseError) else "UNCLASSIFIED"),
                "actual_Unity_import_GPU_color_or_phone_emitter_verified":False,
                "private_Material_names_value_bytes_IDs_Guids_published":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_PARTICLE108_5M_TRUE_RGBA_SCALAR_SAMEEXPORT="+json.dumps(report,sort_keys=True))
    return 0 if report["status"] in (MATCH,MISMATCH) else 2

if __name__=="__main__":
    raise SystemExit(main())
