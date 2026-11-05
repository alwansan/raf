// T4 LOCAL-005: strict SHA-pinned private original RGD Save/Load read-write experiment.
// Never publish game RGD bytes, original type names, private paths or exception text.
// Execution is permitted only after original IL reachability and target checks.
using System.Reflection;
using System.Runtime.CompilerServices;
using Mono.Cecil;
using Mono.Cecil.Cil;
using System.Runtime.Loader;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.RegularExpressions;

internal static class Program
{
    private const long OriginalDllSize = 3211776;
    private const string OriginalDllSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";
    private const long OriginalSeedSize = 2941;
    private const string OriginalSeedSha =
        "b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba";

    private static bool OriginalFile(string path, long length, string digest)
    {
        var info = new FileInfo(path);
        if (!info.Exists || info.Length != length || info.LinkTarget is not null)
            return false;
        using var input = info.OpenRead();
        return Convert.ToHexString(SHA256.HashData(input)).ToLowerInvariant() == digest;
    }

    private static string FailureCategory(Exception e)
    {
        Exception root = e;
        for (int i = 0; i < 3; i++)
        {
            if (root is TargetInvocationException tie && tie.InnerException is not null)
                root = tie.InnerException;
            else if (root is TypeInitializationException init && init.InnerException is not null)
                root = init.InnerException;
            else break;
        }

        return root switch
        {
            SerializationException => "SERIALIZATION_OR_ORIGINAL_SCHEMA",
            FileNotFoundException => "MANAGED_DEPENDENCY_MISSING",
            FileLoadException => "MANAGED_DEPENDENCY_LOAD_FAILURE",
            TypeLoadException => "ORIGINAL_TYPE_LOAD_FAILURE",
            MissingMethodException => "ORIGINAL_METHOD_BINDING_UNAVAILABLE",
            PlatformNotSupportedException => "RUNTIME_PLATFORM_UNSUPPORTED",
            NotSupportedException => "RUNTIME_API_UNSUPPORTED",
            UnauthorizedAccessException => "ACCESS_DENIED",
            IOException => "RUNTIME_FILE_IO",
            OutOfMemoryException => "RESOURCE_LIMIT",
            _ => "OTHER_ISOLATED_RUNTIME_ERROR"
        };
    }

    private static void InstallLocalReferenceResolver(string managed)
    {
        AssemblyLoadContext.Default.Resolving += (context, requested) =>
        {
            string name = requested.Name ?? "";
            if (!Regex.IsMatch(name, @"\A[A-Za-z0-9_.-]{1,128}\z") ||
                name == "." || name == "..") return null;
            string filename = Path.Combine(managed, name + ".dll");
            try
            {
                var candidate = new FileInfo(filename);
                if (!candidate.Exists || candidate.LinkTarget is not null) return null;
                return context.LoadFromAssemblyPath(candidate.FullName);
            }
            catch (Exception)
            {
                // An original missing runtime dependency remains an observable
                // deserialize failure. No arbitrary remote assembly resolving.
                return null;
            }
        };
    }


