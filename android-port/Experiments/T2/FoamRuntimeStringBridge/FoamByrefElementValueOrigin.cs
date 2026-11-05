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
        bool OriginalPrivateSymbolOrNumericValueDisclosed);

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
        return new SafeProfile(1,1,immediate,origin.Category,origin.NewRt,
            origin.CallRt,origin.Null,origin.Local,false,false);
    }
}
