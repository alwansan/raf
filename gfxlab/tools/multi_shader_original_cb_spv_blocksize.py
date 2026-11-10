#!/usr/bin/env python3
"""GFX-MULTI-050 — original Shader48 DXBC CB vec4 declaration size to SPIR-V UBO.

Compare original SHDR dcl_constant_buffer b# vector counts *privately* against
vkd3d-translated Vulkan1.1 SPIR-V 'ubos' reflected block_size byte counts.
Matching total CB size does NOT prove any original Material/Shader property
name, individual constant-buffer member offset or GPU pixel parity.
No register numbers, buffer byte sizes, original shader binaries, property
names, source identifiers or reflection strings leave the ephemeral runner.
"""
from __future__ import annotations
import argparse
import json
import re
import tempfile
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_vkd3d_symbolic_register_map import private_register_from_name
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

MAX_UBO_ROWS=1024
MAX_CB_VECTORS=65535
MAX_BLOCK_BYTES=16*MAX_CB_VECTORS
CB_NAME_WITH_COUNT=re.compile(r"^cb([0-9]+)_([0-9]+)$")

def cb_size_evidence(original_cb_vectors,reflected_ubos):
    """Only fixed aggregate counts; never serialize private b-register keys."""
    if not isinstance(original_cb_vectors,dict) or not isinstance(reflected_ubos,list):
        raise ValueError("GFX050_CB_EVIDENCE_WRONG_INPUT")
    if len(original_cb_vectors)>MAX_UBO_ROWS or len(reflected_ubos)>MAX_UBO_ROWS:
        raise ValueError("GFX050_CB_ROW_COUNT_UNBOUNDED")
    if any(type(k) is not int or not 0<=k<=65535 or type(n) is not int
           or not 0<n<=MAX_CB_VECTORS for k,n in original_cb_vectors.items()):
        raise ValueError("GFX050_ORIGINAL_DCL_CB_VECTORS_INVALID")
    counts=Counter({
        "source_original_dxbc_constant_buffer_declarations":len(original_cb_vectors),
        "translated_spirv_reflected_ubo_entries":len(reflected_ubos),
        "reflected_ubos_with_exact_original_b_register_symbol":0,
        "reflected_ubos_with_generated_name_vector_count":0,
        "generated_name_vec4_counts_agree_with_original_dcl":0,
        "reflected_ubos_with_explicit_block_size":0,
        "source_dcl_vec4_times_16_equals_translated_spirv_block_size":0,
        "source_dcl_vec4_times_16_differs_from_translated_spirv_block_size":0,
        "ubo_reflections_missing_block_size":0,
        "invalid_or_duplicate_reflected_cb_binding":0,
        "source_cb_registers_missing_from_translation":0,
        "translated_cb_register_outside_original_source":0,
        "reflected_name_missing_source_b_register":0,
        "generated_name_vector_count_mismatch":0,
        "source_constant_buffer_member_byte_offset_mapping_proven":0,
    })
    mapped=set()
    bindings=set()
    for row in reflected_ubos:
        if not isinstance(row,dict):
            raise ValueError("GFX050_UBO_REFLECTION_ROW_NOT_OBJECT")
        binding=row.get("binding")
        descriptor_set=row.get("set",0)
        if type(binding) is not int or type(descriptor_set) is not int or binding<0 or descriptor_set<0:
            counts["invalid_or_duplicate_reflected_cb_binding"]+=1
        elif (descriptor_set,binding) in bindings:
            counts["invalid_or_duplicate_reflected_cb_binding"]+=1
        else:
            bindings.add((descriptor_set,binding))
        name=row.get("name")
        source_slot=private_register_from_name("constant_buffer",name)
        if source_slot is None:
            counts["reflected_name_missing_source_b_register"]+=1
            continue
        if source_slot not in original_cb_vectors:
            counts["translated_cb_register_outside_original_source"]+=1
            continue
        if source_slot in mapped:
            counts["invalid_or_duplicate_reflected_cb_binding"]+=1
            continue
        mapped.add(source_slot)
        counts["reflected_ubos_with_exact_original_b_register_symbol"]+=1
        suffix=CB_NAME_WITH_COUNT.fullmatch(name) if isinstance(name,str) else None
        if suffix:
            counts["reflected_ubos_with_generated_name_vector_count"]+=1
            if int(suffix.group(2))==original_cb_vectors[source_slot]:
                counts["generated_name_vec4_counts_agree_with_original_dcl"]+=1
            else:
                counts["generated_name_vector_count_mismatch"]+=1
        reflected_size=row.get("block_size")
        if type(reflected_size) is not int or not 0<reflected_size<=MAX_BLOCK_BYTES:
            counts["ubo_reflections_missing_block_size"]+=1
            continue
        counts["reflected_ubos_with_explicit_block_size"]+=1
        if original_cb_vectors[source_slot]*16==reflected_size:
            counts["source_dcl_vec4_times_16_equals_translated_spirv_block_size"]+=1
        else:
            counts["source_dcl_vec4_times_16_differs_from_translated_spirv_block_size"]+=1
    counts["source_cb_registers_missing_from_translation"]=len(set(original_cb_vectors)-mapped)
    all_matched=(bool(original_cb_vectors)
        and len(mapped)==len(original_cb_vectors)==len(reflected_ubos)
        and counts["source_dcl_vec4_times_16_equals_translated_spirv_block_size"]==len(original_cb_vectors)
        and counts["invalid_or_duplicate_reflected_cb_binding"]==0
        and counts["generated_name_vector_count_mismatch"]==0
        and counts["translated_cb_register_outside_original_source"]==0
        and counts["ubo_reflections_missing_block_size"]==0)
    return {
        **dict(counts),
        "all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes":bool(all_matched),
        "equal_byte_size_proves_member_layout_or_Material_property_semantics":False,
        "original_b_register_indices_or_CB_byte_sizes_exported":False,
    }

