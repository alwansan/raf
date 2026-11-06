#!/usr/bin/env python3
"""Strict stage-local dual-explicit-profile SPIR-V descriptor relocation proof.

Two source-authenticated DXBC compilations MUST request different explicit
VKD3D resource interface mappings. Same original variable IDs with the same
source register row in A/B and byte-for-byte identical SPIR-V after masking
ONLY OpDecorate Binding/DescriptorSet literals is a structural compiler
binding-relocation contract, NOT original Unity/ShaderLab import, pixel math,
texture sampling correctness or Adreno output proof.

All private source register, descriptor coordinates, OpNames, SPV IDs and
SPV instruction bytes stay in memory; only integer counts/flags are public.
"""
from __future__ import annotations

import struct

from scripts import t3_particle108_spirv_opname_candidates as spv

STATUS="T3_DUAL_PROFILE_VKD3D_SPIRV_STAGE_DESCRIPTOR_RELOCATION"
FAMILY={"C","T","S","U"}
MAX_ROWS=64

def _uint(text,bound):
    if type(text) is not str or not text.isascii() or not text.isdecimal() or (
        len(text)>1 and text[0]=="0"):
        raise ValueError("T3_PRIVATE_EXPLICIT_PACKET_NUMERIC")
    val=int(text)
    if val<0 or val>bound:
        raise ValueError("T3_PRIVATE_EXPLICIT_PACKET_RANGE")
    return val

def _private_packet(packet,stage,profile):
    if (type(packet) is not str or not 1<=len(packet)<=4096 or
        type(stage) is not int or stage not in (0,1) or
        profile not in ("A","B")):
        raise ValueError("T3_PRIVATE_EXPLICIT_PAIR_PACKET")
    rows=packet.splitlines()
    header=rows[0].split()
    if (len(header)!=4 or header[0]!="T3MAP1" or
        header[1]!=("V" if stage else "P") or header[2]!=profile):
        raise ValueError("T3_PRIVATE_EXPLICIT_PAIR_HEADER")
    count=_uint(header[3],MAX_ROWS)
    if not count or len(rows)!=count+1:
        raise ValueError("T3_PRIVATE_EXPLICIT_PAIR_ROWS")
    out={}
    target=set()
    for line in rows[1:]:
        columns=line.split()
        if len(columns)!=4 or columns[0] not in FAMILY:
            raise ValueError("T3_PRIVATE_EXPLICIT_PAIR_ENTRY")
        key=(columns[0],_uint(columns[1],4095))
        dest=(_uint(columns[2],64),_uint(columns[3],4095))
        if key in out or dest in target:
            raise ValueError("T3_PRIVATE_EXPLICIT_PAIR_ALIAS")
        out[key]=dest
        target.add(dest)
    return out

def _private_reloc_module(module,stage):
    # Existing strict binary SPV parser verifies exact VS/FS EntryPoint,
    # bounded IDs, descriptor shape, and unique decorations.
    _,decorations,_,variables=spv._private_program(module,stage)
    # Real graphics modules also contain Input/Output/Private OpVariable IDs.
    # They are not resource descriptors and MUST NOT be required to have
    # DescriptorSet/Binding. Conversely, any descriptor attached to such an
    # interface variable remains invalid and fails the exact set check.
    resource_variables={var:(ptr,storage) for var,(ptr,storage) in variables.items()
                        if storage in (spv.STORAGE_UNIFORM_CONSTANT,
                                       spv.STORAGE_UNIFORM,
                                       spv.STORAGE_STORAGE_BUFFER)}
    if not resource_variables or set(decorations)!=set(resource_variables):
        raise ValueError("T3_PRIVATE_EXPLICIT_SPV_BINDING_COVERAGE")
    by_variable={}
    for var in resource_variables:
        x=decorations[var]
        if set(x)!={spv.DECORATION_SET,spv.DECORATION_BINDING}:
            raise ValueError("T3_PRIVATE_EXPLICIT_SPV_BINDING_PAIRS")
        pair=(x[spv.DECORATION_SET],x[spv.DECORATION_BINDING])
        if pair in by_variable.values():
            raise ValueError("T3_PRIVATE_EXPLICIT_SPV_BINDING_ALIAS")
        by_variable[var]=pair
    words=list(struct.unpack("<"+"I"*(len(module)//4),module))
    i=5
    while i<len(words):
        n=words[i]>>16
        opcode=words[i]&0xffff
        if opcode==spv.OP_DECORATE and n==4 and words[i+2] in (
            spv.DECORATION_SET,spv.DECORATION_BINDING):
            if words[i+1] not in resource_variables:
                raise ValueError("T3_PRIVATE_EXPLICIT_DECORATION_NOT_VARIABLE")
            words[i+3]=0
        i+=n
    return by_variable,tuple(words)

def verify_pair(packet_a,packet_b,spv_a,spv_b,stage):
    """Fail-closed chosen A/B register→descriptor structural identity proof."""
    expected_a=_private_packet(packet_a,stage,"A")
    expected_b=_private_packet(packet_b,stage,"B")
    if (set(expected_a)!=set(expected_b) or
        any(expected_a[key]==expected_b[key] for key in expected_a)):
        raise ValueError("T3_PRIVATE_EXPLICIT_SOURCE_MAP_DIFFERENCE")
    variables_a,normal_a=_private_reloc_module(spv_a,stage)
    variables_b,normal_b=_private_reloc_module(spv_b,stage)
    if (len(variables_a)!=len(expected_a) or
        set(variables_a.values())!=set(expected_a.values()) or
        len(variables_b)!=len(expected_b) or
        set(variables_b.values())!=set(expected_b.values())):
        raise ValueError("T3_PRIVATE_EXPLICIT_DESTINATION_CONTRACT")
    # A/B must agree on WHICH original source resource maps to WHICH
    # SPIR-V variable, not simply totals and target set membership.
    inverse_a={value:var for var,value in variables_a.items()}
    inverse_b={value:var for var,value in variables_b.items()}
    if any(inverse_a[expected_a[k]]!=inverse_b[expected_b[k]] for k in expected_a):
        raise ValueError("T3_PRIVATE_EXPLICIT_SAME_SOURCE_VARIABLE_CHANGED")
    if normal_a!=normal_b:
        raise ValueError("T3_PRIVATE_EXPLICIT_NON_DESCRIPTOR_INSTRUCTIONS_CHANGED")
    return {
        "schema_version":1,"status":STATUS,
        "source_registers_mapped_under_both_profiles":len(expected_a),
        "chosen_explicit_target_layouts_verified":2,
        "same_source_to_spirv_variable_identity_across_profiles":True,
        "whole_spirv_program_identical_except_descriptor_literals":True,
        "source_register_numbers_spirv_IDS_descriptor_coordinates_published":False,
        "chosen_translator_binding_map_is_NOT_Unity_material_binding":True,
        "shaderlab_compiled_or_android_pixels_verified":False,
    }
