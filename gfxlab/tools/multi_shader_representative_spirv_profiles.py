#!/usr/bin/env python3
"""GFX-MULTI-049: all 58 original source sampling-profile representatives.

Strict source-private offline comparison only. Find one exact matched
Shader48 VS/FS keyword+tier pair per *global* DXBC t/s sample-use multiset
profile. Convert each selected genuine DXBC stage via vkd3d into Vulkan 1.1
SPIR-V, reflect + disassemble, and compare the *actual* original SHDR
sample texture/sampler opcode-use multiset against the compiler-lowered graph.
Only count summaries leave the private CI runner. A profile does NOT imply
full shader semantic equivalence or true Android GPU execution.
"""
from __future__ import annotations
import argparse
import json
import tempfile
import re
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair, code_from_ref, translate_pair
from gfxlab.tools.multi_shader_all_variant_dxbc_sample_census import (
    private_signature, MAX_CACHED_PROGRAMS, MAX_PAIR_ROWS
)
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import (
    original_sample_pairs, stage_compare
)
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

EXPECTED_PAIRS=524
EXPECTED_SIGNATURE_CLASSES=58
MAX_SELECTED_PAIRS=100
EXPECTED_PASSES=7

# Fixed public diagnostic codes only. Never export arbitrary exception text, DXBC
# tokens, private resource names, register numbers, or original SPIR-V IDs.
PUBLIC_STAGE_ERROR_CODES=frozenset((
    "GFX046_REFLECTION_SYMBOL_OUTSIDE_SOURCE",
    "GFX046_INCOMPLETE_AUTHENTIC_REGISTER_COVERAGE",
    "GFX046_REFLECTED_NAME_NOT_IN_SPIRV_OPNAME",
    "GFX046_AMBIGUOUS_SPIRV_OPNAME",
    "GFX046_DUPLICATE_REFLECTED_VARIABLE_OR_REGISTER",
    "GFX046_REFLECTED_ID_DISAGREES_WITH_SPIRV_OPNAME",
    "GFX046_REFLECTED_ID_NOT_GLOBAL_VARIABLE",
    "GFX046_SAMPLE_ACCOUNTING_INVALID",
    "GFX046_DUPLICATE_RESULT_ID",
    "GFX046_SAMPLE_WITHOUT_RESULT",
    "GFX046_RESOURCE_VARIABLE_ID_MISSING",
    "GFX046_INVALID_SOURCE_SLOT",
    "GFX046_BAD_SOURCE_FAMILY",
    "GFX047_SPIRV_DUPLICATE_RESULT_ID",
    "GFX047_TRANSLATED_COUNTER_RECONCILIATION_FAILED",
    "GFX047_SAMPLE_RESOURCE_OR_SAMPLER_WRONG_TYPE",
    "GFX047_UNDECLARED_TEXTURE_SOURCE_REGISTER",
    "GFX047_UNDECLARED_SAMPLER_SOURCE_REGISTER",
    "GFX047_SAMPLE_OPERAND_TERMINATION_MISMATCH",
))
def safe_failure_code(exc):
    """Recognize only preapproved literal parser labels, never private values."""
    if type(exc) is ValueError and len(exc.args)==1:
        label=exc.args[0]
        if isinstance(label,str) and label in PUBLIC_STAGE_ERROR_CODES:
            return label
    return "UNCLASSIFIED_FAIL_CLOSED"

