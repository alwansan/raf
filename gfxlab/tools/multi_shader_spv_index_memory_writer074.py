#!/usr/bin/env python3
"""GFX074: bounded SPIR-V memory writer candidates for authenticated CB index loads.

A same-block Store->Load is a local SPIR-V candidate ONLY. It does not prove
inter-language DXBC temp register/SSA value mapping, pointer alias freedom,
whole-CFG dominance, runtime bounds or original Shader48 on Android.
No private SPIR-V IDs, source registers, names, or instructions are exported.
"""
from __future__ import annotations
from collections import Counter
import re
from gfxlab.tools.multi_shader_spv_index_root_taxonomy071 import MAX_SPV_TEXT_BYTES, MAX_LINES, ASSIGN

ID=re.compile(r"^%[0-9]+$")
OP=re.compile(r"^Op[A-Za-z0-9_]+$")
PURE_UNARY={"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"}
BARRIERS={"OpFunction","OpFunctionEnd","OpFunctionCall","OpBranch",
          "OpBranchConditional","OpSwitch","OpKill","OpUnreachable",
          "OpReturn","OpReturnValue","OpSelectionMerge","OpLoopMerge",
          "OpMemoryBarrier","OpControlBarrier","OpCopyMemory",
          "OpCopyMemorySized","OpEmitVertex","OpEndPrimitive"}

