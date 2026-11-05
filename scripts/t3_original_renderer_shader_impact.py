#!/usr/bin/env python3
"""T3: real original 6-scene Renderer→Material→Shader48 use-frequency census.

Do not equate source Renderer slot counts with GPU draw calls, visibility or
post-vendor Dummy Shader GUIDs. This joins authentic original one-based PPtrs,
not names inferred from exported ShaderLab. No private asset names/IDs are
published; only source *owner basenames* already public in ZIP2 and counts.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path, PurePosixPath

from scripts.b03_original_renderer_materials import (
    RENDERER_CLASSES, analyze_scene, manifest_provider_basename_counts,
    pointer_shape, SourceError,
)
from scripts.b21_scene_lightmap_links import PIN as SCENE_PINS, verify_source
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_probe_original_shader_links import resolve_pointer
from scripts.w1_stage_zip2_owners import fingerprint

MATERIAL_OWNERS=("resources.assets","sharedassets0.assets","sharedassets1.assets")
SHADER_OWNERS_SELECTED=(*MATERIAL_OWNERS,"sharedassets6.assets")
BUILTIN_NAMES=frozenset(("unity_builtin_extra","unity default resources","unity_default_resources"))
SCENE_RENDERERS=1495
SCENE_MATERIAL_SLOTS=1639
SCENE_NONNULL_SLOTS=1635
SCENE_NULL_SLOTS=4
MAX_SCOPE=200000
STATUS="AUTHENTIC_SIX_SCENE_RENDERER_SHADER_USE_FREQUENCY_VERIFIED"


def band(n:int):
    if type(n) is not int or n <= 0:
        raise ValueError("invalid_original_Shader_use_count")
    return "1" if n==1 else "2-4" if n<=4 else "5-16" if n<=16 else "17+"


def summarize(original_edges:list, materials:dict, typed_shaders:dict,
              *, expected_slots:int=SCENE_MATERIAL_SLOTS,
              expected_nonnull:int=SCENE_NONNULL_SLOTS,
              source_sha_authenticated:bool=False):
    """Pure original-source join: edge=(scene,pid,renderer-class,material-key|None)."""
    if (not isinstance(original_edges,list) or not isinstance(materials,dict)
        or not isinstance(typed_shaders,dict) or len(original_edges)!=expected_slots
        or expected_nonnull<0 or expected_nonnull>expected_slots):
        raise ValueError("incomplete_original_6_scene_material_scope")
    expected_owner_set=set(MATERIAL_OWNERS)
    shader_owner_set=set(SHADER_OWNERS_SELECTED)
    slot_by_shader=Counter()
    renderers_by_shader=defaultdict(set)
    materials_by_shader=defaultdict(set)
    distinct_renderers=set()
    count=Counter()
    used_materials=set()
    by_shader_owner=defaultdict(Counter)
    for row in original_edges:
        if not isinstance(row,tuple) or len(row)!=4:
            raise ValueError("malformed_original_renderer_material_edge")
        scene,pid,kind,material=row
        if (scene not in SCENE_PINS or type(pid) is not int or pid<=0
            or kind not in RENDERER_CLASSES):
            raise ValueError("invalid_original_renderer_identity")
        renderer=(scene,pid)
        distinct_renderers.add(renderer)
        count["original_material_slots"]+=1
        if material is None:
            count["original_null_material_slots"]+=1
            continue
        if (not isinstance(material,tuple) or len(material)!=2
            or material[0] not in expected_owner_set
            or type(material[1]) is not int or material[1]<=0):
            raise ValueError("unverified_original_material_target_owner")
        count["original_nonnull_material_slots"]+=1
        if material not in materials:
            raise ValueError("original_material_target_missing_class21")
        used_materials.add(material)
        shader=materials[material]
        if shader is None:
            count["original_Material_with_null_Shader_slots"]+=1
            continue
        if (not isinstance(shader,tuple) or len(shader)!=2
            or type(shader[0]) is not str or not shader[0]
            or type(shader[1]) is not int or shader[1]<=0):
            raise ValueError("malformed_original_Material_Shader_pointer")
        if shader[0] in shader_owner_set:
            if shader not in typed_shaders:
                raise ValueError("original_Shader48_target_missing_or_wrong_type")
            shdata=typed_shaders[shader]
            if (not isinstance(shdata,dict)
                or type(shdata.get("subshaders")) is not int
                or type(shdata.get("passes")) is not int
                or shdata["subshaders"]<0 or shdata["passes"]<0):
                raise ValueError("malformed_original_typed_Shader48_parsed_structure")
            count["original_slots_to_verified_Shader48"]+=1
            count["original_slots_to_verified_multi_pass_Shader48"]+=int(shdata["passes"]>1)
        elif shader[0].lower() in BUILTIN_NAMES:
            count["original_slots_to_unstaged_Unity_engine_Shader"]+=1
        else:
            count["original_slots_to_unstaged_other_Shader"]+=1
        slot_by_shader[shader]+=1
        renderers_by_shader[shader].add(renderer)
        materials_by_shader[shader].add(material)
        by_shader_owner[shader[0]]["material_slots"]+=1
    if (count["original_material_slots"]!=expected_slots
        or count["original_nonnull_material_slots"]!=expected_nonnull
        or count["original_null_material_slots"]!=expected_slots-expected_nonnull):
        raise ValueError("original_B03_renderer_material_accounting_drift")
    # Keep private tuples only in memory; no per-target identity commitment,
    # hashes, original names, GUID or individual serialized IDs in report.
    freq=Counter(band(n) for n in slot_by_shader.values())
    uniq_renderer_freq=Counter(band(len(renderers_by_shader[k])) for k in slot_by_shader)
    typed_keys={key for key in slot_by_shader if key in typed_shaders}
    raw_sorted=sorted(slot_by_shader.values(), reverse=True)
    verified_sorted=sorted((slot_by_shader[k] for k in typed_keys),reverse=True)
    by_owner={
      owner:{"renderer_material_slots":dict(stats)["material_slots"],
             "distinct_referenced_source_Shaders":sum(k[0]==owner for k in slot_by_shader),
             "typed_Shader48_targets_verified":sum(k[0]==owner for k in typed_keys)}
      for owner,stats in sorted(by_shader_owner.items())
    }
    return {
        "schema_version":1,
        "experiment":"T3-authentic-original-six-scenes-Renderer-Material-Shader48-impact",
        "six_original_scenes_sha_verified":source_sha_authenticated,
        "original_material_target_owners_sha_verified":len(MATERIAL_OWNERS) if source_sha_authenticated else 0,
        "original_selected_shader_owners_sha_verified":len(SHADER_OWNERS_SELECTED) if source_sha_authenticated else 0,
        "original_renderer_material_slots":count["original_material_slots"],
        "original_nonnull_renderer_material_slots":count["original_nonnull_material_slots"],
        "original_null_renderer_material_slots":count["original_null_material_slots"],
        "original_renderer_objects_with_any_material_slots":len(distinct_renderers),
        "original_distinct_referenced_Material_objects":len(used_materials),
        "original_distinct_referenced_Shader_objects":len(slot_by_shader),
        "original_distinct_typed_Shader48_targets":len(typed_keys),
        "counts":{key:count[key] for key in (
            "original_Material_with_null_Shader_slots",
            "original_slots_to_verified_Shader48",
            "original_slots_to_verified_multi_pass_Shader48",
            "original_slots_to_unstaged_Unity_engine_Shader",
            "original_slots_to_unstaged_other_Shader")},
        "per_authenticated_source_shader_owner_counts":by_owner,
        "original_Shader_material_slot_use_frequency_bands":dict(sorted(freq.items())),
        "original_Shader_distinct_renderer_use_frequency_bands":dict(sorted(uniq_renderer_freq.items())),
        "top_ten_original_shader_slot_counts_no_identity":raw_sorted[:10],
        "top_ten_typed_Shader48_slot_counts_no_identity":verified_sorted[:10],
        "source_shader_target_names_guids_ids_hashes_disclosed":False,
        "postvendor_dummy_marker_or_same_export_Shader_identity_checked":False,
        "unity_or_android_drawcalls_white_pixels_verified":False,
        "renderers_without_material_slots_not_counted_here":True,
        "status":STATUS if source_sha_authenticated else "SYNTHETIC_OR_UNAUTHENTICATED_SOURCE_ONLY",
    }


def load_original(source:Path, manifest:Path):
    import UnityPy
    root=source/"Raft_Data"
    if any(p.is_symlink() for p in (source,root,*source.parents)):
        raise ValueError("unsafe_original_source_root")
    seen=manifest_provider_basename_counts(manifest)
    for owner in SHADER_OWNERS_SELECTED:
        if seen.get(owner)!=1:
            raise ValueError("ambiguous_material_or_shader_original_manifest_owner")
        path=root/owner
        if path.is_symlink() or not path.is_file() or fingerprint(path)!=SHADER_OWNERS[owner]:
            raise ValueError("original_Material_or_Shader_owner_SHA_mismatch")
    original_edges=[]
    count=Counter()
    for name,pin in SCENE_PINS.items():
        path=root/name
        verify_source(path,pin)
        file=UnityPy.load(str(path)).file
        ext=[r.path for r in file.externals]
        objects=list(file.objects.values())
        b03=analyze_scene(objects,len(ext),ext,seen)
        bc=b03["counts"]
        count["renderers"]+=bc.get("original_renderer_objects",0)
        count["materials"]+=bc.get("original_material_slots",0)
        count["nonnull"]+=bc.get("external_target_unverified",0)
        count["null"]+=bc.get("null_material_slot",0)
        identity={o.path_id:o.type.name for o in objects}
        for obj in objects:
            if obj.type.name not in RENDERER_CLASSES:continue
            tree=obj.read_typetree(check_read=False)
            if not isinstance(tree,dict) or not isinstance(tree.get("m_Materials"),list):
                raise ValueError("original_renderer_type_tree_missing_materials")
            for ptr in tree["m_Materials"]:
                state,fid,pid=pointer_shape(ptr,identity,len(ext))
                if state=="null_material_slot":
                    target=None
                elif state=="external_target_unverified":
                    owner=PurePosixPath(ext[fid-1].replace("\\","/")).name
                    if owner not in MATERIAL_OWNERS or seen[owner]!=1:
                        raise ValueError("source_scene_material_owner_outside_three_pinned")
                    target=(owner,pid)
                else:
                    raise ValueError("unexpected_original_scene_material_pointer_kind")
                original_edges.append((name,obj.path_id,str(obj.type.name),target))
    if (count["renderers"],count["materials"],count["nonnull"],count["null"])!=(
         SCENE_RENDERERS,SCENE_MATERIAL_SLOTS,SCENE_NONNULL_SLOTS,SCENE_NULL_SLOTS):
        raise ValueError("original_B03_six_scene_source_counts_changed")
    used={row[3] for row in original_edges if row[3] is not None}
    by_owner=defaultdict(set)
    for owner,pid in used:by_owner[owner].add(pid)
    mats={}
    for owner in MATERIAL_OWNERS:
        file=UnityPy.load(str(root/owner)).file
        ext=[r.path for r in file.externals]
        selected=by_owner[owner]
        for obj in file.objects.values():
            if obj.path_id not in selected:continue
            if obj.type.name!="Material" or (owner,obj.path_id) in mats:
                raise ValueError("original_renderer_Material_target_not_class21")
            tree=obj.read_typetree()
            ptr=tree.get("m_Shader")
            if not isinstance(ptr,dict):
                raise ValueError("missing_original_Material_Shader_pointer")
            if (type(ptr.get("m_PathID")) is not int
                or ptr["m_PathID"]<0):
                raise ValueError("invalid_original_Shader_PathID")
            mats[(owner,obj.path_id)]=resolve_pointer(owner,ext,ptr)
    if set(mats)!=used:
        raise ValueError("incomplete_original_material_source_dependency")
    needed={v for v in mats.values() if v is not None and v[0] in SHADER_OWNERS_SELECTED}
    by_shader_owner=defaultdict(set)
    for owner,pid in needed:by_shader_owner[owner].add(pid)
    typed={}
    for owner in SHADER_OWNERS_SELECTED:
        selected=by_shader_owner[owner]
        if not selected:continue
        file=UnityPy.load(str(root/owner)).file
        for obj in file.objects.values():
            if obj.path_id not in selected:continue
            if obj.type.name!="Shader" or (owner,obj.path_id) in typed:
                raise ValueError("original_Material_Shader_target_not_class48")
            tree=obj.read_typetree()
            parsed=tree.get("m_ParsedForm")
            if not isinstance(parsed,dict) or not isinstance(parsed.get("m_SubShaders"),list):
                raise ValueError("missing_original_shader_parsed_form")
            sub=parsed["m_SubShaders"]
            passes=0
            for row in sub:
                if not isinstance(row,dict) or not isinstance(row.get("m_Passes"),list):
                    raise ValueError("unexpected_original_Shader_subshader_pass_schema")
                passes+=len(row["m_Passes"])
            typed[(owner,obj.path_id)]={"passes":passes,"subshaders":len(sub)}
    if set(typed)!=needed:
        raise ValueError("incomplete_typed_original_Shader48_sources")
    return summarize(original_edges,mats,typed,source_sha_authenticated=True)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for flag in ("original","manifest","out"):
        p.add_argument("--"+flag,required=True,type=Path)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_private_original_report_location")
    try:result=load_original(a.original,a.manifest)
    except Exception as exc:
        result={"schema_version":1,"experiment":"T3-authentic-original-six-scenes-Renderer-Material-Shader48-impact",
                "status":"INCONCLUSIVE","error_type":type(exc).__name__,
                "postvendor_dummy_marker_or_same_export_Shader_identity_checked":False,
                "unity_or_android_drawcalls_white_pixels_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("T3_AUTHENTIC_ORIGINAL_SCENE_SHADER_USE "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
