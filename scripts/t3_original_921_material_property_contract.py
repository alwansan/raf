#!/usr/bin/env python3
"""T3 original top-921 Shader48 property declarations versus linked source Materials.

A source-typed property that is not saved in a Material may use its Shader
default. A stale saved property may be deliberately retained. We count these
conditions, not treat them as a graphics or Unity importer failure.
Private names/IDs, shader programs, saved values and materials stay runner-only.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path, PurePosixPath

from scripts import t3_original_921_dxbc_semantic_join as prior
from scripts.b03_original_renderer_materials import RENDERER_CLASSES, pointer_shape
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts.b44_verify_material_colors import normalize_colors
from scripts.b22_verify_material_scalars import normalize as normalize_scalars
from scripts.w1_probe_original_shader_links import resolve_pointer

STATUS = "ORIGINAL_921_SHADER48_TO_RENDERER_LINKED_MATERIAL_PROPERTY_CONTRACT_CENSUSED"
MAX_MATERIALS = 120
MAX_SHADER_PROPERTIES = 256
EXPECTED_SCENE_MATERIAL_SLOTS = 921
SHADER_TYPES = {0:"color",1:"color",2:"float",3:"float",4:"texture"}
SAVED_KINDS = ("texture", "color", "float", "int")
COUNTERS = (
    "source_Shader48_declared_properties",
    "source_Shader48_declared_texture_properties",
    "source_Shader48_declared_color_vector_properties",
    "source_Shader48_declared_float_range_properties",
    "source_Materials_linked_to_921_use_Shader48",
    "source_Material_Renderer_slots_linked_to_921_use_Shader48",
    "source_saved_texture_property_entries", "source_saved_bound_texture_entries",
    "source_saved_null_texture_entries", "source_saved_color_property_entries",
    "source_saved_float_property_entries", "source_saved_int_property_entries",
    "source_declared_property_saved_matches", "source_declared_property_unsaved_uses_default_possible",
    "source_saved_properties_not_declared", "source_saved_wrong_family_entries",
    "source_materials_with_saved_wrong_family",
    "source_materials_with_saved_not_declared",
    "source_materials_with_at_least_one_unsaved_declared",
    "source_renderer_slots_with_saved_wrong_family",
    "source_renderer_slots_with_saved_not_declared",
    "source_renderer_slots_with_at_least_one_unsaved_declared",
    "source_Materials_with_all_declared_properties_explicitly_saved",
    "source_Materials_with_no_declared_props_saved",
    "source_Materials_with_any_declared_texture_bound",
)


def declared_property_families(shader_parsed: dict):
    if type(shader_parsed) is not dict or type(shader_parsed.get("m_PropInfo")) is not dict:
        raise ValueError("unrecognized_original_Shader48_property_header")
    props = shader_parsed["m_PropInfo"].get("m_Props")
    if type(props) is not list or len(props) > MAX_SHADER_PROPERTIES:
        raise ValueError("original_Shader48_property_table_outside_bounds")
    output = {}
    counts = Counter()
    for item in props:
        if type(item) is not dict:
            raise ValueError("malformed_original_Shader_property")
        name, typ = item.get("m_Name"), item.get("m_Type")
        if (type(name) is not str or not 1 <= len(name) <= 256 or "\x00" in name or
            type(typ) is not int or typ not in SHADER_TYPES or name in output):
            raise ValueError("duplicate_or_unsupported_original_Shader_property")
        output[name] = SHADER_TYPES[typ]
        counts[SHADER_TYPES[typ]] += 1
    return output, counts


def normalize_private_saved_properties(props: dict):
    if type(props) is not dict or not {"m_TexEnvs","m_Colors","m_Floats","m_Ints"} <= set(props):
        raise ValueError("missing_original_Material_SavedProperties_family")
    tex = normalize_texenvs(props["m_TexEnvs"])
    colors = normalize_colors(props["m_Colors"])
    numeric = normalize_scalars(props)
    families = {"texture":set(tex),"color":set(colors),
                "float":set(numeric["m_Floats"]),"int":set(numeric["m_Ints"])}
    owned = {}
    for kind,names in families.items():
        if len(names) > 256:
            raise ValueError("oversize_original_saved_property_family")
        for name in names:
            if name in owned:
                raise ValueError("ambiguous_original_property_cross_family")
            owned[name] = kind
    texture_bound = 0
    for name,(ptr,_uv) in tex.items():
        if (type(ptr) is not tuple or len(ptr) != 2 or
            any(type(v) is not int or v < 0 for v in ptr)):
            raise ValueError("malformed_private_original_texture_pointer")
        texture_bound += int(ptr[1] != 0)
    bound_texture_names={name for name,(ptr,_uv) in tex.items() if ptr[1] != 0}
    return owned, {"texture":len(tex),"color":len(colors),
                   "float":len(numeric["m_Floats"]),
                   "int":len(numeric["m_Ints"]), "texture_bound":texture_bound}, bound_texture_names


def classify_private_921_materials(declared: dict, source_materials: dict,
                                   scene_slot_weights: dict):
    """Private join: identities and names never enter aggregate result."""
    if (type(declared) is not dict or not 0 < len(declared) <= MAX_SHADER_PROPERTIES
        or type(source_materials) is not dict or
        type(scene_slot_weights) is not dict or
        not 0 < len(source_materials) <= MAX_MATERIALS or
        set(source_materials) != set(scene_slot_weights)
        or sum(scene_slot_weights.values()) != EXPECTED_SCENE_MATERIAL_SLOTS):
        raise ValueError("untrusted_original_921_Material_Shader_scope")
    if any(type(k) is not str or not k or kind not in ("texture","color","float")
           for k,kind in declared.items()):
        raise ValueError("invalid_original_Shader_property_family")
    counts = Counter({
        "source_Shader48_declared_properties":len(declared),
        "source_Shader48_declared_texture_properties":sum(k=="texture" for k in declared.values()),
        "source_Shader48_declared_color_vector_properties":sum(k=="color" for k in declared.values()),
        "source_Shader48_declared_float_range_properties":sum(k=="float" for k in declared.values()),
        "source_Materials_linked_to_921_use_Shader48":len(source_materials),
        "source_Material_Renderer_slots_linked_to_921_use_Shader48":sum(scene_slot_weights.values()),
    })
    for identity,saved in source_materials.items():
        weight = scene_slot_weights[identity]
        if (type(identity) is not tuple or len(identity)!=2 or
            identity[0] not in prior.prior.original.MATERIAL_OWNERS or
            type(identity[1]) is not int or identity[1]<=0 or
            type(weight) is not int or weight<=0 or
            type(saved) is not dict):
            raise ValueError("invalid_authentic_Material_shaders_or_slot_weights")
        owned, stats, bound_texture_names=normalize_private_saved_properties(saved)
        for name,value in stats.items():
            if name=="texture_bound":
                counts["source_saved_bound_texture_entries"]+=value
                counts["source_saved_null_texture_entries"]+=stats["texture"]-value
            else:
                counts["source_saved_"+name+"_property_entries"]+=value
        matched={p for p in owned if declared.get(p)==owned[p]}
        wrong={p for p in owned if p in declared and declared[p]!=owned[p]}
        extras=set(owned)-set(declared)
        unsaved=set(declared)-set(owned)
        counts["source_declared_property_saved_matches"]+=len(matched)
        counts["source_declared_property_unsaved_uses_default_possible"]+=len(unsaved)
        counts["source_saved_properties_not_declared"]+=len(extras)
        counts["source_saved_wrong_family_entries"]+=len(wrong)
        counts["source_materials_with_saved_wrong_family"]+=bool(wrong)
        counts["source_materials_with_saved_not_declared"]+=bool(extras)
        counts["source_materials_with_at_least_one_unsaved_declared"]+=bool(unsaved)
        counts["source_renderer_slots_with_saved_wrong_family"]+=weight*bool(wrong)
        counts["source_renderer_slots_with_saved_not_declared"]+=weight*bool(extras)
        counts["source_renderer_slots_with_at_least_one_unsaved_declared"]+=weight*bool(unsaved)
        counts["source_Materials_with_all_declared_properties_explicitly_saved"]+=not bool(unsaved)
        counts["source_Materials_with_no_declared_props_saved"]+=not bool(matched)
        counts["source_Materials_with_any_declared_texture_bound"]+=any(
            declared.get(name)=="texture" for name in bound_texture_names
        )
    # Real source Shader properties may be absent from Material and use defaults:
    # this is a structural census, NOT a runtime binding or renderer failure.
    return {
        "schema_version":1,
        "status":STATUS,
        "source":"SHA_pinned_6scenes_4owners_original_921_slot_Shader48",
        "counts":{k:int(counts[k]) for k in COUNTERS},
        "m_PropInfo_vs_Material_saved_fields_checked":True,
        "source_Shader_fallback_defaults_or_keyword_variant_evaluated":False,
        "same_export_or_android_Material_shader_program_binding_verified":False,
        "unity_Adreno_pixel_color_fixed_or_verified":False,
        "original_private_names_values_pathIDs_programs_published":False,
        "source_game_assets_modified":False,
    }


def private_scene_material_weights(original:Path):
    import UnityPy
    root=original/"Raft_Data"
    seen=Counter()
    for scene,pin in prior.prior.original.SCENE_PINS.items():
        path=root/scene
        prior.prior.original.verify_source(path,pin)
        f=UnityPy.load(str(path)).file
        externals=[r.path for r in f.externals]
        identity={obj.path_id:obj.type.name for obj in f.objects.values()}
        for obj in f.objects.values():
            if obj.type.name not in RENDERER_CLASSES:
                continue
            tree=obj.read_typetree(check_read=False)
            if not isinstance(tree,dict) or type(tree.get("m_Materials")) is not list:
                raise ValueError("invalid_original_scene_Renderer_material_slots")
            for ptr in tree["m_Materials"]:
                state,fid,pid=pointer_shape(ptr,identity,len(externals))
                if state=="null_material_slot":
                    continue
                if state!="external_target_unverified":
                    raise ValueError("unsupported_original_scene_Material_reference")
                name=PurePosixPath(externals[fid-1].replace("\\","/")).name
                if name not in prior.prior.original.MATERIAL_OWNERS:
                    raise ValueError("unproven_original_Material_owner")
                seen[(name,pid)]+=1
    if sum(seen.values())!=prior.prior.original.SCENE_NONNULL_SLOTS:
        raise ValueError("original_1635_renderer_Material_slot_baseline_changed")
    return seen


def probe(original:Path,manifest:Path):
    import UnityPy
    profile={}
    source=prior.prior.original.load_original(
        original,manifest,private_slot_counts=profile)
    owner,shader_id=prior.prior.feasibility.selected_high_use(profile,source)
    original_path=original/"Raft_Data"/owner
    if original_path.is_symlink() or prior.prior.fingerprint(original_path)!=prior.prior.SHADER_OWNERS[owner]:
        raise ValueError("original_highest_use_Shader_owner_SHA_changed")
    objects=[o for o in UnityPy.load(str(original_path)).file.objects.values()
             if o.path_id==shader_id]
    if len(objects)!=1 or objects[0].type.name!="Shader":
        raise ValueError("missing_original_highest_use_Shader48")
    parsed=objects[0].read_typetree().get("m_ParsedForm")
    declarations,_=declared_property_families(parsed)
    weights=private_scene_material_weights(original)
    matched, selected_weights={},{}
    for material_owner in prior.prior.original.MATERIAL_OWNERS:
        path=original/"Raft_Data"/material_owner
        if path.is_symlink() or prior.prior.fingerprint(path)!=prior.prior.SHADER_OWNERS[material_owner]:
            raise ValueError("original_Material_owner_SHA_changed")
        f=UnityPy.load(str(path)).file
        ext=[x.path for x in f.externals]
        for o in f.objects.values():
            if o.type.name!="Material":
                continue
            key=(material_owner,o.path_id)
            if key not in weights:
                continue
            tree=o.read_typetree()
            ptr=tree.get("m_Shader")
            if not isinstance(ptr,dict):
                raise ValueError("missing_original_Material_Shader_pointer")
            resolved=resolve_pointer(material_owner,ext,ptr)
            if resolved != (owner,shader_id):
                continue
            saved=tree.get("m_SavedProperties")
            if type(saved) is not dict:
                raise ValueError("missing_original_Material_SavedProperties")
            if key in matched:
                raise ValueError("duplicate_original_Material_in_same_owner")
            matched[key]=saved
            selected_weights[key]=weights[key]
    if sum(selected_weights.values())!=EXPECTED_SCENE_MATERIAL_SLOTS:
        raise ValueError("source_shader921_renderer_weighted_Materials_not_complete")
    result=classify_private_921_materials(declarations,matched,selected_weights)
    result.update({
        "source_original_six_scenes_SHA_verified":6,
        "source_original_owners_SHA_verified":4,
        "original_referenced_renderer_Material_slots":prior.prior.original.SCENE_MATERIAL_SLOTS,
        "original_distinct_typed_Shader48_from_source":source["original_distinct_typed_Shader48_targets"],
        "original_renderer_Material_slot_count_to_selected_Shader48":EXPECTED_SCENE_MATERIAL_SLOTS,
    })
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for n in ("original","manifest","out"):
        p.add_argument("--"+n,type=Path,required=True)
    a=p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()):
        raise ValueError("unsafe_original_Shader_Material_contract_output_path")
    try:
        result=probe(a.original,a.manifest)
    except Exception as error:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "exception_type":type(error).__name__,
                "unity_Adreno_pixel_color_fixed_or_verified":False,
                "original_private_names_values_pathIDs_programs_published":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("T3_ORIGINAL_921_SHADER_MATERIAL_PROPERTIES "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
