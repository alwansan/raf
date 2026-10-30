#if UNITY_EDITOR
using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace RaftAndroid.Editor
{
    // Original CI code. Does not replace gameplay or alter recovered scene order.
    public static class AndroidNativeBuild
    {
        public static void Build()
        {
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.Android)
                throw new BuildFailedException("Unity must be launched with the Android build target.");

            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
            EditorUserBuildSettings.buildAppBundle = false;

            string version = Argument("-androidVersionCode", "1");
            if (!int.TryParse(version, out int code) || code <= 0)
                throw new BuildFailedException("Android version code must be a positive integer.");
            PlayerSettings.Android.bundleVersionCode = code;

            string output = Argument("-customBuildPath", "builds/Android/RaftAndroidExperimental.apk");
            if (!output.EndsWith(".apk", StringComparison.OrdinalIgnoreCase))
                throw new BuildFailedException("Expected an APK output path.");
            output = Path.GetFullPath(output);
            Directory.CreateDirectory(Path.GetDirectoryName(output));

            var scenes = EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray();
            if (scenes.Length == 0 || scenes.Any(s => !File.Exists(s)))
                throw new BuildFailedException("Enabled original build scenes are missing; refusing a dummy scene build.");

            AssetDatabase.SaveAssets();
            Debug.Log("RAFT_ANDROID_NATIVE_CONFIG backend=" +
                      PlayerSettings.GetScriptingBackend(BuildTargetGroup.Android) +
                      " architectures=" + PlayerSettings.Android.targetArchitectures +
                      " enabledScenes=" + scenes.Length);

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = scenes,
                target = BuildTarget.Android,
                locationPathName = output,
                options = BuildOptions.CompressWithLz4
            });
            Debug.Log("RAFT_ANDROID_NATIVE_RESULT result=" + report.summary.result +
                      " errors=" + report.summary.totalErrors +
                      " bytes=" + report.summary.totalSize);
            if (report.summary.result != BuildResult.Succeeded)
                throw new BuildFailedException("Native ARM64 Android build failed; inspect the preceding Unity diagnostics.");
        }

        private static string Argument(string name, string fallback)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i + 1 < args.Length; ++i)
                if (args[i] == name) return args[i + 1];
            return fallback;
        }
    }
}
#endif
