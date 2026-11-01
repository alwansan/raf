using System;
using System.IO;
using System.Threading;

namespace RaftAndroid.Platform
{
    /// <summary>
    /// Stable offline profile identity stored under the caller-provided application sandbox.
    /// Does not call Steam, PlayFab, Xbox Party, network services, or device identifiers.
    /// </summary>
    public sealed class LocalProfileStore
    {
        private const string ProfileFile = "profile.id";
        private readonly string _profileDirectory;

        public LocalProfileStore(string persistentDataPath)
        {
            if (string.IsNullOrWhiteSpace(persistentDataPath))
                throw new ArgumentException("Persistent data root must be provided.", nameof(persistentDataPath));
            _profileDirectory = Path.Combine(Path.GetFullPath(persistentDataPath), "RaftAndroid", "profiles", "local");
        }

        public string GetOrCreateProfileId()
        {
            Directory.CreateDirectory(_profileDirectory);
            string path = Path.Combine(_profileDirectory, ProfileFile);

            if (File.Exists(path))
                return ReadWhenWriterCloses(path);

            string generated = Guid.NewGuid().ToString("N");
            try
            {
                // CreateNew is an atomic exclusive claim on the final path.
                // File.Move(temp, path) can race another creator's existence check
                // on Unix, replacing an identity already returned to a caller.
                using (var output = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(output))
                {
                    writer.WriteLine(generated);
                }
            }
            catch (IOException) when (File.Exists(path))
            {
                // Another process or thread claimed the path. Never replace it.
            }

            return ReadWhenWriterCloses(path);
        }

        private static string ReadWhenWriterCloses(string path)
        {
            // On Unix, a different process can observe a newly created but
            // not-yet-populated profile.id even while its writer holds FileShare.None.
            // Retry both sharing failures and incomplete contents for at most ~1s.
            // A persistently corrupt ID still fails closed; never replace the file.
            for (int attempt = 0; ; attempt++)
            {
                try { return ReadExistingId(path); }
                catch (InvalidDataException) when (attempt < 99)
                {
                    Thread.Sleep(10);
                }
                catch (IOException) when (attempt < 99)
                {
                    Thread.Sleep(10);
                }
            }
        }

        private static string ReadExistingId(string path)
        {
            string id = File.ReadAllText(path).Trim();
            if (id.Length != 32)
                throw new InvalidDataException("Local profile identity is invalid; refusing to overwrite existing saves.");

            foreach (char ch in id)
                if (!((ch >= '0' && ch <= '9') || (ch >= 'a' && ch <= 'f')))
                    throw new InvalidDataException("Local profile identity is invalid; refusing to overwrite existing saves.");
            return id;
        }
    }
}
