#!/usr/bin/env python3
"""GFX073: original Shader48 DXBC relative CB b+literal offset multiset vs real SPV.

Only valid source-private, stage-local DXBC b-register, literal vec4 offset
and direct-relative / immediate32-plus-relative profile is compared to an
independently source-b-authenticated SPV Uniform UBO OpAccessChain→OpLoad
index (Bitcast(OpLoad) or IAdd(literal,Bitcast(OpLoad))).

Original b numbers, offsets, source/temp identifiers and SPV IDs stay private
to GitHub Actions. Only safe aggregate matched/mismatched counts may leave CI.
A matching keyed multiset is NOT source operation bijection, SSA definition,
runtime index values, Material CB member semantics, or Android GPU parity.
"""
from __future__ import annotations
import re,struct
from collections import Counter
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import operand,CUSTOMDATA,MAX_DWORDS,MAX_INST
from gfxlab.tools.multi_shader_original_cb_access_shapes import KNOWN_ARITHMETIC_ARITY
from gfxlab.tools.multi_shader_original_cb_relative_expression067 import decode_original_operand_tree
from gfxlab.tools.multi_shader_original_cb_temp_writer069 import temp_component_source_origin

ASSIGN=re.compile(r"^\s*(%[0-9]+)\s*=\s*(Op[A-Za-z0-9_]+)(?:\s+(.*))?$")
MAX_SPV_BYTES=16*1024*1024
MAX_SPV_LINES=300000

def original_source_private_b_relative_offset_multiset(shdr,declared):
    """Original private source exact b+relative shape+signed-literal multiset."""
    if (not isinstance(shdr,bytes) or len(shdr)<12 or len(shdr)%4
        or len(shdr)>MAX_DWORDS*4 or not isinstance(declared,dict)
        or any(type(b)!=int or type(v)!=int or not 0<=b<=65535
               or not 0<v<=65535 for b,v in declared.items())):
        raise ValueError("GFX073_ORIGINAL_DXBC_OR_CB_INPUT_INVALID")
    words=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if words[1]!=len(words):raise ValueError("GFX073_ORIGINAL_SHDR_LENGTH_MISMATCH")
    out=Counter();c=Counter();p=2;n=0
    while p<len(words):
        op=words[p]&2047
        if op==CUSTOMDATA:
            if p+1>=len(words) or words[p+1]<2:
                raise ValueError("GFX073_SOURCE_CUSTOMDATA_INVALID")
            ln=words[p+1]
        else:ln=(words[p]>>24)&127
        if ln<1 or p+ln>len(words):raise ValueError("GFX073_SOURCE_OPCODE_BOUNDARY_INVALID")
        end=p+ln;n+=1
        if n>MAX_INST:raise ValueError("GFX073_SOURCE_INSTRUCTION_LIMIT")
        if op not in KNOWN_ARITHMETIC_ARITY:
            p=end;continue
        cursor=p+1;ext=bool(words[p]&0x80000000);num=0
        while ext:
            if cursor>=end or num>=4:
                raise ValueError("GFX073_SOURCE_OPCODE_EXTENSION_INVALID")
            x=words[cursor];cursor+=1
            if x&63 not in (0,1,2,3):
                raise ValueError("GFX073_SOURCE_OPCODE_EXTENSION_UNKNOWN")
            ext=bool(x&0x80000000);num+=1
        args=[]
        for _ in range(KNOWN_ARITHMETIC_ARITY[op]):
            first=cursor
            node,cursor=decode_original_operand_tree(words,cursor,end)
            leg,legacy_end=operand(words,first,end)
            if (cursor!=legacy_end or node["type"]!=leg["type"]
                or node["dimension"]!=leg["dimension"]):
                raise ValueError("GFX073_INDEPENDENT_SOURCE_OPERAND_BOUNDARY_DRIFT")
            args.append(node)
        if cursor!=end:raise ValueError("GFX073_SOURCE_OPCODE_ARITY_INVALID")
        if args[0]["type"]==8:raise ValueError("GFX073_SOURCE_CB_DESTINATION")
        for x in args[1:]:
            if x["type"]!=8:continue
            c["source_original_CB_operand_occurrences"]+=1
            if x["dimension"]!=2 or len(x["indices"])!=2:
                c["source_original_unsupported_CB_shape"]+=1;continue
            b,v=x["indices"]
            if b[0] not in ("literal32","literal64") or b[1] not in declared:
                raise ValueError("GFX073_SOURCE_CB_B_NOT_AUTHENTIC_DECLARED")
            if v[0]!="relative":
                continue
            if len(v)!=4 or temp_component_source_origin(v[3]) is None:
                c["source_relative_not_supported_temp_component"]+=1
                continue
            rep=v[1];base=v[2]
            if rep==2 and base==0:kind="direct"
            elif rep==3 and type(base)==int:kind="add"
            else:
                c["source_relative_unhandled_index_representation"]+=1
                continue
            # PRIVATE: this key contains original b index and constant offset.
            out[(b[1],kind,base)]+=1
            c["source_relative_CB_index_keys_classified"]+=1
        p=end
    if p!=len(words):raise ValueError("GFX073_SOURCE_NOT_TERMINATED")
    if c["source_relative_CB_index_keys_classified"]!=sum(out.values()):
        raise ValueError("GFX073_SOURCE_PRIVATE_MULTISET_ACCOUNTING")
    return out,dict(c)

