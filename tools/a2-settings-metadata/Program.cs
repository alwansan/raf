// Read exact original managed TypeDef/FieldDef metadata in a private CI output.
// Input game assembly and output JSON stay transient; no original type/field names
// or game source are logged, committed, uploaded or included in workflow artifacts.
using System.Text.Json;
using Mono.Cecil;

if (args.Length != 2)
    throw new ArgumentException("Pass ORIGINAL_ASSEMBLY and PRIVATE_OUTPUT_JSON paths");
string assemblyPath = Path.GetFullPath(args[0]);
string outputPath = Path.GetFullPath(args[1]);
if (!File.Exists(assemblyPath) || new FileInfo(assemblyPath).Length > 8_000_000)
    throw new InvalidOperationException("Original source-managed assembly missing or oversized");
if (!Path.IsPathFullyQualified(outputPath))
    throw new InvalidOperationException("Private destination must have absolute path");
using AssemblyDefinition assembly = AssemblyDefinition.ReadAssembly(
    assemblyPath, new ReaderParameters { ReadingMode = ReadingMode.Deferred });
if (assembly.Name.Name != "Assembly-CSharp")
    throw new InvalidOperationException("Unexpected original assembly identity");

static IEnumerable<TypeDefinition> Walk(IEnumerable<TypeDefinition> roots)
{
    foreach (TypeDefinition type in roots)
    {
        yield return type;
        foreach (TypeDefinition nested in Walk(type.NestedTypes))
            yield return nested;
    }
}

static string Kind(TypeReference tr, string ownerAssembly)
{
    if (tr is ArrayType)
        return "array";
    if (tr is GenericInstanceType gi)
        return gi.ElementType.FullName.StartsWith("System.Collections.Generic.List", StringComparison.Ordinal)
            ? "list_generic" : "generic_other";
    if (tr.MetadataType is MetadataType.Boolean or MetadataType.Int32
        or MetadataType.Single or MetadataType.Byte or MetadataType.SByte
        or MetadataType.Int16 or MetadataType.UInt16 or MetadataType.UInt32)
        return "primitive_4byte_or_smaller";
    if (tr.MetadataType is MetadataType.Int64 or MetadataType.UInt64
        or MetadataType.Double)
        return "primitive_8byte";
    if (tr.MetadataType == MetadataType.String)
        return "string";
    if (tr.FullName.StartsWith("UnityEngine.", StringComparison.Ordinal))
        return "unity_engine_type_unverified_base";
    try
    {
        TypeDefinition? def = tr.Resolve();
        if (def == null)
            return "unresolved_external";
        if (def.IsEnum)
            return "enum";
        if (def.IsValueType)
            return "value_type";
        if (def.Module.Assembly.Name.Name == ownerAssembly)
            return "same_assembly_class";
        return "resolved_external_class";
    }
    catch
    {
        return "unresolved_external";
    }
}

static object Field(FieldDefinition f, string ownerAssembly)
{
    string typeName = f.FieldType.FullName;
    string? elementName = f.FieldType switch
    {
        ArrayType a => a.ElementType.FullName,
        GenericInstanceType g when g.GenericArguments.Count == 1
            => g.GenericArguments[0].FullName,
        _ => null,
    };
    return new
    {
        name = f.Name,
        token = f.MetadataToken.ToInt32(),
        declaring_type = f.DeclaringType.FullName,
        type_name = typeName,
        kind = Kind(f.FieldType, ownerAssembly),
        element_kind = f.FieldType switch
        {
            ArrayType a => Kind(a.ElementType, ownerAssembly),
            GenericInstanceType g when g.GenericArguments.Count == 1
                => Kind(g.GenericArguments[0], ownerAssembly),
            _ => null,
        },
        element_type_name = elementName,
        is_public = f.IsPublic,
        is_static = f.IsStatic,
        is_const = f.IsLiteral,
        is_readonly = f.IsInitOnly,
        is_not_serialized = f.IsNotSerialized,
        has_serialize_field = f.CustomAttributes.Any(a =>
            a.AttributeType.FullName == "UnityEngine.SerializeField"),
        has_serialize_reference = f.CustomAttributes.Any(a =>
            a.AttributeType.FullName == "UnityEngine.SerializeReference"),
        has_nonserialized_attribute = f.CustomAttributes.Any(a =>
            a.AttributeType.FullName is "System.NonSerializedAttribute"),
    };
}

var settingsCandidates = Walk(assembly.MainModule.Types)
    .Where(t => t.Name == "Settings" && t.IsClass && t.FullName.Length < 256)
    .Select(t => new
    {
        name = t.Name,
        namespace_name = t.Namespace,
        full_name = t.FullName,
        token = t.MetadataToken.ToInt32(),
        base_name = t.BaseType?.FullName,
        is_abstract = t.IsAbstract,
        fields = t.Fields.Select(f => Field(f, assembly.Name.Name)).ToArray(),
    }).ToArray();
if (settingsCandidates.Length is 0 or > 16)
    throw new InvalidOperationException("Source type identity missing or ambiguous");
if (settingsCandidates.Any(t => t.fields.Length > 256))
    throw new InvalidOperationException("Unbounded original field metadata");
var data = new
{
    format_version = 1,
    assembly_name = assembly.Name.Name,
    candidate_types = settingsCandidates,
};
Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
File.WriteAllText(outputPath, JsonSerializer.Serialize(data));
Console.WriteLine("A2_PRIVATE_ORIGINAL_MANAGED_SETTINGS_METADATA saved=true; source_names_printed=false");
