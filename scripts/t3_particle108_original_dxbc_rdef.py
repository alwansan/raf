#!/usr/bin/env python3
"""Exact original Particle108 four DXBC VS/FS pairs: source RDEF register census.

T3-RDEF-reason-13-test-original: real source, privacy-safe classification.
D3D11 compiled shader resource bindings in DXBC RDEF are the SOURCE-ORIGINAL
register contract, before VKD3D/SPIRV-Cross/glslang set/binding remapping.
No source resource names/register numbers, DXBC bytes, GUIDs, shader programs
or hidden metadata leave a private ephemeral original-source reader.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import struct

from scripts import t3_original_particle108_spirv_translation as stage
from scripts import t3_original_particle108_dxbc_feasibility as identity
from scripts.t3_particle108_source_propstate import serialize_properties
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms,records

STATUS="T3_SHA_ORIGINAL_PARTICLE108_FOUR_PAIR_DXBC_RDEF_CLASSIFIED"
PAIRS=4
MAX_BYTES=4*1024*1024
MAX_CHUNKS=64
MAX_RESOURCES=1024
MAX_REGISTER=4095

# Standard D3D_SHADER_INPUT_TYPE categories; preserve exact private type IDs
# for register families even though the report publishes only broad counts.
SAFE_RDEF_FAILURE_REASON={
    "DXBC_SOURCE_CONTAINER_LENGTH_OR_MAGIC":"SOURCE_CONTAINER",
    "DXBC_SOURCE_CHUNK_TABLE_BOUNDS":"CHUNK_TABLE",
    "DXBC_SOURCE_CHUNK_OFFSET_INVALID":"CHUNK_OFFSET",
    "DXBC_SOURCE_CHUNK_SIZE_INVALID":"CHUNK_SIZE",
    "DXBC_SOURCE_OVERLAPPING_CHUNKS":"CHUNK_OVERLAP",
    "DXBC_ORIGINAL_RDEF_NOT_UNIQUE":"ORIGINAL_RDEF_ABSENT_OR_AMBIGUOUS",
    "DXBC_SOURCE_RDEF_HEADER_SHORT":"RDEF_HEADER_SHORT",
    "DXBC_SOURCE_RDEF_BINDING_TABLE_BOUNDS":"RDEF_TABLE",
    "DXBC_SOURCE_RDEF_DESCRIPTOR_INVALID":"RDEF_DESCRIPTOR",
    "DXBC_SOURCE_RDEF_NAME_BOUNDS":"RDEF_NAME_BOUNDS",
    "DXBC_SOURCE_RDEF_NAME_ENCODING":"RDEF_NAME_ENCODING",
    "DXBC_RDEF_BINARY_BOUNDS":"RDEF_BINARY_BOUNDS",
    "original_authored_Shader48_props_changed":"ORIGINAL_SHADER_PROPERTY_SCOPE",
    "original_paired_DXBC_shader_structure_changed":"ORIGINAL_STAGE_SELECTION",
}
BIND_FAMILIES={0:"cbuffer",1:"srv",2:"srv",3:"sampler",
               4:"uav",5:"srv",6:"uav",7:"srv",8:"uav",
               9:"uav",10:"uav",11:"uav",12:"srv",13:"uav"}


def _u32(data,offset):
    if offset<0 or offset+4>len(data):
        raise ValueError("DXBC_RDEF_BINARY_BOUNDS")
    return struct.unpack_from("<I",data,offset)[0]


def source_rdef(dx):
    """Return private (shader-input-type, register-point, count) tuples."""
    if (type(dx) is not bytes or not 36<=len(dx)<=MAX_BYTES or
        dx[:4]!=b"DXBC" or _u32(dx,24)!=len(dx)):
        raise ValueError("DXBC_SOURCE_CONTAINER_LENGTH_OR_MAGIC")
    chunks=_u32(dx,28)
    if not 1<=chunks<=MAX_CHUNKS or 32+4*chunks>len(dx):
        raise ValueError("DXBC_SOURCE_CHUNK_TABLE_BOUNDS")
    found=[]
    occupied=[]
    for i in range(chunks):
        off=_u32(dx,32+4*i)
        if off<32+4*chunks or off+8>len(dx):
            raise ValueError("DXBC_SOURCE_CHUNK_OFFSET_INVALID")
        size=_u32(dx,off+4)
        if size>MAX_BYTES or off+8+size>len(dx):
            raise ValueError("DXBC_SOURCE_CHUNK_SIZE_INVALID")
        if any(off<right and old<off+size+8 for old,right in occupied):
            raise ValueError("DXBC_SOURCE_OVERLAPPING_CHUNKS")
        occupied.append((off,off+size+8))
        if dx[off:off+4]==b"RDEF":
            found.append(dx[off+8:off+8+size])
    if len(found)!=1:
        raise ValueError("DXBC_ORIGINAL_RDEF_NOT_UNIQUE")
    rdef=found[0]
    if len(rdef)<28:
        raise ValueError("DXBC_SOURCE_RDEF_HEADER_SHORT")
    res_count=_u32(rdef,8)
    res_off=_u32(rdef,12)
    if (not 0<=res_count<=MAX_RESOURCES or
        (res_count>0 and (res_off<28 or res_off+32*res_count>len(rdef)))):
        raise ValueError("DXBC_SOURCE_RDEF_BINDING_TABLE_BOUNDS")
    bindings=[]
    for i in range(res_count):
        off=res_off+i*32
        record=struct.unpack_from("<8I",rdef,off)
        nameoff,kind,_return,_dimension,_samples,reg,count,_flags=record
        if (kind not in BIND_FAMILIES or
            count<1 or count>128 or reg>MAX_REGISTER or
            reg+count>MAX_REGISTER+1 or
            nameoff<28 or nameoff>=len(rdef)):
            raise ValueError("DXBC_SOURCE_RDEF_DESCRIPTOR_INVALID")
        terminator=rdef.find(b"\x00",nameoff,min(len(rdef),nameoff+256))
        if terminator<=nameoff:
            raise ValueError("DXBC_SOURCE_RDEF_NAME_BOUNDS")
        # Only validate spelling and never return names to public report.
        name=rdef[nameoff:terminator]
        if len(name)>128 or any(c<32 or c>126 for c in name):
            raise ValueError("DXBC_SOURCE_RDEF_NAME_ENCODING")
        bindings.append((kind,reg,count))
    return tuple(bindings)


def _private_register_layout(rows):
    """Private exact original D3D register families, with array-range overlaps."""
    if type(rows) is not tuple or len(rows)>MAX_RESOURCES:
        raise ValueError("RDEF_ORIGINAL_RESOURCE_ROW_SCHEMA")
    found=Counter()
    per_family={}
    used=set()
    for item in rows:
        if (type(item) is not tuple or len(item)!=3 or
            any(type(x) is not int for x in item)):
            raise ValueError("RDEF_ORIGINAL_RESOURCE_ROW_SCHEMA")
        kind,point,size=item
        if (kind not in BIND_FAMILIES or not 0<=point<=MAX_REGISTER
            or not 1<=size<=128 or point+size>MAX_REGISTER+1):
            raise ValueError("RDEF_ORIGINAL_REGISTER_RANGE_INVALID")
        family=BIND_FAMILIES[kind]
        found[family+"_resource_rows"]+=1
        found[family+"_register_slots"]+=size
        for address in range(point,point+size):
            if (family,address) in used:
                found["same_family_overlapping_register_slots"]+=1
            used.add((family,address))
        per_family.setdefault(family,[]).append((kind,point,size))
    signature=tuple(sorted((key,tuple(sorted(value))) for key,value in per_family.items()))
    return signature,found


def classify_four_pairs(pairs):
    if (type(pairs) is not list or len(pairs)!=PAIRS or
        any(type(pair) is not tuple or len(pair)!=2 for pair in pairs)):
        raise ValueError("ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED")
    counters=Counter()
    stage_signatures={1:[],0:[]}
    pair_signatures=[]
    for vs,fs in pairs:
        left=[]
        for stage_id,bytes_ in ((1,vs),(0,fs)):
            rows=source_rdef(bytes_)
            signature,counts=_private_register_layout(rows)
            stage_signatures[stage_id].append(signature)
            left.append(signature)
            counters["original_DXBC_stages_parsed"]+=1
            counters["original_RDEF_resource_rows"]+=len(rows)
            for key,value in counts.items():
                counters[key]+=value
        pair_signatures.append(tuple(left))
        counters["source_original_vertex_fragment_keyword_pairs_parsed"]+=1
    for name,stage_id in (("vertex",1),("fragment",0)):
        counters[name+"_RDEF_register_layouts_distinct_across_four_keywords"]=len(
            set(stage_signatures[stage_id]))
        counters[name+"_RDEF_register_layout_stable_all_four"]=int(
            len(set(stage_signatures[stage_id]))==1)
    counters["RDEF_original_full_pair_register_layouts_distinct"]=len(set(pair_signatures))
    return {"schema_version":1,"status":STATUS,"source_original_keyword_pairs":PAIRS,
        "counts":dict(sorted(counters.items())),
        "original_DXBC_RDEF_register_numbers_names_types_or_bytecode_published":False,
        "original_shader_program_Unity_compile_or_pixel_equivalence_proven":False,
        "SPIRV_descriptor_set_mapping_proven":False}


def probe(root,manifest):
    import UnityPy
    selected={}
    result=identity.source.load_original(root,manifest,
                                         private_particle_slot_counts=selected)
    owner,pid=identity.select(selected,result)
    path=root/"Raft_Data"/owner
    if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
        raise ValueError("SHA_original_selected_particle_shader_owner_mismatch")
    obj=[o for o in UnityPy.load(str(path)).file.objects.values()
         if o.path_id==pid]
    if len(obj)!=1 or obj[0].type.name!="Shader":
        raise ValueError("original_Particle108_Shader48_identity_mismatch")
    tree=obj[0].read_typetree()
    props,shape=serialize_properties(tree["m_ParsedForm"])
    if shape["original_authored_property_count"]!=13 or shape["original_authored_texture_property_count"]!=2:
        raise ValueError("original_authored_Shader48_props_changed")
    platforms=[records(s) for platform,s in decoded_platforms(tree) if platform==4]
    if len(platforms)!=1:
        raise ValueError("SHA_original_D3D11_player_table_missing")
    baseline=identity.inspect(tree["m_ParsedForm"],platforms[0])
    if (baseline.get("status")!=identity.STATUS or
        baseline.get("matched_vertex_fragment_permutation_pairs")!=PAIRS or
        baseline.get("original_D3D11_program_table_records")!=16):
        raise ValueError("original_paired_DXBC_shader_structure_changed")
    pairs=stage.exact_four_pairs(tree["m_ParsedForm"],platforms[0])
    report=classify_four_pairs(pairs)
    report["source_original_six_scenes_SHA_authenticated"]=True
    report["source_original_four_owner_SHA_authenticated"]=True
    report["source_particle_renderer_material_slots"]=108
    report["source_shader_authored_properties"]=13
    report["source_shader_authored_texture_properties"]=2
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for field in ("original","manifest","out"):
        p.add_argument("--"+field,required=True,type=Path)
    a=p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()):
        raise ValueError("unsafe_DXBC_RDEF_report_location")
    try:
        report=probe(a.original,a.manifest)
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "safe_original_RDEF_failure_reason":SAFE_RDEF_FAILURE_REASON.get(
                    str(exc),"UNCLASSIFIED_ORIGINAL_SOURCE"),
                "original_DXBC_RDEF_register_numbers_names_types_or_bytecode_published":False,
                "original_shader_program_Unity_compile_or_pixel_equivalence_proven":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_DXBC_RDEF_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