def translated_spv_private_authenticated_b_relative_offset_multiset(dis,authenticated):
    """Only actual loaded dynamic vec4 pointers from authenticated original b UBO."""
    if (not isinstance(dis,bytes) or not 0<len(dis)<=MAX_SPV_BYTES
        or not isinstance(authenticated,dict)):
        raise ValueError("GFX073_SPV_INPUT_INVALID")
    lines=dis.decode("utf8","strict").splitlines()
    if len(lines)>MAX_SPV_LINES:raise ValueError("GFX073_SPV_TOO_MANY_LINES")
    defs={};types=set()
    for raw in lines:
        m=ASSIGN.fullmatch(raw.split(";",1)[0].strip())
        if not m:continue
        ident,op,tail=m.groups()
        if ident in defs:raise ValueError("GFX073_DUPLICATE_SPV_RESULT_ID")
        args=(tail or "").split()
        defs[ident]=(op,args)
        if op=="OpTypeInt" and args in (["32","0"],["32","1"]):
            types.add(ident)
    constants={}
    for ident,(op,args) in defs.items():
        if op=="OpConstant" and len(args)==2 and args[0] in types:
            try:constants[ident]=int(args[1],0)
            except ValueError:
                try:constants[ident]=int(args[1],10)
                except ValueError:pass
        elif op=="OpConstantNull" and len(args)==1 and args[0] in types:
            constants[ident]=0
    def idx_kind(token):
        if token in constants:return "literal",constants[token]
        op,args=defs.get(token,(None,[]))
        if (op and op not in ("OpSpecConstant","OpSpecConstantOp",
            "OpSpecConstantComposite","OpConstantNull","OpConstant","OpUndef")
            and args and args[0] in types):
            return "dynamic",None
        return "unknown",None
    def bitcast_load_value(token):
        op,a=defs.get(token,(None,[]))
        if op!="OpBitcast" or len(a)!=2 or a[0] not in types:
            return False
        inner,innerargs=defs.get(a[1],(None,[]))
        return inner=="OpLoad" and len(innerargs)>=2

    def classified_expr(token):
        """Private (index shape, immediate offset). Never export this tuple."""
        if bitcast_load_value(token):return ("direct",0)
        op,a=defs.get(token,(None,[]))
        if op=="OpIAdd" and len(a)==3 and a[0] in types:
            left,right=a[1:]
            kl,vl=idx_kind(left);kr,vr=idx_kind(right)
            if (kl=="literal") != (kr=="literal"):
                literal=vl if kl=="literal" else vr
                other=right if kl=="literal" else left
                if bitcast_load_value(other):
                    if not -(2**31)<=literal<2**32:return None
                    if literal>=2**31:literal-=2**32
                    return ("add",literal)
        return None

    # Strict limited pointer state (original b, array extent, kind, private dynamic index).
    pointers={};out=Counter();c=Counter()
    for raw in lines:
        m=ASSIGN.fullmatch(raw.split(";",1)[0].strip())
        if not m:continue
        ident,op,tail=m.groups();a=(tail or "").split()
        if op in ("OpAccessChain","OpInBoundsAccessChain") and len(a)>=3:
            parentid=a[1]
            if parentid in authenticated:
                data=authenticated[parentid]
                if (not isinstance(data,tuple) or len(data)!=4 or
                    any(type(v)!=int for v in data) or
                    data[1]!=0 or data[2]!=16 or data[3]<=0):
                    raise ValueError("GFX073_INVALID_ORIGINAL_B_AUTHENTICATED_UBO_LAYOUT")
                parent=(data[0],data[3],"root",None)
            elif parentid in pointers:
                parent=pointers[parentid]
            else:continue
            b,extent,kind,_=parent
            indices=a[2:]
            if kind=="root":
                if idx_kind(indices[0])!=("literal",0):
                    c["SPV_invalid_struct_member_or_index"]+=1;continue
                indices=indices[1:]
                if not indices:
                    pointers[ident]=(b,extent,"array",None);continue
            elif kind=="array":pass
            elif kind=="vector":
                k,v=idx_kind(indices[0]) if len(indices)==1 else ("unknown",None)
                if k=="literal" and 0<=v<4:
                    pointers[ident]=(b,extent,"scalar",parent[3])
                else:c["SPV_invalid_component_path"]+=1
                continue
            else:continue
            if len(indices) not in (1,2):
                c["SPV_invalid_vector_index_path"]+=1;continue
            k,v=idx_kind(indices[0])
            if k=="literal":
                if not 0<=v<extent:c["SPV_literal_vector_outside_original_array"]+=1
                continue
            if k!="dynamic":
                c["SPV_unproven_index_type"]+=1;continue
            if len(indices)==2:
                ck,cv=idx_kind(indices[1])
                if ck!="literal" or not 0<=cv<4:
                    c["SPV_invalid_component_path"]+=1;continue
                k2="scalar"
            else:k2="vector"
            pointers[ident]=(b,extent,k2,indices[0])
        elif op=="OpCopyObject" and len(a)==2 and a[1] in pointers:
            pointers[ident]=pointers[a[1]]
        elif op=="OpLoad" and len(a)>=2 and a[1] in pointers:
            b,extent,kind,idx=pointers[a[1]]
            if kind not in ("vector","scalar"):continue
            c["SPV_authenticated_source_b_real_dynamic_UBO_vector_Load_occurrences"]+=1
            shape=classified_expr(idx)
            if shape is None:
                c["SPV_dynamic_UBO_index_shape_unclassified"]+=1
                continue
            out[(b,shape[0],shape[1])]+=1
            c["SPV_dynamic_UBO_index_b_and_offset_keys_classified"]+=1
    if sum(out.values())!=c["SPV_dynamic_UBO_index_b_and_offset_keys_classified"]:
        raise ValueError("GFX073_SPV_PRIVATE_MULTISET_ACCOUNTING")
    return out,dict(c)

