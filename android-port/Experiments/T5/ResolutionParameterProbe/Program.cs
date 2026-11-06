// T5: source-pin original compiled Settings caller signatures without exposing
// original private class/method/parameter identifiers, tokens, or IL bytes.
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long OriginalSize = 3211776;
    private const string OriginalSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";
    private const string Apply = "ApplyCurrentResolutionAndFullscreenMode";

    private sealed record Report(
        int original_settings_method_bodies,
        int apply_definitions,
        int apply_direct_call_sites,
        int distinct_apply_caller_methods,
        int zero_parameter_caller_count,
        int one_parameter_caller_count,
        string one_parameter_public_type_category,
        bool one_parameter_caller_is_static,
        bool one_parameter_caller_is_public,
        bool one_parameter_caller_is_private,
        bool one_parameter_caller_is_virtual,
        bool one_parameter_caller_returns_void,
        int one_parameter_caller_direct_dropdown_api_calls,
        int one_parameter_caller_dropdown_field_reference_sites,
        int one_parameter_caller_direct_dropdown_value_get_sites,
        int one_parameter_caller_direct_dropdown_value_set_sites,
        int one_parameter_caller_direct_dropdown_refresh_sites,
        int one_parameter_caller_direct_dropdown_onvaluechanged_get_sites,
        int one_parameter_caller_direct_addlistener_sites,
        int one_parameter_caller_direct_playerprefs_write_sites,
        int one_parameter_caller_direct_screen_setresolution_sites,
        int one_parameter_caller_direct_resizebuffers_sites,
        int class_direct_addlistener_sites,
        int class_direct_dropdown_onvaluechanged_get_sites,
        bool unity_serialized_onvaluechanged_binding_proven,
        bool persistent_android_render_scale_binding_proven,
        bool android_device_tested);

    private static string Category(TypeReference type)
    {
        if (type is ByReferenceType) return "by_reference";
        if (type is ArrayType) return "array";
        if (type is GenericInstanceType) return "generic_instance";
        if (type is GenericParameter) return "generic_parameter";
        return type.FullName switch
        {
            "System.Int32" => "system_int32",
            "System.Boolean" => "system_boolean",
            "System.String" => "system_string",
            "System.Single" => "system_float",
            "UnityEngine.Resolution" => "unity_screen_resolution",
            "UnityEngine.UI.Dropdown" => "unity_ui_dropdown",
            "TMPro.TMP_Dropdown" => "tmp_dropdown",
            _ when type.FullName.StartsWith("UnityEngine.UI.", StringComparison.Ordinal)
                => "unity_ui_other",
            _ when type.FullName.StartsWith("UnityEngine.", StringComparison.Ordinal)
                => "unity_engine_other",
            _ when type.FullName.StartsWith("System.", StringComparison.Ordinal)
                => "system_other",
            _ when type.IsValueType => "custom_value_type_or_enum",
            _ => "custom_reference_type"
        };
    }

    private static bool IsCall(Instruction i) =>
        i.OpCode.Code == Code.Call || i.OpCode.Code == Code.Callvirt ||
        i.OpCode.Code == Code.Newobj;

    private static bool Dropdown(TypeReference type) =>
        type.FullName == "UnityEngine.UI.Dropdown" ||
        type.FullName == "TMPro.TMP_Dropdown";

    private static Report Inspect(TypeDefinition box)
    {
        var methods = box.Methods.Where(m => m.HasBody).ToArray();
        if (methods.Length < 1 || methods.Length > 256)
            throw new InvalidDataException("type_bound");
        var applies = box.Methods.Where(m => m.Name == Apply && m.HasBody).ToArray();
        if (applies.Length != 1) throw new InvalidDataException("apply_method_cardinality");
        var callers = new List<MethodDefinition>();
        int callsites = 0, allAdd = 0, allGetEvent = 0;
        foreach (MethodDefinition method in methods)
        {
            int count = 0;
            foreach (Instruction ins in method.Body.Instructions)
            {
                if (!IsCall(ins) || ins.Operand is not MethodReference target) continue;
                if (target.DeclaringType.FullName == box.FullName && target.Name == Apply)
                    count++;
                if (target.Name == "AddListener") allAdd++;
                if (target.Name == "get_onValueChanged" && Dropdown(target.DeclaringType))
                    allGetEvent++;
            }
            if (count > 0)
            {
                callsites += count;
                callers.Add(method);
            }
        }
        if (callsites != 3 || callers.Count != 3 ||
            callers.Count(m => m.Parameters.Count == 0) != 2 ||
            callers.Count(m => m.Parameters.Count == 1) != 1)
            throw new InvalidDataException("original_three_caller_signature_drift");
        MethodDefinition single = callers.Single(m => m.Parameters.Count == 1);
        int dropApi = 0, dropField = 0, dropGet = 0, dropSet = 0,
            dropRefresh = 0, dropEvent = 0, listener = 0,
            prefsWrite = 0, screenSet = 0, resize = 0;
        foreach (Instruction ins in single.Body.Instructions)
        {
            if (ins.Operand is FieldReference field && Dropdown(field.FieldType))
                dropField++;
            if (!IsCall(ins) || ins.Operand is not MethodReference target) continue;
            string owner = target.DeclaringType.FullName, name = target.Name;
            if (Dropdown(target.DeclaringType))
            {
                dropApi++;
                if (name == "get_value") dropGet++;
                if (name == "set_value" || name == "SetValueWithoutNotify") dropSet++;
                if (name == "RefreshShownValue") dropRefresh++;
                if (name == "get_onValueChanged") dropEvent++;
            }
            if (name == "AddListener") listener++;
            if (owner == "UnityEngine.PlayerPrefs" &&
                (name.StartsWith("Set", StringComparison.Ordinal) || name == "Save"))
                prefsWrite++;
            if (owner == "UnityEngine.Screen" && name == "SetResolution") screenSet++;
            if (owner == "UnityEngine.ScalableBufferManager" && name == "ResizeBuffers")
                resize++;
        }
        return new Report(
            methods.Length, applies.Length, callsites, callers.Count,
            2, 1, Category(single.Parameters[0].ParameterType),
            single.IsStatic, single.IsPublic, single.IsPrivate, single.IsVirtual,
            single.ReturnType.FullName == "System.Void",
            dropApi, dropField, dropGet, dropSet, dropRefresh, dropEvent,
            listener, prefsWrite, screenSet, resize,
            allAdd, allGetEvent,
            false, false, false);
    }

    private static void Assert(bool condition)
    {
        if (!condition) throw new InvalidDataException("synthetic_check");
    }

    private static int SelfTest()
    {
        using var module = ModuleDefinition.CreateModule("T5SafeParamFixture", ModuleKind.Dll);
        TypeReference Make(string ns, string name) =>
            new TypeReference(ns, name, module, module.TypeSystem.CoreLibrary);
        Assert(Category(module.TypeSystem.Int32) == "system_int32");
        Assert(Category(module.TypeSystem.Boolean) == "system_boolean");
        Assert(Category(Make("UnityEngine", "Resolution")) == "unity_screen_resolution");
        Assert(Category(Make("UnityEngine.UI", "Dropdown")) == "unity_ui_dropdown");
        Assert(Category(Make("TMPro", "TMP_Dropdown")) == "tmp_dropdown");
        Assert(Category(Make("Game.Internal", "PrivateOriginalType")) == "custom_reference_type");
        Assert(Category(new ArrayType(module.TypeSystem.Int32)) == "array");
        Assert(Category(new ByReferenceType(module.TypeSystem.Int32)) == "by_reference");
        Console.WriteLine("T5_RESOLUTION_PARAMETER_SYNTHETIC 8/8 original=false");
        return 0;
    }

    private static int Original(string filePath, string outputPath)
    {
        var file = new FileInfo(filePath);
        if (!file.Exists || file.Length != OriginalSize)
            throw new InvalidDataException("size");
        using (var bytes = file.OpenRead())
        {
            string digest = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
            if (digest != OriginalSha) throw new InvalidDataException("sha");
        }
        using var assembly = AssemblyDefinition.ReadAssembly(file.FullName,
            new ReaderParameters { ReadSymbols = false });
        var types = assembly.MainModule.Types
            .Where(t => t.Name == "GraphicsSettingsBox").ToArray();
        if (types.Length != 1) throw new InvalidDataException("ambiguous_type");
        Report report = Inspect(types[0]);
        // Preserve previous independently source-verified 42 bodies and
        // eight dropdown API calls / eight dropdown fields in this owner.
        if (report.original_settings_method_bodies != 42 ||
            report.one_parameter_caller_direct_dropdown_api_calls != 8 ||
            report.one_parameter_caller_dropdown_field_reference_sites != 8)
            throw new InvalidDataException("prior_ci_provenance_drift");

        var output = new
        {
            schema_version = 1,
            original_assembly_sha256_verified = true,
            original_assembly_bytes = OriginalSize,
            compiled_original_il = true,
            original_method_and_type_identifiers_private = true,
            report,
            serialized_unity_event_callback_proven = false,
            persisted_android_render_resolution_proven = false,
            original_game_modified = false,
            android_device_tested = false
        };
        string dest = Path.GetFullPath(outputPath);
        if (File.Exists(dest) || Directory.Exists(dest))
            throw new InvalidDataException("destination_exists");
        Directory.CreateDirectory(Path.GetDirectoryName(dest)!);
        string safe = JsonSerializer.Serialize(output);
        File.WriteAllText(dest, safe);
        Console.WriteLine("T5_ORIGINAL_RESOLUTION_PARAMETER " + safe);
        return 0;
    }

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length == 1 && args[0] == "--self-test") return SelfTest();
            if (args.Length == 4 && args[0] == "--assembly" && args[2] == "--output")
                return Original(args[1], args[3]);
        }
        catch (Exception)
        {
            Console.WriteLine("T5_ORIGINAL_RESOLUTION_PARAMETER status=INCONCLUSIVE private_data_logged=false");
            return 2;
        }
        Console.WriteLine("T5_ORIGINAL_RESOLUTION_PARAMETER status=INVALID_ARGUMENTS");
        return 2;
    }
}
