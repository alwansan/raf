"""Narrow output dataflow oracle for the pinned AUTHORED receipt shader.

Not a general SPIR-V evaluator: one entrypoint, one straight-line block,
typed constants and simple vector/pointer operations. Unsupported shapes fail
closed. No original shader semantics are inferred.
"""
import math
import shlex
import struct


def need(ok,code):
    if not ok:raise ValueError(code)


def float_bits(value):
    return struct.unpack("<I",struct.pack("<f",value))[0]


def scalar(value):
    return ("f",float_bits(value))


def agg(values):
    return ("agg",tuple(values))


def lanes(value):
    need(type(value) is tuple and len(value)==2 and value[0]=="agg","expected_composite")
    return value[1]


def at(value,indices):
    for i in indices:
        items=lanes(value)
        need(0<=i<len(items),"composite_index")
        value=items[i]
    return value


def put(value,indices,item):
    if not indices:return item
    i,*rest=indices
    items=list(lanes(value))
    need(0<=i<len(items),"composite_index")
    items[i]=put(items[i],rest,item)
    return agg(items)


def binary(op,a,b):
    if a[0]=="agg" or b[0]=="agg":
        left=lanes(a);right=lanes(b)
        need(len(left)==len(right),"vector_operation_shape")
        return agg(binary(op,x,y) for x,y in zip(left,right))
    return (op,a,b)


def unary(op,a):
    if a[0]=="agg":return agg(unary(op,x) for x in lanes(a))
    return (op,a)


def instructions(text):
    result=[]
    for line in text.splitlines():
        line=line.strip()
        if not line or line.startswith(";"):continue
        tokens=shlex.split(line,comments=False,posix=True)
        if len(tokens)>=3 and tokens[1]=="=":
            result.append((tokens[0],tokens[2],tokens[3:]))
        else:result.append((None,tokens[0],tokens[1:]))
    return result