    private static MethodDefinition? AuditOriginalPrivateSave(
        string assemblyPath, Type originalRootType, out int safeCallCount, out string auditCategory)
    {
        safeCallCount = 0;
        auditCategory = "NO_EXACT_PRIVATE_SAVE_SIGNATURE";
        using var defs = AssemblyDefinition.ReadAssembly(
            assemblyPath, new ReaderParameters { ReadSymbols = false });
        var saveTypes = defs.MainModule.Types
            .Where(t => t.Name == "SaveAndLoad").ToArray();
        if (saveTypes.Length != 1)
        {
            auditCategory = "ORIGINAL_SAVE_CLASS_IDENTITY_MISSING";
            return null;
        }
        var matchingShape = saveTypes[0].Methods
            .Where(m => m.Name == "Save" && !m.IsStatic && !m.IsPublic &&
                !m.HasGenericParameters && m.HasBody &&
                m.ReturnType.FullName == "System.Void" &&
                m.Parameters.Count == 2 &&
                m.Parameters[0].ParameterType.FullName == "System.String")
            .ToArray();
        if (matchingShape.Length != 1)
        {
            auditCategory = "ORIGINAL_SAVE_PRIVATE_SIGNATURE_SHAPE_MISSING";
            return null;
        }
        var matches = matchingShape
            .Where(m => m.Parameters[1].ParameterType.Name == originalRootType.Name)
            .ToArray();
        if (matches.Length != 1)
        {
            // Report only structural relation to known RGD argument, not
            // either original CLR type name or metadata values.
            auditCategory = matchingShape[0].Parameters[1].ParameterType.Name == "RGD"
                ? "SHIPPED_SEED_ROOT_DIFFERS_FROM_ORIGINAL_RGD_SAVE_ARGUMENT"
                : "ORIGINAL_SAVE_ARGUMENT_DIFFERS_FROM_SHIPPED_SEED_ROOT";
            return null;
        }
        var candidate = matches[0];
        if (candidate.Body.Instructions.Count > 500 ||
            candidate.Body.ExceptionHandlers.Count > 2)
        {
            auditCategory = "UNEXPECTED_ORIGINAL_SAVE_IL_COMPLEXITY";
            return null;
        }
        bool create = false, serialize = false;
        var handlers = candidate.Body.ExceptionHandlers;
        if (handlers.Any(h => h.HandlerType != ExceptionHandlerType.Catch))
        {
            auditCategory = "UNEXPECTED_ORIGINAL_SAVE_EXCEPTION_REGION";
            return null;
        }
        var instructions = candidate.Body.Instructions;
        for (int i = 0; i < instructions.Count; ++i)
        {
            var insn = instructions[i];
            if (insn.OpCode.Code is Code.Ldfld or Code.Ldflda or Code.Stfld or
                Code.Ldsfld or Code.Ldsflda or Code.Stsfld or Code.Calli or
                Code.Stobj or Code.Ldftn or Code.Ldvirtftn)
            {
                auditCategory = "ORIGINAL_SAVE_FIELD_OR_INDIRECT_ACCESS";
                return null;
            }
            if (insn.OpCode.Code != Code.Call &&
                insn.OpCode.Code != Code.Callvirt &&
                insn.OpCode.Code != Code.Newobj) continue;
            if (insn.Operand is not MethodReference called)
            {
                auditCategory = "UNKNOWN_ORIGINAL_SAVE_CALL_OPERAND";
                return null;
            }
            // Reject any original game or Unity runtime action, except the
            // authenticated FileManager path. One known Unity Debug error
            // printer may be present in the original catch only; do not
            // permit it in the original success path.
            bool insideCatch = handlers.Any(h =>
            {
                int start = instructions.IndexOf(h.HandlerStart);
                int end = h.HandlerEnd is null ? instructions.Count :
                    instructions.IndexOf(h.HandlerEnd);
                return i >= start && i < end;
            });
            string owner = called.DeclaringType.FullName;
            bool fileManager = called.DeclaringType.Name == "FileManager" &&
                called.Name == "CreateFile";
            bool formatter = owner ==
                "System.Runtime.Serialization.Formatters.Binary.BinaryFormatter" &&
                called.Name == "Serialize";
            bool safeBcl = owner.StartsWith("System.IO.", StringComparison.Ordinal) ||
                owner.StartsWith("System.Runtime.Serialization.Formatters.Binary.",
                    StringComparison.Ordinal) ||
                owner is "System.String" or "System.Object" or
                    "System.Exception" or "System.IDisposable";
            bool catchOnlyDebug = insideCatch &&
                owner == "UnityEngine.Debug" &&
                called.Name.StartsWith("Log", StringComparison.Ordinal);
            if (!fileManager && !safeBcl && !catchOnlyDebug)
            {
                auditCategory = insideCatch
                    ? "UNKNOWN_ORIGINAL_SAVE_CATCH_CALLEE"
                    : "UNKNOWN_ORIGINAL_SAVE_SUCCESS_CALLEE";
                return null;
            }
            if (fileManager && !insideCatch) create = true;
            if (formatter && !insideCatch) serialize = true;
            safeCallCount++;
        }
        auditCategory = create && serialize ? "NONE" :
            "ORIGINAL_SAVE_EXPECTED_CREATE_OR_SERIALIZE_MISSING";
        return create && serialize ? candidate : null;
    }

