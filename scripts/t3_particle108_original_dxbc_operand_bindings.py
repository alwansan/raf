#!/usr/bin/env python3
"""T3 strict and privacy-safe Particle108 original DXBC DCL operand decoder.

Same exact original four VS/PS pairs as SHDR/SHEX CI 42259943968 (44 DCL
resource-family opcodes). D3D10/11 operand token format: Microsoft
DirectX-Headers D3D12TokenizedProgramFormat.hpp. Binary operands, register
numbers, resource identities and raw compiled bytes never enter public reports.
This deliberately rejects unsupported dynamic/relative or extended formats
rather than inventing a register number.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import struct

from scripts import t3_particle108_original_dxbc_declarations as declarations
from scripts import t3_particle108_original_dxbc_rdef as native

STATUS="T3_SHA_ORIGINAL_PARTICLE108_DXBC_DECLARATION_OPERANDS"
# Decl opcode -> (register namespace, operand type, trailer dwords).
# Public D3D10/11 opcode and operand type definitions.
DECL={
    88:("srv",7,1), 89:("cbuffer",8,0), 90:("sampler",6,0),
    156:("uav",30,1), 157:("uav",30,0), 158:("uav",30,1),
    161:("srv",7,0), 162:("srv",7,1)
}
SAFE_REASONS={
    "DXBC_BIND_PROGRAM_ALIGNMENT":"TOKEN_ALIGNMENT",
    "DXBC_BIND_PROGRAM_LENGTH":"PROGRAM_LENGTH",
    "DXBC_BIND_PROGRAM_STAGE":"PROGRAM_STAGE",
    "DXBC_BIND_OPCODE_LENGTH":"OPCODE_LENGTH",
    "DXBC_BIND_OPCODE_OVERRUN":"OPCODE_OVERRUN",
    "DXBC_BIND_CUSTOMDATA":"CUSTOMDATA_LENGTH",
    "DXBC_BIND_EXTENDED_OPCODE_UNSUPPORTED":"EXTENDED_OPCODE_UNSUPPORTED",
    "DXBC_BIND_OPERAND_MISSING":"OPERAND_MISSING",
    "DXBC_BIND_OPERAND_TYPE":"OPERAND_TYPE",
    "DXBC_BIND_OPERAND_DIMENSION":"OPERAND_DIMENSION",
    "DXBC_BIND_OPERAND_INDEX_REP_UNSUPPORTED":"INDEX_REP_UNSUPPORTED",
    "DXBC_BIND_OPERAND_EXTENSION_UNSUPPORTED":"OPERAND_EXTENSION_UNSUPPORTED",
    "DXBC_BIND_OPERAND_INDEX_OVERRUN":"INDEX_OVERRUN",
    "DXBC_BIND_DECL_TRAILER":"DECL_TRAILER",
    "DXBC_BIND_STAGE_COUNT":"STAGE_COUNT",
    "original_authored_Shader48_props_changed":"ORIGINAL_SHADER_SCOPE",
    "original_paired_DXBC_shader_structure_changed":"ORIGINAL_PAIR_SCOPE",
    **declarations.SAFE_REASONS,
}

def _private_parse_decl_operand(inst,opcode):
    """Only immediate32, 1D/2D indexing; never return values in safe JSON."""
    family,operand_type,trailer=DECL[opcode]
    if len(inst)<2:
        raise ValueError("DXBC_BIND_OPERAND_MISSING")
    token=inst[1]
    if token&0x80000000:
        raise ValueError("DXBC_BIND_OPERAND_EXTENSION_UNSUPPORTED")
    if (token>>12)&0xff != operand_type:
        raise ValueError("DXBC_BIND_OPERAND_TYPE")
    dims=(token>>20)&0x3
    if dims not in (1,2):
        raise ValueError("DXBC_BIND_OPERAND_DIMENSION")
    indexes=[]
    position=2
    for d in range(dims):
        # 3 bits each, not the 2-bit legacy macro typo.
        rep=(token>>(22+3*d))&7
        if rep!=0:
            raise ValueError("DXBC_BIND_OPERAND_INDEX_REP_UNSUPPORTED")
        if position>=len(inst):
            raise ValueError("DXBC_BIND_OPERAND_INDEX_OVERRUN")
        indexes.append(inst[position])
        position+=1
    if len(inst)-position!=trailer:
        raise ValueError("DXBC_BIND_DECL_TRAILER")
    return (family,opcode,tuple(indexes))

def _private_stage_layout(dx,stage):
    """Return actual private (namespace, opcode, register-index tuple) items."""
    code=declarations.shader_chunk(dx)
    if len(code)<8 or len(code)%4:
        raise ValueError("DXBC_BIND_PROGRAM_ALIGNMENT")
    words=struct.unpack("<"+"I"*(len(code)//4),code)
    if words[1]!=len(words) or len(words)>declarations.MAX_WORDS:
        raise ValueError("DXBC_BIND_PROGRAM_LENGTH")
    if (words[0]>>16)&0xffff !=stage:
        raise ValueError("DXBC_BIND_PROGRAM_STAGE")
    found=[]
    i=2
    while i<len(words):
        t=words[i]
        opcode=t&0x7ff
        if opcode==declarations.CUSTOMDATA:
            if i+1>=len(words) or words[i+1]<2:
                raise ValueError("DXBC_BIND_CUSTOMDATA")
            size=words[i+1]
        else:
            size=(t>>24)&0x7f
            if size<1:
                raise ValueError("DXBC_BIND_OPCODE_LENGTH")
        if size>len(words)-i:
            raise ValueError("DXBC_BIND_OPCODE_OVERRUN")
        if opcode in DECL:
            if t&0x80000000:
                raise ValueError("DXBC_BIND_EXTENDED_OPCODE_UNSUPPORTED")
            found.append(_private_parse_decl_operand(words[i:i+size],opcode))
        i+=size
    return tuple(found)

def classify_four_pairs(pairs):
    if (type(pairs) is not list or len(pairs)!=4 or
        any(type(x) is not tuple or len(x)!=2 for x in pairs)):
        raise ValueError("ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED")
    stage_profiles={1:[],0:[]}
    c=Counter()
    for vertex,pixel in pairs:
        for st,blob in ((1,vertex),(0,pixel)):
            layout=_private_stage_layout(blob,st)
            stage_profiles[st].append(tuple(sorted(layout)))
            c["original_stage_declaration_operand_records"]+=len(layout)
            c["original_DXBC_stage_operand_layouts_parsed"]+=1
            for family,opcode,indexes in layout:
                c["original_dcl_"+family+"_operand_records"]+=1
                c["original_dcl_immediate32_index_dims_"+str(len(indexes))]+=1
            c["original_dcl_repeated_private_register_keys_within_stage"]+=len(layout)-len(set(layout))
        c["original_original_keyword_vsps_pairs"]+=1
    for label,st in (("vertex",1),("fragment",0)):
        distinct=len(set(stage_profiles[st]))
        c["original_"+label+"_private_register_layouts_across_four_variants"]=distinct
        c["original_"+label+"_private_register_layout_stable_across_four"]=int(distinct==1)
    for family in ("cbuffer","srv","sampler","uav"):
        c.setdefault("original_dcl_"+family+"_operand_records",0)
    if c["original_DXBC_stage_operand_layouts_parsed"]!=8:
        raise ValueError("DXBC_BIND_STAGE_COUNT")
    return {"schema_version":1,"status":STATUS,"counts":dict(sorted(c.items())),
        "original_private_dxbc_register_numbers_array_values_or_shader_bytes_published":False,
        "original_shader_program_Unity_compile_or_pixel_equivalence_proven":False,
        "SPIRV_Vulkan_register_binding_equivalence_proven":False,
        "register_array_span_or_cbuffer_byte_offsets_proven":False}

def classify_primary_index_profiles(pairs):
    """Safely distinguish first register index from 2D secondary DCL metadata.

    Signatures containing original numeric index words stay within the private
    process. Public output is count-only; a second cbuffer index is NOT claimed
    to be array size, byte offset or distinct register identity.
    """
    if (type(pairs) is not list or len(pairs)!=4 or
        any(type(p) is not tuple or len(p)!=2 for p in pairs)):
        raise ValueError("ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED")
    profiles={1:{"full":[],"opcode_primary":[],"family_primary":[]},
              0:{"full":[],"opcode_primary":[],"family_primary":[]}}
    by_family={st:{family:[] for family in ("cbuffer","srv","sampler","uav")}
               for st in (1,0)}
    c=Counter()
    for vertex,pixel in pairs:
        for st,blob in ((1,vertex),(0,pixel)):
            layout=_private_stage_layout(blob,st)
            profiles[st]["full"].append(tuple(sorted(layout)))
            profiles[st]["opcode_primary"].append(
                tuple(sorted((f,op,indices[0]) for f,op,indices in layout)))
            profiles[st]["family_primary"].append(
                tuple(sorted((f,indices[0]) for f,op,indices in layout)))
            c["original_private_primary_family_collisions"]+=(
                len(layout)-len(set((f,indices[0]) for f,op,indices in layout)))
            for family in by_family[st]:
                by_family[st][family].append(tuple(sorted(
                    idx[0] for f,_,idx in layout if f==family)))
            c["original_stage_primary_profiles_scanned"]+=1
    for stage,name in ((1,"vertex"),(0,"fragment")):
        for key in ("full","opcode_primary","family_primary"):
            distinct=len(set(profiles[stage][key]))
            c["original_"+name+"_"+key+"_profiles_distinct"]=distinct
            c["original_"+name+"_"+key+"_profiles_stable_all_four"]=int(distinct==1)
        for family,values in by_family[stage].items():
            c["original_"+name+"_"+family+"_first_register_profile_distinct"]=len(set(values))
    if c["original_stage_primary_profiles_scanned"]!=8:
        raise ValueError("DXBC_BIND_STAGE_COUNT")
    return {"schema_version":1,"counts":dict(sorted(c.items())),
        "original_first_register_indexes_or_second_index_values_published":False,
        "original_2d_secondary_index_size_semantics_proven":False,
        "shader_binding_or_device_color_fixed":False}


def probe(root,manifest):
    import UnityPy
    selected={}
    evidence=native.identity.source.load_original(root,manifest,
                                                  private_particle_slot_counts=selected)
    owner,pid=native.identity.select(selected,evidence)
    path=root/"Raft_Data"/owner
    if path.is_symlink() or native.fingerprint(path)!=native.SHADER_OWNERS[owner]:
        raise ValueError("SOURCE_PARTICLE_OWNER_SHA")
    obj=[o for o in UnityPy.load(str(path)).file.objects.values() if o.path_id==pid]
    if len(obj)!=1 or obj[0].type.name!="Shader":
        raise ValueError("SOURCE_PARTICLE_SHADER_IDENTITY")
    tree=obj[0].read_typetree()
    _,prop_shape=native.serialize_properties(tree["m_ParsedForm"])
    if prop_shape["original_authored_property_count"]!=13 or prop_shape["original_authored_texture_property_count"]!=2:
        raise ValueError("original_authored_Shader48_props_changed")
    platforms=[native.records(s) for platform,s in native.decoded_platforms(tree)
               if platform==4]
    if len(platforms)!=1:
        raise ValueError("SOURCE_D3D11_PROGRAM_TABLE")
    basis=native.identity.inspect(tree["m_ParsedForm"],platforms[0])
    if (basis.get("status")!=native.identity.STATUS or
        basis.get("matched_vertex_fragment_permutation_pairs")!=4 or
        basis.get("original_D3D11_program_table_records")!=16):
        raise ValueError("original_paired_DXBC_shader_structure_changed")
    pairs=native.stage.exact_four_pairs(tree["m_ParsedForm"],platforms[0])
    report=classify_four_pairs(pairs)
    report["primary_index_analysis"]=classify_primary_index_profiles(pairs)
    report["source_original_six_scenes_SHA_authenticated"]=True
    report["source_original_four_owner_SHA_authenticated"]=True
    report["source_particle_renderer_material_slots"]=108
    report["source_original_keyword_pairs"]=4
    return report

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","out"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or
        a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_DXBC_private_binding_report_location")
    try:
        report=probe(a.original,a.manifest)
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
            "failure_type":type(exc).__name__,
            "safe_original_DXBC_operand_failure_reason":SAFE_REASONS.get(str(exc),"UNCLASSIFIED_SOURCE"),
            "original_private_dxbc_register_numbers_array_values_or_shader_bytes_published":False,
            "original_shader_program_Unity_compile_or_pixel_equivalence_proven":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_DXBC_OPERANDS_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
