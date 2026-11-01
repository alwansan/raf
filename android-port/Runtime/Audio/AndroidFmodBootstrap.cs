#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using UnityEngine;

namespace RaftAndroid.Audio
{
    public static class AndroidFmodBootstrap
    {
        private static readonly FmodAndroidStartup Startup = new FmodAndroidStartup();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterAssembliesLoaded)]
        private static void Initialize()
        {
            // Restore the same-version Android bridge omitted from the Windows provider.
            // Do not construct replacement FMOD settings, banks or managed SDK types.
            Startup.Initialize(FMODUnity.RuntimeUtils.EnforceLibraryOrder, InitializeJava, ReadVersion);
            Debug.Log("RAFT_FMOD_ANDROID_BOOTSTRAP javaInitialized=true nativeVersion=00020215");
        }

        private static void InitializeJava()
        {
            using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
            using (var bridge = new AndroidJavaClass("org.fmod.FMOD"))
            {
                if (activity == null) throw new InvalidOperationException("Unity Android activity is unavailable for FMOD");
                bridge.CallStatic("init", activity);
            }
        }

        private static uint ReadVersion()
        {
            FMOD.System system;
            Check(FMOD.Factory.System_Create(out system), "create version probe");
            try
            {
                uint version;
                Check(system.getVersion(out version), "read native version");
                return version;
            }
            finally
            {
                Check(system.release(), "release version probe");
            }
        }

        private static void Check(FMOD.RESULT result, string operation)
        {
            if (result != FMOD.RESULT.OK)
                throw new InvalidOperationException("FMOD Android " + operation + " failed: " + result);
        }
    }
}
#endif
