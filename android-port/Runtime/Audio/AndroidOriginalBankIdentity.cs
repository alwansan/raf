using System;
using System.IO;
using System.Security.Cryptography;

namespace RaftAndroid.Audio
{
    // Original v1.1.01 bank identities independently checked against the
    // owner's six-part archive and the tracked original StreamingAssets.
    // Check the actual bytes read from APK/OBB before passing them to FMOD.
    public static class AndroidOriginalBankIdentity
    {
        public static void Verify(string name, byte[] bytes)
        {
            if (bytes == null) throw new ArgumentNullException(nameof(bytes));
            switch (name)
            {
                case "MasterBank.bank":
                    VerifyExact(bytes, 101600960, "10d310416b9f104a38b4ead8877e114142e154efb33105fcddbb2024a81af339");
                    return;
                case "MasterBank.strings.bank":
                    VerifyExact(bytes, 29530, "72cd8d60b0cd84b28359dd06dd1a73f2e00cb77f9d9e9b572e4d87db0cf01896");
                    return;
                case "VO_logs_english.bank":
                    VerifyExact(bytes, 11455008, "60783fd0c9f935313732ab253e604091674b4e8d0c06a3ac92ba09a1aa1e51cb");
                    return;
                case "VO_npc_english.bank":
                    VerifyExact(bytes, 8180896, "3e5c01e25feab18183b6ae90d39fb703800fc40a5580bf59f8af83538978f028");
                    return;
                case "VO_olof_english.bank":
                    VerifyExact(bytes, 2551104, "9eaa50efd40309443a4c704353fdff185b8262466abf676b723a8c753f36b230");
                    return;
                default:
                    throw new InvalidDataException("Unknown original FMOD bank identity: " + name);
            }
        }

        // Same compilation unit as the cheap C# audio harness; no original
        // bank payload is bundled in tests or logs.
        internal static void VerifyExact(byte[] bytes, long expectedLength, string expectedSha256)
        {
            if (bytes == null) throw new ArgumentNullException(nameof(bytes));
            if (string.IsNullOrEmpty(expectedSha256) || expectedSha256.Length != 64)
                throw new ArgumentException("Expected a 64-digit SHA-256", nameof(expectedSha256));
            if (bytes.LongLength != expectedLength)
                throw new InvalidDataException("Original FMOD bank byte count mismatch");
            using (SHA256 sha = SHA256.Create())
            {
                string actual = BitConverter.ToString(sha.ComputeHash(bytes))
                    .Replace("-", "").ToLowerInvariant();
                if (!string.Equals(actual, expectedSha256, StringComparison.Ordinal))
                    throw new InvalidDataException("Original FMOD bank SHA-256 mismatch");
            }
        }
    }
}
