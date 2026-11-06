// T5 isolated bounded IL topology for an authenticated original Settings type.
// Never publish source IL, method tokens, symbols, identifiers or game bytes.
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long OriginalBytes = 3211776;
    private const string OriginalSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";

    private sealed record Evidence(
        int compiled_methods,
        int delegate_instruction_sites,
        int resolved_delegate_sites,
        int unresolved_delegate_sites,
        int unique_delegate_target_methods,
        int delegate_targets_with_int_parameter,
        int option_population_call_sites,
        int methods_populating_options,
        int option_methods_with_delegate_sites,
        int option_methods_direct_apply_calls,
        int option_methods_reach_apply,
        int option_methods_reach_screen_setresolution,
        int delegate_targets_direct_apply_calls,
        int delegate_targets_reach_apply,
        int delegate_targets_direct_screen_setresolution,
        int delegate_targets_reach_screen_setresolution,
        int delegate_targets_direct_playerprefs_write,
        int internal_direct_call_edges,
        int unresolved_internal_call_sites,
        bool runtime_dropdown_callback_binding_proven,
        bool original_custom_persistence_proven,
        bool android_render_scale_binding_proven);

    private static bool IsCall(Instruction ins) =>
        ins.OpCode.Code == Code.Call || ins.OpCode.Code == Code.Callvirt ||
        ins.OpCode.Code == Code.Newobj;

    private static MethodDefinition? Owned(
        HashSet<MethodDefinition> methods, MethodReference reference)
    {
        if (reference is MethodDefinition definition && methods.Contains(definition))
            return definition;
        try
        {
            MethodDefinition? resolved = reference.Resolve();
            return resolved is not null && methods.Contains(resolved) ? resolved : null;
        }
        catch (Exception) { return null; }
    }

    private static bool CanReach(
        MethodDefinition start,
        HashSet<MethodDefinition> targets,
        Dictionary<MethodDefinition, HashSet<MethodDefinition>> graph)
    {
        var pending = new Stack<MethodDefinition>();
        var visited = new HashSet<MethodDefinition>();
        pending.Push(start);
        while (pending.Count > 0)
        {
            MethodDefinition next = pending.Pop();
            if (!visited.Add(next)) continue;
            if (visited.Count > 256) throw new InvalidDataException("bounded_graph");
            if (targets.Contains(next)) return true;
            foreach (MethodDefinition edge in graph[next]) pending.Push(edge);
        }
        return false;
    }

    private static Evidence Analyze(TypeDefinition type)
    {
        var methods = type.Methods.Where(m => m.HasBody).ToArray();
        if (methods.Length < 1 || methods.Length > 256)
            throw new InvalidDataException("type_bounds");
        var owned = new HashSet<MethodDefinition>(methods);
        var graph = methods.ToDictionary(m => m, m => new HashSet<MethodDefinition>());
        var delegated = new List<(MethodDefinition source, MethodDefinition? target)>();
        var optionMethods = new HashSet<MethodDefinition>();
        var setterMethods = new HashSet<MethodDefinition>();
        var applyMethods = new HashSet<MethodDefinition>(methods.Where(m =>
            m.Name == "ApplyCurrentResolutionAndFullscreenMode"));
        var prefWriteMethods = new HashSet<MethodDefinition>();
        int optionSites = 0, unresolvedCalls = 0;

        foreach (MethodDefinition source in methods)
        {
            foreach (Instruction instruction in source.Body.Instructions)
            {
                if (instruction.Operand is not MethodReference reference) continue;
                string ownerName = reference.DeclaringType.FullName;
                string name = reference.Name;
                if ((instruction.OpCode.Code == Code.Ldftn ||
                     instruction.OpCode.Code == Code.Ldvirtftn) &&
                    ownerName == type.FullName)
                {
                    delegated.Add((source, Owned(owned, reference)));
                    continue;
                }
                if (!IsCall(instruction)) continue;
                if (ownerName == type.FullName)
                {
                    MethodDefinition? target = Owned(owned, reference);
                    if (target is null) unresolvedCalls++;
                    else graph[source].Add(target);
                }
                if (ownerName == "UnityEngine.Screen" && name == "SetResolution")
                    setterMethods.Add(source);
                if (name == "AddOptions" || name == "ClearOptions" ||
                    name == "SetValueWithoutNotify")
                {
                    optionSites++;
                    optionMethods.Add(source);
                }
                if (ownerName == "UnityEngine.PlayerPrefs" &&
                    (name.StartsWith("Set", StringComparison.Ordinal) || name == "Save"))
                    prefWriteMethods.Add(source);
            }
        }

        var targetMethods = new HashSet<MethodDefinition>(delegated
            .Where(pair => pair.target is not null)
            .Select(pair => pair.target!));
        int withInt = targetMethods.Count(m => m.Parameters.Any(p =>
            p.ParameterType.FullName == "System.Int32"));

        bool DirectTo(MethodDefinition method, HashSet<MethodDefinition> targets) =>
            graph[method].Any(targets.Contains);

        return new Evidence(
            methods.Length,
            delegated.Count,
            delegated.Count(pair => pair.target is not null),
            delegated.Count(pair => pair.target is null),
            targetMethods.Count,
            withInt,
            optionSites,
            optionMethods.Count,
            optionMethods.Count(method => delegated.Any(pair => pair.source == method)),
            optionMethods.Count(m => DirectTo(m, applyMethods)),
            optionMethods.Count(m => CanReach(m, applyMethods, graph)),
            optionMethods.Count(m => CanReach(m, setterMethods, graph)),
            targetMethods.Count(m => DirectTo(m, applyMethods)),
            targetMethods.Count(m => CanReach(m, applyMethods, graph)),
            targetMethods.Count(m => setterMethods.Contains(m)),
            targetMethods.Count(m => CanReach(m, setterMethods, graph)),
            targetMethods.Count(prefWriteMethods.Contains),
            graph.Values.Sum(e => e.Count),
            unresolvedCalls,
            false, // IL method references do not establish serialized UI callbacks.
            false, // PlayerPrefs alone cannot verify custom game persistence.
            false); // Desktop SetResolution is not a working Android render-scale option.
    }

    // Synthetic fixtures prove topology counts, and avoid publishing any original IL.
    private static TypeDefinition NewType(ModuleDefinition mod, string name)
    {
        var type = new TypeDefinition("", name, Mono.Cecil.TypeAttributes.Public,
            mod.TypeSystem.Object);
        mod.Types.Add(type);
        return type;
    }

    private static MethodDefinition NewMethod(TypeDefinition type, string name)
    {
        var method = new MethodDefinition(name, Mono.Cecil.MethodAttributes.Public,
            type.Module.TypeSystem.Void);
        type.Methods.Add(method);
        return method;
    }

    private static MethodReference External(ModuleDefinition module,
        string ns, string owner, string name) =>
        new MethodReference(name, module.TypeSystem.Void,
            new TypeReference(ns, owner, module, module.TypeSystem.CoreLibrary));

    private static void Assert(bool condition)
    {
        if (!condition) throw new InvalidDataException("synthetic");
    }

    private static int SelfTest()
    {
        using var mod = ModuleDefinition.CreateModule("T5GraphSynthetic", ModuleKind.Dll);
        TypeDefinition owner = NewType(mod, "GraphicsSettingsBox");
        MethodDefinition setter = NewMethod(owner, "ApplyCurrentResolutionAndFullscreenMode");
        setter.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(mod, "UnityEngine", "Screen", "SetResolution")));
        setter.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));

        MethodDefinition handler = NewMethod(owner, "SyntheticHandler");
        handler.Parameters.Add(new ParameterDefinition(mod.TypeSystem.Int32));
        handler.Body.Instructions.Add(Instruction.Create(OpCodes.Call, setter));
        handler.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));

        MethodDefinition selector = NewMethod(owner, "SyntheticOptionsOnly");
        selector.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(mod, "UnityEngine.UI", "Dropdown", "AddOptions")));
        selector.Body.Instructions.Add(Instruction.Create(OpCodes.Ldftn, handler));
        selector.Body.Instructions.Add(Instruction.Create(OpCodes.Pop));
        selector.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));

        Evidence positive = Analyze(owner);
        Assert(positive.delegate_instruction_sites == 1 &&
               positive.resolved_delegate_sites == 1 &&
               positive.delegate_targets_with_int_parameter == 1);
        Assert(positive.delegate_targets_reach_apply == 1 &&
               positive.delegate_targets_reach_screen_setresolution == 1 &&
               positive.option_methods_reach_screen_setresolution == 0);
        Assert(!positive.runtime_dropdown_callback_binding_proven &&
               !positive.android_render_scale_binding_proven);

        TypeDefinition isolated = NewType(mod, "IsolatedOptionOnly");
        MethodDefinition only = NewMethod(isolated, "Only");
        only.Body.Instructions.Add(Instruction.Create(OpCodes.Call,
            External(mod, "UnityEngine.UI", "Dropdown", "AddOptions")));
        only.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        Evidence noHandler = Analyze(isolated);
        Assert(noHandler.methods_populating_options == 1 &&
               noHandler.delegate_instruction_sites == 0 &&
               noHandler.option_methods_reach_screen_setresolution == 0);

        // Cyclic local calls must terminate rather than claiming a setter path.
        TypeDefinition cyclic = NewType(mod, "Cycle");
        MethodDefinition first = NewMethod(cyclic, "First");
        MethodDefinition second = NewMethod(cyclic, "Second");
        first.Body.Instructions.Add(Instruction.Create(OpCodes.Call, second));
        first.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        second.Body.Instructions.Add(Instruction.Create(OpCodes.Call, first));
        second.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
        Assert(!CanReach(first, new HashSet<MethodDefinition>{setter},
            new Dictionary<MethodDefinition, HashSet<MethodDefinition>> {
                [first] = new HashSet<MethodDefinition>{second},
                [second] = new HashSet<MethodDefinition>{first}}));

        Console.WriteLine("T5_ORIGINAL_RESOLUTION_DELEGATES_SYNTHETIC 5/5 source_only=true");
        return 0;
    }

    private static int RunOriginal(string fileName, string outputName)
    {
        var file = new FileInfo(fileName);
        if (!file.Exists || file.Length != OriginalBytes)
            throw new InvalidDataException("input_size");
        using (var input = file.OpenRead())
        {
            string sha = Convert.ToHexString(SHA256.HashData(input)).ToLowerInvariant();
            if (sha != OriginalSha) throw new InvalidDataException("input_sha");
        }
        using var assembly = AssemblyDefinition.ReadAssembly(file.FullName,
            new ReaderParameters { ReadSymbols = false });
        var matches = assembly.MainModule.Types
            .Where(t => t.Name == "GraphicsSettingsBox").ToArray();
        if (matches.Length != 1) throw new InvalidDataException("type_cardinality");
        Evidence result = Analyze(matches[0]);
        // Prior independently authenticated CI 42204488410 found two source
        // same-type ldftn/ldvirtftn sites. Never silently lose or invent one.
        if (result.delegate_instruction_sites != 2 ||
            result.unresolved_delegate_sites != 0 ||
            result.resolved_delegate_sites != 2 ||
            result.methods_populating_options < 1 ||
            result.unique_delegate_target_methods < 1)
            throw new InvalidDataException("original_delegate_identity_inconclusive");
        var safeReport = new
        {
            schema_version = 1,
            original_assembly_sha_verified = true,
            original_assembly_bytes = OriginalBytes,
            original_compiled_il = true,
            unique_original_graphics_settings_type = true,
            graph_method_limit = 256,
            evidence = result,
            no_original_methods_tokens_il_or_sources_emitted = true,
            event_registration_and_callback_dataflow_proven = false,
            android_render_scale_persistence_proven = false,
            actual_android_device_tested = false
        };
        string destination = Path.GetFullPath(outputName);
        if (File.Exists(destination) || Directory.Exists(destination))
            throw new InvalidDataException("output_exists");
        Directory.CreateDirectory(Path.GetDirectoryName(destination)!);
        string json = JsonSerializer.Serialize(safeReport);
        File.WriteAllText(destination, json);
        Console.WriteLine("T5_ORIGINAL_RESOLUTION_DELEGATE_GRAPH " + json);
        return 0;
    }

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length == 1 && args[0] == "--self-test") return SelfTest();
            if (args.Length == 4 && args[0] == "--assembly" && args[2] == "--output")
                return RunOriginal(args[1], args[3]);
        }
        catch (Exception)
        {
            Console.WriteLine("T5_ORIGINAL_RESOLUTION_DELEGATES status=INCONCLUSIVE original_content_logged=false");
            return 2;
        }
        Console.WriteLine("T5_ORIGINAL_RESOLUTION_DELEGATES status=INVALID_ARGUMENTS");
        return 2;
    }
}
