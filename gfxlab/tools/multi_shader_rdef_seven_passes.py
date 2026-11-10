#!/usr/bin/env python3
"""GFX-MULTI-015: count original Shader48 DXBC RDEF coverage in seven passes.

Counts only. Original source shader bytes, DXBC, SPIR-V, material identifiers,
GUID/PPtrs, keyword arrays and source images remain in ephemeral CI staging.
"""
import argparse,json,struct
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref
from gfxlab.tools.multi_shader_dxbc_rdef_shape import rdef_summary

KNOWN={b"RDEF":"RDEF",b"SHEX":"SHEX",b"SHDR":"SHDR",
       b"ISGN":"INPUT_SIGNATURE",b"ISG1":"INPUT_SIGNATURE",
       b"OSGN":"OUTPUT_SIGNATURE",b"OSG1":"OUTPUT_SIGNATURE",b"OSG5":"OUTPUT_SIGNATURE",
       b"PCSG":"PATCH_SIGNATURE",b"STAT":"STAT",b"IFCE":"IFCE",b"SFI0":"SFI0"}

def chunk_counts(data):
    if type(data)!=bytes or len(data)<36 or data[:4]!=b"DXBC":
        raise ValueError("NO_AUTHENTIC_DXBC_HEADER")
    total=struct.unpack_from("<I",data,24)[0]
    count=struct.unpack_from("<I",data,28)[0]
    if total!=len(data) or count<1 or count>64 or 32+4*count>total:
        raise ValueError("BAD_DXBC_CHUNK_TABLE")
    kinds=Counter()
    for n in range(count):
        pos=struct.unpack_from("<I",data,32+n*4)[0]
        if pos+8>total:raise ValueError("DXBC_CHUNK_OFFSET_OUT_OF_RANGE")
        size=struct.unpack_from("<I",data,pos+4)[0]
        if pos+8+size>total:raise ValueError("DXBC_CHUNK_LENGTH_INVALID")
        kinds[KNOWN.get(data[pos:pos+4],"OTHER")]+=1
    if not kinds["SHDR"] and not kinds["SHEX"]:
        raise ValueError("ORIGINAL_DXBC_STAGE_CHUNK_MISSING")
    return dict(sorted(kinds.items()))

def audit(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7:raise ValueError("ORIGINAL_SHADER_PASS_COUNT_DRIFT")
    rows=[]
    for p in passes:
        if not p["pairs"]:raise ValueError("MISSING_ORIGINAL_PAIR")
        v,f=p["pairs"][0]
        parsed={}
        for stage,meta,kind in (("vertex",v,"Vertex"),("fragment",f,"Pixel")):
            buf=code_from_ref(meta,programs,kind)
            chunks=chunk_counts(buf)
            summary=rdef_summary(buf)
            present=not summary.get("rdef_missing_in_source",False)
            parsed[stage]={
                "original_dxbc_container_verified":True,
                "rdef_present":bool(present),
                "source_constant_buffer_count":summary["constant_buffers"],
                "source_binding_descriptor_count":summary["resource_binding_descriptors"],
                "standard_dxbc_chunk_families":chunks,
                "source_to_spirv_register_equivalence_verified":False}
        rows.append({"subshader_ordinal":p["subshader"],"pass_ordinal":p["pass"],
            "source_exact_pairs_available":len(p["pairs"]),"stages":parsed})
    n=sum(1 for p in rows for s in p["stages"].values() if s["rdef_present"])
    return {"experiment":"GFX-MULTI-015","source_sha":ZIP2_SHA,
        "subshader_count":2,"original_pass_count":7,"representative_source_stages":14,
        "rdef_present_source_stages":n,"rdef_absent_source_stages":14-n,
        "per_pass":rows,
        "original_shader_resource_binding_mapping_verified":False,
        "all_variants_tested":False,
        "original_android_shader_compiled":False,
        "original_shader_restored":False,
        "original_game_pixels_verified":False,
        "proprietary_shader_bytes_exported":False,
        "phase_closed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();s=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(s,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI015_SAFE_RDEF_ALL_SEVEN "+json.dumps(s,sort_keys=True))
if __name__=="__main__":main()