def numeric_cb_coordinate_candidate(original_cb_vectors,reflected_ubos):
    """Provisional same-numeric-binding CB size check, NOT source-slot identity.

    Previous GFX018 found that source b# numbers and translated UBO bindings
    can coincide; GFX019 explicitly could not authenticate original CB names.
    Therefore only descriptor_set==0 + binding==original b# is a candidate.
    Never set a semantic resource mapping flag on this evidence.
    """
    if not isinstance(original_cb_vectors,dict) or not isinstance(reflected_ubos,list):
        raise ValueError("GFX050_NUMERIC_CB_WRONG_INPUT")
    if len(original_cb_vectors)>MAX_UBO_ROWS or len(reflected_ubos)>MAX_UBO_ROWS:
        raise ValueError("GFX050_NUMERIC_CB_UNBOUNDED")
    if any(type(k) is not int or not 0<=k<=65535 or type(v) is not int or
           not 0<v<=MAX_CB_VECTORS for k,v in original_cb_vectors.items()):
        raise ValueError("GFX050_NUMERIC_CB_SOURCE_INVALID")
    matched=set();seen=set()
    count=Counter({
        "numeric_b_binding_candidate_matches":0,
        "numeric_b_binding_candidate_same_byte_sizes":0,
        "numeric_b_binding_candidate_different_byte_sizes":0,
        "numeric_b_binding_candidate_missing_block_size":0,
        "nonzero_descriptor_set_excluded_from_numeric_identity_candidate":0,
        "reflected_numeric_binding_outside_source_slots":0,
        "duplicate_or_invalid_reflected_descriptor_coordinate":0,
        "source_cb_slots_without_numeric_candidate":0,
    })
    for row in reflected_ubos:
        if not isinstance(row,dict):
            raise ValueError("GFX050_NUMERIC_CB_BAD_REFLECTED_ROW")
        b=row.get("binding");descriptor_set=row.get("set",0)
        if type(b) is not int or type(descriptor_set) is not int or b<0 or descriptor_set<0:
            count["duplicate_or_invalid_reflected_descriptor_coordinate"]+=1
            continue
        if (descriptor_set,b) in seen:
            count["duplicate_or_invalid_reflected_descriptor_coordinate"]+=1
            continue
        seen.add((descriptor_set,b))
        if descriptor_set!=0:
            count["nonzero_descriptor_set_excluded_from_numeric_identity_candidate"]+=1
            continue
        if b not in original_cb_vectors:
            count["reflected_numeric_binding_outside_source_slots"]+=1
            continue
        matched.add(b)
        count["numeric_b_binding_candidate_matches"]+=1
        size=row.get("block_size")
        if type(size) is not int or not 0<size<=MAX_BLOCK_BYTES:
            count["numeric_b_binding_candidate_missing_block_size"]+=1
        elif original_cb_vectors[b]*16==size:
            count["numeric_b_binding_candidate_same_byte_sizes"]+=1
        else:
            count["numeric_b_binding_candidate_different_byte_sizes"]+=1
    count["source_cb_slots_without_numeric_candidate"]=len(set(original_cb_vectors)-matched)
    candidate_complete=(
        bool(original_cb_vectors)
        and len(matched)==len(original_cb_vectors)==len(reflected_ubos)
        and count["numeric_b_binding_candidate_same_byte_sizes"]==len(matched)
        and not any(count[k] for k in (
            "numeric_b_binding_candidate_different_byte_sizes",
            "numeric_b_binding_candidate_missing_block_size",
            "nonzero_descriptor_set_excluded_from_numeric_identity_candidate",
            "reflected_numeric_binding_outside_source_slots",
            "duplicate_or_invalid_reflected_descriptor_coordinate")))
    return {
        **dict(count),
        "all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only":bool(candidate_complete),
        "numeric_descriptor_equality_proves_original_CB_identity":False,
        "numeric_descriptor_equality_proves_original_CB_member_offsets":False,
        "private_register_numbers_or_UBO_sizes_exported":False,
    }

