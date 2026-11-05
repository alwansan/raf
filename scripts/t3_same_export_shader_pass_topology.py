#!/usr/bin/env python3
"""T3 authentic selected ten Shader48 parsed Passes vs nine true ShaderLab outputs.

A prerequisite SAME export must already prove 41 exact original Material→Shader
typed source/export refs and all custom Shader .shader/.meta GUID targets.
Original m_ParsedForm author pass count is compared only to its exact traced
Shader48 source identity and the corresponding real .shader GUID, never names.
One original Shader exported to a Unity builtin pointer is excluded from custom
ShaderLab Pass counting. No source programs or per-object IDs/Shader names leak.
This compares structure, NOT native compiled variants, runtime or phone pixels.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path

from scripts import t3_material_shader_same_export as links
from scripts import t3_original_shader_pass_topology as original
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.probe_a13_exported_material_shader_guids import GUID,BUILTIN
from scripts.verify_export_lineage import identity,pointer

SOURCE_EXPECTED_SHADERS=10
SOURCE_EXPECTED_PASSES=38
OUTPUT_EXPECTED_CUSTOM=9


def source_profiles(root:Path,needed:set):
    import UnityPy
    if len(needed)!=SOURCE_EXPECTED_SHADERS:
        raise ValueError("original_ten_Shader48_target_scope_changed")
    found={}
    for owner in links.TARGET_OWNERS:
        path=root/"Raft_Data"/owner
        # Prior SHA-authenticated links.original_source(root) must have run.
        for obj in UnityPy.load(str(path)).file.objects.values():
            key=(owner,obj.path_id)
            if key not in needed:continue
            if obj.type.name!="Shader" or key in found:
                raise ValueError("wrong_original_Shader48_type_or_duplicate")
            parsed=obj.read_typetree().get("m_ParsedForm")
            if not isinstance(parsed,dict) or not isinstance(parsed.get("m_SubShaders"),list):
                raise ValueError("missing_original_Shader_parsed_form")
            sub=parsed["m_SubShaders"]
            passes=[]
            for row in sub:
                if not isinstance(row,dict) or not isinstance(row.get("m_Passes"),list):
                    raise ValueError("malformed_original_SubShader_passes")
                if not all(isinstance(p,dict) for p in row["m_Passes"]):
                    raise ValueError("malformed_original_Shader_pass_record")
                passes.append(len(row["m_Passes"]))
            found[key]={"pass_count":sum(passes),"subshader_pass_counts":passes}
    if set(found)!=needed or sum(r["pass_count"] for r in found.values())!=SOURCE_EXPECTED_PASSES:
        raise ValueError("original_ShaderPass_source_population_drift")
    return found


def exported_profiles(assets:Path,guids:set):
    if not assets.is_dir() or assets.is_symlink() or any(p.is_symlink() for p in assets.parents):
        raise ValueError("unsafe_actual_Unity_export")
    if len(guids)!=OUTPUT_EXPECTED_CUSTOM:
        raise ValueError("unexpected_custom_Shader_target_scope")
    found={}
    entries=sorted(assets.rglob("*"))
    if len(entries)>150000 or any(p.is_symlink() for p in entries):
        raise ValueError("unsafe_large_or_linked_shader_export")
    for file in entries:
        if not file.is_file() or not file.name.endswith(".shader.meta"):
            continue
        if file.stat().st_size>256000:raise ValueError("oversize_ShaderImporter_meta")
        gids=GUID.findall(file.read_text("utf8-sig"))
        if len(gids)!=1:raise ValueError("ambiguous_shader_export_meta_GUID")
        gid=gids[0].lower()
        if gid not in guids:continue
        if gid in found:raise ValueError("duplicate_selected_exported_Shader_GUID")
        shader=Path(str(file)[:-5])
        if not shader.is_file() or shader.is_symlink() or shader.stat().st_size>8_000_000:
            raise ValueError("missing_selected_export_ShaderLab_source")
        info=pass_coverage(shader.read_text("utf8-sig"))
        if not info["pass_braces_balanced"]:
            raise ValueError("unbalanced_selected_ShaderLab_source")
        found[gid]={"pass_count":info["pass_count"],
                    "subshader_pass_counts":info["subshader_pass_counts"],
                    "programmed_pass_count":info["passes_with_complete_program"]}
    if set(found)!=guids:
        raise ValueError("missing_selected_ShaderLab_custom_GUID")
    return found


def compare(source:dict,w1:dict,actual:dict,*,real_links_proven:bool):
    if not real_links_proven or len(source)!=SOURCE_EXPECTED_SHADERS:
        raise ValueError("original_41_Material_Shader_same_export_links_unproven")
    rows=w1.get("objects") if isinstance(w1,dict) else None
    if not isinstance(rows,list) or not any(r.get("class_id")==21 for r in rows):
        raise ValueError("missing_same_export_W1_material_trace")
    pairs={}
    builtins=0
    mapping={}
    for row in rows:
        if row.get("class_id")!=48:continue
        key=identity(row["source"])
        if key not in source:continue
        if key in pairs:raise ValueError("duplicate_same_export_Shader48_target")
        target=pointer(row["export"])
        if target[1] in BUILTIN:
            if target[2]!="0":raise ValueError("invalid_engine_builtin_Shader_reference")
            builtins+=1
            pairs[key]=None
        else:
            if target[2]!="3":raise ValueError("invalid_custom_Shader_importer_type")
            if target[1] in mapping:raise ValueError("distinct_original_Shaders_collide_in_export_GUID")
            mapping[target[1]]=key
            pairs[key]=target[1]
    if set(pairs)!=set(source) or builtins!=1 or len(mapping)!=OUTPUT_EXPECTED_CUSTOM:
        raise ValueError("same_export_Shader_targets_not_ten_with_nine_custom")
    if set(actual)!=set(mapping):
        raise ValueError("exact_custom_Shader_meta_file_count_mismatch")
    histogram=Counter()
    by_owner=defaultdict(Counter)
    totals=Counter()
    for key,guid in pairs.items():
        value=source[key]
        originalpass=value["pass_count"]
        sub=value["subshader_pass_counts"]
        if (type(originalpass) is not int or originalpass<0 or
            not isinstance(sub,list) or any(type(v) is not int or v<0 for v in sub)
            or sum(sub)!=originalpass):
            raise ValueError("invalid_original_parsed_shader_profile")
        totals["original_ten_shader_passes"]+=originalpass
        totals["original_ten_shader_subshaders"]+=len(sub)
        histogram[originalpass]+=1
        if guid is None:
            totals["original_builtin_transport_passes"]+=originalpass
            totals["original_builtin_transport_targets"]+=1
            continue
        out=actual[guid]
        if (not isinstance(out,dict) or
            any(type(out.get(k)) is not int or out[k]<0 for k in ("pass_count","programmed_pass_count"))
            or not isinstance(out.get("subshader_pass_counts"),list) or
            any(type(v) is not int or v<0 for v in out["subshader_pass_counts"])
            or sum(out["subshader_pass_counts"])!=out["pass_count"]
            or out["programmed_pass_count"]>out["pass_count"]):
            raise ValueError("invalid_actual_ShaderLab_profile")
        destpass=out["pass_count"]
        owner=key[0]
        totals["original_custom_Shader_pass_records"]+=originalpass
        totals["exported_custom_ShaderLab_passes"]+=destpass
        totals["exported_custom_ShaderLab_programmed_passes"]+=out["programmed_pass_count"]
        totals["selected_custom_ShaderLab_count"]+=1
        totals["custom_shaders_with_pass_deficit"]+=int(originalpass>destpass)
        totals["custom_shaders_with_extra_passes"]+=int(originalpass<destpass)
        totals["missing_original_passes_in_custom_ShaderLab"]+=max(0,originalpass-destpass)
        totals["extra_exported_custom_ShaderLab_passes"]+=max(0,destpass-originalpass)
        by_owner[owner]["original_custom_shader_count"]+=1
        by_owner[owner]["original_custom_passes"]+=originalpass
        by_owner[owner]["exported_ShaderLab_passes"]+=destpass
        by_owner[owner]["missing_passes"]+=max(0,originalpass-destpass)
    if totals["original_ten_shader_passes"]!=SOURCE_EXPECTED_PASSES:
        raise ValueError("original_10_ShaderPass_count_changed")
    if totals["selected_custom_ShaderLab_count"]!=OUTPUT_EXPECTED_CUSTOM:
        raise ValueError("incomplete_same_export_custom_ShaderLab_scope")
    status=("SCOPED_SHADERLAB_PASS_TOPOLOGY_DEFICIT"
           if totals["missing_original_passes_in_custom_ShaderLab"]>0
           else "SCOPED_SHADERLAB_PASS_COUNT_MATCH_NOT_PROGRAM_EQUIVALENCE")
    return {
       "schema_version":1,
       "experiment":"T3-authentic-Shader48-source-to-export-ShaderLab-structural-topology",
       "same_export_original_to_ShaderLab_identity_proven":True,
       "original_shader_pass_count_histogram":dict(sorted(histogram.items())),
       "counts":dict(sorted(totals.items())),
       "custom_shader_source_owner_aggregate":{k:dict(sorted(v.items())) for k,v in sorted(by_owner.items())},
       "original_compiled_variant_program_equivalence_verified":False,
       "source_shader_names_or_per_object_identifiers_published":False,
       "unity_or_android_GPU_pixels_verified":False,
       "status":status,
    }


def run(root:Path,project:Path,w1path:Path,b02path:Path):
    # Reuse exact accepted authenticated source+YAML+Shader importer test.
    links_report=links.run(root,project,w1path,b02path)
    if not links_report["original_Material_Shader_pptr_target_preserved"]:
        raise ValueError("same_export_Shader_link_prerequisite_failed")
    edges,targets=links.original_source(root)
    if len(edges)!=links.MATERIAL_COUNT:raise ValueError("untrusted_Material41_scope")
    profiles=source_profiles(root,targets)
    w1=json.loads(w1path.read_text("utf8"))
    needed=set()
    for row in w1["objects"]:
        if row.get("class_id")==48 and identity(row["source"]) in targets:
            ptr=pointer(row["export"])
            if ptr[1] not in BUILTIN:needed.add(ptr[1])
    meta=exported_profiles(project/"Assets",needed)
    return compare(profiles,w1,meta,real_links_proven=True)


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for flag in ("original","project","w1-trace","b02-trace","out"):
        ap.add_argument("--"+flag,type=Path,required=True)
    a=ap.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())
        or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("unsafe_report_location")
    try:report=run(a.original,a.project,a.w1_trace,a.b02_trace)
    except Exception as ex:
        report={"schema_version":1,
                "experiment":"T3-authentic-Shader48-source-to-export-ShaderLab-structural-topology",
                "status":"INCONCLUSIVE","exception_type":type(ex).__name__,
                "original_compiled_variant_program_equivalence_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("T3_EXACT_ORIGINAL_TO_EXPORT_SHADERLAB_PASS_GAP "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]=="SCOPED_SHADERLAB_PASS_COUNT_MATCH_NOT_PROGRAM_EQUIVALENCE" else 2
if __name__=="__main__":raise SystemExit(main())