def output_expression(text,model):
    ins=instructions(text)
    defs={i:(op,a) for i,op,a in ins if i is not None}
    need(len(defs)==sum(i is not None for i,_,_ in ins),"duplicate_ssa_id")
    entries=[a for _,op,a in ins if op=="OpEntryPoint"]
    need(len(entries)==1 and entries[0][0]==("Vertex" if model==0 else "Fragment"),
         "entrypoint_model")
    entry=entries[0][1]
    interfaces=set(entries[0][3:])
    decorations={}
    members={}
    for _,op,a in ins:
        if op=="OpDecorate" and len(a)>=3:
            if a[1] in ("Location","BuiltIn"):
                key=(a[0],a[1]);need(key not in decorations,"duplicate_decoration")
                decorations[key]=a[2]
        if op=="OpMemberDecorate" and len(a)>=4 and a[2] in ("Location","BuiltIn"):
            key=(a[0],int(a[1]),a[2]);need(key not in members,"duplicate_member_decoration")
            members[key]=a[3]
    values={}
    pointers={}
    memory={}
    unknown=("unknown",)

    def shape(t,fill=unknown):
        op,a=defs[t]
        if op in ("OpTypeFloat","OpTypeInt","OpTypeBool"):return fill
        if op=="OpTypeVector":
            n=int(a[1]);need(1<=n<=16,"vector_shape")
            return agg(shape(a[0],fill) for _ in range(n))
        if op=="OpTypeStruct":
            need(len(a)<=32,"struct_shape")
            return agg(shape(x,fill) for x in a)
        if op=="OpTypeArray":
            n=as_int(a[1]);need(0<n<=64,"array_shape")
            return agg(shape(a[0],fill) for _ in range(n))
        raise ValueError("unsupported_type_shape_"+op)

    def value(i):
        if i in values:return values[i]
        op,a=defs.get(i,("",[]))
        if op=="OpConstant":
            ty,raw=a;kind,detail=defs[ty]
            if kind=="OpTypeFloat" and detail==["32"]:
                f=float.fromhex(raw) if "0x" in raw.lower() else float(raw)
                need(math.isfinite(f),"nonfinite_constant")
                v=scalar(f)
            elif kind=="OpTypeInt":
                v=("i",int(raw,0))
            else:raise ValueError("unsupported_constant_type")
        elif op=="OpConstantComposite":
            v=agg(value(x) for x in a[1:])
        elif op=="OpConstantNull":
            kind,_=defs[a[0]]
            v=shape(a[0],("i",0) if kind=="OpTypeInt" else scalar(0))
        elif op=="OpUndef":
            v=shape(a[0])
        else:raise ValueError("undefined_or_unsupported_value_"+op)
        values[i]=v
        return v

    def as_int(i):
        v=value(i);need(v[0]=="i","nonconstant_pointer_index")
        return v[1]

    def variable(i,a):
        ty,storage=a[:2]
        op,parts=defs[ty]
        need(op=="OpTypePointer" and parts[0]==storage,"variable_pointer_type")
        t=parts[1]
        init=shape(t)
        if storage=="Input" and decorations.get((i,"Location"))=="0":
            op2,parts2=defs[t]
            need(op2=="OpTypeVector" and parts2[1]=="4","authored_position_input_shape")
            init=agg(("input",0,j) for j in range(4))
        if len(a)==3:init=value(a[2])
        pointers[i]=(i,())
        memory[i]=init
        return t

    targets=[]
    in_function=False
    # Global variable declarations precede functions. Locate the exact
    # output interface, allowing a direct BuiltIn or a struct member.
    for i,op,a in ins:
        if op=="OpFunction":break
        if op!="OpVariable":continue
        t=variable(i,a)
        if a[1]!="Output" or i not in interfaces:continue
        deco,key=("BuiltIn","Position") if model==0 else ("Location","0")
        if decorations.get((i,deco))==key:targets.append((i,()))
        top,parts=defs[t]
        if top=="OpTypeStruct":
            for j in range(len(parts)):
                if members.get((t,j,deco))==key:targets.append((i,(j,)))
    need(len(targets)==1,"authored_unique_output_interface")
    target=targets[0]
    active=False
    labels=returns=stores=0
    for i,op,a in ins:
        if op=="OpFunction":
            active=i==entry
            continue
        if op=="OpFunctionEnd":
            active=False
            continue
        if not active:continue
        if op=="OpLabel":
            labels+=1;need(labels==1,"nonlinear_entrypoint")
            continue
        if op in ("OpLine","OpNoLine"):continue
        if op=="OpReturn":
            returns+=1;continue
        if op=="OpVariable":
            variable(i,a);continue
        if op in ("OpAccessChain","OpInBoundsAccessChain"):
            root,indices=pointers[a[1]]
            pointers[i]=(root,indices+tuple(as_int(x) for x in a[2:]))
            continue
        if op=="OpLoad":
            root,indices=pointers[a[1]]
            values[i]=at(memory[root],indices);continue
        if op=="OpStore":
            root,indices=pointers[a[0]]
            memory[root]=put(memory[root],indices,value(a[1]))
            if root==target[0]:stores+=1
            continue
        if op=="OpCopyObject":
            if a[1] in pointers:pointers[i]=pointers[a[1]]
            else:values[i]=value(a[1])
            continue
        if op=="OpCompositeExtract":
            values[i]=at(value(a[1]),tuple(map(int,a[2:])));continue
        if op=="OpCompositeInsert":
            values[i]=put(value(a[2]),tuple(map(int,a[3:])),value(a[1]));continue
        if op=="OpCompositeConstruct":
            t,parts=defs[a[0]]
            items=[value(x) for x in a[1:]]
            if t=="OpTypeVector":
                items=[v for item in items for v in (lanes(item) if item[0]=="agg" else (item,))]
                need(len(items)==int(parts[1]),"construct_vector_shape")
            values[i]=agg(items);continue
        if op=="OpVectorShuffle":
            seq=lanes(value(a[1]))+lanes(value(a[2]))
            values[i]=agg(unknown if int(k)==4294967295 else seq[int(k)] for k in a[3:]);continue
        if op in ("OpFAdd","OpFSub","OpFMul","OpFDiv"):
            values[i]=binary(op,value(a[1]),value(a[2]));continue
        if op=="OpFNegate":
            values[i]=unary(op,value(a[1]));continue
        if op=="OpVectorTimesScalar":
            values[i]=agg(binary("OpFMul",x,value(a[2])) for x in lanes(value(a[1])));continue
        raise ValueError("unsupported_authored_entry_instruction_"+op)
    need(labels==returns==1 and stores>0,"authored_entrypoint_store_missing")
    result=lanes(at(memory[target[0]],target[1]))
    need(len(result)==4,"authored_output_vector_shape")
    if model==0:
        x=result[0]
        need(x[0]=="OpFAdd" and len(x)==3,"vertex_position_x_not_add")
        if x[1]==("input",0,0):constant=x[2]
        elif x[2]==("input",0,0):constant=x[1]
        else:raise ValueError("vertex_position_x_input_not_preserved")
        need(constant[0]=="f","vertex_position_x_marker_not_constant")
        return [constant[1]]
    need(all(x[0]=="f" for x in result),"fragment_output_not_constant")
    return [x[1] for x in result]


def expected_marker(model,pass_index,route_index):
    # Source fixture's exact integer/power-of-two constants.
    if model==0:return [float_bits((route_index+1)/4096)]
    return [float_bits((route_index+1)/1024),float_bits(pass_index/4),
            float_bits(.25),float_bits(1.)]
