using System;
using System.IO;
using UnityEngine;

namespace RaftGraphicsLab
{
    /// <summary>Independent original-mesh viewer: visual proof is owner/device only.</summary>
    public sealed class GfxLabViewer : MonoBehaviour
    {
        public Transform modelRoot;
        public Camera sceneCamera;
        public Renderer[] modelRenderers = new Renderer[0];
        public Material whiteLit;
        public Material whiteUnlit;
        public int meshCount;
        public int vertexCount;
        public int triangleCount;
        public string sourceCategory = "UNKNOWN";

        private float yaw = -25f;
        private float pitch = 12f;
        private float distance = 3.8f;
        private bool unlit;
        private bool spin;
        private int reportCopies;
        private int logErrors;
        private string firstError = "";
        private string reportFile = "";
        private Vector2 priorTouch;
        private float priorPinch;
        private bool touching;

        [Serializable]
        private struct Report
        {
            public string experiment;
            public string sourceCategory;
            public string deviceModel;
            public string gfxDevice;
            public string gfxApi;
            public string gfxVersion;
            public string unity;
            public string colorSpace;
            public bool whiteShaderSupported;
            public bool unlitShaderSupported;
            public bool originalGeometry;
            public int meshCount;
            public int vertices;
            public int triangles;
            public int renderers;
            public int errors;
            public string firstError;
            public string mode;
            public string utc;
        }

        private void Start()
        {
            Application.logMessageReceived += OnLog;
            Debug.Log("GFXLAB_VIEWER_STARTED original_geometry=true source_category=" + sourceCategory);
            SaveReport();
        }

        private void OnDestroy()
        {
            Application.logMessageReceived -= OnLog;
        }

        private void OnLog(string condition, string stackTrace, LogType type)
        {
            if (type != LogType.Exception && type != LogType.Error && type != LogType.Assert) return;
            logErrors++;
            if (firstError.Length == 0)
                firstError = condition.Length > 200 ? condition.Substring(0, 200) : condition;
        }

        private void Update()
        {
            if (sceneCamera == null) return;
            if (spin) yaw += Time.deltaTime * 16f;
            if (Input.touchCount == 1)
            {
                var t = Input.GetTouch(0);
                if (t.phase == TouchPhase.Moved && t.position.y < Screen.height * 0.80f)
                {
                    yaw += t.deltaPosition.x * .18f;
                    pitch = Mathf.Clamp(pitch - t.deltaPosition.y * .12f, -55f, 65f);
                }
                priorPinch = 0;
            }
            else if (Input.touchCount >= 2)
            {
                Vector2 a = Input.GetTouch(0).position;
                Vector2 b = Input.GetTouch(1).position;
                float current = Vector2.Distance(a, b);
                if (priorPinch > 0)
                    distance = Mathf.Clamp(distance + (priorPinch - current) * .008f, 1.5f, 9f);
                priorPinch = current;
            }
            else
            {
                priorPinch = 0;
                if (Input.GetMouseButton(0))
                {
                    yaw += Input.GetAxis("Mouse X") * 3.5f;
                    pitch = Mathf.Clamp(pitch - Input.GetAxis("Mouse Y") * 3.5f, -55f, 65f);
                }
                distance = Mathf.Clamp(distance - Input.mouseScrollDelta.y * .3f, 1.5f, 9f);
            }
            var center = new Vector3(0f, 1.05f, 0f);
            Quaternion angle = Quaternion.Euler(pitch, yaw, 0f);
            sceneCamera.transform.position = center + angle * new Vector3(0, 0, -distance);
            sceneCamera.transform.LookAt(center);
        }

        private void SetMode(bool newUnlit)
        {
            unlit = newUnlit;
            var selected = unlit ? whiteUnlit : whiteLit;
            foreach (Renderer renderer in modelRenderers)
            {
                if (renderer == null) continue;
                var mats = renderer.sharedMaterials;
                for (int n = 0; n < mats.Length; n++) mats[n] = selected;
                if (mats.Length == 0) mats = new [] { selected };
                renderer.sharedMaterials = mats;
            }
            SaveReport();
        }

