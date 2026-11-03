using System;
using System.IO;

namespace RaftAndroid.Platform
{
    /// <summary>
    /// Maps offline profile and world identifiers into Unity's sandbox path.
    /// Only creates isolated directories; serialization format stays owned by the game save layer.
    /// </summary>
    public sealed class LocalSavePaths
    {
        private readonly string _root;
        private readonly string _profileId;

        public LocalSavePaths(string persistentDataPath, string localProfileId)
        {
            if (string.IsNullOrWhiteSpace(persistentDataPath))
                throw new ArgumentException("Persistent data root required.", nameof(persistentDataPath));
            _root = Path.GetFullPath(persistentDataPath);
            ValidateSegment(localProfileId, nameof(localProfileId));
            _profileId = localProfileId;
        }

        public string GetWorldDirectory(string worldId)
        {
            ValidateSegment(worldId, nameof(worldId));
            // Pre-existing profile/world links can redirect otherwise-safe IDs
            // outside the app sandbox. Fail closed without modifying save data.
            RejectLinkedSaveDirectories(worldId);
            return Path.Combine(_root, "RaftAndroid", "profiles", _profileId, "worlds", worldId);
        }

        public string GetWorldSaveFile(string worldId)
        {
            return CheckedSaveFile(GetWorldDirectory(worldId));
        }

        public string GetWorldSaveFileAndCreateDirectory(string worldId)
        {
            string directory = GetWorldDirectory(worldId);
            Directory.CreateDirectory(directory);
            // Recheck after creating missing directories; this is not an atomic
            // defence against a hostile concurrent filesystem writer.
            RejectLinkedSaveDirectories(worldId);
            return CheckedSaveFile(directory);
        }

        private void RejectLinkedSaveDirectories(string worldId)
        {
            // Caller-provided Android root ancestors may legitimately be links.
            // Only descendants controlled by this helper must be link-free.
            string path = _root;
            foreach (string part in new[] { "RaftAndroid", "profiles", _profileId, "worlds", worldId })
            {
                path = Path.Combine(path, part);
                if ((Directory.Exists(path) || File.Exists(path)) &&
                    (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("Linked local save directories are not supported.");
            }
        }

        private static string CheckedSaveFile(string directory)
        {
            string path = Path.Combine(directory, "world.sav");
            try
            {
                // A real parent directory is insufficient: the leaf can be a
                // link to a save outside the profile. Check the link itself,
                // including a dangling link, rather than following a File.Exists
                // check that could suppress broken symbolic links.
                if ((File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("Linked local save files are not supported.");
            }
            catch (FileNotFoundException) { } // New worlds do not have a save yet.
            catch (DirectoryNotFoundException) { }
            // Managed prechecks do not prevent a hostile concurrent path swap.
            return path;
        }

        private static void ValidateSegment(string segment, string paramName)
        {
            if (string.IsNullOrEmpty(segment) || segment.Length > 64)
                throw new ArgumentException("Identifier must contain 1-64 safe characters.", paramName);
            foreach (char ch in segment)
                if (!((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') ||
                      (ch >= '0' && ch <= '9') || ch == '_' || ch == '-'))
                    throw new ArgumentException("Identifier contains an unsafe path character.", paramName);
        }
    }
}
