using System;
using System.IO;

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
                return ReadExistingId(path);

            string generated = Guid.NewGuid().ToString("N");
            string tempPath = Path.Combine(_profileDirectory, "profile." + Guid.NewGuid().ToString("N") + ".tmp");
            try
            {
                using (var output = new FileStream(tempPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                using (var writer = new StreamWriter(output))
                {
                    writer.WriteLine(generated);
                }

                // Do not overwrite an existing ID: simultaneous start / restore must never change an established profile.
                try
                {
                    File.Move(tempPath, path);
                }
                catch (IOException) when (File.Exists(path))
                {
                    // Another caller created the profile first; preserve its identity.
                }
            }
            finally
            {
                if (File.Exists(tempPath))
                    File.Delete(tempPath);
            }

            return ReadExistingId(path);
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
