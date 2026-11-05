// T2: private compiled Foam RenderTexture[] allocation-size versus four
// exact Texture(int) caller indices. Never emit original values or hashes.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamByrefArrayBounds
{
    internal sealed record SafeProfile(
        int ExactRecipientDefinitionMatches,
        int ProvenNewarrRefArrayStoreSites,
        int ExactRenderTextureNewarrSites,
        string NewarrLengthOperandOriginCategory,
        bool? FourOriginalIndicesWithinThisCompiledAllocation,
        bool OriginalNumericLiteralsOrDigestsDisclosed,
        bool RuntimeArrayAllocationOrBoundsVerified);

    private static bool Same(MethodDefinition m, MethodReference call) =>
        m.FullName==call.FullName && m.HasThis==call.HasThis &&
        m.Parameters.Count==call.Parameters.Count &&
        m.Parameters.Zip(call.Parameters,
            (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName).All(x=>x);

    private static int? I4(Instruction op) => op.OpCode.Code switch
    {
        Code.Ldc_I4_M1 => -1,
        Code.Ldc_I4_0 => 0,
        Code.Ldc_I4_1 => 1,
        Code.Ldc_I4_2 => 2,
        Code.Ldc_I4_3 => 3,
        Code.Ldc_I4_4 => 4,
        Code.Ldc_I4_5 => 5,
        Code.Ldc_I4_6 => 6,
        Code.Ldc_I4_7 => 7,
        Code.Ldc_I4_8 => 8,
        Code.Ldc_I4_S when op.Operand is sbyte n => n,
        Code.Ldc_I4 when op.Operand is int n => n,
        _ => null
    };

    internal static SafeProfile Inspect(IEnumerable<MethodDefinition> methods,
        MethodReference originalRecipient,
        FoamByrefAllocationFlow.SafeProfile allocationProof,
        IReadOnlyCollection<int> privateExactIndexValues)
    {
        if(methods is null || originalRecipient is null || allocationProof is null ||
            privateExactIndexValues is null)
            throw new InvalidDataException("Incomplete original array bound provenance");
        var matches=methods.Where(m=>Same(m,originalRecipient)).Take(2).ToList();
        int count=matches.Count;
        if(count!=1 || !matches[0].HasBody)
            return new SafeProfile(count,0,0,"recipient_unresolved",
                null,false,false);
        var method=matches[0];
        var ops=method.Body.Instructions;
        var sites=Enumerable.Range(0,ops.Count).Where(i=>
            ops[i].OpCode.Code==Code.Newarr &&
            ops[i].Operand is TypeReference element &&
            element.FullName=="UnityEngine.RenderTexture").ToList();
        if(allocationProof.OriginalMatchingCalleeDefinitions!=1 ||
            allocationProof.ProvenNewarrRenderTextureArrayToRefFormalStores!=1 ||
            sites.Count!=1)
            return new SafeProfile(count,
                allocationProof.ProvenNewarrRenderTextureArrayToRefFormalStores,
                sites.Count,"exact_allocation_relation_not_unique",
                null,false,false);
        int previous=sites[0]-1;
        while(previous>=0 && ops[previous].OpCode.Code==Code.Nop) previous--;
        if(previous<0)
            return new SafeProfile(count,1,1,
                "length_source_not_proven",null,false,false);
        int? length=I4(ops[previous]);
        if(length is not int n)
            return new SafeProfile(count,1,1,
                "length_source_not_direct_i4",null,false,false);
        // Values remain transient process memory. We emit only a nullable
        // comparison verdict and never any original literal or hash.
        bool? within=privateExactIndexValues.Count==4
            ? privateExactIndexValues.All(v=>v>=0 && v<n) : null;
        return new SafeProfile(count,1,1,"direct_ldc_i4_literal",
            within,false,false);
    }
}
