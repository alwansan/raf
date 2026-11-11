"""GFX105: original-free, bounded DXBC SIV POSITION -> SPIR-V FragCoord witness.

This module receives in-memory shader program bytes, never private files or
identities. Counts semantic *candidates* only, NOT runtime PC↔Android pixels,
not source operand-to-SPIRV SSA/value identity and not an original shader port.

References:
Microsoft DirectX D3D12TokenizedProgramFormat.hpp:
DCL_INPUT_PS_SIV opcode=100; final instruction word is SystemNameToken,
POSITION=1, interpolation mode at bits14:11.
SPIR-V universal grammar: BuiltIn=11, FragCoord builtIn value=15.
"""
import re
import struct
from collections import Counter,defaultdict

SHDR_MAX=2_000_000
SPIRV_MAGIC=0x07230203
DXBC_DCL_INPUT_PS_SIV=100
DXBC_NAME_POSITION=1
DXBC_NOPERSPECTIVE={4,5,7}
SPIRV_OP_VARIABLE=59
SPIRV_OP_POINTER=32
SPIRV_OP_DECORATE=71
SPIRV_OP_MEMBER_DECORATE=72
SPIRV_GROUP_OPS={73,74,75}
SPIRV_BUILTIN=11
SPIRV_FRAGCOORD=15
SPIRV_STORAGE_INPUT=1

def dxbc_ps_siv_noperspective_semantic_counts(shdr):
    """Classify final NameToken only after validating bounded instruction walk."""
    if not isinstance(shdr,bytes) or len(shdr)<12 or len(shdr)%4 or len(shdr)>8*1024*1024:
        raise ValueError("GFX105_SHDR_SIZE")
    words=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if words[1]!=len(words) or len(words)>SHDR_MAX:
        raise ValueError("GFX105_SHDR_DECLARED_LENGTH")
    cursor=2;position=other=0;total=0
    while cursor<len(words):
        token=words[cursor];opcode=token&2047
        if opcode==53:
            if cursor+1>=len(words):raise ValueError("GFX105_CUSTOM_LENGTH_MISSING")
            length=words[cursor+1]
        else:length=(token>>24)&127
        # A legal DXBC instruction can be one DWORD (for example RET).
        # Only DCL_INPUT_PS_SIV requires the longer operand + NameToken.
        if length<1 or cursor+length>len(words):
            raise ValueError("GFX105_BAD_INSTRUCTION_BOUNDARY")
        if opcode==DXBC_DCL_INPUT_PS_SIV and (token>>11)&7 in DXBC_NOPERSPECTIVE:
            # By official token format, last word of this declaration is the
            # System Interpreted Value NameToken after a bounded input operand.
            if token>>31:raise ValueError("GFX105_UNSUPPORTED_EXTENDED_SIV")
            if length<4:raise ValueError("GFX105_SIV_NAME_TOKEN_MISSING")
            semantic=words[cursor+length-1]
            total+=1
            if semantic==DXBC_NAME_POSITION:position+=1
            else:other+=1
        cursor+=length
    if cursor!=len(words):raise ValueError("GFX105_SHDR_PARTIAL_WALK")
    return {"siv_noperspective_declarations":total,
        "siv_noperspective_position_name":position,
        "siv_noperspective_other_system_name":other,
        "siv_position_to_fragcoord_semantics_verified":False}

def spirv_fragment_builtin_inputs(binary):
    """Return count by semantic kind, scoped to actual OpVariable Input only."""
    if not isinstance(binary,bytes) or len(binary)<20 or len(binary)%4 or len(binary)>16*1024*1024:
        raise ValueError("GFX105_SPV_SIZE")
    words=struct.unpack("<%dI"%(len(binary)//4),binary)
    if words[0]!=SPIRV_MAGIC or not 0<words[3]<=1_000_000 or words[4]!=0:
        raise ValueError("GFX105_SPV_HEADER")
    pointers={};inputs={};direct=defaultdict(list);members=defaultdict(list)
    grouped=False;at=5
    while at<len(words):
        head=words[at];size=head>>16;opcode=head&65535
        if size<1 or at+size>len(words):raise ValueError("GFX105_SPV_INSTRUCTION_LENGTH")
        args=words[at+1:at+size]
        if opcode==SPIRV_OP_POINTER:
            if len(args)!=3:raise ValueError("GFX105_POINTER_BAD")
            pointers[args[0]]=(args[1],args[2])
        elif opcode==SPIRV_OP_VARIABLE:
            if len(args)<3:raise ValueError("GFX105_VARIABLE_BAD")
            if args[2]==SPIRV_STORAGE_INPUT:inputs[args[1]]=args[0]
        elif opcode==SPIRV_OP_DECORATE:
            if len(args)<2:raise ValueError("GFX105_DECORATE_BAD")
            if args[1]==SPIRV_BUILTIN:
                if len(args)!=3:raise ValueError("GFX105_BUILTIN_LITERAL_BAD")
                direct[args[0]].append(args[2])
        elif opcode==SPIRV_OP_MEMBER_DECORATE:
            if len(args)<3:raise ValueError("GFX105_MEMBER_BAD")
            if args[2]==SPIRV_BUILTIN:
                if len(args)!=4:raise ValueError("GFX105_MEMBER_BUILTIN_LITERAL_BAD")
                members[args[0]].append((args[1],args[3]))
        elif opcode in SPIRV_GROUP_OPS:grouped=True
        at+=size
    count=Counter();unresolved=0
    for variable,pointer in inputs.items():
        ptr=pointers.get(pointer)
        if ptr is None or ptr[0]!=SPIRV_STORAGE_INPUT:
            unresolved+=1;continue
        values=list(direct.get(variable,[]))
        values.extend(v for index,v in members.get(ptr[1],[]))
        # Count every actual Input builtin decoration; never consult Output
        # or unreferenced decoration on an unrelated variable.
        for code in values:
            count["fragcoord" if code==SPIRV_FRAGCOORD else "other_builtin"]+=1
    return {"input_builtin_fragcoord":count["fragcoord"],
        "input_builtin_other":count["other_builtin"],
        "input_variable_total":len(inputs),
        "input_pointer_type_unresolved":unresolved,
        "group_decorations_unhandled":grouped,
        "semantic_identity_to_source_dxbc_verified":False}

def generated_glsl_fragcoord_use(glsl):
    """Remove comments/literals before checking for real gl_FragCoord references."""
    if not isinstance(glsl,str) or len(glsl)>16*1024*1024:raise ValueError("GFX105_GLSL_SIZE")
    clean=re.sub(r'/\*[\s\S]*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"', "",glsl)
    return bool(re.search(r"\bgl_FragCoord\b",clean))

def classify_siv_builtin_bridge(shdr,spv,glsl):
    a=dxbc_ps_siv_noperspective_semantic_counts(shdr)
    b=spirv_fragment_builtin_inputs(spv)
    c=generated_glsl_fragcoord_use(glsl)
    candidate=(a["siv_noperspective_declarations"]>0 and
        a["siv_noperspective_declarations"]==a["siv_noperspective_position_name"] and
        b["input_builtin_fragcoord"]>=a["siv_noperspective_position_name"] and
        b["input_pointer_type_unresolved"]==0 and
        not b["group_decorations_unhandled"] and c)
    return {"source":a,"spirv":b,
        "generated_glsl_fragcoord_referenced":c,
        "source_position_spirv_fragcoord_glsl_candidate":bool(candidate),
        "source_ssa_register_mapping_verified":False,
        "source_vs_fragment_stage_pixel_parity_verified":False,
        "originalShaderRestored":False,"phase_closed":False}
