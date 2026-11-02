using System;
using System.Globalization;
using System.IO;

namespace RaftAndroid.Audio
{
    // Pure platform policy: use only the expansion archive belonging to the
    // INSTALLED APK version. A stale main.<version> OBB can contain different
    // original banks and must never be selected by enumeration order.
    public static class AndroidFmodBankLocator
    {
        public static string SelectRoot(string streamingRoot, string obbDirectory,
            string packageName, long installedVersionCode)
        {
            if (string.IsNullOrEmpty(packageName) || packageName.IndexOf('/') >= 0 ||
                packageName.IndexOf('\\') >= 0)
                throw new ArgumentException("Android package name required", nameof(packageName));
            if (installedVersionCode <= 0)
                throw new ArgumentOutOfRangeException(nameof(installedVersionCode),
                    "Positive installed Android versionCode required");

            string expectedName = "main." +
                installedVersionCode.ToString(CultureInfo.InvariantCulture) +
                "." + packageName + ".obb";
            string normalizedRoot = streamingRoot == null ? null : streamingRoot.TrimEnd('/');

            // Unity may already expose the expansion as its StreamingAssets
            // root. Verify that it belongs to the installed APK before using
            // its original banks; do not trust an old copied OBB URL.
            if (IsJarRoot(normalizedRoot) &&
                normalizedRoot.IndexOf(".obb!/", StringComparison.OrdinalIgnoreCase) >= 0)
            {
                if (!normalizedRoot.EndsWith("/" + expectedName + "!/assets",
                    StringComparison.Ordinal))
                    throw new InvalidDataException("Unity StreamingAssets OBB version does not match installed APK");
                return normalizedRoot;
            }

            if (!string.IsNullOrEmpty(obbDirectory) && Directory.Exists(obbDirectory))
            {
                string exact = Path.Combine(obbDirectory, expectedName);
                if (File.Exists(exact))
                    return "jar:" + new Uri(Path.GetFullPath(exact)).AbsoluteUri + "!/assets";

                // An old OBB must not silently win just because it is the
                // only archive in getObbDir(). This is a recoverable install
                // problem, not evidence that original FMOD banks are absent.
                string suffix = "." + packageName + ".obb";
                foreach (string file in Directory.EnumerateFiles(
                    obbDirectory, "main.*.obb", SearchOption.TopDirectoryOnly))
                {
                    string name = Path.GetFileName(file);
                    if (!name.StartsWith("main.", StringComparison.Ordinal) ||
                        !name.EndsWith(suffix, StringComparison.Ordinal)) continue;
                    string version = name.Substring(5, name.Length - 5 - suffix.Length);
                    if (version.Length == 0) continue;
                    bool digits = true;
                    foreach (char digit in version)
                        if (digit < '0' || digit > '9') { digits = false; break; }
                    if (digits)
                        throw new InvalidDataException(
                            "Installed APK version has no matching main OBB; stale expansion detected");
                }
            }

            // Non-split Android builds may carry StreamingAssets in the APK.
            // The caller still checks every required bank and its FMOD result.
            if (IsJarRoot(normalizedRoot))
                return normalizedRoot;

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
