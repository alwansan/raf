#!/usr/bin/env python3
"""GFX089: original DXBC declared input kind and ISGN/ISG1 signature (private).

This checks only source-private numeric register coincidence with translated
SPV Input Location and presence of decoration / stage information. It NEVER
proves D3D input semantic, original component values, Unity Material binding
or GPU parity. No raw IDs, names, registers or shader bytes leave CI.
"""
from __future__ import annotations
import struct,re
from collections import Counter
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import operand,CUSTOMDATA,MAX_DWORDS,MAX_INST
from gfxlab.tools.multi_shader_spv_dxbc_input_ubo_overlap088 import authenticated_spv_CB_index_iadd_source_provenance088
from gfxlab.tools.multi_shader_spv_index_root_taxonomy071 import ASSIGN, MAX_SPV_TEXT_BYTES,MAX_LINES

KINDS={95:"plain",96:"sgv",97:"siv",98:"pixel_plain",99:"pixel_sgv",100:"pixel_siv"}
PS_INTERP={0:"undefined",1:"constant",2:"linear",3:"centroid",
           4:"noperspective",5:"noperspective_centroid",
           6:"sample",7:"noperspective_sample"}

def source_dcl_input_private(shdr:bytes,stage:str):
    if (not isinstance(shdr,bytes) or not 8<=len(shdr)<=MAX_DWORDS*4 or
        len(shdr)%4 or stage not in ("vertex","fragment")):
        raise ValueError("GFX089_INVALID_PRIVATE_SHDR_STAGE")
    words=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if words[1]!=len(words):return None
    out={};at=2;steps=0
    while at<len(words):
        token=words[at];op=token&2047
        length=(words[at+1] if at+1<len(words) else 0) if op==CUSTOMDATA else (token>>24)&127
        if length<1 or at+length>len(words) or steps>MAX_INST:return None
        if op in KINDS:
            pos=at+1;n=0;ex=bool(token&0x80000000)
            while ex:
                if pos>=at+length or n>=4:return None
                extra=words[pos];ex=bool(extra&0x80000000);pos+=1;n+=1
            try:inp,end=operand(words,pos,at+length)
            except (ValueError,IndexError):return None
            if (inp.get("type")!=1 or inp.get("dimension")!=1 or
                inp.get("extended") or inp.get("dynamic") or
                len(inp.get("indices",()))!=1 or
                type(inp["indices"][0]) is not int):return None
            reg=inp["indices"][0]
            if not 0<=reg<=65535:return None
            if op in (96,97,99,100):
                if end+1!=at+length:return None
            elif end!=at+length:return None
            cls=KINDS[op]
            mode=(PS_INTERP.get((token>>11)&15,"invalid") if 98<=op<=100 else
                  "not_pixel_declaration")
            if reg in out:out[reg]=("ambiguous","ambiguous")
            else:out[reg]=(cls,mode)
        at+=length;steps+=1
    return out if at==len(words) else None

def input_signature_private(dx:bytes):
    """Conservative chunk parser for DXBC ISGN (24B) or ISG1 (32B).

    ISG1 starts each element with a stream DWORD followed by 24B base
    signature and a min-precision DWORD. Only one unique input signature
    chunk is accepted; any corruption/duplicate register is unknown.
    """
    if not isinstance(dx,bytes) or len(dx)<36 or dx[:4]!=b"DXBC":
        return None
    total=struct.unpack_from("<I",dx,24)[0]
    count=struct.unpack_from("<I",dx,28)[0]
    if total!=len(dx) or not 0<count<=64 or 32+4*count>len(dx):return None
    found=[]
    for i in range(count):
        off=struct.unpack_from("<I",dx,32+4*i)[0]
        if off<32+4*count or off+8>len(dx):return None
        fourcc=dx[off:off+4]
        size=struct.unpack_from("<I",dx,off+4)[0]
        if off+8+size>len(dx):return None
        if fourcc not in (b"ISGN",b"ISG1"):continue
        found.append((fourcc,dx[off+8:off+8+size]))
    if len(found)!=1:return None
    fourcc,data=found[0]
    if len(data)<8:return None
    n,base=struct.unpack_from("<II",data,0)
    row=24 if fourcc==b"ISGN" else 32
    if n>1024 or base<8 or base+n*row>len(data):return None
    result={}
    for i in range(n):
        offset=base+i*row
        start=offset+(4 if fourcc==b"ISG1" else 0)
        nameoff,semantic_idx,system,component,reg=struct.unpack_from("<5I",data,start)
        mask=data[start+20];rw=data[start+21]
        if (nameoff>=len(data) or data.find(b"\x00",nameoff,min(len(data),nameoff+256))<0 or
            reg>65535 or mask>15 or rw>15 or component>9 or system>128):
            return None
        if reg in result:
            result[reg]=("ambiguous","ambiguous","ambiguous")
        else:
            systemtype=("user_semantic" if system==0 else "system_semantic")
            masktype=("full_mask" if mask==15 else
                      "partial_mask" if mask else "empty_mask")
            result[reg]=(systemtype,masktype,
                         "ISG1" if fourcc==b"ISG1" else "ISGN")
    return result

