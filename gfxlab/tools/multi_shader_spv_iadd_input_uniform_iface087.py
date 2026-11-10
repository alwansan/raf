#!/usr/bin/env python3
"""GFX087: original-source-private Input Location and Uniform Binding/Block/Member Offset presence for 24 SPV OpIAdd input OpLoads.

Source-private SPV result IDs, original b-register IDs and dereferenced pointer
names never leave CI. Same SSA pointer-id store-before-load is syntax only, not
alias-free runtime dataflow or DXBC source-temp correspondence.
"""
from __future__ import annotations
import re
from collections import Counter
from gfxlab.tools.multi_shader_spv_index_root_taxonomy071 import ASSIGN, MAX_SPV_TEXT_BYTES, MAX_LINES
from gfxlab.tools.multi_shader_spv_cfg_dominance078 import StrictSpvBlockCfg

SAFE_STORAGES=frozenset({"Function","Private","Input","Output","Uniform",
                         "StorageBuffer","Workgroup","PushConstant","UniformConstant"})
BLOCK_BARRIERS=frozenset({"OpBranch","OpBranchConditional","OpSwitch","OpKill",
    "OpReturn","OpReturnValue","OpUnreachable","OpFunctionCall",
    "OpFunction","OpFunctionEnd","OpControlBarrier","OpMemoryBarrier",
    "OpCopyMemory","OpCopyMemorySized","OpSelectionMerge","OpLoopMerge"})
MAX_DEPTH=12

