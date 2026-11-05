// T2 WATER-001: synthetic only. Never load original game data here.
using System.Text.Json;
using Mono.Cecil;

internal static class Program
{
    private static readonly Version V = new(1, 0, 0, 0);
    private static readonly Version EngineV = new(1, 0, 0, 0);

    private static AssemblyNameReference AssemblyRef(string name) =>
        new(name, V);

    private static TypeReference RenderTexture(ModuleDefinition module,
        string engineName = "UnityEngine.CoreModule") =>
        new("UnityEngine", "RenderTexture", module,
            new AssemblyNameReference(engineName, EngineV));

    private static AssemblyDefinition CreateAssembly(string name)
    {
        return AssemblyDefinition.CreateAssembly(
            new AssemblyNameDefinition(name, V),
            name + ".dll", ModuleKind.Dll);
    }

    private static MethodDefinition MakeFactory(AssemblyDefinition assembly)
    {
        var module = assembly.MainModule;
        var factory = new TypeDefinition("Synthetic", "FoamFactory",
            TypeAttributes.Public | TypeAttributes.Class,
            module.TypeSystem.Object);
        module.Types.Add(factory);
        var method = new MethodDefinition("Make",
            MethodAttributes.Public | MethodAttributes.Static,
            RenderTexture(module));
        factory.Methods.Add(method);
        var il = method.Body.GetILProcessor();
        il.Append(il.Create(Mono.Cecil.Cil.OpCodes.Ldnull));
        il.Append(il.Create(Mono.Cecil.Cil.OpCodes.Ret));
        return method;
    }

    private static MethodReference CallReference(ModuleDefinition caller,
        string declaringAssembly, string returnAssembly = "UnityEngine.CoreModule")
    {
        var type = new TypeReference("Synthetic", "FoamFactory", caller,
            AssemblyRef(declaringAssembly));
        return new MethodReference("Make", RenderTexture(caller, returnAssembly),
            type) { HasThis = false };
    }

    private static bool LooseSignature(MethodReference call, MethodDefinition def)
    {
        return call.FullName == def.FullName
            && call.DeclaringType.FullName == def.DeclaringType.FullName
            && call.HasThis == def.HasThis
            && call.Parameters.Count == def.Parameters.Count
            && call.Parameters.Zip(def.Parameters, (a, b) =>
                a.ParameterType.FullName == b.ParameterType.FullName).All(x => x);
    }

    // Require a known assembly identity for both the declaring type and the
    // UnityEngine.RenderTexture return type. Unknown scope never passes.
    // This checks metadata identity, not whether the method executes.
    private static string? AssemblyIdentity(IMetadataScope? scope) =>
        scope switch
        {
            AssemblyNameReference assembly => assembly.FullName,
            ModuleDefinition module => module.Assembly?.Name.FullName,
            _ => null
        };

    private static bool StrictSignatureAndScope(MethodReference call,
        MethodDefinition def)
    {
        if (!LooseSignature(call, def))
            return false;
        string? callOwner = AssemblyIdentity(call.DeclaringType.Scope);
        string? defOwner = def.Module.Assembly?.Name.FullName;
        string? callReturn = AssemblyIdentity(call.ReturnType.Scope);
        string? defReturn = AssemblyIdentity(def.ReturnType.Scope);
        return callOwner is not null && defOwner is not null
            && callReturn is not null && defReturn is not null
            && StringComparer.Ordinal.Equals(callOwner, defOwner)
            && StringComparer.Ordinal.Equals(callReturn, defReturn);
    }

    private static void Require(bool condition, string message)
    {
        if (!condition)
            throw new InvalidDataException("Synthetic method assembly scope check: " + message);
    }

    private static int Main()
    {
        using var source = CreateAssembly("SyntheticOriginalAssembly");
        using var another = CreateAssembly("SyntheticOtherAssembly");
        var definition = MakeFactory(source);
        var otherDefinition = MakeFactory(another);
        var original = CallReference(source.MainModule, source.Name.Name);
        var external = CallReference(source.MainModule, another.Name.Name);
        var returnSpoof = CallReference(source.MainModule, source.Name.Name,
            "SyntheticFakeEngine");
        var sameModule = new MethodReference("Make",
            RenderTexture(source.MainModule),
            new TypeReference("Synthetic", "FoamFactory",
                source.MainModule, source.MainModule))
        {
            HasThis = false
        };
        var foreignModule = new MethodReference("Make",
            RenderTexture(source.MainModule),
            new TypeReference("Synthetic", "FoamFactory",
                source.MainModule, another.MainModule))
        {
            HasThis = false
        };
        var unspecifiedModule = new MethodReference("Make",
            RenderTexture(source.MainModule),
            new TypeReference("Synthetic", "FoamFactory",
                source.MainModule, new ModuleReference("UnknownModule.dll")))
        {
            HasThis = false
        };
        var overload = CallReference(source.MainModule, source.Name.Name);
        overload.Parameters.Add(new ParameterDefinition(source.MainModule.TypeSystem.Int32));

        Require(LooseSignature(original, definition), "expected identical public signature");
        Require(StrictSignatureAndScope(original, definition), "same assembly must match");
        Require(LooseSignature(external, definition), "external decoy must share FullName");
        Require(!StrictSignatureAndScope(external, definition),
            "foreign assembly with same FullName must be rejected");
        Require(!StrictSignatureAndScope(external, otherDefinition) == false,
            "foreign reference should match its actual other assembly definition");
        Require(LooseSignature(returnSpoof, definition),
            "spoofed RT return assembly must share public FullName");
        Require(!StrictSignatureAndScope(returnSpoof, definition),
            "spoofed Unity return assembly must be rejected");
        Require(StrictSignatureAndScope(sameModule, definition),
            "direct same module scope must match");
        Require(!StrictSignatureAndScope(foreignModule, definition),
            "other ModuleDefinition cannot alias current assembly");
        Require(!StrictSignatureAndScope(unspecifiedModule, definition),
            "unresolved ModuleReference must fail closed");
        Require(!LooseSignature(overload, definition),
            "wrong method arity must be rejected");
        Require(!StrictSignatureAndScope(overload, definition),
            "wrong formal signature cannot pass strict identity");

        Console.WriteLine("T2_FOAM_CECIL_ASSEMBLY_SCOPE_SYNTHETIC_SAFE " +
            JsonSerializer.Serialize(new
            {
                synthetic_only = true,
                cecil_pinned_version = "0.11.5",
                identical_fullname_cross_assembly_collision_exercised = true,
                exact_original_style_same_assembly_accepted = true,
                same_fullname_foreign_assembly_rejected = true,
                correct_foreign_definition_accepted = true,
                fake_Unity_RenderTexture_return_assembly_rejected = true,
                same_module_scope_accepted = true,
                foreign_module_scope_rejected = true,
                unknown_module_reference_rejected = true,
                wrong_formal_signature_rejected = true,
                original_game_source_or_private_data_loaded = false,
                actual_Foam_return_target_assembly_resolved = false,
                android_runtime_or_pixels_verified = false
            }));
        return 0;
    }
}
