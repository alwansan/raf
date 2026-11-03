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
            // Unity may report an APK StreamingAssets URL even when the
            // split Unity/OBB delivery actually contains the original banks.
            // The previous ".obb!/" check silently skipped EVERY bank, which
            // matches the owner's device traces: native FMOD OK but no bank
            // stages, followed by missing events and master VCA.
            long installedVersionCode = ReadInstalledVersionCode();
            string reported = Application.streamingAssetsPath;
            string obbDirectory = null;
            if (reported.IndexOf(".obb!/", StringComparison.OrdinalIgnoreCase) < 0)
            {
                using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                {
                    if (activity == null) throw new InvalidOperationException("Android activity unavailable for OBB discovery");
                    using (var obb = activity.Call<AndroidJavaObject>("getObbDir"))
                        if (obb != null) obbDirectory = obb.Call<string>("getAbsolutePath");
                }
            }
            string root = AndroidFmodBankLocator.SelectRoot(
                reported, obbDirectory, Application.identifier, installedVersionCode);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("audio", "fmod.bank_root",
                "archive=" + (root.IndexOf(".obb!/", StringComparison.OrdinalIgnoreCase) >= 0 ? "obb" : "apk") +
                "; installedVersionCode=" + installedVersionCode +
                "; originalUnityRootWasObb=" + (reported.IndexOf(".obb!/", StringComparison.OrdinalIgnoreCase) >= 0), true);
            // Load every original bank from the actual APK/OBB archive before
            // scene emitters run. Never extract the full expansion on disk.
            foreach (string name in new[] { "MasterBank.strings.bank", "MasterBank.bank", "VO_logs_english.bank", "VO_npc_english.bank", "VO_olof_english.bank" })
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Stage("fmod.expansion_bank." + name, () =>
                {
                    byte[] bytes = RaftAndroid.Platform.AndroidStreamingAssets.ReadAllBytes(root + "/" + name);
                    // Require the independently authenticated original bank bytes before FMOD.
                    // A correct OBB filename alone cannot detect a damaged/replaced ZIP entry.
                    AndroidOriginalBankIdentity.Verify(name, bytes);
                    FMOD.Studio.Bank bank;
                    FMOD.RESULT result = FMODUnity.RuntimeManager.StudioSystem.loadBankMemory(
                        bytes, FMOD.Studio.LOAD_BANK_FLAGS.NORMAL, out bank);
                    // RuntimeManager may have already loaded the exact bank
                    // from APK StreamingAssets. FMOD reports that explicitly;
                    // it is not an absent/corrupt bank or a reason to crash.
                    if (result == FMOD.RESULT.ERR_EVENT_ALREADY_LOADED)
                    {
                        RaftAndroid.Diagnostics.AndroidRuntimeLog.Write(
                            "audio", "fmod_bank_already_loaded", "bank=" + name, true);
                        return;
                    }
                    Check(result, "load original bank " + name);
                    if (!bank.isValid()) throw new InvalidOperationException("FMOD original bank handle is invalid: " + name);
                    // EventNotFound during original JoinGame can abort world
                    // initialization. Record the real event index loaded from
                    // each authentic bank; no fake event or success flag.
                    int eventCount = 0;
                    FMOD.RESULT eventResult = bank.getEventCount(out eventCount);
                    RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("audio", "fmod_expansion_bank_events",
                        "bank=" + name + "; result=" + eventResult +
                        "; eventCount=" + (eventResult == FMOD.RESULT.OK ? eventCount.ToString() : "unavailable"),
                        eventResult != FMOD.RESULT.OK);
                });
            }
            // Owner's last native trace failed at AudioSettingsBox.SettingStart
            // resolving exactly vca:/master. Distinguish missing master metadata
            // from scene-emitter issues after loading every authentic bank.
            FMOD.Studio.VCA masterVca;
            FMOD.RESULT vcaResult = FMODUnity.RuntimeManager.StudioSystem.getVCA(
                "vca:/master", out masterVca);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write(
                "audio", "fmod.master_vca_probe",
                "result=" + vcaResult + "; valid=" +
                (vcaResult == FMOD.RESULT.OK && masterVca.isValid()),
                vcaResult != FMOD.RESULT.OK);
        }

        private static long ReadInstalledVersionCode()
        {
            // OBB filenames are keyed to the installed Android versionCode,
            // not Unity's human-readable Application.version.
            using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
            {
                if (activity == null)
                    throw new InvalidOperationException("Android activity unavailable for package version lookup");
                using (var manager = activity.Call<AndroidJavaObject>("getPackageManager"))
                using (var info = manager.Call<AndroidJavaObject>(
                    "getPackageInfo", Application.identifier, 0))
                using (var build = new AndroidJavaClass("android.os.Build$VERSION"))
                {
                    if (info == null)
                        throw new InvalidOperationException("Installed Android PackageInfo unavailable");
                    long versionCode = build.GetStatic<int>("SDK_INT") >= 28
                        ? info.Call<long>("getLongVersionCode")
                        : info.Get<int>("versionCode");
                    if (versionCode <= 0)
                        throw new InvalidOperationException("Invalid installed Android versionCode");
                    return versionCode;
                }
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

