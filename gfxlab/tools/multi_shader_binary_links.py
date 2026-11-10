#!/usr/bin/env python3
"""GFX-MULTI-010: private verification of original Shader48 pass-variant blob links.

Never print/commit original program bytes, property labels, shader keywords,
texture coordinates, GUIDs/PPtrs or proprietary shader source. The only output
is numerical totals and allowlisted code-family classifications.
"""
from __future__ import annotations
import argparse,json,statistics
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_feasibility import _find_subprogram_rows
from gfxlab.tools.multi_shader_compiled_platform import scalar_first

def code_family(code):
    data=bytes(code)
    prefix=data[:4096]
    if prefix.startswith(b"DXBC"):return "dxbc_at_start"
    if b"DXBC" in prefix:return "dxbc_with_header"
    if prefix[:4]==b"\x03\x02\x23\x07":return "spirv_at_start"
    if b"\x03\x02\x23\x07" in prefix:return "spirv_with_header"
    if b"#version" in prefix or b"void main" in prefix:return "glsl_text_marker"
    if not prefix:return "empty"
    printable=sum(32<=b<127 or b in (9,10,13) for b in prefix)
    return "printable_unknown" if printable*100>=len(prefix)*90 else "binary_unknown"

def count_variant_links(pass_tree,programs):
    if not isinstance(pass_tree,dict):raise ValueError("BAD_TYPED_SOURCE_PASS")
    n=len(programs)
    if not n:raise ValueError("MISSING_COMPILED_PROGRAM_TABLE")
    rows=[]
    for stage in ("progVertex","progFragment"):
        d=pass_tree.get(stage)
        if not isinstance(d,dict):raise ValueError("MISSING_SOURCE_PROGRAM_STAGE")
        rows.extend([(stage,r) for r in (_find_subprogram_rows(d.get("m_SubPrograms"))+
                                         _find_subprogram_rows(d.get("m_PlayerSubPrograms")))])
    out=Counter();used=set();types=Counter();families=Counter()
    for stage,row in rows:
        out["source_variant_links"]+=1
        idx=row.get("m_BlobIndex")
        if type(idx)!=int or not 0<=idx<n:
            out["invalid_source_blob_index_links"]+=1
            continue
        compiled=programs[idx]
        if compiled is None:raise ValueError("MISSING_COMPILED_SOURCE_STAGE")
        used.add(idx)
        out["valid_source_blob_index_links"]+=1
        declared=row.get("m_GpuProgramType")
        compiled_type=int(compiled.m_ProgramType)
        if type(declared)==int:
            out["metadata_program_type_present"]+=1
            if declared==compiled_type:out["metadata_program_type_equal"]+=1
            else:out["metadata_program_type_mismatch"]+=1
        else:
            out["metadata_program_type_unreadable"]+=1
        label=str(compiled.m_ProgramType.name)
        if "GLES" in label:types["gles"]+=1
        elif "DX11" in label:types["dx11"]+=1
        elif "GLCore" in label or "GLLegacy" in label:types["desktop_gl"]+=1
        elif "DX9" in label:types["dx9"]+=1
        else:types["other"]+=1
        families[code_family(compiled.m_ProgramCode)]+=1
        out["stage_vertex_links" if stage=="progVertex" else "stage_fragment_links"]+=1
    return {
      **dict(out),"unique_referenced_blob_indices":len(used),
      "referenced_program_families":dict(types),
      "referenced_code_content_families":dict(families),
      "pass_ordinal_stage_linkage_equivalence_verified":False,
      "android_gles_semantic_equivalence_verified":False}

