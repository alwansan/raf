// T4: execute only the two ORIGINAL SHA-authenticated FileManager file-stream
// helpers on an isolated synthetic file. No Unity, game .rgd serialization,
// private IL/method names, original game source, or user files are published.
using System.Reflection;
using System.Runtime.Loader;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long OriginalSize = 3211776;
    private const string OriginalSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";

    private static MethodReference FindOriginalEdge(TypeDefinition manager, IEnumerable<MethodDefinition> callers)
    {
        var references = callers.Where(method => method.HasBody)
            .SelectMany(method => method.Body.Instructions)
            .Where(insn => insn.OpCode.Code == Code.Call || insn.OpCode.Code == Code.Callvirt)
            .Select(insn => insn.Operand as MethodReference)
            .Where(reference => reference is not null &&
                   reference.DeclaringType.FullName == manager.FullName)
            .ToArray();
        if (references.Length != 1 || references[0] is null)
            throw new InvalidDataException("ambiguous_original_target");
        return references[0]!;
    }

    private static MethodDefinition ResolveExact(
        TypeDefinition manager, MethodReference reference, string bclName, int argc)
    {
        MethodDefinition? method;
        try { method = reference.Resolve(); }
        catch (Exception) { throw new InvalidDataException("cannot_resolve_original_target"); }
        if (method is null || !method.HasBody || !method.IsStatic ||
            method.DeclaringType.FullName != manager.FullName ||
            method.Parameters.Count != argc ||
            !manager.Methods.Any(m => m.MetadataToken.ToInt32() == method.MetadataToken.ToInt32()) ||
            method.ReturnType.FullName != "System.IO.FileStream")
            throw new InvalidDataException("original_compiled_shape_mismatch");
        if (method.Parameters[0].ParameterType.FullName != "System.String")
            throw new InvalidDataException("original_path_type_drift");
        if (argc == 2 && method.Parameters[1].ParameterType.FullName != "System.IO.FileMode")
            throw new InvalidDataException("original_file_mode_drift");
        var calls = method.Body.Instructions
            .Where(i => (i.OpCode.Code == Code.Call || i.OpCode.Code == Code.Callvirt ||
                         i.OpCode.Code == Code.Newobj) && i.Operand is MethodReference callee &&
                    callee.DeclaringType.FullName.StartsWith("System.IO.", StringComparison.Ordinal))
            .Select(i => (MethodReference)i.Operand)
            .ToArray();
        if (calls.Length != 1 || calls[0].DeclaringType.FullName != "System.IO.File" ||
            calls[0].Name != bclName || method.Body.ExceptionHandlers.Count != 1 ||
            method.Body.ExceptionHandlers[0].HandlerType != ExceptionHandlerType.Catch)
            throw new InvalidDataException("original_file_io_path_drift");
        return method;
    }

    private static string ErrorCategory(Exception problem)
    {
        var root = problem is TargetInvocationException tie && tie.InnerException is not null
            ? tie.InnerException : problem;
        return root switch
        {
            FileNotFoundException => "DEPENDENCY_OR_FILE_MISSING",
            DirectoryNotFoundException => "DIRECTORY_MISSING",
            FileLoadException => "DEPENDENCY_LOAD_FAILURE",
            TypeLoadException => "DEPENDENCY_TYPE_UNAVAILABLE",
            ReflectionTypeLoadException => "REFLECTION_TYPE_LOAD_FAILURE",
            MissingMethodException => "METHOD_UNAVAILABLE",
            BadImageFormatException => "UNSUPPORTED_ORIGINAL_BINARY_RUNTIME",
            PlatformNotSupportedException => "UNSUPPORTED_PLATFORM",
            NotSupportedException => "UNSUPPORTED_RUNTIME",
            UnauthorizedAccessException => "ACCESS_DENIED",
            IOException => "IO_FAILURE",
            ArgumentException => "ARGUMENT_MISMATCH",
            _ => "OTHER_RUNTIME_FAILURE"
        };
    }

    private static void RequireBclOnlyOriginalSuccessPath(MethodDefinition method)
    {
        var all = method.Body.Instructions;
        if (method.Body.ExceptionHandlers.Count != 1 ||
            method.Body.ExceptionHandlers[0].HandlerType != ExceptionHandlerType.Catch)
            throw new InvalidDataException("unexpected_original_exception_regions");
        var catchRegion = method.Body.ExceptionHandlers[0];
        int tryStart = all.IndexOf(catchRegion.TryStart);
        int tryEnd = catchRegion.TryEnd is null ? all.Count : all.IndexOf(catchRegion.TryEnd);
        int catchStart = all.IndexOf(catchRegion.HandlerStart);
        int catchEnd = catchRegion.HandlerEnd is null ? all.Count : all.IndexOf(catchRegion.HandlerEnd);
        if (tryStart < 0 || tryEnd <= tryStart || catchStart < 0 || catchEnd <= catchStart)
            throw new InvalidDataException("original_compiled_flow_unresolved");
        int tryCalls = 0, catchCalls = 0, outsideCalls = 0;
        for (int i = 0; i < all.Count; i++)
        {
            var insn = all[i];
            if (insn.OpCode.Code != Code.Call && insn.OpCode.Code != Code.Callvirt &&
                insn.OpCode.Code != Code.Newobj) continue;
            if (insn.Operand is not MethodReference callee)
                throw new InvalidDataException("unrecognized_original_call_operand");
            if (i >= tryStart && i < tryEnd)
            {
                tryCalls++;
                // This is specifically the previous T4 original-CIL proof:
                // success path has only the ONE File.Open/Create BCL call.
                if (callee.DeclaringType.FullName != "System.IO.File" ||
                    (callee.Name != "Open" && callee.Name != "Create"))
                    throw new InvalidDataException("unsafe_original_try_transitive_call");
            }
            else if (i >= catchStart && i < catchEnd) catchCalls++;
            else outsideCalls++;
        }
        // Entire genuine method has 4 calls: 1 original IO within try and
        // 3 logging/helper dependencies strictly confined to catch. This
        // restricts which execution path is safe to exercise in the sandbox.
        if (tryCalls != 1 || catchCalls != 3 || outsideCalls != 0)
            throw new InvalidDataException("unknown_original_transitive_callee_placement");
    }

    private static void RegisterPrivateManagedCompanionResolver(string directory)
    {
        AssemblyLoadContext.Default.Resolving += (ctx, reference) =>
        {
            string? simple = reference.Name;
            if (string.IsNullOrEmpty(simple) || simple.Length > 128 ||
                simple.Contains('/') || simple.Contains('\\') ||
                simple == "." || simple == "..") return null;
            string candidate = Path.Combine(directory, simple + ".dll");
            try
            {
                if (!File.Exists(candidate) ||
                    new FileInfo(candidate).LinkTarget is not null) return null;
                return ctx.LoadFromAssemblyPath(candidate);
            }
            catch (Exception) { return null; }
        };
    }

    private static int Main(string[] args)
    {
        if (args.Length != 4 || args[0] != "--assembly" || args[2] != "--output")
        {
            Console.WriteLine("T4_ORIGINAL_STREAM_ROUNDTRIP status=INVALID_ARGS private_details_published=false");
            return 2;
        }
        string phase = "original_sha";
        string? work = null;
        try
        {
            var original = new FileInfo(args[1]);
            if (!original.Exists || original.Length != OriginalSize || original.LinkTarget is not null)
                throw new InvalidDataException("unverified_original_bytes");
            using (var stream = original.OpenRead())
            {
                string hash = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
                if (hash != OriginalSha) throw new InvalidDataException("unverified_original_sha");
            }
            phase = "compiled_call_edges";
            using var assembly = AssemblyDefinition.ReadAssembly(original.FullName,
                new ReaderParameters { ReadSymbols = false });
            var managers = assembly.MainModule.Types.Where(t => t.Name == "FileManager").ToList();
            var saves = assembly.MainModule.Types.Where(t => t.Name == "SaveAndLoad").ToList();
            if (managers.Count != 1 || saves.Count != 1)
                throw new InvalidDataException("ambiguous_original_game_types");
            var manager = managers.Single();
            var save = saves.Single();
            var readRef = FindOriginalEdge(manager,
                save.Methods.Where(m => m.Name == "Load" && m.HasGenericParameters));
            var writeRef = FindOriginalEdge(manager, save.Methods.Where(m => m.Name == "Save"));
            var read = ResolveExact(manager, readRef, "Open", 2);
            var write = ResolveExact(manager, writeRef, "Create", 1);
            RequireBclOnlyOriginalSuccessPath(read);
            RequireBclOnlyOriginalSuccessPath(write);
            if (read.MetadataToken.ToInt32() == write.MetadataToken.ToInt32())
                throw new InvalidDataException("original_read_write_edge_collision");

            phase = "runtime_reflection";
            RegisterPrivateManagedCompanionResolver(
                Path.GetDirectoryName(original.FullName)!);
            var loaded = AssemblyLoadContext.Default.LoadFromAssemblyPath(original.FullName);
            var type = loaded.GetType(manager.FullName, throwOnError: true)
                ?? throw new InvalidDataException("missing_reflection_type");
            var flags = BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
            var reflected = type.GetMethods(flags);
            var readMethod = reflected.SingleOrDefault(m => m.MetadataToken == read.MetadataToken.ToInt32());
            var writeMethod = reflected.SingleOrDefault(m => m.MetadataToken == write.MetadataToken.ToInt32());
            if (readMethod is null || writeMethod is null ||
                readMethod.ReturnType != typeof(FileStream) || writeMethod.ReturnType != typeof(FileStream))
                throw new InvalidDataException("original_reflection_target_drift");

            // The original method is given only a new directory owned by this
            // process; never follow a supplied filename, user save or symlink.
            phase = "temporary_sandbox";
            work = Path.Combine(Path.GetTempPath(), "t4-authentic-fileio-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(work);
            string testPath = Path.Combine(work, "synthetic-data-not-game-save.rgd");
            byte[] fixture = Encoding.ASCII.GetBytes(
                "T4 authenticated original FileManager managed stream test v1\n");
            phase = "original_create";
            var opened = writeMethod.Invoke(null, new object?[] { testPath });
            if (opened is not FileStream output || !output.CanWrite)
                throw new InvalidDataException("original_write_stream_unavailable");
            using (output)
            {
                output.Write(fixture, 0, fixture.Length);
                output.Flush(flushToDisk: true);
            }

            phase = "original_reopen";
            var openedRead = readMethod.Invoke(null, new object?[] { testPath, FileMode.Open });
            if (openedRead is not FileStream input || !input.CanRead)
                throw new InvalidDataException("original_read_stream_unavailable");
            byte[] observed;
            using (input)
            using (var mem = new MemoryStream())
            {
                input.CopyTo(mem);
                observed = mem.ToArray();
            }

            phase = "independent_contents";
            bool equal = fixture.SequenceEqual(observed);
            bool pathExists = File.Exists(testPath);
            bool lengthEqual = new FileInfo(testPath).Length == fixture.Length;
            if (!equal || !pathExists || !lengthEqual)
                throw new InvalidDataException("original_stream_roundtrip_mismatch");
            phase = "cleanup";
            Directory.Delete(work, recursive: true);
            work = null;
            var result = new
            {
                schema_version = 1,
                source = "SHA_PINNED_ORIGINAL_FILEMANAGER_INVOKED",
                original_managed_dll_authenticated = true,
                original_read_write_edges_verified = true,
                original_create_method_executed = true,
                stream_closed_before_original_open = true,
                original_open_method_executed = true,
                synthetic_bytes_equal_after_reopen = true,
                synthetic_file_size_equal = true,
                temporary_file_cleanup_verified = true,
                synthetic_filename_extension = ".rgd",
                real_game_rgd_serialization_executed = false,
                actual_android_app_storage_tested = false,
                unity_or_il2cpp_executed = false,
                private_game_data_or_identifiers_published = false
            };
            string outputPath = Path.GetFullPath(args[3]);
            if (File.Exists(outputPath) || Directory.Exists(outputPath) ||
                Path.GetDirectoryName(outputPath) is null)
                throw new InvalidDataException("invalid_output_path");
            Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
            File.WriteAllText(outputPath, JsonSerializer.Serialize(result));
            Console.WriteLine("T4_ORIGINAL_STREAM_ROUNDTRIP " + JsonSerializer.Serialize(result));
            return 0;
        }
        catch (Exception error)
        {
            // A failed private original invocation cannot be presented as
            // proof of incompatibility; do not expose raw stack/symbols/paths.
            Console.WriteLine("T4_ORIGINAL_STREAM_ROUNDTRIP status=INCONCLUSIVE phase=" +
                phase + " category=" + ErrorCategory(error) +
                " original_game_data_published=false");
            return 2;
        }
        finally
        {
            if (work is not null)
            {
                try { if (Directory.Exists(work)) Directory.Delete(work, recursive: true); }
                catch (Exception) { /* Private temp cleanup best effort on failed trial. */ }
            }
        }
    }
}
