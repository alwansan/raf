// T4 LOCAL-005: Execute authentic BinaryFormatter.Deserialize against exactly
// one SHA-pinned original, shipped Raft Data.rgd in private CI. The runtime
// comparison is NOT an invocation of original SaveAndLoad.Load<T>, and is not
// a newly generated phone/world save. Never emit payload, serialized members,
// original runtime source, CLR stack traces, type names or filesystem paths.
using System.Reflection;
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

    private static int Main(string[] args)
    {
        if ((args.Length != 6 && (args.Length != 7 || args[6] != "--original-loadt")) ||
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
