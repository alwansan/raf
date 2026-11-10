#!/usr/bin/env python3
"""GFX-MULTI-009: inspect original compiled Shader48 platform inside private runner.

Uses documented UnityPy ShaderConverter parser for compressed SubProgramBlob.
Only generic GPU platform, number of stage programs and byte counts are published.
NEVER export source bytecode, shader strings, identifiers, uniforms, or GL code.
"""
import argparse,json
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries

def scalar_first(x):
    if isinstance(x,list):
        if not x:raise ValueError("SHADER_PLATFORM_LENGTH_FIELD_EMPTY")
        return scalar_first(x[0])
    if not isinstance(x,int):raise ValueError("SHADER_PLATFORM_LENGTH_FIELD_BAD")
    return x

def safe_kind(code):
    if isinstance(code,memoryview):code=code.tobytes()
    if not isinstance(code,(bytes,bytearray)):return "other"
    if code.startswith(b"DXBC"):return "dxbc"
    if code[:4]==b"\x03\x02\x23\x07":return "spirv"
    if code.lstrip().startswith((b"#version",b"precision ",b"void ")):return "glsl_or_text"
    return "other"

def probe_shader(o):
    from UnityPy.export.ShaderConverter import ShaderProgram
    from UnityPy.enums import ShaderCompilerPlatform
    from UnityPy.helpers import CompressionHelper
    from UnityPy.streams import EndianBinaryReader
    shader=o.read()
    plats=getattr(shader,"platforms",None)
    compressed=getattr(shader,"compressedBlob",None)
    clens=getattr(shader,"compressedLengths",None)
    dlens=getattr(shader,"decompressedLengths",None)
    offsets=getattr(shader,"offsets",None)
    if not isinstance(plats,list) or not plats:
        raise ValueError("ORIGINAL_SHADER_COMPILED_PLATFORMS_UNAVAILABLE")
    if any(not isinstance(x,list) for x in (clens,dlens,offsets)):
        raise ValueError("ORIGINAL_SHADER_COMPRESSION_FIELDS_UNAVAILABLE")
    if len(plats)>len(clens) or len(plats)>len(dlens) or len(plats)>len(offsets):
        raise ValueError("ORIGINAL_SHADER_COMPRESSION_LENGTH_MISMATCH")
    source=bytes(compressed)
    if not source or len(source)>512_000_000:raise ValueError("ORIGINAL_SHADER_BLOB_SIZE_UNSAFE")
    results=[]
    for index,platform in enumerate(plats):
        comp_len=scalar_first(clens[index]);dec_len=scalar_first(dlens[index]);offset=scalar_first(offsets[index])
        if comp_len<1 or dec_len<1 or comp_len>512_000_000 or dec_len>512_000_000 or offset<0 or offset+comp_len>len(source):
            raise ValueError("ORIGINAL_SHADER_COMPRESSED_REGION_INVALID")
        data=CompressionHelper.decompress_lz4(source[offset:offset+comp_len],dec_len)
        if len(data)!=dec_len:raise ValueError("ORIGINAL_SHADER_UNCOMPRESSED_LENGTH_MISMATCH")
        stages=ShaderProgram(EndianBinaryReader(data,endian="<"),shader.object_reader.version)
        programs=stages.m_SubPrograms
        if not isinstance(programs,list) or not programs:
            raise ValueError("ORIGINAL_SHADER_SUBPROGRAM_BLOB_MISSING")
        kind=Counter()
        gpu_types=Counter()
        byte_count=0
        for p in programs:
            if p is None:raise ValueError("ORIGINAL_SHADER_COMPRESSED_PROGRAM_MISSING")
            content=bytes(p.m_ProgramCode)
            byte_count+=len(content)
            kind[safe_kind(content)]+=1
            gpu_types[str(p.m_ProgramType.name if hasattr(p.m_ProgramType,"name") else "other")]+=1
        if byte_count<1:raise ValueError("ORIGINAL_SHADER_PROGRAM_BYTES_EMPTY")
        try:label=ShaderCompilerPlatform(int(platform)).name
        except (ValueError,TypeError):label="unknown_platform"
        results.append(dict(source_compiler_platform=label,original_compiled_program_count=len(programs),
            private_program_byte_total=byte_count,
            code_magic_families=dict(kind),
            generic_program_type_counts=dict(gpu_types),
            program_source_bytes_exported=False,
            original_gles_shader_verified=False,
            original_shader_semantics_verified=False))
    return dict(compiled_platforms=results,source_compressed_blob_bytes=len(source),
        number_of_source_compiler_platforms=len(plats),
        original_shaderlab_android_compilation_passed=False,
        source_native_programs_recovered_to_public_git=False)

def audit(stage):
    entries,types,_=all_model_entries(stage)
    if [x["id"] for x in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("GFX_MULTI009_MODEL_SELECTION_DRIFT")
    ids={(m["shader_owner"],m["shader_pid"]) for e in entries for m in e["materials"]}
    if len(ids)!=1 or sum(len(e["materials"]) for e in entries)!=7:
        raise ValueError("GFX_MULTI009_SHADER_IDENTITY_DRIFT")
    owner,pid=next(iter(ids))
    shader=types[owner].get(pid)
    if shader is None or shader.type.name!="Shader":raise ValueError("GFX_MULTI009_UNTYPED_CLASS48")
    return dict(experiment="GFX-MULTI-009",source_sha=ZIP2_SHA,models=6,materials=7,
        verified_typed_original_shader48=True,
        original_shader_binary=probe_shader(shader),
        original_android_shader_restored=False,owner_pc_pixel_parity=False,stage_closed=False)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",required=True,type=Path)
    ap.add_argument("--stage",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    a=ap.parse_args()
    d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI009_SAFE_COMPRESSED_PLATFORM_COUNTS "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
