// Stage ONLY in a fresh, synthetic Unity project at the two paths below.
// Run: -batchmode -force-vulkan -executeMethod SyntheticMaterialAlphaValidation.Run
// No -nographics: a real Vulkan device and raster readback are required.
#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

public static class SyntheticMaterialAlphaValidation
{
    const string ShaderPath = "Assets/SyntheticMaterialAlpha.shader";
    const string ProbePath = "Assets/Editor/SyntheticMaterialAlphaValidation.cs";
    const int Width = 6, Height = 4;
    const float Tolerance = 0.002f, MinimumMismatch = 0.05f;
    static readonly Color Background = new Color(0.125f, 0.25f, 0.5f, 1f);
    static readonly Color Tint = new Color(0.5f, 0.75f, 0.25f, 1f);

    [Serializable] sealed class Sample
    {
        public int x, y;
        public float[] observed, expected, intended;
    }
    [Serializable] sealed class CaseResult
    {
        public string name, kind;
        public bool pass;
        public float max_error, intended_mismatch;
        public int checked_pixel_count;
        public Sample[] samples;
    }
    [Serializable] sealed class Receipt
    {
        public int schema_version = 1;
        public string run_id, status = "NOT_RUN", reason = "not_started";
        public string Unity_version, backend, active_color_space, graphics_device_name;
        public string shader_sha256, probe_sha256;
        public int rendered_case_count, positive_case_count, negative_controls_detected;
        public float max_error;
        public bool synthetic_only = true, Unity_render_executed;
        public bool Android_device, production_pixels, XAPK;
        public List<CaseResult> cases = new List<CaseResult>();
    }
    sealed class Unavailable : Exception
    {
        public Unavailable(string message) : base(message) { }
    }

