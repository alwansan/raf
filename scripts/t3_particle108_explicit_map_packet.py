#!/usr/bin/env python3
"""Prepare private, explicit VKD3D 1.2 VS/FS descriptor mapping packets.

Input is the authenticated original DXBC declaration operand inventory.
Output packet contains private original D3D registers and must be placed
ONLY inside runner-private temporary directories, never version-controlled
or uploaded. Public summaries contain counts only. A mapping REQUEST is not
evidence the compiler honored it; independent SPIR-V verification is needed.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from scripts.t3_particle108_original_dxbc_operand_bindings import DECL

MAGIC="T3MAP1"
FAMILY_CODE={"cbuffer":"C","srv":"T","sampler":"S","uav":"U"}
CODE_ORDER={"C":0,"T":1,"S":2,"U":3}
STAGE_CODE={1:"V",0:"P"}
PROFILE_TARGET={"A":(4,37,7),"B":(7,901,11)}
MAX_ROWS=64

def private_packets(original_layout, stage):
    """Return PRIVATE named packet strings and a SAFE category-only summary."""
    if (type(original_layout) is not tuple or not 1<=len(original_layout)<=MAX_ROWS
        or type(stage) is not int or stage not in STAGE_CODE):
        raise ValueError("T3_INVALID_PRIVATE_EXPLICIT_STAGE_LAYOUT")
    cleaned=[]
    seen=set()
    category=Counter()
    for row in original_layout:
        if (type(row) is not tuple or len(row)!=3 or
            type(row[0]) is not str or type(row[1]) is not int or
            row[1] not in DECL or DECL[row[1]][0]!=row[0] or
            type(row[2]) is not tuple or not 1<=len(row[2])<=2 or
            any(type(i) is not int or not 0<=i<=4095 for i in row[2])):
            raise ValueError("T3_INVALID_PRIVATE_EXPLICIT_DCL_RECORD")
        family,op,register=row
        key=(family,register[0])
        if key in seen:
            raise ValueError("T3_PRIVATE_EXPLICIT_REGISTER_COLLISION")
        seen.add(key)
        category[family]+=1
        cleaned.append((FAMILY_CODE[family],register[0]))
    cleaned.sort(key=lambda x:(CODE_ORDER[x[0]],x[1]))
    packet={}
    for name,(descriptor_set,first,stride) in PROFILE_TARGET.items():
        lines=["%s %s %s %d"%(MAGIC,STAGE_CODE[stage],name,len(cleaned))]
        for n,(family,register) in enumerate(cleaned):
            lines.append("%s %d %d %d"%(family,register,descriptor_set,first+n*stride))
        packet[name]="\n".join(lines)+"\n"
    safe={
        "schema_version":1,
        "source_stage_resource_count":len(cleaned),
        "source_stage_cbuffer_count":category["cbuffer"],
        "source_stage_srv_count":category["srv"],
        "source_stage_sampler_count":category["sampler"],
        "source_stage_uav_count":category["uav"],
        "two_explicit_target_profiles_distinct":True,
        "binding_request_is_NOT_SPIRV_binding_proof":True,
        "private_source_registers_and_descriptor_coordinates_published":False,
        "android_pixels_or_shaderlab_compilation_proven":False,
    }
    return packet,safe

def private_write_packets(packet,folder):
    """Write only to caller-provisioned (non-symlink) private stage directory."""
    if (type(packet) is not dict or set(packet)!=set(PROFILE_TARGET)
        or not isinstance(folder,Path) or not folder.is_dir() or folder.is_symlink()):
        raise ValueError("T3_PRIVATE_PACKET_DESTINATION")
    paths={}
    for profile in sorted(PROFILE_TARGET):
        body=packet[profile]
        if (type(body) is not str or len(body)>4096 or
            not body.startswith(MAGIC+" ")):
            raise ValueError("T3_PRIVATE_PACKET_CONTENT")
        path=folder/("explicit-"+profile+".map")
        if path.is_symlink() or path.exists():
            raise ValueError("T3_PRIVATE_PACKET_PREEXISTING")
        with path.open("x",encoding="ascii",newline="\n") as out:
            out.write(body)
        paths[profile]=path
    return paths
