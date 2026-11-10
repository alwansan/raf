#!/usr/bin/env python3
"""GFX075: count-only original-b-authenticated SPIR-V CB index OpLoad POINTER origin.

Source-private SPV result IDs, original b-register IDs and dereferenced pointer
names never leave CI. Same SSA pointer-id store-before-load is syntax only, not
alias-free runtime dataflow or DXBC source-temp correspondence.
"""
from __future__ import annotations
import re
from collections import Counter
from gfxlab.tools.multi_shader_spv_index_root_taxonomy071 import ASSIGN, MAX_SPV_TEXT_BYTES, MAX_LINES

SAFE_STORAGES=frozenset({"Function","Private","Input","Output","Uniform",
                         "StorageBuffer","Workgroup","PushConstant","UniformConstant"})
BLOCK_BARRIERS=frozenset({"OpBranch","OpBranchConditional","OpSwitch","OpKill",
    "OpReturn","OpReturnValue","OpUnreachable","OpFunctionCall",
    "OpFunction","OpFunctionEnd","OpControlBarrier","OpMemoryBarrier",
    "OpCopyMemory","OpCopyMemorySized","OpSelectionMerge","OpLoopMerge"})
MAX_DEPTH=12

def authenticated_spv_CB_index_pointer_origins(dis:bytes,authenticated:dict)->dict:
    if not isinstance(dis,bytes) or not 0<len(dis)<=MAX_SPV_TEXT_BYTES or not isinstance(authenticated,dict):
        raise ValueError("GFX075_INVALID_INPUT")
    lines=dis.decode("utf8","strict").splitlines()
    if len(lines)>MAX_LINES:raise ValueError("GFX075_TOO_MANY_LINES")
    defs={};records=[];types=set()
    for raw in lines:
        raw=raw.split(";",1)[0].strip()
        if not raw:continue
        m=ASSIGN.fullmatch(raw)
        if m:
            ident,op,tail=m.groups()
            if ident in defs:raise ValueError("GFX075_DUPLICATE_SSA_ID")
            a=(tail or "").split()
            defs[ident]=(op,a)
            records.append((ident,op,a))
            if op=="OpTypeInt" and a in (["32","0"],["32","1"]):types.add(ident)
        else:
            a=raw.split()
            if not a or not re.fullmatch(r"Op[A-Za-z0-9_]+",a[0]):
                raise ValueError("GFX075_INVALID_SPV_OPCODE_SYNTAX")
            records.append((None,a[0],a[1:]))
    constants={}
    for ident,(op,a) in defs.items():
        if op=="OpConstant" and len(a)==2 and a[0] in types:
            try:constants[ident]=int(a[1],0)
            except ValueError:
                try:constants[ident]=int(a[1],10)
                except ValueError:pass
        if op=="OpConstantNull" and len(a)==1 and a[0] in types:
            constants[ident]=0
    def idx(t):
        if t in constants:return ("literal",constants[t])
        op,a=defs.get(t,(None,[]))
        if op is not None and op not in {"OpConstant","OpConstantNull","OpUndef",
              "OpSpecConstant","OpSpecConstantOp","OpSpecConstantComposite"} and a and a[0] in types:
            return ("dynamic",None)
        return ("unknown",None)
    def source_index_load(t):
        def from_bitcast(x):
            op,a=defs.get(x,(None,[]))
            if op!="OpBitcast" or len(a)!=2 or a[0] not in types:return None
            root,ra=defs.get(a[1],(None,[]))
            return a[1] if root=="OpLoad" and len(ra)>=2 else None
        direct=from_bitcast(t)
        if direct:return direct
        op,a=defs.get(t,(None,[]))
        if op=="OpIAdd" and len(a)==3 and a[0] in types:
            for lit,other in ((a[1],a[2]),(a[2],a[1])):
                if idx(lit)[0]=="literal":
                    root=from_bitcast(other)
                    if root:return root
        return None
    def pointer_origin(t):
        """Safe anonymous shape only. No pointer ID or private original b emitted."""
        seen=set();hops=0;chain=0;has_dynamic=False
        direct=defs.get(t,(None,[]))[0]
        while hops<MAX_DEPTH and t not in seen:
            seen.add(t);hops+=1
            op,a=defs.get(t,(None,[]))
            if op=="OpVariable" and len(a)>=2:
                storage=a[1] if a[1] in SAFE_STORAGES else "other"
                return (direct or "missing",storage,"dynamic" if has_dynamic else "literal",chain)
            if op in ("OpAccessChain","OpInBoundsAccessChain","OpPtrAccessChain") and len(a)>=3:
                has_dynamic|=any(idx(x)[0]!="literal" for x in a[2:])
                chain+=1;t=a[1];continue
            if op=="OpCopyObject" and len(a)==2:
                t=a[1];continue
            break
        return (direct or "missing","unresolved","unresolved",chain)
    # Only address chains authenticated to original b Uniform globals with vec4-array member 0.
    cbptr={};stored={};indexload={};c=Counter();block=None
    for name,op,a in records:
        if op=="OpLabel":
            block=name;stored.clear()
            continue
        if op in BLOCK_BARRIERS or op.startswith("OpAtomic"):
            stored.clear()
            if op in ("OpFunction","OpFunctionEnd"):block=None
            continue
        if op=="OpStore":
            if len(a)>=2 and block is not None:
                stored[a[0]]=(block,a[1])
            continue
        if name and op=="OpLoad":
            if len(a)<2:raise ValueError("GFX075_MALFORMED_LOAD")
            ptr=a[1]
            kind,storage,index_shape,depth=pointer_origin(ptr)
            exact=(ptr in stored and stored[ptr][0]==block and block is not None)
            # Store prior in same block with identical SSA pointer id; alias freedom NOT proven.
            indexload[name]=(kind,storage,index_shape,depth,exact)
        if name and op in ("OpAccessChain","OpInBoundsAccessChain") and len(a)>=3:
            parentid=a[1]
            if parentid in authenticated:
                info=authenticated[parentid]
                if (not isinstance(info,tuple) or len(info)!=4 or
                    any(type(v)!=int for v in info) or info[1]!=0 or
                    info[2]!=16 or info[3]<=0):
                    raise ValueError("GFX075_INVALID_AUTHENTICATED_ORIGINAL_B_UBO_LAYOUT")
                parent=("root",info[3],None)
            elif parentid in cbptr:parent=cbptr[parentid]
            else:continue
            shape,length,oldidx=parent
            indices=a[2:]
            if shape=="root":
                if not indices or idx(indices[0])!=("literal",0):
                    c["SPV_bad_UBO_struct_member"]+=1
                    continue
                indices=indices[1:]
                if not indices:
                    cbptr[name]=("array",length,None)
                    continue
            elif shape=="vector":
                if len(indices)==1 and idx(indices[0])[0]=="literal":
                    val=idx(indices[0])[1]
                    if 0<=val<4:cbptr[name]=("scalar",length,oldidx)
                continue
            elif shape!="array":continue
            if len(indices) not in (1,2):continue
            if idx(indices[0])[0]!="dynamic":continue
            if len(indices)==2:
                ch=idx(indices[1])
                if ch[0]!="literal" or not 0<=ch[1]<4:continue
                cbptr[name]=("scalar",length,indices[0])
            else:cbptr[name]=("vector",length,indices[0])
        elif name and op=="OpCopyObject" and len(a)==2 and a[1] in cbptr:
            cbptr[name]=cbptr[a[1]]
        if op=="OpLoad" and len(a)>=2 and a[1] in cbptr:
            shape,length,index=cbptr[a[1]]
            if shape not in ("scalar","vector"):continue
            c["SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"]+=1
            root=source_index_load(index) if index else None
            if root not in indexload:
                c["SPV_index_OpLoad_pointer_root_unclassified"]+=1;continue
            kind,storage,index_shape,depth,exact=indexload[root]
            c["SPV_index_OpLoad_pointer_root_classified"]+=1
            clean_kind=kind if kind in {"OpVariable","OpAccessChain","OpInBoundsAccessChain",
                "OpPtrAccessChain","OpCopyObject","OpPhi","OpSelect","OpFunctionParameter"} else "other"
            c["SPV_index_pointer_direct_definition_"+clean_kind]+=1
            c["SPV_index_pointer_root_storage_"+storage]+=1
            c["SPV_index_pointer_root_index_shape_"+index_shape]+=1
            c["SPV_index_pointer_traversed_AccessChain_count_total"]+=depth
            if exact:c["SPV_same_block_prior_OpStore_exact_pointer_ID_candidates"]+=1
            else:c["SPV_no_same_block_prior_OpStore_exact_pointer_ID_proven"]+=1
    if c["SPV_original_b_authenticated_actual_dynamic_CB_OpLoads"] != (
        c["SPV_index_OpLoad_pointer_root_classified"]+
        c["SPV_index_OpLoad_pointer_root_unclassified"]):
        raise ValueError("GFX075_AUTHENTIC_DYNAMIC_INDEX_PARTITION_DRIFT")
    n=c["SPV_index_OpLoad_pointer_root_classified"]
    for prefix in ("SPV_index_pointer_direct_definition_",
        "SPV_index_pointer_root_storage_","SPV_index_pointer_root_index_shape_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=n:
            raise ValueError("GFX075_ANONYMOUS_POINTER_ORIGIN_PARTITION_DRIFT")
    if c["SPV_same_block_prior_OpStore_exact_pointer_ID_candidates"]+c[
            "SPV_no_same_block_prior_OpStore_exact_pointer_ID_proven"]!=n:
        raise ValueError("GFX075_SOURCE_PTR_EXACT_STORE_ACCOUNTING_DRIFT")
    return {**dict(c),
       "SPV_exact_pointer_ID_prior_Store_means_aliased_memory_value_proven":False,
       "SPV_pointer_origin_shape_proves_original_DXBC_temp_provenance":False,
       "SPV_storage_class_means_full_CFG_dominance_or_runtime_bounds":False,
       "original_Shader48_Material_CB_register_byte_semantics_proven":False,
       "originalShaderRestored":False,
       "phase_closed":False}
