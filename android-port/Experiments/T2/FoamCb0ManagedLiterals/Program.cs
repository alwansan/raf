// T2 original Foam serialized CB0 string-name / original managed setter *candidate* census.
// Source-authenticated original DLL is never executed; no symbols, hashes,
// private method tokens, managed strings or source/body are published.
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const string OriginalSha256 =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";
    private const int OriginalBytes = 3211776;
    private static readonly string[] Roles = ["buffer", "vector", "matrix"];
    private const int MaxMethods = 80000;
    private const int MaxInstructions = 2000000;
    private const int MaxTargetHashes = 128;
    private const int NearInstructionWindow = 16;

    private static string Sha(string value) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();

    private static Dictionary<string, HashSet<string>> LoadPrivateTargets(string path,
                                                                           out int unknownSource)
    {
        using var doc = JsonDocument.Parse(File.ReadAllText(path, Encoding.UTF8));
        var root = doc.RootElement;
        if (root.GetProperty("schema").GetInt32() != 1 ||
            root.GetProperty("source_kind").GetString() !=
            "SHA_original_Foam_CB0_source_name_registry" ||
            root.GetProperty("original_stage_count").GetInt32() != 4 ||
            root.GetProperty("original_cb0_stage_bindings").GetInt32() != 4 ||
            root.GetProperty("actual_Unity_upload_proven").GetBoolean())
            throw new InvalidDataException("Private original source registry mismatch");
        unknownSource = root.GetProperty(
            "original_cb0_parameter_name_indices_unresolved").GetInt32();
        if (unknownSource < 0 || unknownSource > 512)
            throw new InvalidDataException("Unbounded unresolved original CB names");
        var categories = root.GetProperty("categories_sha256");
        var groups = new Dictionary<string, HashSet<string>>(StringComparer.Ordinal);
        int sum = 0;
        foreach (var role in Roles)
        {
            var names = categories.GetProperty(role);
            if (names.ValueKind != JsonValueKind.Array ||
                names.GetArrayLength() > MaxTargetHashes)
                throw new InvalidDataException("Invalid source name digest categories");
            var set = new HashSet<string>(StringComparer.Ordinal);
            foreach (var node in names.EnumerateArray())
            {
                string? digest = node.GetString();
                if (digest is null || digest.Length != 64 ||
                    digest.Any(c => !"0123456789abcdef".Contains(c)) ||
                    !set.Add(digest))
                    throw new InvalidDataException("Invalid private source SHA target");
            }
            groups.Add(role, set);
            sum += set.Count;
        }
        if (groups["buffer"].Count == 0 || sum == 0 || sum > MaxTargetHashes)
            throw new InvalidDataException("Original private target set missing");
        return groups;
    }

    internal static string MaterialFieldStoreImmediateProducer(
        IList<Instruction> instructions, int storePosition, MethodDefinition? context = null)
    {
        if (storePosition < 1 || storePosition >= instructions.Count ||
            instructions[storePosition].OpCode.Code != Code.Stfld ||
            instructions[storePosition].Operand is not FieldReference target ||
            target.FieldType.FullName != "UnityEngine.Material")
            return "unverified_Material_field_store";
        var atStore = instructions[storePosition];
        if (instructions.Any(x => ReferenceEquals(x.Operand, atStore) ||
            x.Operand is Instruction[] branches &&
            branches.Any(t => ReferenceEquals(t,atStore))) ||
            context?.HasBody == true && context.Body.ExceptionHandlers.Any(x =>
                ReferenceEquals(x.TryStart,atStore) ||
                ReferenceEquals(x.HandlerStart,atStore) ||
                ReferenceEquals(x.FilterStart,atStore)))
            return "alternate_entry_at_store";
        var before=instructions[storePosition-1];
        if (before.OpCode.Code == Code.Newobj &&
            before.Operand is MethodReference constructor &&
            constructor.DeclaringType.FullName == "UnityEngine.Material" &&
            constructor.Name == ".ctor" &&
            constructor.HasThis)
            return constructor.Parameters.Count == 1 &&
                constructor.Parameters[0].ParameterType.FullName == "UnityEngine.Shader"
                ? "immediate_new_Material_with_Shader_formal"
                : "immediate_new_Material_other_formals";
        if (before.OpCode.Code is Code.Call or Code.Callvirt &&
            before.Operand is MethodReference method &&
            method.ReturnType.FullName == "UnityEngine.Material")
            return method.DeclaringType.FullName == "UnityEngine.Renderer" &&
                method.Name is "get_material" or "get_sharedMaterial"
                ? "immediate_Renderer_material_getter"
                : "immediate_typed_Material_call_result";
        if (before.OpCode.Code == Code.Ldfld &&
            before.Operand is FieldReference field &&
            field.FieldType.FullName == "UnityEngine.Material")
            return "immediate_typed_Material_field_load";
        if (before.OpCode.Code == Code.Ldsfld &&
            before.Operand is FieldReference staticField &&
            staticField.FieldType.FullName == "UnityEngine.Material")
            return "immediate_typed_Material_static_field_load";
        if (before.OpCode.Code == Code.Ldnull)
            return "immediate_null_literal";
        return "immediate_value_source_unproven";
    }

    private static IEnumerable<TypeDefinition> Walk(IEnumerable<TypeDefinition> types)
    {
        foreach (var type in types)
        {
            yield return type;
            foreach (var nested in Walk(type.NestedTypes))
                yield return nested;
        }
    }

    // Public Unity type/overload schema only. Does not prove actual call argument.
    internal static string? SetterKind(string declaringType, string name,
                                      string firstFormalType, string secondFormalType)
    {
        if (firstFormalType is not ("System.String" or "System.Int32"))
            return null;
        string family = name switch
        {
            "SetVector" or "SetGlobalVector" when secondFormalType == "UnityEngine.Vector4" => "vector",
            "SetFloat" or "SetGlobalFloat" when secondFormalType == "System.Single" => "float",
            "SetMatrix" or "SetGlobalMatrix" when secondFormalType == "UnityEngine.Matrix4x4" => "matrix",
            "SetColor" or "SetGlobalColor" when secondFormalType == "UnityEngine.Color" => "color",
            "SetConstantBuffer" or "SetGlobalConstantBuffer"
                when secondFormalType is ("UnityEngine.ComputeBuffer" or "UnityEngine.GraphicsBuffer")
                => "constant_buffer",
            _ => ""
        };
        if (family == "")
            return null;
        bool globalName = name.StartsWith("SetGlobal", StringComparison.Ordinal);
        if (declaringType == "UnityEngine.Material" && !globalName)
            return "material_" + family;
        if (declaringType == "UnityEngine.MaterialPropertyBlock" && !globalName)
            return "propertyblock_" + family;
        if (declaringType == "UnityEngine.Shader" && globalName)
            return "shader_global_" + family;
        if (declaringType == "UnityEngine.Rendering.CommandBuffer" && globalName)
            return "commandbuffer_global_" + family;
        if (declaringType == "UnityEngine.ComputeShader" && !globalName)
            return "compute_shader_" + family;
        return null;
    }

    private static string? TypedSetter(Instruction instruction)
    {
        if (instruction.OpCode.Code is not (Code.Call or Code.Callvirt) ||
            instruction.Operand is not MethodReference method ||
            method.Parameters.Count < 2)
            return null;
        return SetterKind(method.DeclaringType.FullName, method.Name,
                          method.Parameters[0].ParameterType.FullName,
                          method.Parameters[1].ParameterType.FullName);
    }

    private static bool PropertyToId(Instruction instruction)
    {
        return instruction.OpCode.Code is Code.Call or Code.Callvirt &&
               instruction.Operand is MethodReference method &&
               method.DeclaringType.FullName == "UnityEngine.Shader" &&
               method.Name == "PropertyToID" &&
               method.Parameters.Count == 1 &&
               method.Parameters[0].ParameterType.FullName == "System.String";
    }

    private sealed class Category
    {
        public readonly HashSet<string> Unique = new(StringComparer.Ordinal);
        public int LiteralOccurrences;
        public int DistinctMethodsWithLiteral;
        public int MethodsContainingTypedSetter;
        public int LiteralWithin16InstructionsOfTypedSetter;
        public int LiteralWithin4InstructionsOfPropertyToId;
        public int ExactSourceStringFirstFormalCallCount;
        public int ExactSourcePropertyIdFirstFormalCallCount;
        public readonly HashSet<string> ExactFirstFormalProvenNames = new(StringComparer.Ordinal);
    }

    private static object Probe(string originalDll, string privateTargetFile)
    {
        var file = new FileInfo(originalDll);
        if (!file.Exists || file.Length != OriginalBytes ||
            !string.Equals(Convert.ToHexString(SHA256.HashData(
                File.ReadAllBytes(originalDll))).ToLowerInvariant(), OriginalSha256,
                StringComparison.Ordinal))
            throw new InvalidDataException("Original managed DLL SHA/size authentication failed");
        var names = LoadPrivateTargets(privateTargetFile, out int unknownSource);
        using var assembly = AssemblyDefinition.ReadAssembly(originalDll,
            new ReaderParameters { ReadSymbols = false, ReadingMode = ReadingMode.Deferred });
        var groups = Roles.ToDictionary(x => x, _ => new Category(), StringComparer.Ordinal);
        int methods = 0, instructions = 0, strings = 0, typedSetters = 0;
        var nearSetterCategories = new SortedDictionary<string, int>(StringComparer.Ordinal);
        var exactlyProvenSetterFamilies = new SortedDictionary<string, int>(StringComparer.Ordinal);
        var exactlyProvenSecondValueOrigins = new SortedDictionary<string, int>(StringComparer.Ordinal);
        var exactlyProvenMaterialReceiverOrigins = new SortedDictionary<string, int>(StringComparer.Ordinal);
        var uniqueVector4ConstructorStatuses = new SortedDictionary<string, int>(StringComparer.Ordinal);
        var typedVector4CtorScalarInputSources = new SortedDictionary<string, int>(StringComparer.Ordinal);
        int typedVector4CtorFormalTotal = 0, typedVector4CtorFloatFormalTotal = 0;
        int exactOriginalCtorFieldOccurrences = 0, exactOriginalCtorFloatFieldOccurrences = 0;
        int exactOriginalCtorDistinctDeclaringTypes = 0;
        var exactOriginalCtorFields = new HashSet<string>(StringComparer.Ordinal);
        var originalMaterialPrefixCategories = new SortedDictionary<string, int>(StringComparer.Ordinal);
        var exactOriginalReceiverMaterialFieldIds = new HashSet<string>(StringComparer.Ordinal);
        var exactOriginalReceiverMaterialDeclaringTypes = new HashSet<string>(StringComparer.Ordinal);

        foreach (var type in Walk(assembly.MainModule.Types))
        foreach (var method in type.Methods)
        {
            if (++methods > MaxMethods)
                throw new InvalidDataException("Too many original managed methods");
            if (!method.HasBody)
                continue;
            var items = method.Body.Instructions;
            instructions += items.Count;
            if (instructions > MaxInstructions)
                throw new InvalidDataException("Unbounded original managed instructions");
            var literals = new List<(int Position, string Hash)>();
            var setters = new List<(int Position, string Family)>();
            var propertyToId = new List<int>();
            for (int i = 0; i < items.Count; i++)
            {
                var item = items[i];
                if (item.OpCode.Code == Code.Ldstr && item.Operand is string value)
                {
                    strings++;
                    if (value.Length <= 256 && value.Length > 0)
                    {
                        string h = Sha(value);
                        if (Roles.Any(role => names[role].Contains(h)))
                            literals.Add((i, h));
                    }
                }
                var kind = TypedSetter(item);
                if (kind is not null)
                {
                    typedSetters++;
                    setters.Add((i, kind));
                }
                if (PropertyToId(item))
                    propertyToId.Add(i);
            }
            foreach (var role in Roles)
            {
                var rows = literals.Where(x => names[role].Contains(x.Hash)).ToList();
                if (rows.Count == 0)
                    continue;
                var summary = groups[role];
                summary.DistinctMethodsWithLiteral++;
                summary.LiteralOccurrences += rows.Count;
                if (setters.Count != 0)
                    summary.MethodsContainingTypedSetter++;
                foreach (var row in rows)
                {
                    summary.Unique.Add(row.Hash);
                    var exact = Cb0ExactFirstFormal.Trace(items, row.Position, method);
                    if (exact.HasValue)
                    {
                        summary.ExactFirstFormalProvenNames.Add(row.Hash);
                        originalMaterialPrefixCategories[exact.Value.StrictMaterialReceiverImmediatePrefixOrigin] =
                            originalMaterialPrefixCategories.GetValueOrDefault(
                                exact.Value.StrictMaterialReceiverImmediatePrefixOrigin) + 1;
                        if (exact.Value.StrictMaterialReceiverImmediatePrefixOrigin ==
                                "direct_adjacent_typed_Material_field_load" &&
                            row.Position > 0 &&
                            items[row.Position-1].Operand is FieldReference materialField &&
                            materialField.FieldType.FullName == "UnityEngine.Material")
                        {
                            // Never serialize or print these source-private field IDs.
                            exactOriginalReceiverMaterialFieldIds.Add(materialField.FullName);
                            exactOriginalReceiverMaterialDeclaringTypes.Add(
                                materialField.DeclaringType.FullName);
                        }
                        exactlyProvenSetterFamilies[exact.Value.SetterFamily] =
                            exactlyProvenSetterFamilies.GetValueOrDefault(exact.Value.SetterFamily) + 1;
                        // Only attached to the same authenticated literal→setter
                        // first-formal link, never arbitrary adjacent calls.
                        exactlyProvenSecondValueOrigins[exact.Value.SecondVectorValueOrigin] =
                            exactlyProvenSecondValueOrigins.GetValueOrDefault(exact.Value.SecondVectorValueOrigin) + 1;
                        exactlyProvenMaterialReceiverOrigins[exact.Value.MaterialReceiverOrigin] =
                            exactlyProvenMaterialReceiverOrigins.GetValueOrDefault(exact.Value.MaterialReceiverOrigin) + 1;
                        string ctorStatus = exact.Value.UniqueVector4ConstructorStatus;
                        uniqueVector4ConstructorStatuses[ctorStatus] =
                            uniqueVector4ConstructorStatuses.GetValueOrDefault(ctorStatus) + 1;
                        if (ctorStatus == "one_typed_UnityEngine_Vector4_ctor_in_slice")
                        {
                            typedVector4CtorFormalTotal +=
                                exact.Value.UniqueVector4ConstructorParameterCount;
                            typedVector4CtorFloatFormalTotal +=
                                exact.Value.UniqueVector4ConstructorFloatFormalCount;
                            exactOriginalCtorFieldOccurrences +=
                                exact.Value.UniqueVector4ConstructorExactInputFieldCount;
                            exactOriginalCtorFloatFieldOccurrences +=
                                exact.Value.UniqueVector4ConstructorInputSystemSingleFieldCount;
                            exactOriginalCtorDistinctDeclaringTypes +=
                                exact.Value.UniqueVector4ConstructorDistinctDeclaringTypeCount;
                            if (exact.Value.UniqueVector4ConstructorExactInputFieldCount == 3 &&
                                exact.Value.UniqueVector4ConstructorInputSystemSingleFieldCount == 3 &&
                                exact.Value.UniqueVector4ConstructorInputOriginCounts.GetValueOrDefault(
                                    "instance_field_load") == 3 &&
                                exact.Value.PrivateCtorInputFieldIds.Count == 3)
                            {
                                foreach (string identity in exact.Value.PrivateCtorInputFieldIds)
                                    exactOriginalCtorFields.Add(identity);
                            }
                            foreach (var origin in exact.Value.UniqueVector4ConstructorInputOriginCounts)
                            {
                                typedVector4CtorScalarInputSources[origin.Key] =
                                    typedVector4CtorScalarInputSources.GetValueOrDefault(origin.Key) +
                                    origin.Value;
                            }
                        }
                        if (exact.Value.Kind == "source_literal_as_string")
                            summary.ExactSourceStringFirstFormalCallCount++;
                        else if (exact.Value.Kind == "source_literal_via_PropertyToID")
                            summary.ExactSourcePropertyIdFirstFormalCallCount++;
                    }
                    if (setters.Any(s => s.Position >= row.Position &&
                                        s.Position <= row.Position + NearInstructionWindow))
                    {
                        summary.LiteralWithin16InstructionsOfTypedSetter++;
                        foreach (var family in setters.Where(
                            s => s.Position >= row.Position &&
                                 s.Position <= row.Position + NearInstructionWindow)
                            .Select(s => s.Family).Distinct(StringComparer.Ordinal))
                        {
                            nearSetterCategories[family] =
                                nearSetterCategories.GetValueOrDefault(family) + 1;
                        }
                    }
                    if (propertyToId.Any(i => i >= row.Position && i <= row.Position + 4))
                        summary.LiteralWithin4InstructionsOfPropertyToId++;
                }
            }
        }
        // Second static pass only over authenticated managed DLL: lexical
        // stfld references to exactly the three proven constructor operands.
        // A write site does not establish runtime reachability or numeric value.
        int exactOriginalFieldStoreInstructions = 0;
        int methodsWithStoreToExactOriginalFields = 0;
        var exactOriginalFieldsWithStores = new HashSet<string>(StringComparer.Ordinal);
        int originalExactReceiverMaterialFieldStores = 0;
        int originalExactReceiverMaterialWriterMethodCount = 0;
        int materialWriterMethodsContainingShaderFind = 0;
        int materialWriterMethodsContainingMaterialCtor = 0;
        int materialWriterMethodsContainingRendererGetter = 0;
        var originalMaterialStoreImmediateSources =
            new SortedDictionary<string, int>(StringComparer.Ordinal);
        var originalReceiverMaterialFieldsWithStfld = new HashSet<string>(StringComparer.Ordinal);
        foreach (var definition in Walk(assembly.MainModule.Types))
        foreach (var method in definition.Methods)
        {
            if (!method.HasBody) continue;
            bool methodHasStore = false;
            bool methodHasExactMaterialStore = false;
            var originalInstructions=method.Body.Instructions;
            for (int i=0;i<originalInstructions.Count;i++)
            {
                var instruction=originalInstructions[i];
                if (instruction.OpCode.Code != Code.Stfld ||
                    instruction.Operand is not FieldReference field)
                    continue;
                if (exactOriginalCtorFields.Contains(field.FullName))
                {
                    exactOriginalFieldStoreInstructions++;
                    exactOriginalFieldsWithStores.Add(field.FullName);
                    methodHasStore = true;
                }
                if (field.FieldType.FullName == "UnityEngine.Material" &&
                    exactOriginalReceiverMaterialFieldIds.Contains(field.FullName))
                {
                    originalExactReceiverMaterialFieldStores++;
                    originalReceiverMaterialFieldsWithStfld.Add(field.FullName);
                    methodHasExactMaterialStore = true;
                    string origin=MaterialFieldStoreImmediateProducer(
                        originalInstructions,i,method);
                    originalMaterialStoreImmediateSources[origin] =
                        originalMaterialStoreImmediateSources.GetValueOrDefault(origin)+1;
                }
            }
            if (methodHasStore) methodsWithStoreToExactOriginalFields++;
            if (methodHasExactMaterialStore)
            {
                originalExactReceiverMaterialWriterMethodCount++;
                bool hasShaderFind=false, hasMaterialCtor=false, hasRendererGetter=false;
                foreach (var instruction in originalInstructions)
                {
                    if (instruction.OpCode.Code is not (Code.Call or Code.Callvirt or Code.Newobj) ||
                        instruction.Operand is not MethodReference call) continue;
                    hasShaderFind |= call.DeclaringType.FullName == "UnityEngine.Shader" &&
                        call.Name == "Find" &&
                        call.ReturnType.FullName == "UnityEngine.Shader";
                    hasMaterialCtor |= instruction.OpCode.Code == Code.Newobj &&
                        call.DeclaringType.FullName == "UnityEngine.Material" &&
                        call.Name == ".ctor";
                    hasRendererGetter |= call.DeclaringType.FullName == "UnityEngine.Renderer" &&
                        call.Name is "get_material" or "get_sharedMaterial" &&
                        call.ReturnType.FullName == "UnityEngine.Material";
                }
                materialWriterMethodsContainingShaderFind += hasShaderFind ? 1 : 0;
                materialWriterMethodsContainingMaterialCtor += hasMaterialCtor ? 1 : 0;
                materialWriterMethodsContainingRendererGetter += hasRendererGetter ? 1 : 0;
            }
        }
        return new
        {
            status = "original_Foam_CB0_source_name_managed_literal_contexts_scanned",
            original_managed_DLL_sha256_authenticated = true,
            original_managed_DLL_size_bytes = OriginalBytes,
            source_original_CB0_stage_bindings = 4,
            private_source_names_with_unresolved_name_index_count = unknownSource,
            total_original_compiled_methods_scanned = methods,
            total_original_IL_instructions_scanned = instructions,
            total_original_ldstr_instructions_scanned = strings,
            total_recognized_typed_Unity_uniform_setter_calls = typedSetters,
            source_target_count_by_role = Roles.ToDictionary(x=>x,x=>names[x].Count),
            unique_matched_managed_ldstr_by_role = Roles.ToDictionary(x=>x,x=>groups[x].Unique.Count),
            literal_occurrences_by_role = Roles.ToDictionary(x=>x,x=>groups[x].LiteralOccurrences),
            original_methods_with_matching_literal_by_role =
                Roles.ToDictionary(x=>x,x=>groups[x].DistinctMethodsWithLiteral),
            original_methods_containing_both_literal_and_typed_setter_by_role =
                Roles.ToDictionary(x=>x,x=>groups[x].MethodsContainingTypedSetter),
            literal_within_16_following_IL_instructions_of_typed_setter_by_role =
                Roles.ToDictionary(x=>x,x=>groups[x].LiteralWithin16InstructionsOfTypedSetter),
            literal_within_4_following_IL_instructions_of_PropertyToID_by_role =
                Roles.ToDictionary(x=>x,x=>groups[x].LiteralWithin4InstructionsOfPropertyToId),
            matched_literal_near_typed_setter_API_categories = nearSetterCategories,
            original_source_name_exact_typed_first_formal_unique_by_role =
                Roles.ToDictionary(x=>x,x=>groups[x].ExactFirstFormalProvenNames.Count),
            original_source_name_exact_typed_string_first_formal_calls_by_role =
                Roles.ToDictionary(x=>x,x=>groups[x].ExactSourceStringFirstFormalCallCount),
            original_source_name_exact_typed_PropertyToID_first_formal_calls_by_role =
                Roles.ToDictionary(x=>x,x=>groups[x].ExactSourcePropertyIdFirstFormalCallCount),
            original_source_name_exact_first_formal_typed_setter_API_categories = exactlyProvenSetterFamilies,
            original_source_name_exact_first_formal_second_value_IL_origin_buckets =
                exactlyProvenSecondValueOrigins,
            original_source_name_exact_first_formal_Material_receiver_IL_origin_buckets =
                exactlyProvenMaterialReceiverOrigins,
            original_source_name_exact_first_formal_Vector4_ctor_uniqueness_buckets =
                uniqueVector4ConstructorStatuses,
            original_source_name_proven_unique_Vector4_ctor_formal_count =
                typedVector4CtorFormalTotal,
            original_source_name_proven_unique_Vector4_ctor_float_formal_count =
                typedVector4CtorFloatFormalTotal,
            original_source_name_proven_unique_Vector4_ctor_scalar_input_origin_buckets =
                typedVector4CtorScalarInputSources,
            original_source_name_exact_Vector4_ctor_input_FieldReference_count =
                exactOriginalCtorFieldOccurrences,
            original_source_name_exact_Vector4_ctor_input_SystemSingle_FieldReference_count =
                exactOriginalCtorFloatFieldOccurrences,
            original_source_name_exact_Vector4_ctor_distinct_field_identity_count =
                exactOriginalCtorFields.Count,
            original_source_name_exact_Vector4_ctor_distinct_field_declaring_type_count =
                exactOriginalCtorDistinctDeclaringTypes,
            original_source_name_exact_Vector4_ctor_field_store_IL_instructions =
                exactOriginalFieldStoreInstructions,
            original_source_name_exact_Vector4_ctor_distinct_fields_with_stfld =
                exactOriginalFieldsWithStores.Count,
            original_source_name_exact_Vector4_ctor_original_methods_with_stfld =
                methodsWithStoreToExactOriginalFields,
            original_source_name_exact_Material_receiver_pre_ldstr_IL_prefix_buckets =
                originalMaterialPrefixCategories,
            original_source_name_exact_receiver_Material_FieldReference_count =
                exactOriginalReceiverMaterialFieldIds.Count,
            original_source_name_exact_receiver_Material_declaring_type_count =
                exactOriginalReceiverMaterialDeclaringTypes.Count,
            original_source_name_exact_receiver_Material_stfld_instruction_count =
                originalExactReceiverMaterialFieldStores,
            original_source_name_exact_receiver_Material_distinct_fields_with_stfld =
                originalReceiverMaterialFieldsWithStfld.Count,
            original_source_name_exact_receiver_Material_writer_method_count =
                originalExactReceiverMaterialWriterMethodCount,
            original_source_name_exact_receiver_Material_store_immediate_producer_buckets =
                originalMaterialStoreImmediateSources,
            original_source_name_exact_receiver_Material_writer_methods_with_Shader_Find =
                materialWriterMethodsContainingShaderFind,
            original_source_name_exact_receiver_Material_writer_methods_with_Material_ctor =
                materialWriterMethodsContainingMaterialCtor,
            original_source_name_exact_receiver_Material_writer_methods_with_Renderer_getter =
                materialWriterMethodsContainingRendererGetter,
            original_exact_Material_shader_is_source_Foam_verified = false,
            original_150_byte_or_160_byte_CB0_complete_managed_upload_proven = false,
            original_Vector4_ctor_input_values_verified = false,
            exact_original_Vector4_value_dataflow_to_CB0_verified = false,
            original_Material_receiver_Shader_is_Foam_verified = false,
            literal_adjacency_does_not_prove_operand_or_runtime_upload = true,
            original_Ldstr_is_exact_setter_argument_proven = false,
            runtime_Unity_CB0_value_upload_verified = false,
            actual_Adreno_water_pixels_verified = false,
            private_original_strings_hashes_method_IL_disclosed = false
        };
    }

    private static void SelfTest()
    {
        if (SetterKind("UnityEngine.Material", "SetVector", "System.String",
                       "UnityEngine.Vector4") != "material_vector")
            throw new InvalidOperationException("Setter positive schema");
        if (SetterKind("UnityEngine.Shader", "SetGlobalVector", "System.Int32",
                       "UnityEngine.Vector4") != "shader_global_vector")
            throw new InvalidOperationException("SetGlobalVector positive");
        if (SetterKind("UnityEngine.MaterialPropertyBlock", "SetFloat", "System.String",
                       "System.Single") != "propertyblock_float")
            throw new InvalidOperationException("PropertyBlock positive");
        if (SetterKind("UnityEngine.Shader", "SetGlobalConstantBuffer", "System.Int32",
                       "UnityEngine.ComputeBuffer") != "shader_global_constant_buffer")
            throw new InvalidOperationException("Global CBuffer positive");
        if (SetterKind("UnityEngine.Material", "SetVector", "System.Object",
                       "UnityEngine.Vector4") != null ||
            SetterKind("Game.Material", "SetVector", "System.String",
                       "UnityEngine.Vector4") != null ||
            SetterKind("UnityEngine.Shader", "SetGlobalTexture", "System.String",
                       "UnityEngine.Texture") != null ||
            SetterKind("UnityEngine.Material", "SetColor", "System.String",
                       "System.Single") != null)
            throw new InvalidOperationException("Setter negative schema");
        Cb0ExactFirstFormal.SelfTest();
        using (var module = ModuleDefinition.CreateModule(
            "public-material-writer-fixture", ModuleKind.Dll))
        {
            var materialType = new TypeReference("UnityEngine","Material",module,module);
            var shaderType = new TypeReference("UnityEngine","Shader",module,module);
            var sourceType = new TypeReference("PublicTest","Container",module,module);
            var field = new FieldReference("publicMaterial",materialType,sourceType);
            var wrongField = new FieldReference("notMaterial",module.TypeSystem.Object,sourceType);
            var ctor = new MethodReference(".ctor",module.TypeSystem.Void,materialType)
                {HasThis=true};
            ctor.Parameters.Add(new ParameterDefinition(shaderType));
            var store=Instruction.Create(OpCodes.Stfld,field);
            var valid=new List<Instruction> {
                Instruction.Create(OpCodes.Ldarg_0),
                Instruction.Create(OpCodes.Ldarg_1),
                Instruction.Create(OpCodes.Newobj,ctor),
                store
            };
            if (MaterialFieldStoreImmediateProducer(valid,3)!=
                "immediate_new_Material_with_Shader_formal")
                throw new InvalidOperationException("Material ctor typed immediate producer");
            var wrong=new List<Instruction>(valid);
            wrong[3]=Instruction.Create(OpCodes.Stfld,wrongField);
            if (MaterialFieldStoreImmediateProducer(wrong,3)!=
                "unverified_Material_field_store")
                throw new InvalidOperationException("NonMaterial field false-positive");
            var branched=new List<Instruction>(valid);
            branched.Insert(0,Instruction.Create(OpCodes.Br_S,store));
            if (MaterialFieldStoreImmediateProducer(branched,4)!=
                "alternate_entry_at_store")
                throw new InvalidOperationException("Direct branch to stfld invalidates producer");
            var unknown=new List<Instruction>(valid);
            unknown[2]=Instruction.Create(OpCodes.Ldarg_1);
            if (MaterialFieldStoreImmediateProducer(unknown,3)!=
                "immediate_value_source_unproven")
                throw new InvalidOperationException("Unknown immediate source not guessed");
        }
        Console.WriteLine("T2_CB0_MANAGED_CECIL_SELFTEST pass");
    }

    private static int Main(string[] args)
    {
        if (args.Length == 1 && args[0] == "--selftest")
        {
            SelfTest();
            return 0;
        }
        try
        {
            if (args.Length != 3 || File.Exists(args[2]) ||
                !Directory.Exists(Path.GetDirectoryName(Path.GetFullPath(args[2]))))
                throw new InvalidDataException("Unsafe private probe output path");
            var report = Probe(args[0], args[1]);
            string safe = JsonSerializer.Serialize(report);
            File.WriteAllText(args[2], safe+"\n",new UTF8Encoding(false));
            Console.WriteLine("T2_CB0_ORIGINAL_MANAGED_SAFE " + safe);
            return 0;
        }
        catch (Exception)
        {
            Console.WriteLine("{\"status\":\"blocked_private_original_managed_CB0_probe\","
                              + "\"Unity_CB0_upload_verified\":false,"
                              + "\"private_original_strings_disclosed\":false}");
            return 2;
        }
    }
}


