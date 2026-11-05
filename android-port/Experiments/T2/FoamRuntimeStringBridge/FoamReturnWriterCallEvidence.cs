// T2: bounded, source-safe original RenderTexture-return local call provenance.
// Source method identities and original IL are never emitted in the report.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamReturnWriterCallEvidence
{
    internal sealed record SafeProfile(
        bool PrecedingInstructionIsCall,
        string DeclaredCallReturnCategory,
        bool CallHasDeclaredReturnValue,
        bool AlternateControlFlowEntryBetweenCallAndStore,
        bool ConditionalCallResultIsImmediateStoreStackTop,
        bool DeclaredReturnExactlyRenderTextureByName,
        bool OriginalAssemblyTypeIdentityVerified,
        bool RuntimeCallOrNonNullVerified,
        bool OriginalSymbolsOrIlDisclosed,
        string ImmediatePreCallOpcodeCategory="not_examined",
        string CallConsumedOperandCategory="not_examined",
        bool RetainedDuplicateAfterOneInputVoidCall=false,
        bool OriginalRuntimeStackContentsVerified=false,
        FoamReturnWriterStackSlice.SafeProfile? OriginalSameBlockSurvivingStackSlice=null);

    private static string ReturnCategory(TypeReference type) =>
        type.MetadataType == MetadataType.Void ? "void_return" :
        type is ByReferenceType or PointerType ? "byref_or_pointer_return" :
        type is GenericParameter ? "generic_parameter_return" :
        type.FullName == "UnityEngine.RenderTexture" ? "rendertexture_named_return" :
        type.FullName == "UnityEngine.Texture" ? "texture_named_return" :
        type.FullName == "UnityEngine.Object" ? "unity_object_named_return" :
        type.IsValueType ? "other_value_type_return" : "other_reference_return";

    // Entries here are only possible nonsequential branch/exception edges.
    // Ordinary fallthrough after a call must not be rejected as a join.
    private static HashSet<Instruction> NonSequentialEntries(MethodDefinition method)
    {
        var targets = new HashSet<Instruction>();
        foreach(var ins in method.Body.Instructions)
        {
            if(ins.Operand is Instruction dest) targets.Add(dest);
            if(ins.Operand is Instruction[] dests)
                foreach(var branchDestination in dests) targets.Add(branchDestination);
        }
        foreach(var h in method.Body.ExceptionHandlers)
        {
            if(h.TryStart != null) targets.Add(h.TryStart);
            if(h.TryEnd != null) targets.Add(h.TryEnd);
            if(h.HandlerStart != null) targets.Add(h.HandlerStart);
            if(h.HandlerEnd != null) targets.Add(h.HandlerEnd);
            if(h.FilterStart != null) targets.Add(h.FilterStart);
        }
        return targets;
    }

    internal static SafeProfile Inspect(MethodDefinition method,
        Instruction returnLocalWriter, bool localDeclaredRenderTexture)
    {
        if(method == null || !method.HasBody || returnLocalWriter == null ||
            !localDeclaredRenderTexture)
            return new SafeProfile(false,"not_examined",false,true,false,false,
                false,false,false);
        var il = method.Body.Instructions;
        var at=il.IndexOf(returnLocalWriter);
        if(at<=0 || returnLocalWriter.OpCode.Code is not
            (Code.Stloc or Code.Stloc_S or Code.Stloc_0 or Code.Stloc_1 or
             Code.Stloc_2 or Code.Stloc_3))
            return new SafeProfile(false,"not_examined",false,true,false,false,
                false,false,false);
        int prior=at-1;
        while(prior>=0 && il[prior].OpCode.Code==Code.Nop) prior--;
        if(prior<0 || il[prior].OpCode.Code is not (Code.Call or Code.Callvirt) ||
            il[prior].Operand is not MethodReference call)
            return new SafeProfile(false,"not_a_typed_call",false,true,false,false,
                false,false,false);
        var nonSequential=NonSequentialEntries(method);
        bool bypass=false;
        // Including writer itself blocks a branch bypassing the immediately
        // preceding call, and including intervening nop rejects hidden entry.
        for(int i=prior+1;i<=at;i++)
            if(nonSequential.Contains(il[i])) bypass=true;
        var category=ReturnCategory(call.ReturnType);
        bool pushes=category!="void_return";
        bool namedRt=category=="rendertexture_named_return";
        int pre=prior-1;
        while(pre>=0 && il[pre].OpCode.Code==Code.Nop) pre--;
        string preCategory=pre<0 ? "no_prior_instruction" :
            il[pre].OpCode.Code switch {
                Code.Dup => "dup",
                Code.Ldnull => "ldnull",
                Code.Ldloc or Code.Ldloc_S or Code.Ldloc_0 or Code.Ldloc_1
                  or Code.Ldloc_2 or Code.Ldloc_3 => "ldloc",
                Code.Ldarg or Code.Ldarg_S or Code.Ldarg_0 or Code.Ldarg_1
                  or Code.Ldarg_2 or Code.Ldarg_3 => "ldarg",
                Code.Call or Code.Callvirt => "call",
                Code.Newobj => "newobj",
                Code.Ldfld or Code.Ldsfld => "field_load",
                _ => "other"
            };
        int count=call.Parameters.Count+(call.HasThis?1:0);
        string consumes=count==0 ? "none" : count==1 ? "one" : "multiple";
        bool bypassPre=false;
        if(pre>=0)
            for(int i=pre+1;i<=at;i++)
                if(nonSequential.Contains(il[i])) bypassPre=true;
        bool retained=category=="void_return" && count==1 &&
            preCategory=="dup" && !bypassPre;
        // Conditional IL evaluation-stack result, NOT original runtime
        // call execution, value non-null, assignment type verification, or
        // Unity engine assembly identity. Reference equality by name alone
        // is NOT a proof of source/Unity assembly identity.
        var slice=FoamReturnWriterStackSlice.Inspect(method,returnLocalWriter);
        return new SafeProfile(true,category,pushes,bypass,
            pushes && !bypass,namedRt,false,false,false,
            preCategory,consumes,retained,false,slice);
    }

    // Explicit synthetic-only fixtures: no source game assembly and no
    // private method names are constructed or logged.
    internal static void RunSyntheticControls()
    {
        using var module=ModuleDefinition.CreateModule(
            "T2SyntheticWriterCallCategories",ModuleKind.Dll);
        var host=new TypeDefinition("PublicFixture","SyntheticReturnWriter",
            Mono.Cecil.TypeAttributes.Public|Mono.Cecil.TypeAttributes.Class,
            module.TypeSystem.Object);
        module.Types.Add(host);
        var rt=new TypeReference("UnityEngine","RenderTexture",module,
            module.TypeSystem.Object.Scope);
        MethodReference Ref(string name,TypeReference type) =>
            new MethodReference(name,type,host){HasThis=false};
        (MethodDefinition Method,Instruction Writer) Create(
            MethodReference called,bool addNop=false,bool bypass=false,
            bool includeCall=true)
        {
            var method=new MethodDefinition("SyntheticWriter",
                Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
                rt);
            host.Methods.Add(method);
            method.Body.InitLocals=true;
            method.Body.Variables.Add(new VariableDefinition(rt));
            var il=method.Body.GetILProcessor();
            if(includeCall) il.Append(il.Create(OpCodes.Call,called));
            var nop=il.Create(OpCodes.Nop);
            if(addNop) il.Append(nop);
            var writer=il.Create(OpCodes.Stloc_0);
            il.Append(writer);
            il.Append(il.Create(OpCodes.Ldloc_0));
            il.Append(il.Create(OpCodes.Ret));
            if(bypass && addNop)
                il.Append(il.Create(OpCodes.Br_S,nop));
            return (method,writer);
        }

        var direct=Create(Ref("SyntheticRT",rt));
        var good=Inspect(direct.Method,direct.Writer,true);
        if(!good.PrecedingInstructionIsCall ||
            good.DeclaredCallReturnCategory!="rendertexture_named_return" ||
            !good.CallHasDeclaredReturnValue ||
            !good.ConditionalCallResultIsImmediateStoreStackTop ||
            !good.DeclaredReturnExactlyRenderTextureByName ||
            good.RuntimeCallOrNonNullVerified ||
            good.OriginalAssemblyTypeIdentityVerified)
            throw new InvalidDataException("Synthetic direct RT call/stack category mismatch");

        var voidCase=Create(Ref("SyntheticVoid",module.TypeSystem.Void));
        var noValue=Inspect(voidCase.Method,voidCase.Writer,true);
        if(noValue.DeclaredCallReturnCategory!="void_return" ||
            noValue.CallHasDeclaredReturnValue ||
            noValue.ConditionalCallResultIsImmediateStoreStackTop ||
            noValue.DeclaredReturnExactlyRenderTextureByName)
            throw new InvalidDataException("Void call fabricated returned stack value");

        var other=Create(Ref("SyntheticBool",module.TypeSystem.Boolean));
        var incompatible=Inspect(other.Method,other.Writer,true);
        if(incompatible.DeclaredCallReturnCategory!="other_value_type_return" ||
            !incompatible.CallHasDeclaredReturnValue ||
            incompatible.DeclaredReturnExactlyRenderTextureByName)
            throw new InvalidDataException("Non-RT value promoted as RT");
        var wrongLocalType=Inspect(direct.Method,direct.Writer,false);
        if(wrongLocalType.PrecedingInstructionIsCall ||
            wrongLocalType.ConditionalCallResultIsImmediateStoreStackTop)
            throw new InvalidDataException("Wrong return local type accepted");

        var branched=Create(Ref("SyntheticRT",rt),addNop:true,bypass:true);
        var bypassed=Inspect(branched.Method,branched.Writer,true);
        if(!bypassed.AlternateControlFlowEntryBetweenCallAndStore ||
            bypassed.ConditionalCallResultIsImmediateStoreStackTop)
            throw new InvalidDataException("Branch can skip producer call");
        var harmlessNop=Create(Ref("SyntheticRT",rt),addNop:true);
        if(!Inspect(harmlessNop.Method,harmlessNop.Writer,true)
            .ConditionalCallResultIsImmediateStoreStackTop)
            throw new InvalidDataException("Ordinary nop broke typed producer");
        var nonCall=Create(Ref("SyntheticRT",rt),includeCall:false);
        if(Inspect(nonCall.Method,nonCall.Writer,true).PrecedingInstructionIsCall)
            throw new InvalidDataException("Non-call promoted as call");

        // A void call consuming a duplicated receiver can leave the
        // original stack reference for the following stloc. No null proof.
        var one=Ref("SyntheticOneVoid",module.TypeSystem.Void);
        one.HasThis=true;
        var dupCase=Create(one);
        var dupProcessor=dupCase.Method.Body.GetILProcessor();
        var dupCall=dupCase.Method.Body.Instructions[0];
        dupProcessor.InsertBefore(dupCall,dupProcessor.Create(OpCodes.Ldnull));
        dupProcessor.InsertBefore(dupCall,dupProcessor.Create(OpCodes.Dup));
        var retained=Inspect(dupCase.Method,dupCase.Writer,true);
        if(retained.ImmediatePreCallOpcodeCategory!="dup" ||
           retained.CallConsumedOperandCategory!="one" ||
           !retained.RetainedDuplicateAfterOneInputVoidCall ||
           retained.OriginalRuntimeStackContentsVerified)
           throw new InvalidDataException("Synthetic retained dup not recognized");
        // Branch directly to call, bypassing dup: fail closed.
        var jumpCase=Create(one);
        var jumpProcessor=jumpCase.Method.Body.GetILProcessor();
        var jumpCall=jumpCase.Method.Body.Instructions[0];
        jumpProcessor.InsertBefore(jumpCall,jumpProcessor.Create(OpCodes.Ldnull));
        jumpProcessor.InsertBefore(jumpCall,jumpProcessor.Create(OpCodes.Dup));
        jumpProcessor.Append(jumpProcessor.Create(OpCodes.Br_S,jumpCall));
        if(Inspect(jumpCase.Method,jumpCase.Writer,true)
           .RetainedDuplicateAfterOneInputVoidCall)
           throw new InvalidDataException("Branch bypass incorrectly proved dup");
        var noArgs=Create(Ref("SyntheticNoArgs",module.TypeSystem.Void));
        if(Inspect(noArgs.Method,noArgs.Writer,true).CallConsumedOperandCategory!="none")
           throw new InvalidDataException("No-arg void call operand category incorrect");
        FoamReturnWriterStackSlice.RunSyntheticControls();
    }
}
