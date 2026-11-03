using System;
using System.Formats.Nrbf;
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

try
{
    if (args.Length != 4 || args[0] != "--file" || args[2] != "--sha256")
        throw new ArgumentException("Usage: --file <pinned-original-rgd> --sha256 <expected-original-hash>");
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
    Console.WriteLine("RAFT_ZIP2_RGD_NBRF negativeControls=3/3 sameSourceDeterministic=true unityRuntimeVerified=false actualSaveLoadVerified=false");
    return 0;
}
catch (Exception ex)
{
    Console.Error.WriteLine("RAFT_ZIP2_RGD_NBRF FAIL " + ex.GetType().Name + ": " + ex.Message);
    return 1;
}
