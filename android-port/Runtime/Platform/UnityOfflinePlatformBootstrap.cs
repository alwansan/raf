#if UNITY_5_3_OR_NEWER
using UnityEngine;

namespace RaftAndroid.Platform
{
    /// <summary>
    /// Unity-facing entry point. Intentionally not auto-injected into Raft scenes yet:
    /// original SteamManager / SaveAndLoad call sites must be adapted after Editor import.
    /// </summary>
    public static class UnityOfflinePlatformBootstrap
    {
        public static OfflineSession CreateLocalSession()
        {
            var store = new LocalProfileStore(Application.persistentDataPath);
            return new OfflineSession(store.GetOrCreateProfileId());
        }

        public static LocalSavePaths GetSavePaths(OfflineSession session)
        {
            return new LocalSavePaths(Application.persistentDataPath, session.LocalProfileId);
        }
    }
}
#endif
