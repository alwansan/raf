#!/usr/bin/env python3
"""GFX-MULTI-011: one exact original DX11 VS/FS variant pair, CPU-only translation.

All original proprietary GPU bytecode, shader labels, keywords, textures and
DXBC/SPIR-V files exist only inside an ephemeral runner. Output contains only
counts and booleans. No shader is installed in a Unity game or Android APK.
"""
from __future__ import annotations
import argparse,json,struct,subprocess,tempfile
from pathlib import Path
from collections import Counter
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_shader_variant_feasibility import _find_subprogram_rows
from gfxlab.tools.multi_shader_compiled_platform import scalar_first

def dxbc_containers(code:bytes):
    """Return structurally bounded DXBC slices, never naked marker matches."""
    out=[]
    for off in range(0,max(0,len(code)-31)):
        if code[off:off+4]!=b"DXBC":continue
        if len(code)-off<36:continue
        size=struct.unpack_from("<I",code,off+24)[0]
        chunks=struct.unpack_from("<I",code,off+28)[0]
        if not 36<=size<=8*1024*1024 or chunks<1 or chunks>64 or off+size>len(code):
            continue
        if 32+4*chunks>size:continue
        valid=True;has_stage=False
        for i in range(chunks):
            rel=struct.unpack_from("<I",code,off+32+4*i)[0]
            if rel+8>size:valid=False;break
            name=code[off+rel:off+rel+4]
            length=struct.unpack_from("<I",code,off+rel+4)[0]
            if rel+8+length>size:valid=False;break
            has_stage|=name in (b"SHDR",b"SHEX")
        if valid and has_stage:out.append(code[off:off+size])
    return out

def key(meta):
    # Private identity used strictly in the runner; not logged or persisted.
    fields=("m_GlobalKeywords","m_LocalKeywords","m_Keywords","m_KeywordIndices",
            "m_ShaderHardwareTier")
    return tuple(json.dumps(meta.get(f,[]),sort_keys=True) for f in fields)

def stage_records(stage):
    if not isinstance(stage,dict):raise ValueError("MISSING_ORIGINAL_PASS_STAGE")
    raw=stage.get("m_PlayerSubPrograms")
    if not isinstance(raw,list):raise ValueError("UNSUPPORTED_PLAYER_SUBPROGRAMS")
    result=[]
    for bucket,group in enumerate(raw):
        for row in _find_subprogram_rows(group):
            result.append((bucket,key(row),row))
    if not result:raise ValueError("ORIGINAL_PASS_NO_VARIANTS")
    return result

def exact_pairs(pass_tree):
    v=stage_records(pass_tree.get("progVertex"))
    f=stage_records(pass_tree.get("progFragment"))
    def unique(rows):
        d={};dup=set()
        for bucket,k,row in rows:
            pk=(bucket,k)
            if pk in d:dup.add(pk)
            d[pk]=row
        return {k:row for k,row in d.items() if k not in dup}
    vd=unique(v);fd=unique(f)
    common=vd.keys() & fd.keys()
    return [(vd[k],fd[k]) for k in sorted(common)]

def compiled_programs(obj):
    from UnityPy.export.ShaderConverter import ShaderProgram
    from UnityPy.helpers import CompressionHelper
    from UnityPy.streams import EndianBinaryReader
    shader=obj.read()
    if len(shader.platforms)!=1:raise ValueError("SOURCE_COMPILED_PLATFORM_CHANGED")
    compressed=bytes(shader.compressedBlob)
    off=scalar_first(shader.offsets[0]);ln=scalar_first(shader.compressedLengths[0])
    un=scalar_first(shader.decompressedLengths[0])
    if not 0<ln<=len(compressed) or not 0<=off<=len(compressed)-ln or not 0<un<512*1024*1024:
        raise ValueError("UNSAFE_COMPRESSED_SHADER_BLOB")
    buffer=CompressionHelper.decompress_lz4(compressed[off:off+ln],un)
    if len(buffer)!=un:raise ValueError("CORRUPT_LZ4_ORIGINAL_SHADER_BLOB")
    programs=ShaderProgram(EndianBinaryReader(buffer,endian="<"),shader.object_reader.version).m_SubPrograms
    if len(programs)!=1656:raise ValueError("SHADER_PROGRAM_TABLE_DRIFT")
    return programs

