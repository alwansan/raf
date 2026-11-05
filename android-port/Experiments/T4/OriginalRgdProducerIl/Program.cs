// T4 LOCAL-005: private exact-original compiled-IL producer and Save edge counts.
// No game code execution, original source, raw IL, type member names or RGD bytes
// are published. Presence of newobj and Save call does NOT establish a full
// dynamic argument-value flow or device playability.
using System.Security.Cryptography;
using System.Text.Json;
using Mono.Cecil;
using Mono.Cecil.Cil;

internal static class Program
{
    private const long OriginalBytes = 3211776;
    private const string OriginalSha256 =
        "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e";

    private static bool IsCall(Instruction i) =>
        i.OpCode.Code == Code.Call || i.OpCode.Code == Code.Callvirt;

    private static bool IsPrivateSaveRgdTarget(MethodReference m, TypeDefinition owner,
        MethodDefinition save, string rgdType) =>
        m.DeclaringType.FullName == owner.FullName &&
        m.Name == save.Name && m.HasThis &&
        m.ReturnType.FullName == "System.Void" &&
        m.Parameters.Count == 2 &&
        m.Parameters[0].ParameterType.FullName == "System.String" &&
        m.Parameters[1].ParameterType.FullName == rgdType;

    private static int CountRgdConstructor(MethodDefinition method, string rgdType) =>
        method.Body.Instructions.Count(i =>
            i.OpCode.Code == Code.Newobj &&
            i.Operand is MethodReference m &&
            m.Name == ".ctor" &&
            m.DeclaringType.FullName == rgdType);

    private static int CountRgdFieldStores(MethodDefinition method, string rgdType) =>
        method.Body.Instructions.Count(i => i.OpCode.Code == Code.Stfld &&
            i.Operand is FieldReference f && f.DeclaringType.FullName == rgdType);

    private static int Main(string[] args)
    {
        if (args.Length != 4 || args[0] != "--assembly" || args[2] != "--output")
        {
            Console.WriteLine("T4_ORIGINAL_RGD_PRODUCER status=INVALID_ARGUMENTS source_published=false");
            return 2;
        }
        try
        {
            var original = new FileInfo(Path.GetFullPath(args[1]));
            if (!original.Exists || original.LinkTarget is not null ||
                original.Length != OriginalBytes)
                throw new InvalidDataException("Original original bytes not authenticated");
            using (var input = original.OpenRead())
            {
                if (Convert.ToHexString(SHA256.HashData(input))
                    .ToLowerInvariant() != OriginalSha256)
                    throw new InvalidDataException("Original assembly SHA did not match");
            }

            using var dll = AssemblyDefinition.ReadAssembly(original.FullName,
                new ReaderParameters { ReadSymbols = false });
            var owners = dll.MainModule.Types.Where(t =>
                t.Name == "SaveAndLoad" && t.FullName == "SaveAndLoad").ToArray();
            if (owners.Length != 1)
                throw new InvalidDataException("Original SaveAndLoad owner ambiguous");
            var owner = owners[0];

            static MethodDefinition UniqueVoidNoArgs(TypeDefinition owner, string name)
            {
                var methods = owner.Methods.Where(m => m.HasBody && m.Name == name &&
                    !m.IsStatic && m.ReturnType.FullName == "System.Void" &&
                    m.Parameters.Count == 0).ToArray();
                if (methods.Length != 1)
                    throw new InvalidDataException("Original required method not unique");
                return methods[0];
            }
            MethodDefinition world = UniqueVoidNoArgs(owner, "SaveWorld");
            MethodDefinition user = UniqueVoidNoArgs(owner, "SaveUser");
            var candidates = owner.Methods.Where(m =>
                m.HasBody && m.Name == "Save" &&
                !m.IsStatic && !m.IsPublic && !m.HasGenericParameters &&
                m.ReturnType.FullName == "System.Void" &&
                m.Parameters.Count == 2 &&
                m.Parameters[0].ParameterType.FullName == "System.String" &&
                m.Parameters[1].ParameterType.Name == "RGD").ToArray();
            if (candidates.Length != 1)
                throw new InvalidDataException("Original exact Save RGD signature ambiguous");
            var save = candidates[0];
            string rgdType = save.Parameters[1].ParameterType.FullName;
            if (!dll.MainModule.Types.Any(t => t.FullName == rgdType))
                throw new InvalidDataException("Original RGD type not in authenticated DLL");

            var worldSaveCalls = world.Body.Instructions
                .Where(IsCall)
                .Select(i => i.Operand as MethodReference)
                .Where(m => m is not null &&
                    m.DeclaringType.FullName == owner.FullName && m.Name == "Save")
                .Select(m => m!).ToArray();
            var userSaveCalls = user.Body.Instructions
                .Where(IsCall)
                .Select(i => i.Operand as MethodReference)
                .Where(m => m is not null &&
                    m.DeclaringType.FullName == owner.FullName && m.Name == "Save")
                .Select(m => m!).ToArray();
            int worldExact = worldSaveCalls.Count(m =>
                IsPrivateSaveRgdTarget(m, owner, save, rgdType));
            int userExact = userSaveCalls.Count(m =>
                IsPrivateSaveRgdTarget(m, owner, save, rgdType));
            int worldCtor = CountRgdConstructor(world, rgdType);
            int userCtor = CountRgdConstructor(user, rgdType);
            int worldRgdLocals = world.Body.Variables.Count(v =>
                v.VariableType.FullName == rgdType);
            int userRgdLocals = user.Body.Variables.Count(v =>
                v.VariableType.FullName == rgdType);

            var report = new
            {
                schema_version = 1,
                scope = "EXACT_ORIGINAL_COMPILED_IL_READ_ONLY",
                original_managed_dll_size_sha_verified = true,
                original_saveandload_owner_unique = true,
                original_saveworld_unique = true,
                original_saveuser_unique = true,
                original_private_save_rgd_signature_unique = true,
                world_direct_calls_to_exact_save_rgd = worldExact,
                world_other_calls_named_save = worldSaveCalls.Length - worldExact,
                user_direct_calls_to_exact_save_rgd = userExact,
                user_other_calls_named_save = userSaveCalls.Length - userExact,
                world_direct_rgd_constructor_calls = worldCtor,
                user_direct_rgd_constructor_calls = userCtor,
                world_rgd_typed_locals = worldRgdLocals,
                user_rgd_typed_locals = userRgdLocals,
                world_rgd_field_stores = CountRgdFieldStores(world, rgdType),
                direct_constructor_is_dynamically_proven_save_argument = false,
                original_save_method_invoked = false,
                game_world_rgd_written_or_loaded = false,
                source_or_rgd_payload_published = false,
                android_unity_il2cpp_or_phone_executed = false,
            };
            string target = Path.GetFullPath(args[3]);
            if (File.Exists(target) || Directory.Exists(target) ||
                new FileInfo(target).LinkTarget is not null)
                throw new InvalidDataException("Report destination already occupied");
            Directory.CreateDirectory(Path.GetDirectoryName(target)!);
            File.WriteAllText(target, JsonSerializer.Serialize(report));
            Console.WriteLine("T4_ORIGINAL_RGD_PRODUCER " + JsonSerializer.Serialize(report));
            return 0;
        }
        catch (Exception)
        {
            Console.WriteLine("T4_ORIGINAL_RGD_PRODUCER status=INCONCLUSIVE " +
                "private_game_data_logged=false original_method_invoked=false");
            return 2;
        }
    }
}