def compare_private_b_and_relative_literal_multisets(source,spv):
    """Never include private source register/offset keys in public JSON or errors."""
    if not isinstance(source,Counter) or not isinstance(spv,Counter):
        raise ValueError("GFX073_PRIVATE_MULTISET_TYPE_INVALID")
    if any(type(v)!=int or v<=0 for v in source.values()) or any(
        type(v)!=int or v<=0 for v in spv.values()):
        raise ValueError("GFX073_PRIVATE_MULTISET_MULTIPLICITY_INVALID")
    match=sum((source&spv).values())
    missing=sum((source-spv).values())
    extra=sum((spv-source).values())
    if match+missing!=sum(source.values()) or match+extra!=sum(spv.values()):
        raise ValueError("GFX073_PRIVATE_MULTISET_PARTITION_INVALID")
    return {
      "source_original_relative_CB_operand_occurrences":sum(source.values()),
      "SPV_real_loaded_dynamic_UBO_index_occurrences_classified":sum(spv.values()),
      "private_source_b_offset_shape_multiset_occurrences_matched":match,
      "private_source_b_offset_shape_occurrences_missing_in_SPV":missing,
      "private_translated_SPV_b_offset_shape_occurrences_without_source":extra,
      "private_stage_b_offset_shape_multiset_equal":not missing and not extra,
      "original_temp_component_to_translated_SPV_index_value_proven":False,
      "original_source_CB_relative_operand_to_SPV_instruction_bijection_proven":False,
      "GFX054_original_Material_property_CB_member_mapping_proven":False,
    }
