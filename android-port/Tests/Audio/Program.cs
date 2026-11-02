using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using RaftAndroid.Platform;
using RaftAndroid.Audio;

class Program
{
    static int checks;
    static void Require(bool condition) { if (!condition) throw new Exception("Audio policy case failed: " + checks); checks++; }
    static void Main()
    {
        string root = Path.Combine(Path.GetTempPath(), "raft-asset-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            byte[] bytes = { 0, 255, 82, 73, 70, 70, 128, 1 };
            string archive = Path.Combine(root, "test audio.obb");
            using (var zip = ZipFile.Open(archive, ZipArchiveMode.Create))
            {
                foreach (var mode in new[] { CompressionLevel.NoCompression, CompressionLevel.Optimal })
                {
                    var entry = zip.CreateEntry("assets/Haptics/" + mode + ".wav", mode);
                    using (var stream = entry.Open()) stream.Write(bytes, 0, bytes.Length);
                }
            }
            string prefix = "jar:" + new Uri(archive).AbsoluteUri + "!/";
            foreach (var mode in new[] { CompressionLevel.NoCompression, CompressionLevel.Optimal })
            {
                string original = prefix + "assets/Haptics/" + mode + ".wav";
                Require(Convert.ToBase64String(AndroidStreamingAssets.ReadAllBytes(original)) == Convert.ToBase64String(bytes));
                // Actual device logs contain "/jar:file:/...obb!/assets/..." due
                // to original runtime path normalization, not only "jar:file:".
                Require(AndroidStreamingAssets.ReadAllBytes("/" + original).SequenceEqual(bytes));
            }
            foreach (string bad in new[] { "assets/missing.wav", "assets/../escape", "assets/%2e%2e/escape" })
            {
                bool refused = false;
                try { AndroidStreamingAssets.ReadAllBytes(prefix + bad); }
                catch (InvalidDataException) { refused = true; }
                Require(refused);
                refused = false;
                try { AndroidStreamingAssets.ReadAllBytes("/" + prefix + bad); }
                catch (InvalidDataException) { refused = true; }
                Require(refused);
            }
            // Exercise a multi-megabyte bank, not just tiny haptic samples.
            // The runtime reader must return exact bytes without ToArray's
            // second full-size allocation (the real MasterBank is ~100 MiB).
            byte[] largeBank = new byte[4 * 1024 * 1024];
            for (int i = 0; i < largeBank.Length; i++) largeBank[i] = (byte)((i * 31 + 7) & 255);
            using (var zip = ZipFile.Open(archive, ZipArchiveMode.Update))
            {
                var entry = zip.CreateEntry("assets/MasterBank.bank", CompressionLevel.Optimal);
                using (var stream = entry.Open()) stream.Write(largeBank, 0, largeBank.Length);
            }
            Require(AndroidStreamingAssets.ReadAllBytes(prefix + "assets/MasterBank.bank").SequenceEqual(largeBank));

            // Fake an over-limit central-directory length without allocating
            // a 128+ MiB fixture. Reject before decompressing or allocating.
            string oversized = Path.Combine(root, "oversized.obb");
            using (var zip = ZipFile.Open(oversized, ZipArchiveMode.Create))
            {
                var entry = zip.CreateEntry("assets/MasterBank.bank", CompressionLevel.NoCompression);
                using (var stream = entry.Open()) stream.WriteByte(42);
            }
            byte[] zipBytes = File.ReadAllBytes(oversized);
            int central = -1;
            for (int i = 0; i + 46 <= zipBytes.Length; i++)
            {
                if (zipBytes[i] == 0x50 && zipBytes[i + 1] == 0x4b &&
                    zipBytes[i + 2] == 0x01 && zipBytes[i + 3] == 0x02)
                { central = i; break; }
            }
            Require(central >= 0);
            Array.Copy(BitConverter.GetBytes((uint)(128L * 1024 * 1024 + 1)), 0, zipBytes, central + 24, 4);
            File.WriteAllBytes(oversized, zipBytes);
            bool tooLargeRejected = false;
            try { AndroidStreamingAssets.ReadAllBytes("jar:" + new Uri(oversized).AbsoluteUri + "!/assets/MasterBank.bank"); }
            catch (InvalidDataException) { tooLargeRejected = true; }
            Require(tooLargeRejected);

            string plain = Path.Combine(root, "ordinary.wav"); File.WriteAllBytes(plain, bytes);
            Require(Convert.ToBase64String(AndroidStreamingAssets.ReadAllBytes(plain)) == Convert.ToBase64String(bytes));
            using (var zip = ZipFile.Open(archive, ZipArchiveMode.Update))
            { zip.CreateEntry("assets/Haptics/Optimal.wav"); }
            bool duplicate = false;
            try { AndroidStreamingAssets.ReadAllBytes(prefix + "assets/Haptics/Optimal.wav"); }
            catch (InvalidDataException) { duplicate = true; }
            Require(duplicate);
        }
        finally { Directory.Delete(root, true); }
        var calls = new List<string>();
        var startup = new FmodAndroidStartup();
        Action load = () => calls.Add("load");
        Action java = () => calls.Add("java");
        Func<uint> version = () => { calls.Add("version"); return FmodAndroidStartup.ExpectedVersion; };
        startup.Initialize(load, java, version);
        Require(string.Join(",", calls) == "load,java,version");
        Require(startup.Initialized);
        startup.Initialize(load, java, version);
        Require(calls.Count == 3);
        for (int failing = 0; failing < 3; failing++)
        {
            int stage = failing;
            calls.Clear();
            startup = new FmodAndroidStartup();
            try
            {
                startup.Initialize(() => { calls.Add("load"); if (stage == 0) throw new Exception(); },
                    () => { calls.Add("java"); if (stage == 1) throw new Exception(); },
                    () => { calls.Add("version"); throw new Exception(); });
                throw new Exception("Failure was swallowed");
            }
            catch (Exception) { Require(!startup.Initialized); Require(calls.Count == stage + 1); }
        }
        foreach (uint wrong in new uint[] { 0, 0x00020214, 0x00020221, 0x00020300 })
        {
            startup = new FmodAndroidStartup();
            bool rejected = false;
            try { startup.Initialize(() => {}, () => {}, () => wrong); }
            catch (InvalidOperationException) { rejected = true; }
            Require(rejected && !startup.Initialized);
        }
        startup = new FmodAndroidStartup();
        bool missingRejected = false;
        try { startup.Initialize(null, java, version); }
        catch (ArgumentNullException) { missingRejected = true; }
        Require(missingRejected && !startup.Initialized);
        Console.WriteLine("RAFT_FMOD_STARTUP_POLICY checks=" + checks + " passed=true actualUnityDeviceExecution=false");
    }
}
