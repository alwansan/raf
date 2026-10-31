using System;
using System.IO;
using System.Security.Cryptography;

namespace RaftAndroid.Editor
{
    // Lossless encoding of the ORIGINAL serialized property table, never a fallback.
    public static class PropertyTextureCore
    {
        public const int AttributeRows = 32;

        public static byte[] Encode(int width, float[] rgba)
        {
            if (width < 1 || width > 256 || rgba == null ||
                rgba.Length != width * AttributeRows * 4)
                throw new InvalidDataException("Original property table dimensions require inspection.");
            using (var stream = new MemoryStream())
            using (var writer = new BinaryWriter(stream))
            {
                foreach (float value in rgba)
                {
                    if (float.IsNaN(value) || float.IsInfinity(value))
                        throw new InvalidDataException("Original property table contains non-finite values.");
                    writer.Write(value); // Defined little-endian IEEE754 Float32.
                }
                return stream.ToArray();
            }
        }

        public static string Digest(byte[] bytes)
        {
            using (SHA256 hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        public static void RequireEqual(byte[] expected, byte[] actual)
        {
            if (expected == null || actual == null || expected.Length != actual.Length)
                throw new InvalidDataException("Property texture payload length changed.");
            for (int i = 0; i < expected.Length; i++)
                if (expected[i] != actual[i])
                    throw new InvalidDataException("Property texture payload differs from original values.");
        }
    }
}
