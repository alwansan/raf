#!/usr/bin/env python3
"""GFX-MULTI-048: source-private census of ALL 524 original Shader48 exact pairs.

Read real original tokenized DXBC sample/gather opcode operands and compare the
private resource/sampler use-signature *classes* across all source keyword/tier
variant pairs. The report is purely anonymous counts/histograms: NO t/s register
numbers, pair edges, keywords, tier names, shader blobs, GUIDs or property names.
One original source shader family / 7 passes; no Android ShaderLab or GPU pixels.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import original_sample_pairs

EXPECTED_PAIRS=524
MAX_PAIR_ROWS=2000
MAX_CACHED_PROGRAMS=1656

def private_signature(pairs):
    """Opaque private canonical pair MULTISET, never serialised in any report."""
    if not isinstance(pairs,list) or len(pairs)>200000:
        raise ValueError("GFX048_INVALID_PRIVATE_PAIR_SEQUENCE")
    if any(not isinstance(p,tuple) or len(p)!=2 or
           any(type(s) is not int or s<0 or s>65535 for s in p)
           for p in pairs):
        raise ValueError("GFX048_PRIVATE_PAIR_INVALID")
    return tuple(sorted(Counter(pairs).items()))

def safe_histogram(values,limit=MAX_PAIR_ROWS):
    if not isinstance(values,list) or len(values)>limit:
        raise ValueError("GFX048_BAD_VARIANT_HISTOGRAM")
    if any(type(x) is not int or x<0 or x>200000 for x in values):
        raise ValueError("GFX048_HISTOGRAM_BAD_VALUE")
    return {str(i):n for i,n in sorted(Counter(values).items())}

def summarize_pass_variants(items):
    """Records hold private pair arrays only in runner memory; emit safe buckets."""
    if not isinstance(items,list) or not 1<=len(items)<=MAX_PAIR_ROWS:
        raise ValueError("GFX048_SOURCE_PASS_PAIR_ROWS_INVALID")
    stages=("vertex","fragment")
    result={"exact_original_matched_variant_pairs":len(items)}
    for stage in stages:
        seen=set()
        counts=[]
        distinct=[]
        dynamic=[]
        opcode_sample=[]
        opcode_gather=[]
        for variant in items:
            if not isinstance(variant,dict) or stage not in variant:
                raise ValueError("GFX048_PASS_VARIANT_STAGE_MISSING")
            row=variant[stage]
            if not isinstance(row,dict) or "pairs" not in row or "stat" not in row:
                raise ValueError("GFX048_VARIANT_RECORD_BAD")
            stat=row["stat"]
            if not isinstance(stat,dict):
                raise ValueError("GFX048_VARIANT_COUNTS_INVALID")
            sequence=row["pairs"]
            sig=private_signature(sequence)
            seen.add(sig)
            counts.append(stat["source_sample_or_gather_operations"])
            distinct.append(stat["source_distinct_pairs_within_stage"])
            dynamic.append(stat["source_original_unresolved_dynamic_t_s"])
            opcode_sample.append(stat["original_sample_ops"])
            opcode_gather.append(stat["original_gather_ops"])
            if (len(sequence)+dynamic[-1]!=counts[-1] or len(set(sequence))!=distinct[-1]
                    or opcode_sample[-1]+opcode_gather[-1]!=counts[-1]):
                raise ValueError("GFX048_SOURCE_COUNTS_INCONSISTENT")
        result[stage+"_sample_instruction_count_histogram"]=safe_histogram(counts)
        result[stage+"_source_distinct_t_s_pair_count_histogram"]=safe_histogram(distinct)
        result[stage+"_dynamic_unresolved_count_histogram"]=safe_histogram(dynamic)
        result[stage+"_original_sample_opcode_count_histogram"]=safe_histogram(opcode_sample)
        result[stage+"_original_gather_opcode_count_histogram"]=safe_histogram(opcode_gather)
        result[stage+"_private_unique_t_s_pair_multiset_signature_classes"]=len(seen)
        result[stage+"_total_sample_operations_across_variant_references"]=sum(counts)
        result[stage+"_variants_with_unresolved_dynamic_source_indices"]=sum(v>0 for v in dynamic)
    result["all_variant_source_registers_bounded_and_parsed"]=True
    result["all_variant_register_values_and_pair_fingerprints_exported"]=False
    result["all_variant_PC_or_Android_GPU_parity_verified"]=False
    return result

def audit(stage):
    compiled,passes=source_pair(stage)
    if len(passes)!=7:
        raise ValueError("GFX048_ORIGINAL_SOURCE_SHADER48_PASS_TOPOLOGY_DRIFT")
    cache={}
    def parse_cached(meta,kind):
        index=meta.get("m_BlobIndex")
        typ=meta.get("m_GpuProgramType")
        if type(index) is not int or type(typ) is not int or index<0 or index>=1656:
            raise ValueError("GFX048_AUTHENTIC_SOURCE_REF_INVALID")
        key=(index,kind,typ)
        if key not in cache:
            if len(cache)>=MAX_CACHED_PROGRAMS:
                raise ValueError("GFX048_SOURCE_PROGRAM_CACHE_UNBOUNDED")
            dxbc=code_from_ref(meta,compiled,kind)
            shdr=source_shader_chunk(dxbc)
            slots,_=private_source_slots(shdr)
            seq,stat=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            cache[key]={"pairs":seq,"stat":stat}
        return cache[key]
    totals=Counter()
    output=[]
    all_sig=set()
    for pr in passes:
        variants=pr["pairs"]
        if not 1<=len(variants)<=MAX_PAIR_ROWS:
            raise ValueError("GFX048_MISSING_OR_EXCESS_ORIGINAL_VARIANTS")
        per=[]
        for v,f in variants:
            vr=parse_cached(v,"Vertex")
            fr=parse_cached(f,"Pixel")
            per.append({"vertex":vr,"fragment":fr})
            all_sig.add((private_signature(vr["pairs"]),private_signature(fr["pairs"])))
            totals["exact_keyword_tier_variant_pairs_scanned"]+=1
            totals["vertex_source_stage_references"]+=1
            totals["fragment_source_stage_references"]+=1
        safe=summarize_pass_variants(per)
        totals["representative_earlier_pass_pairs"]+=int(per[0]["fragment"]["stat"]["source_sample_or_gather_operations"] in (10,4,2,6,1))
        output.append({
            "subshader_public_position":pr["subshader"],
            "pass_public_position":pr["pass"],
            **safe
        })
    if totals["exact_keyword_tier_variant_pairs_scanned"]!=EXPECTED_PAIRS:
        raise ValueError("GFX048_SOURCE_VARIANT_PAIR_TOTAL_DRIFT")
    if len(output)!=7 or [x["exact_original_matched_variant_pairs"] for x in output] != [
        len(p["pairs"]) for p in passes
    ]:
        raise ValueError("GFX048_SOURCE_PASS_ACCOUNTING_DRIFT")
    return {
        "experiment":"GFX-MULTI-048",
        "source_zip2_sha":ZIP2_SHA,
        "original_source_shader48_subshaders":2,
        "original_source_shader48_passes":7,
        "original_exact_keyword_tier_pair_rows":EXPECTED_PAIRS,
        "linked_source_stage_references":totals["vertex_source_stage_references"]+totals["fragment_source_stage_references"],
        "cached_distinct_compiled_source_stage_programs_inspected":len(cache),
        "private_distinct_full_vs_fs_sample_signature_class_count":len(all_sig),
        "pass_anonymous_source_sampling_census":output,
        "all_524_original_exact_variant_pairs_scanned":True,
        "original_source_sample_registers_independently_decoded":True,
        "original_material_texenv_property_to_t_s_register_binding_proven":False,
        "constant_buffer_byte_offsets_proven":False,
        "all_524_translated_SPIRV_variants_compared":False,
        "original_Shader48_Android_GPU_runtime_verified":False,
        "original_shader48_PC_to_Adreno_pixel_equivalence_verified":False,
        "originalShaderRestored":False,
        "private_source_registers_pair_signatures_keywords_shader_bytes_exported":False,
        "phase_closed":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX048_SAFE_ALL_524_ORIGINAL_VARIANT_SAMPLE_SIGNATURE_COUNTS "+json.dumps(report,sort_keys=True))

if __name__=="__main__":main()
