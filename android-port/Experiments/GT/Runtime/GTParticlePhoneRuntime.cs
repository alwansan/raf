using System;
using System.IO;
using UnityEngine;

namespace RaftGT
{
    /// <summary>
    /// Original-derived Shader48 PHONE DIAGNOSTIC ONLY. Approximate samplers,
    /// no original Material/GUID/Texture or visual parity claim.
    /// Works fully offline, with no game assets in this isolated test scene.
    /// </summary>
    public sealed class GTParticlePhoneRuntime : MonoBehaviour
    {
        public Material[] privateVariants;
        public Renderer[] testRenderers;
        private int selected;
        private float smoothedFps = 0f;
        private string copyStatus = "Ready";
        private const string Schema = "GT_PARTICLE108_APPROX_PHONE_V1";

        [Serializable]
        private sealed class SafeDeviceLog
        {
            public string schema;
            public string unityVersion;
            public string androidVersion;
            public string graphicsDeviceType;
            public string graphicsDeviceName;
            public int screenWidth;
            public int screenHeight;
            public int currentVariant;
            public int variantCount;
            public bool shaderSupported;
            public bool vulkanActive;
            public bool approximateSamplerStates;
            public bool originalMaterialBindingProven;
            public bool originalShaderRestored;
            public bool originalAdrenoPixelsVerified;
            public float fps;
        }

        private void Awake()
        {
            Screen.orientation = ScreenOrientation.LandscapeLeft;
            Application.targetFrameRate = 60;
            Activate(0);
            SaveSnapshot();
        }

        private void Update()
        {
            if (Time.unscaledDeltaTime > 0.001f)
            {
                float sample = 1f / Time.unscaledDeltaTime;
                smoothedFps = Mathf.Lerp(smoothedFps, sample, 0.06f);
            }
        }

        private SafeDeviceLog Capture()
        {
            var chosen = privateVariants != null && privateVariants.Length > selected
                ? privateVariants[selected] : null;
            return new SafeDeviceLog
            {
                schema = Schema,
                unityVersion = Application.unityVersion,
                androidVersion = SystemInfo.operatingSystem,
                graphicsDeviceType = SystemInfo.graphicsDeviceType.ToString(),
                graphicsDeviceName = SystemInfo.graphicsDeviceName,
                screenWidth = Screen.width,
                screenHeight = Screen.height,
                currentVariant = selected,
                variantCount = privateVariants == null ? 0 : privateVariants.Length,
                shaderSupported = chosen != null && chosen.shader != null && chosen.shader.isSupported,
                vulkanActive = SystemInfo.graphicsDeviceType == UnityEngine.Rendering.GraphicsDeviceType.Vulkan,
                approximateSamplerStates = true,
                originalMaterialBindingProven = false,
                originalShaderRestored = false,
                originalAdrenoPixelsVerified = false,
                fps = smoothedFps
            };
        }

        private void Activate(int index)
        {
            if (privateVariants == null || privateVariants.Length != 4
                || index < 0 || index >= privateVariants.Length)
            {
                copyStatus = "Variant data invalid";
                return;
            }
            selected = index;
            foreach (var r in testRenderers)
                if (r != null) r.sharedMaterial = privateVariants[index];
            Debug.Log("GT_PARTICLE108_APPROX_SELECTED " + selected);
        }

        private string SaveSnapshot()
        {
            string json = JsonUtility.ToJson(Capture(), true);
            try
            {
                string path = Path.Combine(Application.persistentDataPath,
                    "gt-particle108-approx-phone.json");
                File.WriteAllText(path, json);
            }
            catch (Exception)
            {
                // Clipboard remains the preferred user-facing export route.
            }
            Debug.Log("GT_PARTICLE108_APPROX_PHONE_SAFE " + json);
            return json;
        }

        private void OnGUI()
        {
            float factor = Mathf.Clamp(Screen.height / 740f, 0.7f, 1.8f);
            Matrix4x4 previous = GUI.matrix;
            GUI.matrix = Matrix4x4.Scale(new Vector3(factor, factor, 1f));
            var style = new GUIStyle(GUI.skin.label)
            {
                fontSize = 19,
                wordWrap = true,
                normal = { textColor = Color.white }
            };
            GUI.Box(new Rect(12, 12, 650, 202), "");
            GUI.Label(new Rect(26, 20, 620, 74),
                "Raft Particle108 - original-derived Vulkan probe\n" +
                "APPROX SAMPLERS - NOT ORIGINAL SHADER/MATERIAL RESTORATION", style);
            var snapshot = Capture();
            GUI.Label(new Rect(26, 96, 620, 100),
                "GPU: " + snapshot.graphicsDeviceName + " / " + snapshot.graphicsDeviceType +
                "\nShader supported: " + snapshot.shaderSupported +
                " | variant " + (selected + 1) + "/4 | FPS: " + smoothedFps.ToString("F0") +
                "\nOffline diagnostic: " + copyStatus, style);
            for (int i = 0; i < 4; i++)
            {
                int value = i;
                if (GUI.Button(new Rect(24 + i * 128, 223, 122, 55), "Variant " + (i + 1)))
                {
                    Activate(value);
                    SaveSnapshot();
                }
            }
            if (GUI.Button(new Rect(24, 292, 520, 62), "COPY LOG JSON"))
            {
                try
                {
                    GUIUtility.systemCopyBuffer = SaveSnapshot();
                    copyStatus = "JSON copied";
                }
                catch (Exception)
                {
                    copyStatus = "Clipboard unavailable; see logcat/app storage";
                }
            }
            GUI.matrix = previous;
        }
    }
}