// Fail-closed, single-basic-block IL stack provenance only. A proof of a
// compiled setter's first formal argument is NOT proof that the call executes,
// that its receiver uses Foam, nor that Unity writes CB0 bytes on device.
internal static class Cb0ExactFirstFormal
{
    internal readonly record struct Evidence(
        string SetterFamily, string Kind, string SecondVectorValueOrigin,
        string MaterialReceiverOrigin, string UniqueVector4ConstructorStatus,
        int UniqueVector4ConstructorParameterCount,
        int UniqueVector4ConstructorFloatFormalCount,
        IReadOnlyDictionary<string, int> UniqueVector4ConstructorInputOriginCounts,
        int UniqueVector4ConstructorExactInputFieldCount,
        int UniqueVector4ConstructorInputSystemSingleFieldCount,
        int UniqueVector4ConstructorDistinctInputFieldCount,
        int UniqueVector4ConstructorDistinctDeclaringTypeCount,
        IReadOnlyList<string> PrivateCtorInputFieldIds,
        string StrictMaterialReceiverImmediatePrefixOrigin);
    private enum Tag {
        Unknown, SourceString, SourcePropertyId, MethodArgument, NumericLiteral,
        InstanceFieldLoad, StaticFieldLoad, CallReturn, ConstructedInstance,
        NullLiteral, OtherString, PreLiteralUnknown
    }
    // These are opcode-source categories, not runtime object/value identity.
    private static string Origin(Tag tag) => tag switch {
        Tag.MethodArgument => "method_argument_load",
        Tag.NumericLiteral => "numeric_literal",
        Tag.InstanceFieldLoad => "instance_field_load",
        Tag.StaticFieldLoad => "static_field_load",
        Tag.CallReturn => "call_return",
        Tag.ConstructedInstance => "new_object",
        Tag.NullLiteral => "null_literal",
        Tag.OtherString => "other_string_literal",
        Tag.PreLiteralUnknown => "pre_literal_unknown",
        _ => "unproven_or_unsupported"
    };
    private const int MaxSteps = 24;
    private const int MaxStack = 64;
    // Field handles stay in the original-source runner; never serialize them.
    private readonly record struct TraceValue(Tag Kind, FieldReference? Field = null)
    {
        public static implicit operator TraceValue(Tag tag) => new(tag);
    }
    private static string StrictReceiverPrefix(
        IList<Instruction> items, int literalIndex, int preLiteralPops,
        MethodDefinition? context)
    {
        if (preLiteralPops != 1 || literalIndex < 1 || literalIndex >= items.Count)
            return "pre_literal_unproven";
        var atLiteral = items[literalIndex];
        // A branch or an exception-handler entry could skip the previous
        // instruction, so an adjacent field load would not prove stack-top.
        foreach (var instruction in items)
        {
            if (ReferenceEquals(instruction.Operand, atLiteral) ||
                instruction.Operand is Instruction[] targets &&
                targets.Any(t => ReferenceEquals(t, atLiteral)))
                return "pre_literal_alternate_entry";
        }
        if (context?.HasBody == true &&
            context.Body.ExceptionHandlers.Any(x =>
                ReferenceEquals(x.TryStart, atLiteral) ||
                ReferenceEquals(x.HandlerStart, atLiteral) ||
                ReferenceEquals(x.FilterStart, atLiteral)))
            return "pre_literal_alternate_entry";
        var preceding=items[literalIndex-1];
        if (preceding.OpCode.Code == Code.Ldfld &&
            preceding.Operand is FieldReference field &&
            field.FieldType.FullName == "UnityEngine.Material")
            return "direct_adjacent_typed_Material_field_load";
        if (preceding.OpCode.Code == Code.Ldsfld &&
            preceding.Operand is FieldReference staticField &&
            staticField.FieldType.FullName == "UnityEngine.Material")
            return "direct_adjacent_typed_Material_static_field_load";
        if (preceding.OpCode.Code is Code.Call or Code.Callvirt &&
            preceding.Operand is MethodReference method &&
            method.ReturnType.FullName == "UnityEngine.Material")
            return "direct_adjacent_typed_Material_call_result";
        if (context?.HasBody == true &&
            preceding.OpCode.Name.StartsWith("ldloc", StringComparison.Ordinal) &&
            !preceding.OpCode.Name.StartsWith("ldloca", StringComparison.Ordinal))
        {
            int? localIndex=Local(preceding);
            if (localIndex is >= 0 &&
                localIndex.Value < context.Body.Variables.Count &&
                context.Body.Variables[localIndex.Value].VariableType.FullName ==
                    "UnityEngine.Material")
                return "direct_adjacent_typed_Material_local_load";
        }
        return "pre_literal_unproven";
    }

