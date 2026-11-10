#!/usr/bin/env python3
"""GFX-MULTI-038: compare original Shader48 paired DXBC stage signatures safely.

Only public DXBC ISGN/OSGN 24-byte D3D10 signature element structure is used.
Actual private semantic names, registers, bytecode, shaders, and keyword values
must remain in the ephemeral CI runner; the report contains aggregate counts.
Matching metadata does not establish original Android Shader48, rasterizer
interpolation, source Material-to-register/CB mapping or visual pixel parity.
"""
from __future__ import annotations
import argparse
import json
import struct
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_reflection_sweep import _locate_shader
from gfxlab.tools.multi_shader_gl_program_envelope import public_shader_compiler_platform
from gfxlab.tools.multi_shader_one_pass_spirv import compiled_programs,code_from_ref,exact_pairs
from gfxlab.tools.multi_shader_linked_dxbc_debug_chunks import safe_container_chunks

EXPECTED_PAIRS=524
MAX_SIGNATURE_ENTRIES=1024
MAX_SEMANTIC_NAME_BYTES=128
SIGNATURE_ELEMENT_BYTES=24
SIGNATURE_HEADER_BYTES=8

def safe_signature_entries(payload):
    """Bounded ISGN/OSGN base (24-byte) records, per public DXBC format."""
    if not isinstance(payload,bytes) or len(payload)<SIGNATURE_HEADER_BYTES:
        raise ValueError("ORIGINAL_DXBC_SIGNATURE_HEADER_TRUNCATED")
    count, reserved=struct.unpack_from("<II",payload,0)
    if count>MAX_SIGNATURE_ENTRIES or SIGNATURE_HEADER_BYTES+count*SIGNATURE_ELEMENT_BYTES>len(payload):
        raise ValueError("ORIGINAL_DXBC_SIGNATURE_TABLE_OUT_OF_BOUNDS")
    strings_start=SIGNATURE_HEADER_BYTES+count*SIGNATURE_ELEMENT_BYTES
    rows=[]
    for i in range(count):
        off=SIGNATURE_HEADER_BYTES+i*SIGNATURE_ELEMENT_BYTES
        name_off,sem_index,system,component,reg=struct.unpack_from("<IIIII",payload,off)
        mask,rw_mask=struct.unpack_from("<BB",payload,off+20)
        if name_off<strings_start or name_off>=len(payload):
            raise ValueError("ORIGINAL_SIGNATURE_SEMANTIC_OFFSET_INVALID")
        end=payload.find(b"\0",name_off,min(len(payload),name_off+MAX_SEMANTIC_NAME_BYTES+1))
        if end<0 or end==name_off:
            raise ValueError("ORIGINAL_SIGNATURE_NAME_UNTERMINATED_OR_EMPTY")
        raw=payload[name_off:end]
        if not all(32<=c<=126 for c in raw):
            raise ValueError("ORIGINAL_SIGNATURE_NAME_NONASCII")
        # The plain ASCII semantic label must never be serialized or printed.
        name=raw.decode("ascii").upper()
        if sem_index>65535 or system>256 or component>256 or reg>65535:
            raise ValueError("ORIGINAL_SIGNATURE_ENUM_OR_REGISTER_UNREASONABLE")
        if mask&0xf!=mask or rw_mask&0xf!=rw_mask:
            raise ValueError("ORIGINAL_SIGNATURE_COMPONENT_MASK_INVALID")
        rows.append((name,sem_index,system,component,reg,mask,rw_mask))
    return rows


def signature_from_container(dx,tag):
    if tag not in ("ISGN","OSGN"):
        raise ValueError("SOURCE_UNSUPPORTED_SIGNATURE_CHUNK")
    found=[p for name,p in safe_container_chunks(dx) if name==tag]
    if len(found)!=1:
        raise ValueError("ORIGINAL_SIGNATURE_CHUNK_ABSENT_OR_AMBIGUOUS")
    return safe_signature_entries(found[0])


