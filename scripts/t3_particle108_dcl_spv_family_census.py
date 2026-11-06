#!/usr/bin/env python3
"""Original Particle108 DXBC declaration-family vs Vulkan SPIR-V stage census.

Exact SHA original per-stage VS/PS keyword selection is mandatory. This does
NOT establish per-register descriptor provenance, ShaderLab compatibility,
runtime pixel/color fidelity or whether source-declared resources are used.
Only anonymous aggregate counts leave ephemeral runner-private processing.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from scripts import t3_particle108_original_dxbc_operand_bindings as dx
from scripts import t3_particle108_resource_binding_parity as rb
from scripts import t3_original_particle108_spirv_translation as origin
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import reflection
from scripts.t3_particle108_source_propstate import serialize_properties

STATUS="T3_SHA_ORIGINAL_PARTICLE108_DCL_SPV_STAGE_FAMILY_CENSUS"
FAMILIES=("cbuffer","srv","sampler","uav")
SPV_CATEGORIES=rb.CATEGORIES
MAX_RESOURCES=128

def _stage_evidence(layout,reflected):
    """Decode private source declarations + reflected categories, no raw IDs."""
    if type(layout) is not tuple or len(layout)>MAX_RESOURCES:
        raise ValueError("INVALID_PRIVATE_STAGE_DCL_SCOPE")
    records_by_family=Counter()
    seen=set()
    for record in layout:
        if (type(record) is not tuple or len(record)!=3
            or record[0] not in FAMILIES or type(record[1]) is not int
            or type(record[2]) is not tuple or not 1<=len(record[2])<=2
            or any(type(value) is not int or not 0<=value<=4095
                   for value in record[2])):
            raise ValueError("INVALID_PRIVATE_STAGE_DCL_RECORD")
        family,opcode,indexes=record
        primary=(family,indexes[0])
        if primary in seen:
            raise ValueError("DUPLICATE_PRIVATE_PRIMARY_REGISTER")
        seen.add(primary)
        records_by_family[family]+=1
    slots=rb.canonical_resources(reflected)
    n={key:len(slots[key]) for key in SPV_CATEGORIES}
    source_srv=records_by_family["srv"]>0
    source_sampler=records_by_family["sampler"]>0
    spv_image_or_combined=n["textures"]+n["separate_images"]+n["images"]>0
    spv_sampler_or_combined=n["textures"]+n["separate_samplers"]>0
    # Compare source DCL declarations to translated SPIR-V reflection
    # *within this exact keyword/stage*, rather than globally across stages.
    # This catches offsetting drift even when 24/10/10 totals match.
    # Combined sampler images participate in both SRV and sampler counts.
    family_counts={
        "cbuffer":(records_by_family["cbuffer"],n["ubos"]),
        "srv":(records_by_family["srv"],n["textures"]+n["separate_images"]),
        "sampler":(records_by_family["sampler"],n["textures"]+n["separate_samplers"]),
        "uav":(records_by_family["uav"],n["images"]+n["ssbos"]),
    }
    cardinality={
        "stage_"+family+"_cardinality_equal":int(src==spv)
        for family,(src,spv) in family_counts.items()
    }
    cardinality.update({
        "stage_"+family+"_cardinality_mismatch":int(src!=spv)
        for family,(src,spv) in family_counts.items()
    })
    cardinality.update({
        "stage_"+family+"_absolute_descriptor_count_delta":abs(src-spv)
        for family,(src,spv) in family_counts.items()
    })
    cardinality["stage_all_four_resource_family_cardinalities_equal"]=int(
        all(src==spv for src,spv in family_counts.values()))
    return {
        **cardinality,
        "source_decl_cbuffer":records_by_family["cbuffer"],
        "source_decl_srv":records_by_family["srv"],
        "source_decl_sampler":records_by_family["sampler"],
        "source_decl_uav":records_by_family["uav"],
        "spv_reflected_ubos":n["ubos"],
        "spv_reflected_ssbos":n["ssbos"],
        "spv_reflected_textures":n["textures"],
        "spv_reflected_separate_images":n["separate_images"],
        "spv_reflected_separate_samplers":n["separate_samplers"],
        "spv_reflected_images":n["images"],
        # Signals only. A DCL can be optimized away or lowered differently.
        "dcl_cb_but_no_spv_ubo":int(records_by_family["cbuffer"]>0 and n["ubos"]==0),
        "dcl_srv_but_no_spv_image_category":int(source_srv and not spv_image_or_combined),
        "dcl_sampler_but_no_spv_sampler_category":int(source_sampler and not spv_sampler_or_combined),
        "dcl_uav_but_no_spv_storage_category":int(
            records_by_family["uav"]>0 and n["images"]+n["ssbos"]==0),
        "spv_ubo_without_dcl_cb":int(n["ubos"]>0 and records_by_family["cbuffer"]==0),
    }

def classify(pairs,tempdir,*,translator=translate,reflector=reflection):
    if (type(pairs) is not list or len(pairs)!=4
        or any(type(pair) is not tuple or len(pair)!=2
               or any(type(blob) is not bytes or not 0<len(blob)<=origin.MAX_PRIVATE_STAGE_BYTES
                      for blob in pair)
               for pair in pairs)
        or not isinstance(tempdir,Path) or not tempdir.is_dir()
        or tempdir.is_symlink()):
        raise ValueError("INVALID_PRIVATE_FOUR_PAIR_SCOPE")
    c=Counter()
    for pair_idx,(vertex,fragment) in enumerate(pairs):
        for stage,blob in ((1,vertex),(0,fragment)):
            # Per-variant provenance stays private; never copy stage IDs,
            # register values, SPV set/binding values into report.
            layout=dx._private_stage_layout(blob,stage)
            folder=tempdir/("variant-%d-stage-%d"%(pair_idx,stage))
            folder.mkdir(exist_ok=False)
            result=translator(blob,stage,folder)
            if (type(result) is not dict or result.get("stage")!=stage
                or result.get("vulkan11_valid") is not True):
                raise ValueError("PRIVATE_STAGE_VULKAN_TRANSLATION_NOT_VERIFIED")
            reflected=reflector(folder/"original.spv")
            evidence=_stage_evidence(layout,reflected)
            c.update(evidence)
            c["exact_original_keyword_stage_programs_compared"]+=1
            if stage==1:
                c["vertex_stages_compared"]+=1
            else:
                c["fragment_stages_compared"]+=1
        c["exact_original_keyword_vs_fs_pairs_compared"]+=1
    if (c["exact_original_keyword_stage_programs_compared"]!=8
        or c["exact_original_keyword_vs_fs_pairs_compared"]!=4):
        raise ValueError("PRIVATE_STAGE_CENSUS_INCOMPLETE")
    return {
        "schema_version":1,"status":STATUS,
        "counts":dict(sorted(c.items())),
        "original_DCL_registers_or_Vulkan_set_binding_values_published":False,
        "original_to_SPIRV_descriptor_register_provenance_proven":False,
        "source_declared_resource_can_be_unused_or_optimized":True,
        "per_family_presence_is_not_shader_pixel_equivalence":True,
        "per_stage_family_count_equality_is_not_register_identity":True,
        "Unity_ShaderLab_or_device_pixels_verified":False,
    }

def probe(root,manifest):
    for tool in origin.TOOLS:
        if shutil.which(tool) is None:
            raise ValueError("REQUIRED_VULKAN_TRANSLATOR_NOT_AVAILABLE")
    selected={}
    result=rb.identity.source.load_original(root,manifest,
                                             private_particle_slot_counts=selected)
    owner,pid=rb.identity.select(selected,result)
    owner_path=root/"Raft_Data"/owner
    if (any(p.is_symlink() for p in (owner_path,*owner_path.parents))
        or fingerprint(owner_path)!=SHADER_OWNERS[owner]):
        raise ValueError("AUTHENTIC_ORIGINAL_SOURCE_SHA_CHANGED")
    import UnityPy
    objects=[o for o in UnityPy.load(str(owner_path)).file.objects.values()
             if o.path_id==pid]
    if len(objects)!=1 or objects[0].type.name!="Shader":
        raise ValueError("AUTHENTIC_ORIGINAL_SHADER_SELECTION_CHANGED")
    tree=objects[0].read_typetree()
    _,shape=serialize_properties(tree["m_ParsedForm"])
    if shape["original_authored_property_count"]!=13 or shape[
        "original_authored_texture_property_count"]!=2:
        raise ValueError("AUTHENTIC_SOURCE_AUTHORING_SCHEMA_CHANGED")
    players=[records(parts) for platform,parts in decoded_platforms(tree)
             if platform==4]
    if len(players)!=1:
        raise ValueError("AUTHENTIC_ORIGINAL_PLAYER_PLATFORM_UNAVAILABLE")
    baseline=rb.identity.inspect(tree["m_ParsedForm"],players[0])
    if (baseline.get("status")!=rb.identity.STATUS
        or baseline.get("matched_vertex_fragment_permutation_pairs")!=4
        or baseline.get("original_D3D11_program_table_records")!=16):
        raise ValueError("AUTHENTIC_ORIGINAL_FOUR_KEYWORD_STAGE_SCOPE_CHANGED")
    pairs=origin.exact_four_pairs(tree["m_ParsedForm"],players[0])
    with tempfile.TemporaryDirectory(prefix="t3-private-dcl-vulkan-family-") as tmp:
        report=classify(pairs,Path(tmp))
    report["source_original_six_scenes_SHA_authenticated"]=True
    report["source_original_four_owner_SHA_authenticated"]=True
    report["original_selected_particle_renderer_material_use_slots"]=108
    return report

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for field in ("original","manifest","out"):
        parser.add_argument("--"+field,required=True,type=Path)
    a=parser.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("UNSAFE_PRIVATE_CENSUS_DESTINATION")
    try:
        result=probe(a.original,a.manifest)
    except Exception as exc:
        # Never render private exception message; a path, value or source
        # identifier could leak through an unexpected lower-level exception.
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "original_DCL_registers_or_Vulkan_set_binding_values_published":False,
                "original_to_SPIRV_descriptor_register_provenance_proven":False,
                "Unity_ShaderLab_or_device_pixels_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_PRIVATE_ORIGINAL_DCL_SPV_FAMILY_SAFE="+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
