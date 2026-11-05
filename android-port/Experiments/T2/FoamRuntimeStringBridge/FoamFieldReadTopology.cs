// T2: bounded exact original RenderTexture[] field read/address topology.
// Private managed field/type/method names never leave original-SHA CI scratch.
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class FoamFieldReadTopology
{
    internal sealed record SafeProfile(
        int ExactInstanceFieldLoadInstructions,
        int ExactInstanceFieldAddressInstructions,
        int OriginalGetterFieldLoadInstructions,
        int OtherOriginalMethodFieldLoadInstructions,
        int OtherOriginalMethodFieldAddressInstructions,
        int DistinctDirectReaderMethods,
        int DistinctDirectAddressMethods,
        bool ActualRuntimeArrayContentsVerified,
        bool ManagedArrayElementsWrittenOrPopulatedProven);

    private static bool SameExactField(FieldReference value, FieldReference original) =>
        value.FullName==original.FullName &&
        value.FieldType.FullName==original.FieldType.FullName &&
        value.DeclaringType.FullName==original.DeclaringType.FullName;

    internal static SafeProfile Scan(IEnumerable<MethodDefinition> methods,
        FieldReference originalField, MethodDefinition exactOriginalGetter)
    {
        if (methods is null || originalField is null || exactOriginalGetter is null ||
            originalField.FieldType is not ArrayType arr || arr.Rank!=1 ||
            arr.ElementType.FullName!="UnityEngine.RenderTexture" ||
            !FoamProducerBody.Inspect(exactOriginalGetter)
                .ExactNullGuardedOriginalTextureArrayIndexByInt)
            throw new InvalidDataException("Exact original guarded texture getter required");
        int loads=0, addresses=0, getterLoads=0, otherLoads=0, otherAddresses=0;
        var readerMethods=new HashSet<MethodDefinition>();
        var addressMethods=new HashSet<MethodDefinition>();
        foreach (var method in methods)
        {
            if (method is null || !method.HasBody)
                continue;
            foreach (var op in method.Body.Instructions)
            {
                bool isLoad=op.OpCode.Code==Code.Ldfld;
                bool isAddr=op.OpCode.Code==Code.Ldflda;
                if ((!isLoad && !isAddr) || op.Operand is not FieldReference actual ||
                    !SameExactField(actual,originalField))
                    continue;
                if (isLoad)
                {
                    loads++;
                    readerMethods.Add(method);
                    if (ReferenceEquals(method,exactOriginalGetter)) getterLoads++;
                    else otherLoads++;
                }
                else
                {
                    addresses++;
                    addressMethods.Add(method);
                    if (!ReferenceEquals(method,exactOriginalGetter)) otherAddresses++;
                }
                if (loads+addresses>100000)
                    throw new InvalidDataException("Original backing field usage scan budget");
            }
        }
        if (getterLoads!=2 || loads!=getterLoads+otherLoads ||
            addresses<otherAddresses || readerMethods.Count>loads ||
            addressMethods.Count>addresses)
            throw new InvalidDataException("Exact original getter field load invariant failed");
        return new SafeProfile(loads,addresses,getterLoads,otherLoads,
            otherAddresses,readerMethods.Count,addressMethods.Count,
            false,false);
    }
}
