// T5: original-authenticated, strictly bounded compiled IL caller census.
// Publishes no original method IDs/tokens, private strings, IL bytes or game assets.
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

    private sealed record Caller(
        int apply_call_sites,
        int parameters,
        bool has_int_parameter,
        bool has_bool_parameter,
        bool is_known_unity_lifecycle,
        int direct_dropdown_api_calls,
        int direct_dropdown_field_references,
        int direct_screen_resolution_list_reads,
        int direct_screen_current_resolution_reads,
        int direct_playerprefs_reads,
        int direct_playerprefs_writes,
        int direct_custom_settings_type_references,
        int direct_same_type_calls,
        bool contains_option_population,
        bool contains_same_type_delegate_site);

    private sealed record Evidence(
        int original_class_methods_with_body,
        int apply_method_definitions,
        int apply_method_direct_screen_set_resolution_sites,
        int apply_method_direct_scalable_resize_buffers_sites,
        int internal_apply_call_sites,
        int distinct_internal_apply_callers,
        int external_apply_call_sites,
        int distinct_external_apply_callers,
        int external_apply_callers_in_settings_class,
        int original_option_population_sites,
        int original_option_population_methods,
        Caller[] internal_caller_profiles,
        bool serialized_unity_ui_event_binding_proven,
        bool custom_settings_persistence_proven,
        bool android_render_scale_selector_proven,
        bool original_game_modified,
        bool phone_tested);

    private static bool IsCall(Instruction ins) =>
        ins.OpCode.Code == Code.Call || ins.OpCode.Code == Code.Callvirt ||
        ins.OpCode.Code == Code.Newobj;

    private static bool IsApplyReference(MethodReference reference, TypeDefinition box) =>
        reference.DeclaringType.FullName == box.FullName &&
        reference.Name == Apply;

    private static bool IsDropdownType(TypeReference type) =>
        type.FullName == "UnityEngine.UI.Dropdown" ||
        type.FullName == "TMPro.TMP_Dropdown";

    private static bool IsLifecycle(string name) =>
        name is "Awake" or "Start" or "OnEnable" or "OnDisable" or
                "OnDestroy" or "OnValidate" or "Update" or "LateUpdate";

    private static Caller Profile(TypeDefinition box, MethodDefinition method, int applySites)
    {
        int dropdownCalls = 0, dropdownFields = 0, resolutionList = 0,
            current = 0, prefRead = 0, prefWrite = 0, settingsRefs = 0,
            localCalls = 0;
        bool option = false, delegated = false;
        foreach (Instruction ins in method.Body.Instructions)
        {
            if (ins.Operand is FieldReference field)
            {
                if (IsDropdownType(field.FieldType)) dropdownFields++;
                if (field.DeclaringType.Name == "Settings") settingsRefs++;
            }
            if (ins.Operand is not MethodReference target) continue;
            if ((ins.OpCode.Code == Code.Ldftn || ins.OpCode.Code == Code.Ldvirtftn) &&
                target.DeclaringType.FullName == box.FullName)
                delegated = true;
            if (!IsCall(ins)) continue;
            string name = target.Name;
            string owner = target.DeclaringType.FullName;
            if (IsDropdownType(target.DeclaringType))
            {
                dropdownCalls++;
                if (name is "AddOptions" or "ClearOptions" or "SetValueWithoutNotify")
                    option = true;
            }
            if (name is "AddOptions" or "ClearOptions" or "SetValueWithoutNotify")
                option = true;
            if (owner == "UnityEngine.Screen")
            {
                if (name == "get_resolutions") resolutionList++;
                if (name == "get_currentResolution") current++;
            }
            if (owner == "UnityEngine.PlayerPrefs")
            {
                if (name.StartsWith("Get", StringComparison.Ordinal)) prefRead++;
                if (name.StartsWith("Set", StringComparison.Ordinal) || name == "Save")
                    prefWrite++;
            }
            if (target.DeclaringType.Name == "Settings") settingsRefs++;
            if (owner == box.FullName) localCalls++;
        }
        return new Caller(
            applySites, method.Parameters.Count,
            method.Parameters.Any(p => p.ParameterType.FullName == "System.Int32"),
            method.Parameters.Any(p => p.ParameterType.FullName == "System.Boolean"),
            IsLifecycle(method.Name),
            dropdownCalls, dropdownFields, resolutionList, current, prefRead, prefWrite,
            settingsRefs, localCalls, option, delegated);
    }

    private static IEnumerable<TypeDefinition> AllTypes(IEnumerable<TypeDefinition> root)
    {
        foreach (TypeDefinition type in root)
        {
            yield return type;
            foreach (TypeDefinition child in AllTypes(type.NestedTypes)) yield return child;
        }
    }

    private static Evidence Analyze(AssemblyDefinition original, TypeDefinition box)
    {
        MethodDefinition[] methods = box.Methods.Where(m => m.HasBody).ToArray();
        if (methods.Length < 1 || methods.Length > 256)
            throw new InvalidDataException("bounded_class");
        var applyMethods = box.Methods.Where(m => m.Name == Apply).ToArray();
        if (applyMethods.Length != 1 || !applyMethods[0].HasBody)
            throw new InvalidDataException("apply_ambiguity");
        var apply = applyMethods[0];
        int setSites = 0, resizeSites = 0;
        foreach (Instruction instruction in apply.Body.Instructions)
        {
            if (!IsCall(instruction) || instruction.Operand is not MethodReference target)
                continue;
            if (target.DeclaringType.FullName == "UnityEngine.Screen" &&
                target.Name == "SetResolution") setSites++;
            if (target.DeclaringType.FullName == "UnityEngine.ScalableBufferManager" &&
                target.Name == "ResizeBuffers") resizeSites++;
        }

        int internalSites = 0, optionSites = 0;
        var callerRows = new List<Caller>();
        var optionOwners = new HashSet<MethodDefinition>();
        foreach (MethodDefinition method in methods)
        {
            int calls = 0;
            foreach (Instruction ins in method.Body.Instructions)
            {
                if (!IsCall(ins) || ins.Operand is not MethodReference target) continue;
                if (IsApplyReference(target, box)) calls++;
                if (target.Name is "AddOptions" or "ClearOptions" or "SetValueWithoutNotify")
                {
                    optionSites++;
                    optionOwners.Add(method);
                }
            }
            if (calls > 0)
            {
                internalSites += calls;
                callerRows.Add(Profile(box, method, calls));
            }
        }

        int externalSites = 0, externalSettingsSites = 0;
        var externalCallers = new HashSet<MethodDefinition>();
        var typeInventory = AllTypes(original.MainModule.Types).ToArray();
        if (typeInventory.Length > 20000) throw new InvalidDataException("bounded_inventory");
        foreach (TypeDefinition type in typeInventory)
        {
            if (type == box) continue;
            foreach (MethodDefinition method in type.Methods)
            {
                if (!method.HasBody) continue;
                foreach (Instruction ins in method.Body.Instructions)
                {
                    if (!IsCall(ins) || ins.Operand is not MethodReference target ||
                        !IsApplyReference(target, box)) continue;
                    externalSites++;
                    externalCallers.Add(method);
                    if (type.Name == "Settings") externalSettingsSites++;
                }
            }
        }
        var profiles = callerRows
            .OrderBy(c => c.parameters)
            .ThenBy(c => c.apply_call_sites)
            .ThenBy(c => c.direct_dropdown_api_calls)
            .ThenBy(c => c.direct_screen_resolution_list_reads)
            .ThenBy(c => c.direct_playerprefs_writes)
            .ToArray();
        return new Evidence(
            methods.Length, applyMethods.Length, setSites, resizeSites,
            internalSites, profiles.Length, externalSites, externalCallers.Count,
            externalSettingsSites, optionSites, optionOwners.Count,
            profiles,
            false, // Cecil method references alone do not show serialized UnityEvent wiring.
            false, // No direct PlayerPrefs is not proof custom persistence absent.
            false, // Desktop screen-mode mutation is not Android render-scale selection.
            false, false);
    }

    private static TypeDefinition Type(ModuleDefinition mod, string name)
    {
        var type = new TypeDefinition("", name, Mono.Cecil.TypeAttributes.Public,
            mod.TypeSystem.Object);
        mod.Types.Add(type);
        return type;
    }

    private static MethodDefinition Method(TypeDefinition owner, string name,
        TypeReference? param = null)
    {
        var method = new MethodDefinition(name, Mono.Cecil.MethodAttributes.Public,
            owner.Module.TypeSystem.Void);
        if (param is not null) method.Parameters.Add(new ParameterDefinition(param));
        owner.Methods.Add(method);
        return method;
    }

    private static MethodReference External(ModuleDefinition module,
        string ns, string type, string method) =>
        new MethodReference(method, module.TypeSystem.Void,
            new TypeReference(ns, type, module, module.TypeSystem.CoreLibrary));

    private static void Assert(bool condition)
    {
        if (!condition) throw new InvalidDataException("synthetic_assertion");
    }

    private static int SelfTest()
    {
        using var module = ModuleDefinition.CreateModule("SyntheticOnly", ModuleKind.Dll);
        var type = Type(module, "GraphicsSettingsBox");
        var apply = Method(type, Apply);
        apply.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(module, "UnityEngine", "Screen", "SetResolution")));
        apply.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));

        var lifecycle = Method(type, "OnEnable");
        lifecycle.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(module, "UnityEngine.UI", "Dropdown", "AddOptions")));
        lifecycle.Body.Instructions.Add(Instruction.Create(OpCodes.Call, apply));
        lifecycle.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));

        var selection = Method(type, "SyntheticSelection", module.TypeSystem.Int32);
        selection.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(module, "UnityEngine", "PlayerPrefs", "SetInt")));
        selection.Body.Instructions.Add(Instruction.Create(OpCodes.Call, apply));
        selection.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));

        var refresh = Method(type, "Refresh");
        refresh.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(module, "UnityEngine", "Screen", "get_currentResolution")));
        refresh.Body.Instructions.Add(Instruction.Create(OpCodes.Call, apply));
        refresh.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));

        using var assembly = AssemblyDefinition.CreateAssembly(
            new AssemblyNameDefinition("Synthetic", new Version(1, 0)), "Synthetic", ModuleKind.Dll);
        // Analyze the module the synthetic methods actually belong to.
        // Cecil ModuleDefinition.Assembly may be null for CreateModule: rely on
        // its original owning ModuleDefinition rather than a detached assembly.
        // Rebuild the fixture in a proper AssemblyDefinition instead.
        var own = assembly.MainModule;
        var owner = Type(own, "GraphicsSettingsBox");
        var apply2 = Method(owner, Apply);
        apply2.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(own, "UnityEngine", "Screen", "SetResolution")));
        apply2.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        var a = Method(owner, "OnEnable");
        a.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(own, "UnityEngine.UI", "Dropdown", "AddOptions")));
        a.Body.Instructions.Add(Instruction.Create(OpCodes.Call, apply2));
        a.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        var c = Method(owner, "SyntheticSelection", own.TypeSystem.Int32);
        c.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(own, "UnityEngine", "PlayerPrefs", "SetInt")));
        c.Body.Instructions.Add(Instruction.Create(OpCodes.Call, apply2));
        c.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        var d = Method(owner, "Refresh");
        d.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(own, "UnityEngine", "Screen", "get_currentResolution")));
        d.Body.Instructions.Add(Instruction.Create(OpCodes.Call, apply2));
        d.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));

        Evidence ev = Analyze(assembly, owner);
        Assert(ev.internal_apply_call_sites == 3 && ev.distinct_internal_apply_callers == 3);
        Assert(ev.apply_method_direct_screen_set_resolution_sites == 1 &&
               ev.apply_method_direct_scalable_resize_buffers_sites == 0);
        Assert(ev.internal_caller_profiles.Count(x => x.contains_option_population) == 1 &&
               ev.internal_caller_profiles.Count(x => x.has_int_parameter) == 1);
        Assert(ev.internal_caller_profiles.Sum(x => x.direct_playerprefs_writes) == 1 &&
               ev.internal_caller_profiles.Sum(x => x.direct_screen_current_resolution_reads) == 1);
        Assert(ev.external_apply_call_sites == 0 && !ev.android_render_scale_selector_proven);
        Console.WriteLine("T5_APPLY_CALLER_IL_SELFTEST 5/5 synthetic=true original=false");
        return 0;
    }

    private static int Original(string fileName, string outputName)
    {
        var f = new FileInfo(fileName);
        if (!f.Exists || f.Length != OriginalSize) throw new InvalidDataException("source_size");
        using (var stream = f.OpenRead())
        {
            string digest = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
            if (digest != OriginalSha) throw new InvalidDataException("source_sha");
        }
        using var assembly = AssemblyDefinition.ReadAssembly(f.FullName,
            new ReaderParameters { ReadSymbols = false });
        var box = AllTypes(assembly.MainModule.Types)
            .Where(t => t.Name == "GraphicsSettingsBox").ToArray();
        if (box.Length != 1) throw new InvalidDataException("type_cardinality");
        var ev = Analyze(assembly, box[0]);
        if (ev.internal_apply_call_sites != 3 ||
            ev.apply_method_direct_screen_set_resolution_sites != 1 ||
            ev.apply_method_definitions != 1 ||
            ev.original_option_population_sites != 1 ||
            ev.distinct_internal_apply_callers < 1 ||
            ev.distinct_internal_apply_callers > 3)
            throw new InvalidDataException("original_callsite_regression");

        var report = new {
            schema_version = 1,
            original_assembly_sha_verified = true,
            original_assembly_bytes = OriginalSize,
            compiled_original_il_not_decompiled_source = true,
            original_graphics_settings_type_unique = true,
            output_method_names_tokens_private = true,
            evidence = ev,
            selection_to_runtime_callback_proven = false,
            persisted_android_render_scale_proven = false,
            device_tested = false
        };
        string path = Path.GetFullPath(outputName);
        if (File.Exists(path) || Directory.Exists(path))
            throw new InvalidDataException("output_exists");
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        string json = JsonSerializer.Serialize(report);
        File.WriteAllText(path, json);
        Console.WriteLine("T5_ORIGINAL_APPLY_CALLER_IL " + json);
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
            Console.WriteLine("T5_ORIGINAL_APPLY_CALLER_IL status=INCONCLUSIVE private_data_logged=false");
            return 2;
        }
        Console.WriteLine("T5_ORIGINAL_APPLY_CALLER_IL status=INVALID_ARGUMENTS");
        return 2;
    }
}
