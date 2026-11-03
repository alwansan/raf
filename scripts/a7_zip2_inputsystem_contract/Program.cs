// Source-authenticated read-only ABI check for the owner's original Raft InputSystem DLL.
// Never load or execute the Windows game assembly; only inspect .NET metadata.
using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Security.Cryptography;
using System.Text.Json;

internal static class Program
{
    private const long ExpectedBytes = 1_052_672;
    private const string ExpectedSha = "032031efe7f85aec81e28f4af43be496be3cf83d8d20e314ba9de8ca95ebfc3f";
    private const string ExpectedScriptingSha = "50becc5aca96c0287bd8e909cea80ffbb94e45631f8dbb45740c0614e00cbf20";
    private const string ManifestKey = "Raft_Data/Managed/Unity.InputSystem.dll";

    private static void Require(bool condition, string claim)
    {
        if (!condition)
            throw new InvalidOperationException("A7_ZIP2_INPUTSYSTEM_ABI: " + claim);
    }

    private static string Sha256(string file) =>
        Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(file))).ToLowerInvariant();

    private static TypeDefinition FindType(MetadataReader reader, string nameSpace, string name)
    {
        foreach (var handle in reader.TypeDefinitions)
        {
            var candidate = reader.GetTypeDefinition(handle);
            if (reader.GetString(candidate.Namespace) == nameSpace &&
                reader.GetString(candidate.Name) == name)
                return candidate;
        }
        throw new InvalidOperationException("A7_ZIP2_INPUTSYSTEM_ABI: missing-type " + nameSpace + "." + name);
    }

    private static bool HasPublicField(MetadataReader reader, TypeDefinition type, string fieldName)
    {
        foreach (var handle in type.GetFields())
        {
            var field = reader.GetFieldDefinition(handle);
            if (reader.GetString(field.Name) == fieldName &&
                (field.Attributes & FieldAttributes.FieldAccessMask) == FieldAttributes.Public)
                return true;
        }
        return false;
    }

    private static bool HasPublicReadableProperty(MetadataReader reader, TypeDefinition type, string propertyName)
    {
        foreach (var handle in type.GetProperties())
        {
            var property = reader.GetPropertyDefinition(handle);
            if (reader.GetString(property.Name) != propertyName)
                continue;
            var getter = property.GetAccessors().Getter;
            if (getter.IsNil)
                return false;
            var method = reader.GetMethodDefinition(getter);
            return (method.Attributes & MethodAttributes.MemberAccessMask) == MethodAttributes.Public;
        }
        return false;
    }

    private static bool HasPublicReadWriteProperty(MetadataReader reader, TypeDefinition type, string propertyName)
    {
        foreach (var handle in type.GetProperties())
        {
            var property = reader.GetPropertyDefinition(handle);
            if (reader.GetString(property.Name) != propertyName)
                continue;
            var accessors = property.GetAccessors();
            if (accessors.Getter.IsNil || accessors.Setter.IsNil)
                return false;
            var get = reader.GetMethodDefinition(accessors.Getter);
            var set = reader.GetMethodDefinition(accessors.Setter);
            return (get.Attributes & MethodAttributes.MemberAccessMask) == MethodAttributes.Public &&
                   (set.Attributes & MethodAttributes.MemberAccessMask) == MethodAttributes.Public;
        }
        return false;
    }

    private static bool HasMethod(MetadataReader reader, TypeDefinition type, string methodName,
                                  bool generic = false)
    {
        foreach (var handle in type.GetMethods())
        {
            var method = reader.GetMethodDefinition(handle);
            if (reader.GetString(method.Name) == methodName &&
                (method.Attributes & MethodAttributes.MemberAccessMask) == MethodAttributes.Public &&
                (!generic || method.GetGenericParameters().Count > 0))
                return true;
        }
        return false;
    }

    private static void Verify(string dll, string manifest, string scripting)
    {
        Require(new FileInfo(dll).Length == ExpectedBytes, "original-size-mismatch");
        Require(Sha256(dll) == ExpectedSha, "original-sha256-mismatch");
        var expected = "plain\t" + ExpectedBytes + "\t" + ExpectedSha + "\t660\t" + ManifestKey;
        var rows = File.ReadAllLines(manifest)
                       .Where(row => row.EndsWith("\t" + ManifestKey, StringComparison.Ordinal))
                       .ToArray();
        Require(rows.Length == 1 && rows[0] == expected, "original-manifest-mismatch");
        Require(Sha256(scripting) == ExpectedScriptingSha, "original-scripting-assemblies-sha256-mismatch");
        using (var doc = JsonDocument.Parse(File.ReadAllText(scripting)))
        {
            var names = doc.RootElement.GetProperty("names").EnumerateArray()
                           .Select(x => x.GetString()).ToArray();
            Require(names.Contains("Unity.InputSystem.dll", StringComparer.Ordinal),
                    "original-scripting-assemblies-missing-inputsystem");
        }
        using var file = File.OpenRead(dll);
        using var pe = new PEReader(file);
        Require(pe.HasMetadata, "not-managed-metadata");
        var reader = pe.GetMetadataReader();

        // Check the ACTUAL original Windows game DLL's contract, not upstream/tag names.
        var stateEvent = FindType(reader, "UnityEngine.InputSystem.LowLevel", "StateEvent");
        var touchState = FindType(reader, "UnityEngine.InputSystem.LowLevel", "TouchState");
        var eventPtr = FindType(reader, "UnityEngine.InputSystem.LowLevel", "InputEventPtr");
        var screen = FindType(reader, "UnityEngine.InputSystem", "Touchscreen");
        var system = FindType(reader, "UnityEngine.InputSystem", "InputSystem");
        Require(HasMethod(reader, stateEvent, "GetState", generic: true),
                "missing-public-StateEvent.GetState-generic");
        Require(HasPublicField(reader, touchState, "touchId"), "missing-public-TouchState.touchId");
        Require(HasPublicField(reader, touchState, "position"), "missing-public-TouchState.position");
        // Unity's original packed TouchState stores phaseId as a byte and exposes
        // phase through a public property, not through a public field.
        Require(HasPublicField(reader, touchState, "phaseId"), "missing-public-TouchState.phaseId");
        Require(HasPublicReadableProperty(reader, touchState, "phase"),
                "missing-public-TouchState.phase-getter");
        Require(HasMethod(reader, eventPtr, "IsA", generic: true),
                "missing-public-InputEventPtr.IsA-generic");
        // InputSystem 1.7 onEvent is a public get/set InputEventListener
        // property supporting compound +=/-=, not a CLI event with add_onEvent.
        Require(HasPublicReadWriteProperty(reader, system, "onEvent"),
                "missing-public-InputSystem.onEvent-read-write-property");
        Require(HasMethod(reader, system, "add_onBeforeUpdate"),
                "missing-public-InputSystem.onBeforeUpdate");
        // A type lookup for Touchscreen also ensures its interface is present.
        Require(screen.GetMethods().Count > 0, "empty-Touchscreen-type");

        Console.WriteLine("RAFT_A7_ZIP2_INPUTSYSTEM_ABI authenticated_source=true bytes=" +
                          ExpectedBytes + " metadata_types=" + reader.TypeDefinitions.Count +
                          " touchstate_fields=3 phase_property=true onEvent_property=true public_raw_state_api=true original_lfs_used=false" +
                          " unity_execution=false android_device_execution=false");
    }

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length != 3)
                throw new ArgumentException("Expected DLL, ZIP2 manifest and ScriptingAssemblies.json paths");
            Verify(args[0], args[1], args[2]);
            return 0;
        }
        catch (Exception e)
        {
            Console.Error.WriteLine("RAFT_A7_ZIP2_INPUTSYSTEM_ABI failure=" + e.Message);
            return 1;
        }
    }
}
