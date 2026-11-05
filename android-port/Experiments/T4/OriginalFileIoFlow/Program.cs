// T4: privacy-safe ECMA-335 IO-control-flow evidence for the immutable original
// Raft FileManager read/write helpers. No original code, private identifiers,
// method tokens, paths, IL instructions, data bytes or game assets are printed.
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long OriginalSize = 3211776;
    private const string OriginalSha =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";

    private sealed record CallGroups(int system_io, int system_non_io,
        int same_original_filemanager, int other_original_or_external);

    private static CallGroups CategorizeCalls(IEnumerable<Instruction> instructions,
        TypeDefinition manager)
    {
        int io = 0, core = 0, internalMethods = 0, other = 0;
        foreach (var insn in instructions)
        {
            if (insn.OpCode.Code != Code.Call && insn.OpCode.Code != Code.Callvirt &&
                insn.OpCode.Code != Code.Newobj)
                continue;
            if (insn.Operand is not MethodReference callee)
                throw new InvalidDataException("unrecognized_original_compiled_call");
            string owner = callee.DeclaringType.FullName;
            if (owner.StartsWith("System.IO.", StringComparison.Ordinal)) io++;
            else if (owner == manager.FullName) internalMethods++;
            else if (owner.StartsWith("System.", StringComparison.Ordinal)) core++;
            else other++;
        }
        return new CallGroups(io, core, internalMethods, other);
    }

    private sealed record Edge(
        int parameter_count,
        string[] parameter_categories,
        string return_category,
        string direct_io_intent,
        int direct_io_call_count,
        int catch_handler_count,
        int finally_handler_count,
        bool catch_contains_leave,
        bool catch_contains_explicit_throw,
        bool catch_contains_null_literal,
        bool catch_can_exit_normally,
        bool exception_swallow_on_device_proven,
        CallGroups original_try_calls,
        CallGroups original_catch_calls,
        CallGroups original_outside_handler_calls,
        bool original_transitive_callees_executed);

    private static string TypeCategory(TypeReference type)
    {
        string name = type.FullName;
        if (name == "System.Void") return "void";
        if (name == "System.String") return "string";
        if (name == "System.Boolean") return "bool";
        if (name == "System.Byte[]") return "byte_array";
        if (name == "System.IO.Stream" || name == "System.IO.FileStream") return "stream";
        if (name == "System.IO.FileMode" || name == "System.IO.FileAccess" ||
            name == "System.IO.FileShare") return "io_enum";
        if (name == "System.Int32" || name == "System.Int64") return "integer";
        if (type is ByReferenceType) return "byref_other";
        return "other";
    }

    private static bool IsIoOperation(Instruction instruction, out MethodReference? operation)
    {
        operation = instruction.Operand as MethodReference;
        if (instruction.OpCode.Code != Code.Call &&
            instruction.OpCode.Code != Code.Callvirt &&
            instruction.OpCode.Code != Code.Newobj) return false;
        return operation is not null &&
               operation.DeclaringType.FullName.StartsWith("System.IO.", StringComparison.Ordinal);
    }

    private static string IoIntent(MethodReference callee)
    {
        string kind = callee.DeclaringType.FullName;
        string name = callee.Name;
        if (kind == "System.IO.File")
        {
            return name switch
            {
                "Open" or "OpenRead" or "OpenWrite" => "file_open",
                "Create" => "file_create",
                "Exists" => "file_exists",
                "ReadAllBytes" or "ReadAllText" or "ReadAllLines" => "file_read_all",
                "WriteAllBytes" or "WriteAllText" or "WriteAllLines" => "file_write_all",
                "Delete" => "file_delete",
                _ => "other_file_api"
            };
        }
        if (kind == "System.IO.FileStream")
            return name == ".ctor" ? "filestream_construct" : "other_filestream_api";
        if (kind == "System.IO.Directory")
            return name == "CreateDirectory" ? "create_directory" : "other_directory_api";
        return "other_io_api";
    }

    private static bool IsLeave(Code code) => code == Code.Leave || code == Code.Leave_S;
    private static bool IsThrow(Code code) => code == Code.Throw || code == Code.Rethrow;

    private static Edge Inspect(TypeDefinition manager, MethodReference reference, int expectedParameters)
    {
        MethodDefinition? target;
        try { target = reference.Resolve(); }
        catch (Exception) { throw new InvalidDataException("unresolved_original_reference"); }
        if (target is null || target.DeclaringType.FullName != manager.FullName ||
            !manager.Methods.Any(x => x.MetadataToken.ToInt32() == target.MetadataToken.ToInt32()) ||
            !target.IsStatic || !target.HasBody || target.Parameters.Count != expectedParameters)
            throw new InvalidDataException("wrong_compiled_original_target");

        var calls = target.Body.Instructions.Where(x => IsIoOperation(x, out _)).ToList();
        if (calls.Count != 1 || !IsIoOperation(calls[0], out MethodReference? bcl) ||
            bcl is null)
            throw new InvalidDataException("unexpected_io_operation_count");

        var catches = target.Body.ExceptionHandlers.Where(x => x.HandlerType == ExceptionHandlerType.Catch).ToList();
        var finalizers = target.Body.ExceptionHandlers.Where(x => x.HandlerType == ExceptionHandlerType.Finally).ToList();
        if (catches.Count != 1 || target.Body.ExceptionHandlers.Count != 1)
            throw new InvalidDataException("unexpected_original_handler_count");
        ExceptionHandler catchHandler = catches[0];
        var all = target.Body.Instructions;
        int start = all.IndexOf(catchHandler.HandlerStart);
        int end = catchHandler.HandlerEnd is null ? all.Count : all.IndexOf(catchHandler.HandlerEnd);
        if (start < 0 || end <= start || end > all.Count)
            throw new InvalidDataException("invalid_original_exception_handler_region");
        int tryStart = all.IndexOf(catchHandler.TryStart);
        int tryEnd = catchHandler.TryEnd is null ? all.Count : all.IndexOf(catchHandler.TryEnd);
        if (tryStart < 0 || tryEnd <= tryStart || tryEnd > all.Count ||
            (tryStart < end && start < tryEnd))
            throw new InvalidDataException("invalid_original_try_catch_regions");
        var inTry = all.Skip(tryStart).Take(tryEnd - tryStart).ToList();
        var handler = all.Skip(start).Take(end - start).ToList();
        var outside = all.Where((_, position) =>
            !(position >= tryStart && position < tryEnd) &&
            !(position >= start && position < end)).ToList();
        var tryCalls = CategorizeCalls(inTry, manager);
        var catchCalls = CategorizeCalls(handler, manager);
        var otherCalls = CategorizeCalls(outside, manager);
        int originalCallCount = all.Count(i => i.OpCode.Code == Code.Call ||
            i.OpCode.Code == Code.Callvirt || i.OpCode.Code == Code.Newobj);
        if (originalCallCount != 4 ||
            tryCalls.system_io + catchCalls.system_io + otherCalls.system_io != 1 ||
            tryCalls.same_original_filemanager + catchCalls.same_original_filemanager +
            otherCalls.same_original_filemanager != 1 ||
            tryCalls.system_non_io + catchCalls.system_non_io + otherCalls.system_non_io != 1 ||
            tryCalls.other_original_or_external + catchCalls.other_original_or_external +
            otherCalls.other_original_or_external != 1)
            throw new InvalidDataException("original_transitive_callee_profile_changed");
        bool hasLeave = handler.Any(i => IsLeave(i.OpCode.Code));
        bool hasThrow = handler.Any(i => IsThrow(i.OpCode.Code));
        bool hasNull = handler.Any(i => i.OpCode.Code == Code.Ldnull);
        return new Edge(
            target.Parameters.Count,
            target.Parameters.Select(p => TypeCategory(p.ParameterType)).ToArray(),
            TypeCategory(target.ReturnType),
            IoIntent(bcl),
            calls.Count,
            catches.Count,
            finalizers.Count,
            hasLeave,
            hasThrow,
            hasNull,
            hasLeave && !hasThrow,
            false,
            tryCalls,
            catchCalls,
            otherCalls,
            false);
    }

    private static MethodReference ExactlyOneCall(TypeDefinition manager, IEnumerable<MethodDefinition> from)
    {
        var calls = from.Where(m => m.HasBody)
            .SelectMany(m => m.Body.Instructions)
            .Where(i => i.OpCode.Code == Code.Call || i.OpCode.Code == Code.Callvirt)
            .Select(i => i.Operand as MethodReference)
            .Where(m => m is not null && m.DeclaringType.FullName == manager.FullName)
            .ToArray();
        if (calls.Length != 1 || calls[0] is null)
            throw new InvalidDataException("ambiguous_compiled_original_call_edge");
        return calls[0]!;
    }

    private static int Main(string[] args)
    {
        if (args.Length != 4 || args[0] != "--assembly" || args[2] != "--output")
        {
            Console.WriteLine("T4_ORIGINAL_IO_FLOW status=INVALID_ARGUMENTS private_details_published=false");
            return 2;
        }
        try
        {
            var file = new FileInfo(args[1]);
            if (!file.Exists || file.Length != OriginalSize || file.LinkTarget is not null)
                throw new InvalidDataException("unverified_binary_size_or_link");
            using (var stream = file.OpenRead())
            {
                string observed = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
                if (observed != OriginalSha)
                    throw new InvalidDataException("unverified_binary_hash");
            }
            using var assembly = AssemblyDefinition.ReadAssembly(file.FullName,
                new ReaderParameters { ReadSymbols = false });
            var managers = assembly.MainModule.Types.Where(t => t.Name == "FileManager").ToList();
            var savers = assembly.MainModule.Types.Where(t => t.Name == "SaveAndLoad").ToList();
            if (managers.Count != 1 || savers.Count != 1)
                throw new InvalidDataException("original_type_cardinality");
            var manager = managers.Single();
            var save = savers.Single();

            var read = ExactlyOneCall(manager,
                save.Methods.Where(m => m.Name == "Load" && m.HasGenericParameters));
            var write = ExactlyOneCall(manager, save.Methods.Where(m => m.Name == "Save"));
            if (read.MetadataToken.ToInt32() == write.MetadataToken.ToInt32())
                throw new InvalidDataException("read_write_target_not_distinct");
            var readShape = Inspect(manager, read, 2);
            var writeShape = Inspect(manager, write, 1);

            var result = new
            {
                schema_version = 1,
                source = "IMMUTABLE_ORIGINAL_COMPILED_IL",
                exact_dll_size_sha_verified = true,
                read_target_unique = true,
                write_target_unique = true,
                original_methods_distinct = true,
                read = readShape,
                write = writeShape,
                actual_file_io_invoked = false,
                real_rgd_reopened = false,
                android_or_unity_executed = false,
                original_source_or_private_symbols_published = false
            };
            string dest = Path.GetFullPath(args[3]);
            if (File.Exists(dest) || Directory.Exists(dest) ||
                Path.GetDirectoryName(dest) is null)
                throw new InvalidDataException("unsafe_output_exists");
            Directory.CreateDirectory(Path.GetDirectoryName(dest)!);
            File.WriteAllText(dest, JsonSerializer.Serialize(result));
            Console.WriteLine("T4_ORIGINAL_IO_FLOW " + JsonSerializer.Serialize(result));
            return 0;
        }
        catch (Exception)
        {
            Console.WriteLine("T4_ORIGINAL_IO_FLOW status=INCONCLUSIVE private_details_published=false");
            return 2;
        }
    }
}
