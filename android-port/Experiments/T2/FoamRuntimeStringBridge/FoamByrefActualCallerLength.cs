// T2: original exact ref RenderTexture[] caller's int32 length argument.
// Source method names, IL and numeric source data stay in SHA-pinned runner.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamByrefActualCallerLength
{
    internal sealed record SafeProfile(
        int ExactOriginalByrefCallsites,
        bool OriginalNewarrLengthInt32FormalIdentified,
        string ExactActualLengthArgumentSourceCategory,
        bool ActualLengthArgumentDirectPositiveLiteralProven,
        bool? FourPrivateIndicesWithinThisCompiledCallerLength,
        bool ControlFlowOrPreexistingStackJoinedProven,
        bool OriginalRuntimeArrayLengthOrContentsVerified,
        bool OriginalNumericSourceValuesOrDigestsDisclosed);

    private readonly record struct Value(string Category,int? Literal=null);
    private static Value Unknown => new("unresolved_stack_or_producer");
    private static bool Same(MethodDefinition a,MethodReference b) =>
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

    private static int? ArgIndex(Instruction ins,MethodDefinition m)
    {
        int? raw=ins.OpCode.Code switch {
            Code.Ldarg_0 => 0, Code.Ldarg_1 => 1,
            Code.Ldarg_2 => 2, Code.Ldarg_3 => 3,
            Code.Ldarg or Code.Ldarg_S
                when ins.Operand is ParameterDefinition p =>
                p.Index+(m.HasThis?1:0),
            _ => null
        };
        return raw is int n && (!m.HasThis || n>0)
            ? n-(m.HasThis?1:0):null;
    }
    private static int? LocalIndex(Instruction ins) => ins.OpCode.Code switch {
        Code.Ldloc_0 or Code.Stloc_0 => 0,
        Code.Ldloc_1 or Code.Stloc_1 => 1,
        Code.Ldloc_2 or Code.Stloc_2 => 2,
        Code.Ldloc_3 or Code.Stloc_3 => 3,
        Code.Ldloc or Code.Ldloc_S or Code.Stloc or Code.Stloc_S
            when ins.Operand is VariableDefinition v => v.Index,
        _ => null
    };
    private static bool LocalLoad(Instruction ins) => ins.OpCode.Code is
        Code.Ldloc_0 or Code.Ldloc_1 or Code.Ldloc_2 or Code.Ldloc_3 or
        Code.Ldloc or Code.Ldloc_S;
    private static bool LocalStore(Instruction ins) => ins.OpCode.Code is
        Code.Stloc_0 or Code.Stloc_1 or Code.Stloc_2 or Code.Stloc_3 or
        Code.Stloc or Code.Stloc_S;
    private static Value Pop(List<Value> stack)
    {
        if(stack.Count==0) return Unknown;
        var value=stack[^1];
        stack.RemoveAt(stack.Count-1);
        return value;
    }
    private static bool RtArray(TypeReference t) =>
        t is ArrayType a && a.Rank==1 &&
        a.ElementType.FullName=="UnityEngine.RenderTexture";
    private static SafeProfile UnknownResult(string cat,bool formalFound=false) =>
        new(1,formalFound,cat,false,null,false,false,false);

    internal static SafeProfile Inspect(IEnumerable<MethodDefinition> originals,
        MethodDefinition owner,Instruction fieldAddress,Instruction actualCall,
        MethodReference called,int actualRefFormalIndex,
        FoamByrefLengthOrigin.SafeProfile priorLength,
        IReadOnlyCollection<int> privateFourIndexValues)
    {
        if(originals is null || owner is null || fieldAddress is null ||
            actualCall is null || called is null || priorLength is null ||
            privateFourIndexValues is null)
            throw new InvalidDataException("Missing exact original call provenance");
        var defs=originals.Where(m=>Same(m,called)).Take(2).ToList();
        if(defs.Count!=1 || !defs[0].HasBody ||
            priorLength.ResolvedLengthSourceCategory!="int32_argument")
            return UnknownResult("length_formal_not_source_proven");
        var definition=defs[0];
        var dil=definition.Body.Instructions;
        var newarrs=Enumerable.Range(0,dil.Count).Where(i=>
            dil[i].OpCode.Code==Code.Newarr &&
            dil[i].Operand is TypeReference t &&
            t.FullName=="UnityEngine.RenderTexture").ToList();
        if(newarrs.Count!=1) return UnknownResult("newarr_not_unique");
        int previous=newarrs[0]-1;
        while(previous>=0 && dil[previous].OpCode.Code==Code.Nop) previous--;
        if(previous<0) return UnknownResult("newarr_formal_missing");
        int? intFormal=ArgIndex(dil[previous],definition);
        if(intFormal is not int numericParam ||
            numericParam>=definition.Parameters.Count ||
            definition.Parameters[numericParam].ParameterType.FullName!="System.Int32")
            return UnknownResult("newarr_int_formal_not_identified");
        var il=owner.Body.Instructions;
        int start=il.IndexOf(fieldAddress),end=il.IndexOf(actualCall);
        if(start<0 || end<=start || end-start>40 ||
            actualCall.Operand is not MethodReference callRef ||
            callRef.FullName!=called.FullName ||
            actualRefFormalIndex<0 ||
            actualRefFormalIndex>=called.Parameters.Count ||
            called.Parameters[actualRefFormalIndex].ParameterType is not ByReferenceType br ||
            !RtArray(br.ElementType))
            return UnknownResult("actual_callsite_not_proven",true);
        // A branch/exception entry between the field address and call may
        // bypass the address. Refuse a guessed path.
        var entries=new HashSet<Instruction>();
        foreach(var op in il)
        {
            if(op.Operand is Instruction t) entries.Add(t);
            if(op.Operand is Instruction[] arr)
                foreach(var targetInstruction in arr) entries.Add(targetInstruction);
        }
        foreach(var eh in owner.Body.ExceptionHandlers)
        {
            if(eh.TryStart!=null) entries.Add(eh.TryStart);
            if(eh.HandlerStart!=null) entries.Add(eh.HandlerStart);
            if(eh.FilterStart!=null) entries.Add(eh.FilterStart);
        }
        for(int i=start+1;i<=end;i++)
            if(entries.Contains(il[i]))
                return UnknownResult("branch_join_or_exception_entry",true);
        var stack=new List<Value>{new("exact_ref_array_address")};
        var locals=new Dictionary<int,Value>();
        for(int i=start+1;i<end;i++)
        {
            var ins=il[i];
            var code=ins.OpCode.Code;
            if(code==Code.Nop) continue;
            if(ins.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw or FlowControl.Break)
                return UnknownResult("intervening_control_flow",true);
            if(I4(ins) is int literal)
            {
                stack.Add(new Value("direct_i4",literal));
                continue;
            }
            if(ArgIndex(ins,owner) is int a)
            {
                stack.Add(new Value(a<owner.Parameters.Count &&
                    owner.Parameters[a].ParameterType.FullName=="System.Int32"
                    ?"int32_argument":"other_argument"));
                continue;
            }
            if(LocalStore(ins))
            {
                var idx=LocalIndex(ins);
                if(idx is null) return UnknownResult("unknown_local_store",true);
                locals[idx.Value]=Pop(stack);
                continue;
            }
            if(LocalLoad(ins))
            {
                var idx=LocalIndex(ins);
                if(idx is null) return UnknownResult("unknown_local_load",true);
                var src=locals.GetValueOrDefault(idx.Value,Unknown);
                stack.Add(src.Literal is int k
                    ? new Value("same_block_local_i4",k)
                    : new Value("local_from_"+src.Category));
                continue;
            }
            if(code==Code.Dup)
            {
                stack.Add(stack.Count>0?stack[^1]:Unknown);
                continue;
            }
            if(code==Code.Pop){Pop(stack);continue;}
            if(code is Code.Ldnull or Code.Ldstr or Code.Ldtoken or Code.Ldsfld)
            {
                stack.Add(Unknown);
                continue;
            }
            if(code is Code.Conv_I4 or Code.Conv_U4 or Code.Conv_I or Code.Conv_U)
            {
                Pop(stack);stack.Add(new Value("numeric_conversion"));continue;
            }
            if(code is Code.Add or Code.Sub or Code.Mul or Code.Div or Code.And)
            {
                Pop(stack);Pop(stack);stack.Add(new Value("numeric_arithmetic"));continue;
            }
            if(code==Code.Ldfld)
            {
                Pop(stack);stack.Add(new Value("field_load"));continue;
            }
            if(code is Code.Call or Code.Callvirt)
            {
                if(ins.Operand is not MethodReference nested)
                    return UnknownResult("unknown_nested_call",true);
                int total=nested.Parameters.Count+(nested.HasThis?1:0);
                if(total>32) return UnknownResult("nested_call_budget",true);
                while(stack.Count<total) stack.Insert(0,Unknown);
                var args=stack.GetRange(stack.Count-total,total);
                if(args.Any(x=>x.Category=="exact_ref_array_address"))
                    return UnknownResult("ref_escaped_to_nested_call",true);
                stack.RemoveRange(stack.Count-total,total);
                if(nested.ReturnType.FullName!="System.Void")
                    stack.Add(new Value(nested.ReturnType.FullName=="System.Int32"
                        ?"int32_call_return":"other_call_return"));
                continue;
            }
            if(code==Code.Ldlen)
            {
                Pop(stack);stack.Add(new Value("array_length"));continue;
            }
            if(code==Code.Ldind_Ref)
            {
                Pop(stack);stack.Add(new Value("indirect_reference_load"));continue;
            }
            return UnknownResult("unsupported_opcode_before_call",true);
        }
        int required=called.Parameters.Count+(called.HasThis?1:0);
        if(required>33) return UnknownResult("call_budget",true);
        while(stack.Count<required)stack.Insert(0,Unknown);
        int startArg=stack.Count-required+(called.HasThis?1:0);
        if(stack[startArg+actualRefFormalIndex].Category!="exact_ref_array_address")
            return UnknownResult("ref_formal_receiver_not_proven",true);
        Value length=stack[startArg+numericParam];
        bool positive=length.Literal is int n && n>0;
        bool? bounds=positive && privateFourIndexValues.Count==4
            ? privateFourIndexValues.All(x=>x>=0 && x<length.Literal!.Value)
            : null;
        return new SafeProfile(1,true,length.Category,positive,bounds,
            false,false,false);
    }
}
