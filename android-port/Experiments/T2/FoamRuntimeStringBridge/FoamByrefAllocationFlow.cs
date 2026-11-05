// T2 WATER-001: limited same-basic-block source-original array flow.
// Never publish private method names, original IL, or actual numeric indices.
// Branch joins / unsupported instructions always return an unproven site.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamByrefAllocationFlow
{
    internal sealed record SafeProfile(
        int OriginalMatchingCalleeDefinitions,
        int ExactStindRefSites,
        int ProvenNewarrRenderTextureArrayToRefFormalStores,
        int RefFormalStoresWithUnprovenValue,
        int StoreSitesWithUnprovenDestinationOrFlow,
        int ExactStelemRefSites,
        int ProvenArrayElementWritesThroughRefFormal,
        int ArrayElementStoreSitesNotProven,
        bool WholeFunctionBranchJoinVerified,
        bool RuntimeArraySizeOrContentsVerified,
        bool RuntimeExecutionVerified);

    private enum Tag { Unknown, RefArrayFormal, NewRenderArray, FromRefArrayFormal }

    private static bool RtArray(TypeReference type) =>
        type is ArrayType a && a.Rank==1 &&
        a.ElementType.FullName=="UnityEngine.RenderTexture";

    private static bool Same(MethodDefinition m, MethodReference call) =>
        m.FullName==call.FullName && m.HasThis==call.HasThis &&
        m.Parameters.Count==call.Parameters.Count &&
        m.Parameters.Zip(call.Parameters,
            (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName).All(x=>x);

    private static int? ArgIndex(Instruction ins, MethodDefinition m)
    {
        int? raw=ins.OpCode.Code switch
        {
            Code.Ldarg_0 => 0,
            Code.Ldarg_1 => 1,
            Code.Ldarg_2 => 2,
            Code.Ldarg_3 => 3,
            Code.Ldarg or Code.Ldarg_S when ins.Operand is ParameterDefinition p =>
                p.Index+(m.HasThis?1:0),
            _ => null
        };
        return raw.HasValue && (!m.HasThis || raw.Value>0)
            ? raw.Value-(m.HasThis?1:0) : null;
    }

    private static int? LocalIndex(Instruction ins)
    {
        if (ins.Operand is VariableDefinition v) return v.Index;
        return ins.OpCode.Code switch
        {
            Code.Ldloc_0 or Code.Stloc_0 => 0,
            Code.Ldloc_1 or Code.Stloc_1 => 1,
            Code.Ldloc_2 or Code.Stloc_2 => 2,
            Code.Ldloc_3 or Code.Stloc_3 => 3,
            _ => null
        };
    }

    private static HashSet<Instruction> Entries(MethodDefinition method)
    {
        var ops=method.Body.Instructions;
        var entries=new HashSet<Instruction>();
        if(ops.Count>0) entries.Add(ops[0]);
        for(int i=0;i<ops.Count;i++)
        {
            if(ops[i].Operand is Instruction single)
                entries.Add(single);
            if(ops[i].Operand is Instruction[] targets)
                foreach(var target in targets) entries.Add(target);
            if(ops[i].OpCode.FlowControl is FlowControl.Branch or
                 FlowControl.Cond_Branch or FlowControl.Return or
                 FlowControl.Throw or FlowControl.Break)
                if(i+1<ops.Count) entries.Add(ops[i+1]);
        }
        foreach(var h in method.Body.ExceptionHandlers)
        {
            if(h.TryStart!=null) entries.Add(h.TryStart);
            if(h.HandlerStart!=null) entries.Add(h.HandlerStart);
            if(h.FilterStart!=null) entries.Add(h.FilterStart);
            if(h.TryEnd!=null) entries.Add(h.TryEnd);
            if(h.HandlerEnd!=null) entries.Add(h.HandlerEnd);
        }
        return entries;
    }

    private static (bool Proven,bool RefStore,bool Resolved) TraceOne(
        MethodDefinition m, int site, HashSet<Instruction> entries)
    {
        var ops=m.Body.Instructions;
        int start=site;
        while(start>0 && !entries.Contains(ops[start])) start--;
        var stack=new List<Tag>();
        var locals=new Dictionary<int,Tag>();
        static Tag Pop(List<Tag> s)
        {
            if(s.Count==0) return Tag.Unknown;
            Tag value=s[^1];
            s.RemoveAt(s.Count-1);
            return value;
        }
        for(int i=start;i<=site;i++)
        {
            var ins=ops[i];
            var c=ins.OpCode.Code;
            if(c==Code.Nop) continue;
            if(ins.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                 or FlowControl.Return or FlowControl.Throw or FlowControl.Break)
                return (false,false,false);

            int? arg=ArgIndex(ins,m);
            if(arg is int p)
            {
                stack.Add(p<m.Parameters.Count &&
                    m.Parameters[p].ParameterType is ByReferenceType br &&
                    RtArray(br.ElementType) ? Tag.RefArrayFormal : Tag.Unknown);
                continue;
            }
            if(ins.OpCode.Name.StartsWith("ldarg",StringComparison.Ordinal))
            {
                stack.Add(Tag.Unknown);
                continue;
            }
            if(ins.OpCode.Name.StartsWith("stloc",StringComparison.Ordinal))
            {
                int? n=LocalIndex(ins);
                if(n is null) return (false,false,false);
                locals[n.Value]=Pop(stack);
                continue;
            }
            if(ins.OpCode.Name.StartsWith("ldloca",StringComparison.Ordinal))
            {
                stack.Add(Tag.Unknown);
                continue;
            }
            if(ins.OpCode.Name.StartsWith("ldloc",StringComparison.Ordinal))
            {
                int? n=LocalIndex(ins);
                if(n is null) return (false,false,false);
                stack.Add(locals.GetValueOrDefault(n.Value,Tag.Unknown));
                continue;
            }
            if(ins.OpCode.Name.StartsWith("ldc.",StringComparison.Ordinal) ||
                c is Code.Ldnull or Code.Ldstr or Code.Ldtoken or Code.Ldsfld)
            {
                stack.Add(Tag.Unknown);
                continue;
            }
            if(c==Code.Newarr)
            {
                Pop(stack);
                stack.Add(ins.Operand is TypeReference t &&
                    t.FullName=="UnityEngine.RenderTexture"
                    ? Tag.NewRenderArray : Tag.Unknown);
                continue;
            }
            if(c==Code.Ldind_Ref)
            {
                stack.Add(Pop(stack)==Tag.RefArrayFormal
                    ? Tag.FromRefArrayFormal : Tag.Unknown);
                continue;
            }
            if(c==Code.Dup)
            {
                stack.Add(stack.Count>0?stack[^1]:Tag.Unknown);
                continue;
            }
            if(c==Code.Pop){Pop(stack);continue;}
            if(c==Code.Ldlen)
            {
                Pop(stack);
                stack.Add(Tag.Unknown);
                continue;
            }
            if(c is Code.Conv_I4 or Code.Conv_U4 or Code.Conv_I or Code.Conv_U)
            {
                Pop(stack);
                stack.Add(Tag.Unknown);
                continue;
            }
            if(c is Code.Add or Code.Sub or Code.Mul or Code.Div or Code.Ceq
                 or Code.Clt or Code.Cgt or Code.And or Code.Or)
            {
                Pop(stack); Pop(stack); stack.Add(Tag.Unknown);
                continue;
            }
            if(c==Code.Ldfld)
            {
                Pop(stack);
                stack.Add(Tag.Unknown);
                continue;
            }
            if(c==Code.Ldelem_Ref)
            {
                Pop(stack); Pop(stack);
                stack.Add(Tag.Unknown);
                continue;
            }
            if(c==Code.Stind_Ref)
            {
                Tag value=Pop(stack),address=Pop(stack);
                bool refAddress=address==Tag.RefArrayFormal;
                return (refAddress && value==Tag.NewRenderArray,refAddress,true);
            }
            if(c==Code.Stelem_Ref)
            {
                Pop(stack); Pop(stack);
                Tag array=Pop(stack);
                return (array==Tag.FromRefArrayFormal,false,true);
            }
            if(c is Code.Call or Code.Callvirt or Code.Newobj)
            {
                if(ins.Operand is not MethodReference called)
                    return (false,false,false);
                int total=called.Parameters.Count+(c==Code.Newobj?0:called.HasThis?1:0);
                if(total>32) return (false,false,false);
                for(int n=0;n<total;n++) Pop(stack);
                if(c==Code.Newobj || called.ReturnType.FullName!="System.Void")
                    stack.Add(Tag.Unknown);
                continue;
            }
            return (false,false,false);
        }
        return (false,false,false);
    }

    internal static SafeProfile Inspect(IEnumerable<MethodDefinition> source,
        MethodReference recipient)
    {
        if(source is null || recipient is null ||
            !recipient.Parameters.Any(p=>p.ParameterType is ByReferenceType br &&
                RtArray(br.ElementType)))
            throw new InvalidDataException("Actual typed byref RenderTexture[] target required");
        var defs=source.Where(m=>Same(m,recipient)).Take(2).ToList();
        if(defs.Count!=1 || !defs[0].HasBody)
            return new SafeProfile(defs.Count,0,0,0,0,0,0,0,false,false,false);
        MethodDefinition target=defs[0];
        var entries=Entries(target);
        int stores=0,newStores=0,otherRef=0,unproven=0,element=0,elemProven=0;
        int unknownElem=0;
        for(int i=0;i<target.Body.Instructions.Count;i++)
        {
            Code code=target.Body.Instructions[i].OpCode.Code;
            if(code is not (Code.Stind_Ref or Code.Stelem_Ref)) continue;
            var (proven,refStore,tracked)=TraceOne(target,i,entries);
            if(code==Code.Stind_Ref)
            {
                stores++;
                if(proven)newStores++;
                else if(tracked && refStore)otherRef++;
                else unproven++;
            }
            else
            {
                element++;
                if(proven)elemProven++;
                else unknownElem++;
            }
        }
        if(stores!=newStores+otherRef+unproven ||
            element!=elemProven+unknownElem)
            throw new InvalidDataException("Original array flow histogram mismatch");
        return new SafeProfile(1,stores,newStores,otherRef,unproven,
            element,elemProven,unknownElem,false,false,false);
    }
}