        private string BuildReport()
        {
            var r = new Report
            {
                experiment = "GFX-AVATAR-001", sourceCategory = sourceCategory,
                deviceModel = SystemInfo.deviceModel,
                gfxDevice = SystemInfo.graphicsDeviceName, gfxApi = SystemInfo.graphicsDeviceType.ToString(),
                gfxVersion = SystemInfo.graphicsDeviceVersion, unity = Application.unityVersion,
                colorSpace = QualitySettings.activeColorSpace.ToString(),
                whiteShaderSupported = whiteLit != null && whiteLit.shader != null && whiteLit.shader.isSupported,
                unlitShaderSupported = whiteUnlit != null && whiteUnlit.shader != null && whiteUnlit.shader.isSupported,
                originalGeometry = meshCount > 0 && vertexCount > 0, meshCount = meshCount,
                vertices = vertexCount, triangles = triangleCount, renderers = modelRenderers.Length,
                errors = logErrors, firstError = firstError,
                mode = unlit ? "UNLIT_WHITE" : "LIT_WHITE",
                utc = DateTime.UtcNow.ToString("o")
            };
            return JsonUtility.ToJson(r, true);
        }

        private void SaveReport()
        {
            try
            {
                var p = Path.Combine(Application.persistentDataPath, "gfxlab");
                Directory.CreateDirectory(p);
                reportFile = Path.Combine(p, "report.json");
                File.WriteAllText(reportFile, BuildReport());
            }
            catch (Exception e)
            {
                Debug.LogWarning("GFXLAB_SAVE_REPORT_FAILED " + e.GetType().Name);
            }
        }

        private void OnApplicationPause(bool paused) { if (paused) SaveReport(); }
        private void OnApplicationQuit() { SaveReport(); }

        private void OnGUI()
        {
            float s = Mathf.Clamp(Screen.width / 900f, .8f, 1.6f);
            var style = new GUIStyle(GUI.skin.label) { fontSize = Mathf.RoundToInt(22f * s), normal = { textColor = Color.white } };
            var btn = new GUIStyle(GUI.skin.button) { fontSize = Mathf.RoundToInt(19f * s) };
            float panelHeight = 145f * s;
            GUI.Box(new Rect(12, 12, Screen.width - 24, panelHeight), "");
            GUI.Label(new Rect(24, 18, Screen.width - 35, 30*s),
                "RAFT Graphics Lab — ORIGINAL MESH (white material)", style);
            GUI.Label(new Rect(24, 47*s, Screen.width - 35, 30*s),
                "Model: " + sourceCategory + "   Parts: " + meshCount + "   Vertices: " + vertexCount, style);
            GUI.Label(new Rect(24, 76*s, Screen.width - 35, 30*s),
                "GPU: " + SystemInfo.graphicsDeviceName + "   " + SystemInfo.graphicsDeviceType, style);
            float y = 107f*s; float w = (Screen.width-48)/4f;
            if (GUI.Button(new Rect(20, y, w, 42*s), unlit ? "LIT WHITE" : "UNLIT WHITE", btn)) SetMode(!unlit);
            if (GUI.Button(new Rect(25+w, y, w, 42*s), spin ? "STOP SPIN" : "SPIN", btn)) spin = !spin;
            if (GUI.Button(new Rect(30+2*w, y, w, 42*s), "RESET VIEW", btn)) { yaw = -25f; pitch = 12f; distance = 3.8f; }
            if (GUI.Button(new Rect(35+3*w, y, w, 42*s), "COPY LOG", btn))
            {
                SaveReport();
                GUIUtility.systemCopyBuffer = BuildReport();
                reportCopies++;
                Debug.Log("GFXLAB_REPORT_COPIED copies=" + reportCopies + " file=Application.persistentDataPath/gfxlab/report.json");
            }
            GUI.Label(new Rect(22, Screen.height - 37*s, Screen.width-32, 31*s),
                "Drag to rotate  |  Pinch to zoom  |  COPY LOG copies JSON report", style);
        }
    }
}
