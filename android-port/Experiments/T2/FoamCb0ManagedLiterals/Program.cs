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
                    var exact = Cb0ExactFirstFormal.Trace(items, row.Position);
                    if (exact.HasValue)
                    {
                        summary.ExactFirstFormalProvenNames.Add(row.Hash);
                        exactlyProvenSetterFamilies[exact.Value.SetterFamily] =
                            exactlyProvenSetterFamilies.GetValueOrDefault(exact.Value.SetterFamily) + 1;
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
    internal readonly record struct Evidence(string SetterFamily, string Kind);
    private enum Tag { Unknown, SourceString, SourcePropertyId }
    private const int MaxSteps = 24;
    private const int MaxStack = 64;

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

    internal static Evidence? Trace(IList<Instruction> instructions, int literalIndex)
    {
        if (literalIndex < 0 || literalIndex >= instructions.Count ||
            instructions[literalIndex].OpCode.Code != Code.Ldstr)
            return null;
        var stack = new List<Tag> { Tag.SourceString };
        var locals = new Dictionary<int, Tag>();
        Tag Pop()
        {
            if (stack.Count == 0) return Tag.Unknown;
            var v = stack[^1];
            stack.RemoveAt(stack.Count - 1);
            return v;
        }
        bool Push(Tag t)
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
                if (!Push(Tag.Unknown)) return null;
                continue;
            }
            if (name is "ldfld" or "ldflda")
            {
                Pop();
                if (!Push(Tag.Unknown)) return null;
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
                var formals = new Tag[method.Parameters.Count];
                for (int k = formals.Length - 1; k >= 0; k--)
                    formals[k] = Pop();
                if (ins.OpCode.Code != Code.Newobj && method.HasThis)
                    Pop();
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
                            formals[0] == Tag.SourceString)
                            return new Evidence(family,"source_literal_as_string");
                        if (firstType == "System.Int32" &&
                            formals[0] == Tag.SourcePropertyId)
                            return new Evidence(family,"source_literal_via_PropertyToID");
                    }
                }
                Tag result = Tag.Unknown;
                if (ins.OpCode.Code != Code.Newobj &&
                    method.DeclaringType.FullName == "UnityEngine.Shader" &&
                    method.Name == "PropertyToID" &&
                    method.Parameters.Count == 1 &&
                    method.Parameters[0].ParameterType.FullName == "System.String" &&
                    method.ReturnType.FullName == "System.Int32" &&
                    formals[0] == Tag.SourceString)
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
        if (Trace(direct,0)?.Kind != "source_literal_as_string")
            throw new InvalidOperationException("Exact first formal string positive");
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
        if (Trace(ids,0)?.Kind != "source_literal_via_PropertyToID")
            throw new InvalidOperationException("PropertyToID first formal positive");
    }
}
