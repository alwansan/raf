#!/usr/bin/env python3
"""GFX070: read-only SPIR-V Uniform CB OpLoad index expression diagnostics.

This tests a genuine translated SPIR-V dynamic vector index's OWN SSA ancestor
for OpShiftLeftLogical. It never identifies the originating DXBC temporary,
does not prove CFG dominance or source↔SPV semantic parity, and cannot establish
runtime bounds / actual GPU pixels. All SPIR-V IDs, source b numbers and
per-shader identifiers remain private to the CI runner.
"""
from __future__ import annotations
import re
from collections import Counter

MAX_SPV_TEXT_BYTES=16*1024*1024
MAX_LINES=300000
MAX_ANCESTOR_DEPTH=32
ASSIGN=re.compile(r"^\s*(%[0-9]+)\s*=\s*(Op[A-Za-z0-9_]+)(?:\s+(.*))?$")
BINARY={"OpIAdd","OpISub","OpBitwiseAnd","OpBitwiseOr","OpBitwiseXor",
        "OpShiftRightLogical","OpShiftRightArithmetic"}
UNARY={"OpUConvert","OpSConvert","OpBitcast","OpCopyObject"}
UNTRUSTED_FANIN={"OpPhi","OpSelect","OpFunctionCall","OpSpecConstantOp"}
UNSUPPORTED_CONSTANTS={"OpSpecConstant","OpSpecConstantOp",
                       "OpSpecConstantComposite","OpUndef"}

