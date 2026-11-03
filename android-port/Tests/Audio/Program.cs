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
            // Unity 2021 may report its APK path even when Android installed
            // the authentic original banks in main.<version>.<package>.obb.
            // The locator MUST select the actual app-owned expansion and never
            // skip FMOD initialization because streamingAssetsPath says APK.
            string package = "com.alwansan.raft.androidtest";
            string apkRoot = "jar:file:///data/app/base.apk!/assets";
            string ownObb = Path.Combine(root, "app-obb");
            Directory.CreateDirectory(ownObb);
            string obbCandidate = Path.Combine(ownObb, "main.80." + package + ".obb");
            File.Copy(archive, obbCandidate);
            string resolved = AndroidFmodBankLocator.SelectRoot(apkRoot, ownObb, package, 80);
            Require(resolved == "jar:" + new Uri(obbCandidate).AbsoluteUri + "!/assets");
            Require(AndroidStreamingAssets.ReadAllBytes(
                resolved + "/Haptics/" + CompressionLevel.NoCompression + ".wav").SequenceEqual(bytes));
            // A canonical Unity OBB root must match the installed version.
            Require(AndroidFmodBankLocator.SelectRoot(
                resolved, ownObb, package, 80) == resolved);
            // APK-only builds still use APK StreamingAssets, not a silent return.
            Require(AndroidFmodBankLocator.SelectRoot(apkRoot, null, package, 80) == apkRoot);
            Require(AndroidFmodBankLocator.SelectRoot(apkRoot,
                Path.Combine(root, "no-such-directory"), package, 80) == apkRoot);
            File.WriteAllBytes(Path.Combine(ownObb, "main.foo." + package + ".obb"), bytes);
            File.WriteAllBytes(Path.Combine(ownObb, "main.7.com.another.game.obb"), bytes);
            Require(AndroidFmodBankLocator.SelectRoot(apkRoot, ownObb, package, 80) == resolved);
            string newerObb = Path.Combine(ownObb, "main.81." + package + ".obb");
            File.WriteAllBytes(newerObb, bytes);
            // Both OBBs can coexist after a manual install. Select the exact
            // installed version rather than throwing or loading stale banks.
            Require(AndroidFmodBankLocator.SelectRoot(apkRoot, ownObb, package, 80) == resolved);
            Require(AndroidFmodBankLocator.SelectRoot(apkRoot, ownObb, package, 81) ==
                "jar:" + new Uri(newerObb).AbsoluteUri + "!/assets");
            bool mismatchedUnityRoot = false;
            try { AndroidFmodBankLocator.SelectRoot(resolved, ownObb, package, 81); }
            catch (InvalidDataException) { mismatchedUnityRoot = true; }
            Require(mismatchedUnityRoot);
            bool staleOnly = false;
            try { AndroidFmodBankLocator.SelectRoot(apkRoot, ownObb, package, 82); }
            catch (InvalidDataException) { staleOnly = true; }
            Require(staleOnly);
            bool invalid = false;
            try { AndroidFmodBankLocator.SelectRoot("/raw/storage", null, package, 80); }
            catch (InvalidDataException) { invalid = true; }
            Require(invalid);
            bool invalidPackage = false;
            try { AndroidFmodBankLocator.SelectRoot(apkRoot, ownObb, "../unsafe", 80); }
            catch (ArgumentException) { invalidPackage = true; }
            Require(invalidPackage);
            bool invalidVersion = false;
            try { AndroidFmodBankLocator.SelectRoot(apkRoot, ownObb, package, 0); }
            catch (ArgumentOutOfRangeException) { invalidVersion = true; }
            Require(invalidVersion);
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
            // Assert original bank provenance is checked before runtime FMOD loading.
            // These are synthetic bytes, never a copy of the proprietary game banks.
            byte[] sampleBank = { 0, 1, 2, 3, 4, 255 };
            string sampleSha;
            using (var sha = System.Security.Cryptography.SHA256.Create())
                sampleSha = BitConverter.ToString(sha.ComputeHash(sampleBank)).Replace("-", "").ToLowerInvariant();
            AndroidOriginalBankIdentity.VerifyExact(sampleBank, sampleBank.Length, sampleSha);
            Require(true);
            byte[] altered = (byte[])sampleBank.Clone();
            altered[2] ^= 1;
            bool alteredRejected = false;
            try { AndroidOriginalBankIdentity.VerifyExact(altered, sampleBank.Length, sampleSha); }
            catch (InvalidDataException) { alteredRejected = true; }
            Require(alteredRejected);
            bool lengthRejected = false;
            try { AndroidOriginalBankIdentity.VerifyExact(sampleBank, sampleBank.Length + 1, sampleSha); }
            catch (InvalidDataException) { lengthRejected = true; }
            Require(lengthRejected);
            bool malformedHashRejected = false;
            try { AndroidOriginalBankIdentity.VerifyExact(sampleBank, sampleBank.Length, "bad"); }
            catch (ArgumentException) { malformedHashRejected = true; }
            Require(malformedHashRejected);
            foreach (string originalName in new[] { "MasterBank.bank", "MasterBank.strings.bank",
                "VO_logs_english.bank", "VO_npc_english.bank", "VO_olof_english.bank" })
            {
                bool wrongOriginalRejected = false;
                try { AndroidOriginalBankIdentity.Verify(originalName, sampleBank); }
                catch (InvalidDataException) { wrongOriginalRejected = true; }
                Require(wrongOriginalRejected);
            }
            bool unknownBankRejected = false;
            try { AndroidOriginalBankIdentity.Verify("untracked.bank", sampleBank); }
            catch (InvalidDataException) { unknownBankRejected = true; }
            Require(unknownBankRejected);
            bool nullBankRejected = false;
            try { AndroidOriginalBankIdentity.Verify("MasterBank.bank", null); }
            catch (ArgumentNullException) { nullBankRejected = true; }
            Require(nullBankRejected);

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
