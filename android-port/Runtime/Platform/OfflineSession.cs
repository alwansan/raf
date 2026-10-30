using System;

namespace RaftAndroid.Platform
{
    /// <summary>
    /// Minimal offline host semantics. This is a platform adapter prototype,
    /// not a replacement implementation of the game's Raft_Network class.
    /// </summary>
    public sealed class OfflineSession
    {
        public OfflineSession(string localProfileId)
        {
            if (string.IsNullOrEmpty(localProfileId))
                throw new ArgumentException("Local identity required.", nameof(localProfileId));
            LocalProfileId = localProfileId;
        }

        public string LocalProfileId { get; }
        public bool IsSinglePlayer => true;
        public bool IsHost => true;
        public bool IsConnected => true;
        public int ConnectedPlayerCount => 1;
        public bool UsesSteam => false;
        public bool UsesInternet => false;
    }
}
