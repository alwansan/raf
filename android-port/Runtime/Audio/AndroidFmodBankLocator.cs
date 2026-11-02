using System;
using System.IO;

namespace RaftAndroid.Audio
{
    // Pure platform policy: use the actual package-owned OBB when Unity
    // reports only its APK streaming-assets URL. No game assets are copied
    // out of the expansion archive and no network lookup is permitted.
    public static class AndroidFmodBankLocator
    {
        public static string SelectRoot(string streamingRoot, string obbDirectory, string packageName)
        {
            if (string.IsNullOrEmpty(packageName) || packageName.IndexOf('/') >= 0 ||
                packageName.IndexOf('\\') >= 0)
                throw new ArgumentException("Android package name required", nameof(packageName));

            // When Unity already points at its expansion, preserve that
            // canonical path. The bank reader validates every ZIP entry.
            if (!string.IsNullOrEmpty(streamingRoot) &&
                streamingRoot.IndexOf(".obb!/", StringComparison.OrdinalIgnoreCase) >= 0 &&
                IsJarRoot(streamingRoot))
                return streamingRoot.TrimEnd('/');

            string match = null;
            if (!string.IsNullOrEmpty(obbDirectory) && Directory.Exists(obbDirectory))
            {
                string prefix = "main.";
                string suffix = "." + packageName + ".obb";
                foreach (string file in Directory.EnumerateFiles(
                    obbDirectory, "main.*.obb", SearchOption.TopDirectoryOnly))
                {
                    string name = Path.GetFileName(file);
                    if (!name.StartsWith(prefix, StringComparison.Ordinal) ||
                        !name.EndsWith(suffix, StringComparison.Ordinal)) continue;
                    string version = name.Substring(prefix.Length,
                        name.Length - prefix.Length - suffix.Length);
                    if (version.Length == 0) continue;
                    bool digits = true;
                    foreach (char character in version)
                        if (character < '0' || character > '9') { digits = false; break; }
                    if (!digits) continue;
                    if (match != null)
                        throw new InvalidDataException("Ambiguous original Android main OBB versions");
                    match = file;
                }
            }
            if (match != null)
                return "jar:" + new Uri(Path.GetFullPath(match)).AbsoluteUri + "!/assets";

            // Non-split Android builds can carry StreamingAssets in the APK.
            // Never silently skip the audio loader: the caller will validate
            // each required original bank in the selected archive.
            if (IsJarRoot(streamingRoot))
                return streamingRoot.TrimEnd('/');

            throw new InvalidDataException("Original FMOD bank archive unavailable on Android");
        }

        private static bool IsJarRoot(string path)
        {
            return !string.IsNullOrEmpty(path) &&
                (path.StartsWith("jar:file:", StringComparison.Ordinal) ||
                 path.StartsWith("/jar:file:", StringComparison.Ordinal)) &&
                path.IndexOf("!/assets", StringComparison.Ordinal) >= 0;
        }
    }
}
