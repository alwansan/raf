// T4 LOCAL-005: bounded source-authentic RGD pre-call IL structural classifier.
// This is a read-only metadata probe, not an original game code invocation.
// Never echo private IL, member names, original CLR types, source, stack or paths.
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long OriginalLength = 3211776;
    private const string OriginalSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";

    private static TypeDefinition UniqueType(ModuleDefinition module, string name)
    {
        var matches = module.Types.Where(t => t.FullName == name).ToArray();
        if (matches.Length != 1)
            throw new InvalidDataException("original_source_shape_drift");
        return matches[0];
    }

    private static MethodDefinition UniqueNoArgMethod(TypeDefinition type, string name)
    {
        var matches = type.Methods.Where(m => m.HasBody && m.Name == name &&
            !m.IsStatic && m.Parameters.Count == 0 &&
            m.ReturnType.FullName == "System.Void").ToArray();
        if (matches.Length != 1)
            throw new InvalidDataException("original_method_shape_drift");
        return matches[0];
    }

    private static MethodDefinition UniqueSave(TypeDefinition type)
    {
        var matches = type.Methods.Where(m => m.HasBody && m.Name == "Save" &&
            !m.IsStatic && !m.IsPublic && !m.HasGenericParameters &&
            m.Parameters.Count == 2 &&
            m.Parameters[0].ParameterType.FullName == "System.String" &&
            m.Parameters[1].ParameterType.Name == "RGD" &&
            m.ReturnType.FullName == "System.Void").ToArray();
        if (matches.Length != 1)
            throw new InvalidDataException("original_RGD_save_shape_drift");
        return matches[0];
    }

    private static Instruction FindOriginalCall(
        MethodDefinition caller, MethodDefinition save)
    {
        var targets = caller.Body.Instructions.Where(i =>
            (i.OpCode.Code == Code.Call || i.OpCode.Code == Code.Callvirt) &&
            i.Operand is MethodReference m &&
            m.DeclaringType.FullName == save.DeclaringType.FullName &&
            m.Name == save.Name &&
            m.HasThis && m.Parameters.Count == 2 &&
            m.ReturnType.FullName == save.ReturnType.FullName &&
            m.Parameters[0].ParameterType.FullName == save.Parameters[0].ParameterType.FullName &&
            m.Parameters[1].ParameterType.FullName == save.Parameters[1].ParameterType.FullName)
            .ToArray();
        if (targets.Length != 1) throw new InvalidDataException("ambiguous_original_save_edge");
        return targets[0];
    }

    private static string TypeRelation(
        ModuleDefinition module, TypeReference candidate, string originalRgdType)
    {
        if (candidate.FullName == originalRgdType) return "EXACT_RGD";
        var possible = module.Types.FirstOrDefault(t => t.FullName == candidate.FullName);
        if (possible is null) return "OTHER_OR_UNRESOLVED";
        for (int n = 0; n < 8; ++n)
        {
            TypeReference? parent = possible.BaseType;
            if (parent is null) break;
            if (parent.FullName == originalRgdType) return "DERIVED_RGD";
            possible = module.Types.FirstOrDefault(t => t.FullName == parent.FullName);
            if (possible is null) break;
        }
        return "OTHER_OR_UNRESOLVED";
    }

    private static string WithRelation(string prefix, TypeReference type,
        ModuleDefinition module, string rgd) =>
        prefix + "_" + TypeRelation(module, type, rgd);

    private static string ClassifyPrecall(
        MethodDefinition method, MethodDefinition save, ModuleDefinition module,
        string rgd)
    {
        var call = FindOriginalCall(method, save);
        return ClassifyPredecessorAt(method, module, rgd,
            method.Body.Instructions.IndexOf(call), save.DeclaringType.FullName);
    }

    // Lexical predecessor only: not a control-flow or SSA proof.
    private static string ClassifyPredecessorAt(
        MethodDefinition method, ModuleDefinition module, string rgd,
        int at, string ownerType)
    {
        int previous = at - 1;
        while (previous >= 0 && method.Body.Instructions[previous].OpCode.Code == Code.Nop)
            previous--;
        if (previous < 0) return "UNKNOWN_PRECALL";
        var i = method.Body.Instructions[previous];
        Code opcode = i.OpCode.Code;
        if (opcode == Code.Ldnull) return "NULL_LITERAL";
        if (opcode is Code.Ldfld or Code.Ldsfld && i.Operand is FieldReference f)
            return WithRelation("FIELD", f.FieldType, module, rgd);
        if (opcode is Code.Ldflda or Code.Ldsflda && i.Operand is FieldReference fAddress)
            return WithRelation("FIELD_ADDRESS", fAddress.FieldType, module, rgd);
        if (opcode == Code.Newobj && i.Operand is MethodReference ctor)
            return WithRelation("CONSTRUCTOR", ctor.DeclaringType, module, rgd);
        if (opcode is Code.Castclass or Code.Isinst && i.Operand is TypeReference t)
            return WithRelation("CAST", t, module, rgd);
        if (opcode is Code.Box or Code.Unbox_Any && i.Operand is TypeReference boxed)
            return WithRelation("BOX", boxed, module, rgd);
        if (opcode is Code.Call or Code.Callvirt && i.Operand is MethodReference called)
        {
            var result = called.ReturnType;
            if (i.Operand is GenericInstanceMethod g &&
                g.Name == "Load" && g.GenericArguments.Count == 1 &&
                g.DeclaringType.FullName == ownerType)
                result = g.GenericArguments[0];
            return WithRelation("CALL_RETURN", result, module, rgd);
        }

        int index = opcode switch
        {
            Code.Ldloc_0 => 0,
            Code.Ldloc_1 => 1,
            Code.Ldloc_2 => 2,
            Code.Ldloc_3 => 3,
            Code.Ldloc or Code.Ldloc_S when i.Operand is VariableDefinition =>
                ((VariableDefinition)i.Operand).Index,
            _ => -1
        };
        if (index >= 0 && index < method.Body.Variables.Count)
            return WithRelation("LOCAL", method.Body.Variables[index].VariableType, module, rgd);
        if (opcode == Code.Dup) return "DUP_PREVIOUS_STACK";
        if (opcode is Code.Br or Code.Br_S or Code.Leave or Code.Leave_S)
            return "BRANCH_PREVIOUS_STACK";
        if (opcode is Code.Ldarg_0 or Code.Ldarg_1 or Code.Ldarg_2 or Code.Ldarg_3 or
            Code.Ldarg or Code.Ldarg_S)
            return "ARGUMENT_PUSH";
        if (opcode == Code.Ldelem_Ref) return "ARRAY_REF_LOAD";
        if (opcode == Code.Ldstr) return "STRING_LITERAL";
        return "OTHER_PRECALL";
    }


    // Interpret only local-slot opcodes; no branch-path or stack inference.
    private static int LocalSlot(Instruction i, bool store)
    {
        if (store)
            return i.OpCode.Code switch
            {
                Code.Stloc_0 => 0, Code.Stloc_1 => 1,
                Code.Stloc_2 => 2, Code.Stloc_3 => 3,
                Code.Stloc or Code.Stloc_S when i.Operand is VariableDefinition v =>
                    v.Index,
                _ => -1
            };
        return i.OpCode.Code switch
        {
            Code.Ldloc_0 => 0, Code.Ldloc_1 => 1,
            Code.Ldloc_2 => 2, Code.Ldloc_3 => 3,
            Code.Ldloc or Code.Ldloc_S when i.Operand is VariableDefinition v =>
                v.Index,
            _ => -1
        };
    }

    private static (int Stores, string NearestSource) SaveWorldLocalStores(
        MethodDefinition world, MethodDefinition save, ModuleDefinition module,
        string originalRgd)
    {
        var il = world.Body.Instructions;
        int at = il.IndexOf(FindOriginalCall(world, save));
        int prior = at - 1;
        while (prior >= 0 && il[prior].OpCode.Code == Code.Nop) prior--;
        if (prior < 0) return (0, "NOT_A_LOCAL_LOAD");
        int localSlot = LocalSlot(il[prior], store: false);
        if (localSlot < 0 || localSlot >= world.Body.Variables.Count)
            return (0, "NOT_A_LOCAL_LOAD");
        if (TypeRelation(module, world.Body.Variables[localSlot].VariableType,
                originalRgd) is not ("EXACT_RGD" or "DERIVED_RGD"))
            return (0, "NOT_A_LOCAL_LOAD");
        var stores = Enumerable.Range(0, at)
            .Where(i => LocalSlot(il[i], store: true) == localSlot).ToArray();
        if (stores.Length == 0) return (0, "NO_LEXICAL_STORE");
        return (stores.Length, ClassifyPredecessorAt(world, module, originalRgd,
            stores[^1], save.DeclaringType.FullName));
    }

    private static IEnumerable<TypeDefinition> NestedTypes(TypeDefinition type)
    {
        yield return type;
        foreach (var nested in type.NestedTypes)
            foreach (var found in NestedTypes(nested))
                yield return found;
    }

    private static (string OwnerScope, int DirectStores) SaveUserFieldStores(
        MethodDefinition user, MethodDefinition save, ModuleDefinition module)
    {
        var il = user.Body.Instructions;
        int index = il.IndexOf(FindOriginalCall(user, save)) - 1;
        while (index >= 0 && il[index].OpCode.Code == Code.Nop) index--;
        if (index < 0 ||
            (il[index].OpCode.Code != Code.Ldfld &&
             il[index].OpCode.Code != Code.Ldsfld) ||
            il[index].Operand is not FieldReference field)
            return ("NOT_A_FIELD_LOAD", 0);

        string owner = field.DeclaringType.FullName;
        var types = module.Types.SelectMany(NestedTypes).ToArray();
        string ownerScope = owner == save.DeclaringType.FullName ?
            "SAVEANDLOAD_CLASS" :
            types.Any(t => t.FullName == owner) ?
                "OTHER_ORIGINAL_CLASS" : "DECLARER_UNRESOLVED";
        int stores = types.SelectMany(t => t.Methods)
            .Where(m => m.HasBody)
            .SelectMany(m => m.Body.Instructions)
            .Count(i => (i.OpCode.Code == Code.Stfld ||
                         i.OpCode.Code == Code.Stsfld) &&
                i.Operand is FieldReference f &&
                f.Name == field.Name &&
                f.DeclaringType.FullName == owner &&
                f.FieldType.FullName == field.FieldType.FullName);
        return (ownerScope, stores);
    }

    private static int Main(string[] args)
    {
        if (args.Length != 4 || args[0] != "--assembly" || args[2] != "--output")
        {
            Console.WriteLine("T4_RGD_PRECALL status=INVALID_ARGUMENTS data_published=false");
            return 2;
        }
        try
        {
            var original = new FileInfo(Path.GetFullPath(args[1]));
            if (!original.Exists || original.Length != OriginalLength ||
                original.LinkTarget is not null)
                throw new InvalidDataException("original_source_not_authentic");
            using (var source = original.OpenRead())
            {
                if (Convert.ToHexString(SHA256.HashData(source))
                    .ToLowerInvariant() != OriginalSha)
                    throw new InvalidDataException("original_source_not_authentic");
            }
            using var assembly = AssemblyDefinition.ReadAssembly(original.FullName,
                new ReaderParameters { ReadSymbols = false });
            var owner = UniqueType(assembly.MainModule, "SaveAndLoad");
            var world = UniqueNoArgMethod(owner, "SaveWorld");
            var user = UniqueNoArgMethod(owner, "SaveUser");
            var save = UniqueSave(owner);
            string rgd = save.Parameters[1].ParameterType.FullName;
            var actualRgd = UniqueType(assembly.MainModule, rgd);
            if (!actualRgd.IsClass)
                throw new InvalidDataException("original_RGD_not_class");

            var worldLocalStores = SaveWorldLocalStores(world, save,
                assembly.MainModule, rgd);
            var userFieldStores = SaveUserFieldStores(user, save,
                assembly.MainModule);
            // No names/opcodes/surrounding IL, private path or source leave this tool.
            var report = new
            {
                schema_version = 1,
                source_kind = "PINNED_ORIGINAL_READONLY_IL",
                original_assembly_sha_verified = true,
                original_private_RGD_class_verified = true,
                saveworld_exact_original_private_save_edge = true,
                saveuser_exact_original_private_save_edge = true,
                world_precall_type_class = ClassifyPrecall(world, save,
                    assembly.MainModule, rgd),
                user_precall_type_class = ClassifyPrecall(user, save,
                    assembly.MainModule, rgd),
                world_local_lexical_store_site_count = worldLocalStores.Stores,
                world_nearest_lexical_store_precall_class =
                    worldLocalStores.NearestSource,
                user_field_declaring_scope = userFieldStores.OwnerScope,
                user_field_direct_store_site_count = userFieldStores.DirectStores,
                lexical_local_store_reached_save_at_runtime = false,
                user_field_initialized_at_runtime = false,
                original_save_executed = false,
                original_RGD_created_or_read = false,
                original_game_source_or_payload_published = false,
                Android_Unity_IL2CPP_or_device_executed = false,
                dynamic_argument_identity_proven = false
            };
            var target = Path.GetFullPath(args[3]);
            if (File.Exists(target) || Directory.Exists(target) ||
                new FileInfo(target).LinkTarget is not null)
                throw new InvalidDataException("unsafe_output");
            Directory.CreateDirectory(Path.GetDirectoryName(target)!);
            File.WriteAllText(target, JsonSerializer.Serialize(report));
            Console.WriteLine("T4_RGD_PRECALL original_metadata_verified=true read_only=true");
            return 0;
        }
        catch (Exception)
        {
            Console.WriteLine("T4_RGD_PRECALL status=INCONCLUSIVE original_details_published=false");
            return 2;
        }
    }
}