def shifted_source_spv_dynamic_UBO_reads(dis:bytes,authenticated:dict):
    """Return safe counts. Every reported CB load requires source b-authenticated
    global, member 0, 16-byte vec4 array layout, dynamic int32 index and OpLoad.

    Untrusted Phi/Select alias, non-vector member or unsupported index is not
    promoted to a positive shift-dependent read.
    """
    if not isinstance(dis,bytes) or not 0<len(dis)<=MAX_SPV_TEXT_BYTES or not isinstance(authenticated,dict):
        raise ValueError("GFX070_SPV_INPUT_INVALID")
    lines=dis.decode("utf8","strict").splitlines()
    if len(lines)>MAX_LINES:raise ValueError("GFX070_SPV_LINES_LIMIT")
    defs={}
    int32=set()
    for raw in lines:
        m=ASSIGN.fullmatch(raw.split(";",1)[0].strip())
        if not m:continue
        ident,op,tail=m.groups()
        if ident in defs:raise ValueError("GFX070_DUPLICATE_SPV_RESULT_ID")
        args=(tail or "").split()
        defs[ident]=(op,args)
        if op=="OpTypeInt" and args in (["32","0"],["32","1"]):
            int32.add(ident)
    constants={}
    for ident,(op,args) in defs.items():
        if op=="OpConstant" and len(args)==2 and args[0] in int32:
            try:constants[ident]=int(args[1],0)
            except ValueError:
                try:constants[ident]=int(args[1],10)
                except ValueError:pass
        elif op=="OpConstantNull" and len(args)==1 and args[0] in int32:
            constants[ident]=0

    def idx_kind(ident):
        if ident in constants:return ("literal",constants[ident])
        op,args=defs.get(ident,(None,[]))
        if (op is not None and op not in UNSUPPORTED_CONSTANTS and
            op not in ("OpConstant","OpConstantNull") and args and args[0] in int32):
            return ("dynamic",None)
        return ("unproven",None)

    def shift_ancestor(ident,seen=None,depth=0):
        """Pure SSA def-use, *not* correspondence to any original DXBC register."""
        if seen is None:seen=frozenset()
        if depth>MAX_ANCESTOR_DEPTH or ident in seen:
            return "unproven"
        if ident in constants:return "no_shift"
        op,args=defs.get(ident,(None,[]))
        if op is None or op in UNTRUSTED_FANIN:
            return "unproven"
        if op=="OpShiftLeftLogical":
            return "direct_shift" if len(args)==3 and args[0] in int32 else "unproven"
        if op in UNARY and len(args)==2:
            return shift_ancestor(args[1],seen|{ident},depth+1)
        if op in BINARY and len(args)==3 and args[0] in int32:
            values=[shift_ancestor(t,seen|{ident},depth+1) for t in args[1:]]
            if any(v in ("direct_shift","via_shift") for v in values):
                return "via_shift"
            return "unproven" if "unproven" in values else "no_shift"
        # OpLoad may supply an index but its source is runtime storage,
        # and must not imply a preceding shift.
        return "unproven"

    # State is (source_authenticated_root, array_length, kind, vector_index_id).
    pointers={}
    c=Counter({
      "SPV_authenticated_global_access_chains":0,
      "SPV_authenticated_dynamic_vec_index_pointers":0,
      "SPV_authenticated_dynamic_vec_OpLoad_occurrences":0,
      "SPV_dynamic_vec_OpLoad_index_direct_shift":0,
      "SPV_dynamic_vec_OpLoad_index_via_shift_ancestor":0,
      "SPV_dynamic_vec_OpLoad_index_with_no_proven_shift":0,
      "SPV_dynamic_vec_OpLoad_index_unproven_expression":0,
      "SPV_bad_authentic_UBO_layout_rejected":0,
      "SPV_invalid_struct_member_or_index_path":0,
      "SPV_dynamic_vec_pointers_without_OpLoad":0,
      "SPV_unproven_phi_or_select_pointer_alias":0,
    })
    used_pointer_ids=set()
    dynamic_pointer_ids=set()
    for raw in lines:
        m=ASSIGN.fullmatch(raw.split(";",1)[0].strip())
        if not m:continue
        ident,op,tail=m.groups()
        a=(tail or "").split()
        if op in ("OpAccessChain","OpInBoundsAccessChain") and len(a)>=3:
            parent_id=a[1]
            if parent_id in authenticated:
                info=authenticated[parent_id]
                if (not isinstance(info,tuple) or len(info)!=4 or
                    any(type(v)!=int for v in info) or
                    info[1]!=0 or info[2]!=16 or info[3]<=0):
                    raise ValueError("GFX070_INVALID_AUTHENTICATED_CB_GLOBAL_LAYOUT")
                parent=(parent_id,info[3],"root",None)
                c["SPV_authenticated_global_access_chains"]+=1
            elif parent_id in pointers:
                parent=pointers[parent_id]
            else:continue
            root,length,kind,_=parent
            indices=a[2:]
            if kind=="root":
                if idx_kind(indices[0])!=("literal",0):
                    c["SPV_invalid_struct_member_or_index_path"]+=1;continue
                indices=indices[1:]
                if not indices:
                    pointers[ident]=(root,length,"array",None)
                    continue
            elif kind=="array":
                pass
            elif kind=="vector":
                if len(indices)==1 and idx_kind(indices[0])[0]=="literal" and 0<=idx_kind(indices[0])[1]<4:
                    pointers[ident]=(root,length,"scalar",parent[3])
                    dynamic_pointer_ids.add(ident)
                else:c["SPV_invalid_struct_member_or_index_path"]+=1
                continue
            else:continue
            if len(indices) not in (1,2):
                c["SPV_invalid_struct_member_or_index_path"]+=1;continue
            vector_id=indices[0]
            k,v=idx_kind(vector_id)
            if k=="literal":
                if not 0<=v<length:c["SPV_invalid_struct_member_or_index_path"]+=1
                continue
            if k!="dynamic":
                c["SPV_invalid_struct_member_or_index_path"]+=1;continue
            if len(indices)==2:
                component_k,component_v=idx_kind(indices[1])
                if component_k!="literal" or not 0<=component_v<4:
                    c["SPV_invalid_struct_member_or_index_path"]+=1;continue
                pkind="scalar"
            else:pkind="vector"
            pointers[ident]=(root,length,pkind,vector_id)
            dynamic_pointer_ids.add(ident)
            c["SPV_authenticated_dynamic_vec_index_pointers"]+=1
        elif op=="OpCopyObject" and len(a)==2 and a[1] in pointers:
            pointers[ident]=pointers[a[1]]
            if pointers[ident][2] in ("scalar","vector"):
                dynamic_pointer_ids.add(ident)
        elif op=="OpLoad" and len(a)>=2:
            ptr=a[1]
            if ptr not in pointers or pointers[ptr][2] not in ("scalar","vector"):
                continue
            used_pointer_ids.add(ptr)
            c["SPV_authenticated_dynamic_vec_OpLoad_occurrences"]+=1
            result=shift_ancestor(pointers[ptr][3])
            if result=="direct_shift":
                c["SPV_dynamic_vec_OpLoad_index_direct_shift"]+=1
            elif result=="via_shift":
                c["SPV_dynamic_vec_OpLoad_index_via_shift_ancestor"]+=1
            elif result=="no_shift":
                c["SPV_dynamic_vec_OpLoad_index_with_no_proven_shift"]+=1
            else:c["SPV_dynamic_vec_OpLoad_index_unproven_expression"]+=1
        elif op in ("OpPhi","OpSelect") and any(k in pointers for k in a):
            c["SPV_unproven_phi_or_select_pointer_alias"]+=1
    c["SPV_dynamic_vec_pointers_without_OpLoad"]=len(dynamic_pointer_ids-used_pointer_ids)
    if c["SPV_authenticated_dynamic_vec_OpLoad_occurrences"]!=sum(c[k] for k in (
        "SPV_dynamic_vec_OpLoad_index_direct_shift",
        "SPV_dynamic_vec_OpLoad_index_via_shift_ancestor",
        "SPV_dynamic_vec_OpLoad_index_with_no_proven_shift",
        "SPV_dynamic_vec_OpLoad_index_unproven_expression",
    )):
        raise ValueError("GFX070_DYNAMIC_UBO_LOAD_PARTITION_INVALID")
    return {
      **dict(c),
      "SPV_dynamic_shift_ancestor_means_same_original_DXBC_ISHL":False,
      "SPV_dynamic_shift_ancestor_means_original_CB_numeric_index_parity":False,
      "original_source_temp_to_SPV_SSA_global_mapping_proven":False,
      "spv_full_runtime_CB_bounds_proven":False,
    }
