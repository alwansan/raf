// T2: exact source-managed RenderTexture[] backing-field write provenance.
// Names/IL from original game stay inside the private SHA-pinned CI runner.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamFieldWriterLineage
{
    internal sealed record SafeProfile(
        int ExactBackingFieldStoreInstructions,
        int DistinctDirectWriterMethods,
        int ConstructorMethodsWithDirectWrite,
        int DirectRenderTextureArrayNewarrSources,
        int DirectNullSources,
        int OtherOrUnprovenSources,
        bool ExactOriginalGetterFieldIdentityMatched,
        bool OriginalRuntimeWriteExecutedProven,
        bool OriginalArrayElementsPopulatedProven);

    private static bool IsRenderArray(FieldReference? f) =>
        f?.FieldType is ArrayType a && a.Rank == 1 &&
        a.ElementType.FullName == "UnityEngine.RenderTexture";

    private static bool SameField(FieldReference a, FieldReference b) =>
        a.FullName == b.FullName &&
        a.DeclaringType.FullName == b.DeclaringType.FullName &&
        a.FieldType.FullName == b.FieldType.FullName;

    internal static FieldReference? ExactGetterBackingField(MethodDefinition getter)
    {
        if (getter is null || !FoamProducerBody.Inspect(getter)
            .ExactNullGuardedOriginalTextureArrayIndexByInt)
            return null;
        var ops = getter.Body.Instructions.Where(i => i.OpCode.Code != Code.Nop).ToList();
        if (ops.Count != 10 || ops[1].Operand is not FieldReference first ||
            !IsRenderArray(first))
            return null;
        int secondPosition = ops[2].OpCode.Code switch {
            Code.Brfalse or Code.Brfalse_S => 4,
            Code.Brtrue or Code.Brtrue_S => 6,
            _ => -1
        };
        if (secondPosition < 0 || ops[secondPosition].OpCode.Code != Code.Ldfld ||
            ops[secondPosition].Operand is not FieldReference second ||
            !SameField(first, second))
            return null;
        return first;
    }

    internal static SafeProfile Scan(IEnumerable<MethodDefinition> methods, FieldReference field)
    {
        if (methods is null || !IsRenderArray(field))
            throw new InvalidDataException("Missing exact original Foam array field");
        int total=0, newarr=0, cleared=0, other=0;
        var writers=new HashSet<string>(StringComparer.Ordinal);
        var constructors=new HashSet<string>(StringComparer.Ordinal);
        foreach (var method in methods)
        {
            if (method is null || !method.HasBody)
                continue;
            var ops=method.Body.Instructions;
            for (int i=0;i<ops.Count;i++)
            {
                if (ops[i].OpCode.Code != Code.Stfld ||
                    ops[i].Operand is not FieldReference stored ||
                    !SameField(stored,field))
                    continue;
                total++;
                // Private identifiers are never included in SafeProfile.
                writers.Add(method.FullName);
                if (method.IsConstructor)
                    constructors.Add(method.FullName);
                int previous=i-1;
                while (previous>=0 && ops[previous].OpCode.Code==Code.Nop)
                    previous--;
                if (previous>=0 && ops[previous].OpCode.Code==Code.Newarr &&
                    ops[previous].Operand is TypeReference element &&
                    element.FullName=="UnityEngine.RenderTexture")
                    newarr++;
                else if (previous>=0 && ops[previous].OpCode.Code==Code.Ldnull)
                    cleared++;
                else
                    other++;
                if (total>100000)
                    throw new InvalidDataException("Original store-site analysis over budget");
            }
        }
        if (newarr+cleared+other!=total || constructors.Count>writers.Count ||
            writers.Count>total)
            throw new InvalidDataException("Original store-site histogram invalid");
        return new SafeProfile(total,writers.Count,constructors.Count,newarr,cleared,
            other,true,false,false);
    }
}
