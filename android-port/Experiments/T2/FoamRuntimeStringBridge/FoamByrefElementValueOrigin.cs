// T2 SHA-original Foam: classify only the proven exact stelem.ref value
// operand source. Compiled IL source and original symbols never leave CI.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamByrefElementValueOrigin
{
    internal sealed record SafeProfile(
        int ExactMatchingOriginalRecipientDefinitions,
        int ExactStelemRefSites,
        string ImmediateElementValueProducerCategory,
        string ResolvedElementValueOriginCategory,
        bool ExactRenderTextureConstructorValueProven,
        bool DeclaredRenderTextureReturnValueProven,
        bool LiteralNullElementValueProven,
        bool SameBlockLocalValueDefinitionProven,
        bool RuntimeRenderTextureObjectOrPixelsVerified,
        bool OriginalPrivateSymbolOrNumericValueDisclosed,
        int MatchingOriginalReturnMethodDefinitions=0,
        string ActualReturnTargetDeclarationCategory="not_examined",
        bool MatchingOriginalMethodBodyAvailable=false,
        int OriginalReturnInstructionSites=0,
        int DirectNullReturnSites=0,
        int DirectRenderTextureConstructorReturnSites=0,
        int DirectRenderTextureCallReturnSites=0,
        int ReturnSitesWithUnresolvedProducer=0,
        int BodyBranchInstructionCount=0,
        string OriginalReturnSitePlacementCategory="not_examined",
        string OriginalReturnImmediatePriorOpcodeCategory="not_examined",
        SafeLocalWriters? OriginalReturnLocalWriterCensus=null);

    internal sealed record SafeLocalWriters(
        int ExactReturnLocalLoadSites,
        bool ReturnLocalDeclaredRenderTexture,
        int ExactLocalAssignmentSites,
        int DirectNullAssignmentSites,
        int DirectRenderTextureConstructorAssignmentSites,
        int DirectRenderTextureTypedCallAssignmentSites,
        int LocalAliasAssignmentSites,
        int UnresolvedAssignmentSites,
        bool BranchJoinOrRuntimeValueVerified=false,
        string SoleWriterImmediatePriorOpcodeCategory="not_examined",
        bool SoleWriterIsControlFlowEntry=false,
        FoamReturnWriterCallEvidence.SafeProfile? OriginalSoleWriterCallReturnEvidence=null);

    private readonly record struct Origin(string Category,bool NewRt=false,
        bool CallRt=false,bool Null=false,bool Local=false);
    private static bool Same(MethodDefinition m,MethodReference reference) =>
        m.FullName==reference.FullName && m.HasThis==reference.HasThis &&
        m.Parameters.Count==reference.Parameters.Count &&
        m.Parameters.Zip(reference.Parameters,
            (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName).All(x=>x);
    private static int? Local(Instruction ins) => ins.OpCode.Code switch {
        Code.Ldloc_0 or Code.Stloc_0 => 0,
        Code.Ldloc_1 or Code.Stloc_1 => 1,
        Code.Ldloc_2 or Code.Stloc_2 => 2,
        Code.Ldloc_3 or Code.Stloc_3 => 3,
        Code.Ldloc or Code.Ldloc_S or Code.Stloc or Code.Stloc_S
            when ins.Operand is VariableDefinition v => v.Index,
        _ => null
    };
    private static bool Load(Instruction ins) => ins.OpCode.Code is
        Code.Ldloc_0 or Code.Ldloc_1 or Code.Ldloc_2 or Code.Ldloc_3 or
        Code.Ldloc or Code.Ldloc_S;
    private static bool Store(Instruction ins) => ins.OpCode.Code is
        Code.Stloc_0 or Code.Stloc_1 or Code.Stloc_2 or Code.Stloc_3 or
        Code.Stloc or Code.Stloc_S;
    private static int Prev(Mono.Collections.Generic.Collection<Instruction> il,
        int start,int end)
    {
        for(int i=end-1;i>=start;i--)
            if(il[i].OpCode.Code!=Code.Nop) return i;
        return -1;
    }
    private static HashSet<Instruction> Entries(MethodDefinition m)
    {
        var il=m.Body.Instructions;
        var entries=new HashSet<Instruction>();
        if(il.Count>0) entries.Add(il[0]);
        for(int i=0;i<il.Count;i++)
        {
            if(il[i].Operand is Instruction target) entries.Add(target);
            if(il[i].Operand is Instruction[] targets)
                foreach(var entry in targets) entries.Add(entry);
            if(il[i].OpCode.FlowControl is FlowControl.Branch or
                FlowControl.Cond_Branch or FlowControl.Return or
                FlowControl.Throw or FlowControl.Break)
                if(i+1<il.Count) entries.Add(il[i+1]);
        }
        foreach(var h in m.Body.ExceptionHandlers)
        {
            if(h.TryStart!=null) entries.Add(h.TryStart);
            if(h.TryEnd!=null) entries.Add(h.TryEnd);
            if(h.HandlerStart!=null) entries.Add(h.HandlerStart);
            if(h.HandlerEnd!=null) entries.Add(h.HandlerEnd);
            if(h.FilterStart!=null) entries.Add(h.FilterStart);
        }
        return entries;
    }
    private static Origin Resolve(MethodDefinition method,int index,int start,int depth)
    {
        var il=method.Body.Instructions;
        if(index<start || depth>3) return new Origin("unresolved_origin_or_block");
        var op=il[index];
        if(op.OpCode.Code==Code.Ldnull)
            return new Origin("literal_null",Null:true);
        if(op.OpCode.Code==Code.Newobj)
            return new Origin(op.Operand is MethodReference ctor &&
                ctor.DeclaringType.FullName=="UnityEngine.RenderTexture" &&
                ctor.Name==".ctor"
                ?"newobj_rendertexture":"newobj_other_type",
                NewRt:op.Operand is MethodReference good &&
                    good.DeclaringType.FullName=="UnityEngine.RenderTexture" &&
                    good.Name==".ctor");
        if(op.OpCode.Code is Code.Call or Code.Callvirt)
            return new Origin(op.Operand is MethodReference ret &&
                ret.ReturnType.FullName=="UnityEngine.RenderTexture"
                ?"call_returns_rendertexture":"call_other_return",
                CallRt:op.Operand is MethodReference good &&
                    good.ReturnType.FullName=="UnityEngine.RenderTexture");
        if(Load(op))
        {
            int? local=Local(op);
            if(local is null) return new Origin("unknown_local");
            for(int i=index-1;i>=start;i--)
                if(Store(il[i]) && Local(il[i])==local)
                {
                    int value=Prev(il,start,i);
                    if(value<start) return new Origin("local_value_outside_block");
                    var src=Resolve(method,value,start,depth+1);
                    return new Origin("same_block_local_from_"+src.Category,
                        src.NewRt,src.CallRt,src.Null,true);
                }
            return new Origin("local_definition_outside_block");
        }
        if(op.OpCode.Code is Code.Ldarg or Code.Ldarg_S or Code.Ldarg_0
            or Code.Ldarg_1 or Code.Ldarg_2 or Code.Ldarg_3)
            return new Origin("argument_load");
        if(op.OpCode.Code is Code.Ldfld or Code.Ldsfld)
            return new Origin("field_load");
        if(op.OpCode.Code is Code.Ldelem_Ref or Code.Ldind_Ref)
            return new Origin("indirect_object_load");
        if(op.OpCode.Code==Code.Dup)
            return new Origin("duplicate_without_stack_proof");
        return new Origin("unsupported_value_producer");
    }


    // Match declaration only. No source return-value semantics or runtime
    // non-null guarantees follow from a matching signature.
    internal static (int Count,string Category,bool Body) MatchActualRtCall(
        IEnumerable<MethodDefinition> originals,MethodReference call)
    {
        if (originals is null || call is null ||
            call.ReturnType.FullName!="UnityEngine.RenderTexture")
            throw new InvalidDataException("Typed original RT call required");
        var candidates=originals.Where(m=>
            m.FullName==call.FullName &&
            m.DeclaringType.FullName==call.DeclaringType.FullName &&
            m.HasThis==call.HasThis &&
            m.ReturnType.FullName==call.ReturnType.FullName &&
            m.Parameters.Count==call.Parameters.Count &&
            m.Parameters.Zip(call.Parameters,
                (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName)
                .All(x=>x)).Take(2).ToList();
        if(candidates.Count>1)
            throw new InvalidDataException("Ambiguous original RT return signature");
        string category=candidates.Count==1
            ?"matching_sha_managed_signature"
            :call.DeclaringType.FullName.StartsWith("UnityEngine.",
                StringComparison.Ordinal)
                ?"unresolved_unityengine_declaration"
                :"unresolved_nonunity_declaration";
        return (candidates.Count,category,
            candidates.Count==1 && candidates[0].HasBody);
    }


    // Method-wide compiled return census. A return at a branch/exception
    // entry is never inferred from its textual predecessor.
    internal static (int Total,int Null,int NewRt,int CallRt,int Unknown,int Branches)
        ScanMatchingReturnBody(IEnumerable<MethodDefinition> originals,
                               MethodReference exactRtTarget)
    {
        var found=originals.Where(m=>
            m.FullName==exactRtTarget.FullName &&
            m.DeclaringType.FullName==exactRtTarget.DeclaringType.FullName &&
            m.HasThis==exactRtTarget.HasThis &&
            m.ReturnType.FullName==exactRtTarget.ReturnType.FullName &&
            m.Parameters.Count==exactRtTarget.Parameters.Count &&
            m.Parameters.Zip(exactRtTarget.Parameters,
                (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName)
                .All(x=>x)).Take(2).ToList();
        if(found.Count!=1 || !found[0].HasBody)
            return (0,0,0,0,0,0);
        var method=found[0];
        var ins=method.Body.Instructions;
        var entries=Entries(method);
        int total=0,nulls=0,constructors=0,calls=0,unknown=0,branches=0;
        for(int i=0;i<ins.Count;i++)
        {
            if(ins[i].OpCode.FlowControl is FlowControl.Branch or
                FlowControl.Cond_Branch) branches++;
            if(ins[i].OpCode.Code!=Code.Ret) continue;
            total++;
            if(entries.Contains(ins[i]))
            {
                unknown++;
                continue;
            }
            int p=Prev(ins,0,i);
            if(p<0 || p>=i ||
                ins[p].OpCode.FlowControl is FlowControl.Branch or
                    FlowControl.Cond_Branch or FlowControl.Throw)
            {
                unknown++;
                continue;
            }
            var op=ins[p];
            if(op.OpCode.Code==Code.Ldnull)
                nulls++;
            else if(op.OpCode.Code==Code.Newobj &&
                op.Operand is MethodReference ctor &&
                ctor.Name==".ctor" &&
                ctor.DeclaringType.FullName=="UnityEngine.RenderTexture")
                constructors++;
            else if(op.OpCode.Code is (Code.Call or Code.Callvirt) &&
                op.Operand is MethodReference returned &&
                returned.ReturnType.FullName=="UnityEngine.RenderTexture")
                calls++;
            else unknown++;
        }
        if(total!=nulls+constructors+calls+unknown)
            throw new InvalidDataException("Unbalanced original RT return count");
        return (total,nulls,constructors,calls,unknown,branches);
    }


    // Original method symbols, IL bytes and numeric operands are private.
    // Report only fixed coarse categories; branch targets NEVER imply
    // straight-line return-value provenance.
    internal static (string Placement,string Immediate) ExplainRetSite(
        IEnumerable<MethodDefinition> originals, MethodReference exactReturnCall)
    {
        var found=originals.Where(m=>
            m.FullName==exactReturnCall.FullName &&
            m.DeclaringType.FullName==exactReturnCall.DeclaringType.FullName &&
            m.HasThis==exactReturnCall.HasThis &&
            m.ReturnType.FullName==exactReturnCall.ReturnType.FullName &&
            m.Parameters.Count==exactReturnCall.Parameters.Count &&
            m.Parameters.Zip(exactReturnCall.Parameters,
                (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName)
                .All(x=>x)).Take(2).ToList();
        if(found.Count!=1 || !found[0].HasBody)
            return ("unresolved_method","unresolved_method");
        var method=found[0];
        var il=method.Body.Instructions;
        var rets=Enumerable.Range(0,il.Count)
            .Where(i=>il[i].OpCode.Code==Code.Ret).ToList();
        if(rets.Count!=1)
            return ("zero_or_multiple_returns","zero_or_multiple_returns");
        int site=rets[0];
        bool atEntry=Entries(method).Contains(il[site]);
        string placement=atEntry?"branch_exception_or_method_entry":
            "sequential_return_site";
        int prev=Prev(il,0,site);
        if(prev<0)
            return (placement,"no_prior_opcode");
        var op=il[prev];
        string prior=op.OpCode.Code switch
        {
            Code.Ldnull => "ldnull",
            Code.Ldloc or Code.Ldloc_S or Code.Ldloc_0 or Code.Ldloc_1 or
                Code.Ldloc_2 or Code.Ldloc_3 => "ldloc",
            Code.Ldarg or Code.Ldarg_S or Code.Ldarg_0 or Code.Ldarg_1 or
                Code.Ldarg_2 or Code.Ldarg_3 => "ldarg",
            Code.Ldfld or Code.Ldsfld => "field_load",
            Code.Call or Code.Callvirt => "call",
            Code.Newobj => "newobj",
            Code.Dup => "dup",
            Code.Ldelem_Ref or Code.Ldind_Ref => "indirect_load",
            _ when op.OpCode.FlowControl is FlowControl.Branch or
                FlowControl.Cond_Branch => "branch_opcode",
            _ => "other_opcode"
        };
        return (placement,prior);
    }



    private static string WriterPriorOpcodeFamily(Instruction instruction)
    {
        var op=instruction.OpCode.Code;
        return op switch
        {
            Code.Ldnull => "ldnull",
            Code.Newobj => "newobj",
            Code.Call or Code.Callvirt => "call",
            Code.Ldloc or Code.Ldloc_S or Code.Ldloc_0 or Code.Ldloc_1 or
                Code.Ldloc_2 or Code.Ldloc_3 => "ldloc",
            Code.Ldarg or Code.Ldarg_S or Code.Ldarg_0 or Code.Ldarg_1 or
                Code.Ldarg_2 or Code.Ldarg_3 => "ldarg",
            Code.Ldfld or Code.Ldsfld => "field_load",
            Code.Ldelem_Ref or Code.Ldind_Ref => "indirect_reference_load",
            Code.Castclass or Code.Isinst => "reference_type_cast",
            Code.Dup => "dup",
            Code.Ldc_I4 or Code.Ldc_I4_S or Code.Ldc_I4_M1 or
                Code.Ldc_I4_0 or Code.Ldc_I4_1 or Code.Ldc_I4_2 or
                Code.Ldc_I4_3 or Code.Ldc_I4_4 or Code.Ldc_I4_5 or
                Code.Ldc_I4_6 or Code.Ldc_I4_7 or Code.Ldc_I4_8
                    => "integer_literal",
            _ when instruction.OpCode.FlowControl is FlowControl.Branch or
                FlowControl.Cond_Branch => "branch_opcode",
            _ => "other_opcode"
        };
    }

    // An opcode census, not reaching-definition/CFG proof. Counting a
    // local write never means that path is executed or that a value is live.
    internal static SafeLocalWriters ScanExactReturnLocalWriters(
        IEnumerable<MethodDefinition> originals,
        MethodReference exactReturnCall)
    {
        var found=originals.Where(m=>
            m.FullName==exactReturnCall.FullName &&
            m.DeclaringType.FullName==exactReturnCall.DeclaringType.FullName &&
            m.HasThis==exactReturnCall.HasThis &&
            m.ReturnType.FullName==exactReturnCall.ReturnType.FullName &&
            m.Parameters.Count==exactReturnCall.Parameters.Count &&
            m.Parameters.Zip(exactReturnCall.Parameters,
                (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName)
                .All(x=>x)).Take(2).ToList();
        if(found.Count!=1 || !found[0].HasBody)
            return new SafeLocalWriters(0,false,0,0,0,0,0,0);
        var method=found[0];
        var il=method.Body.Instructions;
        var retSites=Enumerable.Range(0,il.Count)
            .Where(i=>il[i].OpCode.Code==Code.Ret).ToList();
        if(retSites.Count!=1)
            return new SafeLocalWriters(0,false,0,0,0,0,0,0);
        int predecessor=Prev(il,0,retSites[0]);
        if(predecessor<0 || !Load(il[predecessor]))
            return new SafeLocalWriters(0,false,0,0,0,0,0,0);
        int? localIndex=Local(il[predecessor]);
        if(localIndex is not int n || n<0 || n>=method.Body.Variables.Count)
            return new SafeLocalWriters(0,false,0,0,0,0,0,0);
        bool typed=method.Body.Variables[n].VariableType.FullName==
            "UnityEngine.RenderTexture";
        var entries=Entries(method);
        int total=0,nulls=0,newrt=0,rtcalls=0,aliases=0,unknown=0;
        string soleWriterPrior="not_examined";
        bool soleWriterIsEntry=false;
        for(int i=0;i<il.Count;i++)
        {
            if(!Store(il[i]) || Local(il[i])!=n)
                continue;
            total++;
            int previous=Prev(il,0,i);
            if(total==1)
            {
                soleWriterPrior=previous<0?"no_prior_opcode":
                    WriterPriorOpcodeFamily(il[previous]);
                soleWriterIsEntry=entries.Contains(il[i]);
            }
            else
            {
                soleWriterPrior="multiple_writers";
                soleWriterIsEntry=false;
            }
            if(previous<0 || entries.Contains(il[i]) ||
                il[previous].OpCode.FlowControl is FlowControl.Branch or
                    FlowControl.Cond_Branch or FlowControl.Throw)
            {
                unknown++;
                continue;
            }
            var op=il[previous];
            if(op.OpCode.Code==Code.Ldnull)
                nulls++;
            else if(op.OpCode.Code==Code.Newobj &&
                op.Operand is MethodReference ctor &&
                ctor.Name==".ctor" &&
                ctor.DeclaringType.FullName=="UnityEngine.RenderTexture")
                newrt++;
            else if(op.OpCode.Code is (Code.Call or Code.Callvirt) &&
                op.Operand is MethodReference producer &&
                producer.ReturnType.FullName=="UnityEngine.RenderTexture")
                rtcalls++;
            else if(Load(op))
                aliases++;
            else unknown++;
        }
        if(total!=nulls+newrt+rtcalls+aliases+unknown)
            throw new InvalidDataException("Unbalanced original RT local write categories");
        var soleWriterSite=total==1
            ? Enumerable.Range(0,il.Count)
                .FirstOrDefault(i=>Store(il[i]) && Local(il[i])==n,-1)
            : -1;
        var typedCallEvidence=soleWriterSite>=0
            ? FoamReturnWriterCallEvidence.Inspect(
                method,il[soleWriterSite],typed)
            : null;
        return new SafeLocalWriters(1,typed,total,nulls,newrt,rtcalls,
            aliases,unknown,false,soleWriterPrior,soleWriterIsEntry,
            typedCallEvidence);
    }

    internal static SafeProfile Inspect(IEnumerable<MethodDefinition> originals,
        MethodReference recipient,FoamByrefAllocationFlow.SafeProfile prior)
    {
        if(originals is null || recipient is null || prior is null)
            throw new InvalidDataException("Missing typed original array member evidence");
        var matches=originals.Where(m=>Same(m,recipient)).Take(2).ToList();
        if(matches.Count!=1 || !matches[0].HasBody)
            return new SafeProfile(matches.Count,0,"unresolved_recipient",
                "unresolved_recipient",false,false,false,false,false,false);
        var method=matches[0];
        var il=method.Body.Instructions;
        var stelem=Enumerable.Range(0,il.Count)
            .Where(i=>il[i].OpCode.Code==Code.Stelem_Ref).ToList();
        if(stelem.Count!=1 ||
            prior.ProvenArrayElementWritesThroughRefFormal!=1)
            return new SafeProfile(1,stelem.Count,"unverified_array_element",
                "unverified_array_element",false,false,false,false,false,false);
        int site=stelem[0],start=site;
        var entries=Entries(method);
        while(start>0 && !entries.Contains(il[start])) start--;
        int producer=Prev(il,start,site);
        if(producer<start)
            return new SafeProfile(1,1,"value_not_proven_in_block",
                "value_not_proven_in_block",false,false,false,false,false,false);
        var op=il[producer];
        string immediate=op.OpCode.Code switch {
            Code.Newobj => "newobj",
            Code.Call or Code.Callvirt => "call",
            Code.Ldnull => "ldnull",
            Code.Ldloc or Code.Ldloc_S or Code.Ldloc_0 or Code.Ldloc_1 or
                Code.Ldloc_2 or Code.Ldloc_3 => "ldloc",
            Code.Ldarg or Code.Ldarg_S or Code.Ldarg_0 or Code.Ldarg_1 or
                Code.Ldarg_2 or Code.Ldarg_3 => "ldarg",
            Code.Ldfld or Code.Ldsfld => "field",
            Code.Ldelem_Ref or Code.Ldind_Ref => "indirect_load",
            _ => "other"
        };
        var origin=Resolve(method,producer,start,0);
        var identity=origin.CallRt &&
            op.OpCode.Code is (Code.Call or Code.Callvirt) &&
            op.Operand is MethodReference call
            ? MatchActualRtCall(originals,call)
            : (0,"not_an_immediate_rendertexture_call",false);
        var returns=identity.Item1==1 && identity.Item3 &&
            op.Operand is MethodReference rtCall
            ? ScanMatchingReturnBody(originals,rtCall)
            : (0,0,0,0,0,0);
        var retReason=identity.Item1==1 && identity.Item3 &&
            op.Operand is MethodReference originalCall
            ? ExplainRetSite(originals,originalCall)
            : ("not_examined","not_examined");
        var localWrites=identity.Item1==1 && identity.Item3 &&
            op.Operand is MethodReference targetCall
            ? ScanExactReturnLocalWriters(originals,targetCall)
            : new SafeLocalWriters(0,false,0,0,0,0,0,0);
        return new SafeProfile(1,1,immediate,origin.Category,origin.NewRt,
            origin.CallRt,origin.Null,origin.Local,false,false,
            identity.Item1,identity.Item2,identity.Item3,
            returns.Item1,returns.Item2,returns.Item3,
            returns.Item4,returns.Item5,returns.Item6,
            retReason.Item1,retReason.Item2,localWrites);
    }
}