def compare_stage_signatures(vertex_outputs,fragment_inputs):
    """Conservative *metadata* comparison; system values kept separate.

    Fragment system-value inputs may be rasterizer generated, so do not infer
    an error if no matching vertex output appears. Match ordinary varyings
    only by authored semantic + index (not by register ordinal).
    """
    if not isinstance(vertex_outputs,list) or not isinstance(fragment_inputs,list):
        raise ValueError("ORIGINAL_STAGE_SIGNATURE_SHAPE_INVALID")
    index={}
    for row in vertex_outputs:
        if not isinstance(row,tuple) or len(row)!=7:
            raise ValueError("ORIGINAL_VERTEX_SIGNATURE_RECORD_MALFORMED")
        index.setdefault((row[0],row[1]),[]).append(row)
    totals=Counter({
        "fragment_system_inputs":0,
        "fragment_non_system_inputs":0,
        "fragment_non_system_name_index_matches":0,
        "fragment_non_system_missing_output":0,
        "fragment_non_system_ambiguous_output":0,
        "fragment_non_system_component_type_mismatches":0,
        "fragment_non_system_component_mask_gaps":0,
        "fragment_non_system_compatible_by_signature":0,
        "system_inputs_with_same_named_vertex_output":0,
        "fragment_zero_component_masks":0,
    })
    used=set()
    for row in fragment_inputs:
        if not isinstance(row,tuple) or len(row)!=7:
            raise ValueError("ORIGINAL_FRAGMENT_SIGNATURE_RECORD_MALFORMED")
        name,semantic_index,sysval,ctype,reg,mask,rwmask=row
        options=index.get((name,semantic_index),[])
        if sysval!=0 or name.startswith("SV_"):
            totals["fragment_system_inputs"]+=1
            totals["system_inputs_with_same_named_vertex_output"]+=int(bool(options))
            continue
        totals["fragment_non_system_inputs"]+=1
        if mask==0:totals["fragment_zero_component_masks"]+=1
        if not options:
            totals["fragment_non_system_missing_output"]+=1
            continue
        totals["fragment_non_system_name_index_matches"]+=1
        if len(options)!=1:
            totals["fragment_non_system_ambiguous_output"]+=1
            continue
        source=options[0]
        used.add((name,semantic_index))
        if source[3]!=ctype:
            totals["fragment_non_system_component_type_mismatches"]+=1
        elif (mask & ~source[5])!=0:
            totals["fragment_non_system_component_mask_gaps"]+=1
        else:
            totals["fragment_non_system_compatible_by_signature"]+=1
    good=(totals["fragment_non_system_missing_output"]==0 and
          totals["fragment_non_system_ambiguous_output"]==0 and
          totals["fragment_non_system_component_type_mismatches"]==0 and
          totals["fragment_non_system_component_mask_gaps"]==0)
    return {
        **dict(totals),
        "vertex_output_signature_entries":len(vertex_outputs),
        "fragment_input_signature_entries":len(fragment_inputs),
        "vertex_output_name_index_keys_not_consumed_by_non_system_inputs":
            len(set(index)-used),
        "non_system_fragment_inputs_compatible_by_signature_only":good,
        "interpolation_mode_and_rasterizer_system_value_semantics_verified":False,
        "material_to_original_register_cb_mapping_verified":False,
    }


