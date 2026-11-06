// T5: inspect authenticated Raft IL without exposing original identifiers, IL or game bytes.
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long Size = 3211776;
    private const string Sha = "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";

    private sealed record Counts(int method_bodies, int call_sites,
        int screen_set_resolution, int screen_resolutions_read,
        int screen_current_resolution_read, int screen_dimensions_read,
        int event_add_listener, int option_population, int playerprefs_reads,
        int playerprefs_writes, int local_apply_resolution_calls,
        int dynamic_resolution_references, int scalable_resize_buffers,
        int same_type_delegate_targets);

    private static Counts Inspect(TypeDefinition t)
    {
        int bodies = 0, calls = 0, set = 0, resolutions = 0, current = 0,
            dimensions = 0, listeners = 0, options = 0, getPrefs = 0,
            setPrefs = 0, apply = 0, dynamic = 0, resize = 0, delegates = 0;
        foreach (var method in t.Methods)
        {
            if (!method.HasBody) continue;
            bodies++;
            foreach (var ins in method.Body.Instructions)
            {
                if (ins.Operand is FieldReference f && f.DeclaringType.Name == "DynamicResolution")
                    dynamic++;
                if (ins.Operand is not MethodReference m) continue;
                if (m.DeclaringType.Name == "DynamicResolution") dynamic++;
                if (ins.OpCode.Code == Code.Ldftn || ins.OpCode.Code == Code.Ldvirtftn)
                {
                    if (m.DeclaringType.FullName == t.FullName) delegates++;
                    continue;
                }
                if (ins.OpCode.Code != Code.Call &&
                    ins.OpCode.Code != Code.Callvirt &&
                    ins.OpCode.Code != Code.Newobj) continue;
                calls++;
                string owner = m.DeclaringType.FullName;
                string name = m.Name;
                if (owner == "UnityEngine.Screen")
                {
                    if (name == "SetResolution") set++;
                    if (name == "get_resolutions") resolutions++;
                    if (name == "get_currentResolution") current++;
                    if (name == "get_width" || name == "get_height") dimensions++;
                }
                if (name == "AddListener") listeners++;
                if (name == "AddOptions" || name == "ClearOptions" ||
                    name == "SetValueWithoutNotify") options++;
                if (owner == "UnityEngine.PlayerPrefs")
                {
                    if (name.StartsWith("Get", StringComparison.Ordinal)) getPrefs++;
                    if (name.StartsWith("Set", StringComparison.Ordinal) ||
                        name == "Save") setPrefs++;
                }
                if (owner == t.FullName && name == "ApplyCurrentResolutionAndFullscreenMode")
                    apply++;
                if (owner == "UnityEngine.ScalableBufferManager" && name == "ResizeBuffers")
                    resize++;
            }
        }
        return new Counts(bodies, calls, set, resolutions, current,
            dimensions, listeners, options, getPrefs, setPrefs, apply,
            dynamic, resize, delegates);
    }

    private static TypeDefinition Type(ModuleDefinition mod, string name)
    {
        var t = new TypeDefinition("", name, Mono.Cecil.TypeAttributes.Public,
            mod.TypeSystem.Object);
        mod.Types.Add(t);
        return t;
    }

    private static MethodReference Target(ModuleDefinition mod, string ns, string owner, string name)
    {
        return new MethodReference(name, mod.TypeSystem.Void,
            new TypeReference(ns, owner, mod, mod.TypeSystem.CoreLibrary));
    }

    private static void Fixture(TypeDefinition t, params MethodReference[] targets)
    {
        var m = new MethodDefinition("Synthetic", Mono.Cecil.MethodAttributes.Public,
            t.Module.TypeSystem.Void);
        t.Methods.Add(m);
        foreach (var target in targets)
            m.Body.Instructions.Add(Instruction.Create(OpCodes.Call, target));
        m.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
    }

    private static int SelfTest()
    {
        using var mod = ModuleDefinition.CreateModule("T5SyntheticOnly", ModuleKind.Dll);
        var box = Type(mod, "GraphicsSettingsBox");
        var dyn = Type(mod, "DynamicResolution");
        Fixture(box, Target(mod, "UnityEngine", "Screen", "SetResolution"),
            Target(mod, "UnityEngine", "Screen", "get_resolutions"),
            Target(mod, "UnityEngine.Events", "UnityEvent", "AddListener"),
            Target(mod, "UnityEngine", "PlayerPrefs", "SetInt"));
        Fixture(dyn, Target(mod, "UnityEngine", "ScalableBufferManager", "ResizeBuffers"));
        var a = Inspect(box);
        var d = Inspect(dyn);
        if (a.screen_set_resolution != 1 || a.screen_resolutions_read != 1)
            throw new InvalidDataException("synthetic");
        if (a.event_add_listener != 1 || a.playerprefs_writes != 1)
            throw new InvalidDataException("synthetic");
        if (a.scalable_resize_buffers != 0 || d.scalable_resize_buffers != 1)
            throw new InvalidDataException("synthetic");
        var displayOnly = Type(mod, "DisplayOnly");
        Fixture(displayOnly, Target(mod, "UnityEngine", "Screen", "get_resolutions"));
        if (Inspect(displayOnly).event_add_listener != 0)
            throw new InvalidDataException("synthetic");
        Console.WriteLine("T5_RESOLUTION_IL_SELFTEST 4/4 synthetic_only=true");
        return 0;
    }

    private static int Scan(string input, string output)
    {
        var file = new FileInfo(input);
        if (!file.Exists || file.Length != Size)
            throw new InvalidDataException("size");
        using (var stream = file.OpenRead())
        {
            string sha = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
            if (!string.Equals(sha, Sha, StringComparison.Ordinal))
                throw new InvalidDataException("sha");
        }
        using var asm = AssemblyDefinition.ReadAssembly(file.FullName,
            new ReaderParameters { ReadSymbols = false });
        var boxes = asm.MainModule.Types.Where(t => t.Name == "GraphicsSettingsBox").ToList();
        var dyns = asm.MainModule.Types.Where(t => t.Name == "DynamicResolution").ToList();
        if (boxes.Count != 1 || dyns.Count != 1)
            throw new InvalidDataException("types");
        var settings = Inspect(boxes[0]);
        var dynamic = Inspect(dyns[0]);
        if (settings.method_bodies == 0 || dynamic.method_bodies == 0)
            throw new InvalidDataException("empty");
        var safe = new {
            schema_version = 1,
            original_assembly_sha_verified = true,
            original_assembly_bytes = Size,
            original_classes_unique = true,
            settings,
            dynamic,
            compiled_il_inspected = true,
            option_to_callback_dataflow_proven = false,
            persisted_android_render_scale_proven = false,
            equal_axis_render_scale_proven = false,
            phone_tested = false,
            original_game_modified = false
        };
        string path = Path.GetFullPath(output);
        if (File.Exists(path) || Directory.Exists(path))
            throw new InvalidDataException("destination");
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        string json = JsonSerializer.Serialize(safe);
        File.WriteAllText(path, json);
        Console.WriteLine("T5_ORIGINAL_RESOLUTION_IL " + json);
        return 0;
    }

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length == 1 && args[0] == "--self-test")
                return SelfTest();
            if (args.Length == 4 && args[0] == "--assembly" && args[2] == "--output")
                return Scan(args[1], args[3]);
        }
        catch (Exception)
        {
            Console.WriteLine("T5_RESOLUTION_IL status=INCONCLUSIVE private_data_logged=false");
            return 2;
        }
        Console.WriteLine("T5_RESOLUTION_IL status=INVALID_ARGUMENTS");
        return 2;
    }
}
