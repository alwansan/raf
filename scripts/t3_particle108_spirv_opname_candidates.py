#!/usr/bin/env python3
"""Bounded source-DXBC DCL to SPIR-V OpName descriptor *candidate* join.

Only synthetic evidence is provided by this file's initial tests. In an
authenticated original+VKD3D run, OpName is untrusted debug information and
may be stripped, normalized, forged, or changed by the translator. It is
NEVER conclusive register provenance or shader/Android pixel equivalence.
The public result is COUNT-ONLY, with no original register/name, Vulkan
set/binding, SPIR-V IDs, program bytes, or per-keyword private identities.
"""
from __future__ import annotations

from collections import Counter
import re
import struct

from scripts.t3_particle108_original_dxbc_operand_bindings import DECL

MAX_SPIRV_BYTES=8*1024*1024
MAX_SPIRV_IDS=1_000_000
SPV_MAGIC=0x07230203
# SPIR-V core grammar opcodes and decorations, not HLSL-to-Vulkan mappings.
OP_ENTRY_POINT=15
OP_NAME=5
OP_DECORATE=71
OP_TYPE_IMAGE=25
OP_TYPE_SAMPLER=26
OP_TYPE_SAMPLED_IMAGE=27
OP_TYPE_ARRAY=28
OP_TYPE_RUNTIME_ARRAY=29
OP_TYPE_STRUCT=30
OP_TYPE_POINTER=32
OP_VARIABLE=59
DECORATION_BINDING=33
DECORATION_SET=34
STORAGE_UNIFORM_CONSTANT=0
STORAGE_UNIFORM=2
STORAGE_STORAGE_BUFFER=12
DEBUG_NAME=re.compile(r"^(cb|t|s|u)(0|[1-9][0-9]{0,3})$")
PREFIX={"cb":"cbuffer","t":"srv","s":"sampler","u":"uav"}
STAGE_MODEL={1:0,0:4} # DXBC vertex/pixel vs SPV ExecutionModel

