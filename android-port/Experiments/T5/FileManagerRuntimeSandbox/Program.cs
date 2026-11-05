// Execute only SHA-authenticated original FileManager read/write IL against a
// disposable synthetic file. No original private symbols or compiler text leave CI.
// This is Linux managed CLR smoke, NOT Unity, Android or serialized .rgd proof.
using System.Reflection;
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const string OriginalSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";
    private const long OriginalBytes = 3211776;
    private static readonly byte[] Fixture = System.Text.Encoding.ASCII.GetBytes(
        "T5-FILEMANAGER-MANAGED-ROUNDTRIP\nThis is not a game save.\n");

    private static MethodDefinition SingleEdge(TypeDefinition owner, TypeDefinition manager, bool load)
    {
        var callers = owner.Methods.Where(m =>
            load ? m.Name == "Load" && m.HasGenericParameters : m.Name == "Save");
        var edges = callers.Where(m => m.HasBody)
            .SelectMany(m => m.Body.Instructions)
            .Where(x => x.OpCode.Code == Code.Call || x.OpCode.Code == Code.Callvirt)
            .Select(x => x.Operand as MethodReference)
            .Where(x => x != null && x.DeclaringType.FullName == manager.FullName)
            .Cast<MethodReference>().ToList();
        if (edges.Count != 1)
            throw new InvalidDataException("ambiguous_method_edge");
        var method = edges[0].Resolve();
        if (method == null || !manager.Methods.Any(m => m.MetadataToken.ToInt32() ==
                method.MetadataToken.ToInt32()) || !method.IsStatic || !method.HasBody)
            throw new InvalidDataException("unresolved_method_body");
        return method;
    }

    private static bool SafeCalleeScope(MethodDefinition method)
    {
        // Only permit an extremely small original method with no external
        // network/Unity/Steam/Process/Environment calls, and no async behavior.
        // The one direct System.IO call and EH observed at CI42012597665 remain
        // invariants. Reject unfamiliar opcodes instead of executing guesses.
        var methods = method.Body.Instructions
            .Where(x => x.OpCode.Code == Code.Call || x.OpCode.Code == Code.Callvirt ||
                        x.OpCode.Code == Code.Newobj)
            .Select(x => x.Operand as MethodReference).ToList();
        return methods.Count == 1 && methods[0] != null &&
               methods[0]!.DeclaringType.FullName.StartsWith("System.IO.", StringComparison.Ordinal)
               && method.Body.ExceptionHandlers.Count == 1
               && method.Body.Instructions.Count <= 20;
    }

    private static string Classify(Exception e)
    {
        var root = e is TargetInvocationException tie && tie.InnerException != null
            ? tie.InnerException : e;
        return root switch
        {
            FileNotFoundException => "MISSING_FILE",
            DirectoryNotFoundException => "MISSING_DIRECTORY",
            UnauthorizedAccessException => "ACCESS_DENIED",
            System.TypeLoadException => "DEPENDENCY_UNRESOLVED",
            FileLoadException => "DEPENDENCY_LOAD_FAILED",
            NotSupportedException => "UNSUPPORTED_RUNTIME",
            ArgumentException => "ARGUMENT_REJECTED",
            IOException => "FILE_IO_FAILURE",
            _ => "UNKNOWN_RUNTIME_FAILURE"
        };
    }

    private static object?[] Arguments(MethodInfo method, string file, bool second)
    {
        var parameters = method.GetParameters();
        if (parameters.Length < 1 || parameters.Length > 2 ||
            parameters.Count(p => p.ParameterType == typeof(string)) != 1 ||
            parameters.Any(p => p.ParameterType != typeof(string) &&
                                 p.ParameterType != typeof(bool)))
            throw new NotSupportedException();
        return parameters.Select(p => p.ParameterType == typeof(string)
            ? (object?)file : (object?)second).ToArray();
    }

    private static string Outcome(MethodInfo read, string file)
    {
        foreach (bool second in new[] { false, true })
        {
            object? result = read.Invoke(null, Arguments(read, file, second));
            try
            {
                if (result is Stream s)
                {
                    using var bytes = new MemoryStream();
                    s.CopyTo(bytes);
                    if (bytes.ToArray().SequenceEqual(Fixture)) return "EXACT_BYTES";
                }
                else if (result is byte[] bytes && bytes.SequenceEqual(Fixture))
                    return "EXACT_BYTES";
                else if (result != null)
                    return "UNSUPPORTED_READ_RETURN";
            }
            finally
            {
                if (result is IDisposable disposable) disposable.Dispose();
            }
        }
        return "BYTES_MISMATCH";
    }

    private static int Main(string[] args)
    {
        // Fail closed on directory existence: only runner-provided disposable
        // scratch paths can be used; no user's actual .rgd files are accessed.
        if (args.Length != 4 || args[0] != "--assembly" || args[2] != "--scratch")
        {
            Console.WriteLine("T5_FILEMANAGER_RUNTIME status=INVALID_ARGUMENTS");
            return 2;
        }
        var stage = "SOURCE_PIN";
        bool verified = false, bounded = false, invoked = false, exact = false;
        string outcome = "INCONCLUSIVE", error = "NONE";
        try
        {
            var original = new FileInfo(args[1]);
            if (original.Length != OriginalBytes) throw new InvalidDataException();
            using (var data = original.OpenRead())
            {
                if (Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant() != OriginalSha)
                    throw new InvalidDataException();
            }
            verified = true;
            stage = "COMPILED_IL_GUARD";
            using var metadata = AssemblyDefinition.ReadAssembly(original.FullName);
            var manager = metadata.MainModule.Types.Single(t => t.Name == "FileManager");
            var owner = metadata.MainModule.Types.Single(t => t.Name == "SaveAndLoad");
            var read = SingleEdge(owner, manager, true);
            var write = SingleEdge(owner, manager, false);
            if (read.MetadataToken.ToInt32() == write.MetadataToken.ToInt32() ||
                !SafeCalleeScope(read) || !SafeCalleeScope(write))
                throw new NotSupportedException();
            bounded = true;
            stage = "SCRATCH_GUARD";
            var root = Path.GetFullPath(args[3]);
            // The shell creates an empty private dir, and the tool never writes
            // anywhere else intentionally. Absolute paths only, no linked roots.
            if (!Path.IsPathFullyQualified(args[3]) || !Directory.Exists(root) ||
                Directory.EnumerateFileSystemEntries(root).Any() ||
                new DirectoryInfo(root).Attributes.HasFlag(FileAttributes.ReparsePoint))
                throw new UnauthorizedAccessException();
            var file = Path.Combine(root, "t5-synthetic-original-path.rgd");
            stage = "ORIGINAL_MANAGED_INVOCATION";
            // No other assembly is invoked except the two verified original
            // bounded methods; .NET/Unity missing deps are inconclusive.
            var loaded = Assembly.LoadFrom(original.FullName);
            var writeMethod = loaded.ManifestModule.ResolveMethod(write.MetadataToken.ToInt32())
                as MethodInfo ?? throw new TypeLoadException();
            var readMethod = loaded.ManifestModule.ResolveMethod(read.MetadataToken.ToInt32())
                as MethodInfo ?? throw new TypeLoadException();
            if (writeMethod.ReturnType != typeof(Stream) &&
                !typeof(Stream).IsAssignableFrom(writeMethod.ReturnType))
                throw new NotSupportedException();
            var stream = writeMethod.Invoke(null, Arguments(writeMethod, file, false)) as Stream
                ?? throw new NotSupportedException();
            using (stream)
            {
                stream.Write(Fixture);
                stream.Flush();
            }
            invoked = true;
            if (File.Exists(file) && new FileInfo(file).Length == Fixture.Length)
            {
                outcome = Outcome(readMethod, file);
                exact = outcome == "EXACT_BYTES";
            }
            else outcome = "FILE_NOT_CREATED";
        }
        catch (Exception exc)
        {
            error = Classify(exc);
            outcome = "INCONCLUSIVE";
        }
        Console.WriteLine("T5_FILEMANAGER_RUNTIME " + JsonSerializer.Serialize(new {
            schema_version = 1, status = exact ? "MANAGED_SYNTHETIC_ROUNDTRIP" : outcome,
            original_sha_verified = verified,
            static_compiled_call_safety_guard = bounded,
            original_managed_methods_invoked = invoked,
            synthetic_bytes_exact_readback = exact,
            failed_phase = exact ? "NONE" : stage,
            failure_category = exact ? "NONE" : error,
            original_rgd_serialization_proven = false,
            original_world_or_unity_or_android_proven = false,
            private_method_names_or_original_bytes_disclosed = false
        }));
        return exact ? 0 : 2;
    }
}
