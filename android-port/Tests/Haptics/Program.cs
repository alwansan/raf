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

    // Separate high-fidelity CPU lane. The original 29 WAV inputs stay in a
    // private GitHub Actions workspace and the temporary OBB is never uploaded.
    // A3's independent SHA/Git-blob source manifest gate runs before this lane.
    static int RunOriginalWavs(string sourceDirectory)
    {
        string[] paths = Directory.GetFiles(sourceDirectory, "*.wav", SearchOption.TopDirectoryOnly);
        Require(paths.Length == 29, "Expected all original tracked WAV files");
        Require(paths.Sum(p => new FileInfo(p).Length) == 32733104L,
                "Original total WAV byte length changed");
        Require(paths.All(p => Path.GetFileName(p).EndsWith(".wav", StringComparison.Ordinal)),
                "Unexpected original file extension");

        string temporary = Path.Combine(Path.GetTempPath(), "raft-a5-original-haptics-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(temporary);
        try
        {
            string obb = Path.Combine(temporary, "main.80.com.alwansan.raft.androidtest.obb");
            using (var stream = File.Create(obb))
            using (var zip = new ZipArchive(stream, ZipArchiveMode.Create))
            {
                foreach (string path in paths)
                {
                    var entry = zip.CreateEntry("assets/Haptics/" + Path.GetFileName(path), CompressionLevel.Optimal);
                    using var src = File.OpenRead(path);
                    using var dest = entry.Open();
                    src.CopyTo(dest);
                }
            }

            string jarRoot = "jar:" + new Uri(Path.GetFullPath(obb)).AbsoluteUri + "!/assets/Haptics/";
            long validated = 0;
            foreach (string path in paths)
            {
                string entry = Path.GetFileName(path);
                byte[] original = File.ReadAllBytes(path);
                byte[] originalHash = System.Security.Cryptography.SHA256.HashData(original);
                foreach (string prefix in new[] { "", "/" })
                {
                    byte[] extracted = AndroidStreamingAssets.ReadAllBytes(prefix + jarRoot + entry);
                    Require(extracted.Length == original.Length, "Original ZIP payload length changed");
                    Require(extracted.AsSpan().SequenceEqual(original), "Original ZIP payload bytes changed");
                    Require(System.Security.Cryptography.SHA256.HashData(extracted).AsSpan().SequenceEqual(originalHash),
                            "Original ZIP SHA-256 changed");
                    validated++;
                }
            }

            // A corrupt *but internally well-formed* OBB entry may be returned by
            // this byte reader. The external hash comparison catches it; do NOT
            // claim the production reader itself authenticates WAVs at runtime.
            string modified = Path.Combine(temporary, "tampered.obb");
            string victim = paths[0];
            byte[] originalVictim = File.ReadAllBytes(victim);
            byte[] altered = (byte[])originalVictim.Clone();
            altered[altered.Length / 2] ^= 1;
            using (var stream = File.Create(modified))
            using (var zip = new ZipArchive(stream, ZipArchiveMode.Create))
            using (var dst = zip.CreateEntry("assets/Haptics/" + Path.GetFileName(victim), CompressionLevel.Optimal).Open())
            {
                dst.Write(altered, 0, altered.Length);
            }
            byte[] testedAltered = AndroidStreamingAssets.ReadAllBytes(
                "jar:" + new Uri(Path.GetFullPath(modified)).AbsoluteUri +
                "!/assets/Haptics/" + Path.GetFileName(victim));
            Require(!testedAltered.AsSpan().SequenceEqual(originalVictim),
                    "Tamper negative control did not change content");
            Require(!System.Security.Cryptography.SHA256.HashData(testedAltered).AsSpan()
                        .SequenceEqual(System.Security.Cryptography.SHA256.HashData(originalVictim)),
                    "Tamper negative control did not change SHA-256");

            Console.WriteLine("RAFT_A5_AUTHENTIC_HAPTICS_ARCHIVE originalWavs=29 " +
                              "originalSourceBytes=32733104 originalArchiveReads=" + validated +
                              " strictSourceBytesMatched=true tamperControlDetected=true " +
                              "rawAssetOutput=false unityRun=false phoneRun=false");
            return 0;
        }
        finally
        {
            Directory.Delete(temporary, recursive: true);
        }
    }

    static int Main(string[] args)
    {
        if (args.Length == 2 && args[0] == "--original-wavs")
            return RunOriginalWavs(args[1]);
        if (args.Length != 1) throw new ArgumentException("Supply filename manifest or --original-wavs source directory");
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
