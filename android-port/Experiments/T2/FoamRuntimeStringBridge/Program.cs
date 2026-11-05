// T2 source-authentic original Raft Foam shader name -> managed ldstr context.
// Mono.Cecil IL is inspected only in a disposable runner. It never executes
// Assembly-CSharp.dll, publishes method/class names or outputs IL/source text.
// Same-method setter occurrence is NOT a proven operand/dataflow binding.
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const string OriginalSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";
    private const int OriginalBytes = 3211776;

    private static string Sha(string text) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();

    private static HashSet<string> ReadDigests(JsonElement root, string key, int expected)
    {
        var node = root.GetProperty(key);
        if (node.ValueKind != JsonValueKind.Array || node.GetArrayLength() != expected)
            throw new InvalidDataException("Unexpected source-authentic target count");
        var hashes = new HashSet<string>(StringComparer.Ordinal);
        foreach (var value in node.EnumerateArray())
        {
            string? digest = value.GetString();
            if (digest is null || digest.Length != 64 ||
                digest.Any(ch => !("0123456789abcdef".Contains(ch))))
                throw new InvalidDataException("Invalid ephemeral SHA-256 shape");
            if (!hashes.Add(digest))
                throw new InvalidDataException("Duplicate private source-name digest");
        }
        return hashes;
    }

    private static IEnumerable<TypeDefinition> WalkTypes(IEnumerable<TypeDefinition> input)
    {
        foreach (var type in input)
        {
            yield return type;
            foreach (var nested in WalkTypes(type.NestedTypes))
                yield return nested;
        }
    }

    private static bool IsPropertyToId(Instruction instruction)
    {
        if (instruction.OpCode.Code is not (Code.Call or Code.Callvirt) ||
            instruction.Operand is not MethodReference callee)
            return false;
        return callee.DeclaringType.FullName == "UnityEngine.Shader" &&
               callee.Name == "PropertyToID" &&
               callee.Parameters.Count == 1 &&
               callee.Parameters[0].ParameterType.FullName == "System.String";
    }

    internal static string? SetterClass(Instruction instruction)
    {
        if (instruction.OpCode.Code is not (Code.Call or Code.Callvirt) ||
            instruction.Operand is not MethodReference callee)
            return null;
        string type = callee.DeclaringType.FullName;
        string name = callee.Name;
        if (type == "UnityEngine.Shader" && name == "SetGlobalTexture")
            return "shader_global_texture";
        if (type == "UnityEngine.Material" && name == "SetTexture")
            return "material_texture";
        if (type == "UnityEngine.MaterialPropertyBlock" && name == "SetTexture")
            return "material_propertyblock_texture";
        if (type == "UnityEngine.Rendering.CommandBuffer" && name == "SetGlobalTexture")
            return "commandbuffer_global_texture";
        if (type == "UnityEngine.ComputeShader" && name == "SetTexture")
            return "compute_shader_texture";
        return null;
    }

    private static string PrivateOriginalProducerParamTypeCategory(TypeReference type,
                                                                    ModuleDefinition owner)
    {
        string n=type.FullName;
        if (n=="System.String") return "system_string";
        if (n=="System.Int32") return "system_int32";
        if (n=="System.Single") return "system_float32";
        if (n=="System.Boolean") return "system_bool";
        if (n=="UnityEngine.Texture") return "unity_texture";
        if (n=="UnityEngine.RenderTexture") return "unity_rendertexture";
        if (type.Namespace=="UnityEngine" ||
            type.Namespace.StartsWith("UnityEngine.",StringComparison.Ordinal))
            return "unity_other_type";
        if (type.Scope==owner || type.Module==owner ||
            type.Scope?.Name=="Assembly-CSharp")
            return "original_managed_declared_type";
        return "other_external_or_unresolved_type";
    }

    private sealed class Summary
    {
        public int MethodCount;
        public int InstructionCount;
        public int LiteralCount;
        public int SourceHashMatchedNonAuthoredOccurrences;
        public int SourceHashMatchedAuthoredOccurrences;
        public readonly HashSet<string> MatchedNonAuthored = new(StringComparer.Ordinal);
        public readonly HashSet<string> MatchedAuthored = new(StringComparer.Ordinal);
        public readonly HashSet<string> MethodsWithNonAuthored = new(StringComparer.Ordinal);
        public readonly HashSet<string> MethodsWithAuthored = new(StringComparer.Ordinal);
        public int MethodsWithNonAuthoredAndSetter;
        public int MethodsWithAuthoredAndSetter;
        public int NonAuthoredLiteralAdjacentPropertyToId;
        public int AuthoredLiteralAdjacentPropertyToId;
        public int NonAuthoredLiteralWithSetterWithin8Instructions;
        public readonly HashSet<string> NonAuthoredExactSetterArgumentNames = new(StringComparer.Ordinal);
        public readonly HashSet<string> AuthoredExactSetterArgumentNames = new(StringComparer.Ordinal);
        public int NonAuthoredExactSetterLiteralUses;
        public int AuthoredExactSetterLiteralUses;
        public int NonAuthoredExactMaterialSetTextureNameArgs;
        public int NonAuthoredExactMaterialPropertyBlockSetTextureNameArgs;
        public int NonAuthoredExactNameViaPropertyToId;
        public int NonAuthoredExactNameViaDirectString;
        public readonly Dictionary<string,int> NonAuthoredExactSecondOriginCounts =
            new(StringComparer.Ordinal);
        public int NonAuthoredExactSecondDeclaredUnityTexture;
        public readonly Dictionary<string,int> SecondProducerDeclaredReturnTypes = new(StringComparer.Ordinal);
        public readonly Dictionary<string,int> SecondProducerDeclaringKinds = new(StringComparer.Ordinal);
        public int SecondProducerStaticCallCount;
        public int SecondProducerInstanceCallCount;
        public int SecondProducerCallvirtCount;
        public int SecondProducerReturnKnownUnityTextureTypeCount;
        public readonly Dictionary<int,int> SecondProducerParameterCount = new();
        public readonly Dictionary<string,int> SecondProducerParameterTypeCategories =
            new(StringComparer.Ordinal);
        public readonly Dictionary<string,int> SecondProducerActualIndexInt32Origins =
            new(StringComparer.Ordinal);
        // Original small-domain indices remain private to this running process.
        // Never serialize this list or hash its contents into a public report.
        public readonly List<int> PrivateExactFourI4Values = new();
        public readonly HashSet<string> SecondProducerDistinctPrivateSignatures =
            new(StringComparer.Ordinal);
        public int SecondProducerExactManagedMethodDefinitionMatches;
        public int SecondProducerExactManagedBodyMatches;
        public int SecondProducerAmbiguousOrMissingMethodDefinitions;
        public FoamProducerBody.SafeProfile? OriginalSingleProducerBodyProfile;
        public FoamFieldWriterLineage.SafeProfile? OriginalFieldWriterProfile;
        public FoamFieldSerializationMetadata.SafeProfile? OriginalFieldSerializationProfile;
        public FoamFieldReadTopology.SafeProfile? OriginalFieldReadTopologyProfile;
        public FoamFieldAddressConsumer.SafeProfile? OriginalAddressConsumerProfile;
        public FoamByrefTargetBody.SafeProfile? OriginalByrefTargetBodyProfile;
        public FoamByrefAllocationFlow.SafeProfile? OriginalByrefAllocationFlowProfile;
        public FoamByrefArrayBounds.SafeProfile? OriginalByrefArrayBoundsProfile;
        public FoamByrefLengthOrigin.SafeProfile? OriginalByrefLengthOriginProfile;
        public FoamByrefActualCallerLength.SafeProfile? OriginalByrefCallerLengthProfile;
        public FoamByrefElementValueOrigin.SafeProfile? OriginalElementValueOriginProfile;
        public readonly Dictionary<string,int> TotalSetterCalls = new(StringComparer.Ordinal)
        {
            ["shader_global_texture"] = 0,
            ["material_texture"] = 0,
            ["material_propertyblock_texture"] = 0,
            ["commandbuffer_global_texture"] = 0,
            ["compute_shader_texture"] = 0
        };
        public readonly Dictionary<string,int> MatchedNonAuthoredSameMethodSetter = new(StringComparer.Ordinal)
        {
            ["shader_global_texture"] = 0,
            ["material_texture"] = 0,
            ["material_propertyblock_texture"] = 0,
            ["commandbuffer_global_texture"] = 0,
            ["compute_shader_texture"] = 0
        };
    }

    private static Summary Scan(IEnumerable<MethodDefinition> methods,
                                HashSet<string> nonAuthored,
                                HashSet<string> authored)
    {
        var result = new Summary();
        var sourceMethods=methods.ToList();
        FieldReference? exactGetterBackingField=null;
        MethodDefinition? exactOriginalTextureGetter=null;
        // Comparison is entirely private and all original method names remain
        // in CI memory. Only aggregate match cardinalities leave the runner.
        var definitions=sourceMethods.GroupBy(m=>m.FullName,StringComparer.Ordinal)
                                     .ToDictionary(g=>g.Key,g=>g.ToList(),StringComparer.Ordinal);
        foreach (var method in sourceMethods)
        {
            if (!method.HasBody)
                continue;
            var body = method.Body.Instructions;
            result.MethodCount++;
            result.InstructionCount += body.Count;
            if (result.MethodCount > 100000 || result.InstructionCount > 10000000)
                throw new InvalidDataException("Original compiled managed code budget exceeded");
            var setters = new HashSet<string>(StringComparer.Ordinal);
            bool containsNon = false, containsAuthor = false;
            int methodNonCount = 0;
            var literalTargets = new List<(int Index, bool Non)>();
            for (int i = 0; i < body.Count; i++)
            {
                string? setter = SetterClass(body[i]);
                if (setter is not null)
                {
                    result.TotalSetterCalls[setter]++;
                    setters.Add(setter);
                }
                if (body[i].OpCode.Code != Code.Ldstr)
                    continue;
                result.LiteralCount++;
                if (body[i].Operand is not string literal)
                    throw new InvalidDataException("Invalid original IL ldstr operand");
                var digest = Sha(literal);
                bool isNon = nonAuthored.Contains(digest);
                bool isAuthor = authored.Contains(digest);
                if (isNon && isAuthor)
                    throw new InvalidDataException("Original source property digest ambiguous");
                if (isNon)
                {
                    result.SourceHashMatchedNonAuthoredOccurrences++;
                    result.MatchedNonAuthored.Add(digest);
                    containsNon = true;
                    methodNonCount++;
                    literalTargets.Add((i,true));
                }
                else if (isAuthor)
                {
                    result.SourceHashMatchedAuthoredOccurrences++;
                    result.MatchedAuthored.Add(digest);
                    containsAuthor = true;
                    literalTargets.Add((i,false));
                }
            }
            if (containsNon)
                result.MethodsWithNonAuthored.Add(method.MetadataToken.ToInt32().ToString());
            if (containsAuthor)
                result.MethodsWithAuthored.Add(method.MetadataToken.ToInt32().ToString());
            if (containsNon && setters.Count > 0)
            {
                result.MethodsWithNonAuthoredAndSetter++;
                foreach (string kind in setters)
                    result.MatchedNonAuthoredSameMethodSetter[kind]++;
            }
            if (containsAuthor && setters.Count > 0)
                result.MethodsWithAuthoredAndSetter++;
            foreach ((int idx, bool non) in literalTargets)
            {
                // An exact first formal name argument follows the actual IL
                // evaluation-stack and local tags, not just an eight-opcode
                // window or same-method setter count. Only bounded flow counts.
                var exact=FoamSetterFlow.Trace(method,idx);
                if (exact is not null)
                {
                    string? sourceLiteral=body[idx].Operand as string;
                    if (sourceLiteral is null)
                        throw new InvalidDataException("Original named source IL literal changed");
                    if (non)
                    {
                        result.NonAuthoredExactSetterLiteralUses++;
                        result.NonAuthoredExactSetterArgumentNames.Add(Sha(sourceLiteral));
                        var origin = exact.Value.SecondTextureOperandOrigin;
                        result.NonAuthoredExactSecondOriginCounts[origin] =
                            result.NonAuthoredExactSecondOriginCounts.GetValueOrDefault(origin) + 1;
                        if (exact.Value.SecondFormalParameterIsUnityTexture)
                            result.NonAuthoredExactSecondDeclaredUnityTexture++;
                        var rt=exact.Value.SecondProducerDeclaredReturnClass;
                        var owner=exact.Value.SecondProducerDeclaringTypeClass;
                        result.SecondProducerDeclaredReturnTypes[rt] =
                            result.SecondProducerDeclaredReturnTypes.GetValueOrDefault(rt)+1;
                        result.SecondProducerDeclaringKinds[owner] =
                            result.SecondProducerDeclaringKinds.GetValueOrDefault(owner)+1;
                        if (exact.Value.SecondProducerHasThis)
                            result.SecondProducerInstanceCallCount++;
                        else
                            result.SecondProducerStaticCallCount++;
                        if (exact.Value.SecondProducerIsCallvirt)
                            result.SecondProducerCallvirtCount++;
                        if (rt is "unity_texture" or "unity_texture2d" or "unity_rendertexture" or
                            "unity_texture3d" or "unity_cubemap" or "unity_texture2darray")
                            result.SecondProducerReturnKnownUnityTextureTypeCount++;
                        var argc=exact.Value.SecondProducerParameterCount;
                        result.SecondProducerParameterCount[argc] =
                            result.SecondProducerParameterCount.GetValueOrDefault(argc)+1;
                        var indexOrigin=exact.Value.SecondProducerIndexInt32ArgumentOrigin;
                        result.SecondProducerActualIndexInt32Origins[indexOrigin]=
                            result.SecondProducerActualIndexInt32Origins.GetValueOrDefault(indexOrigin)+1;
                        if (indexOrigin=="direct_ldc_i4_literal")
                        {
                            if (exact.Value.SecondProducerIndexInt32ArgumentLiteral is not int literal)
                                throw new InvalidDataException("Exact int32 source marker missing typed numeric operand");
                            result.PrivateExactFourI4Values.Add(literal);
                        }
                        else if (exact.Value.SecondProducerIndexInt32ArgumentLiteral is not null)
                            throw new InvalidDataException("Nonliteral index source cannot carry exact numeric value");
                        var producer=exact.Value.SecondProducerReference;
                        if (producer is not null)
                        {
                            var signature=producer.FullName;
                            result.SecondProducerDistinctPrivateSignatures.Add(signature);
                            foreach (var param in producer.Parameters)
                            {
                                var kind=PrivateOriginalProducerParamTypeCategory(
                                    param.ParameterType,method.Module);
                                result.SecondProducerParameterTypeCategories[kind] =
                                    result.SecondProducerParameterTypeCategories.GetValueOrDefault(kind)+1;
                            }
                            if (definitions.TryGetValue(signature,out var candidates)
                                && candidates.Count==1
                                && candidates[0].DeclaringType.FullName==producer.DeclaringType.FullName
                                && candidates[0].ReturnType.FullName==producer.ReturnType.FullName
                                && candidates[0].Parameters.Count==producer.Parameters.Count
                                && candidates[0].HasThis==producer.HasThis
                                && candidates[0].Parameters.Zip(producer.Parameters,
                                    (a,b)=>a.ParameterType.FullName==b.ParameterType.FullName).All(x=>x))
                            {
                                result.SecondProducerExactManagedMethodDefinitionMatches++;
                                if (candidates[0].HasBody &&
                                    candidates[0].Body.Instructions.Count>0)
                                {
                                    result.SecondProducerExactManagedBodyMatches++;
                                    if (candidates[0].HasThis &&
                                        candidates[0].Parameters.Count==1 &&
                                        candidates[0].Parameters[0].ParameterType.FullName=="System.Int32" &&
                                        candidates[0].ReturnType.FullName=="UnityEngine.Texture")
                                    {
                                        // All four source names resolve one SHA-original
                                        // producer signature. Inspect that one body
                                        // once; a repeated dictionary-valued record
                                        // is not compared by object identity.
                                        if (result.OriginalSingleProducerBodyProfile is null)
                                        {
                                            result.OriginalSingleProducerBodyProfile=
                                                FoamProducerBody.Inspect(candidates[0]);
                                            exactGetterBackingField=
                                                FoamFieldWriterLineage.ExactGetterBackingField(candidates[0]);
                                            exactOriginalTextureGetter=candidates[0];
                                        }
                                    }
                                }
                            }
                            else
                                result.SecondProducerAmbiguousOrMissingMethodDefinitions++;
                        }
                        else if (origin=="call_return")
                            result.SecondProducerAmbiguousOrMissingMethodDefinitions++;
                        if (exact.Value.SetterKind=="material_texture")
                            result.NonAuthoredExactMaterialSetTextureNameArgs++;
                        if (exact.Value.SetterKind=="material_propertyblock_texture")
                            result.NonAuthoredExactMaterialPropertyBlockSetTextureNameArgs++;
                        if (exact.Value.FirstArgRole=="property_id")
                            result.NonAuthoredExactNameViaPropertyToId++;
                        else if (exact.Value.FirstArgRole=="string")
                            result.NonAuthoredExactNameViaDirectString++;
                    }
                    else
                    {
                        result.AuthoredExactSetterLiteralUses++;
                        result.AuthoredExactSetterArgumentNames.Add(Sha(sourceLiteral));
                    }
                }
                // Adjacent means the exact next IL instruction, not a guess
                // that the string reached a later SetTexture argument.
                if (idx + 1 < body.Count && IsPropertyToId(body[idx + 1]))
                {
                    if (non) result.NonAuthoredLiteralAdjacentPropertyToId++;
                    else result.AuthoredLiteralAdjacentPropertyToId++;
                }
                if (!non)
                    continue;
                for (int step = 1; step <= 8 && idx + step < body.Count; step++)
                {
                    if (SetterClass(body[idx + step]) is not null)
                    {
                        result.NonAuthoredLiteralWithSetterWithin8Instructions++;
                        break;
                    }
                }
            }
        }
        if (exactGetterBackingField is not null)
        {
            result.OriginalFieldWriterProfile=
                FoamFieldWriterLineage.Scan(sourceMethods,exactGetterBackingField);
            if (exactOriginalTextureGetter is null)
                throw new InvalidDataException("Missing exact SHA-original texture getter");
            result.OriginalFieldReadTopologyProfile=
                FoamFieldReadTopology.Scan(sourceMethods,exactGetterBackingField,
                    exactOriginalTextureGetter);
            var exactByrefRecipients=new List<MethodReference>();
            var exactByrefCalls=new List<(MethodDefinition Owner,Instruction Address,
                Instruction Call,MethodReference Recipient,int RefFormal)>();
            result.OriginalAddressConsumerProfile=
                FoamFieldAddressConsumer.Scan(sourceMethods,exactGetterBackingField,
                    recipient=>exactByrefRecipients.Add(recipient),
                    (owner,address,call,recipient,refFormal)=>
                        exactByrefCalls.Add((owner,address,call,recipient,refFormal)));
            if (exactByrefCalls.Count!=1)
                throw new InvalidDataException("Actual original byref callsite count not one");
            if (exactByrefRecipients.Count!=1)
                throw new InvalidDataException("Original exact field byref target count not one");
            result.OriginalByrefTargetBodyProfile=
                FoamByrefTargetBody.Inspect(sourceMethods,exactByrefRecipients[0]);
            result.OriginalByrefAllocationFlowProfile=
                FoamByrefAllocationFlow.Inspect(sourceMethods,exactByrefRecipients[0]);
            result.OriginalElementValueOriginProfile=
                FoamByrefElementValueOrigin.Inspect(sourceMethods,
                    exactByrefRecipients[0],result.OriginalByrefAllocationFlowProfile);
            result.OriginalByrefArrayBoundsProfile=
                FoamByrefArrayBounds.Inspect(sourceMethods,exactByrefRecipients[0],
                    result.OriginalByrefAllocationFlowProfile,
                    result.PrivateExactFourI4Values);
            result.OriginalByrefLengthOriginProfile=
                FoamByrefLengthOrigin.Inspect(sourceMethods,exactByrefRecipients[0],
                    result.OriginalByrefAllocationFlowProfile,
                    result.PrivateExactFourI4Values);
            var originalCall=exactByrefCalls[0];
            result.OriginalByrefCallerLengthProfile=
                FoamByrefActualCallerLength.Inspect(sourceMethods,
                    originalCall.Owner,originalCall.Address,originalCall.Call,
                    originalCall.Recipient,originalCall.RefFormal,
                    result.OriginalByrefLengthOriginProfile,
                    result.PrivateExactFourI4Values);
            // Resolve the exact original FieldDefinition without publishing
            // private type, token or field identifiers.
            var sourceTypes=sourceMethods.Count==0
                ? Enumerable.Empty<TypeDefinition>()
                : WalkTypes(sourceMethods[0].Module.Types);
            result.OriginalFieldSerializationProfile=
                FoamFieldSerializationMetadata.Inspect(sourceTypes,exactGetterBackingField);
        }
        return result;
    }

    private static object PublicReport(Summary result, bool exactOriginalDll, bool selftest)
    {
        return new
        {
            status = selftest ? "synthetic_cecil_source_literal_controls_passed" :
                "original_foam_compiled_managed_literal_contexts_scanned",
            source_kind = selftest ? "synthetic_public_IL_fixture" : "SHA_PINNED_ORIGINAL_MANAGED_ASSEMBLY_CSHARP",
            original_dll_sha256_authenticated = exactOriginalDll,
            original_dll_size_bytes = exactOriginalDll ? OriginalBytes : 0,
            source_original_non_authored_tex_names = 4,
            source_original_authored_tex_names = 1,
            original_managed_method_bodies_scanned = result.MethodCount,
            original_managed_il_instructions_scanned = result.InstructionCount,
            original_managed_ldstr_instructions_scanned = result.LiteralCount,
            distinct_non_authored_source_names_seen_as_ldstr = result.MatchedNonAuthored.Count,
            distinct_authored_source_names_seen_as_ldstr = result.MatchedAuthored.Count,
            non_authored_source_ldstr_occurrences = result.SourceHashMatchedNonAuthoredOccurrences,
            authored_source_ldstr_occurrences = result.SourceHashMatchedAuthoredOccurrences,
            methods_containing_non_authored_source_literal = result.MethodsWithNonAuthored.Count,
            methods_containing_authored_source_literal = result.MethodsWithAuthored.Count,
            methods_containing_non_authored_literal_and_any_texture_setter = result.MethodsWithNonAuthoredAndSetter,
            methods_containing_authored_literal_and_any_texture_setter = result.MethodsWithAuthoredAndSetter,
            non_authored_source_literal_directly_adjacent_to_shader_propertytoid = result.NonAuthoredLiteralAdjacentPropertyToId,
            authored_source_literal_directly_adjacent_to_shader_propertytoid = result.AuthoredLiteralAdjacentPropertyToId,
            non_authored_literal_with_texture_setter_within_eight_IL_instructions = result.NonAuthoredLiteralWithSetterWithin8Instructions,
            distinct_non_authored_source_names_proven_as_exact_typed_settexture_first_argument = result.NonAuthoredExactSetterArgumentNames.Count,
            distinct_authored_source_names_proven_as_exact_typed_settexture_first_argument = result.AuthoredExactSetterArgumentNames.Count,
            non_authored_exact_name_arg_literal_occurrences = result.NonAuthoredExactSetterLiteralUses,
            authored_exact_name_arg_literal_occurrences = result.AuthoredExactSetterLiteralUses,
            non_authored_exact_settexture_first_args_material = result.NonAuthoredExactMaterialSetTextureNameArgs,
            non_authored_exact_settexture_first_args_material_property_block = result.NonAuthoredExactMaterialPropertyBlockSetTextureNameArgs,
            non_authored_exact_name_via_propertytoid = result.NonAuthoredExactNameViaPropertyToId,
            non_authored_exact_name_via_direct_string = result.NonAuthoredExactNameViaDirectString,
            original_four_non_authored_names_exact_setter_name_arg_proven = result.NonAuthoredExactSetterArgumentNames.Count==4,
            non_authored_exact_second_arg_opcode_origin_histogram = result.NonAuthoredExactSecondOriginCounts,
            non_authored_exact_second_formal_is_UnityEngine_Texture_count = result.NonAuthoredExactSecondDeclaredUnityTexture,
            non_authored_second_exact_producer_return_declared_type_categories = result.SecondProducerDeclaredReturnTypes,
            non_authored_second_exact_producer_declaring_type_categories = result.SecondProducerDeclaringKinds,
            non_authored_second_exact_producer_static_calls = result.SecondProducerStaticCallCount,
            non_authored_second_exact_producer_instance_calls = result.SecondProducerInstanceCallCount,
            non_authored_second_exact_producer_callvirt_calls = result.SecondProducerCallvirtCount,
            non_authored_second_exact_producer_known_Unity_Texture_return_types = result.SecondProducerReturnKnownUnityTextureTypeCount,
            non_authored_second_exact_producer_parameter_count_histogram = result.SecondProducerParameterCount,
            non_authored_second_producer_parameter_declared_type_categories = result.SecondProducerParameterTypeCategories,
            non_authored_second_Texture_int_actual_index_argument_origin_histogram = result.SecondProducerActualIndexInt32Origins,
            non_authored_actual_i4_index_values_decoded_count = result.PrivateExactFourI4Values.Count,
            non_authored_actual_i4_index_values_distinct_count = result.PrivateExactFourI4Values.Distinct().Count(),
            non_authored_actual_i4_index_values_all_nonnegative =
                result.PrivateExactFourI4Values.Count==4 && result.PrivateExactFourI4Values.All(v=>v>=0),
            original_RenderTexture_array_runtime_length_or_element_validity_verified = false,
            private_original_i4_index_values_or_digests_disclosed = false,
            non_authored_second_producer_distinct_compiled_private_method_signatures = result.SecondProducerDistinctPrivateSignatures.Count,
            non_authored_second_producer_compiled_signature_exact_original_method_definition_matches = result.SecondProducerExactManagedMethodDefinitionMatches,
            non_authored_second_producer_exact_original_method_definitions_with_body = result.SecondProducerExactManagedBodyMatches,
            non_authored_second_producer_missing_or_ambiguous_original_definitions = result.SecondProducerAmbiguousOrMissingMethodDefinitions,
            original_exact_Texture_int_producer_body_op_classes = result.OriginalSingleProducerBodyProfile,
            original_exact_Texture_int_backing_field_writer_op_classes = result.OriginalFieldWriterProfile,
            original_exact_RenderTexture_array_field_serialization_metadata = result.OriginalFieldSerializationProfile,
            original_exact_RenderTexture_array_field_managed_read_topology = result.OriginalFieldReadTopologyProfile,
            original_exact_RenderTexture_array_field_address_consumer = result.OriginalAddressConsumerProfile,
            original_exact_RenderTexture_array_byref_target_body_profile = result.OriginalByrefTargetBodyProfile,
            original_exact_RenderTexture_array_byref_target_allocation_flow = result.OriginalByrefAllocationFlowProfile,
            original_exact_RenderTexture_array_byref_compiled_bounds_vs_callers = result.OriginalByrefArrayBoundsProfile,
            original_exact_RenderTexture_array_byref_length_origin_same_block = result.OriginalByrefLengthOriginProfile,
            original_exact_RenderTexture_array_byref_actual_caller_length = result.OriginalByrefCallerLengthProfile,
            original_exact_RenderTexture_array_byref_element_value_source = result.OriginalElementValueOriginProfile,
            original_exact_Texture_int_producer_body_accepted_same_SHA_definition = result.OriginalSingleProducerBodyProfile is not null,
            original_exact_method_definition_is_original_runtime_called_or_output_proof = false,
            producer_declared_signature_is_actual_runtime_texture_object_proof = false,
            second_argument_origin_label_is_actual_texture_instance_proof = false,
            material_receiver_identity_or_runtime_reachability_verified = false,
            original_managed_texture_setter_calls_by_kind = result.TotalSetterCalls,
            non_authored_source_literal_and_setter_same_method_by_kind = result.MatchedNonAuthoredSameMethodSetter,
            same_method_cooccurrence_is_argument_dataflow_proof = false,
            original_foam_texture_runtime_binding_verified = false,
            original_all_managed_assemblies_examined = false,
            original_native_plugin_writer_examined = false,
            authored_shaderlab_unity_import_verified = false,
            android_device_water_pixels_verified = false,
            private_names_hashes_method_names_assembly_or_IL_published = false
        };
    }

    private static int SelfTest()
    {
        using var m = ModuleDefinition.CreateModule("SyntheticPublicTextureLiteral", ModuleKind.Dll);
        var td = new TypeDefinition("Synthetic", "Fixture",
            Mono.Cecil.TypeAttributes.Public | Mono.Cecil.TypeAttributes.Class,
            m.TypeSystem.Object);
        m.Types.Add(td);
        var method = new MethodDefinition("SyntheticProbe",
            Mono.Cecil.MethodAttributes.Public | Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        td.Methods.Add(method);
        var shim = new TypeReference("UnityEngine","Shader",m,m.TypeSystem.Object.Scope);
        var propertyToId = new MethodReference("PropertyToID",m.TypeSystem.Int32,shim);
        propertyToId.Parameters.Add(new ParameterDefinition(m.TypeSystem.String));
        var il = method.Body.GetILProcessor();
        il.Append(il.Create(OpCodes.Ldstr,"public-synthetic-non-authored"));
        il.Append(il.Create(OpCodes.Call,propertyToId));
        il.Append(il.Create(OpCodes.Pop));
        il.Append(il.Create(OpCodes.Ret));
        var non = new HashSet<string>(StringComparer.Ordinal){ Sha("public-synthetic-non-authored") };
        var author = new HashSet<string>(StringComparer.Ordinal){ Sha("public-synthetic-authored") };
        var observed = Scan(new[]{method},non,author);
        if (observed.MatchedNonAuthored.Count != 1 ||
            observed.SourceHashMatchedNonAuthoredOccurrences != 1 ||
            observed.NonAuthoredLiteralAdjacentPropertyToId != 1 ||
            observed.MatchedAuthored.Count != 0 ||
            observed.MethodsWithNonAuthoredAndSetter != 0)
            throw new InvalidDataException("Synthetic exact IL literal-to-PropertyToID fixture failed");
        // Synthetic positive direct Material.SetTexture(string, Texture)
        // and negative same-window coincidence. No game source method names.
        var materialType = new TypeReference("UnityEngine","Material",m,m.TypeSystem.Object.Scope);
        var textureType = new TypeReference("UnityEngine","Texture",m,m.TypeSystem.Object.Scope);
        var setTexture = new MethodReference("SetTexture",m.TypeSystem.Void,materialType)
            { HasThis=true };
        setTexture.Parameters.Add(new ParameterDefinition(m.TypeSystem.String));
        setTexture.Parameters.Add(new ParameterDefinition(textureType));
        var positive = new MethodDefinition("PositivePublicSetTexture",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        positive.Parameters.Add(new ParameterDefinition(m.TypeSystem.Object));
        td.Methods.Add(positive);
        var lip=positive.Body.GetILProcessor();
        lip.Append(lip.Create(OpCodes.Ldarg_0));
        lip.Append(lip.Create(OpCodes.Ldstr,"public-direct-tex-name"));
        lip.Append(lip.Create(OpCodes.Ldnull));
        lip.Append(lip.Create(OpCodes.Callvirt,setTexture));
        lip.Append(lip.Create(OpCodes.Ret));
        var verified=FoamSetterFlow.Trace(positive,1);
        if (verified is null || verified.Value.SetterKind!="material_texture" ||
            verified.Value.FirstArgRole!="string" ||
            verified.Value.SecondTextureOperandOrigin!="null_literal" ||
            !verified.Value.SecondFormalParameterIsUnityTexture)
            throw new InvalidDataException("Direct original marker to SetTexture arg fixture failed");
        // A real field-load marker is not an executed Texture instance proof:
        // it identifies just the static IL opcode family and formal Texture type.
        var field=new FieldDefinition("SyntheticTextureField",
            Mono.Cecil.FieldAttributes.Public | Mono.Cecil.FieldAttributes.Static,textureType);
        td.Fields.Add(field);
        var fieldExample=new MethodDefinition("SyntheticStaticTextureFieldFlow",
            Mono.Cecil.MethodAttributes.Public | Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        fieldExample.Parameters.Add(new ParameterDefinition(materialType));
        td.Methods.Add(fieldExample);
        var lif=fieldExample.Body.GetILProcessor();
        lif.Append(lif.Create(OpCodes.Ldarg_0));
        lif.Append(lif.Create(OpCodes.Ldstr,"public-second-field-name"));
        lif.Append(lif.Create(OpCodes.Ldsfld,field));
        lif.Append(lif.Create(OpCodes.Callvirt,setTexture));
        lif.Append(lif.Create(OpCodes.Ret));
        var fieldTrace=FoamSetterFlow.Trace(fieldExample,1);
        if (fieldTrace is null ||
            fieldTrace.Value.SecondTextureOperandOrigin!="static_field_load" ||
            !fieldTrace.Value.SecondFormalParameterIsUnityTexture)
            throw new InvalidDataException("Static field opcode provenance synthetic fixture failed");
        var argumentExample=new MethodDefinition("SyntheticArgumentTextureFlow",
            Mono.Cecil.MethodAttributes.Public | Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        argumentExample.Parameters.Add(new ParameterDefinition(materialType));
        argumentExample.Parameters.Add(new ParameterDefinition(textureType));
        td.Methods.Add(argumentExample);
        var lia=argumentExample.Body.GetILProcessor();
        lia.Append(lia.Create(OpCodes.Ldarg_0));
        lia.Append(lia.Create(OpCodes.Ldstr,"public-second-arg-name"));
        lia.Append(lia.Create(OpCodes.Ldarg_1));
        lia.Append(lia.Create(OpCodes.Callvirt,setTexture));
        lia.Append(lia.Create(OpCodes.Ret));
        var argTrace=FoamSetterFlow.Trace(argumentExample,1);
        if (argTrace is null || argTrace.Value.SecondTextureOperandOrigin!="argument_load")
            throw new InvalidDataException("Argument opcode provenance synthetic fixture failed");
        // Exactly track the declared return MethodReference behind a call
        // result instead of inferring it from a nearby unrelated IL opcode.
        var publicFactory=new TypeReference("Synthetic","Factory",m,m.TypeSystem.Object.Scope);
        var producerMethod=new MethodReference("PublicSyntheticTextureProducer",
            textureType,publicFactory){HasThis=false};
        var factoryDef=new TypeDefinition("Synthetic","Factory",
            Mono.Cecil.TypeAttributes.Public|Mono.Cecil.TypeAttributes.Class,
            m.TypeSystem.Object);
        m.Types.Add(factoryDef);
        var producerDef=new MethodDefinition("PublicSyntheticTextureProducer",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            textureType);
        factoryDef.Methods.Add(producerDef);
        var producerBody=producerDef.Body.GetILProcessor();
        producerBody.Append(producerBody.Create(OpCodes.Ldnull));
        producerBody.Append(producerBody.Create(OpCodes.Ret));
        var produced=new MethodDefinition("PublicSyntheticProducedTextureFlow",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        produced.Parameters.Add(new ParameterDefinition(materialType));
        td.Methods.Add(produced);
        var liprod=produced.Body.GetILProcessor();
        liprod.Append(liprod.Create(OpCodes.Ldarg_0));
        liprod.Append(liprod.Create(OpCodes.Ldstr,"public-direct-typed-producer"));
        liprod.Append(liprod.Create(OpCodes.Call,producerMethod));
        liprod.Append(liprod.Create(OpCodes.Callvirt,setTexture));
        liprod.Append(liprod.Create(OpCodes.Ret));
        var traced=FoamSetterFlow.Trace(produced,1);
        if (traced is null || traced.Value.SecondTextureOperandOrigin!="call_return" ||
            traced.Value.SecondProducerDeclaredReturnClass!="unity_texture" ||
            traced.Value.SecondProducerDeclaringTypeClass!="original_managed_assembly_declared" ||
            traced.Value.SecondProducerHasThis || traced.Value.SecondProducerIsCallvirt ||
            traced.Value.SecondProducerParameterCount!=0)
            throw new InvalidDataException("Exact typed call producer source fixture failed");

        // Source-free exact producer-int operand origin tests: use the
        // immediate call stack, never infer a guessed original integer.
        var oneIndexMethod=new MethodReference("PublicSyntheticOneIntTexture",
            textureType,publicFactory){HasThis=false};
        oneIndexMethod.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        var literalCall=new MethodDefinition("PublicSyntheticOneIntLiteral",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        literalCall.Parameters.Add(new ParameterDefinition(materialType));
        td.Methods.Add(literalCall);
        var ilLit=literalCall.Body.GetILProcessor();
        ilLit.Append(ilLit.Create(OpCodes.Ldarg_0));
        ilLit.Append(ilLit.Create(OpCodes.Ldstr,"public-synthetic-index-literal"));
        ilLit.Append(ilLit.Create(OpCodes.Ldc_I4_2));
        ilLit.Append(ilLit.Create(OpCodes.Call,oneIndexMethod));
        ilLit.Append(ilLit.Create(OpCodes.Callvirt,setTexture));
        ilLit.Append(ilLit.Create(OpCodes.Ret));
        var literalOrigin=FoamSetterFlow.Trace(literalCall,1);
        if (literalOrigin is null ||
            literalOrigin.Value.SecondProducerIndexInt32ArgumentOrigin!="direct_ldc_i4_literal" ||
            literalOrigin.Value.SecondProducerIndexInt32ArgumentLiteral!=2 ||
            literalOrigin.Value.SecondTextureOperandOrigin!="call_return")
            throw new InvalidDataException("Exact synthetic one-int literal provenance fixture failed");
        var parameterCall=new MethodDefinition("PublicSyntheticOneIntParameter",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        parameterCall.Parameters.Add(new ParameterDefinition(materialType));
        parameterCall.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        td.Methods.Add(parameterCall);
        var ilParam=parameterCall.Body.GetILProcessor();
        ilParam.Append(ilParam.Create(OpCodes.Ldarg_0));
        ilParam.Append(ilParam.Create(OpCodes.Ldstr,"public-synthetic-index-argument"));
        ilParam.Append(ilParam.Create(OpCodes.Ldarg_1));
        ilParam.Append(ilParam.Create(OpCodes.Call,oneIndexMethod));
        ilParam.Append(ilParam.Create(OpCodes.Callvirt,setTexture));
        ilParam.Append(ilParam.Create(OpCodes.Ret));
        var paramOrigin=FoamSetterFlow.Trace(parameterCall,1);
        if (paramOrigin is null ||
            paramOrigin.Value.SecondProducerIndexInt32ArgumentOrigin!="argument_load" ||
            paramOrigin.Value.SecondProducerIndexInt32ArgumentLiteral is not null)
            throw new InvalidDataException("Exact synthetic one-int argument provenance fixture failed");
        var invalidTokenCall=new MethodDefinition("PublicSyntheticTokenIsNotAnIntLiteral",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        invalidTokenCall.Parameters.Add(new ParameterDefinition(materialType));
        td.Methods.Add(invalidTokenCall);
        var ilToken=invalidTokenCall.Body.GetILProcessor();
        ilToken.Append(ilToken.Create(OpCodes.Ldarg_0));
        ilToken.Append(ilToken.Create(OpCodes.Ldstr,"public-synthetic-not-int-literal"));
        ilToken.Append(ilToken.Create(OpCodes.Ldtoken,m.TypeSystem.Int32));
        ilToken.Append(ilToken.Create(OpCodes.Call,oneIndexMethod));
        ilToken.Append(ilToken.Create(OpCodes.Callvirt,setTexture));
        ilToken.Append(ilToken.Create(OpCodes.Ret));
        var tokenOrigin=FoamSetterFlow.Trace(invalidTokenCall,1);
        if (tokenOrigin is null ||
            tokenOrigin.Value.SecondProducerIndexInt32ArgumentOrigin=="direct_ldc_i4_literal" ||
            tokenOrigin.Value.SecondProducerIndexInt32ArgumentLiteral is not null)
            throw new InvalidDataException("Non-i4 metadata token cannot prove an int literal");
        // Public synthetic -1 / short / 32-bit integer opcode controls.
        // These constants are invented test data, never original game values.
        var smallNegative=new MethodDefinition("SyntheticNegativeShortI4",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        smallNegative.Parameters.Add(new ParameterDefinition(materialType));
        td.Methods.Add(smallNegative);
        var ilNegative=smallNegative.Body.GetILProcessor();
        ilNegative.Append(ilNegative.Create(OpCodes.Ldarg_0));
        ilNegative.Append(ilNegative.Create(OpCodes.Ldstr,"public-synthetic-short-negative"));
        ilNegative.Append(ilNegative.Create(OpCodes.Ldc_I4_S,(sbyte)-5));
        ilNegative.Append(ilNegative.Create(OpCodes.Call,oneIndexMethod));
        ilNegative.Append(ilNegative.Create(OpCodes.Callvirt,setTexture));
        ilNegative.Append(ilNegative.Create(OpCodes.Ret));
        var negativeOrigin=FoamSetterFlow.Trace(smallNegative,1);
        if (negativeOrigin is null ||
            negativeOrigin.Value.SecondProducerIndexInt32ArgumentLiteral!=-5 ||
            negativeOrigin.Value.SecondProducerIndexInt32ArgumentOrigin!="direct_ldc_i4_literal")
            throw new InvalidDataException("Signed synthetic ldc.i4.s source decoding failed");
        var widePositive=new MethodDefinition("SyntheticWideI4",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        widePositive.Parameters.Add(new ParameterDefinition(materialType));
        td.Methods.Add(widePositive);
        var ilWide=widePositive.Body.GetILProcessor();
        ilWide.Append(ilWide.Create(OpCodes.Ldarg_0));
        ilWide.Append(ilWide.Create(OpCodes.Ldstr,"public-synthetic-wide"));
        ilWide.Append(ilWide.Create(OpCodes.Ldc_I4,300));
        ilWide.Append(ilWide.Create(OpCodes.Call,oneIndexMethod));
        ilWide.Append(ilWide.Create(OpCodes.Callvirt,setTexture));
        ilWide.Append(ilWide.Create(OpCodes.Ret));
        var wideOrigin=FoamSetterFlow.Trace(widePositive,1);
        if (wideOrigin is null ||
            wideOrigin.Value.SecondProducerIndexInt32ArgumentLiteral!=300 ||
            wideOrigin.Value.SecondProducerIndexInt32ArgumentOrigin!="direct_ldc_i4_literal")
            throw new InvalidDataException("Synthetic wide ldc.i4 source decoding failed");
        var negativeOne=new MethodDefinition("SyntheticMinusOneI4",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        negativeOne.Parameters.Add(new ParameterDefinition(materialType));
        td.Methods.Add(negativeOne);
        var ilMinus=negativeOne.Body.GetILProcessor();
        ilMinus.Append(ilMinus.Create(OpCodes.Ldarg_0));
        ilMinus.Append(ilMinus.Create(OpCodes.Ldstr,"public-synthetic-minus-one"));
        ilMinus.Append(ilMinus.Create(OpCodes.Ldc_I4_M1));
        ilMinus.Append(ilMinus.Create(OpCodes.Call,oneIndexMethod));
        ilMinus.Append(ilMinus.Create(OpCodes.Callvirt,setTexture));
        ilMinus.Append(ilMinus.Create(OpCodes.Ret));
        var minusOrigin=FoamSetterFlow.Trace(negativeOne,1);
        if (minusOrigin is null ||
            minusOrigin.Value.SecondProducerIndexInt32ArgumentLiteral!=-1)
            throw new InvalidDataException("Synthetic ldc.i4.m1 source decoding failed");
        var syntheticSafeValues=new[]{literalOrigin.Value.SecondProducerIndexInt32ArgumentLiteral,
            literalOrigin.Value.SecondProducerIndexInt32ArgumentLiteral,
            wideOrigin.Value.SecondProducerIndexInt32ArgumentLiteral,
            negativeOrigin.Value.SecondProducerIndexInt32ArgumentLiteral};
        if (syntheticSafeValues.Any(v=>v is null) ||
            syntheticSafeValues.Distinct().Count()!=3 ||
            syntheticSafeValues.Count(v=>v<0)!=1)
            throw new InvalidDataException("Synthetic repeated/negative aggregate controls failed");
        var strict=Scan(new[]{produced,producerDef},
            new HashSet<string>(StringComparer.Ordinal){Sha("public-direct-typed-producer")},
            new HashSet<string>(StringComparer.Ordinal));
        if (strict.SecondProducerDistinctPrivateSignatures.Count!=1 ||
            strict.SecondProducerExactManagedMethodDefinitionMatches!=1 ||
            strict.SecondProducerExactManagedBodyMatches!=1 ||
            strict.SecondProducerAmbiguousOrMissingMethodDefinitions!=0)
            throw new InvalidDataException("Same exact original method definition synthetic proof failed");
        var missing=Scan(new[]{produced},
            new HashSet<string>(StringComparer.Ordinal){Sha("public-direct-typed-producer")},
            new HashSet<string>(StringComparer.Ordinal));
        if (missing.SecondProducerExactManagedMethodDefinitionMatches!=0 ||
            missing.SecondProducerAmbiguousOrMissingMethodDefinitions!=1)
            throw new InvalidDataException("Unresolved original method definition must not be invented");
        var indexedField=new FieldDefinition("PublicSyntheticTextureArray",
            Mono.Cecil.FieldAttributes.Public,new ArrayType(textureType));
        factoryDef.Fields.Add(indexedField);
        var indexedGetter=new MethodDefinition("PublicSyntheticIndexedTexture",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Virtual,
            textureType);
        indexedGetter.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        factoryDef.Methods.Add(indexedGetter);
        var ilidx=indexedGetter.Body.GetILProcessor();
        ilidx.Append(ilidx.Create(OpCodes.Ldarg_0));
        ilidx.Append(ilidx.Create(OpCodes.Ldfld,indexedField));
        ilidx.Append(ilidx.Create(OpCodes.Ldarg_1));
        ilidx.Append(ilidx.Create(OpCodes.Ldelem_Ref));
        ilidx.Append(ilidx.Create(OpCodes.Ret));
        var knownShape=FoamProducerBody.Inspect(indexedGetter);
        if (!knownShape.ExactThisTextureArrayIndexedByIntParameter ||
            !knownShape.TypedTextureArrayFieldReferenced ||
            knownShape.IndexedReferenceLoads!=1)
            throw new InvalidDataException("Synthetic exact Texture[] indexed return not validated");
        var guarded=new MethodDefinition("PublicSyntheticNullGuardedArrayTexture",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Virtual,
            textureType);
        guarded.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        factoryDef.Methods.Add(guarded);
        var ilguard=guarded.Body.GetILProcessor();
        var fallBack=ilguard.Create(OpCodes.Ldnull);
        ilguard.Append(ilguard.Create(OpCodes.Ldarg_0));
        ilguard.Append(ilguard.Create(OpCodes.Ldfld,indexedField));
        ilguard.Append(ilguard.Create(OpCodes.Brfalse_S,fallBack));
        ilguard.Append(ilguard.Create(OpCodes.Ldarg_0));
        ilguard.Append(ilguard.Create(OpCodes.Ldfld,indexedField));
        ilguard.Append(ilguard.Create(OpCodes.Ldarg_1));
        ilguard.Append(ilguard.Create(OpCodes.Ldelem_Ref));
        ilguard.Append(ilguard.Create(OpCodes.Ret));
        ilguard.Append(fallBack);
        ilguard.Append(ilguard.Create(OpCodes.Ret));
        var guardProfile=FoamProducerBody.Inspect(guarded);
        if (!guardProfile.ExactNullGuardedOriginalTextureArrayIndexByInt ||
            !guardProfile.OriginalFallbackReturnsNull ||
            !guardProfile.TypedTextureArrayFieldReferenced ||
            guardProfile.InstanceFieldLoads!=2 ||
            guardProfile.InstructionCount!=10)
            throw new InvalidDataException("Original null-guarded Texture[] return fixture failed");
        // Opposite branch layout: null is returned immediately when the
        // RenderTexture[] backing field is absent, else array[index].
        var renderTextureType=new TypeReference("UnityEngine","RenderTexture",
            m,m.TypeSystem.Object.Scope);
        var renderArray=new FieldDefinition("PublicSyntheticRenderTextureArray",
            Mono.Cecil.FieldAttributes.Public,new ArrayType(renderTextureType));
        factoryDef.Fields.Add(renderArray);
        var guardedOther=new MethodDefinition("PublicSyntheticEarlyNullRenderTextureArray",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Virtual,
            textureType);
        guardedOther.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        factoryDef.Methods.Add(guardedOther);
        var ilother=guardedOther.Body.GetILProcessor();
        var nonNull=ilother.Create(OpCodes.Ldarg_0);
        ilother.Append(ilother.Create(OpCodes.Ldarg_0));
        ilother.Append(ilother.Create(OpCodes.Ldfld,renderArray));
        ilother.Append(ilother.Create(OpCodes.Brtrue_S,nonNull));
        ilother.Append(ilother.Create(OpCodes.Ldnull));
        ilother.Append(ilother.Create(OpCodes.Ret));
        ilother.Append(nonNull);
        ilother.Append(ilother.Create(OpCodes.Ldfld,renderArray));
        ilother.Append(ilother.Create(OpCodes.Ldarg_1));
        ilother.Append(ilother.Create(OpCodes.Ldelem_Ref));
        ilother.Append(ilother.Create(OpCodes.Ret));
        var testedOther=FoamProducerBody.Inspect(guardedOther);
        if (!testedOther.ExactNullGuardedOriginalTextureArrayIndexByInt ||
            !testedOther.OriginalFallbackReturnsNull ||
            !testedOther.OriginalInstanceFieldTypeCategories.TryGetValue("unity_rendertexture_array",out var count) ||
            count!=2)
            throw new InvalidDataException("Opposite branch RenderTexture[] fixture must prove null-indexed path");
                
        // Public synthetic exact-field writer, null-clear and same-typed decoy.
        var originalField=FoamFieldWriterLineage.ExactGetterBackingField(guardedOther);
        if (originalField is null ||
            FoamFieldWriterLineage.ExactGetterBackingField(guarded) is not null)
            throw new InvalidDataException("Conservative getter backing field extraction fixture failed");
        var writer=new MethodDefinition("SyntheticExactArrayWriter",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(writer);
        var iw=writer.Body.GetILProcessor();
        iw.Append(iw.Create(OpCodes.Ldarg_0));
        iw.Append(iw.Create(OpCodes.Ldc_I4_2));
        iw.Append(iw.Create(OpCodes.Newarr,renderTextureType));
        iw.Append(iw.Create(OpCodes.Stfld,renderArray));
        iw.Append(iw.Create(OpCodes.Ret));
        var clear=new MethodDefinition("SyntheticExactArrayClear",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(clear);
        var ic=clear.Body.GetILProcessor();
        ic.Append(ic.Create(OpCodes.Ldarg_0));
        ic.Append(ic.Create(OpCodes.Ldnull));
        ic.Append(ic.Create(OpCodes.Stfld,renderArray));
        ic.Append(ic.Create(OpCodes.Ret));
        var decoyField=new FieldDefinition("SyntheticDifferentRenderTextureArray",
            Mono.Cecil.FieldAttributes.Public,new ArrayType(renderTextureType));
        factoryDef.Fields.Add(decoyField);
        var decoy=new MethodDefinition("SyntheticDecoyArrayClear",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(decoy);
        var id=decoy.Body.GetILProcessor();
        id.Append(id.Create(OpCodes.Ldarg_0));
        id.Append(id.Create(OpCodes.Ldnull));
        id.Append(id.Create(OpCodes.Stfld,decoyField));
        id.Append(id.Create(OpCodes.Ret));
        var writerProof=FoamFieldWriterLineage.Scan(
            new[]{writer,clear,decoy,guardedOther},originalField);
        if (writerProof.ExactBackingFieldStoreInstructions!=2 ||
            writerProof.DistinctDirectWriterMethods!=2 ||
            writerProof.DirectRenderTextureArrayNewarrSources!=1 ||
            writerProof.DirectNullSources!=1 ||
            writerProof.OtherOrUnprovenSources!=0 ||
            !writerProof.ExactOriginalGetterFieldIdentityMatched ||
            writerProof.OriginalRuntimeWriteExecutedProven ||
            writerProof.OriginalArrayElementsPopulatedProven)
            throw new InvalidDataException("Synthetic exact writer/decoy provenance fixture failed");

        // Public synthetic metadata negatives: don't confuse visibility,
        // SerializeField and a runtime scene assignment. Field names here are
        // fixture-only and never copied from the original assembly.
        var publicMetadata=FoamFieldSerializationMetadata.Inspect(
            new[]{factoryDef},renderArray);
        if (publicMetadata.ExactOriginalManagedFieldDefinitionCount!=1 ||
            !publicMetadata.DeclaredPublic ||
            !publicMetadata.EligibleByFieldModifiersOnly ||
            publicMetadata.OriginalSceneOrPrefabValueVerified ||
            publicMetadata.RuntimeArrayLengthOrMembersVerified)
            throw new InvalidDataException("Synthetic public RenderTexture[] metadata control failed");
        var hiddenArray=new FieldDefinition("SyntheticHiddenArray",
            Mono.Cecil.FieldAttributes.Private,new ArrayType(renderTextureType));
        factoryDef.Fields.Add(hiddenArray);
        var hiddenMeta=FoamFieldSerializationMetadata.Inspect(new[]{factoryDef},hiddenArray);
        if (hiddenMeta.EligibleByFieldModifiersOnly || hiddenMeta.DeclaredPublic)
            throw new InvalidDataException("Private unmarked array must not imply serialization");
        var serializedArray=new FieldDefinition("SyntheticExplicitSerializeField",
            Mono.Cecil.FieldAttributes.Private,new ArrayType(renderTextureType));
        factoryDef.Fields.Add(serializedArray);
        var serializeAttrType=new TypeReference("UnityEngine","SerializeField",
            m,m.TypeSystem.Object.Scope);
        var serializeCtor=new MethodReference(".ctor",m.TypeSystem.Void,serializeAttrType)
            {HasThis=true};
        serializedArray.CustomAttributes.Add(new CustomAttribute(serializeCtor));
        var serialMeta=FoamFieldSerializationMetadata.Inspect(new[]{factoryDef},serializedArray);
        if (!serialMeta.HasExplicitUnitySerializeField ||
            !serialMeta.EligibleByFieldModifiersOnly)
            throw new InvalidDataException("Explicit synthetic SerializeField ignored");
        var notSerialized=new FieldDefinition("SyntheticExcludedArray",
            Mono.Cecil.FieldAttributes.Public|Mono.Cecil.FieldAttributes.NotSerialized,
            new ArrayType(renderTextureType));
        factoryDef.Fields.Add(notSerialized);
        var blockedMeta=FoamFieldSerializationMetadata.Inspect(new[]{factoryDef},notSerialized);
        if (!blockedMeta.HasNonSerializedMetadata ||
            blockedMeta.EligibleByFieldModifiersOnly)
            throw new InvalidDataException("NonSerialized synthetic array incorrectly eligible");
        var staticArray=new FieldDefinition("SyntheticStaticArray",
            Mono.Cecil.FieldAttributes.Public|Mono.Cecil.FieldAttributes.Static,
            new ArrayType(renderTextureType));
        factoryDef.Fields.Add(staticArray);
        var staticMeta=FoamFieldSerializationMetadata.Inspect(new[]{factoryDef},staticArray);
        if (!staticMeta.IsStatic || staticMeta.EligibleByFieldModifiersOnly)
            throw new InvalidDataException("Static synthetic array must be excluded");
        var readonlyArray=new FieldDefinition("SyntheticReadonlyArray",
            Mono.Cecil.FieldAttributes.Public|Mono.Cecil.FieldAttributes.InitOnly,
            new ArrayType(renderTextureType));
        factoryDef.Fields.Add(readonlyArray);
        var readonlyMeta=FoamFieldSerializationMetadata.Inspect(new[]{factoryDef},readonlyArray);
        if (!readonlyMeta.IsInitOnly || readonlyMeta.EligibleByFieldModifiersOnly)
            throw new InvalidDataException("Readonly synthetic array must be excluded");
        var missingArray=new FieldReference("SyntheticMissingRenderTexture",
            new ArrayType(renderTextureType),factoryDef);
        var missingMeta=FoamFieldSerializationMetadata.Inspect(new[]{factoryDef},missingArray);
        if (missingMeta.ExactOriginalManagedFieldDefinitionCount!=0 ||
            missingMeta.EligibleByFieldModifiersOnly)
            throw new InvalidDataException("Missing field definition must not be invented");
        // Public synthetic exact backing array read/address topology. The
        // real guarded getter has two matching field loads; other reader,
        // address-taking writer candidate, and equal-typed wrong-field decoy
        // are separate instructions. No field value is read at runtime.
        var extraReader=new MethodDefinition("SyntheticOtherRead",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(extraReader);
        var lir=extraReader.Body.GetILProcessor();
        lir.Append(lir.Create(OpCodes.Ldarg_0));
        lir.Append(lir.Create(OpCodes.Ldfld,renderArray));
        lir.Append(lir.Create(OpCodes.Pop));
        lir.Append(lir.Create(OpCodes.Ret));
        var byrefReader=new MethodDefinition("SyntheticAddressRead",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(byrefReader);
        var liaf=byrefReader.Body.GetILProcessor();
        liaf.Append(liaf.Create(OpCodes.Ldarg_0));
        liaf.Append(liaf.Create(OpCodes.Ldflda,renderArray));
        liaf.Append(liaf.Create(OpCodes.Pop));
        liaf.Append(liaf.Create(OpCodes.Ret));
        var wrongReader=new MethodDefinition("SyntheticWrongFieldRead",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(wrongReader);
        var liwr=wrongReader.Body.GetILProcessor();
        liwr.Append(liwr.Create(OpCodes.Ldarg_0));
        liwr.Append(liwr.Create(OpCodes.Ldfld,decoyField));
        liwr.Append(liwr.Create(OpCodes.Pop));
        liwr.Append(liwr.Create(OpCodes.Ret));
        var readProof=FoamFieldReadTopology.Scan(
            new[]{guardedOther,extraReader,byrefReader,wrongReader},
            originalField,guardedOther);
        if (readProof.ExactInstanceFieldLoadInstructions!=3 ||
            readProof.ExactInstanceFieldAddressInstructions!=1 ||
            readProof.OriginalGetterFieldLoadInstructions!=2 ||
            readProof.OtherOriginalMethodFieldLoadInstructions!=1 ||
            readProof.OtherOriginalMethodFieldAddressInstructions!=1 ||
            readProof.DistinctDirectReaderMethods!=2 ||
            readProof.DistinctDirectAddressMethods!=1 ||
            readProof.ActualRuntimeArrayContentsVerified ||
            readProof.ManagedArrayElementsWrittenOrPopulatedProven)
            throw new InvalidDataException("Original field access topology fixture must exclude typed decoy");
        // Public synthetic address consumers: exact typed byref call, direct
        // indirection store, array-element store, read and typed-field decoy.
        var syntheticByref=new MethodReference("SyntheticMayWriteArrayByRef",
            m.TypeSystem.Void,publicFactory){HasThis=false};
        syntheticByref.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        var typedByrefSite=new MethodDefinition("SyntheticTypedByrefArrayCall",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(typedByrefSite);
        var ilTb=typedByrefSite.Body.GetILProcessor();
        ilTb.Append(ilTb.Create(OpCodes.Ldarg_0));
        ilTb.Append(ilTb.Create(OpCodes.Ldflda,renderArray));
        ilTb.Append(ilTb.Create(OpCodes.Call,syntheticByref));
        ilTb.Append(ilTb.Create(OpCodes.Ret));
        var syntheticCallees=new List<MethodReference>();
        var typedProf=FoamFieldAddressConsumer.Scan(
            new[]{typedByrefSite},originalField,
            recipient=>syntheticCallees.Add(recipient));
        if (syntheticCallees.Count!=1)
            throw new InvalidDataException("Exact synthetic call capture failed");
        if (typedProf.ExactFieldAddressSites!=1 ||
            typedProf.SinkCategories.GetValueOrDefault(
                "typed_byref_array_call_potential_mutation")!=1 ||
            typedProf.OriginalRuntimeExecutionVerified)
            throw new InvalidDataException("Typed original array byref call fixture failed");

        // A precise matching public method body must be distinguished from a
        // same-named but differently typed method and an unresolved external.
        var syntheticTargetDef=new MethodDefinition("SyntheticMayWriteArrayByRef",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        syntheticTargetDef.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        factoryDef.Methods.Add(syntheticTargetDef);
        var targetIl=syntheticTargetDef.Body.GetILProcessor();
        targetIl.Append(targetIl.Create(OpCodes.Ldarg_0));
        targetIl.Append(targetIl.Create(OpCodes.Ldnull));
        targetIl.Append(targetIl.Create(OpCodes.Stind_Ref));
        targetIl.Append(targetIl.Create(OpCodes.Ret));
        var originalStyleBody=FoamByrefTargetBody.Inspect(
            new[]{syntheticTargetDef},syntheticCallees[0]);
        if (originalStyleBody.ExactSourceManagedMethodDefinitionMatches!=1 ||
            !originalStyleBody.ExactOriginalMethodBodyAvailable ||
            !originalStyleBody.CallFormalContainsExactRefRenderTextureArray ||
            originalStyleBody.BodyDirectIndirectRefStoreOpcodeCount!=1 ||
            originalStyleBody.BodyStrictNullStoreThroughRefArrayFormalCount!=1 ||
            originalStyleBody.RuntimeCallExecutionProven ||
            originalStyleBody.RuntimeArrayInitializationProven)
            throw new InvalidDataException("Exact synthetic typed byref callee body matching failed");
        var typedWrong=new MethodDefinition("SyntheticMayWriteArrayByRef",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        typedWrong.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(textureType))));
        factoryDef.Methods.Add(typedWrong);
        var wrongRecipient=FoamByrefTargetBody.Inspect(
            new[]{typedWrong},syntheticCallees[0]);
        if (wrongRecipient.ExactSourceManagedMethodDefinitionMatches!=0 ||
            wrongRecipient.ExactOriginalMethodBodyAvailable)
            throw new InvalidDataException("Same-named wrong-type recipient falsely matched");

        // Strict source-free same-basic-block proof: ref array formal
        // receives the actual newarr RenderTexture[] return.
        var syntheticAlloc=new MethodDefinition("SyntheticDirectAllocateByRef",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        syntheticAlloc.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        factoryDef.Methods.Add(syntheticAlloc);
        var allocIl=syntheticAlloc.Body.GetILProcessor();
        allocIl.Append(allocIl.Create(OpCodes.Ldarg_0));
        allocIl.Append(allocIl.Create(OpCodes.Ldc_I4_3));
        allocIl.Append(allocIl.Create(OpCodes.Newarr,renderTextureType));
        allocIl.Append(allocIl.Create(OpCodes.Stind_Ref));
        allocIl.Append(allocIl.Create(OpCodes.Ret));
        var allocationPositiveProof=FoamByrefAllocationFlow.Inspect(
            new[]{syntheticAlloc},syntheticAlloc);
        if(allocationPositiveProof.ExactStindRefSites!=1 ||
            allocationPositiveProof.ProvenNewarrRenderTextureArrayToRefFormalStores!=1 ||
            allocationPositiveProof.StoreSitesWithUnprovenDestinationOrFlow!=0 ||
            allocationPositiveProof.RuntimeExecutionVerified)
            throw new InvalidDataException("Exact positive newarr to ref array store fixture failed");
        var syntheticAmbiguous=new MethodDefinition("SyntheticAcrossBranchUnproven",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        syntheticAmbiguous.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        factoryDef.Methods.Add(syntheticAmbiguous);
        var ambIl=syntheticAmbiguous.Body.GetILProcessor();
        var sink=ambIl.Create(OpCodes.Stind_Ref);
        ambIl.Append(ambIl.Create(OpCodes.Ldarg_0));
        ambIl.Append(ambIl.Create(OpCodes.Ldc_I4_3));
        ambIl.Append(ambIl.Create(OpCodes.Newarr,renderTextureType));
        ambIl.Append(ambIl.Create(OpCodes.Br_S,sink));
        ambIl.Append(sink);
        ambIl.Append(ambIl.Create(OpCodes.Ret));
        var unresolved=FoamByrefAllocationFlow.Inspect(
            new[]{syntheticAmbiguous},syntheticAmbiguous);
        if(unresolved.ProvenNewarrRenderTextureArrayToRefFormalStores!=0 ||
            unresolved.StoreSitesWithUnprovenDestinationOrFlow!=1)
            throw new InvalidDataException("Cross-branch source must remain unproven");
        var wrongNewarr=new MethodDefinition("SyntheticWrongNewarrElement",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        wrongNewarr.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        factoryDef.Methods.Add(wrongNewarr);
        var wrongIl=wrongNewarr.Body.GetILProcessor();
        wrongIl.Append(wrongIl.Create(OpCodes.Ldarg_0));
        wrongIl.Append(wrongIl.Create(OpCodes.Ldc_I4_3));
        wrongIl.Append(wrongIl.Create(OpCodes.Newarr,textureType));
        wrongIl.Append(wrongIl.Create(OpCodes.Stind_Ref));
        wrongIl.Append(wrongIl.Create(OpCodes.Ret));
        var wrongProof=FoamByrefAllocationFlow.Inspect(
            new[]{wrongNewarr},wrongNewarr);
        if(wrongProof.ProvenNewarrRenderTextureArrayToRefFormalStores!=0 ||
            wrongProof.RefFormalStoresWithUnprovenValue!=1)
            throw new InvalidDataException("Wrong-element array cannot prove source RT allocation");
        // Source-free bounded size checks. Synthetic original-style length=3
        // is not related to the actual private original constant.
        var syntheticFlow=FoamByrefAllocationFlow.Inspect(
            new[]{syntheticAlloc},syntheticAlloc);
        var boundedYes=FoamByrefArrayBounds.Inspect(
            new[]{syntheticAlloc},syntheticAlloc,syntheticFlow,
            new[]{0,1,2,2});
        var boundedNo=FoamByrefArrayBounds.Inspect(
            new[]{syntheticAlloc},syntheticAlloc,syntheticFlow,
            new[]{0,1,2,3});
        if(boundedYes.FourOriginalIndicesWithinThisCompiledAllocation!=true ||
            boundedNo.FourOriginalIndicesWithinThisCompiledAllocation!=false ||
            boundedYes.NewarrLengthOperandOriginCategory!="direct_ldc_i4_literal" ||
            boundedYes.OriginalNumericLiteralsOrDigestsDisclosed ||
            boundedYes.RuntimeArrayAllocationOrBoundsVerified)
            throw new InvalidDataException("Synthetic exact size vs caller bounds control failed");
        var syntheticUnknownLength=new MethodDefinition("SyntheticDynamicLengthByref",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        syntheticUnknownLength.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        syntheticUnknownLength.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        factoryDef.Methods.Add(syntheticUnknownLength);
        var unknownIl=syntheticUnknownLength.Body.GetILProcessor();
        unknownIl.Append(unknownIl.Create(OpCodes.Ldarg_0));
        unknownIl.Append(unknownIl.Create(OpCodes.Ldarg_1));
        unknownIl.Append(unknownIl.Create(OpCodes.Newarr,renderTextureType));
        unknownIl.Append(unknownIl.Create(OpCodes.Stind_Ref));
        unknownIl.Append(unknownIl.Create(OpCodes.Ret));
        var unknownFlow=FoamByrefAllocationFlow.Inspect(
            new[]{syntheticUnknownLength},syntheticUnknownLength);
        var unknownBound=FoamByrefArrayBounds.Inspect(
            new[]{syntheticUnknownLength},syntheticUnknownLength,unknownFlow,
            new[]{0,1,2,3});
        if(unknownBound.FourOriginalIndicesWithinThisCompiledAllocation is not null ||
            unknownBound.NewarrLengthOperandOriginCategory!="length_source_not_direct_i4")
            throw new InvalidDataException("Dynamic original allocation size must remain unproven");
        // Invented public fixtures: same-block literal via local; argument
        // via local; and cross-branch local which MUST remain unresolved.
        var t2LocalSize=new MethodDefinition("SyntheticLocalI4Length",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        t2LocalSize.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        t2LocalSize.Body.Variables.Add(new VariableDefinition(m.TypeSystem.Int32));
        t2LocalSize.Body.InitLocals=true;
        factoryDef.Methods.Add(t2LocalSize);
        var ilLs=t2LocalSize.Body.GetILProcessor();
        ilLs.Append(ilLs.Create(OpCodes.Ldc_I4_4));
        ilLs.Append(ilLs.Create(OpCodes.Stloc_0));
        ilLs.Append(ilLs.Create(OpCodes.Ldarg_0));
        ilLs.Append(ilLs.Create(OpCodes.Ldloc_0));
        ilLs.Append(ilLs.Create(OpCodes.Newarr,renderTextureType));
        ilLs.Append(ilLs.Create(OpCodes.Stind_Ref));
        ilLs.Append(ilLs.Create(OpCodes.Ret));
        var t2LocalFlow=FoamByrefAllocationFlow.Inspect(new[]{t2LocalSize},t2LocalSize);
        var t2LocalOrigin=FoamByrefLengthOrigin.Inspect(new[]{t2LocalSize},
            t2LocalSize,t2LocalFlow,new[]{0,1,2,3});
        if(t2LocalOrigin.ImmediateLengthProducerCategory!="ldloc" ||
            t2LocalOrigin.ResolvedLengthSourceCategory!="same_block_local_i4" ||
            !t2LocalOrigin.CompileTimePositiveArrayLengthProven ||
            t2LocalOrigin.FourPrivateOriginalIndicesInBoundsForCompiledLength!=true)
            throw new InvalidDataException("Same-block synthetic literal local failed");
        var t2ArgSize=new MethodDefinition("SyntheticLocalArgLength",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        t2ArgSize.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        t2ArgSize.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        t2ArgSize.Body.Variables.Add(new VariableDefinition(m.TypeSystem.Int32));
        t2ArgSize.Body.InitLocals=true;
        factoryDef.Methods.Add(t2ArgSize);
        var ilLa=t2ArgSize.Body.GetILProcessor();
        ilLa.Append(ilLa.Create(OpCodes.Ldarg_1));
        ilLa.Append(ilLa.Create(OpCodes.Stloc_0));
        ilLa.Append(ilLa.Create(OpCodes.Ldarg_0));
        ilLa.Append(ilLa.Create(OpCodes.Ldloc_0));
        ilLa.Append(ilLa.Create(OpCodes.Newarr,renderTextureType));
        ilLa.Append(ilLa.Create(OpCodes.Stind_Ref));
        ilLa.Append(ilLa.Create(OpCodes.Ret));
        var t2ArgFlow=FoamByrefAllocationFlow.Inspect(new[]{t2ArgSize},t2ArgSize);
        var t2ArgOrigin=FoamByrefLengthOrigin.Inspect(new[]{t2ArgSize},
            t2ArgSize,t2ArgFlow,new[]{0,1,2,3});
        if(t2ArgOrigin.ResolvedLengthSourceCategory!="same_block_local_from_int32_argument" ||
            t2ArgOrigin.FourPrivateOriginalIndicesInBoundsForCompiledLength is not null)
            throw new InvalidDataException("Local from argument cannot prove length");
        var t2BranchSize=new MethodDefinition("SyntheticCrossBlockLength",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        t2BranchSize.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        t2BranchSize.Body.Variables.Add(new VariableDefinition(m.TypeSystem.Int32));
        t2BranchSize.Body.InitLocals=true;
        factoryDef.Methods.Add(t2BranchSize);
        var ilLb=t2BranchSize.Body.GetILProcessor();
        var t2Target=ilLb.Create(OpCodes.Ldarg_0);
        ilLb.Append(ilLb.Create(OpCodes.Ldc_I4_4));
        ilLb.Append(ilLb.Create(OpCodes.Stloc_0));
        ilLb.Append(ilLb.Create(OpCodes.Br_S,t2Target));
        ilLb.Append(t2Target);
        ilLb.Append(ilLb.Create(OpCodes.Ldloc_0));
        ilLb.Append(ilLb.Create(OpCodes.Newarr,renderTextureType));
        ilLb.Append(ilLb.Create(OpCodes.Stind_Ref));
        ilLb.Append(ilLb.Create(OpCodes.Ret));
        var t2BranchFlow=FoamByrefAllocationFlow.Inspect(new[]{t2BranchSize},t2BranchSize);
        var t2BranchOrigin=FoamByrefLengthOrigin.Inspect(new[]{t2BranchSize},
            t2BranchSize,t2BranchFlow,new[]{0,1,2,3});
        if(t2BranchOrigin.ResolvedLengthSourceCategory!="local_definition_outside_block" ||
            t2BranchOrigin.FourPrivateOriginalIndicesInBoundsForCompiledLength is not null)
            throw new InvalidDataException("Cross-block size must remain unknown");

        // Synthetic actual caller: exact RT array field ref and a direct
        // constant length into the genuine typed int32 formal. The values
        // here are test-only and have no relationship to original game data.
        var syntheticRefLengthTarget=new MethodDefinition("PublicSyntheticByrefSize",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        syntheticRefLengthTarget.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        syntheticRefLengthTarget.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        factoryDef.Methods.Add(syntheticRefLengthTarget);
        var targetSizeIl=syntheticRefLengthTarget.Body.GetILProcessor();
        targetSizeIl.Append(targetSizeIl.Create(OpCodes.Ldarg_0));
        targetSizeIl.Append(targetSizeIl.Create(OpCodes.Ldarg_1));
        targetSizeIl.Append(targetSizeIl.Create(OpCodes.Newarr,renderTextureType));
        targetSizeIl.Append(targetSizeIl.Create(OpCodes.Stind_Ref));
        targetSizeIl.Append(targetSizeIl.Create(OpCodes.Ret));
        var syntheticTargetFlow=FoamByrefAllocationFlow.Inspect(
            new[]{syntheticRefLengthTarget},syntheticRefLengthTarget);
        var syntheticTargetSize=FoamByrefLengthOrigin.Inspect(
            new[]{syntheticRefLengthTarget},syntheticRefLengthTarget,
            syntheticTargetFlow,new[]{0,1,2,3});
        var lengthLiteralCaller=new MethodDefinition("PublicSyntheticLengthLiteralCaller",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(lengthLiteralCaller);
        var litCallerIl=lengthLiteralCaller.Body.GetILProcessor();
        litCallerIl.Append(litCallerIl.Create(OpCodes.Ldarg_0));
        var litAddress=litCallerIl.Create(OpCodes.Ldflda,renderArray);
        litCallerIl.Append(litAddress);
        litCallerIl.Append(litCallerIl.Create(OpCodes.Ldc_I4_4));
        var litCall=litCallerIl.Create(OpCodes.Call,syntheticRefLengthTarget);
        litCallerIl.Append(litCall);
        litCallerIl.Append(litCallerIl.Create(OpCodes.Ret));
        var proofLit=FoamByrefActualCallerLength.Inspect(
            new[]{syntheticRefLengthTarget},lengthLiteralCaller,litAddress,
            litCall,syntheticRefLengthTarget,0,syntheticTargetSize,
            new[]{0,1,2,3});
        if(proofLit.ExactActualLengthArgumentSourceCategory!="direct_i4" ||
            !proofLit.ActualLengthArgumentDirectPositiveLiteralProven ||
            proofLit.FourPrivateIndicesWithinThisCompiledCallerLength!=true ||
            proofLit.OriginalRuntimeArrayLengthOrContentsVerified)
            throw new InvalidDataException("Synthetic exact typed caller length proof failed");
        var lengthArgumentCaller=new MethodDefinition("PublicSyntheticLengthArgCaller",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        lengthArgumentCaller.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        factoryDef.Methods.Add(lengthArgumentCaller);
        var argCallerIl=lengthArgumentCaller.Body.GetILProcessor();
        argCallerIl.Append(argCallerIl.Create(OpCodes.Ldarg_0));
        var argAddress=argCallerIl.Create(OpCodes.Ldflda,renderArray);
        argCallerIl.Append(argAddress);
        argCallerIl.Append(argCallerIl.Create(OpCodes.Ldarg_1));
        var argCall=argCallerIl.Create(OpCodes.Call,syntheticRefLengthTarget);
        argCallerIl.Append(argCall);
        argCallerIl.Append(argCallerIl.Create(OpCodes.Ret));
        var proofArg=FoamByrefActualCallerLength.Inspect(
            new[]{syntheticRefLengthTarget},lengthArgumentCaller,argAddress,
            argCall,syntheticRefLengthTarget,0,syntheticTargetSize,
            new[]{0,1,2,3});
        if(proofArg.ExactActualLengthArgumentSourceCategory!="int32_argument" ||
            proofArg.FourPrivateIndicesWithinThisCompiledCallerLength is not null)
            throw new InvalidDataException("Synthetic argument source must not imply bounds");

        // Public synthetic original-style array member value constructor.
        // This constructor is a typed IL reference, not an executed Unity API.
        var t2RtCtor=new MethodReference(".ctor",m.TypeSystem.Void,
            renderTextureType){HasThis=true};
        var t2ElementMethod=new MethodDefinition("SyntheticRenderTextureMemberValue",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        t2ElementMethod.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        factoryDef.Methods.Add(t2ElementMethod);
        var t2ElementIl=t2ElementMethod.Body.GetILProcessor();
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Ldarg_0));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Ldc_I4_2));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Newarr,renderTextureType));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Stind_Ref));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Ldarg_0));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Ldind_Ref));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Ldc_I4_0));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Newobj,t2RtCtor));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Stelem_Ref));
        t2ElementIl.Append(t2ElementIl.Create(OpCodes.Ret));
        var t2ValueFlow=FoamByrefAllocationFlow.Inspect(
            new[]{t2ElementMethod},t2ElementMethod);
        var t2ValuePositive=FoamByrefElementValueOrigin.Inspect(
            new[]{t2ElementMethod},t2ElementMethod,t2ValueFlow);
        if(!t2ValuePositive.ExactRenderTextureConstructorValueProven ||
            t2ValuePositive.ResolvedElementValueOriginCategory!="newobj_rendertexture" ||
            t2ValuePositive.RuntimeRenderTextureObjectOrPixelsVerified)
            throw new InvalidDataException("Original-style synthetic RT member value fixture failed");
        var t2NullValueMethod=new MethodDefinition("SyntheticNullArrayMember",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        t2NullValueMethod.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        factoryDef.Methods.Add(t2NullValueMethod);
        var t2NullIl=t2NullValueMethod.Body.GetILProcessor();
        t2NullIl.Append(t2NullIl.Create(OpCodes.Ldarg_0));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Ldc_I4_2));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Newarr,renderTextureType));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Stind_Ref));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Ldarg_0));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Ldind_Ref));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Ldc_I4_0));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Ldnull));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Stelem_Ref));
        t2NullIl.Append(t2NullIl.Create(OpCodes.Ret));
        var t2NullFlow=FoamByrefAllocationFlow.Inspect(
            new[]{t2NullValueMethod},t2NullValueMethod);
        var t2ValueNull=FoamByrefElementValueOrigin.Inspect(
            new[]{t2NullValueMethod},t2NullValueMethod,t2NullFlow);
        if(!t2ValueNull.LiteralNullElementValueProven ||
            t2ValueNull.ExactRenderTextureConstructorValueProven)
            throw new InvalidDataException("Synthetic null RT member value must not imply object");
        var t2WrongCtor=new MethodReference(".ctor",m.TypeSystem.Void,
            textureType){HasThis=true};
        var t2WrongValueMethod=new MethodDefinition("SyntheticWrongTextureMember",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        t2WrongValueMethod.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        factoryDef.Methods.Add(t2WrongValueMethod);
        var t2WrongIl=t2WrongValueMethod.Body.GetILProcessor();
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Ldarg_0));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Ldc_I4_2));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Newarr,renderTextureType));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Stind_Ref));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Ldarg_0));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Ldind_Ref));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Ldc_I4_0));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Newobj,t2WrongCtor));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Stelem_Ref));
        t2WrongIl.Append(t2WrongIl.Create(OpCodes.Ret));
        var t2WrongFlow=FoamByrefAllocationFlow.Inspect(
            new[]{t2WrongValueMethod},t2WrongValueMethod);
        var t2ValueWrong=FoamByrefElementValueOrigin.Inspect(
            new[]{t2WrongValueMethod},t2WrongValueMethod,t2WrongFlow);
        if(t2ValueWrong.ExactRenderTextureConstructorValueProven ||
            t2ValueWrong.ResolvedElementValueOriginCategory!="newobj_other_type")
            throw new InvalidDataException("Wrong typed constructor must not count as RenderTexture");
        // Public-only synthetic method identity: the same actual typed
        // element call reaches an internal SHA-original-like declaration.
        var t2ReturnDefinition=new MethodDefinition("SyntheticReturnTargetIdentity",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            renderTextureType);
        factoryDef.Methods.Add(t2ReturnDefinition);
        var t2ReturnIl=t2ReturnDefinition.Body.GetILProcessor();
        t2ReturnIl.Append(t2ReturnIl.Create(OpCodes.Ldnull));
        t2ReturnIl.Append(t2ReturnIl.Create(OpCodes.Ret));
        var t2ReturnStore=new MethodDefinition("SyntheticElementTargetIdentityStore",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        t2ReturnStore.Parameters.Add(new ParameterDefinition(
            new ByReferenceType(new ArrayType(renderTextureType))));
        factoryDef.Methods.Add(t2ReturnStore);
        var t2IdentityIl=t2ReturnStore.Body.GetILProcessor();
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Ldarg_0));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Ldc_I4_2));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Newarr,renderTextureType));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Stind_Ref));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Ldarg_0));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Ldind_Ref));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Ldc_I4_0));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Call,t2ReturnDefinition));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Stelem_Ref));
        t2IdentityIl.Append(t2IdentityIl.Create(OpCodes.Ret));
        var t2IdentityFlow=FoamByrefAllocationFlow.Inspect(
            new[]{t2ReturnStore},t2ReturnStore);
        var t2OriginalLikeIdentity=FoamByrefElementValueOrigin.Inspect(
            new[]{t2ReturnStore,t2ReturnDefinition},t2ReturnStore,t2IdentityFlow);
        if(t2OriginalLikeIdentity.MatchingOriginalReturnMethodDefinitions!=1 ||
            !t2OriginalLikeIdentity.MatchingOriginalMethodBodyAvailable ||
            t2OriginalLikeIdentity.ActualReturnTargetDeclarationCategory!=
                "matching_sha_managed_signature")
            throw new InvalidDataException("Exact typed synthetic RT declaration identity missed");
        var t2WrongReturnDefinition=new MethodDefinition(
            "SyntheticReturnTargetIdentity",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            renderTextureType);
        t2WrongReturnDefinition.Parameters.Add(
            new ParameterDefinition(m.TypeSystem.Int32));
        var t2WrongIdentity=FoamByrefElementValueOrigin.MatchActualRtCall(
            new[]{t2WrongReturnDefinition},t2ReturnDefinition);
        if(t2WrongIdentity.Count!=0 || t2WrongIdentity.Body)
            throw new InvalidDataException("Wrong-signature synthetic RT target falsely matched");
        var t2ExternalRtCall=new MethodReference("SyntheticExternal",
            renderTextureType,renderTextureType){HasThis=false};
        var t2ExternalIdentity=FoamByrefElementValueOrigin.MatchActualRtCall(
            new[]{t2ReturnDefinition},t2ExternalRtCall);
        if(t2ExternalIdentity.Count!=0 ||
            t2ExternalIdentity.Category!="unresolved_unityengine_declaration")
            throw new InvalidDataException("Unresolved UnityEngine RT source falsely matched");

        // Synthetic compiled return controls; no original class or IL published.
        var t2OriginalNullRet=FoamByrefElementValueOrigin.ScanMatchingReturnBody(
            new[]{t2ReturnDefinition},t2ReturnDefinition);
        if(t2OriginalNullRet.Total!=1 || t2OriginalNullRet.Null!=1 ||
            t2OriginalNullRet.Unknown!=0)
            throw new InvalidDataException("Synthetic direct null RT return missed");
        var t2RtNewobjRet=new MethodDefinition("SyntheticNewobjRtReturn",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            renderTextureType);
        factoryDef.Methods.Add(t2RtNewobjRet);
        var t2NewobjIl=t2RtNewobjRet.Body.GetILProcessor();
        t2NewobjIl.Append(t2NewobjIl.Create(OpCodes.Newobj,t2RtCtor));
        t2NewobjIl.Append(t2NewobjIl.Create(OpCodes.Ret));
        var t2OriginalNewobjRet=FoamByrefElementValueOrigin.ScanMatchingReturnBody(
            new[]{t2RtNewobjRet},t2RtNewobjRet);
        if(t2OriginalNewobjRet.Total!=1 || t2OriginalNewobjRet.NewRt!=1 ||
            t2OriginalNewobjRet.Null!=0)
            throw new InvalidDataException("Synthetic direct RT constructor return missed");
        var t2BranchRtRet=new MethodDefinition("SyntheticBranchTargetRtReturn",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            renderTextureType);
        factoryDef.Methods.Add(t2BranchRtRet);
        var t2BranchReturnIl=t2BranchRtRet.Body.GetILProcessor();
        var t2ReturnTarget=t2BranchReturnIl.Create(OpCodes.Ret);
        t2BranchReturnIl.Append(t2BranchReturnIl.Create(OpCodes.Ldnull));
        t2BranchReturnIl.Append(t2BranchReturnIl.Create(OpCodes.Br_S,t2ReturnTarget));
        t2BranchReturnIl.Append(t2ReturnTarget);
        var t2UnknownTargetRet=FoamByrefElementValueOrigin.ScanMatchingReturnBody(
            new[]{t2BranchRtRet},t2BranchRtRet);
        if(t2UnknownTargetRet.Total!=1 || t2UnknownTargetRet.Unknown!=1 ||
            t2UnknownTargetRet.Null!=0 || t2UnknownTargetRet.Branches!=1)
            throw new InvalidDataException("Cross-branch synthetic RT return cannot be proven");

        // Source-free return reason cases. A branch-to-ret is not
        // interpreted as the value from its textual predecessor.
        var t2ReasonNull=FoamByrefElementValueOrigin.ExplainRetSite(
            new[]{t2ReturnDefinition},t2ReturnDefinition);
        if(t2ReasonNull.Placement!="sequential_return_site" ||
            t2ReasonNull.Immediate!="ldnull")
            throw new InvalidDataException("Synthetic direct null return reason mismatch");
        var t2ReasonBranch=FoamByrefElementValueOrigin.ExplainRetSite(
            new[]{t2BranchRtRet},t2BranchRtRet);
        if(t2ReasonBranch.Placement!="branch_exception_or_method_entry" ||
            t2ReasonBranch.Immediate!="branch_opcode")
            throw new InvalidDataException("Synthetic branch-return origin was improperly promoted");
        var t2ReasonLocalDef=new MethodDefinition("SyntheticLocalReturnReason",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            renderTextureType);
        t2ReasonLocalDef.Body.Variables.Add(new VariableDefinition(renderTextureType));
        t2ReasonLocalDef.Body.InitLocals=true;
        factoryDef.Methods.Add(t2ReasonLocalDef);
        var t2ReasonLocalIl=t2ReasonLocalDef.Body.GetILProcessor();
        t2ReasonLocalIl.Append(t2ReasonLocalIl.Create(OpCodes.Ldnull));
        t2ReasonLocalIl.Append(t2ReasonLocalIl.Create(OpCodes.Stloc_0));
        t2ReasonLocalIl.Append(t2ReasonLocalIl.Create(OpCodes.Ldloc_0));
        t2ReasonLocalIl.Append(t2ReasonLocalIl.Create(OpCodes.Ret));
        var t2ReasonLocal=FoamByrefElementValueOrigin.ExplainRetSite(
            new[]{t2ReasonLocalDef},t2ReasonLocalDef);
        if(t2ReasonLocal.Placement!="sequential_return_site" ||
            t2ReasonLocal.Immediate!="ldloc")
            throw new InvalidDataException("Synthetic local-load return source not categorized");

        // Public synthetic local-writer controls distinguish exact return
        // local from another local and actual assigned source categories.
        var t2NullWriter=FoamByrefElementValueOrigin.ScanExactReturnLocalWriters(
            new[]{t2ReasonLocalDef},t2ReasonLocalDef);
        if(t2NullWriter.ExactReturnLocalLoadSites!=1 ||
            !t2NullWriter.ReturnLocalDeclaredRenderTexture ||
            t2NullWriter.ExactLocalAssignmentSites!=1 ||
            t2NullWriter.DirectNullAssignmentSites!=1 ||
            t2NullWriter.UnresolvedAssignmentSites!=0 ||
            t2NullWriter.SoleWriterImmediatePriorOpcodeCategory!="ldnull" ||
            t2NullWriter.SoleWriterIsControlFlowEntry)
            throw new InvalidDataException("Typed return local direct null writer fixture failed");
        var t2CtorWriterMethod=new MethodDefinition("SyntheticReturnLocalCtorWriter",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            renderTextureType);
        factoryDef.Methods.Add(t2CtorWriterMethod);
        t2CtorWriterMethod.Body.InitLocals=true;
        t2CtorWriterMethod.Body.Variables.Add(
            new VariableDefinition(renderTextureType));
        var t2CtorWriterIl=t2CtorWriterMethod.Body.GetILProcessor();
        t2CtorWriterIl.Append(t2CtorWriterIl.Create(OpCodes.Newobj,t2RtCtor));
        t2CtorWriterIl.Append(t2CtorWriterIl.Create(OpCodes.Stloc_0));
        t2CtorWriterIl.Append(t2CtorWriterIl.Create(OpCodes.Ldloc_0));
        t2CtorWriterIl.Append(t2CtorWriterIl.Create(OpCodes.Ret));
        var t2CtorWriter=FoamByrefElementValueOrigin.ScanExactReturnLocalWriters(
            new[]{t2CtorWriterMethod},t2CtorWriterMethod);
        if(t2CtorWriter.ExactLocalAssignmentSites!=1 ||
            t2CtorWriter.DirectRenderTextureConstructorAssignmentSites!=1 ||
            t2CtorWriter.DirectNullAssignmentSites!=0 ||
            t2CtorWriter.SoleWriterImmediatePriorOpcodeCategory!="newobj")
            throw new InvalidDataException("Synthetic RT constructor return-local writer rejected");
        var t2CallWriterMethod=new MethodDefinition("SyntheticReturnLocalCallWriter",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            renderTextureType);
        factoryDef.Methods.Add(t2CallWriterMethod);
        t2CallWriterMethod.Body.InitLocals=true;
        t2CallWriterMethod.Body.Variables.Add(
            new VariableDefinition(renderTextureType));
        var t2CallWriterIl=t2CallWriterMethod.Body.GetILProcessor();
        t2CallWriterIl.Append(t2CallWriterIl.Create(OpCodes.Call,t2ReturnDefinition));
        t2CallWriterIl.Append(t2CallWriterIl.Create(OpCodes.Stloc_0));
        t2CallWriterIl.Append(t2CallWriterIl.Create(OpCodes.Ldloc_0));
        t2CallWriterIl.Append(t2CallWriterIl.Create(OpCodes.Ret));
        var t2CallWriter=FoamByrefElementValueOrigin.ScanExactReturnLocalWriters(
            new[]{t2CallWriterMethod},t2CallWriterMethod);
        if(t2CallWriter.ExactLocalAssignmentSites!=1 ||
            t2CallWriter.DirectRenderTextureTypedCallAssignmentSites!=1 ||
            t2CallWriter.SoleWriterImmediatePriorOpcodeCategory!="call")
            throw new InvalidDataException("Synthetic RT-typed return-local call writer rejected");
        var t2OtherWriterMethod=new MethodDefinition("SyntheticWrongReturnLocalWriter",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            renderTextureType);
        factoryDef.Methods.Add(t2OtherWriterMethod);
        t2OtherWriterMethod.Body.InitLocals=true;
        t2OtherWriterMethod.Body.Variables.Add(
            new VariableDefinition(renderTextureType));
        t2OtherWriterMethod.Body.Variables.Add(
            new VariableDefinition(renderTextureType));
        var t2WrongLocalIl=t2OtherWriterMethod.Body.GetILProcessor();
        t2WrongLocalIl.Append(t2WrongLocalIl.Create(OpCodes.Ldnull));
        t2WrongLocalIl.Append(t2WrongLocalIl.Create(OpCodes.Stloc_1));
        t2WrongLocalIl.Append(t2WrongLocalIl.Create(OpCodes.Ldloc_0));
        t2WrongLocalIl.Append(t2WrongLocalIl.Create(OpCodes.Ret));
        var t2WrongLocalWriter=FoamByrefElementValueOrigin.ScanExactReturnLocalWriters(
            new[]{t2OtherWriterMethod},t2OtherWriterMethod);
        if(t2WrongLocalWriter.ExactReturnLocalLoadSites!=1 ||
            t2WrongLocalWriter.ExactLocalAssignmentSites!=0 ||
            t2WrongLocalWriter.DirectNullAssignmentSites!=0 ||
            t2WrongLocalWriter.SoleWriterImmediatePriorOpcodeCategory!="not_examined")
            throw new InvalidDataException("Wrong local typed decoy was counted as return writer");

        var syntheticIndirect=new MethodDefinition("SyntheticFieldReferenceStore",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(syntheticIndirect);
        var ilIs=syntheticIndirect.Body.GetILProcessor();
        ilIs.Append(ilIs.Create(OpCodes.Ldarg_0));
        ilIs.Append(ilIs.Create(OpCodes.Ldflda,renderArray));
        ilIs.Append(ilIs.Create(OpCodes.Ldnull));
        ilIs.Append(ilIs.Create(OpCodes.Stind_Ref));
        ilIs.Append(ilIs.Create(OpCodes.Ret));
        var directProf=FoamFieldAddressConsumer.Scan(
            new[]{syntheticIndirect},originalField);
        if (directProf.SinkCategories.GetValueOrDefault(
                "direct_field_reference_store")!=1)
            throw new InvalidDataException("Direct byref store synthetic fixture failed");
        var syntheticElementStore=new MethodDefinition("SyntheticArrayMemberStore",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(syntheticElementStore);
        var ilEs=syntheticElementStore.Body.GetILProcessor();
        ilEs.Append(ilEs.Create(OpCodes.Ldarg_0));
        ilEs.Append(ilEs.Create(OpCodes.Ldflda,renderArray));
        ilEs.Append(ilEs.Create(OpCodes.Ldind_Ref));
        ilEs.Append(ilEs.Create(OpCodes.Ldc_I4_0));
        ilEs.Append(ilEs.Create(OpCodes.Ldnull));
        ilEs.Append(ilEs.Create(OpCodes.Stelem_Ref));
        ilEs.Append(ilEs.Create(OpCodes.Ret));
        var elementProf=FoamFieldAddressConsumer.Scan(
            new[]{syntheticElementStore},originalField);
        if (elementProf.SinkCategories.GetValueOrDefault(
                "direct_array_element_store_via_field")!=1)
            throw new InvalidDataException("Array member store from field address fixture failed");
        var syntheticLength=new MethodDefinition("SyntheticArrayLengthRead",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(syntheticLength);
        var ilLen=syntheticLength.Body.GetILProcessor();
        ilLen.Append(ilLen.Create(OpCodes.Ldarg_0));
        ilLen.Append(ilLen.Create(OpCodes.Ldflda,renderArray));
        ilLen.Append(ilLen.Create(OpCodes.Ldind_Ref));
        ilLen.Append(ilLen.Create(OpCodes.Ldlen));
        ilLen.Append(ilLen.Create(OpCodes.Pop));
        ilLen.Append(ilLen.Create(OpCodes.Ret));
        var lengthProf=FoamFieldAddressConsumer.Scan(
            new[]{syntheticLength},originalField);
        if (lengthProf.SinkCategories.GetValueOrDefault(
                "array_length_read_via_address")!=1)
            throw new InvalidDataException("Array length from field address fixture failed");
        var wrongAddress=new MethodDefinition("SyntheticSameTypedWrongFieldAddr",
            Mono.Cecil.MethodAttributes.Public,m.TypeSystem.Void);
        factoryDef.Methods.Add(wrongAddress);
        var ilWa=wrongAddress.Body.GetILProcessor();
        ilWa.Append(ilWa.Create(OpCodes.Ldarg_0));
        ilWa.Append(ilWa.Create(OpCodes.Ldflda,decoyField));
        ilWa.Append(ilWa.Create(OpCodes.Pop));
        ilWa.Append(ilWa.Create(OpCodes.Ret));
        var wrongProf=FoamFieldAddressConsumer.Scan(new[]{wrongAddress},originalField);
        if (wrongProf.ExactFieldAddressSites!=0 || wrongProf.SinkCategories.Count!=0)
            throw new InvalidDataException("Similar-typed decoy address must not count");
        var guardedWrong=new MethodDefinition("PublicSyntheticWrongConditionalTarget",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Virtual,
            textureType);
        guardedWrong.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        factoryDef.Methods.Add(guardedWrong);
        var ilgw=guardedWrong.Body.GetILProcessor();
        var badReturn=ilgw.Create(OpCodes.Ret);
        ilgw.Append(ilgw.Create(OpCodes.Ldarg_0));
        ilgw.Append(ilgw.Create(OpCodes.Ldfld,indexedField));
        ilgw.Append(ilgw.Create(OpCodes.Brfalse_S,badReturn));
        ilgw.Append(ilgw.Create(OpCodes.Ldarg_0));
        ilgw.Append(ilgw.Create(OpCodes.Ldfld,indexedField));
        ilgw.Append(ilgw.Create(OpCodes.Ldarg_1));
        ilgw.Append(ilgw.Create(OpCodes.Ldelem_Ref));
        ilgw.Append(badReturn);
        ilgw.Append(ilgw.Create(OpCodes.Ldnull));
        ilgw.Append(ilgw.Create(OpCodes.Ret));
        if (FoamProducerBody.Inspect(guardedWrong).ExactNullGuardedOriginalTextureArrayIndexByInt)
            throw new InvalidDataException("Wrong branch target must not prove null fallback");
                var wrongIndexed=new MethodDefinition("PublicSyntheticExtraSourceInstruction",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Virtual,
            textureType);
        wrongIndexed.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        factoryDef.Methods.Add(wrongIndexed);
        var ilwrong=wrongIndexed.Body.GetILProcessor();
        ilwrong.Append(ilwrong.Create(OpCodes.Ldarg_0));
        ilwrong.Append(ilwrong.Create(OpCodes.Ldfld,indexedField));
        ilwrong.Append(ilwrong.Create(OpCodes.Ldarg_1));
        ilwrong.Append(ilwrong.Create(OpCodes.Ldc_I4_0));
        ilwrong.Append(ilwrong.Create(OpCodes.Pop));
        ilwrong.Append(ilwrong.Create(OpCodes.Ldelem_Ref));
        ilwrong.Append(ilwrong.Create(OpCodes.Ret));
        if (FoamProducerBody.Inspect(wrongIndexed).ExactThisTextureArrayIndexedByIntParameter)
            throw new InvalidDataException("Changed original Texture[] body must reject exact pattern");
                var wrongProducer=new MethodReference("PublicSyntheticWrongReturn",
            m.TypeSystem.Object,publicFactory){HasThis=false};
        var producedWrong=new MethodDefinition("PublicSyntheticNonTextureProducer",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        producedWrong.Parameters.Add(new ParameterDefinition(materialType));
        td.Methods.Add(producedWrong);
        var liwrong=producedWrong.Body.GetILProcessor();
        liwrong.Append(liwrong.Create(OpCodes.Ldarg_0));
        liwrong.Append(liwrong.Create(OpCodes.Ldstr,"public-synthetic-unknown-producer"));
        liwrong.Append(liwrong.Create(OpCodes.Call,wrongProducer));
        liwrong.Append(liwrong.Create(OpCodes.Callvirt,setTexture));
        liwrong.Append(liwrong.Create(OpCodes.Ret));
        var tracedWrong=FoamSetterFlow.Trace(producedWrong,1);
        if (tracedWrong is null ||
            tracedWrong.Value.SecondProducerDeclaredReturnClass!="other_unverified_return_type")
            throw new InvalidDataException("Unknown return type must not be labeled genuine Unity Texture");
                var negative = new MethodDefinition("NearbyButWrongPublicSetTexture",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        negative.Parameters.Add(new ParameterDefinition(m.TypeSystem.Object));
        td.Methods.Add(negative);
        var lin=negative.Body.GetILProcessor();
        lin.Append(lin.Create(OpCodes.Ldarg_0));
        lin.Append(lin.Create(OpCodes.Ldstr,"public-unrelated-tex-name"));
        lin.Append(lin.Create(OpCodes.Pop));
        lin.Append(lin.Create(OpCodes.Ldstr,"other-later-name"));
        lin.Append(lin.Create(OpCodes.Ldnull));
        lin.Append(lin.Create(OpCodes.Callvirt,setTexture));
        lin.Append(lin.Create(OpCodes.Ret));
        if (FoamSetterFlow.Trace(negative,1) is not null)
            throw new InvalidDataException("Unrelated proximity must not establish argument flow");
        var idTexture = new MethodReference("SetTexture",m.TypeSystem.Void,materialType)
            { HasThis=true };
        idTexture.Parameters.Add(new ParameterDefinition(m.TypeSystem.Int32));
        idTexture.Parameters.Add(new ParameterDefinition(textureType));
        var numeric = new MethodDefinition("PropertyIdPublicSetTexture",
            Mono.Cecil.MethodAttributes.Public|Mono.Cecil.MethodAttributes.Static,
            m.TypeSystem.Void);
        numeric.Parameters.Add(new ParameterDefinition(m.TypeSystem.Object));
        td.Methods.Add(numeric);
        var lid=numeric.Body.GetILProcessor();
        lid.Append(lid.Create(OpCodes.Ldarg_0));
        lid.Append(lid.Create(OpCodes.Ldstr,"public-prop-id-name"));
        lid.Append(lid.Create(OpCodes.Call,propertyToId));
        lid.Append(lid.Create(OpCodes.Ldnull));
        lid.Append(lid.Create(OpCodes.Callvirt,idTexture));
        lid.Append(lid.Create(OpCodes.Ret));
        var throughId=FoamSetterFlow.Trace(numeric,1);
        if (throughId is null || throughId.Value.FirstArgRole!="property_id")
            throw new InvalidDataException("Original marker PropertyToID to SetTexture nameID fixture failed");
        Console.WriteLine("T2_FOAM_CECIL_SELFTEST " +
            JsonSerializer.Serialize(new {
                status = "synthetic_cecil_source_literal_controls_passed",
                matched_one_exact_public_literal = true,
                direct_adjacent_property_to_id_call_observed = true,
                fake_texture_setter_evidence_rejected = true,
                direct_original_name_to_settexture_first_arg_positive_fixture=true,
                same_window_false_positive_rejected=true,
                propertytoid_name_id_to_settexture_first_arg_fixture=true,
                second_operand_null_literal_proven_in_public_fixture=true,
                second_operand_static_field_load_proven_in_public_fixture=true,
                second_operand_argument_load_proven_in_public_fixture=true,
                second_formal_Texture_type_checked_without_runtime_claim=true,
                exact_producer_method_declared_return_type_traced=true,
                wrong_producer_return_type_rejected_as_Unity_Texture=true,
                producer_runtime_execution_not_claimed=true,
                actual_original_method_signature_and_body_fixture=true,
                source_class_declaring_same_assembly_without_real_definition_rejected=true,
                strict_original_managed_Texture_array_int_index_return_fixture=true,
                altered_extra_instruction_return_body_shape_rejected=true,
                guarded_original_texture_array_null_fallback_fixture=true,
                wrong_branch_target_guarded_texture_array_rejected=true,
                early_null_brtrue_guarded_RenderTexture_array_fixture=true,
                exact_backing_field_writer_newarr_null_decoy_fixture=true,
                strict_original_backing_field_serialization_metadata_fixtures=true,
                strict_original_field_load_address_typed_decoy_fixture=true,
                typed_byref_indirect_array_store_length_and_decoy_sink_controls=true,
                exact_byref_target_internal_body_and_wrong_signature_controls=true,
                strict_newarr_to_ref_array_same_block_and_cross_branch_negative_controls=true,
                private_compiled_allocation_length_inbounds_and_dynamic_negative_controls=true,
                source_original_length_same_block_local_arg_and_branch_controls=true,
                original_byref_caller_int_argument_direct_vs_dynamic_controls=true,
                original_rt_array_element_newobj_null_and_wrong_type_controls=true,
                exact_original_return_signature_vs_external_type_controls=true,
                exact_original_return_direct_null_newobj_and_branch_controls=true,
                synthetic_return_branch_target_and_local_predecessor_classifier=true,
                synthetic_exact_rt_return_local_writer_and_wrong_local_controls=true,
                synthetic_single_writer_prior_opcode_and_entry_controls=true,
                four_original_style_Texture_int_argument_origin_controls=true,
                signed_short_wide_and_duplicate_private_i4_aggregate_controls=true,
                private_IL_names_or_source_published = false
            }));
        return 0;
    }

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length == 1 && args[0] == "--selftest")
                return SelfTest();
            if (args.Length != 3)
                throw new ArgumentException("Exact private original assembly, targets, safe output required");
            string asmPath = Path.GetFullPath(args[0]);
            string targetPath = Path.GetFullPath(args[1]);
            string output = Path.GetFullPath(args[2]);
            if (!File.Exists(asmPath) || !File.Exists(targetPath) || File.Exists(output) ||
                output.StartsWith(Path.GetDirectoryName(asmPath)! + Path.DirectorySeparatorChar,
                                  StringComparison.Ordinal))
                throw new InvalidDataException("Invalid source/output path");
            byte[] original = File.ReadAllBytes(asmPath);
            if (original.Length != OriginalBytes || Convert.ToHexString(
                    SHA256.HashData(original)).ToLowerInvariant() != OriginalSha)
                throw new InvalidDataException("Original immutable Assembly-CSharp.dll SHA mismatch");
            using var privateSource = JsonDocument.Parse(File.ReadAllText(targetPath));
            var root = privateSource.RootElement;
            if (root.GetProperty("schema_version").GetInt32() != 1 ||
                root.GetProperty("source_kind").GetString() !=
                    "SHA_AUTHENTIC_ORIGINAL_FOAM_SHADER_TEXTURE_NAMES" ||
                root.GetProperty("original_source_texture_occurrences").GetInt32() != 6 ||
                root.GetProperty("original_distinct_source_texture_names").GetInt32() != 5 ||
                root.GetProperty("runtime_upload_proven").GetBoolean())
                throw new InvalidDataException("Unapproved original Shader name provenance");
            var non = ReadDigests(root,"non_authored_sha256",4);
            var author = ReadDigests(root,"authored_texture_sha256",1);
            if (non.Overlaps(author))
                throw new InvalidDataException("Ambiguous hashed private source register");
            using var assembly = AssemblyDefinition.ReadAssembly(asmPath,
                new ReaderParameters { ReadSymbols = false, ReadingMode = ReadingMode.Deferred });
            Summary scan = Scan(WalkTypes(assembly.MainModule.Types)
                                    .SelectMany(t => t.Methods),non,author);
            string safe = JsonSerializer.Serialize(PublicReport(scan,true,false));
            File.WriteAllText(output,safe + Environment.NewLine,new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
            Console.WriteLine("T2_FOAM_MANAGED_IL " + JsonSerializer.Serialize(new
            {
                status = "source_authenticated_original_managed_IL_static_scan_complete",
                original_dll_sha256_authenticated = true,
                distinct_original_non_property_texture_names_in_managed_IL =
                    scan.MatchedNonAuthored.Count,
                original_texture_runtime_upload_proven = false,
                private_names_or_IL_published = false
            }));
            return 0;
        }
        catch (Exception ex)
        {
            // Never emit original source/string/method/type/assembly names, paths,
            // decompiler output or exception messages; type only is safe.
            Console.WriteLine("T2_FOAM_MANAGED_IL " + JsonSerializer.Serialize(new
            {
                status = "blocked",
                exception_type = ex.GetType().Name,
                exact_managed_upload_dataflow_verified = false,
                private_names_or_IL_published = false
            }));
            return 2;
        }
    }
}
