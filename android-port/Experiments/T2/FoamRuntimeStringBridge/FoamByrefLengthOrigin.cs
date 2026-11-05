// T2: SHA-original Foam newarr length; retain private symbols and numbers in CI.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamByrefLengthOrigin
{
    internal sealed record SafeProfile(
        int ExactRecipientDefinitions,
        int ExactOriginalRenderTextureNewarrSites,
        string ImmediateLengthProducerCategory,
        string ResolvedLengthSourceCategory,
        bool SameBasicBlockLocalDefinitionFound,
        bool CompileTimePositiveArrayLengthProven,
        bool? FourPrivateOriginalIndicesInBoundsForCompiledLength,
        bool BranchJoinsOrRuntimeExecutionVerified,
        bool OriginalNumericValuesOrDigestsExposed);

    private readonly record struct Origin(string Category, int? Literal = null);
    private static bool Matches(MethodDefinition a, MethodReference b) =>
        a.FullName==b.FullName && a.HasThis==b.HasThis &&
        a.Parameters.Count==b.Parameters.Count &&
        a.Parameters.Zip(b.Parameters,
            (p,q)=>p.ParameterType.FullName==q.ParameterType.FullName).All(x=>x);
    private static int? I4(Instruction ins) => ins.OpCode.Code switch {
        Code.Ldc_I4_M1 => -1, Code.Ldc_I4_0 => 0, Code.Ldc_I4_1 => 1,
        Code.Ldc_I4_2 => 2, Code.Ldc_I4_3 => 3, Code.Ldc_I4_4 => 4,
        Code.Ldc_I4_5 => 5, Code.Ldc_I4_6 => 6, Code.Ldc_I4_7 => 7,
        Code.Ldc_I4_8 => 8, Code.Ldc_I4_S when ins.Operand is sbyte n => n,
        Code.Ldc_I4 when ins.Operand is int n => n, _ => null
    };
    private static int? LocalIndex(Instruction op) => op.OpCode.Code switch {
        Code.Ldloc_0 or Code.Stloc_0 => 0,
        Code.Ldloc_1 or Code.Stloc_1 => 1,
        Code.Ldloc_2 or Code.Stloc_2 => 2,
        Code.Ldloc_3 or Code.Stloc_3 => 3,
        Code.Ldloc or Code.Ldloc_S or Code.Stloc or Code.Stloc_S
            when op.Operand is VariableDefinition v => v.Index, _ => null
    };
    private static bool Load(Instruction op) => op.OpCode.Code is
        Code.Ldloc_0 or Code.Ldloc_1 or Code.Ldloc_2 or Code.Ldloc_3 or
        Code.Ldloc or Code.Ldloc_S;
    private static bool Store(Instruction op) => op.OpCode.Code is
        Code.Stloc_0 or Code.Stloc_1 or Code.Stloc_2 or Code.Stloc_3 or
        Code.Stloc or Code.Stloc_S;
    private static int Prev(Mono.Collections.Generic.Collection<Instruction> il,
        int start, int end)
    {
        for(int i=end-1;i>=start;i--)
            if(il[i].OpCode.Code!=Code.Nop) return i;
        return -1;
    }
    private static HashSet<Instruction> Entries(MethodDefinition method)
    {
        var il=method.Body.Instructions;
        var entries=new HashSet<Instruction>();
        if(il.Count>0) entries.Add(il[0]);
        for(int i=0;i<il.Count;i++)
        {
            if(il[i].Operand is Instruction target) entries.Add(target);
            if(il[i].Operand is Instruction[] targets)
                foreach(var t in targets) entries.Add(t);
            if(il[i].OpCode.FlowControl is FlowControl.Branch or
                FlowControl.Cond_Branch or FlowControl.Return or
                FlowControl.Throw or FlowControl.Break)
                if(i+1<il.Count) entries.Add(il[i+1]);
        }
        foreach(var h in method.Body.ExceptionHandlers)
        {
            if(h.TryStart!=null) entries.Add(h.TryStart);
            if(h.TryEnd!=null) entries.Add(h.TryEnd);
            if(h.HandlerStart!=null) entries.Add(h.HandlerStart);
            if(h.HandlerEnd!=null) entries.Add(h.HandlerEnd);
            if(h.FilterStart!=null) entries.Add(h.FilterStart);
        }
        return entries;
    }
    private static Origin Resolve(MethodDefinition method, int producer,
        int blockStart, int depth)
    {
        var il=method.Body.Instructions;
        if(producer<blockStart || depth>3)
            return new Origin("unresolved_block_or_depth");
        var op=il[producer];
        if(I4(op) is int n) return new Origin("direct_i4",n);
        if(Load(op))
        {
            int? index=LocalIndex(op);
            if(index is null) return new Origin("unresolved_local_index");
            for(int i=producer-1;i>=blockStart;i--)
                if(Store(il[i]) && LocalIndex(il[i])==index)
                {
                    int value=Prev(il,blockStart,i);
                    if(value<blockStart)
                        return new Origin("local_value_outside_block");
                    var src=Resolve(method,value,blockStart,depth+1);
                    return src.Literal is int k
                        ? new Origin("same_block_local_i4",k)
                        : new Origin("same_block_local_from_"+src.Category);
                }
            return new Origin("local_definition_outside_block");
        }
        int? raw=op.OpCode.Code switch {
            Code.Ldarg_0 => 0, Code.Ldarg_1 => 1,
            Code.Ldarg_2 => 2, Code.Ldarg_3 => 3,
            Code.Ldarg or Code.Ldarg_S
                when op.Operand is ParameterDefinition p =>
                p.Index+(method.HasThis?1:0),
            _ => null
        };
        if(raw is int r)
        {
            int parameterIndex=r-(method.HasThis?1:0);
            return new Origin(parameterIndex>=0 && parameterIndex<method.Parameters.Count &&
                method.Parameters[parameterIndex].ParameterType.FullName=="System.Int32"
                ?"int32_argument":"other_argument");
        }
        if(op.OpCode.Code==Code.Ldlen) return new Origin("array_length");
        if(op.OpCode.Code is Code.Call or Code.Callvirt)
            return new Origin(op.Operand is MethodReference callee &&
                callee.ReturnType.FullName=="System.Int32"
                ?"int32_call_return":"call_type_unknown");
        if(op.OpCode.Code is Code.Ldfld or Code.Ldsfld)
            return new Origin(op.Operand is FieldReference f &&
                f.FieldType.FullName=="System.Int32"
                ?"int32_field_load":"field_type_unknown");
        if(op.OpCode.Code is Code.Conv_I4 or Code.Conv_U4 or
            Code.Conv_I or Code.Conv_U) return new Origin("numeric_conversion");
        if(op.OpCode.Code is Code.Add or Code.Sub or Code.Mul or Code.Div or
            Code.Div_Un or Code.Rem or Code.And or Code.Or or Code.Xor or
            Code.Shl or Code.Shr) return new Origin("numeric_arithmetic");
        if(op.OpCode.Code is Code.Ldind_I4 or Code.Ldind_U4)
            return new Origin("indirect_int32_load");
        return new Origin("unsupported_producer");
    }

    internal static SafeProfile Inspect(IEnumerable<MethodDefinition> source,
        MethodReference recipient, FoamByrefAllocationFlow.SafeProfile allocation,
        IReadOnlyCollection<int> privateFour)
    {
        if(source is null || recipient is null || allocation is null ||
            privateFour is null) throw new InvalidDataException("Missing source evidence");
        var definitions=source.Where(m=>Matches(m,recipient)).Take(2).ToList();
        if(definitions.Count!=1 || !definitions[0].HasBody)
            return new SafeProfile(definitions.Count,0,"unresolved_recipient",
                "unresolved_recipient",false,false,null,false,false);
        var method=definitions[0];
        var il=method.Body.Instructions;
        var newarr=Enumerable.Range(0,il.Count).Where(i=>
            il[i].OpCode.Code==Code.Newarr &&
            il[i].Operand is TypeReference element &&
            element.FullName=="UnityEngine.RenderTexture").ToList();
        if(newarr.Count!=1 ||
            allocation.ProvenNewarrRenderTextureArrayToRefFormalStores!=1)
            return new SafeProfile(1,newarr.Count,"ambiguous_allocation",
                "ambiguous_allocation",false,false,null,false,false);
        int site=newarr[0], blockStart=site;
        var entries=Entries(method);
        while(blockStart>0 && !entries.Contains(il[blockStart]))
            blockStart--;
        int producer=Prev(il,blockStart,site);
        if(producer<blockStart)
            return new SafeProfile(1,1,"no_same_block_producer",
                "no_same_block_producer",false,false,null,false,false);
        var op=il[producer];
        string immediate=I4(op).HasValue?"ldc_i4":
            Load(op)?"ldloc":
            op.OpCode.Code is Code.Ldarg or Code.Ldarg_S or Code.Ldarg_0 or
                Code.Ldarg_1 or Code.Ldarg_2 or Code.Ldarg_3?"ldarg":
            op.OpCode.Code==Code.Ldlen?"ldlen":
            op.OpCode.Code is Code.Call or Code.Callvirt?"call":
            op.OpCode.Code is Code.Ldfld or Code.Ldsfld?"field":
            op.OpCode.Code is Code.Add or Code.Sub or Code.Mul or Code.Div
                ?"arithmetic":"other";
        var origin=Resolve(method,producer,blockStart,0);
        bool local=origin.Category.StartsWith("same_block_local_",StringComparison.Ordinal);
        bool positive=origin.Literal is int n && n>0;
        bool? inRange=positive && privateFour.Count==4
            ? privateFour.All(v=>v>=0 && v<origin.Literal!.Value):null;
        return new SafeProfile(1,1,immediate,origin.Category,local,
            positive,inRange,false,false);
    }
}
