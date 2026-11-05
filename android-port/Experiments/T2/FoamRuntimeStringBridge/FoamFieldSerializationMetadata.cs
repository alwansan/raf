// T2 WATER-001: original SHA-authentic Cecil field metadata provenance.
// The exact private RenderTexture[] symbol never leaves CI runner memory.
// This is NOT an observed Unity serialization event or populated texture.
using Mono.Cecil;

internal static class FoamFieldSerializationMetadata
{
    internal sealed record SafeProfile(
        int ExactOriginalManagedFieldDefinitionCount,
        bool ExactBackingFieldTypeIsRenderTextureArray,
        bool DeclaredPublic,
        bool HasExplicitUnitySerializeField,
        bool HasNonSerializedMetadata,
        bool IsStatic,
        bool IsInitOnly,
        bool EligibleByFieldModifiersOnly,
        string OwnerDirectBaseTypeCategory,
        bool OriginalSceneOrPrefabValueVerified,
        bool RuntimeArrayLengthOrMembersVerified);

    private static bool Matches(FieldDefinition candidate, FieldReference target) =>
        candidate.FullName==target.FullName &&
        candidate.DeclaringType.FullName==target.DeclaringType.FullName &&
        candidate.FieldType.FullName==target.FieldType.FullName;

    private static string DirectOwnerBaseCategory(TypeDefinition owner)
    {
        return owner.BaseType?.FullName switch
        {
            "UnityEngine.MonoBehaviour" => "direct_unity_monobehaviour",
            "UnityEngine.ScriptableObject" => "direct_unity_scriptableobject",
            "UnityEngine.Behaviour" => "direct_unity_behaviour",
            _ => "not_proven_unity_owner_by_direct_base"
        };
    }

    internal static SafeProfile Inspect(IEnumerable<TypeDefinition> managedTypes,
                                        FieldReference backing)
    {
        if (managedTypes is null ||
            backing?.FieldType is not ArrayType array || array.Rank != 1 ||
            array.ElementType.FullName!="UnityEngine.RenderTexture")
            throw new InvalidDataException("Exact typed original RenderTexture[] field required");
        var matching=managedTypes.SelectMany(t=>t.Fields)
            .Where(f=>Matches(f,backing)).Take(2).ToList();
        if (matching.Count!=1)
            return new SafeProfile(matching.Count,true,false,false,false,
                false,false,false,"definition_unknown",false,false);
        var field=matching[0];
        bool explicitSerialized=field.CustomAttributes.Any(a=>
            a.AttributeType.FullName=="UnityEngine.SerializeField");
        bool nonSerialized=field.IsNotSerialized ||
            field.CustomAttributes.Any(a=>
                a.AttributeType.FullName=="System.NonSerializedAttribute");
        bool eligibleByModifiers=(field.IsPublic||explicitSerialized) &&
            !nonSerialized && !field.IsStatic && !field.IsInitOnly;
        return new SafeProfile(1,true,field.IsPublic,explicitSerialized,
            nonSerialized,field.IsStatic,field.IsInitOnly,eligibleByModifiers,
            DirectOwnerBaseCategory(field.DeclaringType),false,false);
    }
}
