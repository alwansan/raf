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
            return Path.Combine(_root, "RaftAndroid", "profiles", _profileId, "worlds", worldId);
        }

        public string GetWorldSaveFile(string worldId)
        {
            return Path.Combine(GetWorldDirectory(worldId), "world.sav");
        }

        public string GetWorldSaveFileAndCreateDirectory(string worldId)
        {
            string directory = GetWorldDirectory(worldId);
            Directory.CreateDirectory(directory);
            return Path.Combine(directory, "world.sav");
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