    private static int Main(string[] args)
    {
        if ((args.Length != 6 && (args.Length != 7 || args[6] != "--original-save-roundtrip")) ||
            args[0] != "--assembly" || args[2] != "--seed" || args[4] != "--output")
        {
            Console.WriteLine("T4_ORIGINAL_RGD_DESERIALIZE status=INVALID_ARGUMENTS source_published=false");
            return 2;
        }
        try
        {
            string assemblyPath = Path.GetFullPath(args[1]);
            string seedPath = Path.GetFullPath(args[3]);
            string reportPath = Path.GetFullPath(args[5]);
            if (File.Exists(reportPath) || Directory.Exists(reportPath) ||
                new FileInfo(reportPath).LinkTarget is not null ||
                !OriginalFile(assemblyPath, OriginalDllSize, OriginalDllSha) ||
                !OriginalFile(seedPath, OriginalSeedSize, OriginalSeedSha))
                throw new InvalidDataException("original_source_authentication_failed");

            string refs = Path.GetDirectoryName(assemblyPath)
                ?? throw new InvalidDataException("original_managed_directory_missing");
            var companionPaths = Directory.GetFiles(refs, "*.dll")
                .Where(p => Path.GetFileName(p) != "Assembly-CSharp.dll")
                .ToArray();
            if (companionPaths.Length != 151 ||
                companionPaths.Any(p => new FileInfo(p).LinkTarget is not null))
                throw new InvalidDataException("original_managed_companion_context_incomplete");

            InstallLocalReferenceResolver(refs);
            var original = AssemblyLoadContext.Default.LoadFromAssemblyPath(assemblyPath);
            bool originalIdentity = original.GetName().Name == "Assembly-CSharp";
            if (!originalIdentity)
                throw new InvalidDataException("unexpected_original_managed_identity");

            bool success = false;
            Type? originalRootType = null;
            bool rootFromOriginalAssembly = false;
            object? seedRootObject = null;
            string category = "NONE";
            // Input is *only* the fixed SHA-authenticated 2941 byte shipped
            // file; arbitrary user-supplied serialization is never accepted.
            // Always try only once, never log exception strings or inner data.
            try
            {
                AppContext.SetSwitch(
                    "System.Runtime.Serialization.EnableUnsafeBinaryFormatterSerialization", true);
                using var input = File.OpenRead(seedPath);
#pragma warning disable SYSLIB0011
                var serializer = new BinaryFormatter();
                object? result = serializer.Deserialize(input);
#pragma warning restore SYSLIB0011
                success = result is not null;
                seedRootObject = result;
                rootFromOriginalAssembly = result?.GetType().Assembly == original;
                if (rootFromOriginalAssembly) originalRootType = result!.GetType();
                if (!success) category = "DESERIALIZED_NULL";
            }
            catch (Exception e)
            {
                category = FailureCategory(e);
            }

            // No actual original SaveAndLoad.Load<T> or persistent world file
            // has been executed. Success only pertains to this shipped seed
            // in this isolated .NET 8 runtime, not Unity Mono or Android.
            bool exerciseLoadT = args.Length == 7;
            bool originalLoadMethodFound = false;
            bool originalLoadInvoked = false;
            bool originalLoadReturnedMatchingType = false;
            string originalLoadCategory = "NOT_REQUESTED";
            if (exerciseLoadT)
            {
                if (originalRootType is null)
                    originalLoadCategory = "ORIGINAL_ROOT_TYPE_UNAVAILABLE";
                else
                {
                    try
                    {
                        Type? saveAndLoad = original.GetType("SaveAndLoad", throwOnError: false);
                        var matching = saveAndLoad?.GetMethods(BindingFlags.Public |
                                BindingFlags.NonPublic | BindingFlags.Static)
                            .Where(m => m.Name == "Load" && m.IsGenericMethodDefinition &&
                                m.GetGenericArguments().Length == 1 &&
                                m.ReturnType.IsGenericParameter &&
                                m.GetParameters().Length == 1 &&
                                m.GetParameters()[0].ParameterType == typeof(string))
                            .ToArray() ?? Array.Empty<MethodInfo>();
                        originalLoadMethodFound = matching.Length == 1;
                        if (!originalLoadMethodFound)
                            originalLoadCategory = "ORIGINAL_METHOD_BINDING_UNAVAILABLE";
                        else
                        {
                            var concrete = matching[0].MakeGenericMethod(originalRootType);
                            originalLoadInvoked = true;
                            object? loaded = concrete.Invoke(null, new object[] { seedPath });
                            originalLoadReturnedMatchingType =
                                loaded is not null && loaded.GetType() == originalRootType;
                            originalLoadCategory = originalLoadReturnedMatchingType
                                ? "NONE" : "RETURNED_DEFAULT_OR_NONMATCHING_TYPE";
                        }
                    }
                    catch (Exception ex)
                    {
                        originalLoadCategory = FailureCategory(ex);
                    }
                }
            }


            bool saveIlGuard = false;
            bool savedOriginalObjectByGameMethod = false;
            bool savedFileNonzero = false;
            bool savedFileExisted = false;
            bool loadedSavedObjectByGameMethod = false;
            bool removedTemp = false;
            string saveCategory = "ORIGINAL_ROOT_TYPE_UNAVAILABLE";
            int safeSaveCalls = 0;
            string saveAuditCategory = "NOT_AUDITED";
            string? workDirectory = null;
            if (originalRootType is not null)
            {
                try
                {
                    var audited = AuditOriginalPrivateSave(
                        assemblyPath, originalRootType, out safeSaveCalls,
                        out saveAuditCategory);
                    saveIlGuard = audited is not null;
                    if (!saveIlGuard)
                    {
                        saveCategory = saveAuditCategory;
                    }
                    else
                    {
                        var saveType = original.GetType("SaveAndLoad",
                            throwOnError: false);
                        var method = saveType?.GetMethods(
                                BindingFlags.Instance | BindingFlags.Public |
                                BindingFlags.NonPublic)
                            .Where(m => m.MetadataToken ==
                                audited!.MetadataToken.ToInt32())
                            .ToArray() ?? Array.Empty<MethodInfo>();
                        if (method.Length != 1 ||
                            method[0].GetParameters().Length != 2 ||
                            method[0].GetParameters()[0].ParameterType != typeof(string) ||
                            method[0].GetParameters()[1].ParameterType != originalRootType ||
                            method[0].ReturnType != typeof(void))
                        {
                            saveCategory = "ORIGINAL_SAVE_REFLECTION_SIGNATURE_MISMATCH";
                        }
                        else
                        {
                            workDirectory = Path.Combine(Path.GetTempPath(),
                                "t4-rgd-output-" + Guid.NewGuid().ToString("N"));
                            Directory.CreateDirectory(workDirectory);
                            string savedPath = Path.Combine(workDirectory,
                                "isolated-shipped-seed-roundtrip.rgd");
                            // No Unity lifecycle; fail closed if original
                            // instance type cannot be allocated safely.
                            object target = RuntimeHelpers.GetUninitializedObject(saveType!);
                            method[0].Invoke(target,
                                new object?[] { savedPath, seedRootObject });
                            savedOriginalObjectByGameMethod = true;
                            savedFileExisted = File.Exists(savedPath);
                            savedFileNonzero = savedFileExisted &&
                                new FileInfo(savedPath).Length > 0L;
                            if (savedFileNonzero && originalLoadMethodFound)
                            {
                                var loadMethod = saveType!.GetMethods(
                                        BindingFlags.Static |
                                        BindingFlags.Public | BindingFlags.NonPublic)
                                    .Single(m => m.Name == "Load" &&
                                        m.IsGenericMethodDefinition &&
                                        m.GetParameters().Length == 1 &&
                                        m.GetParameters()[0].ParameterType == typeof(string))
                                    .MakeGenericMethod(originalRootType);
                                object? loaded = loadMethod.Invoke(
                                    null, new object?[] { savedPath });
                                loadedSavedObjectByGameMethod = loaded is not null &&
                                    loaded.GetType() == originalRootType;
                            }
                            saveCategory = loadedSavedObjectByGameMethod
                                ? "NONE" : "GENUINE_SAVE_OR_LOAD_ROUNDTRIP_UNVERIFIED";
                        }
                    }
                }
                catch (Exception e)
                {
                    saveCategory = FailureCategory(e);
                }
                finally
                {
                    if (workDirectory is not null)
                    {
                        try
                        {
                            Directory.Delete(workDirectory, recursive: true);
                            removedTemp = !Directory.Exists(workDirectory);
                        }
                        catch (Exception) { removedTemp = false; }
                    }
                }
            }

            var report = new Dictionary<string, object?>
            {
                ["schema_version"] = 1,
                ["source"] = "IMMUTABLE_SHA_VERIFIED_ORIGINAL_RGD_SEED",
                ["original_dll_sha_verified"] = true,
                ["original_seed_sha_verified"] = true,
                ["managed_reference_siblings"] = companionPaths.Length,
                ["original_CLR_assembly_loaded"] = true,
                ["formatter_runtime"] = "DOTNET8_BINARYFORMATTER",
                ["actual_formatter_deserialize_attempted"] = true,
                ["actual_formatter_deserialize_object_created"] = success,
                ["deserialized_root_defined_in_original_dll"] = rootFromOriginalAssembly,
                ["bounded_runtime_category"] = category,
                ["original_SaveAndLoad_LoadT_invoked"] = originalLoadInvoked,
                ["user_generated_game_world_loaded"] = false,
                ["real_game_rgd_write_or_roundtrip"] = false,
                ["android_unity_il2cpp_or_phone_executed"] = false,
                ["original_data_or_private_type_names_published"] = false,
                ["original_private_Save_IL_guard_passed"] = saveIlGuard,
                ["original_private_Save_safe_calls"] = safeSaveCalls,
                ["original_private_Save_audit_category"] = saveAuditCategory,
                ["original_private_Save_invoked"] = savedOriginalObjectByGameMethod,
                ["original_private_Save_output_created"] = savedFileExisted,
                ["original_private_Save_output_nonzero"] = savedFileNonzero,
                ["original_private_Save_generated_LoadT_matching_root"] = loadedSavedObjectByGameMethod,
                ["original_private_Save_isolated_temp_removed"] = removedTemp,
                ["original_private_Save_result_category"] = saveCategory,
            };
            if (exerciseLoadT)
            {
                report["original_LoadT_method_signature_verified"] = originalLoadMethodFound;
                report["original_LoadT_returned_matching_seed_type"] = originalLoadReturnedMatchingType;
                report["original_LoadT_result_category"] = originalLoadCategory;
            }

            Directory.CreateDirectory(Path.GetDirectoryName(reportPath)!);
            File.WriteAllText(reportPath, JsonSerializer.Serialize(report));
            Console.WriteLine("T4_ORIGINAL_RGD_DESERIALIZE " + JsonSerializer.Serialize(report));
            return 0;
        }
        catch (Exception)
        {
            Console.WriteLine(
                "T4_ORIGINAL_RGD_DESERIALIZE status=ORIGINAL_INTAKE_INCONCLUSIVE " +
                "private_exception_or_payload_logged=false");
            return 2;
        }
    }
}
