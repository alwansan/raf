"""GFX104: source-safe SPIR-V NoPerspective input decorations (stdlib only).

Reads in-memory binary generated from authenticated Shader48 DXBC on a private
CI runner; never outputs variable IDs, names, source code, registers or paths.
SPIR-V specification: OpDecorate=71, OpMemberDecorate=72, NoPerspective=13,
Flat=14, BuiltIn=11, Location=30, OpVariable=59, Input storage class=1.
Counters are candidates only, not DXBC operand identity/pixel parity.
"""
import struct
from collections import defaultdict

SPIRV_MAGIC=0x07230203
INPUT=1
OP_VARIABLE=59
OP_TYPE_POINTER=32
OP_DECORATE=71
OP_MEMBER_DECORATE=72
OP_DECORATION_GROUP=73
OP_GROUP_DECORATE=74
OP_GROUP_MEMBER_DECORATE=75
BUILTIN=11
NO_PERSPECTIVE=13
FLAT=14
LOCATION=30

def inspect_spirv_input_interpolation(binary):
    if not isinstance(binary,bytes) or len(binary)<20 or len(binary)%4:
        raise ValueError("GFX104_SPIRV_SIZE")
    if len(binary)>16*1024*1024:
        raise ValueError("GFX104_SPIRV_TOO_LARGE")
    words=struct.unpack("<%dI"%(len(binary)//4),binary)
    if words[0]!=SPIRV_MAGIC or words[4]!=0 or not 0<words[3]<=1_000_000:
        raise ValueError("GFX104_SPIRV_HEADER")
    decorations=defaultdict(set)
    member_decorations=defaultdict(set)
    input_variables={}
    pointer_types={}
    group_decorations=False
    instruction_count=0
    at=5
    while at<len(words):
        header=words[at]
        count=header>>16
        op=header&0xffff
        if count<1 or at+count>len(words):
            raise ValueError("GFX104_SPIRV_INSTRUCTION_BOUNDS")
        args=words[at+1:at+count]
        if op==OP_DECORATE:
            if len(args)<2:raise ValueError("GFX104_DECORATION_TRUNCATED")
            decorations[args[0]].add(args[1])
        elif op==OP_MEMBER_DECORATE:
            if len(args)<3:raise ValueError("GFX104_MEMBER_DECORATION_TRUNCATED")
            member_decorations[args[0]].add((args[1],args[2]))
        elif op==OP_TYPE_POINTER:
            if len(args)!=3:raise ValueError("GFX104_POINTER_TYPE_TRUNCATED")
            pointer_types[args[0]]=(args[1],args[2])
        elif op==OP_VARIABLE:
            if len(args)<3:raise ValueError("GFX104_VARIABLE_TRUNCATED")
            if args[2]==INPUT:
                input_variables[args[1]]=args[0]
        elif op in (OP_DECORATION_GROUP,OP_GROUP_DECORATE,OP_GROUP_MEMBER_DECORATE):
            group_decorations=True
        instruction_count+=1
        if instruction_count>1_000_000:
            raise ValueError("GFX104_INSTRUCTION_LIMIT")
        at+=count
    if at!=len(words):raise ValueError("GFX104_SPIRV_NOT_EXHAUSTED")
    direct_native=direct_builtin=direct_flat=0
    member_native=member_builtin=0
    undecorated_input=0
    unresolved_type=0
    for var_id,pointer_id in input_variables.items():
        dec=decorations[var_id]
        builtin=BUILTIN in dec
        if builtin:direct_builtin+=1
        if NO_PERSPECTIVE in dec and not builtin:direct_native+=1
        if FLAT in dec and not builtin:direct_flat+=1
        ptr=pointer_types.get(pointer_id)
        if ptr is None or ptr[0]!=INPUT:
            unresolved_type+=1
            continue
        struct_id=ptr[1]
        for member_index,mode in member_decorations.get(struct_id,set()):
            if mode==NO_PERSPECTIVE:member_native+=1
            if mode==BUILTIN:member_builtin+=1
        if not dec and not member_decorations.get(struct_id):
            undecorated_input+=1
    all_input_native_candidates=direct_native+member_native
    return {
        "source":"SPIRV_BINARY_CPU_ONLY",
        "input_variables":len(input_variables),
        "input_direct_noperspective_nonbuiltin":direct_native,
        "input_direct_builtin_variables":direct_builtin,
        "input_direct_flat_nonbuiltin":direct_flat,
        "input_member_noperspective_decorations":member_native,
        "input_member_builtin_decorations":member_builtin,
        "input_no_perspective_candidate_count":all_input_native_candidates,
        "input_undecorated_variables":undecorated_input,
        "input_pointer_type_unresolved":unresolved_type,
        "group_decorations_unhandled":group_decorations,
        "native_interface_identity_proven":False,
        "source_dxbc_ps_varying_identity_proven":False,
        "android_gpu_source_stage_pixel_parity_proven":False,
        "originalShaderRestored":False,
        "phase_closed":False,
    }