def _private_program(blob,stage):
    """Private names/decorations/variables; never return this object publicly."""
    if (type(blob) is not bytes or len(blob)%4 or
        not 20<=len(blob)<=MAX_SPIRV_BYTES or stage not in STAGE_MODEL):
        raise ValueError("T3_SPIRV_INPUT_BOUNDS")
    words=struct.unpack("<"+"I"*(len(blob)//4),blob)
    if (words[0]!=SPV_MAGIC or words[1]>>16!=1 or
        words[1]&0xffff>6 or words[3]<2 or words[3]>MAX_SPIRV_IDS
        or words[4]!=0):
        raise ValueError("T3_SPIRV_HEADER")
    bound=words[3]
    names={};dec={};types={};variables={};entry=[]
    seen_result_ids=set()
    def valid_id(value):
        if type(value) is not int or not 0<value<bound:
            raise ValueError("T3_SPIRV_ID_BOUNDS")
    def define(value):
        valid_id(value)
        if value in seen_result_ids:
            raise ValueError("T3_SPIRV_DUPLICATE_ID")
        seen_result_ids.add(value)
    index=5
    while index<len(words):
        header=words[index];n=header>>16;opcode=header&0xffff
        if n<1 or index+n>len(words):
            raise ValueError("T3_SPIRV_INSTRUCTION_BOUNDS")
        a=words[index+1:index+n]
        if opcode==OP_ENTRY_POINT:
            if len(a)<3:
                raise ValueError("T3_SPIRV_ENTRYPOINT")
            valid_id(a[1]);entry.append(a[0])
        elif opcode==OP_NAME:
            if len(a)<2:
                raise ValueError("T3_SPIRV_NAME")
            valid_id(a[0])
            raw=struct.pack("<"+"I"*(len(a)-1),*a[1:])
            term=raw.find(b"\0")
            if (term<1 or term>128 or any(raw[term+1:])):
                raise ValueError("T3_SPIRV_NAME")
            try:
                name=raw[:term].decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError("T3_SPIRV_NAME") from None
            if a[0] in names:
                raise ValueError("T3_SPIRV_DUPLICATE_NAME")
            names[a[0]]=name
        elif opcode==OP_DECORATE and len(a)>=2 and a[1] in (DECORATION_BINDING,DECORATION_SET):
            if len(a)!=3 or a[2]>4095:
                raise ValueError("T3_SPIRV_DESCRIPTOR_DECORATION")
            valid_id(a[0])
            slot=dec.setdefault(a[0],{})
            if a[1] in slot:
                raise ValueError("T3_SPIRV_DUPLICATE_DECORATION")
            slot[a[1]]=a[2]
        elif opcode in (OP_TYPE_IMAGE,OP_TYPE_SAMPLER,OP_TYPE_SAMPLED_IMAGE,
                        OP_TYPE_ARRAY,OP_TYPE_RUNTIME_ARRAY,OP_TYPE_STRUCT,OP_TYPE_POINTER):
            if not a:
                raise ValueError("T3_SPIRV_TYPE")
            define(a[0])
            if (opcode==OP_TYPE_IMAGE and len(a) not in (8,9) or
                opcode==OP_TYPE_SAMPLER and len(a)!=1 or
                opcode==OP_TYPE_SAMPLED_IMAGE and len(a)!=2 or
                opcode==OP_TYPE_ARRAY and len(a)!=3 or
                opcode==OP_TYPE_RUNTIME_ARRAY and len(a)!=2 or
                opcode==OP_TYPE_POINTER and len(a)!=3):
                raise ValueError("T3_SPIRV_TYPE")
            types[a[0]]=(opcode,a)
        elif opcode==OP_VARIABLE:
            if len(a) not in (3,4):
                raise ValueError("T3_SPIRV_VARIABLE")
            valid_id(a[0]);define(a[1])
            variables[a[1]]=(a[0],a[2])
        index+=n
    if len(entry)!=1 or entry[0]!=STAGE_MODEL[stage]:
        raise ValueError("T3_SPIRV_STAGE_ENTRYPOINT")
    return names,dec,types,variables

def _private_resource_family(types,ptr_id,storage):
    t=types.get(ptr_id)
    if t is None or t[0]!=OP_TYPE_POINTER or t[1][1]!=storage:
        return None
    element=t[1][2]
    seen=set()
    for _ in range(8):
        if element in seen:
            raise ValueError("T3_SPIRV_TYPE_CYCLE")
        seen.add(element)
        data=types.get(element)
        if not data:
            return None
        opcode,args=data
        if opcode in (OP_TYPE_ARRAY,OP_TYPE_RUNTIME_ARRAY):
            # Array binding cardinality vs D3D register span needs
            # explicit independent reflection. Do not infer a candidate.
            return None
        if opcode==OP_TYPE_STRUCT:
            if storage==STORAGE_UNIFORM:
                return "cbuffer"
            if storage==STORAGE_STORAGE_BUFFER:
                return "uav"
            return None
        if opcode==OP_TYPE_IMAGE and storage==STORAGE_UNIFORM_CONSTANT:
            # OpTypeImage Sampled field: 1 = read-only sampled, 2 = storage.
            # Unknown (0) is not enough to establish family correspondence.
            return "srv" if args[6]==1 else "uav" if args[6]==2 else None
        if opcode==OP_TYPE_SAMPLER and storage==STORAGE_UNIFORM_CONSTANT:
            return "sampler"
        # Combined sampled image cannot be assigned uniquely to t# or s#.
        return None
    return None

def candidate_counts(source_layout,spv_bytes,stage):
    """Return safe candidate *counts*, never exact register identity proof.

    One original source DCL key can be counted as covered only when exactly
    one SPIR-V resource variable has matching simple OpName and type family
    and its own unique descriptor pair. Names can lie, so even all-covered
    sets return original_to_SPIRV_register_provenance_proven=False.
    """
    if type(source_layout) is not tuple or len(source_layout)>128:
        raise ValueError("T3_DX_SOURCE_LAYOUT")
    original=set()
    for item in source_layout:
        if (type(item) is not tuple or len(item)!=3 or
            type(item[1]) is not int or item[1] not in DECL or
            item[0]!=DECL[item[1]][0] or type(item[2]) is not tuple or
            len(item[2]) not in (1,2) or
            any(type(i) is not int or not 0<=i<=4095 for i in item[2])):
            raise ValueError("T3_DX_SOURCE_LAYOUT")
        key=(item[0],item[2][0])
        if key in original:
            raise ValueError("T3_DX_SOURCE_PRIMARY_COLLISION")
        original.add(key)
    names,decorations,types,variables=_private_program(spv_bytes,stage)
    named={}
    orphan=0;unsupported=0;unbound=0
    for var_id,(ptr_id,storage) in variables.items():
        name=names.get(var_id,"")
        match=DEBUG_NAME.fullmatch(name)
        if not match:
            continue
        key=(PREFIX[match.group(1)],int(match.group(2)))
        family=_private_resource_family(types,ptr_id,storage)
        if family!=key[0]:
            unsupported+=1
            continue
        if key in named:
            raise ValueError("T3_SPIRV_DEBUG_REGISTER_COLLISION")
        deco=decorations.get(var_id,{})
        if set(deco)!={DECORATION_BINDING,DECORATION_SET}:
            unbound+=1
            continue
        named[key]=(deco[DECORATION_SET],deco[DECORATION_BINDING])
        if key not in original:
            orphan+=1
    inverse=Counter(named.values())
    duplicate_descriptor_targets=sum(max(0,n-1) for n in inverse.values())
    matched=len(original & named.keys())
    return {
        "schema_version":1,
        "original_source_dcl_resource_rows":len(original),
        "spirv_debug_name_resource_candidates":len(named),
        "spirv_debug_candidates_matching_original_source_name_keys":matched,
        "original_source_dcl_without_typed_debug_candidate":len(original)-matched,
        "spirv_named_candidate_not_in_source_dcl":orphan,
        "spirv_debug_named_family_or_type_unsupported":unsupported,
        "spirv_debug_name_without_binding_or_set":unbound,
        "duplicate_candidate_descriptor_targets":duplicate_descriptor_targets,
        "all_original_resource_names_have_debug_candidates":bool(original) and
            matched==len(original) and orphan==0 and unsupported==0 and
            unbound==0 and duplicate_descriptor_targets==0,
        "debug_names_are_not_authoritative_binding_provenance":True,
        "original_to_SPIRV_register_provenance_proven":False,
        "ShaderLab_Android_pixels_or_resource_equivalence_proven":False,
        "private_SPIRV_descriptor_sets_bindings_DXBC_registers_names_published":False,
    }