def spv_actual_input_candidates(dis:bytes):
    """Map only SPV Input Location -> direct OpVariable ID privately."""
    if not isinstance(dis,bytes) or not 0<len(dis)<=MAX_SPV_TEXT_BYTES:raise ValueError("GFX089_INVALID_SPV")
    lines=dis.decode("utf8","strict").splitlines()
    if len(lines)>MAX_LINES:raise ValueError("GFX089_TOO_MANY_SPV_LINES")
    defs={};decs={};candidates={}
    for ln in lines:
        ln=ln.split(";",1)[0].strip()
        if not ln:continue
        m=ASSIGN.fullmatch(ln)
        if m:
            name,op,rest=m.groups()
            if name in defs:raise ValueError("GFX089_DUPLICATE_SPV_SSA")
            defs[name]=(op,(rest or "").split())
        elif ln.startswith("OpDecorate "):
            args=ln.split()
            if len(args)>=3:
                decs.setdefault((args[1],args[2]),set()).add(tuple(args[3:]))
    for name,(op,args) in defs.items():
        if op!="OpVariable" or len(args)<2 or args[1]!="Input":continue
        loc=decs.get((name,"Location"),set())
        if len(loc)==1 and len(next(iter(loc)))==1 and next(iter(loc))[0].isdigit():
            location=int(next(iter(loc))[0])
            candidates[name]=(location,{k for k in ("Flat","NoPerspective","Centroid","Sample","BuiltIn")
                 if (name,k) in decs})
    return candidates

def input_interface_source_semantic089(dis:bytes,auth:dict,shdr:bytes,source_cb:dict,
                                        dxbc:bytes,stage:str):
    """One pass strict old GFX088 audit plus anonymous numeric interface checks.

    Note: this scans all Input globals for a stage and is a stage-wide
    candidate taxonomy. Per 12 OpIAdd-linked inputs is separately checked by
    existing GFX088 SPV real CB index and original source audit.
    """
    old=authenticated_spv_CB_index_iadd_source_provenance088(dis,auth,shdr,source_cb)
    declaration=source_dcl_input_private(shdr,stage)
    signature=input_signature_private(dxbc)
    cand=spv_actual_input_candidates(dis)
    c=Counter()
    for loc,spvdecs in cand.values():
        dcl=(declaration or {}).get(loc,None) if declaration is not None else None
        if declaration is None:category="source_dcl_parse_unresolved"
        elif dcl is None:category="no_numeric_dcl_match"
        elif dcl[0]=="ambiguous":category="source_dcl_duplicate_ambiguous"
        else:category="dcl_"+dcl[0]
        c["source_Input_global_numeric_dcl_kind_"+category]+=1
        if dcl is None:c["source_Input_global_dcl_interpolation_unresolved"]+=1
        else:c["source_Input_global_dcl_interpolation_"+dcl[1]]+=1
        sig=(signature or {}).get(loc,None) if signature is not None else None
        if signature is None:sc="source_signature_unavailable_or_untrusted"
        elif sig is None:sc="signature_register_no_match"
        else:sc="signature_"+sig[0]+"_"+sig[1]+"_"+sig[2]
        c["source_Input_global_signature_"+sc]+=1
        spv_class=("Flat" if "Flat" in spvdecs else
                   "NoPerspective" if "NoPerspective" in spvdecs else
                   "Centroid" if "Centroid" in spvdecs else
                   "Sample" if "Sample" in spvdecs else
                   "no_interpolation_decoration")
        c["source_Input_global_SPV_interpolation_class_"+spv_class]+=1
        c["source_Input_global_stage_"+stage]+=1
    expected=len(cand)
    for prefix in ("source_Input_global_numeric_dcl_kind_",
                   "source_Input_global_dcl_interpolation_",
                   "source_Input_global_signature_",
                   "source_Input_global_SPV_interpolation_class_",
                   "source_Input_global_stage_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=expected:
            raise ValueError("GFX089_SOURCE_INPUT_STAGE_INTERFACE_PARTITION_DRIFT")
    return {**dict(c),"source_input_global_count":expected,
        "GFX089_stage_global_location_equals_original_semantic_proven":False,
        "GFX089_source_signature_and_SPV_decor_prove_component_mask_parity":False,
        "GFX089_DXBC_decl_variant_and_SPV_interp_prove_runtime_interpolation":False,
        "GFX089_originalShaderRestored":False,
        "GFX089_original_source_CB_material_bytes_proven":False,
        "GFX089_original_pixel_parity_proven":False,
        "GFX089_previous_427_authenticated_source_CB_reads":old.get("SPV_original_b_authenticated_actual_dynamic_CB_OpLoads",0)}
