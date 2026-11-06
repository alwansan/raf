using System;
using System.IO;
using System.IO.Compression;
using RaftAndroid.Platform;

internal static class Program
{
    private const string Package = "com.alwansan.raft.androidtest";
    private static int checks;
    private static void Check(bool ok, string detail)
    {
        if (!ok) throw new Exception("T5 synthetic OBB probe assertion: " + detail);
        checks++;
    }

    private static void CreateZip(string dir, long version, bool unity,
        bool banks = false, bool emptyUnity = false, bool duplicateUnity = false,
        bool duplicateBank = false, bool emptyDuplicateBank = false)
    {
        string path = Path.Combine(dir, "main." + version + "." + Package + ".obb");
        using (var file = File.Create(path))
        using (var zip = new ZipArchive(file, ZipArchiveMode.Create))
        {
            if (unity)
            {
                Add(zip, "assets/bin/Data/synthetic-data-0", emptyUnity ? 0 : 4);
                if (duplicateUnity)
                    Add(zip, "assets/bin/Data/synthetic-data-0", 2);
            }
            if (banks)
            {
                foreach (string name in new[] { "MasterBank.strings.bank", "MasterBank.bank",
                    "VO_logs_english.bank", "VO_npc_english.bank", "VO_olof_english.bank" })
                    Add(zip, "assets/" + name, 3);
                if (duplicateBank)
                    Add(zip, "assets/MasterBank.bank", emptyDuplicateBank ? 0 : 3);
            }
            Add(zip, "assets/Haptics/synthetic.wav", 2);
        }
    }

    private static void Add(ZipArchive zip, string name, int size)
    {
        var entry = zip.CreateEntry(name, CompressionLevel.NoCompression);
        using (var stream = entry.Open())
            for (int i = 0; i < size; i++) stream.WriteByte((byte)(42 + i));
    }

    public static void Main()
    {
        string root = Path.Combine(Path.GetTempPath(), "t5-obb-read-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(root);
        try
        {
            var noDir = AndroidExpansionArchiveProbe.Inspect(
                Path.Combine(root, "not-installed"), Package, 89);
            Check(noDir.Status == "obb_directory_unavailable", "no directory");
            Check(AndroidExpansionArchiveProbe.Inspect(root, Package, 89).Status ==
                "matching_obb_missing", "not yet installed");

            CreateZip(root, 88, true);
            Check(AndroidExpansionArchiveProbe.Inspect(root, Package, 89).Status ==
                "matching_obb_missing_stale_exists", "stale 88 never selected");
            Check(AndroidExpansionArchiveProbe.Inspect(root, Package, 88).Status ==
                "unity_zip_first_byte_readable", "positive version 88 read");

            CreateZip(root, 89, true, banks: true);
            var good = AndroidExpansionArchiveProbe.Inspect(root, Package, 89);
            Check(good.Status == "unity_zip_first_byte_readable", "exact main 89");
            Check(good.UnityFirstByteRead, "real one byte of synthetic unity payload");
            Check(good.UnityDataEntries == 1, "one Unity entry");
            Check(good.OriginalBankPaths == 5, "all 5 symbolic FMOD routes");
            Check(good.ObbBytes > 0 && good.ZipEntries == 7, "bounded ZIP index");

            CreateZip(root, 95, true, banks: true, duplicateBank: true);
            var duplicate = AndroidExpansionArchiveProbe.Inspect(root, Package, 95);
            Check(duplicate.Status == "ambiguous_fmod_bank_path",
                "duplicate nonempty FMOD path must not masquerade as valid 5/5");
            Check(!duplicate.UnityFirstByteRead,
                "ambiguous FMOD ZIP paths rejected before sample read");
            Check(!duplicate.ToLogFields().Contains(root),
                "ambiguous FMOD diagnostic never logs physical source path");

            CreateZip(root, 96, true, banks: true,
                duplicateBank: true, emptyDuplicateBank: true);
            var emptyDuplicate = AndroidExpansionArchiveProbe.Inspect(root, Package, 96);
            Check(emptyDuplicate.Status == "ambiguous_fmod_bank_path",
                "empty FMOD duplicate must not disappear in path set");
            Check(emptyDuplicate.OriginalBankPaths <= 5,
                "ambiguous FMOD bank counts remain bounded");
            Check(!good.ToLogFields().Contains(root), "no raw physical path");
            Check(good.ToLogFields().Contains("installed_obb_sha_verified=false"),
                "sample is never full integrity claim");
            Check(good.ToLogFields().Contains("unity_engine_resource_load_verified=false"),
                "ZIP byte is not engine load");

            Check(AndroidExpansionArchiveProbe.Inspect(root, "../bad", 89).Status ==
                "invalid_installed_identity", "reject path traversal");
            Check(AndroidExpansionArchiveProbe.Inspect(root, "onecomponent", 89).Status ==
                "invalid_installed_identity", "reject invalid Android package");
            Check(AndroidExpansionArchiveProbe.Inspect(root, Package, 0).Status ==
                "invalid_installed_identity", "reject invalid version");
            Check(AndroidExpansionArchiveProbe.Inspect(root, Package, -1).Status ==
                "invalid_installed_identity", "reject negative version");

            CreateZip(root, 90, false);
            var missing = AndroidExpansionArchiveProbe.Inspect(root, Package, 90);
            Check(missing.Status == "unity_data_missing", "FMOD and WAV are not Unity scene data");
            Check(!missing.UnityFirstByteRead, "missing scene never reported readable");

            CreateZip(root, 91, true, emptyUnity: true);
            Check(AndroidExpansionArchiveProbe.Inspect(root, Package, 91).Status ==
                "unity_data_missing", "empty Unity entry rejected");

            CreateZip(root, 92, true, duplicateUnity: true);
            Check(AndroidExpansionArchiveProbe.Inspect(root, Package, 92).Status ==
                "ambiguous_unity_data", "ambiguous Unity path rejected");

            File.WriteAllText(Path.Combine(root, "main.93." + Package + ".obb"),
                "synthetic invalid ZIP");
            var bad = AndroidExpansionArchiveProbe.Inspect(root, Package, 93);
            Check(bad.Status == "archive_probe_unavailable", "bad zip recoverable");
            Check(!bad.ToLogFields().Contains(root), "exception path not logged");
            Check(!bad.UnityFirstByteRead, "bad zip not claimed good");

            using (File.Create(Path.Combine(root, "main.94." + Package + ".obb"))) { }
            Check(AndroidExpansionArchiveProbe.Inspect(root, Package, 94).Status ==
                "matching_obb_empty", "empty archive fail closed");

            Console.WriteLine("T5_INSTALLED_OBB_READ_PROBE synthetic_checks=" + checks +
                " status=PASS device_verified=false");
        }
        finally
        {
            Directory.Delete(root, recursive: true);
        }
    }
}
