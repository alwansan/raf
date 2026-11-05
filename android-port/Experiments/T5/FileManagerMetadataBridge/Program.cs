// T5: independent ECMA-335 metadata oracle for authentic Raft FileManager calls.
// No original managed binary, decompiled source, method names or IL are published.
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long OriginalSize = 3211776;
    private const string OriginalSha256 =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";

    private sealed record Edge(
        bool resolved,
        bool declared_in_filemanager,
        bool static_target,
        bool has_il_body,
        int? parameter_count,
        int? il_instruction_count,
        int? direct_system_io_call_sites,
        int? exception_handler_count);

    private static List<MethodReference> DirectCalls(
        TypeDefinition manager, IEnumerable<MethodDefinition> callers)
    {
        return callers.Where(method => method.HasBody)
            .SelectMany(method => method.Body.Instructions)
            .Where(instruction => instruction.OpCode.Code == Code.Call ||
                                  instruction.OpCode.Code == Code.Callvirt)
            .Select(instruction => instruction.Operand as MethodReference)
            .Where(reference => reference is not null &&
                   reference.DeclaringType.FullName == manager.FullName)
            .Cast<MethodReference>().ToList();
    }

    private static Edge ResolveEdge(TypeDefinition manager, MethodReference reference)
    {
        MethodDefinition? target = null;
        try { target = reference.Resolve(); }
        catch (AssemblyResolutionException) { /* Unknown, never claim absent. */ }
        catch (ResolutionException) { /* Unknown, never claim absent. */ }
        bool sameType = target is not null &&
                        target.DeclaringType.FullName == manager.FullName &&
                        manager.Methods.Any(method => method.MetadataToken == target.MetadataToken);
        if (!sameType || target is null)
            return new Edge(false, false, false, false, null, null, null, null);
        bool hasBody = target.HasBody;
        int? ioCalls = hasBody
            ? target.Body.Instructions.Count(instruction =>
                (instruction.OpCode.Code == Code.Call ||
                 instruction.OpCode.Code == Code.Callvirt ||
                 instruction.OpCode.Code == Code.Newobj) &&
                instruction.Operand is MethodReference callee &&
                callee.DeclaringType.FullName.StartsWith("System.IO.", StringComparison.Ordinal))
            : null;
        return new Edge(true, true, target.IsStatic, hasBody,
            target.Parameters.Count,
            hasBody ? target.Body.Instructions.Count : null,
            ioCalls,
            hasBody ? target.Body.ExceptionHandlers.Count : null);
    }

    private static int Main(string[] args)
    {
        if (args.Length != 4 || args[0] != "--assembly" || args[2] != "--output")
        {
            Console.WriteLine("T5_FILEMANAGER_METADATA status=INVALID_ARGUMENTS");
            return 2;
        }
        try
        {
            var original = new FileInfo(args[1]);
            if (!original.Exists || original.Length != OriginalSize)
                throw new InvalidDataException("size");
            using (var input = original.OpenRead())
            {
                string sha = Convert.ToHexString(SHA256.HashData(input)).ToLowerInvariant();
                if (!string.Equals(sha, OriginalSha256, StringComparison.Ordinal))
                    throw new InvalidDataException("sha");
            }
            using var assembly = AssemblyDefinition.ReadAssembly(
                original.FullName, new ReaderParameters { ReadSymbols = false });
            var types = assembly.MainModule.Types;
            var managerTypes = types.Where(type => type.Name == "FileManager").ToList();
            var saveTypes = types.Where(type => type.Name == "SaveAndLoad").ToList();
            if (managerTypes.Count != 1 || saveTypes.Count != 1)
                throw new InvalidDataException("type_cardinality");

            var manager = managerTypes[0];
            var save = saveTypes[0];
            var readEdges = DirectCalls(manager,
                save.Methods.Where(method => method.Name == "Load" && method.HasGenericParameters));
            var writeEdges = DirectCalls(manager,
                save.Methods.Where(method => method.Name == "Save"));
            // T4 authenticated lexical sources observed exactly one call per
            // method family; do not silently select an arbitrary overload.
            if (readEdges.Count != 1 || writeEdges.Count != 1)
                throw new InvalidDataException("call_cardinality");

            var read = ResolveEdge(manager, readEdges[0]);
            var write = ResolveEdge(manager, writeEdges[0]);
            bool targetsResolved = read.resolved && read.has_il_body &&
                                   write.resolved && write.has_il_body;
            var report = new
            {
                schema_version = 1,
                source = "SHA_PINNED_ORIGINAL_MANAGED_DLL",
                original_dll_sha256_verified = true,
                original_dll_bytes = OriginalSize,
                read_direct_call_count = readEdges.Count,
                write_direct_call_count = writeEdges.Count,
                read,
                write,
                both_target_bodies_resolved = targetsResolved,
                inspected_compiled_il_not_decompiler_text = true,
                file_write_readback_executed = false,
                rgd_reopen_or_android_device_proven = false,
                private_identifiers_or_il_published = false
            };
            var output = Path.GetFullPath(args[3]);
            if (File.Exists(output) || Directory.Exists(output))
                throw new InvalidDataException("destination_exists");
            Directory.CreateDirectory(Path.GetDirectoryName(output)!);
            File.WriteAllText(output, JsonSerializer.Serialize(report));
            Console.WriteLine("T5_FILEMANAGER_METADATA " + JsonSerializer.Serialize(report));
            return targetsResolved ? 0 : 2;
        }
        catch (Exception)
        {
            // Private exception strings, path names and original symbols stay
            // off public CI. Preserve a nonzero inconclusive result.
            Console.WriteLine("T5_FILEMANAGER_METADATA status=INCONCLUSIVE private_source_logged=false");
            return 2;
        }
    }
}
