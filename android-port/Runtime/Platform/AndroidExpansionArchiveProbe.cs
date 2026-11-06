using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.IO.Compression;

namespace RaftAndroid.Platform
{
    // Diagnostic ONLY. Probe the exact installed APK-version main OBB from
    // getObbDir(), without unpacking it or reading a multi-GB Unity resource.
    // A readable ZIP sample is NOT engine-side Unity resource-load or pixel proof.
    public sealed class AndroidExpansionArchiveProbeResult
    {
        public string Status { get; internal set; } = "unavailable";
        public string ErrorType { get; internal set; } = "";
        public long ObbBytes { get; internal set; }
        public int ZipEntries { get; internal set; }
        public int UnityDataEntries { get; internal set; }
        public int OriginalBankPaths { get; internal set; }
        public bool UnityFirstByteRead { get; internal set; }

        // Never include an absolute device path, entry name, GUID, bank bytes or digest.
        public string ToLogFields()
        {
            return "status=" + Status +
                "; error_type=" + (ErrorType.Length == 0 ? "none" : ErrorType) +
                "; obb_bytes=" + ObbBytes.ToString(CultureInfo.InvariantCulture) +
                "; zip_entries=" + ZipEntries.ToString(CultureInfo.InvariantCulture) +
                "; unity_data_entries=" + UnityDataEntries.ToString(CultureInfo.InvariantCulture) +
                "; expected_fmod_bank_paths=" + OriginalBankPaths.ToString(CultureInfo.InvariantCulture) + "/5" +
                "; unity_zip_first_byte_read=" + (UnityFirstByteRead ? "true" : "false") +
                "; installed_obb_sha_verified=false" +
                "; unity_engine_resource_load_verified=false" +
                "; gpu_pixels_verified=false";
        }
    }

    public static class AndroidExpansionArchiveProbe
    {
        private static readonly string[] BankNames =
        {
            "MasterBank.strings.bank", "MasterBank.bank", "VO_logs_english.bank",
            "VO_npc_english.bank", "VO_olof_english.bank"
        };

        private static bool ValidPackage(string value)
        {
            if (string.IsNullOrEmpty(value) || value.Length > 200) return false;
            string[] parts = value.Split('.');
            if (parts.Length < 2) return false;
            foreach (string part in parts)
            {
                if (part.Length == 0 || !IsLetter(part[0])) return false;
                foreach (char c in part)
                    if (!IsLetter(c) && !(c >= '0' && c <= '9') && c != '_')
                        return false;
            }
            return true;
        }

        private static bool IsLetter(char c)
        {
            return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
        }

        private static bool HasStaleVersion(string directory, string package, string expected)
        {
            string suffix = "." + package + ".obb";
            foreach (string path in Directory.EnumerateFiles(directory, "main.*.obb",
                         SearchOption.TopDirectoryOnly))
            {
                string name = Path.GetFileName(path);
                if (name == expected || !name.StartsWith("main.", StringComparison.Ordinal) ||
                    !name.EndsWith(suffix, StringComparison.Ordinal))
                    continue;
                string version = name.Substring(5, name.Length - 5 - suffix.Length);
                if (version.Length == 0) continue;
                bool numeric = true;
                foreach (char c in version)
                    if (c < '0' || c > '9') { numeric = false; break; }
                if (numeric) return true;
            }
            return false;
        }

        public static AndroidExpansionArchiveProbeResult Inspect(
            string obbDirectory, string packageName, long installedVersionCode)
        {
            var report = new AndroidExpansionArchiveProbeResult();
            if (!ValidPackage(packageName) || installedVersionCode <= 0)
            {
                report.Status = "invalid_installed_identity";
                return report;
            }

            if (string.IsNullOrEmpty(obbDirectory) || !Directory.Exists(obbDirectory))
            {
                report.Status = "obb_directory_unavailable";
                return report;
            }

            // Never select a stale expansion merely because it is the only
            // readable OBB on the device.
            string expected = "main." + installedVersionCode.ToString(CultureInfo.InvariantCulture) +
                "." + packageName + ".obb";
            string path = Path.Combine(obbDirectory, expected);
            try
            {
                if (!File.Exists(path))
                {
                    report.Status = HasStaleVersion(obbDirectory, packageName, expected)
                        ? "matching_obb_missing_stale_exists" : "matching_obb_missing";
                    return report;
                }
                if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
                {
                    report.Status = "matching_obb_link_unsupported";
                    return report;
                }

                using (var input = File.Open(path, FileMode.Open, FileAccess.Read, FileShare.Read))
                {
                    report.ObbBytes = input.Length;
                    if (report.ObbBytes == 0)
                    {
                        report.Status = "matching_obb_empty";
                        return report;
                    }
                    using (var zip = new ZipArchive(input, ZipArchiveMode.Read, leaveOpen: false))
                    {
                        report.ZipEntries = zip.Entries.Count;
                        if (report.ZipEntries > 4096)
                        {
                            report.Status = "zip_entry_count_out_of_bound";
                            return report;
                        }

                        var unityNames = new HashSet<string>(StringComparer.Ordinal);
                        ZipArchiveEntry sample = null;
                        var banks = new HashSet<string>(StringComparer.Ordinal);
                        foreach (ZipArchiveEntry entry in zip.Entries)
                        {
                            string name = entry.FullName;
                            if (name.StartsWith("assets/bin/Data/", StringComparison.Ordinal) &&
                                !name.EndsWith("/", StringComparison.Ordinal) && entry.Length > 0)
                            {
                                if (!unityNames.Add(name))
                                {
                                    report.Status = "ambiguous_unity_data";
                                    return report;
                                }
                                report.UnityDataEntries++;
                                if (sample == null) sample = entry;
                            }
                            foreach (string bank in BankNames)
                                if (name == "assets/" + bank && entry.Length > 0)
                                    banks.Add(bank);
                        }
                        report.OriginalBankPaths = banks.Count;
                        if (sample == null)
                        {
                            report.Status = "unity_data_missing";
                            return report;
                        }

                        // Deliberately read ONE byte only, with no payload log,
                        // full-file CRC/hash, decompression to disk or large array.
                        using (var asset = sample.Open())
                            report.UnityFirstByteRead = asset.ReadByte() >= 0;
                        report.Status = report.UnityFirstByteRead
                            ? "unity_zip_first_byte_readable" : "unity_zip_sample_empty";
                    }
                }
            }
            catch (Exception ex)
            {
                // Fail open for the game; never disclose physical paths or
                // exception messages that could contain user data.
                report.Status = "archive_probe_unavailable";
                report.ErrorType = ex.GetType().Name;
            }
            return report;
        }
    }
}
