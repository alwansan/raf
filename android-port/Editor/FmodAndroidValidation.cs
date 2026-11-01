#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

namespace RaftAndroid.Editor
{
    public static class FmodAndroidValidation
    {
        public static void Validate()
        {
            // Never use Settings.Instance here: it can manufacture default settings.
            var platforms = Resources.LoadAll<FMODUnity.Platform>("FMODStudioSettings");
            // The vendor Settings.OnEnable destroys duplicate platform assets. Refuse
            // ambiguous original identities before explicitly loading that Settings.
            var identifiers = platforms.Select(p => new SerializedObject(p).FindProperty("identifier")).ToArray();
            if (identifiers.Any(p => p == null) ||
                identifiers.Select(p => p.stringValue).Distinct().Count() != platforms.Length)
                throw new BuildFailedException("Original FMOD platform identities are ambiguous; no assets cleaned up.");
            var settings = Resources.Load<FMODUnity.Settings>("FMODStudioSettings");
            int android = platforms.Count(p => p is FMODUnity.PlatformAndroid);
            int defaults = platforms.Count(p => p is FMODUnity.PlatformDefault);
            Debug.Log("RAFT_FMOD_ORIGINAL_SETTINGS settingsPresent=" + (settings != null) +
                      " resourcePlatforms=" + platforms.Length + " androidPlatforms=" + android +
                      " defaultPlatforms=" + defaults + " manufacturedSettings=0");
            if (settings == null || android != 1 || defaults != 1)
                throw new BuildFailedException("Original FMOD settings/platform resource layout is incomplete; no defaults substituted.");
            var version = new SerializedObject(settings).FindProperty("CurrentVersion");
            Debug.Log("RAFT_FMOD_ORIGINAL_CONFIGURATION version=" + (version == null ? -1 : version.intValue) +
                      " androidUseOBB=" + settings.AndroidUseOBB +
                      " importType=" + settings.ImportType +
                      " bankSubfolderEmpty=" + string.IsNullOrEmpty(settings.TargetSubFolder));
            if (version == null || version.intValue != 0x00020215)
                throw new BuildFailedException("Original FMOD settings version mismatch.");
            if (settings.AndroidUseOBB)
                throw new BuildFailedException("Original FMOD OBB loading requires a separate verified adapter.");
            if (settings.ImportType != FMODUnity.ImportType.StreamingAssets)
                throw new BuildFailedException("Original FMOD bank import mode requires original-path validation.");
            if (!string.IsNullOrEmpty(settings.TargetSubFolder))
                throw new BuildFailedException("Original FMOD bank subfolder requires original-path validation before staging.");
            foreach (string name in new[] { "libfmod.so", "libfmodstudio.so", "libresonanceaudio.so" })
            {
                string path = "Assets/Plugins/FMOD/platforms/android/lib/arm64-v8a/" + name;
                var importer = AssetImporter.GetAtPath(path) as PluginImporter;
                if (importer == null || !importer.GetCompatibleWithPlatform(BuildTarget.Android) ||
                    importer.GetCompatibleWithEditor() || importer.GetPlatformData(BuildTarget.Android, "CPU") != "ARM64")
                    throw new BuildFailedException("Audited FMOD Android plugin importer is not ARM64-only: " + name);
            }
            Debug.Log("RAFT_FMOD_ANDROID_IMPORTERS arm64Libraries=3 editorEnabled=0 originalProvidersPreserved=true");
        }

        public static void RequireOriginalBanks()
        {
            foreach (string bank in new[] { "MasterBank.bank", "MasterBank.strings.bank", "VO_logs_english.bank", "VO_npc_english.bank", "VO_olof_english.bank" })
                if (!File.Exists(Path.Combine(Application.streamingAssetsPath, bank)))
                    throw new BuildFailedException("Verified original FMOD bank was not staged: " + bank);
        }
    }
}
#endif
