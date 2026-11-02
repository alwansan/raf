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
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Initialize();
            Startup.Initialize(LoadAndroidLibraries, InitializeJava, ReadVersion);
            LoadExpansionBanks();
            Debug.Log("RAFT_FMOD_ANDROID_BOOTSTRAP javaInitialized=true nativeVersion=00020215");
        }

        private static void LoadExpansionBanks()
        {
            string root = Application.streamingAssetsPath;
            if (root.IndexOf(".obb!/", StringComparison.OrdinalIgnoreCase) < 0) return;
            // The original Windows-compiled provider uses android_asset, which
            // cannot address Unity's expansion ZIP. Feed the exact original bank
            // bytes to the original Studio system before scene emitters execute.
            foreach (string name in new[] { "MasterBank.strings.bank", "MasterBank.bank", "VO_logs_english.bank", "VO_npc_english.bank", "VO_olof_english.bank" })
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.expansion_bank." + name, () =>
                {
                    byte[] bytes = RaftAndroid.Platform.AndroidStreamingAssets.ReadAllBytes(root + "/" + name);
                    FMOD.Studio.Bank bank;
                    Check(FMODUnity.RuntimeManager.StudioSystem.loadBankMemory(bytes, FMOD.Studio.LOAD_BANK_FLAGS.NORMAL, out bank), "load expansion bank " + name);
                    if (!bank.isValid()) throw new InvalidOperationException("FMOD expansion bank handle is invalid");
                });
            }
        }

        private static void LoadAndroidLibraries()
        {
            // Restore the vendor's Android-only block compiled out of RuntimeUtils.
            // Windows VERSION.dll is "fmodstudio"; Android Core is a separate "fmod".
            using (var system = new AndroidJavaClass("java.lang.System"))
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.load_core",
                    () => system.CallStatic("loadLibrary", "fmod"));
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.load_studio",
                    () => system.CallStatic("loadLibrary", "fmodstudio"));
            }
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.original_library_order",
                FMODUnity.RuntimeUtils.EnforceLibraryOrder);
        }

        private static void InitializeJava()
        {
            using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
            using (var bridge = new AndroidJavaClass("org.fmod.FMOD"))
            {
                if (activity == null) throw new InvalidOperationException("Unity Android activity is unavailable for FMOD");
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.java_init", () => bridge.CallStatic("init", activity));
            }
        }

        private static uint ReadVersion()
        {
            FMOD.System system;
            system = default(FMOD.System);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.version_probe_create", () => Check(FMOD.Factory.System_Create(out system), "create version probe"));
            try
            {
                uint version;
                version = 0;
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.version_probe_read", () => Check(system.getVersion(out version), "read native version"));
                return version;
            }
            finally
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.version_probe_release", () => Check(system.release(), "release version probe"));
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

