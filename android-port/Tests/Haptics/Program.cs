using System;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using RaftAndroid.Platform;

// CPU-only harness: link the ACTUAL production AndroidStreamingAssets.cs.
// Synthetic WAV-like bytes; original game WAV payloads are never copied or published.
internal static class Program
{
    static int assertions;

    static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
        assertions++;
    }

    static void Throws<T>(Action action, string message) where T : Exception
    {
        try { action(); }
        catch (T) { assertions++; return; }
        throw new InvalidOperationException(message);
    }

    static byte[] TestBytes(string name) => Encoding.ASCII.GetBytes("RIFF-TEST-ONLY-WAVE:" + name);

    static int Main(string[] args)
    {
        if (args.Length != 1) throw new ArgumentException("Supply git-tree-derived original filename manifest");
        string[] names = File.ReadAllLines(args[0]);
        Require(names.Length == 29, "Original tracked Haptics WAV count changed");
        Require(names.Distinct(StringComparer.Ordinal).Count() == names.Length, "Duplicate original filenames");
        Require(names.All(s => s.EndsWith(".wav", StringComparison.Ordinal) &&
                               !s.Contains('/') && !s.Contains('\\') && s != "." && s != ".."),
                "Unexpected original Haptics path");
        Require(names.Contains("SharkBiteRaftHaptics.wav") && names.Contains("Dynamite.wav"),
                "Original log-identified paths missing from manifest");

        string root = Path.Combine(Path.GetTempPath(), "raft-a5-haptics-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            string obb = Path.Combine(root, "main.80.com.alwansan.raft.androidtest.obb");
            using (var stream = File.Create(obb))
            using (var archive = new ZipArchive(stream, ZipArchiveMode.Create))
            {
                foreach (string name in names)
                {
                    var entry = archive.CreateEntry("assets/Haptics/" + name, CompressionLevel.Optimal);
                    using var dst = entry.Open();
                    var bytes = TestBytes(name);
                    dst.Write(bytes, 0, bytes.Length);
                }
            }
            string rootUri = "jar:" + new Uri(Path.GetFullPath(obb)).AbsoluteUri + "!/assets/Haptics/";
            foreach (string name in names)
            {
                byte[] expected = TestBytes(name);
                Require(AndroidStreamingAssets.ReadAllBytes(rootUri + name).SequenceEqual(expected),
                        "Standard OBB ZIP path did not return original entry: " + name);
                // The CL APK80 stack trace is THIS leading slash form, produced
                // by an original Path.Combine/GetFullPath call-site.
                Require(AndroidStreamingAssets.ReadAllBytes("/" + rootUri + name).SequenceEqual(expected),
                        "CL-observed /jar:file: path not normalized: " + name);
            }
            string ordinary = Path.Combine(root, "ordinary.wav");
            File.WriteAllBytes(ordinary, TestBytes("filesystem"));
            Require(AndroidStreamingAssets.ReadAllBytes(ordinary).SequenceEqual(TestBytes("filesystem")),
                    "Windows/non-jar local-file fallback changed");

            Throws<InvalidDataException>(() => AndroidStreamingAssets.ReadAllBytes(rootUri + "absent.wav"),
                "Missing original WAV must not become fake success");
            Throws<InvalidDataException>(() => AndroidStreamingAssets.ReadAllBytes(rootUri + "%2e%2e/ordinary.wav"),
                "Encoded archive traversal must be rejected");
            Throws<InvalidDataException>(() => AndroidStreamingAssets.ReadAllBytes("jar:file:/invalid.obb"),
                "Malformed archive URI must fail");
            Throws<InvalidDataException>(() => AndroidStreamingAssets.ReadAllBytes("jar:https://example.org/a.obb!/assets/Haptics/x.wav"),
                "Remote ZIP URI must not be accepted");
            Throws<InvalidDataException>(() => AndroidStreamingAssets.ReadAllBytes("/jar:https://example.org/a.obb!/assets/Haptics/x.wav"),
                "Leading-slash remote ZIP URI must not be accepted");
            string dup = Path.Combine(root, "dup.obb");
            using (var stream = File.Create(dup))
            using (var archive = new ZipArchive(stream, ZipArchiveMode.Create))
            {
                foreach (int index in Enumerable.Range(0, 2))
                {
                    using var dst = archive.CreateEntry("assets/Haptics/duplicate.wav").Open();
                    dst.WriteByte((byte)index);
                }
            }
            Throws<InvalidDataException>(() => AndroidStreamingAssets.ReadAllBytes(
                "jar:" + new Uri(Path.GetFullPath(dup)).AbsoluteUri + "!/assets/Haptics/duplicate.wav"),
                "Ambiguous duplicate ZIP entry must be rejected");
            Console.WriteLine($"RAFT_A5_HAPTICS_ARCHIVE originalTrackedWavs={names.Length} " +
                              $"archiveRoundTrips={names.Length * 2} assertions={assertions} " +
                              "syntheticOnly=true originalPayloadsRead=false unityRun=false deviceRun=false");
            return 0;
        }
        finally { Directory.Delete(root, true); }
    }
}
