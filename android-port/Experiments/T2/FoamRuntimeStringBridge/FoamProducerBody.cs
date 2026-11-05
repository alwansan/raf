// T2: bounded *aggregate* original compiled Texture(int) producer IL shape.
// No private instruction sequence/method names/field identifiers are emitted.
// A strict five-instruction pattern is proven only when exact; all other
// bodies remain unknown, never reconstructed by guessing decompiled source.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamProducerBody
{
    internal sealed record SafeProfile(
        int InstructionCount, int ReturnInstructions, int InstanceFieldLoads,
        int StaticFieldLoads, int IndexedReferenceLoads, int Calls,
        int Branches, int LocalLoads, int OriginalArgumentLoads,
        bool TypedTextureArrayFieldReferenced,
        bool ExactThisTextureArrayIndexedByIntParameter,
        string SafeClassification,
        IReadOnlyDictionary<string,int> OriginalInstanceFieldTypeCategories,
        bool ExactNullGuardedOriginalTextureArrayIndexByInt,
        bool OriginalFallbackReturnsNull);

    private static string FieldCategory(FieldReference field)
    {
        if (field.FieldType is not ArrayType array)
            return "other_nonarray_field_type";
        if (array.Rank!=1) return "other_multidimensional_array_type";
        return array.ElementType.FullName switch {
            "UnityEngine.Texture" => "unity_texture_array",
            "UnityEngine.RenderTexture" => "unity_rendertexture_array",
            "UnityEngine.Texture2D" => "unity_texture2d_array",
            "UnityEngine.Texture3D" => "unity_texture3d_array",
            "UnityEngine.Cubemap" => "unity_cubemap_array",
            "UnityEngine.Texture2DArray" => "unity_texture2darray_array",
            _ => "other_unverified_element_array_type",
        };
    }

    private static bool IsOneDimensionalKnownTextureArray(FieldReference field)
    {
        return FieldCategory(field) is
            "unity_texture_array" or "unity_rendertexture_array" or
            "unity_texture2d_array" or "unity_texture3d_array" or
            "unity_cubemap_array" or "unity_texture2darray_array";
    }

    internal static SafeProfile Inspect(MethodDefinition method)
    {
        if (method is null || !method.HasBody ||
            method.ReturnType.FullName!="UnityEngine.Texture" ||
            method.Parameters.Count!=1 ||
            method.Parameters[0].ParameterType.FullName!="System.Int32" ||
            !method.HasThis)
            throw new InvalidDataException("Unapproved original one-index Texture producer method shape");
        var all=method.Body.Instructions.Where(i=>i.OpCode.Code!=Code.Nop).ToList();
        if (all.Count==0 || all.Count>10000)
            throw new InvalidDataException("Original Texture producer body out of bounds");
        int returns=0,fields=0,staticFields=0,arrayReads=0,calls=0,branches=0,
            locals=0,args=0;
        bool typedArray=false;
        var fieldsByCategory=new Dictionary<string,int>(StringComparer.Ordinal);
        foreach (var op in all)
        {
            if (op.OpCode.Code==Code.Ret) returns++;
            if (op.OpCode.Code==Code.Ldfld)
            {
                fields++;
                if (op.Operand is FieldReference field)
                {
                    var category=FieldCategory(field);
                    fieldsByCategory[category]=fieldsByCategory.GetValueOrDefault(category)+1;
                    if (IsOneDimensionalKnownTextureArray(field))
                        typedArray=true;
                }
            }
            if (op.OpCode.Code==Code.Ldsfld) staticFields++;
            if (op.OpCode.Code==Code.Ldelem_Ref) arrayReads++;
            if (op.OpCode.Code is Code.Call or Code.Callvirt) calls++;
            if (op.OpCode.FlowControl is FlowControl.Cond_Branch or FlowControl.Branch)
                branches++;
            if (op.OpCode.Name.StartsWith("ldloc",StringComparison.Ordinal)) locals++;
            if (op.OpCode.Name.StartsWith("ldarg",StringComparison.Ordinal)) args++;
        }
        bool exact = all.Count==5 &&
            all[0].OpCode.Code==Code.Ldarg_0 &&
            all[1].OpCode.Code==Code.Ldfld &&
            all[1].Operand is FieldReference fieldRef &&
            fieldRef.FieldType is ArrayType array &&
            array.ElementType.FullName=="UnityEngine.Texture" &&
            array.Rank==1 &&
            all[2].OpCode.Code==Code.Ldarg_1 &&
            all[3].OpCode.Code==Code.Ldelem_Ref &&
            all[4].OpCode.Code==Code.Ret;
        bool guarded = all.Count==10 &&
            all[0].OpCode.Code==Code.Ldarg_0 &&
            all[1].OpCode.Code==Code.Ldfld &&
            all[1].Operand is FieldReference first &&
            IsOneDimensionalKnownTextureArray(first) &&
            (all[2].OpCode.Code is Code.Brfalse or Code.Brfalse_S) &&
            all[2].Operand is Instruction destination &&
            ReferenceEquals(destination,all[8]) &&
            all[3].OpCode.Code==Code.Ldarg_0 &&
            all[4].OpCode.Code==Code.Ldfld &&
            all[4].Operand is FieldReference second &&
            first.FullName==second.FullName &&
            all[5].OpCode.Code==Code.Ldarg_1 &&
            all[6].OpCode.Code==Code.Ldelem_Ref &&
            all[7].OpCode.Code==Code.Ret &&
            all[8].OpCode.Code==Code.Ldnull &&
            all[9].OpCode.Code==Code.Ret;
        // The genuine original may put the null fallback *before* the
        // non-null branch. This is the dual, equally guarded and strict
        // 10-instruction form (no synthetic assumptions about branch target).
        bool guardedOpposite = all.Count==10 &&
            all[0].OpCode.Code==Code.Ldarg_0 &&
            all[1].OpCode.Code==Code.Ldfld &&
            all[1].Operand is FieldReference oppositeFirst &&
            IsOneDimensionalKnownTextureArray(oppositeFirst) &&
            (all[2].OpCode.Code is Code.Brtrue or Code.Brtrue_S) &&
            all[2].Operand is Instruction oppositeDestination &&
            ReferenceEquals(oppositeDestination,all[5]) &&
            all[3].OpCode.Code==Code.Ldnull &&
            all[4].OpCode.Code==Code.Ret &&
            all[5].OpCode.Code==Code.Ldarg_0 &&
            all[6].OpCode.Code==Code.Ldfld &&
            all[6].Operand is FieldReference oppositeSecond &&
            oppositeFirst.FullName==oppositeSecond.FullName &&
            all[7].OpCode.Code==Code.Ldarg_1 &&
            all[8].OpCode.Code==Code.Ldelem_Ref &&
            all[9].OpCode.Code==Code.Ret;
        bool anyNullGuard = guarded || guardedOpposite;
        return new SafeProfile(all.Count,returns,fields,staticFields,arrayReads,
            calls,branches,locals,args,typedArray,exact,
            exact?"exact_original_instance_Texture_array_indexed_by_int":
                  anyNullGuard?"exact_original_null_guarded_Texture_array_index_by_int":
                  "original_compiled_Texture_int_body_requires_deeper_provenance",
            fieldsByCategory,anyNullGuard,anyNullGuard);
    }
}
