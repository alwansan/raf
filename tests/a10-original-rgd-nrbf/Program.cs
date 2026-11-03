using System;
using System.Formats.Nrbf;
using System.Linq;
using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.IO;
using System.Security.Cryptography;
using System.Text;

static string Hash(byte[] data) => Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();

static (string RootKind, string RootTypeFingerprint, long Unread) Verify(byte[] bytes, string requiredSha)
{
    if (bytes.Length == 0 || !string.Equals(Hash(bytes), requiredSha, StringComparison.OrdinalIgnoreCase))
        throw new InvalidDataException("Original RGD SHA256 mismatch");
    if (!NrbfDecoder.StartsWithPayloadHeader(bytes))
        throw new InvalidDataException("Original RGD is not a complete NRBF header");
    using var input = new MemoryStream(bytes, writable: false);
    var root = NrbfDecoder.Decode(input, leaveOpen: true);
    if (root is not ClassRecord cls)
        throw new InvalidDataException("Original RGD root is not a class record");
    string identity = cls.TypeName.AssemblyQualifiedName;
    string typeHash = Hash(Encoding.UTF8.GetBytes(identity));
    return (root.RecordType.ToString(), typeHash, input.Length - input.Position);
}

static void MustReject(byte[] bytes, string sha, string name)
{
    try { Verify(bytes, sha); }
    catch (Exception e) when (e is InvalidDataException or EndOfStreamException or NotSupportedException
                             or System.Runtime.Serialization.SerializationException
                             or DecoderFallbackException)
    {
        Console.WriteLine($"RAFT_RGD_NEGATIVE {name}=rejected");
        return;
    }
    throw new InvalidDataException("Negative control was accepted: " + name);
}


static (bool RootTypeDefined, int TypesDefined, int OriginalFields, int SerializedMembers, int MatchingFields)
    CompareAuthenticAssembly(byte[] payload, byte[] managedAssembly, string expectedAssemblySha)
{
    if (!string.Equals(Hash(managedAssembly), expectedAssemblySha, StringComparison.OrdinalIgnoreCase))
        throw new InvalidDataException("Original Assembly-CSharp SHA256 mismatch");
    using var pe = new PEReader(new MemoryStream(managedAssembly, writable: false));
    if (!pe.HasMetadata)
        throw new InvalidDataException("Original managed image has no readable metadata");
    var meta = pe.GetMetadataReader();
    using var input = new MemoryStream(payload, writable: false);
    ClassRecord root = NrbfDecoder.DecodeClassRecord(input);
    var serialized = root.MemberNames.ToHashSet(StringComparer.Ordinal);
    var originalName = root.TypeName.FullName;
    foreach (var handle in meta.TypeDefinitions)
    {
        var type = meta.GetTypeDefinition(handle);
        string name = meta.GetString(type.Name);
        string ns = meta.GetString(type.Namespace);
        string fullName = string.IsNullOrEmpty(ns) ? name : ns + "." + name;
        if (!string.Equals(fullName, originalName, StringComparison.Ordinal))
            continue;
        var fields = type.GetFields().Select(h => meta.GetString(meta.GetFieldDefinition(h).Name))
            .ToHashSet(StringComparer.Ordinal);
        return (true, meta.TypeDefinitions.Count, fields.Count, serialized.Count, serialized.Count(fields.Contains));
    }
    return (false, meta.TypeDefinitions.Count, 0, serialized.Count, 0);
}

try
{
    if (args.Length != 8 || args[0] != "--file" || args[2] != "--sha256" || args[4] != "--assembly" || args[6] != "--assembly-sha256")
        throw new ArgumentException("Usage: --file <pinned-original-rgd> --sha256 <expected-original-hash> --assembly <pinned-original-assembly> --assembly-sha256 <expected-original-assembly-hash>");
    byte[] original = File.ReadAllBytes(args[1]);
    string expected = args[3];
    if (original.Length != 2941)
        throw new InvalidDataException("Unexpected original RGD byte count");
    var detail = Verify(original, expected);
    Console.WriteLine($"RAFT_ZIP2_RGD_NBRF originalSize={original.Length} originalSHA256={Hash(original)} rootKind={detail.RootKind} rootTypeFingerprint={detail.RootTypeFingerprint} remainingBytes={detail.Unread} executableDeserializer=false");
    MustReject(original, new string('0', 64), "mismatchedHash");
    var damagedHeader = (byte[])original.Clone();
    damagedHeader[0] = 0xff;
    MustReject(damagedHeader, Hash(damagedHeader), "damagedHeader");
    var truncated = original[..32];
    MustReject(truncated, Hash(truncated), "truncatedPayload");
    var twin = Verify((byte[])original.Clone(), expected);
    if (twin != detail) throw new InvalidDataException("Byte-identical original decoded inconsistently");
    byte[] originalManaged = File.ReadAllBytes(args[5]);
    if (originalManaged.Length != 3211776) throw new InvalidDataException("Unexpected original Assembly-CSharp byte count");
    var metadata = CompareAuthenticAssembly(original, originalManaged, args[7]);
    Console.WriteLine($"RAFT_ZIP2_RGD_ASSEMBLY originalManagedBytes={originalManaged.Length} assemblySHA256={Hash(originalManaged)} rootTypeDefinedInAssembly={metadata.RootTypeDefined} gameTypeDefinitions={metadata.TypesDefined} declaredFields={metadata.OriginalFields} serializedRootMembers={metadata.SerializedMembers} intersectingFields={metadata.MatchingFields} codeExecuted=false");
    try { CompareAuthenticAssembly(original, originalManaged, new string('0', 64)); throw new InvalidDataException("Assembly SHA negative accepted"); }
    catch (InvalidDataException ex) when (ex.Message.Contains("SHA256 mismatch", StringComparison.Ordinal)) { Console.WriteLine("RAFT_RGD_NEGATIVE mismatchedAssemblyHash=rejected"); }
    Console.WriteLine("RAFT_ZIP2_RGD_NBRF negativeControls=4/4 sameSourceDeterministic=true unityRuntimeVerified=false actualSaveLoadVerified=false");
    return 0;
}
catch (Exception ex)
{
    Console.Error.WriteLine("RAFT_ZIP2_RGD_NBRF FAIL " + ex.GetType().Name + ": " + ex.Message);
    return 1;
}