def authenticated_spv_CB_index_iadd_load_interfaces087(dis:bytes,authenticated:dict)->dict:
    if not isinstance(dis,bytes) or not 0<len(dis)<=MAX_SPV_TEXT_BYTES or not isinstance(authenticated,dict):
        raise ValueError("GFX087_INVALID_INPUT")
    lines=dis.decode("utf8","strict").splitlines()
    if len(lines)>MAX_LINES:raise ValueError("GFX087_TOO_MANY_LINES")
    defs={};records=[];types=set()
    for raw in lines:
        raw=raw.split(";",1)[0].strip()
        if not raw:continue
        m=ASSIGN.fullmatch(raw)
        if m:
            ident,op,tail=m.groups()
            if ident in defs:raise ValueError("GFX087_DUPLICATE_SSA_ID")
            a=(tail or "").split()
            defs[ident]=(op,a)
            records.append((ident,op,a))
            if op=="OpTypeInt" and a in (["32","0"],["32","1"]):types.add(ident)
        else:
            a=raw.split()
            if not a or not re.fullmatch(r"Op[A-Za-z0-9_]+",a[0]):
                raise ValueError("GFX087_INVALID_SPV_OPCODE_SYNTAX")
            records.append((None,a[0],a[1:]))
    # SPIR-V public interface decorations parsed once per stage. Private
    # location/binding/offset numeric values and variable IDs never leave CI.
    decorations={};member_offsets=set()
    for _,op,a in records:
        if op=="OpDecorate" and len(a)>=2:
            key=(a[0],a[1])
            values=decorations.setdefault(key,set())
            # Preserve raw private arguments only within local memory.
            values.add(tuple(a[2:]))
        elif op=="OpMemberDecorate" and len(a)>=4 and a[2]=="Offset":
            if a[1].isdigit() and a[3].isdigit():
                member_offsets.add((a[0],int(a[1])))
    def valid_decor(target,kind):
        values=decorations.get((target,kind),set())
        if len(values)!=1:return False
        val=next(iter(values))
        return len(val)==1 and val[0].isdigit()
    def safe_pointer_path(ptr):
        """One private root Variable + bounded composite index path."""
        visited=set();indices=[];shape="direct";cur=ptr
        for _ in range(MAX_DEPTH):
            if cur in visited:return None,(),"unresolved_cycle"
            visited.add(cur)
            op,a=defs.get(cur,(None,[]))
            if op=="OpVariable" and len(a)>=2:return cur,tuple(indices),"direct" if shape=="direct" else shape
            if op in ("OpInBoundsAccessChain","OpAccessChain") and len(a)>=3:
                seq=[idx(x) for x in a[2:]]
                if any(k=="unknown" for k,_ in seq):shape="unresolved_indices"
                elif any(k=="dynamic" for k,_ in seq):shape="dynamic_indices"
                elif shape=="direct":shape="literal_indices"
                indices=[*seq,*indices]
                cur=a[1];continue
            if op=="OpCopyObject" and len(a)==2:
                cur=a[1];continue
            return None,(),"unresolved_pointer"
        return None,(),"depth_exceeded"
    def classify_input_uniform_interface(load_id):
        """Public enum-only summary; never proof of Material/CB byte binding."""
        if load_id is None:return ("not_load","not_load","not_load","not_load","not_load")
        op,a=defs.get(load_id,(None,[]))
        if op!="OpLoad" or len(a)!=2:return ("untrusted_load","untrusted_load","untrusted_load","untrusted_load","untrusted_load")
        root,steps,path_shape=safe_pointer_path(a[1])
        if root is None:return (path_shape,"unresolved","unresolved","unresolved","unresolved")
        vop,va=defs.get(root,(None,[]))
        if vop!="OpVariable" or len(va)<2:
            return ("unresolved_root","unresolved","unresolved","unresolved","unresolved")
        storage=va[1]
        if storage=="Input":
            loc=valid_decor(root,"Location")
            builtin=valid_decor(root,"BuiltIn") or (root,"BuiltIn") in decorations
            input_class=("location_and_builtin_conflict" if loc and builtin
                         else "location_only" if loc else
                         "builtin_only" if builtin else "no_direct_location_or_builtin")
        else:input_class="not_Input"
        if storage=="Uniform":
            binding=valid_decor(root,"Binding")
            descriptor=valid_decor(root,"DescriptorSet")
            bind_class=("binding_and_set" if binding and descriptor else
                       "binding_only" if binding else
                       "set_only" if descriptor else "no_direct_binding_or_set")
        else:bind_class="not_Uniform"
        ptr_op,ptr_args=defs.get(va[0],(None,[]))
        if ptr_op!="OpTypePointer" or len(ptr_args)!=2:
            return (path_shape,input_class,bind_class,"unverified_pointer_type",
                    "unverified_member_path")
        curtype=ptr_args[1]
        block_class="not_Uniform"
        member_class="not_Uniform"
        if storage=="Uniform":
            block=bool(decorations.get((curtype,"Block")))
            bufblock=bool(decorations.get((curtype,"BufferBlock")))
            type_op,type_a=defs.get(curtype,(None,[]))
            block_class=("Block" if block and not bufblock else
                         "BufferBlock" if bufblock and not block else
                         "conflicting_block_decorations" if block and bufblock else
                         "struct_without_block" if type_op=="OpTypeStruct" else
                         "not_struct_or_missing_type")
            member_class="no_selected_struct_member"
            if path_shape in ("unresolved_indices","dynamic_indices"):
                member_class="unverified_dynamic_index"
            else:
                for k,val in steps:
                    if k!="literal" or not isinstance(val,int):
                        member_class="unverified_index";break
                    inner_op,inner_args=defs.get(curtype,(None,[]))
                    if inner_op=="OpTypeStruct":
                        if val<0 or val>=len(inner_args):
                            member_class="invalid_member_index";break
                        member_class=("selected_member_has_offset" if
                          (curtype,val) in member_offsets else
                          "selected_member_without_proven_offset")
                        curtype=inner_args[val]
                    elif inner_op in ("OpTypeArray","OpTypeRuntimeArray",
                                     "OpTypeVector","OpTypeMatrix"):
                        if not inner_args:member_class="invalid_composite_type";break
                        curtype=inner_args[0]
                    else:
                        member_class="unverified_composite_path";break
        return path_shape,input_class,bind_class,block_class,member_class
    cfg=StrictSpvBlockCfg(records)
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
    def function_literal_address_path(t):
        """Source-private normalized Function root and constant access path.

        The returned tuple embeds original SPV IDs and literal indices; NEVER
        print/export it. Equivalent syntax is not CFG dominance or alias freedom.
        """
        seen=set();parts=[]
        for _ in range(MAX_DEPTH):
            if t in seen:return None
            seen.add(t)
            op,a=defs.get(t,(None,[]))
            if op=="OpVariable" and len(a)>=2 and a[1]=="Function":
                return (t,tuple(v for part in reversed(parts) for v in part))
            if op in ("OpInBoundsAccessChain","OpAccessChain") and len(a)>=3:
                indices=[idx(x) for x in a[2:]]
                if any(k!="literal" or type(v)!=int for k,v in indices):return None
                parts.append(tuple(v for _,v in indices))
                t=a[1];continue
            if op=="OpCopyObject" and len(a)==2:
                t=a[1];continue
            return None
        return None
    def store_value_provenance(t):
        """Bounded SPV SSA-only syntax. Never original DXBC temp equivalence."""
        op,a=defs.get(t,(None,[]))
        allow={"OpShiftLeftLogical","OpIAdd","OpISub","OpBitcast",
               "OpCopyObject","OpCompositeConstruct","OpCompositeExtract",
               "OpLoad","OpConstant","OpConstantNull","OpPhi","OpSelect"}
        producer=op if op in allow else "other"
        unary={"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"}
        binary={"OpIAdd","OpISub","OpBitwiseAnd","OpBitwiseOr","OpBitwiseXor",
                "OpShiftRightLogical","OpShiftRightArithmetic"}
        def walk(x,seen,depth):
            if depth>MAX_DEPTH or x in seen:return "unknown"
            o,ar=defs.get(x,(None,[]))
            if o=="OpShiftLeftLogical" and len(ar)==3:return "shift"
            if o in ("OpConstant","OpConstantNull") and len(ar) in (1,2):return "no_shift"
            if o in unary and len(ar)==2:
                return walk(ar[1],seen|{x},depth+1)
            if o in binary and len(ar)==3:
                res=[walk(ar[1],seen|{x},depth+1),walk(ar[2],seen|{x},depth+1)]
                if "shift" in res:return "shift"
                return "unknown" if "unknown" in res else "no_shift"
            return "unknown"
        ancestry=walk(t,frozenset(),0)
        if ancestry=="shift":
            ancestry="direct_shift" if op=="OpShiftLeftLogical" else "via_shift"
        return producer,ancestry
    def public_terminal_family(op):
        """Standard SPIR-V opcode category only; never return proprietary IDs."""
        groups={
          "integer_math":{"OpIAdd","OpISub","OpIMul","OpUDiv","OpSDiv",
                          "OpUMod","OpSRem","OpSMod","OpSNegate",
                          "OpUClamp","OpSClamp","OpUMin","OpSMin",
                          "OpUMax","OpSMax","OpIAddCarry","OpISubBorrow",
                          "OpUMulExtended","OpSMulExtended"},
          "float_math":{"OpFAdd","OpFSub","OpFMul","OpFDiv",
                        "OpFRem","OpFMod","OpFNegate","OpDot",
                        "OpMatrixTimesVector","OpVectorTimesScalar",
                        "OpMatrixTimesScalar","OpVectorTimesMatrix",
                        "OpMatrixTimesMatrix","OpOuterProduct","OpTranspose"},
          "integer_bitwise":{"OpBitwiseAnd","OpBitwiseOr","OpBitwiseXor",
                             "OpShiftLeftLogical","OpShiftRightLogical",
                             "OpShiftRightArithmetic","OpNot","OpBitFieldInsert",
                             "OpBitFieldSExtract","OpBitFieldUExtract",
                             "OpBitReverse","OpBitCount"},
          "conversion":{"OpBitcast","OpUConvert","OpSConvert","OpFConvert",
                        "OpConvertFToU","OpConvertFToS",
                        "OpConvertSToF","OpConvertUToF",
                        "OpConvertPtrToU","OpConvertUToPtr",
                        "OpSatConvertSToU","OpSatConvertUToS",
                        "OpQuantizeToF16","OpConvertUToAccelerationStructureKHR"},
          "vector_composite":{"OpVectorShuffle","OpVectorExtractDynamic",
                              "OpVectorInsertDynamic","OpCompositeExtract",
                              "OpCompositeInsert","OpCompositeConstruct",
                              "OpCopyObject","OpTranspose"},
          "logical_comparison":{"OpIEqual","OpINotEqual","OpULessThan",
                                "OpSLessThan","OpULessThanEqual",
                                "OpSLessThanEqual","OpUGreaterThan",
                                "OpSGreaterThan","OpULessThanEqual",
                                "OpSGreaterThanEqual","OpUGreaterThanEqual",
                                "OpFOrdEqual","OpFUnordEqual","OpFOrdLessThan",
                                "OpFUnordLessThan","OpLogicalAnd","OpLogicalOr",
                                "OpLogicalEqual","OpLogicalNotEqual","OpLogicalNot",
                                "OpAny","OpAll","OpIsNan","OpIsInf"},
          "memory":{"OpLoad","OpAtomicLoad","OpImageRead",
                    "OpImageFetch","OpImageSampleImplicitLod",
                    "OpImageSampleExplicitLod","OpImageGather",
                    "OpImageDrefGather","OpImageSparseFetch"},
          "control_merge":{"OpPhi","OpSelect","OpFunctionCall"},
          "extension_intrinsic":{"OpExtInst","OpExtInstWithForwardRefsKHR"},
        }
        for family,names in groups.items():
            if op in names:return family
        return "other_public_opcode" if re.fullmatch(r"Op[A-Za-z0-9_]{1,80}",op or "") else "missing_or_invalid_opcode"
    def unknown_source_terminal(t):
        """Anonymous terminal opcode at end of bounded transparent SSA unary chain.

        Do not expose SPV IDs and never equate terminal syntax with runtime
        shader semantics or a specific original DXBC temporary.
        """
        seen=set()
        transparent={"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"}
        for _ in range(MAX_DEPTH):
            if t in seen:return "cycle"
            seen.add(t)
            op,args=defs.get(t,(None,[]))
            if op in transparent and len(args)==2:
                t=args[1]
                continue
            if op in ("OpLoad","OpPhi","OpSelect","OpCompositeExtract",
                      "OpCompositeConstruct","OpIAdd","OpISub",
                      "OpShiftLeftLogical","OpFunctionCall",
                      "OpUndef","OpSpecConstantOp","OpConstant"):
                return op
            if op is None:return "missing"
            return public_terminal_family(op)
        return "depth_exceeded"
    def private_integer_terminal_shape(t):
        """Safe public SPIR-V integer-op name + private literal category, no IDs.

        Recognizes a literal power of two for a 32-bit OpIMul operand as
        a mathematical bit-pattern form only. No source DXBC equivalence,
        CFG memory value or SPV runtime variable assignment is inferred.
        """
        transparent={"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"}
        seen=set()
        for _ in range(MAX_DEPTH):
            if t in seen:return "cycle","unproven"
            seen.add(t)
            op,a=defs.get(t,(None,[]))
            if op in transparent and len(a)==2:
                t=a[1]
                continue
            integer={"OpIAdd","OpISub","OpIMul","OpUDiv","OpSDiv",
                     "OpUMod","OpSRem","OpSMod","OpSNegate",
                     "OpIAddCarry","OpISubBorrow","OpUMulExtended",
                     "OpSMulExtended"}
            op_name=op if op in integer else "other_integer_terminal"
            if op!="OpIMul":
                return op_name,"not_imul"
            if len(a)!=3 or a[0] not in types:
                return op_name,"unverified_integer_width_or_arity"
            candidates=[]
            for operand in a[1:]:
                if operand in constants:
                    c=constants[operand]
                    if type(c) is not int or not -(2**31)<=c<2**32:
                        return op_name,"invalid_literal_range"
                    candidates.append((operand,c))
            if len(candidates)==2:return op_name,"both_constant_operands"
            if len(candidates)==0:return op_name,"no_proven_literal"
            literal_id,value=candidates[0]
            other=a[2] if literal_id==a[1] else a[1]
            other_op,other_args=defs.get(other,(None,[]))
            if (other_op in ("OpUndef","OpSpecConstant","OpSpecConstantOp") or
                not other_args or other_args[0] not in types):
                return op_name,"other_operand_type_or_origin_unproven"
            mask=value&0xffffffff
            if mask==0:return op_name,"literal_zero"
            if mask&(mask-1)==0:return op_name,"one_unsigned_power_of_two_literal"
            return op_name,"nonpower_of_two_literal"
        return "depth_exceeded","unproven"
    def imul_dynamic_operand_source(t):
        """Count-only classification of nonliteral OpIMul operand's bounded SSA.

        No private SPV IDs, pointer paths or original source constants escape.
        Transparent unary steps are only a syntax chain: the memory value or
        original DXBC temporary is NEVER proven.
        """
        seen=set()
        while len(seen)<MAX_DEPTH:
            if t in seen:return ("cycle","cycle","untrusted",None)
            seen.add(t)
            op,a=defs.get(t,(None,[]))
            if len(seen)==1:
                immediate=(op if op in {"OpLoad","OpBitcast","OpCopyObject",
                    "OpUConvert","OpSConvert","OpIAdd","OpISub","OpIMul",
                    "OpShiftLeftLogical","OpCompositeExtract","OpPhi","OpSelect",
                    "OpConstant","OpSpecConstant","OpUndef"} else "other")
            if op in {"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"} and len(a)==2:
                t=a[1];continue
            if op=="OpLoad":
                if len(a)!=2:return (immediate,"OpLoad","untrusted_memory_operands",None)
                _,storage,shape,depth=pointer_origin(a[1])
                if storage=="Function":
                    path=function_literal_address_path(a[1])
                    if path is not None:return (immediate,"OpLoad","Function_literal_path",t)
                    return (immediate,"OpLoad","Function_dynamic_or_unresolved_path",t)
                if storage in SAFE_STORAGES:
                    return (immediate,"OpLoad","other_storage_"+storage,t)
                return (immediate,"OpLoad","unknown_pointer_storage",t)
            terminal=op if op in {"OpPhi","OpSelect","OpCompositeExtract",
                "OpCompositeConstruct","OpIAdd","OpISub","OpIMul",
                "OpShiftLeftLogical","OpShiftRightLogical","OpShiftRightArithmetic",
                "OpBitwiseAnd","OpBitwiseOr","OpBitwiseXor","OpFunctionCall",
                "OpConstant","OpConstantNull","OpSpecConstant","OpSpecConstantOp",
                "OpUndef","OpFAdd","OpFMul"} else "other"
            return (immediate,terminal,"nonmemory_terminal",None)
        return (immediate if "immediate" in locals() else "other",
                "depth_exceeded","untrusted",None)
    def private_nonpower_imul_input(t):
        # Follow only transparent unary wrappers from SPV candidate Store value
        # to an exactly 32-bit integer OpIMul with a single non-power literal.
        seen=set()
        for _ in range(MAX_DEPTH):
            if t in seen:return None
            seen.add(t)
            op,a=defs.get(t,(None,[]))
            if op in {"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"} and len(a)==2:
                t=a[1];continue
            if op!="OpIMul" or len(a)!=3 or a[0] not in types:return None
            literals=[x for x in a[1:] if x in constants]
            if len(literals)!=1:return None
            v=constants[literals[0]]
            if type(v) is not int or not -(2**31)<=v<2**32:return None
            mask=v&0xffffffff
            if mask==0 or mask&(mask-1)==0:return None
            operand=a[2] if literals[0]==a[1] else a[1]
            return imul_dynamic_operand_source(operand)
        return None
    def immediate_public_op(t):
        op=defs.get(t,(None,[]))[0]
        # Return only standard/public SPV instruction names; no target IDs.
        allowed={"OpLoad","OpBitcast","OpCopyObject","OpCompositeExtract",
                 "OpCompositeInsert","OpCompositeConstruct","OpVectorShuffle",
                 "OpVectorExtractDynamic","OpVectorInsertDynamic","OpIAdd",
                 "OpISub","OpIMul","OpShiftLeftLogical","OpShiftRightLogical",
                 "OpShiftRightArithmetic","OpBitwiseAnd","OpBitwiseOr",
                 "OpBitwiseXor","OpSelect","OpPhi","OpFunctionCall",
                 "OpUConvert","OpSConvert","OpFConvert","OpConvertFToU",
                 "OpConvertFToS","OpConvertSToF","OpConvertUToF",
                 "OpFAdd","OpFMul","OpFSub","OpFDiv","OpExtInst",
                 "OpConstant","OpConstantNull","OpSpecConstant",
                 "OpSpecConstantOp","OpUndef","OpVariable"}
        return op if op in allowed else "missing_or_other"
    def prior_store_bitcast_source(t):
        """Public opcode-only inner SSA taxonomy for prior-Store value.

        Return anonymous enum labels, never raw SPV identifiers, vector lane,
        shader source bytes or private b/s register mapping. Composite source
        immediate opcode is syntax, not proof of component/value equality.
        """
        first,fa=defs.get(t,(None,[]))
        if first!="OpBitcast" or len(fa)!=2:return ("not_direct_OpBitcast","unknown","unverified")
        transparent={"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"}
        depth=0;seen=set()
        while depth<MAX_DEPTH:
            if t in seen:return ("cycle","unknown","unverified")
            seen.add(t)
            op,a=defs.get(t,(None,[]))
            if op in transparent and len(a)==2:
                t=a[1];depth+=1;continue
            terminal=immediate_public_op(t)
            if op=="OpCompositeExtract":
                if len(a)<3:return (terminal,"malformed_composite","unverified")
                # SPIR-V composite literal indices are numeric tokens; never export.
                if any(not re.fullmatch(r"[0-9]{1,10}",v) for v in a[2:]):
                    return (terminal,"nonliteral_or_malformed_component","unverified")
                source=immediate_public_op(a[1])
                detail=("one_literal_component" if len(a)==3 else
                        "multiple_literal_components")
                source_class=("composite_source_"+source if source in
                    {"OpLoad","OpCompositeConstruct","OpCompositeExtract",
                     "OpVectorShuffle","OpPhi","OpSelect","OpUndef","OpConstant"}
                    else "composite_source_other")
                return (terminal,detail,source_class)
            if op=="OpVectorShuffle":
                if len(a)<5:return (terminal,"malformed_shuffle","unverified")
                # Operand selectors remain CI-private; publish only operation class.
                return (terminal,"vector_shuffle","source_class_unproven")
            if op=="OpLoad":
                if len(a)!=2:return (terminal,"untrusted_memory_access","unverified")
                _,storage,shape,hops=pointer_origin(a[1])
                if storage=="Function":
                    p=function_literal_address_path(a[1])
                    detail=("Function_literal_pointer" if p is not None else
                            "Function_unresolved_pointer")
                elif storage in SAFE_STORAGES:
                    detail="other_storage_"+storage
                else:detail="unknown_pointer_storage"
                return (terminal,detail,"memory_reaching_value_unproven")
            if op in ("OpPhi","OpSelect","OpFunctionCall"):
                return (terminal,"control_or_call_merge","unproven")
            if op in ("OpIAdd","OpISub","OpIMul","OpShiftLeftLogical",
                      "OpShiftRightLogical","OpShiftRightArithmetic",
                      "OpBitwiseAnd","OpBitwiseOr","OpBitwiseXor"):
                return (terminal,"integer_arithmetic","source_ancestry_unproven")
            if op in ("OpFAdd","OpFSub","OpFMul","OpFDiv"):
                return (terminal,"float_arithmetic","source_ancestry_unproven")
            if op in ("OpConstant","OpConstantNull","OpUndef","OpSpecConstant",
                      "OpSpecConstantOp"):
                return (terminal,"constant_or_undef","source_ancestry_unproven")
            return (terminal,"other_or_unverified_opcode","unproven")
        return ("depth_exceeded","unknown","unverified")
    def source_inner_iadd_operands(t):
        """Anonymous source operand opcode/constant shape behind Store Bitcast.

        Counts only syntactic SPIR-V result definitions, not memory values,
        source DXBC temp IDs or runtime equivalence. Returns no raw operands.
        """
        seen=set()
        for _ in range(MAX_DEPTH):
            if t in seen:return ("cycle","unknown","unknown","unverified")
            seen.add(t)
            op,a=defs.get(t,(None,[]))
            if op in {"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"} and len(a)==2:
                t=a[1];continue
            if op!="OpIAdd" or len(a)!=3 or a[0] not in types:
                return ("not_verified_32bit_OpIAdd","unknown","unknown","unverified")
            def one(x):
                if x in constants:
                    return ("constant_zero" if constants[x]==0 else "constant_nonzero"),"constant"
                cur=x;visited=set()
                for _ in range(MAX_DEPTH):
                    if cur in visited:return "cycle","unknown"
                    visited.add(cur)
                    oper,params=defs.get(cur,(None,[]))
                    if oper in {"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"} and len(params)==2:
                        cur=params[1];continue
                    return "dynamic","source_"+immediate_public_op(cur)
                return "depth_exceeded","unknown"
            acls,asrc=one(a[1]);bcls,bsrc=one(a[2])
            key=("_".join(sorted((acls,bcls))) if
                 acls in {"constant_zero","constant_nonzero","dynamic"} and
                 bcls in {"constant_zero","constant_nonzero","dynamic"} else
                 "unverified")
            return key,asrc,bsrc,"verified_32bit_scalar_integer_opcode"
        return ("depth_exceeded","unknown","unknown","unverified")
    def iadd_operand_read_roots(t):
        """Source-private true OpLoad result IDs for two SPV OpIAdd inputs.

        These IDs are used only inside this Python process to inspect each
        OpLoad's own read-time snapshot; they are never written to artifacts.
        """
        def transparent(x):
            seen=set()
            for _ in range(MAX_DEPTH):
                if x in seen:return None
                seen.add(x)
                op,a=defs.get(x,(None,[]))
                if op in {"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"} and len(a)==2:
                    x=a[1];continue
                return x if op=="OpLoad" else None
            return None
        seen=set()
        for _ in range(MAX_DEPTH):
            if t in seen:return (None,None)
            seen.add(t)
            op,a=defs.get(t,(None,[]))
            if op in {"OpBitcast","OpCopyObject","OpUConvert","OpSConvert"} and len(a)==2:
                t=a[1];continue
            if op!="OpIAdd" or len(a)!=3 or a[0] not in types:return (None,None)
            return transparent(a[1]),transparent(a[2])
        return (None,None)
    def load_memory_storage_shape(load_id):
        if load_id is None:return "not_OpLoad","not_OpLoad"
        op,a=defs.get(load_id,(None,[]))
        if op!="OpLoad" or len(a)!=2:return "untrusted_or_malformed","untrusted_or_malformed"
        pointer=a[1]
        _,storage,shape,depth=pointer_origin(pointer)
        if storage=="Function":
            ptr_class=("Function_literal_address" if
                       function_literal_address_path(pointer) is not None else
                       "Function_nonliteral_or_unresolved_address")
        elif storage in SAFE_STORAGES:
            ptr_class="storage_"+storage
        else:ptr_class="unresolved_pointer"
        prior_class=memory_read_state.get(load_id,("unobserved_OpLoad",None))[0]
        return ptr_class,prior_class
    # Only address chains authenticated to original b Uniform globals with vec4-array member 0.
    cbptr={};stored={};indexload={};c=Counter();block=None;window_store={};historical_store={};memory_read_state={}
    for name,op,a in records:
        if op=="OpLabel":
            block=name;stored.clear();window_store.clear()
            continue
        if op in BLOCK_BARRIERS or op.startswith("OpAtomic"):
            stored.clear();window_store.clear()
            if op not in ("OpBranch","OpBranchConditional","OpSwitch",
                          "OpSelectionMerge","OpLoopMerge"):
                historical_store.clear()
            if op in ("OpFunction","OpFunctionEnd"):block=None
            continue
        if op=="OpStore":
            if len(a)==2 and block is not None:
                stored[a[0]]=(block,a[1])
                path=function_literal_address_path(a[0])
                if path is not None:
                    window_store[path]=(block,a[1])
                    historical_store[path]=(block,a[1])
                else:
                    # An unknown write could alias any saved local candidate.
                    window_store.clear();historical_store.clear()
            else:
                window_store.clear();historical_store.clear()
            continue
        if name and op=="OpLoad":
            if len(a)<2:raise ValueError("GFX087_MALFORMED_LOAD")
            ptr=a[1]
            # Snapshot the actual input memory read at its own instruction,
            # NOT later at the consuming OpIMul or final UBO access.
            # Never expose source-private path or SPIR-V result IDs.
            read_path=function_literal_address_path(ptr) if len(a)==2 else None
            if read_path is None:read_class="untrusted_path"
            elif read_path in window_store and window_store[read_path][0]==block and block is not None:
                read_class="same_block_store_syntax"
            elif read_path in historical_store:
                relation=cfg.classify(historical_store[read_path][0],block)
                read_class="prior_store_CFG_"+relation
            else:read_class="no_prior_matching_store_observed"
            # Save the syntactic matching writer's value SSA ID privately
            # as it stood at the original OpLoad instruction time.
            writer_value=(window_store[read_path][1] if read_class=="same_block_store_syntax" else None)
            memory_read_state[name]=(read_class,writer_value)
            kind,storage,index_shape,depth=pointer_origin(ptr)
            exact=(len(a)==2 and ptr in stored and stored[ptr][0]==block and block is not None and storage=="Function" and index_shape=="literal")
            # Private Function root + all literal indices, independent of SSA pointer ID.
            path=function_literal_address_path(ptr) if len(a)==2 else None
            if path is None:category="unresolved"
            elif path in window_store and window_store[path][0]==block and block is not None:
                category="same_block_path_store_candidate"
            elif path in historical_store:
                category="prior_path_store_outside_trusted_window"
            else:category="no_prior_matching_path_store"
            # This value comes from a preceding same-block equivalent address-path
            # syntactic candidate only. Pointer alias freedom and actual runtime
            # Store->Load memory dependency are NOT proven.
            val_producer=None;val_shift=None;unknown_terminal=None;dom_relation=None
            integer_op=None;integer_literal_shape=None
            imul_input=None
            if category=="same_block_path_store_candidate":
                candidate_value=window_store[path][1]
                val_producer,val_shift=store_value_provenance(candidate_value)
                if val_shift=="unknown":
                    unknown_terminal=unknown_source_terminal(candidate_value)
                    if unknown_terminal=="integer_math":
                        integer_op,integer_literal_shape=private_integer_terminal_shape(candidate_value)
                        if integer_op=="OpIMul" and integer_literal_shape=="nonpower_of_two_literal":
                            imul_input=private_nonpower_imul_input(candidate_value)
                            if imul_input is None:
                                raise ValueError("GFX087_IMUL_NONPOWER_LITERAL_BUT_INPUT_UNCLASSIFIABLE")
            elif category=="prior_path_store_outside_trusted_window":
                writer_block=historical_store[path][0]
                dom_relation=cfg.classify(writer_block,block)
            indexload[name]=(kind,storage,index_shape,depth,exact,category,
                             val_producer,val_shift,unknown_terminal,dom_relation,
                             integer_op,integer_literal_shape,imul_input)
        if name and op in ("OpAccessChain","OpInBoundsAccessChain") and len(a)>=3:
            parentid=a[1]
            if parentid in authenticated:
                info=authenticated[parentid]
                if (not isinstance(info,tuple) or len(info)!=4 or
                    any(type(v)!=int for v in info) or info[1]!=0 or
                    info[2]!=16 or info[3]<=0):
                    raise ValueError("GFX087_INVALID_AUTHENTICATED_ORIGINAL_B_UBO_LAYOUT")
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
            kind,storage,index_shape,depth,exact,category,val_producer,val_shift,unknown_terminal,dom_relation,integer_op,integer_literal_shape,imul_input=indexload[root]
            if imul_input is not None:
                direct,terminal,memory_class,read_id=imul_input
                if terminal=="OpLoad":
                    read_state,writer_value=memory_read_state.get(
                        read_id,("unresolved_read_snapshot",None))
                    c["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_"+read_state]+=1
                    if read_state=="same_block_store_syntax":
                        if writer_value is None:
                            raise ValueError("GFX087_MISSING_MATCHED_SAMEBLOCK_WRITER_VALUE")
                        p,ancestry=store_value_provenance(writer_value)
                        inner,shape,origin=prior_store_bitcast_source(writer_value)
                        if inner=="OpIAdd":
                            operand_shape,lhs,rhs,type_class=source_inner_iadd_operands(writer_value)
                            left_id,right_id=iadd_operand_read_roots(writer_value)
                            for side,load_id in (("lhs",left_id),("rhs",right_id)):
                                shape,location,binding,block_kind,member=classify_input_uniform_interface(load_id)
                                for key,value in (("ptr_index_shape",shape),
                                                  ("input_location_kind",location),
                                                  ("uniform_binding_kind",binding),
                                                  ("uniform_block_kind",block_kind),
                                                  ("uniform_member_offset_kind",member)):
                                    c["SPV_iadd_OpLoad_interface_"+side+"_"+key+"_"+value]+=1
                                pointer_class,prior_class=load_memory_storage_shape(load_id)
                                c["SPV_iadd_operand_actual_OpLoad_"+side+"_pointer_storage_"+pointer_class]+=1
                                c["SPV_iadd_operand_actual_OpLoad_"+side+"_prior_store_at_read_"+prior_class]+=1
                            c["SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_"+operand_shape]+=1
                            c["SPV_imul_input_prior_store_Bitcast_OpIAdd_lhs_source_"+lhs]+=1
                            c["SPV_imul_input_prior_store_Bitcast_OpIAdd_rhs_source_"+rhs]+=1
                            c["SPV_imul_input_prior_store_Bitcast_OpIAdd_type_"+type_class]+=1
                        c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_"+inner]+=1
                        c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_shape_"+shape]+=1
                        c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_source_class_"+origin]+=1
                        c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_value_immediate_"+p]+=1
                        c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_value_bounded_shift_"+ancestry]+=1
                c["SPV_nonpower_OpIMul_dynamic_input_immediate_"+direct]+=1
                c["SPV_nonpower_OpIMul_dynamic_input_terminal_"+terminal]+=1
                c["SPV_nonpower_OpIMul_dynamic_input_memory_origin_"+memory_class]+=1
            if integer_op is not None:
                c["SPV_unknown_integer_terminal_public_core_opcode_"+integer_op]+=1
                c["SPV_unknown_integer_terminal_OpIMul_literal_shape_"+integer_literal_shape]+=1
            if unknown_terminal is not None:
                c["SPV_sameblock_store_unknown_ancestry_terminal_"+unknown_terminal]+=1
            if dom_relation is not None:
                c["SPV_prior_path_store_CFG_block_relation_"+dom_relation]+=1
            if val_producer is not None:
                c["SPV_sameblock_equivalent_path_Store_value_immediate_producer_"+val_producer]+=1
                c["SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_"+val_shift]+=1
            c["SPV_index_normalized_Function_literal_path_"+category]+=1
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
        raise ValueError("GFX087_AUTHENTIC_DYNAMIC_INDEX_PARTITION_DRIFT")
    n=c["SPV_index_OpLoad_pointer_root_classified"]
    for prefix in ("SPV_index_pointer_direct_definition_",
        "SPV_index_pointer_root_storage_","SPV_index_pointer_root_index_shape_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=n:
            raise ValueError("GFX087_ANONYMOUS_POINTER_ORIGIN_PARTITION_DRIFT")
    if c["SPV_same_block_prior_OpStore_exact_pointer_ID_candidates"]+c[
            "SPV_no_same_block_prior_OpStore_exact_pointer_ID_proven"]!=n:
        raise ValueError("GFX087_SOURCE_PTR_EXACT_STORE_ACCOUNTING_DRIFT")
    if sum(v for k,v in c.items() if k.startswith(
            "SPV_index_normalized_Function_literal_path_"))!=n:
        raise ValueError("GFX087_NORMALIZED_FUNCTION_LITERAL_PATH_ACCOUNTING_DRIFT")
    cross=c["SPV_index_normalized_Function_literal_path_prior_path_store_outside_trusted_window"]
    if sum(v for k,v in c.items() if k.startswith(
            "SPV_prior_path_store_CFG_block_relation_"))!=cross:
        raise ValueError("GFX087_CROSS_BLOCK_CFG_PARTITION_DRIFT")
    candidate=c["SPV_index_normalized_Function_literal_path_same_block_path_store_candidate"]
    for prefix in ("SPV_sameblock_equivalent_path_Store_value_immediate_producer_",
                   "SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=candidate:
            raise ValueError("GFX087_LOCAL_STORE_VALUE_SOURCE_OPCODE_COUNT_PARTITION_DRIFT")
    unknown=c["SPV_sameblock_equivalent_path_Store_value_bounded_shift_ancestry_unknown"]
    nonpower=c["SPV_unknown_integer_terminal_OpIMul_literal_shape_nonpower_of_two_literal"]
    input_oploads=c["SPV_nonpower_OpIMul_dynamic_input_terminal_OpLoad"]
    sameblock=c["SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_same_block_store_syntax"]
    target=c["SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_OpIAdd"]
    for side in ("lhs","rhs"):
        for category in ("ptr_index_shape","input_location_kind",
                         "uniform_binding_kind","uniform_block_kind",
                         "uniform_member_offset_kind"):
            prefix="SPV_iadd_OpLoad_interface_"+side+"_"+category+"_"
            if sum(v for k,v in c.items() if k.startswith(prefix))!=target:
                raise ValueError("GFX087_INPUT_UNIFORM_INTERFACE_DECORATION_PARTITION_DRIFT")

    for side in ("lhs","rhs"):
        for suffix in ("pointer_storage_","prior_store_at_read_"):
            prefix="SPV_iadd_operand_actual_OpLoad_"+side+"_"+suffix
            if sum(v for k,v in c.items() if k.startswith(prefix))!=target:
                raise ValueError("GFX087_OPIADD_TRUE_LOAD_STORAGE_AND_PRIORSTORE_PARTITION_DRIFT")

    for prefix in ("SPV_imul_input_prior_store_Bitcast_OpIAdd_operand_shape_",
                   "SPV_imul_input_prior_store_Bitcast_OpIAdd_lhs_source_",
                   "SPV_imul_input_prior_store_Bitcast_OpIAdd_rhs_source_",
                   "SPV_imul_input_prior_store_Bitcast_OpIAdd_type_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=target:
            raise ValueError("GFX087_IADD_OPERAND_CLASSIFICATION_PARTITION_DRIFT")
    for prefix in ("SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_opcode_",
                   "SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_inner_shape_",
                   "SPV_nonpower_OpIMul_input_sameblock_prior_writer_Bitcast_source_class_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=sameblock:
            raise ValueError("GFX087_WRITER_BITCAST_SOURCE_PARTITION_DRIFT")
    for prefix in ("SPV_nonpower_OpIMul_input_sameblock_prior_writer_value_immediate_",
                   "SPV_nonpower_OpIMul_input_sameblock_prior_writer_value_bounded_shift_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=sameblock:
            raise ValueError("GFX087_PRIOR_WRITER_VALUE_PRODUCER_PARTITION_DRIFT")
    if sum(v for k,v in c.items() if k.startswith(
            "SPV_nonpower_OpIMul_dynamic_input_OpLoad_prior_store_"))!=input_oploads:
        raise ValueError("GFX087_IMUL_INPUT_MEMORY_READ_STORE_PARTITION_DRIFT")
    for prefix in ("SPV_nonpower_OpIMul_dynamic_input_immediate_",
                   "SPV_nonpower_OpIMul_dynamic_input_terminal_",
                   "SPV_nonpower_OpIMul_dynamic_input_memory_origin_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=nonpower:
            raise ValueError("GFX087_IMUL_INPUT_PARTITION_DRIFT")
    grouped=c["SPV_sameblock_store_unknown_ancestry_terminal_integer_math"]
    for prefix in ("SPV_unknown_integer_terminal_public_core_opcode_",
                   "SPV_unknown_integer_terminal_OpIMul_literal_shape_"):
        if sum(v for k,v in c.items() if k.startswith(prefix))!=grouped:
            raise ValueError("GFX087_INTEGER_OPCODE_LITERAL_SHAPE_PARTITION_DRIFT")

    if sum(v for k,v in c.items() if k.startswith(
            "SPV_sameblock_store_unknown_ancestry_terminal_"))!=unknown:
        raise ValueError("GFX087_UNKNOWN_TERMINAL_OPCODE_PARTITION_DRIFT")
    return {**dict(c),
       "SPV_interface_decorations_prove_original_DXBC_semantics":False,
       "SPV_Uniform_Binding_and_Offset_prove_Material_CB_byte_parity":False,
       "SPV_Input_Location_proves_original_vertex_attribute_interpolation":False,
       "SPV_OpIAdd_input_memory_pointer_proves_original_DXBC_temp_mapping":False,
       "SPV_OpIAdd_input_prior_Store_class_proves_effective_memory_value":False,
       "SPV_OpIAdd_operand_shape_proves_numeric_input_parity":False,
       "SPV_OpIAdd_operand_SSA_proves_original_DXBC_component_mapping":False,
       "SPV_Bitcast_inner_opcode_proves_original_DXBC_temp_component":False,
       "SPV_CompositeExtract_source_SSA_proves_actual_pixel_parity":False,
       "SPV_OpIMul_input_prior_writer_value_SSA_proves_original_DXBC_ISHL":False,
       "SPV_OpIMul_input_prior_writer_value_syntax_proves_alias_free_memory":False,
       "SPV_OpIMul_input_prior_Store_syntax_proves_memory_reaching_value":False,
       "SPV_OpIMul_input_writer_CFG_block_dominance_proves_alias_freedom":False,
       "SPV_OpIMul_input_SSA_syntax_proves_original_DXBC_source_temp":False,
       "SPV_OpIMul_input_OpLoad_proves_reaching_memory_Store":False,
       "SPV_OpIMul_literal_power_two_proves_original_DXBC_ISHL":False,
       "SPV_OpIMul_literal_power_two_proves_memory_Store_to_Load_value":False,
       "SPV_unknown_opcode_family_is_shader_semantic_proof":False,
       "SPV_CFG_block_dominance_proves_Store_memory_value_reaching_Load":False,
       "SPV_unknown_Store_value_terminal_proves_absent_shift":False,
       "SPV_Store_value_SSA_shift_ancestry_proves_original_DXBC_ISHL":False,
       "SPV_local_store_value_producer_proves_actual_runtime_index_value":False,
       "SPV_equivalent_Function_literal_address_paths_prove_runtime_dataflow":False,
       "SPV_equivalent_address_path_store_proves_CFG_dominance":False,
       "SPV_equivalent_address_path_proves_DXBC_temp_to_SPV_SSA_mapping":False,
       "SPV_exact_pointer_ID_prior_Store_means_aliased_memory_value_proven":False,
       "SPV_pointer_origin_shape_proves_original_DXBC_temp_provenance":False,
       "SPV_storage_class_means_full_CFG_dominance_or_runtime_bounds":False,
       "original_Shader48_Material_CB_register_byte_semantics_proven":False,
       "originalShaderRestored":False,
       "phase_closed":False}