    private static int? Local(Instruction i)
    {
        if (i.Operand is VariableDefinition variable)
            return variable.Index;
        string n = i.OpCode.Name;
        for (int k = 0; k < 4; k++)
            if (n.EndsWith("." + k.ToString(), StringComparison.Ordinal))
                return k;
        return null;
    }

    internal static Evidence? Trace(
        IList<Instruction> instructions, int literalIndex,
        MethodDefinition? methodContext = null)
    {
        if (literalIndex < 0 || literalIndex >= instructions.Count ||
            instructions[literalIndex].OpCode.Code != Code.Ldstr)
            return null;
        var stack = new List<TraceValue> { Tag.SourceString };
        var locals = new Dictionary<int, TraceValue>();
        int preLiteralUnderflows = 0;
        int newobjCount = 0, typedVector4CtorFormals = 0, typedVector4CtorFloats = 0;
        var uniqueCtorOrigins = new Dictionary<string, int>(StringComparer.Ordinal);
        var uniqueCtorFields = new List<FieldReference>();
        bool typedVector4CtorSeen = false;
        Evidence Matched(string family, string kind, TraceValue value, TraceValue receiver)
        {
            bool valid = value.Kind == Tag.ConstructedInstance &&
                newobjCount == 1 && typedVector4CtorSeen;
            var fields=valid ? uniqueCtorFields : new List<FieldReference>();
            return new Evidence(
                family, kind, Origin(value.Kind), Origin(receiver.Kind),
                valid ? "one_typed_UnityEngine_Vector4_ctor_in_slice"
                      : "not_uniquely_proven",
                valid ? typedVector4CtorFormals : 0,
                valid ? typedVector4CtorFloats : 0,
                valid ? new Dictionary<string, int>(uniqueCtorOrigins, StringComparer.Ordinal)
                      : new Dictionary<string, int>(StringComparer.Ordinal),
                fields.Count,
                fields.Count(x=>x.FieldType.FullName=="System.Single"),
                fields.Select(x=>x.FullName).Distinct(StringComparer.Ordinal).Count(),
                fields.Select(x=>x.DeclaringType.FullName).Distinct(StringComparer.Ordinal).Count(),
                fields.Select(x=>x.FullName).Distinct(StringComparer.Ordinal).ToArray(),
                StrictReceiverPrefix(instructions,literalIndex,preLiteralUnderflows,methodContext));
        }
        TraceValue Pop()
        {
            if (stack.Count == 0)
            {
                preLiteralUnderflows++;
                return Tag.PreLiteralUnknown;
            }
            var v = stack[^1];
            stack.RemoveAt(stack.Count - 1);
            return v;
        }
        bool Push(TraceValue t)
        {
            if (stack.Count >= MaxStack) return false;
            stack.Add(t);
            return true;
        }
        for (int pos = literalIndex + 1;
             pos < instructions.Count && pos <= literalIndex + MaxSteps; pos++)
        {
            var ins = instructions[pos];
            if (ins.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch
                or FlowControl.Return or FlowControl.Throw or FlowControl.Break)
                return null;
            string name = ins.OpCode.Name;
            if (name == "nop") continue;
            if (name == "dup")
            {
                if (!Push(stack.Count > 0 ? stack[^1] : Tag.Unknown))
                    return null;
                continue;
            }
            if (name == "pop") { Pop(); continue; }
            if (name.StartsWith("stloc", StringComparison.Ordinal))
            {
                int? i = Local(ins);
                if (i is null || i < 0 || i > 255) return null;
                locals[i.Value] = Pop();
                continue;
            }
            if (name.StartsWith("ldloca", StringComparison.Ordinal))
            {
                if (!Push(Tag.Unknown)) return null;
                continue;
            }
            if (name.StartsWith("ldloc", StringComparison.Ordinal))
            {
                int? i = Local(ins);
                if (i is null || i < 0 || i > 255) return null;
                if (!Push(locals.GetValueOrDefault(i.Value, Tag.Unknown)))
                    return null;
                continue;
            }
            if (name.StartsWith("ldarg", StringComparison.Ordinal)
                || name.StartsWith("ldc.", StringComparison.Ordinal)
                || name is "ldnull" or "ldsfld" or "ldsflda" or "ldstr"
                    or "ldtoken" or "ldftn" or "sizeof")
            {
                Tag origin = name.StartsWith("ldarg", StringComparison.Ordinal)
                    ? Tag.MethodArgument
                    : name.StartsWith("ldc.", StringComparison.Ordinal)
                        ? Tag.NumericLiteral
                        : name == "ldsfld" ? Tag.StaticFieldLoad
                        : name == "ldnull" ? Tag.NullLiteral
                        : name == "ldstr" ? Tag.OtherString : Tag.Unknown;
                if (!Push(origin)) return null;
                continue;
            }
            if (name is "ldfld" or "ldflda")
            {
                Pop();
                TraceValue value = name == "ldfld" &&
                    ins.Operand is FieldReference field
                        ? new TraceValue(Tag.InstanceFieldLoad,field)
                        : Tag.Unknown;
                if (!Push(value)) return null;
                continue;
            }
            if (name is "stfld")
            {
                Pop(); Pop(); continue;
            }
            if (name is "stsfld") { Pop(); continue; }
            if (name is "newarr" or "ldlen" or "box" or "castclass"
                or "unbox.any")
            {
                Pop();
                if (!Push(Tag.Unknown)) return null;
                continue;
            }
            if (name.StartsWith("conv.", StringComparison.Ordinal))
            {
                Pop();
                if (!Push(Tag.Unknown)) return null;
                continue;
            }
            if (name.StartsWith("ldelem", StringComparison.Ordinal))
            {
                Pop(); Pop();
                if (!Push(Tag.Unknown)) return null;
                continue;
            }
            if (name.StartsWith("stelem", StringComparison.Ordinal))
            {
                Pop(); Pop(); Pop(); continue;
            }
            if (ins.OpCode.Code is Code.Call or Code.Callvirt or Code.Newobj)
            {
                if (ins.Operand is not MethodReference method ||
                    method.Parameters.Count > 32)
                    return null;
                var formals = new TraceValue[method.Parameters.Count];
                for (int k = formals.Length - 1; k >= 0; k--)
                    formals[k] = Pop();
                TraceValue receiver = (ins.OpCode.Code != Code.Newobj && method.HasThis)
                    ? Pop() : Tag.Unknown;
                if (method.Parameters.Count >= 2 &&
                    ins.OpCode.Code != Code.Newobj)
                {
                    string? family = Program.SetterKind(
                        method.DeclaringType.FullName, method.Name,
                        method.Parameters[0].ParameterType.FullName,
                        method.Parameters[1].ParameterType.FullName);
                    if (family is not null)
                    {
                        string firstType = method.Parameters[0].ParameterType.FullName;
                        if (firstType == "System.String" &&
                            formals[0].Kind == Tag.SourceString)
                            return Matched(family, "source_literal_as_string",
                                           formals[1], receiver);
                        if (firstType == "System.Int32" &&
                            formals[0].Kind == Tag.SourcePropertyId)
                            return Matched(family, "source_literal_via_PropertyToID",
                                           formals[1], receiver);
                    }
                }
                if (ins.OpCode.Code == Code.Newobj)
                {
                    newobjCount++;
                    // Source-symbol-free classification only. Multiple newobj
                    // operations in this slice make value attribution ambiguous.
                    if (newobjCount == 1 &&
                        method.DeclaringType.FullName == "UnityEngine.Vector4" &&
                        method.Name == ".ctor" && method.HasThis)
                    {
                        typedVector4CtorSeen = true;
                        typedVector4CtorFormals = method.Parameters.Count;
                        typedVector4CtorFloats = method.Parameters.Count(x =>
                            x.ParameterType.FullName == "System.Single");
                        foreach (TraceValue input in formals)
                        {
                            string category = Origin(input.Kind);
                            uniqueCtorOrigins[category] =
                                uniqueCtorOrigins.GetValueOrDefault(category) + 1;
                            if (input.Kind == Tag.InstanceFieldLoad &&
                                input.Field is FieldReference field)
                                uniqueCtorFields.Add(field);
                        }
                    }
                }
                Tag result = ins.OpCode.Code == Code.Newobj
                    ? Tag.ConstructedInstance : Tag.CallReturn;
                if (ins.OpCode.Code != Code.Newobj &&
                    method.DeclaringType.FullName == "UnityEngine.Shader" &&
                    method.Name == "PropertyToID" &&
                    method.Parameters.Count == 1 &&
                    method.Parameters[0].ParameterType.FullName == "System.String" &&
                    method.ReturnType.FullName == "System.Int32" &&
                    formals[0].Kind == Tag.SourceString)
                    result = Tag.SourcePropertyId;
                if (ins.OpCode.Code == Code.Newobj ||
                    method.ReturnType.FullName != "System.Void")
                {
                    if (!Push(result)) return null;
                }
                continue;
            }
            // No assumptions about unsupported opcode stack behavior.
            return null;
        }
        return null;
    }

