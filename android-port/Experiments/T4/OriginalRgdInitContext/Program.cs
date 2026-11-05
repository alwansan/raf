// T4 LOCAL-005. Read-only, SHA-authenticated ORIGINAL compiled RGD data origins.
// Zero original method invocation. Never print game IL/source/type/member names,
// argument strings, file paths, game save data, method signatures or stacktraces.
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long OriginalLength = 3211776;
    private const string OriginalSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";

    private static IEnumerable<TypeDefinition> Types(TypeDefinition t)
    {
        yield return t;
        foreach (var n in t.NestedTypes)
            foreach (var a in Types(n))
                yield return a;
    }
    private static TypeDefinition[] AllTypes(ModuleDefinition m) =>
        m.Types.SelectMany(Types).ToArray();

    private static bool IsCall(Instruction i) =>
        i.OpCode.Code is Code.Call or Code.Callvirt;

    private static MethodDefinition UniqueVoidNoArg(TypeDefinition t, string name)
    {
        var m = t.Methods.Where(x => x.HasBody && !x.IsStatic &&
            x.Name == name && x.Parameters.Count == 0 &&
            x.ReturnType.FullName == "System.Void").ToArray();
        if (m.Length != 1) throw new InvalidDataException("original_method_shape_drift");
        return m[0];
    }
    private static MethodDefinition UniquePrivateSave(TypeDefinition t)
    {
        var m = t.Methods.Where(x => x.HasBody && x.Name == "Save" &&
            !x.IsStatic && !x.IsPublic && !x.HasGenericParameters &&
            x.Parameters.Count == 2 && x.Parameters[0].ParameterType.FullName ==
            "System.String" && x.Parameters[1].ParameterType.Name == "RGD" &&
            x.ReturnType.FullName == "System.Void").ToArray();
        if (m.Length != 1) throw new InvalidDataException("original_save_shape_drift");
        return m[0];
    }
    private static Instruction FindSaveCall(MethodDefinition m, MethodDefinition save)
    {
        var targets = m.Body.Instructions.Where(i => IsCall(i) &&
            i.Operand is MethodReference called &&
            called.Name == save.Name &&
            called.DeclaringType.FullName == save.DeclaringType.FullName &&
            called.Parameters.Count == 2 && called.HasThis &&
            called.ReturnType.FullName == "System.Void" &&
            called.Parameters[0].ParameterType.FullName == "System.String" &&
            called.Parameters[1].ParameterType.FullName ==
                save.Parameters[1].ParameterType.FullName).ToArray();
        if (targets.Length != 1) throw new InvalidDataException("original_save_call_ambiguous");
        return targets[0];
    }

    private static int LocalSlot(Instruction ins, bool store)
    {
        if (store)
            return ins.OpCode.Code switch
            {
                Code.Stloc_0 => 0, Code.Stloc_1 => 1,
                Code.Stloc_2 => 2, Code.Stloc_3 => 3,
                Code.Stloc or Code.Stloc_S when ins.Operand is VariableDefinition v =>
                    v.Index,
                _ => -1
            };
        return ins.OpCode.Code switch
        {
            Code.Ldloc_0 => 0, Code.Ldloc_1 => 1,
            Code.Ldloc_2 => 2, Code.Ldloc_3 => 3,
            Code.Ldloc or Code.Ldloc_S when ins.Operand is VariableDefinition v =>
                v.Index,
            _ => -1
        };
    }

    private static int PriorNonNop(MethodDefinition m, int at)
    {
        int k = at - 1;
        while (k >= 0 && m.Body.Instructions[k].OpCode.Code == Code.Nop)
            k--;
        return k;
    }

    private static bool DerivesFrom(TypeReference t, string rgd, TypeDefinition[] types)
    {
        if (t.FullName == rgd) return true;
        var def = types.FirstOrDefault(x => x.FullName == t.FullName);
        for (int n = 0; n < 8 && def is not null && def.BaseType is not null; n++)
        {
            if (def.BaseType.FullName == rgd) return true;
            def = types.FirstOrDefault(x => x.FullName == def.BaseType.FullName);
        }
        return false;
    }

    // Strict lexical adjacency and type shape. Branch-path equivalence remains UNKNOWN.
    private static (string Scope, string Arity, string Kind, bool CompiledBody)
        WorldProducer(MethodDefinition world, MethodDefinition save,
                      TypeDefinition[] types, string rgd)
    {
        var instructions = world.Body.Instructions;
        int saveAt = instructions.IndexOf(FindSaveCall(world, save));
        int localPush = PriorNonNop(world, saveAt);
        if (localPush < 0) throw new InvalidDataException("world_save_arg_missing");
        int local = LocalSlot(instructions[localPush], store: false);
        if (local < 0 || local >= world.Body.Variables.Count ||
            !DerivesFrom(world.Body.Variables[local].VariableType, rgd, types))
            throw new InvalidDataException("world_arg_not_derived_local");
        var stores = Enumerable.Range(0, saveAt).Where(i =>
            LocalSlot(instructions[i], store: true) == local).ToArray();
        if (stores.Length != 1)
            throw new InvalidDataException("world_local_assignment_not_unique");
        int prior = PriorNonNop(world, stores[0]);
        if (prior < 0 || !IsCall(instructions[prior]) ||
            instructions[prior].Operand is not MethodReference producer ||
            !DerivesFrom(producer.ReturnType, rgd, types))
            throw new InvalidDataException("world_local_producer_not_derived_call");

        string scope = producer.DeclaringType.FullName == save.DeclaringType.FullName
            ? "SAVEANDLOAD"
            : types.Any(t => t.FullName == producer.DeclaringType.FullName)
                ? "OTHER_ORIGINAL_CLASS" : "EXTERNAL_OR_UNRESOLVED";
        string arity = producer.Parameters.Count == 0 ? "ZERO" :
            producer.Parameters.Count == 1 ? "ONE" : "MULTIPLE";
        string kind = producer.HasThis ? "INSTANCE_CALL" : "STATIC_CALL";
        bool body = false;
        if (scope != "EXTERNAL_OR_UNRESOLVED")
        {
            try
            {
                var def = producer.Resolve();
                body = def is not null && def.HasBody &&
                    def.Module == save.Module;
            }
            catch (Exception) { body = false; }
        }
        return (scope, arity, kind, body);
    }


    // Source-only lexical return-site categories, NOT branch-aware stack value tracing.
    private static object WorldProducerReturnSites(
        MethodDefinition world, MethodDefinition save,
        TypeDefinition[] types, string rgd)
    {
        var worldIl = world.Body.Instructions;
        int saveAt = worldIl.IndexOf(FindSaveCall(world, save));
        int localLoad = PriorNonNop(world, saveAt);
        if (localLoad < 0) throw new InvalidDataException("world_local_missing");
        int slot = LocalSlot(worldIl[localLoad], store: false);
        if (slot < 0 || slot >= world.Body.Variables.Count ||
            !DerivesFrom(world.Body.Variables[slot].VariableType, rgd, types))
            throw new InvalidDataException("world_original_local_shape_drift");
        var stores = Enumerable.Range(0, saveAt).Where(i =>
            LocalSlot(worldIl[i], store: true) == slot).ToArray();
        if (stores.Length != 1) throw new InvalidDataException("world_local_store_shape_drift");
        int beforeStore = PriorNonNop(world, stores[0]);
        if (beforeStore < 0 || !IsCall(worldIl[beforeStore]) ||
            worldIl[beforeStore].Operand is not MethodReference reference ||
            reference.DeclaringType.FullName != save.DeclaringType.FullName ||
            reference.Parameters.Count != 0 || !reference.HasThis ||
            !DerivesFrom(reference.ReturnType, rgd, types))
            throw new InvalidDataException("world_producer_contract_drift");
        MethodDefinition? original = null;
        try { original = reference.Resolve(); } catch (Exception) {}
        if (original is null || !original.HasBody || original.Module != save.Module ||
            original.DeclaringType.FullName != save.DeclaringType.FullName ||
            !DerivesFrom(original.ReturnType, rgd, types))
            throw new InvalidDataException("world_original_factory_body_not_pinned");

        var il = original.Body.Instructions;
        int returns = 0, nullPredecessor = 0, localPredecessor = 0,
            fieldPredecessor = 0, typedCallPredecessor = 0,
            typedNewPredecessor = 0, otherPredecessor = 0;
        int typedConstructors = 0, typedCallReturns = 0,
            conditionalBranches = 0, throwSites = 0, nullLiteralLoads = 0;

        for (int i = 0; i < il.Count; i++)
        {
            var ins = il[i];
            if (ins.OpCode.FlowControl == FlowControl.Cond_Branch)
                conditionalBranches++;
            if (ins.OpCode.Code is Code.Throw or Code.Rethrow)
                throwSites++;
            if (ins.OpCode.Code == Code.Ldnull)
                nullLiteralLoads++;
            if (ins.OpCode.Code == Code.Newobj && ins.Operand is MethodReference ctor &&
                DerivesFrom(ctor.DeclaringType, rgd, types))
                typedConstructors++;
            if (IsCall(ins) && ins.Operand is MethodReference method &&
                DerivesFrom(method.ReturnType, rgd, types))
                typedCallReturns++;
            if (ins.OpCode.Code != Code.Ret) continue;
            returns++;
            int before = PriorNonNop(original, i);
            if (before < 0) { otherPredecessor++; continue; }
            var prev = il[before];
            if (prev.OpCode.Code == Code.Ldnull) { nullPredecessor++; continue; }
            int local = LocalSlot(prev, store: false);
            if (local >= 0 && local < original.Body.Variables.Count &&
                DerivesFrom(original.Body.Variables[local].VariableType, rgd, types))
            { localPredecessor++; continue; }
            if ((prev.OpCode.Code == Code.Ldfld || prev.OpCode.Code == Code.Ldsfld) &&
                prev.Operand is FieldReference fld && DerivesFrom(fld.FieldType, rgd, types))
            { fieldPredecessor++; continue; }
            if (IsCall(prev) && prev.Operand is MethodReference called &&
                DerivesFrom(called.ReturnType, rgd, types))
            { typedCallPredecessor++; continue; }
            if (prev.OpCode.Code == Code.Newobj &&
                prev.Operand is MethodReference ctorAtRet &&
                DerivesFrom(ctorAtRet.DeclaringType, rgd, types))
            { typedNewPredecessor++; continue; }
            otherPredecessor++;
        }
        if (returns < 1 || returns > 10000 ||
            nullPredecessor + localPredecessor + fieldPredecessor +
                typedCallPredecessor + typedNewPredecessor + otherPredecessor != returns)
            throw new InvalidDataException("original_factory_return_counts_inconsistent");

        if (returns != 1 || localPredecessor != 1)
            throw new InvalidDataException("factory_expected_single_derived_RGD_local_return");
        int retAt = il.ToList().FindIndex(i => i.OpCode.Code == Code.Ret);
        int loadAt = PriorNonNop(original, retAt);
        int returnedSlot = loadAt < 0 ? -1 :
            LocalSlot(il[loadAt], store: false);
        if (returnedSlot < 0 || returnedSlot >= original.Body.Variables.Count ||
            !DerivesFrom(original.Body.Variables[returnedSlot].VariableType,
                rgd, types))
            throw new InvalidDataException("factory_return_local_shape_drift");
        int returnedStores = 0, storeNull = 0, storeCtor = 0, storeCall = 0,
            storeLocal = 0, storeField = 0, storeUnknown = 0;
        string lastStoreClass = "NO_STORES";
        for (int at = 0; at < retAt; at++)
        {
            var candidate = il[at];
            if (LocalSlot(candidate, store: true) != returnedSlot) continue;
            returnedStores++;
            string source = FactoryLocalPrestoreClass(original, candidate, types, rgd);
            lastStoreClass = source;
            switch (source)
            {
                case "NULL_LITERAL": storeNull++; break;
                case "DERIVED_CONSTRUCTOR": storeCtor++; break;
                case "DERIVED_CALL": storeCall++; break;
                case "DERIVED_LOCAL": storeLocal++; break;
                case "DERIVED_FIELD": storeField++; break;
                default: storeUnknown++; break;
            }
        }
        if (returnedStores > 10000 ||
            storeNull + storeCtor + storeCall + storeLocal +
                storeField + storeUnknown != returnedStores)
            throw new InvalidDataException("factory_local_store_partition_invalid");

        int derivedLocals = original.Body.Variables.Count(v =>
            DerivesFrom(v.VariableType, rgd, types));
        return new
        {
            factory_lexical_return_sites = returns,
            factory_return_preceded_by_null_literal = nullPredecessor,
            factory_return_preceded_by_derived_local = localPredecessor,
            factory_return_preceded_by_derived_field = fieldPredecessor,
            factory_return_preceded_by_derived_call = typedCallPredecessor,
            factory_return_preceded_by_derived_constructor = typedNewPredecessor,
            factory_return_preceded_by_other_or_unknown = otherPredecessor,
            factory_derived_rgd_local_slot_count = derivedLocals,
            factory_direct_derived_rgd_constructor_sites = typedConstructors,
            factory_direct_derived_rgd_returning_call_sites = typedCallReturns,
            factory_conditional_branch_sites = conditionalBranches,
            factory_throw_or_rethrow_sites = throwSites,
            factory_null_literal_load_sites = nullLiteralLoads,
            factory_all_return_paths_proven = false,
            factory_return_local_lexical_store_sites = returnedStores,
            factory_return_local_store_null_literal = storeNull,
            factory_return_local_store_derived_constructor = storeCtor,
            factory_return_local_store_derived_call = storeCall,
            factory_return_local_store_derived_local = storeLocal,
            factory_return_local_store_derived_field = storeField,
            factory_return_local_store_other_or_unknown = storeUnknown,
            factory_return_local_nearest_lexical_store_source = lastStoreClass,
            factory_return_local_store_path_reachability_proven = false
        };
    }


    // The exact original returned local, counted only by lexical stloc writes.
    // These categories say nothing about executed control flow, nonnull values,
    // or whether a store has reached the one return in a particular world.
    private static string FactoryLocalPrestoreClass(
        MethodDefinition method, Instruction store, TypeDefinition[] types,
        string rgd)
    {
        int previous = PriorNonNop(method, method.Body.Instructions.IndexOf(store));
        if (previous < 0) return "OTHER_OR_UNKNOWN";
        var i = method.Body.Instructions[previous];
        if (i.OpCode.Code == Code.Ldnull) return "NULL_LITERAL";
        if (i.OpCode.Code == Code.Newobj && i.Operand is MethodReference ctor &&
            DerivesFrom(ctor.DeclaringType, rgd, types))
            return "DERIVED_CONSTRUCTOR";
        if (IsCall(i) && i.Operand is MethodReference called &&
            DerivesFrom(called.ReturnType, rgd, types))
            return "DERIVED_CALL";
        int slot = LocalSlot(i, store: false);
        if (slot >= 0 && slot < method.Body.Variables.Count &&
            DerivesFrom(method.Body.Variables[slot].VariableType, rgd, types))
            return "DERIVED_LOCAL";
        if (i.OpCode.Code is Code.Ldfld or Code.Ldsfld &&
            i.Operand is FieldReference field &&
            DerivesFrom(field.FieldType, rgd, types))
            return "DERIVED_FIELD";
        return "OTHER_OR_UNKNOWN";
    }

    private static string ImmediateStoreValueCategory(
        MethodDefinition m, Instruction write, TypeDefinition[] types, string rgd)
    {
        int at = m.Body.Instructions.IndexOf(write);
        int k = PriorNonNop(m, at);
        if (k < 0) return "UNKNOWN_OR_OTHER";
        var prev = m.Body.Instructions[k];
        if (prev.OpCode.Code == Code.Ldnull)
            return "NULL_LITERAL";
        if (IsCall(prev) && prev.Operand is MethodReference called &&
            DerivesFrom(called.ReturnType, rgd, types))
            return "DERIVED_TYPED_IMMEDIATE";
        if (prev.OpCode.Code == Code.Newobj &&
            prev.Operand is MethodReference ctor &&
            DerivesFrom(ctor.DeclaringType, rgd, types))
            return "DERIVED_TYPED_IMMEDIATE";
        int local = LocalSlot(prev, store: false);
        if (local >= 0 && local < m.Body.Variables.Count &&
            DerivesFrom(m.Body.Variables[local].VariableType, rgd, types))
            return "DERIVED_TYPED_IMMEDIATE";
        if ((prev.OpCode.Code == Code.Ldfld || prev.OpCode.Code == Code.Ldsfld) &&
            prev.Operand is FieldReference read &&
            DerivesFrom(read.FieldType, rgd, types))
            return "DERIVED_TYPED_IMMEDIATE";
        return "UNKNOWN_OR_OTHER";
    }

    private static object UserFieldWrites(
        MethodDefinition user, MethodDefinition save, TypeDefinition[] types, string rgd)
    {
        var instructions = user.Body.Instructions;
        int i = PriorNonNop(user, instructions.IndexOf(FindSaveCall(user, save)));
        if (i < 0 || instructions[i].OpCode.Code is not (Code.Ldfld or Code.Ldsfld) ||
            instructions[i].Operand is not FieldReference field ||
            field.DeclaringType.FullName != save.DeclaringType.FullName ||
            !DerivesFrom(field.FieldType, rgd, types))
            throw new InvalidDataException("original_user_field_shape_drift");

        int ctor = 0, cctor = 0, world = 0, userWrites = 0,
            otherOwner = 0, otherType = 0, nullSource = 0,
            derivedSource = 0, unknownSource = 0;
        foreach (var t in types)
            foreach (var method in t.Methods.Where(x => x.HasBody))
                foreach (var ins in method.Body.Instructions)
                {
                    if (ins.OpCode.Code is not (Code.Stfld or Code.Stsfld) ||
                        ins.Operand is not FieldReference f ||
                        f.Name != field.Name ||
                        f.DeclaringType.FullName != field.DeclaringType.FullName ||
                        f.FieldType.FullName != field.FieldType.FullName)
                        continue;
                    if (method.DeclaringType.FullName != save.DeclaringType.FullName)
                        otherType++;
                    else if (method.IsConstructor && method.IsStatic) cctor++;
                    else if (method.IsConstructor) ctor++;
                    else if (method.Name == "SaveWorld") world++;
                    else if (method.Name == "SaveUser") userWrites++;
                    else otherOwner++;
                    switch (ImmediateStoreValueCategory(method, ins, types, rgd))
                    {
                        case "NULL_LITERAL": nullSource++; break;
                        case "DERIVED_TYPED_IMMEDIATE": derivedSource++; break;
                        default: unknownSource++; break;
                    }
                }
        int total = ctor + cctor + world + userWrites + otherOwner + otherType;
        if (total != 3 || nullSource + derivedSource + unknownSource != total)
            throw new InvalidDataException("original_field_sites_drift");
        return new
        {
            user_original_direct_write_sites = total,
            user_field_writes_in_instance_constructor = ctor,
            user_field_writes_in_static_constructor = cctor,
            user_field_writes_in_saveworld = world,
            user_field_writes_in_saveuser = userWrites,
            user_field_writes_in_other_saveandload_methods = otherOwner,
            user_field_writes_in_other_original_types = otherType,
            user_field_write_immediate_null_literals = nullSource,
            user_field_write_immediate_derived_typed_values = derivedSource,
            user_field_write_immediate_unknown_or_other = unknownSource
        };
    }

    private static int Main(string[] args)
    {
        if (args.Length != 4 || args[0] != "--assembly" || args[2] != "--output")
        {
            Console.WriteLine("T4_ORIGINAL_RGD_INIT status=INVALID_ARGUMENTS");
            return 2;
        }
        try
        {
            var original = new FileInfo(Path.GetFullPath(args[1]));
            if (!original.Exists || original.LinkTarget is not null ||
                original.Length != OriginalLength)
                throw new InvalidDataException("unauthentic_original_bytes");
            using (var s = original.OpenRead())
                if (Convert.ToHexString(SHA256.HashData(s)).ToLowerInvariant() != OriginalSha)
                    throw new InvalidDataException("unauthentic_original_sha");

            using var assembly = AssemblyDefinition.ReadAssembly(original.FullName,
                new ReaderParameters { ReadSymbols = false });
            var all = AllTypes(assembly.MainModule);
            var owners = all.Where(t => t.FullName == "SaveAndLoad").ToArray();
            if (owners.Length != 1) throw new InvalidDataException("save_owner_ambiguous");
            var owner = owners[0];
            var world = UniqueVoidNoArg(owner, "SaveWorld");
            var user = UniqueVoidNoArg(owner, "SaveUser");
            var save = UniquePrivateSave(owner);
            string rgd = save.Parameters[1].ParameterType.FullName;
            if (all.Count(t => t.FullName == rgd) != 1)
                throw new InvalidDataException("rgd_owner_ambiguous");

            var producer = WorldProducer(world, save, all, rgd);
            var writes = UserFieldWrites(user, save, all, rgd);
            var factoryReturns = WorldProducerReturnSites(world, save, all, rgd);
            var report = new
            {
                schema = 1,
                scope = "PINNED_ORIGINAL_READONLY_IL_CLASSIFICATION",
                original_assembly_sha_verified = true,
                original_world_and_user_save_rgd_edges_verified = true,
                world_producer_declaring_scope = producer.Scope,
                world_producer_argument_count_category = producer.Arity,
                world_producer_invocation_kind = producer.Kind,
                world_producer_compiled_method_body_found = producer.CompiledBody,
                field_write_breakdown = writes,
                world_factory_return_metadata = factoryReturns,
                direct_game_save_invoked = false,
                actual_world_data_initialized = false,
                original_rgd_file_read_or_written = false,
                android_unity_il2cpp_device_executed = false,
                derived_rgd_object_identity_or_control_flow_proven = false,
                private_game_code_or_data_published = false
            };
            string output = Path.GetFullPath(args[3]);
            if (File.Exists(output) || Directory.Exists(output) ||
                new FileInfo(output).LinkTarget is not null)
                throw new InvalidDataException("unsafe_output");
            Directory.CreateDirectory(Path.GetDirectoryName(output)!);
            File.WriteAllText(output, JsonSerializer.Serialize(report));
            Console.WriteLine("T4_ORIGINAL_RGD_INIT original_source_sha_verified=true read_only=true");
            return 0;
        }
        catch (Exception)
        {
            Console.WriteLine("T4_ORIGINAL_RGD_INIT status=INCONCLUSIVE " +
                "private_details_published=false original_save_invoked=false");
            return 2;
        }
    }
}
