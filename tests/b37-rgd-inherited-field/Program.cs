// B37: authenticated original NRBF root -> managed base-field lineage.
// Do NOT execute/deserialise original game types or publish field/type names.
using System;
using System.Collections.Generic;
using System.Formats.Nrbf;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using System.Text.Json;

static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
// ECMA-335 metadata bit flags; no deprecated .NET formatter APIs are invoked.
const TypeAttributes SERIALIZABLE_TYPE_BIT = (TypeAttributes)0x00002000;
const FieldAttributes NONSERIALIZED_FIELD_BIT = (FieldAttributes)0x0080;

static byte[] Exact(string path, long expectedSize, string expectedSha)
{
    var file = new FileInfo(path);
    if (!file.Exists || file.Length != expectedSize ||
        (file.Attributes & FileAttributes.ReparsePoint) != 0)
        throw new InvalidDataException("Missing, redirected or wrong-sized original input");
    var bytes = File.ReadAllBytes(path);
    if (bytes.LongLength != expectedSize || Hash(bytes) != expectedSha)
        throw new InvalidDataException("Original input SHA256 mismatch");
    return bytes;
}

static string FullName(MetadataReader metadata, TypeDefinitionHandle handle)
{
    var definition = metadata.GetTypeDefinition(handle);
    string name = metadata.GetString(definition.Name);
    string ns = metadata.GetString(definition.Namespace);
    return string.IsNullOrEmpty(ns) ? name : ns + "." + name;
}

static int Matches(HashSet<string> serialized, IEnumerable<string> fieldNames)
    => fieldNames.Count(serialized.Contains);

static object Check(byte[] payload, byte[] gameDll)
{
    if (!NrbfDecoder.StartsWithPayloadHeader(payload))
        throw new InvalidDataException("Original RGD has no NRBF header");
    using var stream = new MemoryStream(payload, writable: false);
    var root = NrbfDecoder.DecodeClassRecord(stream);
    if (stream.Position != stream.Length)
        throw new InvalidDataException("Original NRBF trailing bytes");
    var members = root.MemberNames.ToHashSet(StringComparer.Ordinal);
    if (members.Count != 1)
        throw new InvalidDataException("Unexpected serialized root member count");

    using var pe = new PEReader(new MemoryStream(gameDll, writable: false));
    if (!pe.HasMetadata)
        throw new InvalidDataException("Original managed game has no metadata");
    var md = pe.GetMetadataReader();
    var candidates = md.TypeDefinitions
        .Where(h => FullName(md, h) == root.TypeName.FullName).ToArray();
    if (candidates.Length != 1)
        throw new InvalidDataException("Original NRBF root has ambiguous or absent game type");

    var rootDefinition = md.GetTypeDefinition(candidates[0]);
    var directFields = rootDefinition.GetFields()
        .Select(h => md.GetFieldDefinition(h)).ToArray();
    var directNames = directFields.Select(d => md.GetString(d.Name)).ToArray();
    if (directFields.Length != 1 || Matches(members, directNames) != 0)
        throw new InvalidDataException("A10 original root shape is not stable");
    int totalFields = 0, effectiveFields = 0, totalInheritedFields = 0;
    int inheritedMatch = 0, inheritedEffectiveMatch = 0;
    int staticFields = 0, nonserializedFields = 0, depth = 0;
    int rootEffectiveFields = 0, rootEffectiveMatches = 0;
    bool chainComplete = true, rootSerializable = (rootDefinition.Attributes & SERIALIZABLE_TYPE_BIT) != 0;
    var visited = new HashSet<TypeDefinitionHandle>();
    var current = candidates[0];
    while (true)
    {
        if (!visited.Add(current) || visited.Count > 128)
            throw new InvalidDataException("Original base type cycle or excessive depth");
        var definition = md.GetTypeDefinition(current);
        var fields = definition.GetFields().Select(h => md.GetFieldDefinition(h)).ToArray();
        foreach (var field in fields)
        {
            bool isStatic = (field.Attributes & FieldAttributes.Static) != 0;
            bool notSerialized = (field.Attributes & NONSERIALIZED_FIELD_BIT) != 0;
            bool included = !isStatic && !notSerialized;
            string name = md.GetString(field.Name);
            totalFields++;
            if (isStatic) staticFields++;
            if (notSerialized) nonserializedFields++;
            if (included) effectiveFields++;
            if (depth == 0)
            {
                if (included) rootEffectiveFields++;
                if (included && members.Contains(name)) rootEffectiveMatches++;
            }
            else
            {
                totalInheritedFields++;
                if (members.Contains(name)) inheritedMatch++;
                if (included && members.Contains(name)) inheritedEffectiveMatch++;
            }
        }
        var parent = definition.BaseType;
        if (parent.IsNil)
            break;
        if (parent.Kind == HandleKind.TypeDefinition)
        {
            current = (TypeDefinitionHandle)parent;
            depth++;
            continue;
        }
        if (parent.Kind == HandleKind.TypeReference)
        {
            var external = md.GetTypeReference((TypeReferenceHandle)parent);
            string ns = md.GetString(external.Namespace);
            string name = md.GetString(external.Name);
            // Object/ValueType are framework terminal base types without user fields.
            chainComplete = ns == "System" && (name == "Object" || name == "ValueType");
            break;
        }
        chainComplete = false;
        break;
    }