    public static void Run()
    {
        var result = new Receipt {
            run_id = Option("RAFT_SYNTHETIC_ALPHA_RUN_ID", "-raftSyntheticAlphaRunId"),
            Unity_version = Application.unityVersion,
            backend = SystemInfo.graphicsDeviceType.ToString(),
            active_color_space = QualitySettings.activeColorSpace.ToString(),
            graphics_device_name = SystemInfo.graphicsDeviceName
        };
        var owned = new List<UnityEngine.Object>();
        RenderTexture previousTarget = RenderTexture.active;
        bool previousSrgb = GL.sRGBWrite;
        bool previousAsync = ShaderUtil.allowAsyncCompilation;
        RenderTexture target = null;
        string output = null;
        int exitCode = 2;
        try
        {
            string root = Directory.GetParent(Application.dataPath).FullName;
            output = OutsideProjectReport(root);
            if (String.IsNullOrWhiteSpace(result.run_id)) throw new Unavailable("missing_run_id");
            result.shader_sha256 = Hash(Path.Combine(root, ShaderPath));
            result.probe_sha256 = Hash(Path.Combine(root, ProbePath));
            CheckEnvironment();
            ShaderUtil.allowAsyncCompilation = false;
            AssetDatabase.ImportAsset(ShaderPath, ImportAssetOptions.ForceSynchronousImport);
            var shader = AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
            if (shader == null || !shader.isSupported || ShaderUtil.ShaderHasError(shader))
                throw new InvalidOperationException("synthetic_shader_unavailable_or_compile_error");

            // The launcher supplies a dedicated empty project; nothing is saved.
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            target = Own(new RenderTexture(Width, Height, 0,
                RenderTextureFormat.ARGBFloat, RenderTextureReadWrite.Linear), owned);
            target.antiAliasing = 1;
            target.useMipMap = false;
            target.autoGenerateMips = false;
            target.filterMode = FilterMode.Point;
            if (!target.Create() || target.sRGB || target.graphicsFormat != GraphicsFormat.R32G32B32A32_SFloat)
                throw new Unavailable("exact_linear_float_render_target_unavailable");
            var readback = Own(new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true), owned);
            var cameraObject = Own(new GameObject("Synthetic camera"), owned);
            var camera = cameraObject.AddComponent<Camera>();
            camera.enabled = false;
            camera.transform.position = new Vector3(0, 0, -2);
            camera.orthographic = true;
            camera.orthographicSize = 1;
            camera.aspect = (float)Width / Height;
            camera.nearClipPlane = 0.1f;
            camera.farClipPlane = 10;
            camera.clearFlags = CameraClearFlags.Nothing;
            camera.renderingPath = RenderingPath.Forward;
            camera.allowMSAA = false;
            camera.allowHDR = true;
            camera.allowDynamicResolution = false;
            camera.useOcclusionCulling = false;
            camera.targetTexture = target;
            var quad = Own(new GameObject("Synthetic quad"), owned);
            var mesh = Own(new Mesh(), owned);
            mesh.vertices = new[] { new Vector3(-1.5f, -1, 0), new Vector3(1.5f, -1, 0),
                new Vector3(1.5f, 1, 0), new Vector3(-1.5f, 1, 0) };
            mesh.uv = new[] { new Vector2(0, 0), new Vector2(1, 0), new Vector2(1, 1), new Vector2(0, 1) };
            mesh.triangles = new[] { 0, 1, 2, 0, 2, 3 };
            mesh.RecalculateBounds();
            quad.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = quad.AddComponent<MeshRenderer>();
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;

            RunCase("opaque_texture_tint", true, true, true, false, false,
                shader, renderer, camera, target, readback, owned, result);
            RunCase("straight_alpha", true, false, true, false, false,
                shader, renderer, camera, target, readback, owned, result);
            RunCase("missing_texture_binding", false, false, false, false, false,
                shader, renderer, camera, target, readback, owned, result);
            RunCase("missing_tint_binding", false, false, true, true, false,
                shader, renderer, camera, target, readback, owned, result);
            RunCase("disabled_blending", false, false, true, false, true,
                shader, renderer, camera, target, readback, owned, result);
            if (ShaderUtil.ShaderHasError(shader)) throw new InvalidOperationException("shader_error_after_render");
            bool allPassed = result.cases.TrueForAll(item => item.pass);
            result.status = allPassed ? "PASS" : "FAIL";
            result.reason = allPassed ? "five_synthetic_vulkan_readbacks_verified" : "pixel_or_negative_control_mismatch";
            exitCode = allPassed ? 0 : 2;
        }
        catch (Unavailable error) { result.status = "NOT_RUN"; result.reason = error.Message; }
        catch (Exception error) { result.status = "FAIL"; result.reason = error.GetType().Name + ": " + error.Message; }
        finally
        {
            RenderTexture.active = previousTarget;
            GL.sRGBWrite = previousSrgb;
            ShaderUtil.allowAsyncCompilation = previousAsync;
            if (target != null) target.Release();
            for (int i = owned.Count - 1; i >= 0; --i)
                if (owned[i] != null) UnityEngine.Object.DestroyImmediate(owned[i]);
        }
        try
        {
            if (output == null) throw new IOException("outside_project_report_path_required");
            File.WriteAllText(output, JsonUtility.ToJson(result, true) + "\n");
            Debug.Log("RAFT_SYNTHETIC_ALPHA " + JsonUtility.ToJson(result));
        }
        catch (Exception error) { Debug.LogError(error.Message); exitCode = 2; }
        EditorApplication.Exit(exitCode);
    }

    static void CheckEnvironment()
    {
        if (!Application.isBatchMode) throw new Unavailable("dedicated_batchmode_project_required");
        if (Application.unityVersion != "2021.3.45f2") throw new Unavailable("exact_Unity_2021_3_45f2_required");
        if (SystemInfo.graphicsDeviceType != GraphicsDeviceType.Vulkan) throw new Unavailable("real_Vulkan_backend_required");
        if (QualitySettings.activeColorSpace != ColorSpace.Linear) throw new Unavailable("active_linear_color_space_required");
        if (GraphicsSettings.currentRenderPipeline != null) throw new Unavailable("built_in_render_pipeline_required");
        if (!SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat)
            || !SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat)
            || !SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat, FormatUsage.Render)
            || !SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat, FormatUsage.Blend)
            || !SystemInfo.IsFormatSupported(GraphicsFormat.R32G32B32A32_SFloat, FormatUsage.Sample))
            throw new Unavailable("float_texture_and_render_support_required");
    }

    static void RunCase(string name, bool positive, bool opaque, bool bindTexture,
        bool omitTint, bool disableBlend, Shader shader, MeshRenderer renderer,
        Camera camera, RenderTexture target, Texture2D readback,
        List<UnityEngine.Object> owned, Receipt result)
    {
        Color[] texels = Texels(opaque);
        var texture = Own(new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true), owned);
        texture.filterMode = FilterMode.Point;
        texture.wrapMode = TextureWrapMode.Clamp;
        texture.SetPixels(texels);
        texture.Apply(false, false);
        var material = Own(new Material(shader), owned);
        if (bindTexture) material.SetTexture("_MainTex", texture);
        if (!omitTint) material.SetColor("_Tint", Tint);
        material.SetFloat("_SrcBlend", (float)(disableBlend ? BlendMode.One : BlendMode.SrcAlpha));
        material.SetFloat("_DstBlend", (float)(disableBlend ? BlendMode.Zero : BlendMode.OneMinusSrcAlpha));
        renderer.sharedMaterial = material;
        RenderTexture.active = target;
        GL.sRGBWrite = false;
        GL.Clear(false, true, Background); // Exact raw linear values, no camera color conversion.
        camera.Render();
        RenderTexture.active = target;
        readback.ReadPixels(new Rect(0, 0, Width, Height), 0, 0, false);
        Color[] observed = readback.GetPixels();
        if (observed.Length != Width * Height) throw new InvalidOperationException("readback_pixel_count_mismatch");
        result.Unity_render_executed = true;
        result.rendered_case_count++;
        if (positive) result.positive_case_count++;
        var row = new CaseResult { name = name, kind = positive ? "positive" : "negative",
            checked_pixel_count = observed.Length, samples = new Sample[observed.Length] };
        for (int i = 0; i < observed.Length; ++i)
        {
            Color intended = Composite(texels[i] * Tint, false);
            Color source = (bindTexture ? texels[i] : Color.white) * (omitTint ? Color.white : Tint);
            Color expected = Composite(source, disableBlend);
            row.max_error = Mathf.Max(row.max_error, Difference(observed[i], expected));
            row.intended_mismatch = Mathf.Max(row.intended_mismatch, Difference(observed[i], intended));
            row.samples[i] = new Sample { x = i % Width, y = i / Width,
                observed = Channels(observed[i]), expected = Channels(expected), intended = Channels(intended) };
        }
        row.pass = row.max_error <= Tolerance && (positive || row.intended_mismatch >= MinimumMismatch);
        if (!positive && row.pass) result.negative_controls_detected++;
        result.max_error = Mathf.Max(result.max_error, row.max_error);
        result.cases.Add(row);
    }

    static Color[] Texels(bool opaque)
    {
        // All rows identical: vertical origin is irrelevant here. Columns are
        // intentionally asymmetric; a horizontal flip must fail the oracle.
        Color[] columns = { new Color(0, 0, 0, 0), new Color(1, 0.25f, 0, 0.5f),
            new Color(0.25f, 1, 0.5f, 1), new Color(0.75f, 0.125f, 1, 1),
            new Color(0.125f, 0.5f, 0.75f, 0.5f), new Color(0, 0, 0, 0) };
        var pixels = new Color[Width * Height];
        for (int i = 0; i < pixels.Length; ++i)
        {
            pixels[i] = columns[i % Width];
            if (opaque) pixels[i].a = 1;
        }
        return pixels;
    }

    static Color Composite(Color source, bool disableBlend)
    {
        float a = source.a;
        return new Color(disableBlend ? source.r : source.r * a + Background.r * (1 - a),
            disableBlend ? source.g : source.g * a + Background.g * (1 - a),
            disableBlend ? source.b : source.b * a + Background.b * (1 - a),
            a + Background.a * (1 - a));
    }
    static float Difference(Color actual, Color expected)
    {
        float difference = 0;
        for (int channel = 0; channel < 4; ++channel)
        {
            if (Single.IsNaN(actual[channel]) || Single.IsInfinity(actual[channel]))
                throw new InvalidOperationException("nonfinite_pixel_readback");
            difference = Mathf.Max(difference, Mathf.Abs(actual[channel] - expected[channel]));
        }
        return difference;
    }
    static float[] Channels(Color color) { return new[] { color.r, color.g, color.b, color.a }; }
    static T Own<T>(T value, List<UnityEngine.Object> owned) where T : UnityEngine.Object
    { owned.Add(value); return value; }
    static string Hash(string path)
    {
        using (var hash = SHA256.Create())
        using (var stream = File.OpenRead(path))
            return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }
    static string OutsideProjectReport(string root)
    {
        string path = Option("RAFT_SYNTHETIC_ALPHA_REPORT", "-raftSyntheticAlphaReport");
        if (String.IsNullOrWhiteSpace(path) || !Path.IsPathRooted(path))
            throw new Unavailable("absolute_report_path_required");
        path = Path.GetFullPath(path);
        string prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
        StringComparison comparison = Path.DirectorySeparatorChar == '\\' ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        if (path.StartsWith(prefix, comparison) || String.Equals(path, root, comparison))
            throw new Unavailable("report_must_be_outside_project");
        return path;
    }
    static string Option(string environment, string argument)
    {
        string value = Environment.GetEnvironmentVariable(environment);
        if (!String.IsNullOrWhiteSpace(value)) return value;
        string[] args = Environment.GetCommandLineArgs();
        for (int i = 0; i + 1 < args.Length; ++i)
            if (args[i] == argument) return args[i + 1];
        return null;
    }
}
#endif
