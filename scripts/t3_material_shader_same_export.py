#!/usr/bin/env python3
"""T3 bounded SHA-pinned original 41 Material→10 Shader→SAME export proof.

Unlike the A13 exported-only GUID guard or B43 Material-only keyword parity,
this joins actual original one-based m_Shader source pointer, typed Shader48
target, W1 same-instance source/export trace, actual exported Material.m_Shader
PPtr and .shader.meta/.shader importer target. ShaderLab structural pass
count is diagnostic, NOT compiled program/Unity/Android pixel fidelity.
No game asset names/IDs/GUIDs/source YAML ever leave the runner.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_probe_original_shader_links import resolve_pointer
from scripts.verify_export_lineage import (identity, pointer, document_key,
                                           check as check_lineage,actual_graph)
from scripts import t3_same_export_material_colors as colors
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.probe_a13_exported_material_shader_guids import GUID,BUILTIN

OWNER="sharedassets6.assets"
TARGET_OWNERS=("sharedassets0.assets","sharedassets1.assets","sharedassets6.assets","resources.assets")
MATERIAL_COUNT=41
SHADER_COUNT=10


def original_source(root):
    import UnityPy
    sources={}
    shaders=set()
    for owner in TARGET_OWNERS:
        path=root/"Raft_Data"/owner
        if path.is_symlink() or not path.is_file() or fingerprint(path)!=SHADER_OWNERS[owner]:
            raise ValueError("unverified_original_Shader_source_SHA")
        env=UnityPy.load(str(path))
        if owner==OWNER:
            ext=[ref.path for ref in env.file.externals]
            for obj in env.file.objects.values():
                if obj.type.name!="Material":continue
                key=(owner,obj.path_id)
                if key in sources:raise ValueError("duplicate_original_Material")
                data=obj.read_typetree()
                if "m_Shader" not in data:raise ValueError("missing_original_Material_m_Shader")
                target=resolve_pointer(owner,ext,data["m_Shader"])
                if target is None:raise ValueError("original_Material_null_shader")
                if target[0] not in TARGET_OWNERS:raise ValueError("original_Shader_owner_not_staged")
                sources[key]=target
        for obj in env.file.objects.values():
            if obj.type.name=="Shader":
                key=(owner,obj.path_id)
                if key in shaders:raise ValueError("duplicate_original_Shader_identity")
                shaders.add(key)
    targets=set(sources.values())
    if len(sources)!=MATERIAL_COUNT or len(targets)!=SHADER_COUNT:
        raise ValueError("original_41_Material_or_10_Shader_scope_changed")
    if not targets.issubset(shaders):raise ValueError("original_Shader_target_not_typed_class48")
    return sources,targets


def shader_metadata(assets,shader_guids):
    if assets.is_symlink() or not assets.is_dir() or any(x.is_symlink() for x in assets.parents):
        raise ValueError("unsafe_Unity_exported_Assets")
    paths=sorted(assets.rglob("*"))
    if len(paths)>150000 or any(p.is_symlink() for p in paths):
        raise ValueError("unsafe_or_oversize_Unity_export_files")
    matching={}
    shaderfiles=0
    for path in paths:
        if not path.is_file() or not path.name.endswith(".shader.meta"):
            continue
        shaderfiles+=1
        if path.stat().st_size>256_000:raise ValueError("oversized_ShaderImporter_meta")
        hits=GUID.findall(path.read_text("utf-8-sig"))
        if len(hits)!=1:raise ValueError("invalid_export_Shader_meta_GUID")
        guid=hits[0].lower()
        if guid in matching:raise ValueError("duplicate_export_Shader_meta_GUID")
        sibling=Path(str(path)[:-5])
        if not sibling.is_file() or sibling.is_symlink():
            raise ValueError("orphaned_exported_Shader_source_meta")
        matching[guid]=sibling
    selected={}
    for guid in shader_guids:
        path=matching.get(guid)
        if path is None:raise ValueError("missing_export_ShaderLab_meta_for_original_target")
        if path.stat().st_size>8_000_000:
            raise ValueError("oversized_export_ShaderLab_source")
        selected[guid]=path
    counts=Counter()
    for path in selected.values():
        info=pass_coverage(path.read_text("utf-8-sig"))
        counts["selected_shader_files"]+=1
        counts["shaderlab_total_parsed_passes"]+=info["pass_count"]
        counts["shaderlab_passes_with_program_blocks"]+=info["passes_with_complete_program"]
        counts["shaderlab_sources_with_programs"]+=int(info["all_subshaders_programmed"])
        counts["shaderlab_sources_with_no_passes"]+=int(info["pass_count"]==0)
        counts["shaderlab_braces_balanced"]+=int(info["pass_braces_balanced"])
    counts["all_export_shader_files"]=shaderfiles
    return counts


def selected_compare(source_edges,original_shaders,w1,b02,all_actual,assets,
                     *, shader_meta_fn=shader_metadata):
    """Strict same-instance input and exact link comparison, private graph in RAM."""
    if len(source_edges)!=MATERIAL_COUNT or len(original_shaders)!=SHADER_COUNT:
        raise ValueError("untrusted_selected_source_scope")
    selected=colors.select_same_export_materials(w1,b02)
    materials=selected["objects"]
    for row in materials:
        if identity(row["source"]) not in source_edges:
            raise ValueError("different_selected_Original_Material_trace")
    if set(identity(row["source"]) for row in materials)!=set(source_edges):
        raise ValueError("missing_same_export_Material_trace_source")
    needed=set(source_edges.values())
    source_shaders=[]
    for row in w1["objects"]:
        if row.get("class_id")!=48:continue
        key=identity(row["source"])
        if key in needed:source_shaders.append(row)
    if set(identity(row["source"]) for row in source_shaders)!=needed:
        raise ValueError("missing_same_export_Shader_trace")
    joined={"schema_version":1,"export_instance":selected["export_instance"],
            "objects":source_shaders+materials}
    keys=set()
    for row in materials:
        export=pointer(row["export"])
        if row.get("exportable") is False:
            raise ValueError("selected_source_material_redirected_not_exported")
        key=document_key(export)
        if key in keys:raise ValueError("duplicate_selected_Material_export_pointer")
        keys.add(key)
    actual={key:value for key,value in all_actual.items()
            if (key[0],key[1]) in keys}
    if len(actual)!=MATERIAL_COUNT:raise ValueError("missing_actual_41_Material_Shader_field")
    report=check_lineage(joined,source_edges,original_shaders,actual)
    if (report["source_material_edges_verified"]!=MATERIAL_COUNT
        or report["source_shader_objects_traced"]!=SHADER_COUNT
        or report["actual_material_documents_verified"]!=MATERIAL_COUNT
        or not report["original_exported_material_shader_assignments_verified"]):
        raise ValueError("scoped_original_Shader_link_parity_failed")
    exported_custom=set()
    builtin=0
    for row in source_shaders:
        dest=pointer(row["export"])
        if dest[1] in BUILTIN:
            if dest[2]!="0":raise ValueError("invalid_engine_Shader_export_pointer")
            builtin+=1
        else:
            if dest[2]!="3":raise ValueError("unexpected_custom_Shader_export_type")
            exported_custom.add(dest[1])
    counts=shader_meta_fn(assets,exported_custom)
    if counts["selected_shader_files"]!=len(exported_custom):
        raise ValueError("not_all_selected_custom_shaders_have_ShaderLab_meta")
    return {
      "schema_version":1,"experiment":"T3-41-original-Material-to-Shader-same-export",
      "authenticated_original_materials":MATERIAL_COUNT,
      "original_typed_distinct_shader_targets":SHADER_COUNT,
      "real_same_instance_original_material_shaders_verified":report["source_material_edges_verified"],
      "real_same_instance_shader_trace_objects":report["source_shader_objects_traced"],
      "actual_exported_material_shader_fields_exact":report["actual_material_documents_verified"],
      "selected_engine_shader_transport_targets":builtin,
      "selected_custom_ShaderLab_meta_targets":len(exported_custom),
      "shaderlab_structural_aggregate":dict(sorted(counts.items())),
      "original_Material_Shader_pptr_target_preserved":True,
      "original_Shader_program_variants_or_GPU_pixels_verified":False,
      "full_game_scope_verified":False,
      "status":"SCOPED_ORIGINAL_SHADER_POINTER_AND_SHADERLAB_META_MATCH",
    }


def run(root,project,w1path,b02path):
    source,shaders=original_source(root)
    w1=json.loads(w1path.read_text("utf8"))
    b02=json.loads(b02path.read_text("utf8"))
    actual=actual_graph(project)
    return selected_compare(source,shaders,w1,b02,actual,project/"Assets")


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for k in ("original","project","w1-trace","b02-trace","out"):
        p.add_argument("--"+k,type=Path,required=True)
    args=p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())
        or args.out.resolve().is_relative_to(args.project.resolve())):
        raise ValueError("unsafe_private_original_or_export_output")
    try:result=run(args.original,args.project,args.w1_trace,args.b02_trace)
    except Exception as e:
        result={"schema_version":1,
                "experiment":"T3-41-original-Material-to-Shader-same-export",
                "status":"INCONCLUSIVE","exception_type":type(e).__name__,
                "original_Material_Shader_pptr_target_preserved":False,
                "original_Shader_program_variants_or_GPU_pixels_verified":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n","utf8")
    print("T3_41_ORIGINAL_MATERIAL_SHADER_SAME_EXPORT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="SCOPED_ORIGINAL_SHADER_POINTER_AND_SHADERLAB_META_MATCH" else 2
if __name__=="__main__":raise SystemExit(main())