_UNIFORM_CONSTANT_VAR=re.compile(
    r"^\s*(%[0-9]+)\s*=\s*OpVariable\s+%[0-9]+\s+UniformConstant(?:\s|$)"
)
_OPNAME=re.compile(r'^\s*OpName\s+(%[0-9]+)\s+"([^"]{1,100})"\s*def select_private_sample_profiles(passes, inspect_stage, limit=MAX_SELECTED_PAIRS):
    """Select one exact VS/FS source pair per private global sample signature.

    Accept a source-free synthetic inspector for tests. Never serialize the
    returned original variant rows, private signatures, or stage identities.
    """
    if (not isinstance(passes,list) or len(passes)!=EXPECTED_PASSES
        or type(limit) is not int or not 1<=limit<=MAX_SELECTED_PAIRS):
        raise ValueError("GFX049_INVALID_ORIGINAL_PASS_INPUT")
    seen=set()
    selections=[]
    pass_summary=[]
    scanned=0
    for passrecord in passes:
        pairs=passrecord.get("pairs") if isinstance(passrecord,dict) else None
        if not isinstance(pairs,list) or not 1<=len(pairs)<=MAX_PAIR_ROWS:
            raise ValueError("GFX049_INVALID_ORIGINAL_PAIR_BUCKET")
        new_classes=0
        for pair in pairs:
            if not isinstance(pair,(list,tuple)) or len(pair)!=2:
                raise ValueError("GFX049_INVALID_EXACT_PAIR")
            v,f=pair
            vinfo=inspect_stage(v,"Vertex")
            finfo=inspect_stage(f,"Pixel")
            if not isinstance(vinfo,dict) or not isinstance(finfo,dict):
                raise ValueError("GFX049_BAD_PRIVATE_SOURCE_INSPECTOR")
            signature=(private_signature(vinfo["pairs"]),private_signature(finfo["pairs"]))
            scanned+=1
            if signature not in seen:
                if len(selections)>=limit:
                    raise ValueError("GFX049_SOURCE_PROFILE_LIMIT_EXCEEDED")
                seen.add(signature)
                selections.append((passrecord,v,f,vinfo,finfo))
                new_classes+=1
        pass_summary.append({
            "subshader_public_position":passrecord.get("subshader"),
            "pass_public_position":passrecord.get("pass"),
            "exact_source_variant_pairs_examined":len(pairs),
            "new_global_sampling_profile_representatives_selected":new_classes,
        })
    if scanned!=EXPECTED_PAIRS:
        raise ValueError("GFX049_AUTHENTIC_524_PAIR_COUNT_DRIFT")
    return selections,pass_summary,scanned,len(seen)


def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=EXPECTED_PASSES:
        raise ValueError("GFX049_SHADER48_PASS_TOPOLOGY_DRIFT")
    cache={}
    def inspect_source(meta,kind):
        idx=meta.get("m_BlobIndex") if isinstance(meta,dict) else None
        gpu=meta.get("m_GpuProgramType") if isinstance(meta,dict) else None
        if type(idx) is not int or type(gpu) is not int or idx<0 or idx>=1656:
            raise ValueError("GFX049_ORIGINAL_STAGE_REF_INVALID")
        key=(kind,idx,gpu)
        if key not in cache:
            if len(cache)>=MAX_CACHED_PROGRAMS:
                raise ValueError("GFX049_SOURCE_STAGE_CACHE_UNBOUNDED")
            source=code_from_ref(meta,programs,kind)
            shdr=source_shader_chunk(source)
            slots,_=private_source_slots(shdr)
            pairs,counters=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            if counters["source_original_unresolved_dynamic_t_s"]!=0:
                raise ValueError("GFX049_UNRESOLVED_ORIGINAL_REGISTER_USE")
            cache[key]={"pairs":pairs,"sample_count":counters["source_sample_or_gather_operations"]}
        return cache[key]

    selected,pass_rows,scanned,classes=select_private_sample_profiles(passes,inspect_source)
    if scanned!=EXPECTED_PAIRS or classes!=EXPECTED_SIGNATURE_CLASSES or len(selected)!=classes:
        raise ValueError("GFX049_SOURCE_PROFILE_COUNT_DRIFT")
    totals=Counter({
        "original_exact_keyword_tier_pairs_scanned":scanned,
        "original_source_stage_programs_deduplicated_in_private_cache":len(cache),
        "selected_original_source_sampling_profiles":len(selected),
        "representative_pair_translations_attempted":0,
        "representative_pair_translations_validated":0,
        "representative_pair_exact_source_to_SPIRV_t_s_pair_parity":0,
        "representative_pairs_with_any_stage_failure":0,
        "failed_translation_or_spirv_validation_stages":0,
        "failed_spirv_reflection_or_disassembly_stages":0,
        "failed_strict_source_to_spirv_pair_comparison_stages":0,
        "mismatched_source_translated_t_s_multiset_stages":0,
        "source_t_s_sample_instructions_validated_in_equal_multisets":0,
        "translated_spirv_sample_instructions_validated_in_equal_multisets":0,
        "sampled_source_selected_stages":0,
        "source_zero_sample_selected_stages":0,
    })
    failure_categories=Counter()
    # Only bounded safe counts and public pass positions. Neither the selected
    # program index nor its private sampling signature is ever exported.
    for passrecord,vmeta,fmeta,vinfo,finfo in selected:
        totals["representative_pair_translations_attempted"]+=1
        pair_ok=True
        with tempfile.TemporaryDirectory(prefix="gfxlab049-private-") as temp:
            folder=Path(temp)
            originals={
                "vertex":code_from_ref(vmeta,programs,"Vertex"),
                "fragment":code_from_ref(fmeta,programs,"Pixel")
            }
            converted=translate_pair(originals["vertex"],originals["fragment"],folder)
            for kind in ("vertex","fragment"):
                if not converted[kind]["vulkan11_spirv_validation_success"]:
                    totals["failed_translation_or_spirv_validation_stages"]+=1
                    pair_ok=False
                    failure_categories["conversion_or_validation"]+=1
                    continue
                spv=folder/(kind+".spv")
                ok,refdata=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:
                    totals["failed_spirv_reflection_or_disassembly_stages"]+=1
                    pair_ok=False
                    failure_categories["reflection_tool"]+=1
                    continue
                try:
                    reflected=json.loads(refdata.decode("utf-8"))
                except (ValueError,UnicodeDecodeError):
                    reflected=None
                if not isinstance(reflected,dict):
                    totals["failed_spirv_reflection_or_disassembly_stages"]+=1
                    pair_ok=False
                    failure_categories["reflection_shape"]+=1
                    continue
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:
                    totals["failed_spirv_reflection_or_disassembly_stages"]+=1
                    pair_ok=False
                    failure_categories["disassembly_tool"]+=1
                    continue
                try:
                    # Only remove OpName annotations for non-descriptor
                    # values. The validated SPIR-V binary and every actual
                    # sample/OpLoad instruction remain unchanged.
                    result=stage_compare(
                        originals[kind],spv,reflected,
                        filter_nonresource_opnames(dis))
                except (ValueError,IndexError,KeyError,TypeError) as exc:
                    # Fixed public literal label only, never arbitrary private
                    # exception text, source tokens, resource names or IDs.
                    totals["failed_strict_source_to_spirv_pair_comparison_stages"]+=1
                    pair_ok=False
                    failure_categories[safe_failure_code(exc)]+=1
                    continue
                if not result["same_exact_private_original_DXBC_t_s_pair_multiset_as_translated_SPIRV"]:
                    totals["mismatched_source_translated_t_s_multiset_stages"]+=1
                    pair_ok=False
                    failure_categories["private_pair_multiset_mismatch"]+=1
                else:
                    totals["source_t_s_sample_instructions_validated_in_equal_multisets"]+=result["source_original_immediate_t_s_pairs"]
                    totals["translated_spirv_sample_instructions_validated_in_equal_multisets"]+=result["translated_sample_or_gather_strict_pairs"]
                if result["source_sample_or_gather_operations"]>0:
                    totals["sampled_source_selected_stages"]+=1
                else:
                    totals["source_zero_sample_selected_stages"]+=1
        if pair_ok:
            totals["representative_pair_translations_validated"]+=1
            totals["representative_pair_exact_source_to_SPIRV_t_s_pair_parity"]+=1
        else:
            totals["representative_pairs_with_any_stage_failure"]+=1
    if (totals["representative_pair_translations_attempted"]!=classes
            or totals["representative_pair_exact_source_to_SPIRV_t_s_pair_parity"]+
                totals["representative_pairs_with_any_stage_failure"]!=classes):
        raise ValueError("GFX049_REPRESENTATIVE_ACCOUNTING_INVALID")
    return {
        "experiment":"GFX-MULTI-049",
        "source_zip2_sha":ZIP2_SHA,
        "evidence_level":"ORIGINAL_SOURCE_AND_OFFLINE_TRANSLATOR_SPIRV_REPRESENTATIVE_PROFILES_ONLY",
        "original_shader48_passes":EXPECTED_PASSES,
        "all_524_exact_keyword_tier_pair_rows_scanned_for_selection":True,
        "unique_source_t_s_sample_multiset_classes_confirmed":classes,
        "original_source_variant_profile_selection_by_private_pair_multiset":True,
        "source_profile_representative_selection_by_original_pass_public_position":pass_rows,
        "representative_validation_safe_counts":dict(totals),
        "representative_failure_fixed_public_categories":dict(failure_categories),
        "all_58_sample_profiles_cpu_parity_proven":(
            totals["representative_pair_exact_source_to_SPIRV_t_s_pair_parity"]==EXPECTED_SIGNATURE_CLASSES),
        "all_524_original_pairs_translated_to_SPIRV":False,
        "sample_use_signature_equivalent_to_full_shader_logic":False,
        "material_texenv_property_to_original_DX11_resource_slot_mapping_proven":False,
        "original_constantbuffer_member_offsets_proven":False,
        "original_shader48_Android_GPU_execution_proven":False,
        "PC_to_Adreno_original_shader_pixel_parity_proven":False,
        "originalShaderRestored":False,
        "private_original_code_registers_pairs_keywords_or_identifiers_exported":False,
        "phase_closed":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip2",type=Path,required=True)
    parser.add_argument("--stage",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=audit(stage_originals(args.zip2,args.stage))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX049_SAFE_58_PROFILE_SOURCE_DXBC_SPIRV_COUNTS "+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
)

def filter_nonresource_opnames(dis):
    """Retain only resource-global OpName labels, preserve every real instruction.

    A SPIR-V compiler may give a type or function-local value the same debug
    name as a UniformConstant descriptor. The generic GFX046 parser reasonably
    rejects duplicate names; GFX049 can safely exclude *only* labels not
    attached to global UniformConstant OpVariable IDs. Duplicate names on
    actual resource globals remain and must still fail closed.
    """
    if not isinstance(dis,bytes) or not 0<len(dis)<=16*1024*1024:
        raise ValueError("GFX049_SPIRV_DISASSEMBLY_BOUNDS")
    try:
        lines=dis.decode("utf-8","strict").splitlines()
    except UnicodeDecodeError:
        raise ValueError("GFX049_SPIRV_DISASSEMBLY_UTF8_INVALID") from None
    resource_globals=set()
    for line in lines:
        match=_UNIFORM_CONSTANT_VAR.fullmatch(line.split(";",1)[0].strip())
        if match:
            resource_globals.add(match.group(1))
    output=[]
    for line in lines:
        match=_OPNAME.fullmatch(line.split(";",1)[0].strip())
        if match and match.group(1) not in resource_globals:
            continue
        output.append(line)
    return ("\n".join(output)+"\n").encode("utf-8")

def select_private_sample_profiles(passes, inspect_stage, limit=MAX_SELECTED_PAIRS):
    """Select one exact VS/FS source pair per private global sample signature.

    Accept a source-free synthetic inspector for tests. Never serialize the
    returned original variant rows, private signatures, or stage identities.
    """
    if (not isinstance(passes,list) or len(passes)!=EXPECTED_PASSES
        or type(limit) is not int or not 1<=limit<=MAX_SELECTED_PAIRS):
        raise ValueError("GFX049_INVALID_ORIGINAL_PASS_INPUT")
    seen=set()
    selections=[]
    pass_summary=[]
    scanned=0
    for passrecord in passes:
        pairs=passrecord.get("pairs") if isinstance(passrecord,dict) else None
        if not isinstance(pairs,list) or not 1<=len(pairs)<=MAX_PAIR_ROWS:
            raise ValueError("GFX049_INVALID_ORIGINAL_PAIR_BUCKET")
        new_classes=0
        for pair in pairs:
            if not isinstance(pair,(list,tuple)) or len(pair)!=2:
                raise ValueError("GFX049_INVALID_EXACT_PAIR")
            v,f=pair
            vinfo=inspect_stage(v,"Vertex")
            finfo=inspect_stage(f,"Pixel")
            if not isinstance(vinfo,dict) or not isinstance(finfo,dict):
                raise ValueError("GFX049_BAD_PRIVATE_SOURCE_INSPECTOR")
            signature=(private_signature(vinfo["pairs"]),private_signature(finfo["pairs"]))
            scanned+=1
            if signature not in seen:
                if len(selections)>=limit:
                    raise ValueError("GFX049_SOURCE_PROFILE_LIMIT_EXCEEDED")
                seen.add(signature)
                selections.append((passrecord,v,f,vinfo,finfo))
                new_classes+=1
        pass_summary.append({
            "subshader_public_position":passrecord.get("subshader"),
            "pass_public_position":passrecord.get("pass"),
            "exact_source_variant_pairs_examined":len(pairs),
            "new_global_sampling_profile_representatives_selected":new_classes,
        })
    if scanned!=EXPECTED_PAIRS:
        raise ValueError("GFX049_AUTHENTIC_524_PAIR_COUNT_DRIFT")
    return selections,pass_summary,scanned,len(seen)


def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=EXPECTED_PASSES:
        raise ValueError("GFX049_SHADER48_PASS_TOPOLOGY_DRIFT")
    cache={}
    def inspect_source(meta,kind):
        idx=meta.get("m_BlobIndex") if isinstance(meta,dict) else None
        gpu=meta.get("m_GpuProgramType") if isinstance(meta,dict) else None
        if type(idx) is not int or type(gpu) is not int or idx<0 or idx>=1656:
            raise ValueError("GFX049_ORIGINAL_STAGE_REF_INVALID")
        key=(kind,idx,gpu)
        if key not in cache:
            if len(cache)>=MAX_CACHED_PROGRAMS:
                raise ValueError("GFX049_SOURCE_STAGE_CACHE_UNBOUNDED")
            source=code_from_ref(meta,programs,kind)
            shdr=source_shader_chunk(source)
            slots,_=private_source_slots(shdr)
            pairs,counters=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            if counters["source_original_unresolved_dynamic_t_s"]!=0:
                raise ValueError("GFX049_UNRESOLVED_ORIGINAL_REGISTER_USE")
            cache[key]={"pairs":pairs,"sample_count":counters["source_sample_or_gather_operations"]}
        return cache[key]

    selected,pass_rows,scanned,classes=select_private_sample_profiles(passes,inspect_source)
    if scanned!=EXPECTED_PAIRS or classes!=EXPECTED_SIGNATURE_CLASSES or len(selected)!=classes:
        raise ValueError("GFX049_SOURCE_PROFILE_COUNT_DRIFT")
    totals=Counter({
        "original_exact_keyword_tier_pairs_scanned":scanned,
        "original_source_stage_programs_deduplicated_in_private_cache":len(cache),
        "selected_original_source_sampling_profiles":len(selected),
        "representative_pair_translations_attempted":0,
        "representative_pair_translations_validated":0,
        "representative_pair_exact_source_to_SPIRV_t_s_pair_parity":0,
        "representative_pairs_with_any_stage_failure":0,
        "failed_translation_or_spirv_validation_stages":0,
        "failed_spirv_reflection_or_disassembly_stages":0,
        "failed_strict_source_to_spirv_pair_comparison_stages":0,
        "mismatched_source_translated_t_s_multiset_stages":0,
        "source_t_s_sample_instructions_validated_in_equal_multisets":0,
        "translated_spirv_sample_instructions_validated_in_equal_multisets":0,
        "sampled_source_selected_stages":0,
        "source_zero_sample_selected_stages":0,
    })
    failure_categories=Counter()
    # Only bounded safe counts and public pass positions. Neither the selected
    # program index nor its private sampling signature is ever exported.
    for passrecord,vmeta,fmeta,vinfo,finfo in selected:
        totals["representative_pair_translations_attempted"]+=1
        pair_ok=True
        with tempfile.TemporaryDirectory(prefix="gfxlab049-private-") as temp:
            folder=Path(temp)
            originals={
                "vertex":code_from_ref(vmeta,programs,"Vertex"),
                "fragment":code_from_ref(fmeta,programs,"Pixel")
            }
            converted=translate_pair(originals["vertex"],originals["fragment"],folder)
            for kind in ("vertex","fragment"):
                if not converted[kind]["vulkan11_spirv_validation_success"]:
                    totals["failed_translation_or_spirv_validation_stages"]+=1
                    pair_ok=False
                    failure_categories["conversion_or_validation"]+=1
                    continue
                spv=folder/(kind+".spv")
                ok,refdata=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:
                    totals["failed_spirv_reflection_or_disassembly_stages"]+=1
                    pair_ok=False
                    failure_categories["reflection_tool"]+=1
                    continue
                try:
                    reflected=json.loads(refdata.decode("utf-8"))
                except (ValueError,UnicodeDecodeError):
                    reflected=None
                if not isinstance(reflected,dict):
                    totals["failed_spirv_reflection_or_disassembly_stages"]+=1
                    pair_ok=False
                    failure_categories["reflection_shape"]+=1
                    continue
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:
                    totals["failed_spirv_reflection_or_disassembly_stages"]+=1
                    pair_ok=False
                    failure_categories["disassembly_tool"]+=1
                    continue
                try:
                    result=stage_compare(originals[kind],spv,reflected,dis)
                except (ValueError,IndexError,KeyError,TypeError) as exc:
                    # Fixed public literal label only, never arbitrary private
                    # exception text, source tokens, resource names or IDs.
                    totals["failed_strict_source_to_spirv_pair_comparison_stages"]+=1
                    pair_ok=False
                    failure_categories[safe_failure_code(exc)]+=1
                    continue
                if not result["same_exact_private_original_DXBC_t_s_pair_multiset_as_translated_SPIRV"]:
                    totals["mismatched_source_translated_t_s_multiset_stages"]+=1
                    pair_ok=False
                    failure_categories["private_pair_multiset_mismatch"]+=1
                else:
                    totals["source_t_s_sample_instructions_validated_in_equal_multisets"]+=result["source_original_immediate_t_s_pairs"]
                    totals["translated_spirv_sample_instructions_validated_in_equal_multisets"]+=result["translated_sample_or_gather_strict_pairs"]
                if result["source_sample_or_gather_operations"]>0:
                    totals["sampled_source_selected_stages"]+=1
                else:
                    totals["source_zero_sample_selected_stages"]+=1
        if pair_ok:
            totals["representative_pair_translations_validated"]+=1
            totals["representative_pair_exact_source_to_SPIRV_t_s_pair_parity"]+=1
        else:
            totals["representative_pairs_with_any_stage_failure"]+=1
    if (totals["representative_pair_translations_attempted"]!=classes
            or totals["representative_pair_exact_source_to_SPIRV_t_s_pair_parity"]+
                totals["representative_pairs_with_any_stage_failure"]!=classes):
        raise ValueError("GFX049_REPRESENTATIVE_ACCOUNTING_INVALID")
    return {
        "experiment":"GFX-MULTI-049",
        "source_zip2_sha":ZIP2_SHA,
        "evidence_level":"ORIGINAL_SOURCE_AND_OFFLINE_TRANSLATOR_SPIRV_REPRESENTATIVE_PROFILES_ONLY",
        "original_shader48_passes":EXPECTED_PASSES,
        "all_524_exact_keyword_tier_pair_rows_scanned_for_selection":True,
        "unique_source_t_s_sample_multiset_classes_confirmed":classes,
        "original_source_variant_profile_selection_by_private_pair_multiset":True,
        "source_profile_representative_selection_by_original_pass_public_position":pass_rows,
        "representative_validation_safe_counts":dict(totals),
        "representative_failure_fixed_public_categories":dict(failure_categories),
        "all_58_sample_profiles_cpu_parity_proven":(
            totals["representative_pair_exact_source_to_SPIRV_t_s_pair_parity"]==EXPECTED_SIGNATURE_CLASSES),
        "all_524_original_pairs_translated_to_SPIRV":False,
        "sample_use_signature_equivalent_to_full_shader_logic":False,
        "material_texenv_property_to_original_DX11_resource_slot_mapping_proven":False,
        "original_constantbuffer_member_offsets_proven":False,
        "original_shader48_Android_GPU_execution_proven":False,
        "PC_to_Adreno_original_shader_pixel_parity_proven":False,
        "originalShaderRestored":False,
        "private_original_code_registers_pairs_keywords_or_identifiers_exported":False,
        "phase_closed":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--zip2",type=Path,required=True)
    parser.add_argument("--stage",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=audit(stage_originals(args.zip2,args.stage))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX049_SAFE_58_PROFILE_SOURCE_DXBC_SPIRV_COUNTS "+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
