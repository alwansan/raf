// T2: fail-closed bounded same-basic-block stack source slice.
// Source-original instruction operands and method names stay in private CI scratch.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamReturnWriterStackSlice
{
    internal sealed record SafeProfile(
        string AnalysisStatus,
        string ConditionalSourceOpcodeFamily,
        bool SameBlockSurvivingValueSourceFound,
        bool MultiInputVoidCallConsumptionModeled,
        bool WholeFunctionBranchJoinProven=false,
        bool OriginalRuntimeValueOrPixelsVerified=false,
        bool PrivateSourceNamesIlOrValuesDisclosed=false);

    // A block entry may have a non-empty incoming stack. We never claim
    // to know values that predate the block or cross handler/branch entries.
    private static HashSet<Instruction> BlockEntries(MethodDefinition method)
    {
        var il=method.Body.Instructions;
        var entries=new HashSet<Instruction>();
        if(il.Count!=0) entries.Add(il[0]);
        for(int i=0;i<il.Count;i++)
        {
            if(il[i].Operand is Instruction dest) entries.Add(dest);
            if(il[i].Operand is Instruction[] dests)
                foreach(var branchDestination in dests) entries.Add(branchDestination);
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

    private static bool IsStore(Instruction ins) => ins.OpCode.Code is
        Code.Stloc or Code.Stloc_S or Code.Stloc_0 or Code.Stloc_1 or
        Code.Stloc_2 or Code.Stloc_3;

    private static bool Effect(Instruction ins,out int pop,out int push)
    {
        pop=0; push=0;
        switch(ins.OpCode.Code)
        {
            case Code.Nop: break;
            case Code.Ldnull:
            case Code.Ldarg: case Code.Ldarg_S:
            case Code.Ldarg_0: case Code.Ldarg_1: case Code.Ldarg_2:
            case Code.Ldarg_3: case Code.Ldarga: case Code.Ldarga_S:
            case Code.Ldloc: case Code.Ldloc_S:
            case Code.Ldloc_0: case Code.Ldloc_1: case Code.Ldloc_2:
            case Code.Ldloc_3: case Code.Ldloca: case Code.Ldloca_S:
            case Code.Ldc_I4: case Code.Ldc_I4_S: case Code.Ldc_I4_M1:
            case Code.Ldc_I4_0: case Code.Ldc_I4_1: case Code.Ldc_I4_2:
            case Code.Ldc_I4_3: case Code.Ldc_I4_4: case Code.Ldc_I4_5:
            case Code.Ldc_I4_6: case Code.Ldc_I4_7: case Code.Ldc_I4_8:
            case Code.Ldc_I8: case Code.Ldc_R4: case Code.Ldc_R8:
            case Code.Ldstr: case Code.Ldtoken:
            case Code.Ldsfld: case Code.Ldsflda:
            case Code.Ldftn: case Code.Sizeof:
                push=1; break;
            case Code.Dup: pop=1; push=2; break;
            case Code.Pop:
            case Code.Stloc: case Code.Stloc_S:
            case Code.Stloc_0: case Code.Stloc_1: case Code.Stloc_2:
            case Code.Stloc_3: case Code.Starg: case Code.Starg_S:
            case Code.Stsfld: case Code.Initobj:
                pop=1; break;
            case Code.Ldfld: case Code.Ldflda:
            case Code.Ldlen: case Code.Ldind_Ref:
            case Code.Ldind_I4: case Code.Ldobj:
            case Code.Castclass: case Code.Isinst:
            case Code.Box: case Code.Unbox: case Code.Unbox_Any:
            case Code.Neg: case Code.Not:
            case Code.Conv_I: case Code.Conv_I1: case Code.Conv_I2:
            case Code.Conv_I4: case Code.Conv_I8:
            case Code.Conv_U: case Code.Conv_U1: case Code.Conv_U2:
            case Code.Conv_U4: case Code.Conv_U8:
            case Code.Conv_R4: case Code.Conv_R8:
            case Code.Conv_R_Un:
            case Code.Conv_Ovf_I: case Code.Conv_Ovf_U:
                pop=1; push=1; break;
            case Code.Ldelem_Ref: case Code.Ldelema:
            case Code.Add: case Code.Sub: case Code.Mul:
            case Code.Div: case Code.Div_Un:
            case Code.Ceq: case Code.Cgt: case Code.Clt:
                pop=2; push=1; break;
            case Code.Stfld: case Code.Stind_Ref: case Code.Stobj:
                pop=2; break;
            case Code.Stelem_Ref:
                pop=3; break;
            case Code.Newarr:
                pop=1; push=1; break;
            case Code.Newobj:
                if(ins.Operand is not MethodReference ctor) return false;
                if(ctor.CallingConvention==MethodCallingConvention.VarArg) return false;
                pop=ctor.Parameters.Count; push=1; break;
            case Code.Call: case Code.Callvirt:
                if(ins.Operand is not MethodReference call) return false;
                if(call.CallingConvention==MethodCallingConvention.VarArg) return false;
                pop=call.Parameters.Count+(call.HasThis?1:0);
                push=call.ReturnType.MetadataType==MetadataType.Void?0:1;
                break;
            default: return false;
        }
        return true;
    }

    private static string Producer(Instruction ins) => ins.OpCode.Code switch
    {
        Code.Ldnull => "literal_null",
        Code.Newobj when ins.Operand is MethodReference ctor &&
            ctor.DeclaringType.FullName=="UnityEngine.RenderTexture" =>
            "named_rendertexture_constructor",
        Code.Newobj => "other_constructor",
        Code.Call or Code.Callvirt when ins.Operand is MethodReference mr &&
            mr.ReturnType.FullName=="UnityEngine.RenderTexture" =>
            "named_rendertexture_call_result",
        Code.Call or Code.Callvirt => "other_call_result",
        Code.Ldloc or Code.Ldloc_S or Code.Ldloc_0 or Code.Ldloc_1
          or Code.Ldloc_2 or Code.Ldloc_3 => "local_load",
        Code.Ldarg or Code.Ldarg_S or Code.Ldarg_0 or Code.Ldarg_1
          or Code.Ldarg_2 or Code.Ldarg_3 => "argument_load",
        Code.Ldfld or Code.Ldsfld => "field_load",
        Code.Ldind_Ref or Code.Ldelem_Ref => "indirect_reference_load",
        Code.Ldloca or Code.Ldloca_S or Code.Ldarga or Code.Ldarga_S
          or Code.Ldflda or Code.Ldsflda => "address_load",
        Code.Castclass or Code.Isinst => "reference_cast",
        Code.Ldstr => "string_literal",
        Code.Ldc_I4 or Code.Ldc_I4_S or Code.Ldc_I4_M1 or Code.Ldc_I4_0
          or Code.Ldc_I4_1 or Code.Ldc_I4_2 or Code.Ldc_I4_3 or Code.Ldc_I4_4
          or Code.Ldc_I4_5 or Code.Ldc_I4_6 or Code.Ldc_I4_7 or Code.Ldc_I4_8 =>
            "integer_literal",
        _ => "other_stack_producer"
    };

    private static SafeProfile Result(string state,string producer="unresolved",
        bool found=false,bool modeled=false) =>
        new(state,producer,found,modeled,false,false,false);

    internal static SafeProfile Inspect(MethodDefinition method,
        Instruction returnLocalWriter,int maxInstructions=192,int maxDepth=128)
    {
        if(method==null || !method.HasBody || returnLocalWriter==null ||
            maxInstructions<=0 || maxDepth<=0)
            return Result("invalid_input");
        var il=method.Body.Instructions;
        int writer=il.IndexOf(returnLocalWriter);
        if(writer<1 || !IsStore(returnLocalWriter))
            return Result("invalid_writer");
        int callIndex=writer-1;
        while(callIndex>=0 && il[callIndex].OpCode.Code==Code.Nop)
            callIndex--;
        if(callIndex<0 || il[callIndex].OpCode.Code is not
            (Code.Call or Code.Callvirt) ||
            il[callIndex].Operand is not MethodReference call ||
            call.ReturnType.MetadataType!=MetadataType.Void ||
            call.CallingConvention==MethodCallingConvention.VarArg)
            return Result("not_a_supported_void_call");
        int args=call.Parameters.Count+(call.HasThis?1:0);
        if(args<2) return Result("not_multi_input_void_call");

        var entries=BlockEntries(method);
        // A branch directly to stloc bypasses the inspected call.
        for(int i=callIndex+1;i<=writer;i++)
            if(entries.Contains(il[i])) return Result("alternate_entry_before_store");
        int start=0;
        for(int i=0;i<=callIndex;i++)
            if(entries.Contains(il[i])) start=i;
        int distance=1,steps=0;
        for(int i=writer-1;i>=start;i--)
        {
            if(++steps>maxInstructions) return Result("instruction_budget",modeled:true);
            var ins=il[i];
            if(ins.OpCode.Code==Code.Nop) continue;
            if(ins.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw or FlowControl.Break)
                return Result("control_flow_crossing",modeled:true);
            if(!Effect(ins,out int pop,out int push))
                return Result("unsupported_stack_opcode",modeled:true);
            if(pop<0 || push<0 || pop>maxDepth || push>maxDepth)
                return Result("stack_effect_budget",modeled:true);
            // Dup copies a single source value into two equivalent slots.
            if(ins.OpCode.Code==Code.Dup)
            {
                if(distance<=2) distance=1;
                else distance--;
                continue;
            }
            if(push>=distance)
                return Result("same_block_stack_source_found",
                    Producer(ins),true,true);
            distance=distance-push+pop;
            if(distance>maxDepth || distance<1)
                return Result("stack_depth_budget",modeled:true);
        }
        // The surviving reference may originate at a predecessor block,
        // so this is never a positive source or non-null object proof.
        return Result("incoming_stack_unresolved",modeled:true);
    }

    internal static void RunSyntheticControls()
    {
        using var m=ModuleDefinition.CreateModule("T2PublicStackSlice",ModuleKind.Dll);
        var host=new TypeDefinition("PublicFixture","SyntheticStackSlice",
            Mono.Cecil.TypeAttributes.Public|Mono.Cecil.TypeAttributes.Class,
            m.TypeSystem.Object);
        m.Types.Add(host);
        var rt=new TypeReference("UnityEngine","RenderTexture",m,m.TypeSystem.Object.Scope);
        var ctor=new MethodReference(".ctor",m.TypeSystem.Void,rt){HasThis=true};
        var multi=new MethodReference("SyntheticConsumeTwo",m.TypeSystem.Void,host)
            {HasThis=false};
        multi.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        multi.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        var rtAndInt=new MethodReference("SyntheticConsumeObjectAndInt",
            m.TypeSystem.Void,host){HasThis=false};
        rtAndInt.Parameters.Add(new ParameterDefinition(rt));
        rtAndInt.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        (MethodDefinition Method,Instruction Writer,ILProcessor Il) Build(string name)
        {
            var method=new MethodDefinition(name,
                Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
                rt);
            host.Methods.Add(method);
            method.Body.InitLocals=true;
            method.Body.Variables.Add(new VariableDefinition(rt));
            var ip=method.Body.GetILProcessor();
            var wr=ip.Create(OpCodes.Stloc_0);
            return (method,wr,ip);
        }
        void End((MethodDefinition Method,Instruction Writer,ILProcessor Il) x)
        {
            x.Il.Append(x.Writer);
            x.Il.Append(x.Il.Create(OpCodes.Ldloc_0));
            x.Il.Append(x.Il.Create(OpCodes.Ret));
        }
        var origin=Build("SyntheticConstructorSurvivesTwoArgs");
        origin.Il.Append(origin.Il.Create(OpCodes.Newobj,ctor));
        origin.Il.Append(origin.Il.Create(OpCodes.Ldc_I4_0));
        origin.Il.Append(origin.Il.Create(OpCodes.Ldc_I4_1));
        origin.Il.Append(origin.Il.Create(OpCodes.Call,multi));
        End(origin);
        var positive=Inspect(origin.Method,origin.Writer);
        if(!positive.SameBlockSurvivingValueSourceFound ||
            positive.ConditionalSourceOpcodeFamily!="named_rendertexture_constructor" ||
            !positive.MultiInputVoidCallConsumptionModeled ||
            positive.OriginalRuntimeValueOrPixelsVerified)
            throw new InvalidDataException("Synthetic RT constructor stack slice failed");

        var literal=Build("SyntheticNullSurvivesTwoArgs");
        literal.Il.Append(literal.Il.Create(OpCodes.Ldnull));
        literal.Il.Append(literal.Il.Create(OpCodes.Ldc_I4_0));
        literal.Il.Append(literal.Il.Create(OpCodes.Ldc_I4_1));
        literal.Il.Append(literal.Il.Create(OpCodes.Call,multi));
        End(literal);
        if(Inspect(literal.Method,literal.Writer).ConditionalSourceOpcodeFamily
            !="literal_null")
            throw new InvalidDataException("Synthetic literal null misclassified");

        var duplicate=Build("SyntheticDupSurvivesTwoArgs");
        duplicate.Il.Append(duplicate.Il.Create(OpCodes.Newobj,ctor));
        duplicate.Il.Append(duplicate.Il.Create(OpCodes.Dup));
        duplicate.Il.Append(duplicate.Il.Create(OpCodes.Ldc_I4_0));
        duplicate.Il.Append(duplicate.Il.Create(OpCodes.Call,rtAndInt));
        End(duplicate);
        if(Inspect(duplicate.Method,duplicate.Writer).ConditionalSourceOpcodeFamily
            !="named_rendertexture_constructor")
            throw new InvalidDataException("Synthetic dup did not resolve original producer");

        var missing=Build("SyntheticMissingSource");
        missing.Il.Append(missing.Il.Create(OpCodes.Ldc_I4_0));
        missing.Il.Append(missing.Il.Create(OpCodes.Ldc_I4_1));
        missing.Il.Append(missing.Il.Create(OpCodes.Call,multi));
        End(missing);
        var unresolved=Inspect(missing.Method,missing.Writer);
        if(unresolved.SameBlockSurvivingValueSourceFound ||
           unresolved.AnalysisStatus!="incoming_stack_unresolved")
            throw new InvalidDataException("Synthetic underflow was falsely classified");

        var branch=Build("SyntheticBranchEntryBoundary");
        branch.Il.Append(branch.Il.Create(OpCodes.Newobj,ctor));
        branch.Il.Append(branch.Il.Create(OpCodes.Ldc_I4_0));
        branch.Il.Append(branch.Il.Create(OpCodes.Ldc_I4_1));
        var targetCall=branch.Il.Create(OpCodes.Call,multi);
        branch.Il.Append(branch.Il.Create(OpCodes.Br_S,targetCall));
        branch.Il.Append(targetCall);
        End(branch);
        if(Inspect(branch.Method,branch.Writer).SameBlockSurvivingValueSourceFound)
            throw new InvalidDataException("Synthetic cross-branch value promoted");

        var unsupported=Build("SyntheticUnknownStackOperation");
        unsupported.Il.Append(unsupported.Il.Create(OpCodes.Newobj,ctor));
        unsupported.Il.Append(unsupported.Il.Create(OpCodes.Ldc_I4_0));
        unsupported.Il.Append(unsupported.Il.Create(OpCodes.Localloc));
        unsupported.Il.Append(unsupported.Il.Create(OpCodes.Ldc_I4_1));
        unsupported.Il.Append(unsupported.Il.Create(OpCodes.Call,multi));
        End(unsupported);
        if(Inspect(unsupported.Method,unsupported.Writer).SameBlockSurvivingValueSourceFound)
            throw new InvalidDataException("Unsupported opcode promoted source");

        if(Inspect(origin.Method,origin.Writer,maxInstructions:1)
            .SameBlockSurvivingValueSourceFound)
            throw new InvalidDataException("Instruction budget bypassed");
    }
}