def audit(stage):
    from UnityPy.export.ShaderConverter import ShaderProgram
    from UnityPy.helpers import CompressionHelper
    from UnityPy.streams import EndianBinaryReader
    entries,typed,_=all_model_entries(stage)
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("MODEL_SELECTION_DRIFT")
    unique={(m["shader_owner"],m["shader_pid"]) for e in entries for m in e["materials"]}
    if len(unique)!=1 or sum(len(e["materials"]) for e in entries)!=7:
        raise ValueError("MATERIAL_SHADER_REFERENCE_DRIFT")
    owner,pid=next(iter(unique))
    obj=typed[owner].get(pid)
    if obj is None or obj.type.name!="Shader":raise ValueError("ORIGINAL_CLASS48_NOT_FOUND")
    d=obj.read_typetree(check_read=False)
    shader=obj.read()
    if len(shader.platforms)!=1:raise ValueError("UNEXPECTED_SOURCE_COMPILED_PLATFORM_COUNT")
    compressed=bytes(shader.compressedBlob)
    length=scalar_first(shader.compressedLengths[0])
    decompressed=scalar_first(shader.decompressedLengths[0])
    offset=scalar_first(shader.offsets[0])
    if not 0<length<=len(compressed) or not 0<=offset<=len(compressed)-length or not 0<decompressed<512_000_000:
        raise ValueError("ORIGINAL_SHADER_BLOB_BOUNDS_INVALID")
    plain=CompressionHelper.decompress_lz4(compressed[offset:offset+length],decompressed)
    if len(plain)!=decompressed:raise ValueError("ORIGINAL_SHADER_LZ4_SIZE_MISMATCH")
    progs=ShaderProgram(EndianBinaryReader(plain,endian="<"),shader.object_reader.version).m_SubPrograms
    if len(progs)!=1656:raise ValueError("ORIGINAL_SHADER_PROGRAM_TABLE_DRIFT")
    parsed=d.get("m_ParsedForm")
    if not isinstance(parsed,dict):raise ValueError("SHADER_PARSED_FORM_MISSING")
    subs=parsed.get("m_SubShaders")
    if not isinstance(subs,list) or len(subs)!=2:raise ValueError("ORIGINAL_SUBSHADER_COUNT_DRIFT")
    rows=[]
    for si,sub in enumerate(subs):
        passes=sub.get("m_Passes") if isinstance(sub,dict) else None
        if not isinstance(passes,list):raise ValueError("INVALID_ORIGINAL_PASSES")
        for pi,p in enumerate(passes):
            safe=count_variant_links(p,progs)
            rows.append({"subshader_index":si,"pass_index":pi,**safe})
    if len(rows)!=7:raise ValueError("ORIGINAL_SHADER_PASS_COUNT_DRIFT")
    total=Counter()
    for row in rows:
        for key in ("source_variant_links","valid_source_blob_index_links",
                    "invalid_source_blob_index_links","metadata_program_type_equal",
                    "metadata_program_type_mismatch","metadata_program_type_present",
                    "metadata_program_type_unreadable"):
            total[key]+=row.get(key,0)
    lens=[len(p.m_ProgramCode) for p in progs]
    # Only aggregate diagnostics. UnityPy can return non-source GPU blobs or
    # payloads with headers; neither indicates an Android executable shader.
    return {
      "experiment":"GFX-MULTI-010","source_sha":ZIP2_SHA,"models":6,"material_slots":7,
      "source_subshaders":2,"source_passes":7,"compiled_table_entries":len(progs),
      "compressed_blob_bytes":len(compressed),"decompressed_payload_bytes":len(plain),
      "sum_individual_program_code_bytes":sum(lens),"program_code_min_bytes":min(lens),
      "program_code_median_bytes":statistics.median(lens),"program_code_max_bytes":max(lens),
      "total_source_variant_links":dict(total),
      "per_pass_links":rows,
      "original_shader_bytes_exposed":False,"actual_android_shader_compiled":False,
      "program_semantics_verified":False,"original_shader_restored":False,"phase_closed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI010_SAFE_REFERENCED_VARIANT_LINKS "+json.dumps(report,sort_keys=True))
if __name__=="__main__":main()