def audit(stage):
    source_programs,passes=source_pair(stage)
    if len(passes)!=7 or any(not p["pairs"] for p in passes):
        raise ValueError("GFX050_ORIGINAL_SOURCE_PASS_TOPOLOGY_DRIFT")
    totals=Counter()
    perpass=[]
    for passrow in passes:
        v,f=passrow["pairs"][0]
        originals={"vertex":code_from_ref(v,source_programs,"Vertex"),
                   "fragment":code_from_ref(f,source_programs,"Pixel")}
        source_sizes={
            kind:private_source_slots(source_shader_chunk(buf))[1]
            for kind,buf in originals.items()
        }
        stage_summary={}
        with tempfile.TemporaryDirectory(prefix="gfxlab-050-private-") as temp:
            folder=Path(temp)
            validated=translate_pair(originals["vertex"],originals["fragment"],folder)
            for kind in ("vertex","fragment"):
                if not validated[kind]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX050_ORIGINAL_SOURCE_SPIRV_VALIDATION_FAILED")
                ok,data=run_quiet(["spirv-cross",str(folder/(kind+".spv")),"--reflect"])
                if not ok:raise ValueError("GFX050_ORIGINAL_SOURCE_SPV_REFLECTION_FAILED")
                try:reflect=json.loads(data.decode("utf-8","strict"))
                except (UnicodeDecodeError,ValueError):
                    raise ValueError("GFX050_ORIGINAL_PRIVATE_REFLECTION_FORMAT") from None
                if not isinstance(reflect,dict):
                    raise ValueError("GFX050_REFLECTION_NOT_OBJECT")
                c=cb_size_evidence(source_sizes[kind],reflect.get("ubos",[]))
                numeric=numeric_cb_coordinate_candidate(source_sizes[kind],reflect.get("ubos",[]))
                c["numeric_binding_candidate_evidence"]=numeric
                stage_summary[kind]=c
                totals["numeric_candidate_source_b_to_spv_ubo_matched"]+=numeric["numeric_b_binding_candidate_matches"]
                totals["numeric_candidate_equal_block_byte_sizes"]+=numeric["numeric_b_binding_candidate_same_byte_sizes"]
                totals["numeric_candidate_different_block_byte_sizes"]+=numeric["numeric_b_binding_candidate_different_byte_sizes"]
                totals["numeric_candidate_missing_UBO_block_byte_sizes"]+=numeric["numeric_b_binding_candidate_missing_block_size"]
                totals["stages_with_all_numeric_coordinate_CB_bytes_candidate_equal"]+=int(
                    numeric["all_original_b_numbers_match_spirv_ubo_numeric_binding_and_block_byte_size_as_candidate_only"])
                totals["total_source_dxbc_constant_buffer_declarations"]+=c["source_original_dxbc_constant_buffer_declarations"]
                totals["total_translated_spirv_reflected_ubos"]+=c["translated_spirv_reflected_ubo_entries"]
                totals["source_dcl_to_translated_ubo_exact_block_size_matches"]+=c["source_dcl_vec4_times_16_equals_translated_spirv_block_size"]
                totals["source_dcl_to_translated_ubo_block_size_mismatches"]+=c["source_dcl_vec4_times_16_differs_from_translated_spirv_block_size"]
                totals["source_cb_registers_not_found_in_spirv_reflection"]+=c["source_cb_registers_missing_from_translation"]
                totals["spirv_ubo_missing_explicit_block_size"]+=c["ubo_reflections_missing_block_size"]
                totals["stages_with_all_CB_block_byte_sizes_matched"]+=int(
                    c["all_original_CB_declaration_vector_lengths_equal_translated_SPIRV_UBO_block_bytes"])
                totals["source_stage_comparisons"]+=1
        perpass.append({"subshader_public_position":passrow["subshader"],
                        "pass_public_position":passrow["pass"],
                        "original_source_CB_block_size_evidence":stage_summary})
    if totals["source_stage_comparisons"]!=14 or len(perpass)!=7:
        raise ValueError("GFX050_ORIGINAL_SOURCE_STAGE_ACCOUNTING_FAILURE")
    return {
        "experiment":"GFX-MULTI-050",
        "original_zip2_sha":ZIP2_SHA,
        "evidence_level":"ORIGINAL_SOURCE_DXBC_DCL_CB_VECTOR_LENGTH_TO_VKD3D_SPIRV_REFLECTION_BLOCK_SIZE_CPU_ONLY",
        "original_shader48_source_passes":7,
        "original_exact_keyword_tier_representative_pairs":7,
        "original_source_stage_programs":14,
        "source_CB_to_translated_UBO_safe_aggregate":dict(totals),
        "per_pass":perpass,
        "all_14_stages_CB_byte_size_equality_proven":totals["stages_with_all_CB_block_byte_sizes_matched"]==14,
        "all_14_stages_numeric_binding_candidate_block_size_matched":totals["stages_with_all_numeric_coordinate_CB_bytes_candidate_equal"]==14,
        "numeric_binding_candidate_is_original_CB_semantic_identity":False,
        "all_524_variants_covered":False,
        "source_Material_Shader_property_to_original_CB_register_mapping_proven":False,
        "original_constantbuffer_individual_member_byte_offsets_proven":False,
        "original_shader48_Unity_Android_GPU_runtime_proven":False,
        "original_PC_vs_Adreno_pixels_proven":False,
        "originalShaderRestored":False,
        "source_private_shader_code_registers_names_or_CB_sizes_exported":False,
        "phase_closed":False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    out=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("GFX050_SAFE_ORIGINAL_CB_DECLARATION_VS_SPIRV_BLOCK_SIZE_COUNTS "+json.dumps(out,sort_keys=True))
if __name__=="__main__":
    main()
