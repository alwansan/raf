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
            // LocalProfileStore produces canonical 32-character lowercase hex IDs.
            // Reject a nonempty but invalid ID before advertising a connected host;
            // reuse the validator used by the stable original save-key mapping.
            _ = LocalPlayerIdentity.FromProfile(localProfileId);
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
