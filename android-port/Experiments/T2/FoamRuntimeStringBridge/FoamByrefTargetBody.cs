// T2 WATER-001: classify the actual SHA-original typed byref method target.
// Original names and compiled IL remain in private CI scratch only.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamByrefTargetBody
{
    internal sealed record SafeProfile(
        int ExactSourceManagedMethodDefinitionMatches,
        bool ExactOriginalMethodBodyAvailable,
        bool CallFormalContainsExactRefRenderTextureArray,
        string OriginalTargetDefinitionCategory,
        bool RecognizedSystemArrayResizeSignature,
        int BodyDirectIndirectRefStoreOpcodeCount,
        int BodyDirectArrayNewarrOpcodeCount,
        int BodyDirectReferenceElementStoreOpcodeCount,
        int BodyBranchOpcodeCount,
        int BodyStrictNullStoreThroughRefArrayFormalCount,
        bool RuntimeCallExecutionProven,
        bool RuntimeArrayInitializationProven);

    private static bool IsTargetArray(TypeReference value) =>
        value is ArrayType ar && ar.Rank==1 &&
        ar.ElementType.FullName=="UnityEngine.RenderTexture";

    private static bool Matches(MethodDefinition def, MethodReference reference) =>
        def.FullName==reference.FullName &&
        def.DeclaringType.FullName==reference.DeclaringType.FullName &&
        def.ReturnType.FullName==reference.ReturnType.FullName &&
        def.HasThis==reference.HasThis &&
        def.Parameters.Count==reference.Parameters.Count &&
        def.Parameters.Zip(reference.Parameters,
            (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName).All(x=>x);

    private static int? LoadArgIndex(Instruction ins, MethodDefinition method)
    {
        int raw=ins.OpCode.Code switch
        {
            Code.Ldarg_0 => 0,
            Code.Ldarg_1 => 1,
            Code.Ldarg_2 => 2,
            Code.Ldarg_3 => 3,
            Code.Ldarg or Code.Ldarg_S when ins.Operand is ParameterDefinition p =>
                p.Index+(method.HasThis?1:0),
            _ => -1
        };
        if (raw<0 || method.HasThis && raw==0) return null;
        return raw-(method.HasThis?1:0);
    }

    internal static SafeProfile Inspect(IEnumerable<MethodDefinition> original,
        MethodReference call)
    {
        if (original is null || call is null)
            throw new InvalidDataException("Missing actual original byref recipient");
        var methods=original.ToList();
        bool typed=call.Parameters.Any(p=>p.ParameterType is ByReferenceType br &&
            IsTargetArray(br.ElementType));
        if (!typed)
            throw new InvalidDataException("Call has no typed ref RenderTexture[] formal");
        var found=methods.Where(m=>Matches(m,call)).Take(2).ToList();
        if (found.Count>1)
            throw new InvalidDataException("Ambiguous original managed byref definition");
        bool standardResize=call.DeclaringType.FullName=="System.Array" &&
            call.Name=="Resize" && call.Parameters.Count==2 &&
            call.Parameters[1].ParameterType.FullName=="System.Int32" &&
            !call.HasThis;
        string category=found.Count==1?"same_sha_managed_definition":
            standardResize?"framework_system_array_resize_signature":
            "not_resolved_in_original_AssemblyCSharp";
        MethodDefinition? matched=found.FirstOrDefault();
        bool body=matched?.HasBody==true;
        int indStore=0,newarr=0,stelem=0,branches=0,strictNull=0;
        if(body)
        {
            var ops=matched!.Body.Instructions.Where(i=>i.OpCode.Code!=Code.Nop).ToList();
            foreach(var op in ops)
            {
                if(op.OpCode.Code==Code.Stind_Ref) indStore++;
                if(op.OpCode.Code==Code.Newarr &&
                    op.Operand is TypeReference t &&
                    t.FullName=="UnityEngine.RenderTexture")
                    newarr++;
                if(op.OpCode.Code==Code.Stelem_Ref) stelem++;
                if(op.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch)
                    branches++;
            }
            // Only literal 'ldarg ref-array; ldnull; stind.ref' is a
            // direct target-formal clear. Other IL is NOT silently promoted.
            for(int i=2;i<ops.Count;i++)
            {
                if(ops[i].OpCode.Code!=Code.Stind_Ref ||
                    ops[i-1].OpCode.Code!=Code.Ldnull)
                    continue;
                int? index=LoadArgIndex(ops[i-2],matched);
                if(index is int k && k<matched.Parameters.Count &&
                    matched.Parameters[k].ParameterType is ByReferenceType br &&
                    IsTargetArray(br.ElementType))
                    strictNull++;
            }
        }
        return new SafeProfile(found.Count,body,typed,category,standardResize,
            indStore,newarr,stelem,branches,strictNull,false,false);
    }
}