    internal static void SelfTest()
    {
        using var module = ModuleDefinition.CreateModule("t2-cb0-public-fixture",
                                                         ModuleKind.Dll);
        var material = new TypeReference("UnityEngine","Material",module,module);
        var shader = new TypeReference("UnityEngine","Shader",module,module);
        var vector4 = new TypeReference("UnityEngine","Vector4",module,module);
        var setter = new MethodReference("SetVector",module.TypeSystem.Void,material)
            { HasThis = true };
        setter.Parameters.Add(new ParameterDefinition(module.TypeSystem.String));
        setter.Parameters.Add(new ParameterDefinition(vector4));
        var direct = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        var directEvidence = Trace(direct,0);
        if (directEvidence?.Kind != "source_literal_as_string" ||
            directEvidence?.SecondVectorValueOrigin != "method_argument_load" ||
            directEvidence?.MaterialReceiverOrigin != "pre_literal_unknown")
            throw new InvalidOperationException("Exact first formal and numeric-typed origin positive");
        var distractor = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Pop),
            Instruction.Create(OpCodes.Ldstr,"UNRELATED"),
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        if (Trace(distractor,0) is not null)
            throw new InvalidOperationException("Proximity false-positive control");
        var branch = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Br_S,Instruction.Create(OpCodes.Nop)),
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        if (Trace(branch,0) is not null)
            throw new InvalidOperationException("Branch must block first formal proof");
        var propertyId = new MethodReference("PropertyToID",module.TypeSystem.Int32,shader)
            { HasThis = false };
        propertyId.Parameters.Add(new ParameterDefinition(module.TypeSystem.String));
        var setFloat = new MethodReference("SetFloat",module.TypeSystem.Void,material)
            { HasThis = true };
        setFloat.Parameters.Add(new ParameterDefinition(module.TypeSystem.Int32));
        setFloat.Parameters.Add(new ParameterDefinition(module.TypeSystem.Single));
        var ids = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Call,propertyId),
            Instruction.Create(OpCodes.Ldc_R4,1.0f),
            Instruction.Create(OpCodes.Callvirt,setFloat)
        };
        var propertyEvidence = Trace(ids,0);
        if (propertyEvidence?.Kind != "source_literal_via_PropertyToID" ||
            propertyEvidence?.SecondVectorValueOrigin != "numeric_literal" ||
            propertyEvidence?.MaterialReceiverOrigin != "pre_literal_unknown")
            throw new InvalidOperationException("PropertyToID first formal positive");
        var owner = new TypeReference("PublicFixture", "Owner", module, module);
        var field = new FieldReference("publicValue", vector4, owner);
        var fieldOrigin = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr, "PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldfld, field),
            Instruction.Create(OpCodes.Callvirt, setter)
        };
        if (Trace(fieldOrigin,0)?.SecondVectorValueOrigin != "instance_field_load")
            throw new InvalidOperationException("Exact second operand field origin");
        var getValue = new MethodReference("PublicGetValue", vector4, owner)
            { HasThis = false };
        var callOrigin = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Call,getValue),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        if (Trace(callOrigin,0)?.SecondVectorValueOrigin != "call_return")
            throw new InvalidOperationException("Exact second operand call result");
        // A receiver loaded before the name cannot be reconstructed from a
        // forward-only slice; the local bridge can demonstrate the distinction.
        var local = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Stloc_0),
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldloc_0),
            Instruction.Create(OpCodes.Ldarg_1),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        var localEvidence=Trace(local,0);
        if (localEvidence?.Kind != "source_literal_as_string" ||
            localEvidence?.SecondVectorValueOrigin != "method_argument_load" ||
            localEvidence?.MaterialReceiverOrigin != "method_argument_load")
            throw new InvalidOperationException("Exact receiver after local name bridge");
        var unsupported = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Add),
            Instruction.Create(OpCodes.Ldarg_1),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        if (Trace(unsupported,0) is not null)
            throw new InvalidOperationException("Unknown IL must not imply origins");
        var ctor = new MethodReference(".ctor", module.TypeSystem.Void, vector4)
            { HasThis = true };
        for (int n=0;n<4;n++)
            ctor.Parameters.Add(new ParameterDefinition(module.TypeSystem.Single));
        var vectorCtor = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr, "PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Ldc_R4,1f),
            Instruction.Create(OpCodes.Ldc_R4,2f),
            Instruction.Create(OpCodes.Ldc_R4,3f),
            Instruction.Create(OpCodes.Ldc_R4,4f),
            Instruction.Create(OpCodes.Newobj,ctor),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        var verifiedVectorCtor = Trace(vectorCtor,0);
        if (verifiedVectorCtor?.UniqueVector4ConstructorStatus !=
                "one_typed_UnityEngine_Vector4_ctor_in_slice" ||
            verifiedVectorCtor?.UniqueVector4ConstructorParameterCount != 4 ||
            verifiedVectorCtor?.UniqueVector4ConstructorFloatFormalCount != 4 ||
            !verifiedVectorCtor.Value.UniqueVector4ConstructorInputOriginCounts
                .TryGetValue("numeric_literal", out int literalCount) ||
            literalCount != 4)
            throw new InvalidOperationException("Typed Vector4 ctor with scalar origins");
        var nonVectorCtor = new MethodReference(".ctor", module.TypeSystem.Void, owner)
            { HasThis = true };
        for (int n=0;n<4;n++)
            nonVectorCtor.Parameters.Add(new ParameterDefinition(module.TypeSystem.Single));
        var rejectedCtor = vectorCtor.Select(x => x).ToList();
        rejectedCtor[5] = Instruction.Create(OpCodes.Newobj,nonVectorCtor);
        if (Trace(rejectedCtor,0)?.UniqueVector4ConstructorStatus !=
            "not_uniquely_proven")
            throw new InvalidOperationException("Wrong ctor type must not prove Vector4");
        var twoConstructors = new List<Instruction> {
            Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME"),
            Instruction.Create(OpCodes.Ldc_R4,5f),
            Instruction.Create(OpCodes.Ldc_R4,6f),
            Instruction.Create(OpCodes.Ldc_R4,7f),
            Instruction.Create(OpCodes.Ldc_R4,8f),
            Instruction.Create(OpCodes.Newobj,nonVectorCtor),
            Instruction.Create(OpCodes.Pop),
            Instruction.Create(OpCodes.Ldc_R4,1f),
            Instruction.Create(OpCodes.Ldc_R4,2f),
            Instruction.Create(OpCodes.Ldc_R4,3f),
            Instruction.Create(OpCodes.Ldc_R4,4f),
            Instruction.Create(OpCodes.Newobj,ctor),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        if (Trace(twoConstructors,0)?.UniqueVector4ConstructorStatus !=
            "not_uniquely_proven")
            throw new InvalidOperationException("Multiple newobj sources are ambiguous");
        var sourceOwner = new TypeReference("PublicFixture","WaterOwner",module,module);
        var publicMaterialField = new FieldReference("publicMaterial",material,sourceOwner);
        var firstField = new FieldReference("publicFirst",module.TypeSystem.Single,sourceOwner);
        var secondField = new FieldReference("publicSecond",module.TypeSystem.Single,sourceOwner);
        var thirdField = new FieldReference("publicThird",module.TypeSystem.Single,sourceOwner);
        var sourceName = Instruction.Create(OpCodes.Ldstr,"PUBLIC_SOURCE_NAME");
        var exactFieldsWithPrefix = new List<Instruction> {
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldfld,publicMaterialField),
            sourceName,
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldfld,firstField),
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldfld,secondField),
            Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Ldfld,thirdField),
            Instruction.Create(OpCodes.Ldc_R4,1f),
            Instruction.Create(OpCodes.Newobj,ctor),
            Instruction.Create(OpCodes.Callvirt,setter)
        };
        var exactFieldEvidence=Trace(exactFieldsWithPrefix,2);
        if (exactFieldEvidence?.UniqueVector4ConstructorExactInputFieldCount != 3 ||
            exactFieldEvidence?.UniqueVector4ConstructorInputSystemSingleFieldCount != 3 ||
            exactFieldEvidence?.UniqueVector4ConstructorDistinctInputFieldCount != 3 ||
            exactFieldEvidence?.UniqueVector4ConstructorDistinctDeclaringTypeCount != 1 ||
            exactFieldEvidence?.PrivateCtorInputFieldIds.Count != 3 ||
            exactFieldEvidence?.StrictMaterialReceiverImmediatePrefixOrigin !=
                "direct_adjacent_typed_Material_field_load")
            throw new InvalidOperationException("Typed original Vector4 field ids and receiver prefix");
        var wrongMaterialField = new FieldReference("otherObject",module.TypeSystem.Object,sourceOwner);
        var wrongPrefix = new List<Instruction>(exactFieldsWithPrefix);
        wrongPrefix[1] = Instruction.Create(OpCodes.Ldfld, wrongMaterialField);
        if (Trace(wrongPrefix,2)?.StrictMaterialReceiverImmediatePrefixOrigin !=
            "pre_literal_unproven")
            throw new InvalidOperationException("Untyped preliteral field receiver rejected");
        var branchedPrefix = new List<Instruction>(exactFieldsWithPrefix);
        branchedPrefix.Insert(0,Instruction.Create(OpCodes.Br_S,sourceName));
        if (Trace(branchedPrefix,3)?.StrictMaterialReceiverImmediatePrefixOrigin !=
            "pre_literal_alternate_entry")
            throw new InvalidOperationException("Branch into ldstr invalidates immediate receiver");
    }
}
