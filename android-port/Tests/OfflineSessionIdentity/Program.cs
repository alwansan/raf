using System;
using System.IO;
using RaftAndroid.Platform;

// Pure managed source fixture: no original Raft assets, Unity or device.
internal static class Program
{
    private static int checks;
    private static void Require(bool value, string description)
    {
        if (!value) throw new Exception("OFFLINE_SESSION_IDENTITY_FAIL: " + description);
        checks++;
    }

    private static void InvalidIdentityMustFail(string? identity, string label)
    {
        bool rejected = false;
        try { _ = new OfflineSession(identity!); }
        catch (ArgumentException) { rejected = true; }
        Require(rejected, "invalid profile was accepted: " + label);
    }

    // Verify the REAL compiled managed platform adapter, not a C# text
    // substring, requests persistence before returning the new profile ID.
    // A normal FileStream/StreamWriter.Dispose is not an fsync guarantee.
    private static void AssertProfileFirstCreateFlushBoundary()
    {
        var method = typeof(LocalProfileStore).GetMethod(nameof(LocalProfileStore.GetOrCreateProfileId));
        Require(method != null, "Missing actual profile creation method");
        var body = method!.GetMethodBody();
        Require(body != null, "Missing compiled profile creation body");
        byte[] instructions = body!.GetILAsByteArray() ?? throw new Exception("Missing original profile IL");
        var opcodes = new System.Collections.Generic.Dictionary<ushort, System.Reflection.Emit.OpCode>();
        foreach (var field in typeof(System.Reflection.Emit.OpCodes).GetFields(
                     System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Static))
        {
            if (field.GetValue(null) is System.Reflection.Emit.OpCode op)
                opcodes[unchecked((ushort)op.Value)] = op;
        }
        int flushOffset = -1;
        int p = 0;
        while (p < instructions.Length)
        {
            int start = p;
            ushort value = instructions[p++] == 0xFE
                ? (ushort)(0xFE00 | instructions[p++])
                : (ushort)instructions[start];
            Require(opcodes.TryGetValue(value, out var opcode), "Unrecognized compiled IL opcode");
            var kind = opcode.OperandType;
            int operandWidth = kind switch
            {
                System.Reflection.Emit.OperandType.InlineNone => 0,
                System.Reflection.Emit.OperandType.ShortInlineBrTarget or
                System.Reflection.Emit.OperandType.ShortInlineI or
                System.Reflection.Emit.OperandType.ShortInlineVar => 1,
                System.Reflection.Emit.OperandType.InlineVar => 2,
                System.Reflection.Emit.OperandType.InlineI8 or
                System.Reflection.Emit.OperandType.InlineR => 8,
                System.Reflection.Emit.OperandType.InlineSwitch => 4 + 4 * BitConverter.ToInt32(instructions, p),
                _ => 4
            };
            Require(p + operandWidth <= instructions.Length, "Truncated compiled source IL");
            if (kind == System.Reflection.Emit.OperandType.InlineMethod)
            {
                var called = method.Module.ResolveMethod(BitConverter.ToInt32(instructions, p));
                if (called?.DeclaringType == typeof(FileStream) && called.Name == "Flush")
                {
                    var parameters = called.GetParameters();
                    if (parameters.Length == 1 && parameters[0].ParameterType == typeof(bool))
                        flushOffset = start;
                }
            }
            p += operandWidth;
        }
        Require(flushOffset >= 0, "New profile ID never requests FileStream.Flush(true)");
        // A WriteLine/Flush exception must NOT enter the FileMode.CreateNew
        // collision catch just because the freshly-created path now exists.
        // The C# exception filter must guard ONLY opening the new file.
        var filters = body.ExceptionHandlingClauses;
        int filtered = 0;
        foreach (var handler in filters)
        {
            if (handler.Flags != System.Reflection.ExceptionHandlingClauseOptions.Filter)
                continue;
            filtered++;
            Require(flushOffset < handler.TryOffset ||
                    flushOffset >= handler.TryOffset + handler.TryLength,
                    "Write/flush exception is swallowed by profile CreateNew collision catch");
        }
        Require(filtered >= 1, "Original concurrent creator must retain collision-only catch");
    }

    public static int Main()
    {
        string root = Path.Combine(Path.GetTempPath(), "raft-a9-identity-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            string canonical = new LocalProfileStore(root).GetOrCreateProfileId();
            AssertProfileFirstCreateFlushBoundary();
            var session = new OfflineSession(canonical);
            Require(session.LocalProfileId == canonical && canonical.Length == 32,
                "normal generated ID must remain unchanged");
            Require(session.IsConnected && session.IsHost && session.IsSinglePlayer &&
                session.ConnectedPlayerCount == 1 && !session.UsesSteam && !session.UsesInternet,
                "valid local-only host semantics must remain unchanged");
            Require(LocalPlayerIdentity.FromProfile(canonical) > 0 &&
                LocalPlayerIdentity.FromProfile(canonical) == LocalPlayerIdentity.FromProfile(session.LocalProfileId),
                "original stable profile-derived ID must remain unchanged");
            Require(new LocalSavePaths(root, session.LocalProfileId).GetWorldDirectory("world_01")
                .Contains("world_01"), "valid local world path must remain available");

            InvalidIdentityMustFail(null, "null");
            InvalidIdentityMustFail("", "empty");
            InvalidIdentityMustFail("ab", "short");
            InvalidIdentityMustFail(new string('a', 31), "31 hex");
            InvalidIdentityMustFail(new string('a', 33), "33 hex");
            InvalidIdentityMustFail(new string('A', 32), "uppercase hex");
            InvalidIdentityMustFail(new string('g', 32), "nonhex");
            InvalidIdentityMustFail("../external", "path traversal");
            InvalidIdentityMustFail(new string('a', 31) + "/", "path separator");
            InvalidIdentityMustFail("local", "would be accepted by old prototype but not original profile store");
            Console.WriteLine("A9_OFFLINE_SESSION_IDENTITY_PASS checks=" + checks);
            return 0;
        }
        finally
        {
            try { Directory.Delete(root, recursive: true); } catch (IOException) { }
        }
    }
}
