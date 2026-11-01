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
            // The original Platform assets live at Resources/FMODStudioSettingsPlatform*.asset,
            // not inside a Resources/FMODStudioSettings/ directory. Resources.LoadAll with
            // the settings asset name finds no platforms. Enumerate only those original
            // root assets, and prove each resolves through the player-facing Resources API.
            string resourceRoot = Path.Combine(Application.dataPath, "Resources");
            if (!Directory.Exists(resourceRoot))
                throw new BuildFailedException("Original FMOD Resources directory is missing.");
            string[] platformFiles = Directory.GetFiles(resourceRoot, "FMODStudioSettingsPlatform*.asset",
                    SearchOption.TopDirectoryOnly)
                .OrderBy(p => p, StringComparer.Ordinal).ToArray();
            if (platformFiles.Length == 0)
                throw new BuildFailedException("Original FMOD platform resource files are missing.");
            var platforms = platformFiles.Select(path =>
            {
                string name = Path.GetFileNameWithoutExtension(path);
                string assetPath = "Assets/Resources/" + Path.GetFileName(path);
                var original = AssetDatabase.LoadAssetAtPath<FMODUnity.Platform>(assetPath);
                var runtime = Resources.Load<FMODUnity.Platform>(name);
                if (original == null || runtime == null || original != runtime)
                    throw new BuildFailedException("Original FMOD platform is not loadable by resource name: " + name);
                return runtime;
            }).ToArray();
            Debug.Log("RAFT_FMOD_PLATFORM_RESOURCE_LOOKUP candidates=" + platformFiles.Length +
                      " loaded=" + platforms.Length + " strategy=exact-original-filenames");
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
