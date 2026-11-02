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
            // Some original Unity Path.Combine/GetFullPath call sites hand back
            // "/jar:file:/...obb!/assets/..." instead of "jar:file:/...".
            // This is still an Android ZIP URI, not a real absolute directory.
            // Recognize ONLY this exact leading-slash form; keep every archive
            // and entry validation below instead of silently treating it as a file.
            if (path.StartsWith("/jar:file:", StringComparison.Ordinal)) path = path.Substring(1);
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
                // MasterBank can exceed 100 MiB. Allocate only its verified
                // declared length; MemoryStream.ToArray used to duplicate the
                // entire bank in managed memory during Android startup.
                byte[] bytes = new byte[(int)entry.Length];
                using (var input = entry.Open())
                {
                    int offset = 0;
                    while (offset < bytes.Length)
                    {
                        int read = input.Read(bytes, offset, bytes.Length - offset);
                        if (read <= 0) throw new InvalidDataException("Truncated Android asset");
                        offset += read;
                    }
                    // Do not accept a stream that expands past the declared
                    // length even when its ZIP metadata is inconsistent.
                    if (input.ReadByte() != -1) throw new InvalidDataException("Android asset exceeds declared length");
                }
                return bytes;
            }
        }
    }
}