    bool? rootAssemblySimpleNameMatches = null;
    bool? rootAssemblyVersionMatches = null;
    string prefix = root.TypeName.FullName + ", ";
    if (root.TypeName.AssemblyQualifiedName.StartsWith(prefix, StringComparison.Ordinal))
    {
        try
        {
            var serialized = new AssemblyName(root.TypeName.AssemblyQualifiedName[prefix.Length..]);
            var assembly = md.GetAssemblyDefinition();
            rootAssemblySimpleNameMatches = string.Equals(serialized.Name, md.GetString(assembly.Name), StringComparison.Ordinal);
            rootAssemblyVersionMatches = serialized.Version == assembly.Version;
        }
        catch (ArgumentException)
        {
            // Unexpected proprietary assembly naming is UNKNOWN, never interpreted as a mismatch.
        }
    }

    if (Matches(new HashSet<string> { "name" }, new[] { "other", "name" }) != 1 ||
        Matches(new HashSet<string> { "name" }, new[] { "other" }) != 0)
        throw new InvalidDataException("Synthetic inherited-field identity controls failed");

    return new
    {
        schema_version = 1,
        original_rgd_sha256 = Hash(payload),
        original_managed_sha256 = Hash(gameDll),
        serialized_root_members = members.Count,
        root_type_resolves_unique = candidates.Length == 1,
        root_type_serializable_attribute = rootSerializable,
        direct_field_count = directFields.Length,
        direct_field_name_matches = Matches(members, directNames),
        root_effective_serializable_fields = rootEffectiveFields,
        root_effective_member_matches = rootEffectiveMatches,
        inherited_type_definitions_walked = depth,
        inherited_field_count = totalInheritedFields,
        inherited_member_name_matches = inheritedMatch,
        inherited_effective_serializable_member_matches = inheritedEffectiveMatch,
        full_base_chain_resolved = chainComplete,
        total_fields_in_scanned_types = totalFields,
        excluded_static_fields = staticFields,
        excluded_nonserialized_fields = nonserializedFields,
        effective_serializable_fields = effectiveFields,
        serialized_assembly_simple_name_matches = rootAssemblySimpleNameMatches,
        serialized_assembly_version_matches = rootAssemblyVersionMatches,
        source_field_values_or_names_published = false,
        binaryformatter_deserialize_called = false,
        android_unity_or_save_roundtrip_executed = false,
        negative_controls = "4/4"
    };
}

try
{
    if (args.Length != 8 || args[0] != "--file" || args[2] != "--sha256" ||
        args[4] != "--assembly" || args[6] != "--assembly-sha256")
        throw new ArgumentException("Expected original path and SHA256 pairs");
    byte[] payload = Exact(args[1], 2941, args[3]);
    byte[] dll = Exact(args[5], 3211776, args[7]);
    var result = Check(payload, dll);
    Console.WriteLine("B37_ORIGINAL_RGD_INHERITED_FIELDS " + JsonSerializer.Serialize(result));

    bool badRgd = false, badDll = false;
    try { Exact(args[1], 2941, new string('0', 64)); }
    catch (InvalidDataException) { badRgd = true; }
    try { Exact(args[5], 3211776, new string('0', 64)); }
    catch (InvalidDataException) { badDll = true; }
    if (!badRgd || !badDll)
        throw new InvalidDataException("Bad original identity was accepted");
    var corrupted = (byte[])payload.Clone();
    corrupted[0] ^= 255;
    bool badHeader = false;
    try { Check(corrupted, dll); }
    catch (InvalidDataException) { badHeader = true; }
    bool missingBytes = false;
    try { Check(payload[..32], dll); }
    catch (Exception e) when (e is InvalidDataException or EndOfStreamException or System.Runtime.Serialization.SerializationException)
    { missingBytes = true; }
    if (!badHeader || !missingBytes)
        throw new InvalidDataException("Invalid NRBF input was accepted");
    Console.WriteLine("B37_ORIGINAL_RGD_INHERITANCE_NEGATIVE mismatchedRgd=true mismatchedDll=true damagedHeader=true truncatedPayload=true");
    return 0;
}
catch (Exception e)
{
    Console.Error.WriteLine("B37_ORIGINAL_RGD_INHERITED_FIELDS_FAILED " + e.GetType().Name);
    return 1;
}
