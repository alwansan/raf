using System;
using System.Security.Cryptography;
using System.Text;

namespace RaftAndroid.Platform
{
    public static class LocalPlayerIdentity
    {
        // This is a local save/player key, never a Steam or PlayFab login.
        public static bool Enabled
        {
            get
            {
#if UNITY_ANDROID && !UNITY_EDITOR
                return true;
#else
                return false;
#endif
            }
        }

        private static ulong cached;
        public static ulong Current
        {
            get
            {
#if UNITY_5_3_OR_NEWER
                if (cached == 0)
                    cached = GetOrCreate(UnityEngine.Application.persistentDataPath);
                return cached;
#else
                throw new InvalidOperationException("Unity persistent storage is required.");
#endif
            }
        }

        public static ulong GetOrCreate(string persistentRoot)
        {
            return FromProfile(new LocalProfileStore(persistentRoot).GetOrCreateProfileId());
        }

        public static ulong FromProfile(string profileId)
        {
            if (profileId == null || profileId.Length != 32)
                throw new ArgumentException("Expected original local profile identity.", nameof(profileId));
            foreach (char ch in profileId)
                if (!((ch >= '0' && ch <= '9') || (ch >= 'a' && ch <= 'f')))
                    throw new ArgumentException("Invalid local profile identity.", nameof(profileId));
            using (var sha = SHA256.Create())
            {
                byte[] digest = sha.ComputeHash(Encoding.UTF8.GetBytes("RaftAndroid.LocalPlayer.v1:" + profileId));
                ulong result = 0;
                for (int i = 0; i < 8; i++)
                    result = (result << 8) | digest[i];
                // Retain nonzero, positive long-compatible IDs used by original RGD consumers.
                return (result & 0x7fffffffffffffffUL) | 1UL;
            }
        }
    }
}
