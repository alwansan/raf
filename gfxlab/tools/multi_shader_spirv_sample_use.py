#!/usr/bin/env python3
"""GFX-MULTI-046: source-authenticated, translated SPIR-V sample-pair use sites.

The private DXBC Shader48 source->vkd3d->SPIR-V chain is immutable and validated.
Trace OpLoad/OpCopyObject -> OpSampledImage -> actual OpImageSample*/Gather.
Only strict direct paths count. Unknown paths are counted as unresolved.
It is NOT direct original DXBC sample opcode decoding, Shader48 Material property
mapping, source CB byte layout, Android execution or PC pixel parity. All
original t/s slot indices, SPIR-V IDs, names and shader bytes stay in CI runner.
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair, code_from_ref, translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_vkd3d_symbolic_register_map import private_register_from_name
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

MAX_DISASSEMBLY_BYTES=16*1024*1024
MAX_INSTRUCTIONS=300000
MAX_REFLECTED_RESOURCES=4096
ASSIGN=re.compile(r"^\s*(%[0-9]+)\s*=\s*(Op[A-Za-z0-9_]+)(?:\s+(.*?))?\s*$")
ID=re.compile(r"^%[0-9]+$")
SAMPLE_PREFIX=("OpImageSample", "OpImageSparseSample")
GATHER={"OpImageGather","OpImageDrefGather","OpImageSparseGather",
        "OpImageSparseDrefGather"}
FETCH={"OpImageFetch","OpImageSparseFetch","OpImageRead","OpImageSparseRead"}

def disassembled_opnames(dis):
    """Obtain private SPIR-V raw variable IDs by exact OpName; no names serialized."""
    if not isinstance(dis,(bytes,bytearray)) or len(dis)>MAX_DISASSEMBLY_BYTES:
        raise ValueError("GFX046_DISASSEMBLY_NAME_INPUT_INVALID")
    try:
        text=dis.decode("utf-8","strict")
    except UnicodeDecodeError:
        raise ValueError("GFX046_DISASSEMBLY_NAMES_NON_UTF8") from None
    labels={}
    for line in text.splitlines():
        match=re.fullmatch(r'\s*OpName\s+(%[0-9]+)\s+"([^"]{1,100})"\s*',line)
        if match:
            spvid,name=match.groups()
            if name in labels or spvid in labels.values():
                raise ValueError("GFX046_AMBIGUOUS_SPIRV_OPNAME")
            labels[name]=spvid
    return labels


def resource_variable_ids(source_slots, reflection, family, disassembly=None):
    """Cross-check DXBC source set, SPIRV-Cross names, and actual disassembled OpName.

    SPIRV-Cross --reflect builds may omit the numeric variable 'id' field;
    never treat descriptor 'binding' as that ID. Fall back only to an exact,
    unique SPIR-V OpName from the same validated private binary.
    """
    if family not in ("resource","sampler") or not isinstance(source_slots,set):
        raise ValueError("GFX046_BAD_SOURCE_FAMILY")
    if not isinstance(reflection,list) or len(reflection)>MAX_REFLECTED_RESOURCES:
        raise ValueError("GFX046_REFLECTION_LIST_UNBOUNDED")
    if any(type(s) is not int or not 0<=s<=65535 for s in source_slots):
        raise ValueError("GFX046_INVALID_SOURCE_SLOT")
    private_names=(disassembled_opnames(disassembly) if disassembly is not None else {})
    selected={};seen_slots=set()
    for record in reflection:
        if not isinstance(record,dict):
            raise ValueError("GFX046_REFLECTION_ROW_MALFORMED")
        name=record.get("name")
        symbol=private_register_from_name(family,name)
        if symbol is None or symbol not in source_slots:
            raise ValueError("GFX046_REFLECTION_SYMBOL_OUTSIDE_SOURCE")
        num=record.get("id")
        if num is not None and (type(num) is not int or num<=0):
            raise ValueError("GFX046_RESOURCE_VARIABLE_ID_MISSING")
        if num is None:
            key=private_names.get(name)
            if key is None:
                raise ValueError("GFX046_REFLECTED_NAME_NOT_IN_SPIRV_OPNAME")
        else:
            key="%"+str(num)
            if disassembly is not None and private_names.get(name)!=key:
                raise ValueError("GFX046_REFLECTED_ID_DISAGREES_WITH_SPIRV_OPNAME")
        if key in selected or symbol in seen_slots:
            raise ValueError("GFX046_DUPLICATE_REFLECTED_VARIABLE_OR_REGISTER")
        selected[key]=(family,symbol)
        seen_slots.add(symbol)
    if seen_slots!=source_slots:
        raise ValueError("GFX046_INCOMPLETE_AUTHENTIC_REGISTER_COVERAGE")
    return selected

def spv_sample_use(dis, image_ids, sampler_ids):
    """Strict source-private translated SPIR-V def-use; only safe counts returned.

    Handles immutable direct OpLoad, OpCopyObject and OpSampledImage. Dynamic
    pointer/access-chain, phi/select, combined descriptors remain UNKNOWN, not
    guessed. For SPIR-V copied intermediate sampled images, pair is propagated.
    """
    if (not isinstance(dis,(bytes,bytearray))
            or not 0<len(dis)<=MAX_DISASSEMBLY_BYTES
            or not isinstance(image_ids,dict) or not isinstance(sampler_ids,dict)
            or set(image_ids)&set(sampler_ids)):
        raise ValueError("GFX046_DIS_INPUT_INVALID")
    try:
        source=dis.decode("utf-8","strict")
    except UnicodeDecodeError:
        raise ValueError("GFX046_SPIRV_DISASSEMBLY_NON_UTF8") from None
    known={**image_ids,**sampler_ids}
    values={}
    sampled={}
    instructions=0
    constructed=0
    unresolved_constructions=0
    consumed_pairs=[]
    unknown_samples=0
    fetch=0
    total_sample=0
    variables=set()
    for line in source.splitlines():
        line=line.split(";",1)[0].strip()
        if not line:continue
        ins=ASSIGN.match(line)
        if ins:
            result,op,raw=ins.groups()
            args=(raw or "").split()
            if result in values or result in sampled:
                raise ValueError("GFX046_DUPLICATE_RESULT_ID")
            # The only variable origins we trust are directly reflected globals.
            if op=="OpVariable":
                variables.add(result)
            if op=="OpLoad" and len(args)>=2:
                pointer=args[1]
                if pointer in known:
                    values[result]=known[pointer]
            elif op=="OpCopyObject" and len(args)>=2:
                prev=args[1]
                if prev in values:
                    values[result]=values[prev]
                if prev in sampled:
                    sampled[result]=sampled[prev]
            elif op=="OpSampledImage":
                constructed+=1
                if len(args)>=3:
                    image=values.get(args[1])
                    sampler=values.get(args[2])
                    if image and sampler and image[0]=="resource" and sampler[0]=="sampler":
                        sampled[result]=(image[1],sampler[1])
                    else:
                        unresolved_constructions+=1
                else:
                    unresolved_constructions+=1
            if op.startswith(SAMPLE_PREFIX) or op in GATHER:
                total_sample+=1
                if len(args)>=2 and args[1] in sampled:
                    consumed_pairs.append(sampled[args[1]])
                else:
                    unknown_samples+=1
            elif op in FETCH:
                fetch+=1
        else:
            op=line.split(" ",1)[0]
            # Non-result instructions are not valid sampled-image operations.
            if op.startswith(SAMPLE_PREFIX) or op in GATHER:
                raise ValueError("GFX046_SAMPLE_WITHOUT_RESULT")
        if line.startswith("Op") or ins:
            instructions+=1
            if instructions>MAX_INSTRUCTIONS:
                raise ValueError("GFX046_SPIRV_INSTRUCTIONS_UNBOUNDED")
    if not set(known)<=variables:
        raise ValueError("GFX046_REFLECTED_ID_NOT_GLOBAL_VARIABLE")
    if (len(consumed_pairs)+unknown_samples!=total_sample
            or constructed < len(set(sampled.values()))):
        raise ValueError("GFX046_SAMPLE_ACCOUNTING_INVALID")
    # Only public aggregates. No pair tuple or SPIR-V register ID is emitted.
    return {
        "spirv_instructions_scanned":instructions,
        "reflected_original_source_resource_variables":len(image_ids),
        "reflected_original_source_sampler_variables":len(sampler_ids),
        "sampled_image_constructions":constructed,
        "sampled_image_constructions_unresolved":unresolved_constructions,
        "sample_or_gather_operations":total_sample,
        "sample_or_gather_with_strict_t_s_pair":len(consumed_pairs),
        "sample_or_gather_unresolved":unknown_samples,
        "distinct_source_t_s_pairs_observed_in_translated_samples":len(set(consumed_pairs)),
        "non_sampler_fetch_or_read_instructions":fetch,
        "translated_sample_pair_proven_for_every_sample_operation":total_sample>0 and unknown_samples==0,
        "unresolved_sample_operations_counted_not_assumed":True,
        "source_register_numbers_or_translated_spirv_ids_exported":False,
        "original_material_texenv_to_t_s_binding_verified":False,
        "original_dxbc_sample_use_site_parity_independent_from_translator_verified":False,
        "original_shader48_android_GPU_verified":False,
    }

def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7 or any(not p["pairs"] for p in passes):
        raise ValueError("GFX046_ORIGINAL_SEVEN_PASS_SOURCE_PAIR_DRIFT")
    perpass=[]
    totals=Counter()
    for p in passes:
        vmeta,fmeta=p["pairs"][0]
        original={
            "vertex":code_from_ref(vmeta,programs,"Vertex"),
            "fragment":code_from_ref(fmeta,programs,"Pixel")}
        private_slots={
            st:private_source_slots(source_shader_chunk(data))[0]
            for st,data in original.items()}
        with tempfile.TemporaryDirectory(prefix="gfxlab-multi046-shader-private-") as td:
            folder=Path(td)
            converted=translate_pair(original["vertex"],original["fragment"],folder)
            stage_counts={}
            for st in ("vertex","fragment"):
                if not converted[st]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX046_PRIVATE_VKD3D_STAGE_VALIDATION_FAILED")
                spv=folder/(st+".spv")
                ok,reflection_bytes=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:
                    raise ValueError("GFX046_SPIRV_CROSS_REFLECTION_FAILED")
                try:
                    reflect=json.loads(reflection_bytes.decode("utf-8"))
                except (UnicodeDecodeError,ValueError):
                    raise ValueError("GFX046_PRIVATE_REFLECTION_JSON_INVALID") from None
                if not isinstance(reflect,dict):
                    raise ValueError("GFX046_PRIVATE_REFLECTION_OBJECT_INVALID")
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:raise ValueError("GFX046_SPIRV_DISASSEMBLY_FAILED")
                resources=resource_variable_ids(private_slots[st]["resource"],
                          reflect.get("separate_images",[]),"resource",dis)
                samplers=resource_variable_ids(private_slots[st]["sampler"],
                          reflect.get("separate_samplers",[]),"sampler",dis)
                c=spv_sample_use(dis,resources,samplers)
                stage_counts[st]=c
                for key in ("sampled_image_constructions","sampled_image_constructions_unresolved",
                            "sample_or_gather_operations","sample_or_gather_with_strict_t_s_pair",
                            "sample_or_gather_unresolved","distinct_source_t_s_pairs_observed_in_translated_samples",
                            "non_sampler_fetch_or_read_instructions"):
                    totals[key]+=c[key]
        perpass.append({
            "subshader_public_position":p["subshader"],
            "pass_public_position":p["pass"],
            "representative_exact_keyword_and_tier_pair_only":True,
            "translated_source_stage_sample_use_counts":stage_counts})
    if len(perpass)!=7:
        raise ValueError("GFX046_SEVEN_PASS_ACCOUNTING_FAILURE")
    return {
        "experiment":"GFX-MULTI-046",
        "source_zip2_sha":ZIP2_SHA,
        "original_shader48_subshader_count":2,
        "original_shader48_pass_count":7,
        "authentic_matched_variant_pairs_selected":7,
        "authentic_stage_programs":14,
        "evidence_level":"ORIGINAL_SOURCE_AND_TRANSLATOR_SPIRV_CPU_ONLY",
        "translated_spirv_t_s_use_aggregate":dict(totals),
        "per_pass":perpass,
        "all_524_exact_source_pairs_evaluated":False,
        "original_shader_source_property_to_DXBC_t_s_register_binding_verified":False,
        "source_texture2d_to_actual_gpu_sample_semantics_verified":False,
        "original_constantbuffer_byte_offsets_verified":False,
        "shader48_original_android_GPU_runtime_verified":False,
        "originalShaderRestored":False,
        "pc_to_adreno_original_pixel_parity":False,
        "private_shader_bytes_registers_names_ids_or_pair_edges_exported":False,
        "phase_closed":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    report=audit(stage_originals(args.zip2,args.stage))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI046_SAFE_TRANSLATED_SAMPLER_USE " + json.dumps(report,sort_keys=True))

if __name__=="__main__":
    main()
