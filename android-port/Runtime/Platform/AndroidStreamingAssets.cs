using System;
using System.IO;
using System.IO.Compression;
using System.Linq;

namespace RaftAndroid.Platform
{
    // Read the exact requested APK/OBB ZIP entry; never reinterpret a jar URL
    // as a filesystem path or extract the entire multi-GB game archive.
    public static class AndroidStreamingAssets
    {
        public static byte[] ReadAllBytes(string path)
        {
            if (path == null) throw new ArgumentNullException(nameof(path));
            if (!path.StartsWith("jar:file:", StringComparison.Ordinal)) return File.ReadAllBytes(path);
            int separator = path.IndexOf("!/", StringComparison.Ordinal);
            if (separator < 0) throw new InvalidDataException("Malformed Android asset URL");
            var archiveUri = new Uri(path.Substring(4, separator - 4), UriKind.Absolute);
            if (!archiveUri.IsFile) throw new InvalidDataException("Local APK/OBB required");
            string entryName = Uri.UnescapeDataString(path.Substring(separator + 2));
            if (!entryName.StartsWith("assets/", StringComparison.Ordinal) ||
                entryName.Contains("\\") || entryName.Split('/').Any(s => s == ".." || s == "." || s.Length == 0))
                throw new InvalidDataException("Unsafe Android asset entry");
            using (var file = File.OpenRead(archiveUri.LocalPath))
            using (var zip = new ZipArchive(file, ZipArchiveMode.Read))
            {
                var entries = zip.Entries.Where(e => e.FullName == entryName).ToArray();
                if (entries.Length != 1) throw new InvalidDataException("Android asset absent or ambiguous");
                var entry = entries[0];
                if (entry.Length > 128L * 1024 * 1024) throw new InvalidDataException("Individual audio asset exceeds read bound");
                using (var input = entry.Open())
                using (var output = new MemoryStream((int)entry.Length))
                {
                    input.CopyTo(output);
                    if (output.Length != entry.Length) throw new InvalidDataException("Truncated Android asset");
                    return output.ToArray();
                }
            }
        }
    }
}
