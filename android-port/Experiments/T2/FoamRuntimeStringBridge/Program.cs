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
        foreach (var method in methods)
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
