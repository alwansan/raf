using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace RaftGT
{
    /// <summary>
    /// Isolated Android phone build of an original-derived Particle108 candidate.
    /// NO original game scene, Material, GUID, texture or sampler parity claims.
    /// The private source shader is generated on the runner only. The APK is
    /// diagnostic and uses deliberately approximate texture sampler states.
    /// </summary>
    public static class GTParticlePhoneBuild
    {
        [Serializable]
        private sealed class SafeBuild
        {
            public string status;
            public string unityVersion;
            public string failureType;
            public int privateVariants;
            public int shaderErrors;
            public long apkBytes;
            public bool androidVulkanOnly;
            public bool arm64;
            public bool offline;
            public bool approximateSamplerStates;
            public bool originalMaterialBindingProven;
            public bool originalShaderRestored;
            public bool actualDevicePixelsVerified;
            public bool originalGameAssetsChanged;
        }

        private const string ShaderAsset = "Assets/GTPrivateOriginal.shader";
        private const string SceneAsset = "Assets/GTParticlePhoneScene.unity";
        private const string PackageId = "com.alwansan.raft.gtparticle108approx";

        private static Texture2D CreateDiagnosticTexture()
        {
            var texture = new Texture2D(64, 64, TextureFormat.RGBA32, false);
            texture.name = "GeneratedCheckerOnly";
            texture.filterMode = FilterMode.Bilinear;
            texture.wrapMode = TextureWrapMode.Repeat;
            var colors = new Color[64 * 64];
            for (int y = 0; y < 64; y++)
                for (int x = 0; x < 64; x++)
                    colors[y * 64 + x] = (((x / 8) + (y / 8)) % 2 == 0)
                        ? new Color(0.9f, 0.8f, 0.35f, 1f)
                        : new Color(0.12f, 0.6f, 0.8f, 1f);
            texture.SetPixels(colors);
            texture.Apply();
            AssetDatabase.CreateAsset(texture, "Assets/GTGeneratedChecker.asset");
            return texture;
        }

        private static Material[] MakeVariants(Shader shader, string[] keywords, Texture2D texture)
        {
            var result = new Material[4];
            for (int bits = 0; bits < 4; bits++)
            {
                var material = new Material(shader);
                material.name = "ApproxPrivateVariant" + bits;
                material.shaderKeywords = keywords.Where((word, i) =>
                    (bits & (1 << i)) != 0).ToArray();
                for (int p = 0; p < ShaderUtil.GetPropertyCount(shader); p++)
                {
                    if (ShaderUtil.GetPropertyType(shader, p) == ShaderUtil.ShaderPropertyType.TexEnv)
                        material.SetTexture(ShaderUtil.GetPropertyName(shader, p), texture);
                }
                AssetDatabase.CreateAsset(material,
                    "Assets/GTApproxPrivateVariant" + bits + ".mat");
                result[bits] = material;
            }
            return result;
        }

        private static Renderer[] CreateDiagnostics(Material firstVariant)
        {
            var renderers = new Renderer[3];
            for (int i = 0; i < 2; i++)
            {
                var quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
                quad.name = "ApproxShaderQuad_" + i;
                quad.transform.position = new Vector3(-2.4f + i * 2.4f, -1.15f, 0f);
                quad.transform.localScale = new Vector3(2.2f, 2.2f, 1f);
                renderers[i] = quad.GetComponent<Renderer>();
                renderers[i].sharedMaterial = firstVariant;
            }
            var go = new GameObject("ApproxParticleRenderer");
            go.transform.position = new Vector3(2.4f, -1.15f, 0f);
            var particle = go.AddComponent<ParticleSystem>();
            var main = particle.main;
            main.loop = true;
            main.startLifetime = 3f;
            main.startSpeed = 0.25f;
            main.startSize = 0.45f;
            main.startColor = Color.white;
            var emission = particle.emission;
            emission.rateOverTime = 6f;
            var shape = particle.shape;
            shape.shapeType = ParticleSystemShapeType.Circle;
            shape.radius = 0.7f;
            var pr = go.GetComponent<ParticleSystemRenderer>();
            pr.renderMode = ParticleSystemRenderMode.Billboard;
            pr.sharedMaterial = firstVariant;
            renderers[2] = pr;
            return renderers;
        }

        private static void MakeScene(Material[] variants)
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var cameraGo = new GameObject("ApproxPhoneCamera");
            cameraGo.transform.position = new Vector3(0f, 0f, -11f);
            cameraGo.transform.rotation = Quaternion.identity;
            var camera = cameraGo.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.035f, 0.055f, 0.09f);
            camera.fieldOfView = 46f;
            var ui = cameraGo.AddComponent<GTParticlePhoneRuntime>();
            ui.privateVariants = variants;
            ui.testRenderers = CreateDiagnostics(variants[0]);
            var light = new GameObject("DiagnosticLight");
            light.transform.rotation = Quaternion.Euler(40f, -30f, 0f);
            light.AddComponent<Light>().type = LightType.Directional;
            if (!EditorSceneManager.SaveScene(scene, SceneAsset))
                throw new InvalidOperationException("PrivateSceneSaveFailed");
        }

        public static void Build()
        {
            var result = new SafeBuild
            {
                status = "INCONCLUSIVE",
                unityVersion = Application.unityVersion,
                approximateSamplerStates = true,
                offline = true,
                originalMaterialBindingProven = false,
                originalShaderRestored = false,
                actualDevicePixelsVerified = false,
                originalGameAssetsChanged = false
            };
            string root = Directory.GetParent(Application.dataPath).FullName;
            string evidence = Path.Combine(root, "ProbeResults");
            Directory.CreateDirectory(evidence);
            int exitCode = 1;
            try
            {
                if (Application.unityVersion != "2021.3.45f2")
                    throw new InvalidOperationException("UnpinnedUnityVersion");
                if (AssetDatabase.LoadAssetAtPath<GTParticlePhoneRuntime>(
                        "Assets/GTParticlePhoneRuntime.cs") == null)
                {
                    // Runtime script is a MonoScript, not the MonoBehaviour
                    // itself. The C# reference used in MakeScene is the
                    // authoritative compile-time type check.
                    if (!File.Exists(Path.Combine(root, "Assets/GTParticlePhoneRuntime.cs")))
                        throw new InvalidOperationException("PrivateRuntimeCodeMissing");
                }
                PlayerSettings.companyName = "alwansan";
                PlayerSettings.productName = "Raft Particle108 Approx Diagnostic";
                PlayerSettings.bundleVersion = "0.1.0";
                PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, PackageId);
                PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
                PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android,
                    ScriptingImplementation.IL2CPP);
                PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
                    new[] { GraphicsDeviceType.Vulkan });
                result.androidVulkanOnly = PlayerSettings.GetGraphicsAPIs(BuildTarget.Android)
                    .SequenceEqual(new[] { GraphicsDeviceType.Vulkan });
                result.arm64 = PlayerSettings.Android.targetArchitectures == AndroidArchitecture.ARM64;
                if (!result.androidVulkanOnly || !result.arm64)
                    throw new InvalidOperationException("PrivateAndroidTargetNotVulkanArm64");
                EditorUserBuildSettings.buildAppBundle = false;
                AssetDatabase.ImportAsset(ShaderAsset,
                    ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
                Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(ShaderAsset);
                if (shader == null)
                    throw new InvalidOperationException("PrivateShaderMissing");
                string source = File.ReadAllText(Path.Combine(root, ShaderAsset));
                string[] keywords = Regex.Matches(source,
                    @"(?m)^[ \t]*#pragma multi_compile __ ([A-Za-z_][A-Za-z_0-9]*)[ \t]*$")
                    .Cast<Match>().Select(match => match.Groups[1].Value).ToArray();
                if (keywords.Length != 2 || keywords.Distinct().Count() != 2)
                    throw new InvalidOperationException("PrivateKeywordMatrixChanged");
                result.shaderErrors = ShaderUtil.GetShaderMessages(shader)
                    .Count(message => message.severity.ToString() == "Error");
                if (result.shaderErrors != 0 || ShaderUtil.ShaderHasError(shader))
                    throw new InvalidOperationException("PrivateShaderHasErrors");
                var texture = CreateDiagnosticTexture();
                Material[] variants = MakeVariants(shader, keywords, texture);
                result.privateVariants = variants.Length;
                MakeScene(variants);
                AssetDatabase.SaveAssets();
                string outputDir = Path.Combine(root, "Build");
                Directory.CreateDirectory(outputDir);
                string apk = Path.Combine(outputDir, "GT-Particle108-Approx-Vulkan-ARM64.apk");
                BuildReport build = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                    scenes = new[] { SceneAsset },
                    locationPathName = apk,
                    target = BuildTarget.Android,
                    options = BuildOptions.Development | BuildOptions.AllowDebugging
                });
                result.apkBytes = File.Exists(apk) ? new FileInfo(apk).Length : 0;
                if (build.summary.result != BuildResult.Succeeded || result.apkBytes < 1024)
                    throw new InvalidOperationException("PrivateAndroidPlayerBuildFailed");
                result.status = "GT_PARTICLE108_APPROX_ANDROID_VULKAN_PHONE_APK_BUILT";
                exitCode = 0;
            }
            catch (Exception e)
            {
                // Public report only contains exception TYPE, no source
                // shader names, HLSL, GUIDs or compiler messages.
                result.failureType = e.GetType().Name;
            }
            string json = JsonUtility.ToJson(result, true);
            File.WriteAllText(Path.Combine(evidence, "gt-particle108-phone-build-safe.json"), json);
            Debug.Log("GT_PARTICLE108_PHONE_BUILD_SAFE " + json);
            EditorApplication.Exit(exitCode);
        }
    }
}