def audit(stage):
    entries,typed,_=all_model_entries(stage)
    shader=_locate_shader(entries,typed)
    if public_shader_compiler_platform(shader.read().platforms)!="kShaderCompPlatformD3D11":
        raise ValueError("ORIGINAL_SHADER48_SOURCE_PLATFORM_DRIFT")
    parsed=shader.read_typetree(check_read=False).get("m_ParsedForm")
    if not isinstance(parsed,dict):
        raise ValueError("ORIGINAL_SHADER48_PARSED_FORM_MISSING")
    sub=parsed.get("m_SubShaders")
    if not isinstance(sub,list) or [len(s.get("m_Passes",[])) for s in sub]!=[4,3]:
        raise ValueError("ORIGINAL_SHADER48_SEVEN_PASS_TOPOLOGY_CHANGED")
    programs=compiled_programs(shader)
    cache={}
    totals=Counter({
        "exact_original_keyword_tier_pairs":0,
        "pairs_with_non_system_fragment_inputs":0,
        "pairs_all_non_system_inputs_signature_compatible":0,
        "pairs_with_any_missing_non_system_varying":0,
        "pairs_with_any_component_type_mismatch":0,
        "pairs_with_any_component_mask_gap":0,
        "pairs_with_any_ambiguous_semantic":0,
        "unique_vertex_dxbc_signatures_inspected":0,
        "unique_fragment_dxbc_signatures_inspected":0,
    })
    per_pass=[]
    for s in sub:
        for p in s["m_Passes"]:
            pairs=exact_pairs(p)
            if not pairs:raise ValueError("ORIGINAL_PASS_EXACT_VARIANTS_MISSING")
            bypass=Counter({"exact_pairs":0,"compatible_pairs":0,
                            "pairs_with_unmatched_non_system_inputs":0})
            for vmeta,fmeta in pairs:
                vals=[]
                for meta,expected,kind in ((vmeta,"Vertex","OSGN"),(fmeta,"Pixel","ISGN")):
                    idx=meta.get("m_BlobIndex")
                    if type(idx) is not int or not 0<=idx<len(programs):
                        raise ValueError("ORIGINAL_PAIR_LINK_INDEX_INVALID")
                    key=(idx,kind)
                    if key not in cache:
                        dx=code_from_ref(meta,programs,expected)
                        cache[key]=signature_from_container(dx,kind)
                        totals["unique_vertex_dxbc_signatures_inspected" if kind=="OSGN"
                               else "unique_fragment_dxbc_signatures_inspected"]+=1
                    vals.append(cache[key])
                result=compare_stage_signatures(vals[0],vals[1])
                totals["exact_original_keyword_tier_pairs"]+=1
                bypass["exact_pairs"]+=1
                for name,value in result.items():
                    if type(value) is int:totals[name]+=value
                valid=result["non_system_fragment_inputs_compatible_by_signature_only"]
                totals["pairs_with_non_system_fragment_inputs"]+=int(
                    result["fragment_non_system_inputs"]>0)
                totals["pairs_all_non_system_inputs_signature_compatible"]+=int(valid)
                totals["pairs_with_any_missing_non_system_varying"]+=int(
                    result["fragment_non_system_missing_output"]>0)
                totals["pairs_with_any_component_type_mismatch"]+=int(
                    result["fragment_non_system_component_type_mismatches"]>0)
                totals["pairs_with_any_component_mask_gap"]+=int(
                    result["fragment_non_system_component_mask_gaps"]>0)
                totals["pairs_with_any_ambiguous_semantic"]+=int(
                    result["fragment_non_system_ambiguous_output"]>0)
                bypass["compatible_pairs"]+=int(valid)
                bypass["pairs_with_unmatched_non_system_inputs"]+=int(not valid)
            per_pass.append(dict(bypass))
    if len(per_pass)!=7 or totals["exact_original_keyword_tier_pairs"]!=EXPECTED_PAIRS:
        raise ValueError("SOURCE_EXACT_SIGNATURE_PAIR_COUNT_DRIFT")
    if totals["unique_vertex_dxbc_signatures_inspected"]>620 or totals["unique_fragment_dxbc_signatures_inspected"]>655:
        raise ValueError("SOURCE_EXACT_SIGNATURE_UNIQUE_PROGRAM_COUNT_DRIFT")
    return {
        "experiment":"GFX-MULTI-038",
        "source_sha":ZIP2_SHA,
        "original_shader_compiled_platform":"kShaderCompPlatformD3D11",
        "original_shader_passes":len(per_pass),
        "original_variant_signature_pair_totals":dict(totals),
        "per_original_pass_aggregate_counts":per_pass,
        "all_exact_pairs_non_system_signature_compatible":(
            totals["pairs_all_non_system_inputs_signature_compatible"]==EXPECTED_PAIRS),
        "signature_compatibility_proves_full_original_shader_execution":False,
        "original_material_to_shader_register_cb_semantics_verified":False,
        "original_unity_shaderlab_or_android_gles_compilation_verified":False,
        "original_pc_vs_adreno_pixels_verified":False,
        "original_shader48_restored":False,
        "source_private_semantics_program_bytes_keywords_ids_or_registers_exported":False,
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
    print("GFX_MULTI038_SAFE_DXBC_PAIR_SIGNATURE_COUNTERS "+json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
