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
        string SafeClassification);

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
        foreach (var op in all)
        {
            if (op.OpCode.Code==Code.Ret) returns++;
            if (op.OpCode.Code==Code.Ldfld)
            {
                fields++;
                if (op.Operand is FieldReference field &&
                    field.FieldType is ArrayType typed &&
                    typed.ElementType.FullName=="UnityEngine.Texture" &&
                    typed.Rank==1)
                    typedArray=true;
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
        return new SafeProfile(all.Count,returns,fields,staticFields,arrayReads,
            calls,branches,locals,args,typedArray,exact,
            exact?"exact_original_instance_Texture_array_indexed_by_int":
                  "original_compiled_Texture_int_body_requires_deeper_provenance");
    }
}