def source_pair(stage):
    entries,types,_=all_model_entries(stage)
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("MODEL_SELECTION_DRIFT")
    ids={(m["shader_owner"],m["shader_pid"]) for e in entries for m in e["materials"]}
    if len(ids)!=1:raise ValueError("SOURCE_SHADER_IDENTITY_DRIFT")
    owner,pid=next(iter(ids));obj=types[owner].get(pid)
    if obj is None or obj.type.name!="Shader":raise ValueError("SHADER48_UNAVAILABLE")
    d=obj.read_typetree(check_read=False)
    subs=d.get("m_ParsedForm",{}).get("m_SubShaders",[])
    if len(subs)!=2 or [len(s["m_Passes"]) for s in subs]!=[4,3]:
        raise ValueError("PASS_TOPOLOGY_DRIFT")
    programs=compiled_programs(obj)
    result=[]
    for si,sub in enumerate(subs):
        for pi,pass_tree in enumerate(sub["m_Passes"]):
            pairs=exact_pairs(pass_tree)
            result.append({"subshader":si,"pass":pi,"pairs":pairs})
    return programs,result

def code_from_ref(meta,programs,expected):
    idx=meta.get("m_BlobIndex")
    if type(idx)!=int or idx<0 or idx>=len(programs):
        raise ValueError("ORIGINAL_SHADER_LINK_OUT_OF_RANGE")
    prog=programs[idx]
    if type(meta.get("m_GpuProgramType"))!=int or int(prog.m_ProgramType)!=meta["m_GpuProgramType"]:
        raise ValueError("ORIGINAL_SOURCE_PROGRAM_TYPE_LINK_MISMATCH")
    label=prog.m_ProgramType.name
    if expected not in label or "DX11" not in label:
        raise ValueError("SHADER_STAGE_NOT_AUTHENTIC_DX11")
    candidates=dxbc_containers(bytes(prog.m_ProgramCode))
    if len(candidates)!=1:raise ValueError("ORIGINAL_SOURCE_DXBC_CONTAINER_AMBIGUOUS")
    return candidates[0]

def quiet_command(args):
    try:
        r=subprocess.run(args,capture_output=True,timeout=90,check=False)
        return r.returncode==0
    except (OSError,subprocess.TimeoutExpired):
        return False

def translate_pair(vs,fs,folder):
    out={}
    for stage,buf in (("vertex",vs),("fragment",fs)):
        inp=folder/(stage+".dxbc");spv=folder/(stage+".spv")
        inp.write_bytes(buf)
        translated=quiet_command(["vkd3d-compiler","-x","dxbc-tpf","-b","spirv-binary","-o",str(spv),str(inp)])
        validated=translated and spv.exists() and spv.stat().st_size>20 and quiet_command(
            ["spirv-val","--target-env","vulkan1.1",str(spv)])
        out[stage]={"authentic_source_dxbc_container":True,
                    "vulkan11_spirv_translation_success":translated,
                    "vulkan11_spirv_validation_success":validated,
                    "android_gles3_compilation_verified":False}
    return out

def audit(stage):
    programs,perpass=source_pair(stage)
    counts=[{"subshader":p["subshader"],"pass":p["pass"],"exact_variant_pairs":len(p["pairs"])}
            for p in perpass]
    chosen=next((p for p in perpass if len(p["pairs"])>0),None)
    if chosen is None:raise ValueError("NO_EXACT_ORIGINAL_STAGE_VARIANT_PAIRS")
    # Do not match a vertex record against an arbitrary fragment bucket.
    failures=Counter()
    validated=None
    for v,f in chosen["pairs"][:12]:
        try:
            vs=code_from_ref(v,programs,"Vertex")
            fs=code_from_ref(f,programs,"Pixel")
        except ValueError:
            failures["link_or_dxbc_rejection"]+=1;continue
        with tempfile.TemporaryDirectory(prefix="gfxlab-private-dxbc-") as name:
            validated=translate_pair(vs,fs,Path(name))
        break
    if validated is None:raise ValueError("NO_BOUNDED_AUTHENTIC_DXBC_STAGE_PAIR")
    return {"experiment":"GFX-MULTI-011","source_sha":ZIP2_SHA,
        "pass_variant_pair_counts":counts,"passes_with_exact_variant_pair":sum(c["exact_variant_pairs"]>0 for c in counts),
        "selected_subshader_index":chosen["subshader"],"selected_pass_index":chosen["pass"],
        "selected_pair":"exact_keyword_and_tier_bucket","candidate_link_rejections":dict(failures),
        "translation_stages":validated,"original_shader_source_private":True,
        "shader_binary_published":False,"original_shaderlab_restored":False,
        "android_gles3_compiled":False,"owner_device_shader_pixels_verified":False,"stage_closed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI011_SAFE_ONE_PASS_TRANSLATION "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