def spv_index_local_store_candidates(dis:bytes, authenticated:dict)->dict:
    if not isinstance(dis,bytes) or not 0<len(dis)<=MAX_SPV_TEXT_BYTES or not isinstance(authenticated,dict):
        raise ValueError("GFX074_BAD_INPUT")
    lines=dis.decode("utf-8","strict").splitlines()
    if len(lines)>MAX_LINES: raise ValueError("GFX074_LINE_BOUND_EXCEEDED")
    records=[];defs={};int32=set()
    for line in lines:
        line=line.split(";",1)[0].strip()
        if not line:continue
        m=ASSIGN.fullmatch(line)
        if m:
            name,op,tail=m.groups()
            if name in defs: raise ValueError("GFX074_DUPLICATE_RESULT_ID")
            args=(tail or "").split()
            defs[name]=(op,args)
            records.append((name,op,args))
            if op=="OpTypeInt" and args in (["32","0"],["32","1"]):int32.add(name)
        else:
            tok=line.split()
            if not tok or not OP.fullmatch(tok[0]):
                raise ValueError("GFX074_UNRECOGNIZED_SPV_INSTRUCTION")
            records.append((None,tok[0],tok[1:]))
    constants={}
    for name,(op,a) in defs.items():
        if op=="OpConstant" and len(a)==2 and a[0] in int32:
            try:constants[name]=int(a[1],0)
            except ValueError:
                try:constants[name]=int(a[1],10)
                except ValueError:pass
        if op=="OpConstantNull" and len(a)==1 and a[0] in int32:
            constants[name]=0
    def index_kind(t):
        if t in constants:return "literal",constants[t]
        op,a=defs.get(t,(None,[]))
        if op and op not in {"OpConstant","OpConstantNull","OpSpecConstant",
                "OpSpecConstantOp","OpUndef"} and a and a[0] in int32:
            return "dynamic",None
        return "unknown",None
    def root_index_load(t):
        """Get actual index OpLoad result from a strict Bitcast or single-literal IAdd."""
        op,a=defs.get(t,(None,[]))
        def bitcast_load(x):
            o,v=defs.get(x,(None,[]))
            if o!="OpBitcast" or len(v)!=2 or v[0] not in int32:return None
            lo,la=defs.get(v[1],(None,[]))
            if lo=="OpLoad" and len(la)>=2:return v[1]
            return None
        direct=bitcast_load(t)
        if direct:return direct
        if op=="OpIAdd" and len(a)==3 and a[0] in int32:
            left,right=a[1:]
            for literal,other in ((left,right),(right,left)):
                if index_kind(literal)[0]=="literal":
                    return bitcast_load(other)
        return None
    def shifted_store_value(value):
        """Pure, bounded SSA ancestor only; never assert DXBC writer equivalence."""
        seen=set()
        for _ in range(9):
            if value in seen:return False
            seen.add(value)
            op,a=defs.get(value,(None,[]))
            if op=="OpShiftLeftLogical" and len(a)==3 and a[0] in int32:
                return True
            if op in PURE_UNARY and len(a)==2:
                value=a[1];continue
            return False
        return False
    ptrs={};last_store={};index_read={};c=Counter()
    block=None
    for name,op,a in records:
        if op=="OpLabel":
            block=name;last_store.clear()
            continue
        if op in BARRIERS or op.startswith("OpAtomic"):
            last_store.clear()
            if op in ("OpFunction","OpFunctionEnd"):block=None
            continue
        if op=="OpStore":
            # All unknown pointer writes are potential aliases and invalidate earlier stores.
            if (len(a)!=2 or block is None or a[0] not in defs or
                defs[a[0]][0]!="OpVariable" or
                len(defs[a[0]][1])<2 or defs[a[0]][1][1]!="Function"):
                last_store.clear()
                c["SPV_untrusted_store_pointer_or_memory_operands_barriers"]+=1
            else:
                last_store[a[0]]=(a[1],block)
            continue
        if op=="OpLoad" and name:
            if len(a)<2:raise ValueError("GFX074_SPV_LOAD_INVALID")
            pointer=a[1]
            # A local store is candidate only if pointer is a direct Function variable.
            origin=defs.get(pointer,(None,[]))
            if len(a)!=2 or origin[0]!="OpVariable" or len(origin[1])<2 or origin[1][1]!="Function":
                index_read[name]="unknown"
            elif block is None:
                index_read[name]="no_block"
            elif pointer in last_store and last_store[pointer][1]==block:
                index_read[name]="local_shift" if shifted_store_value(last_store[pointer][0]) else "local_store"
            else:
                index_read[name]="no_same_block_store"
        if name and op in ("OpAccessChain","OpInBoundsAccessChain") and len(a)>=3:
            root=a[1];inds=a[2:]
            if root in authenticated:
                info=authenticated[root]
                if (not isinstance(info,tuple) or len(info)!=4 or
                    any(type(v)!=int for v in info) or info[1]!=0 or
                    info[2]!=16 or info[3]<=0):
                    raise ValueError("GFX074_UNTRUSTED_ORIGINAL_CB_LAYOUT")
                kind="root";extent=info[3]
            elif root in ptrs:
                kind,extent,old_idx=ptrs[root]
            else:continue
            if kind=="root":
                if not inds or index_kind(inds[0])!=("literal",0):continue
                inds=inds[1:]
                if not inds:
                    ptrs[name]=("array",extent,None);continue
            elif kind=="vector":
                if len(inds)==1 and index_kind(inds[0])[0]=="literal":
                    val=index_kind(inds[0])[1]
                    if 0<=val<4:ptrs[name]=("scalar",extent,old_idx)
                continue
            elif kind!="array":continue
            if len(inds) not in (1,2):continue
            if index_kind(inds[0])[0]!="dynamic":continue
            if len(inds)==2:
                comp=index_kind(inds[1])
                if comp[0]!="literal" or not 0<=comp[1]<4:continue
                k="scalar"
            else:k="vector"
            ptrs[name]=(k,extent,inds[0])
        elif name and op=="OpCopyObject" and len(a)==2 and a[1] in ptrs:
            ptrs[name]=ptrs[a[1]]
        if op=="OpLoad" and len(a)>=2 and a[1] in ptrs:
            kind,extent,idx=ptrs[a[1]]
            if kind not in ("vector","scalar"):continue
            c["SPV_authenticated_actual_dynamic_CB_OpLoad_occurrences"]+=1
            if idx is None:
                c["SPV_index_root_unclassified"]+=1;continue
            root_load=root_index_load(idx)
            if root_load is None:
                c["SPV_index_root_unclassified"]+=1;continue
            c["SPV_index_root_is_actual_OpLoad"]+=1
            category=index_read.get(root_load,"unknown")
            if category=="local_shift":c["SPV_same_block_local_store_with_shift_SSA_ancestor_candidates"]+=1
            elif category=="local_store":c["SPV_same_block_local_store_without_proven_shift_candidates"]+=1
            elif category=="no_same_block_store":c["SPV_index_memory_no_preceding_same_block_store"]+=1
            elif category=="no_block":c["SPV_index_memory_without_function_block"]+=1
            else:c["SPV_index_memory_pointer_alias_or_volatile_unknown"]+=1
    keys=("SPV_same_block_local_store_with_shift_SSA_ancestor_candidates",
          "SPV_same_block_local_store_without_proven_shift_candidates",
          "SPV_index_memory_no_preceding_same_block_store",
          "SPV_index_memory_without_function_block",
          "SPV_index_memory_pointer_alias_or_volatile_unknown")
    if sum(c[k] for k in keys)!=c["SPV_index_root_is_actual_OpLoad"]:
        raise ValueError("GFX074_WRITER_CLASSIFICATION_PARTITION_DRIFT")
    return {**dict(c),
            "SPV_local_store_candidate_proves_full_CFG_dominance":False,
            "SPV_local_store_shift_proves_original_DXBC_ISHL_correspondence":False,
            "original_DXBC_temp_to_SPV_index_loaded_value_equivalence_proven":False,
            "GFX054_original_Material_property_to_CB_member_bridge_proven":False,
            "originalShaderRestored":False,
            "phase_closed":False}
