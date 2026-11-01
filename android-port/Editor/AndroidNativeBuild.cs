#if UNITY_EDITOR
using System;
using System.IO;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
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
        public static void ValidateSdkBindings()
        {
            SdkScriptBindingResolver.Rebind(Path.Combine(Application.dataPath, "Editor/RaftAndroid/sdk-script-manifest.json"));
            MicroSplatPropertyTextureRecovery.Restore();
            FmodAndroidValidation.Validate();
            ReportInputBindings();
            ValidatePostFxHistogram();
            Debug.Log("RAFT_SDK_VALIDATION_COMPLETE noAndroidBuildRequested=true");
        }

        private static void ValidatePostFxHistogram()
        {
            var histogram = Resources.Load<ComputeShader>("Shaders/EyeHistogram");
            if (histogram == null)
                throw new BuildFailedException("Original PostFX histogram Resources identity is unresolved.");
            foreach (string name in new[] { "KEyeHistogram", "KEyeHistogramClear" })
            {
                int kernel = histogram.FindKernel(name);
                histogram.GetKernelThreadGroupSizes(kernel, out uint x, out uint y, out uint z);
                uint expectedY = name == "KEyeHistogram" ? 16u : 1u;
                if (x != 16u || y != expectedY || z != 1u)
                    throw new BuildFailedException("PostFX histogram kernel thread-group contract mismatch.");
            }
            Debug.Log("RAFT_POSTFX_COMPUTE_GATE resource=Shaders/EyeHistogram kernels=2 imported=true deviceDispatchVerified=false");
        }

        private static void ReportInputBindings()
        {
            var guids = AssetDatabase.FindAssets("t:InputActionAsset");
            int assets = 0, bindings = 0, touch = 0, mouse = 0, keyboard = 0, gamepad = 0;
            foreach (string guid in guids)
            {
                var asset = AssetDatabase.LoadAssetAtPath<UnityEngine.InputSystem.InputActionAsset>(AssetDatabase.GUIDToAssetPath(guid));
                if (asset == null) continue;
                assets++;
                foreach (var map in asset.actionMaps)
                foreach (var binding in map.bindings)
                {
                    bindings++;
                    string path = binding.effectivePath ?? "";
                    if (path.IndexOf("<Touchscreen>", StringComparison.OrdinalIgnoreCase) >= 0) touch++;
                    if (path.IndexOf("<Mouse>", StringComparison.OrdinalIgnoreCase) >= 0) mouse++;
                    if (path.IndexOf("<Keyboard>", StringComparison.OrdinalIgnoreCase) >= 0) keyboard++;
                    if (path.IndexOf("<Gamepad>", StringComparison.OrdinalIgnoreCase) >= 0) gamepad++;
                }
            }
            Debug.Log("RAFT_INPUT_BINDING_INVENTORY assets=" + assets + " bindings=" + bindings +
                      " touchscreen=" + touch + " mouse=" + mouse + " keyboard=" + keyboard +
                      " gamepad=" + gamepad + " deviceBehaviorVerified=false");
        }

        public static void Build()
        {
            ValidateSdkBindings();
            FmodAndroidValidation.RequireOriginalBanks();
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.Android)
                throw new BuildFailedException("Unity must be launched with the Android build target.");

            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, "com.alwansan.raft.androidtest");
            PlayerSettings.productName = "Raft Android Test";
            // Force Android's launch Activity to landscape before the first Unity frame.
            // The runtime may still permit both landscape rotations after startup.
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
            PlayerSettings.allowedAutorotateToPortrait = false;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
            PlayerSettings.allowedAutorotateToLandscapeLeft = true;
            PlayerSettings.allowedAutorotateToLandscapeRight = true;
            PlayerSettings.enableFrameTimingStats = true;
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
            // This recovered game has exactly 40 original level scenes. A one-scene
            // or partial export must never be presented as a complete Raft APK.
            // Case-insensitive uniqueness also rejects case-only collisions on Linux.
            if (scenes.Length != 40 ||
                scenes.Distinct(StringComparer.OrdinalIgnoreCase).Count() != 40 ||
                scenes.Any(s => !s.EndsWith(".unity", StringComparison.OrdinalIgnoreCase) ||
                                !File.Exists(s)))
                throw new BuildFailedException("Expected exactly 40 distinct existing original Unity scenes; refusing a partial Android APK.");
            Debug.Log("RAFT_ANDROID_SCENE_GATE originalScenes=40 uniquePaths=true");

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
            ReportDiagnosticClasses(report);
            Debug.Log("RAFT_ANDROID_NATIVE_RESULT result=" + report.summary.result +
                      " errors=" + report.summary.totalErrors +
                      " bytes=" + report.summary.totalSize);
            if (report.summary.result != BuildResult.Succeeded)
                throw new BuildFailedException("Native ARM64 Android build failed; inspect the preceding Unity diagnostics.");
        }

        private static void ReportDiagnosticClasses(BuildReport report)
        {
            var classes = new SortedDictionary<string, int>(StringComparer.Ordinal);
            var unknown = new SortedDictionary<string, int>(StringComparer.Ordinal);
            int occurrences = 0;
            foreach (var step in report.steps)
            foreach (var message in step.messages)
            {
                if (message.type != LogType.Error && message.type != LogType.Assert &&
                    message.type != LogType.Exception) continue;
                occurrences++;
                string text = (message.content ?? "").ToLowerInvariant();
                string category =
                    text.Contains("kfirstvalidstandalonetarget") ? "standalone_target_assertion" :
                    text.Contains("texture2d.setpixels") && text.Contains("unsupported") ? "property_texture_write" :
                    text.Contains("nullreferenceexception") ? "null_reference" :
                    text.Contains("shader") ? "shader" :
                    text.Contains("texture") ? "other_texture" :
                    text.Contains("serializ") ? "serialization" :
                    text.Contains("script") ? "script_binding" : "other";
                if (!classes.ContainsKey(category)) classes[category] = 0;
                classes[category]++;
                if (category == "other")
                {
                    string digest;
                    using (var sha = SHA256.Create())
                        digest = BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(text)))
                            .Replace("-", "").Substring(0, 16).ToLowerInvariant();
                    if (!unknown.ContainsKey(digest)) unknown[digest] = 0;
                    unknown[digest]++;
                }
            }
            Debug.Log("RAFT_BUILDREPORT_DIAGNOSTIC_CLASSES messageOccurrences=" + occurrences +
                      " categories=" + string.Join(",", classes.Select(p => p.Key + ":" + p.Value)) +
                      " unknownMessageHashes=" + string.Join(",", unknown.Take(12).Select(p => p.Key + ":" + p.Value)) +
                      " notEquivalentToSummaryTotalErrors=true");
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
