// Stage only in a fresh authored project. Reimport identical PNG bytes; no game content.
// Run: -batchmode -force-vulkan -executeMethod SyntheticImportedAlphaValidation.Run
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

public static class SyntheticImportedAlphaValidation
{
    const string ShaderPath = "Assets/SyntheticMaterialAlpha.shader";
    const string ProbePath = "Assets/Editor/SyntheticImportedAlphaValidation.cs";
    const string PngPath = "Assets/AuthoredAlpha.png";
    const int Width = 6, Height = 4;
    const float Tolerance = 0.008f;
    static readonly Color Background = new Color(0.125f, 0.25f, 0.5f, 0.25f);
    static readonly Color Tint = new Color(0.5f, 0.75f, 0.25f, 1f);

    [Serializable] sealed class Sample
    {
        public int x, y;
        public float[] observed;
        public int[] imported_rgba8;
    }
    [Serializable] sealed class CaseResult
    {
        public string name, alpha_source, texture_format, graphics_format, asset_guid, bound_texture;
        public string filter_mode, wrap_mode, texture_shape, texture_type, compression, npot_scale, png_sha256;
        public bool srgb_import, srgb_graphics_format, readable, mipmaps_enabled, alpha_is_transparency;
        public int width, height, mip_count, aniso_level, material_id, checked_pixel_count;
        public float[] tint;
        public int src_blend, dst_blend;
        public Sample[] samples;
    }
    [Serializable] sealed class Receipt
    {
        public int schema_version = 1;
        public string run_id, status = "NOT_RUN", reason = "not_started";
        public string Unity_version, backend, active_color_space, graphics_device_name;
        public string shader_sha256, probe_sha256, png_sha256, png_sha256_after;
        public int rendered_case_count, reimport_count;
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
            run_id = Option("RAFT_IMPORTED_ALPHA_RUN_ID", "-raftImportedAlphaRunId"),
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
            result.png_sha256 = Hash(Path.Combine(root, PngPath));
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

            var material = Own(new Material(shader), owned);
            renderer.sharedMaterial = material;
            var input = Reimport(TextureImporterAlphaSource.FromInput, false, result);
            RunCase("input_linear", input, "imported", Tint, false, material, camera, target, readback, result);
            var none = Reimport(TextureImporterAlphaSource.None, false, result);
            RunCase("none_linear", none, "imported", Tint, false, material, camera, target, readback, result);
            var gray = Reimport(TextureImporterAlphaSource.FromGrayScale, false, result);
            RunCase("grayscale_linear", gray, "imported", Tint, false, material, camera, target, readback, result);
            var srgb = Reimport(TextureImporterAlphaSource.FromInput, true, result);
            RunCase("input_srgb", srgb, "imported", Tint, false, material, camera, target, readback, result);
            input = Reimport(TextureImporterAlphaSource.FromInput, false, result);
            RunCase("wrong_blend", input, "imported", Tint, true, material, camera, target, readback, result);
            RunCase("white_binding", input, "explicit_white", Tint, false, material, camera, target, readback, result);
            RunCase("missing_binding", input, "null", Tint, false, material, camera, target, readback, result);
            RunCase("missing_tint", input, "imported", Color.white, false, material, camera, target, readback, result);
            if (ShaderUtil.ShaderHasError(shader)) throw new InvalidOperationException("shader_error_after_render");
            result.png_sha256_after = Hash(Path.Combine(root, PngPath));
            if (result.png_sha256 != result.png_sha256_after) throw new InvalidOperationException("authored_png_changed");
            result.status = "OBSERVED";
            result.reason = "eight_cases_captured_independent_oracle_required";
            exitCode = 0;
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
            Debug.Log("RAFT_IMPORTED_ALPHA " + JsonUtility.ToJson(result));
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

    static Texture2D Reimport(TextureImporterAlphaSource source, bool srgb, Receipt result)
    {
        var importer = AssetImporter.GetAtPath(PngPath) as TextureImporter;
        if (importer == null) throw new InvalidOperationException("authored_png_importer_missing");
        importer.textureType = TextureImporterType.Default;
        importer.textureShape = TextureImporterShape.Texture2D;
        importer.alphaSource = source;
        importer.alphaIsTransparency = false;
        importer.sRGBTexture = srgb;
        importer.isReadable = true;
        importer.mipmapEnabled = false;
        importer.npotScale = TextureImporterNPOTScale.None;
        importer.textureCompression = TextureImporterCompression.Uncompressed;
        importer.crunchedCompression = false;
        importer.maxTextureSize = 32;
        importer.filterMode = FilterMode.Point;
        importer.wrapMode = TextureWrapMode.Clamp;
        importer.anisoLevel = 0;
        importer.SaveAndReimport();
        var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(PngPath);
        if (texture == null || texture.width != Width || texture.height != Height ||
            !texture.isReadable || texture.mipmapCount != 1)
            throw new InvalidOperationException("actual_imported_texture_unavailable");
        result.reimport_count++;
        return texture;
    }

    static void RunCase(string name, Texture2D imported, string binding, Color tint, bool disableBlend,
        Material material, Camera camera, RenderTexture target, Texture2D readback, Receipt result)
    {
        var importer = AssetImporter.GetAtPath(PngPath) as TextureImporter;
        if (importer == null || AssetDatabase.GetAssetPath(imported) != PngPath)
            throw new InvalidOperationException("actual_png_asset_identity_required");
        var rgba = imported.GetPixels32();
        Texture supplied = binding == "null" ? null : binding == "explicit_white" ? Texture2D.whiteTexture : imported;
        material.SetTexture("_MainTex", supplied);
        material.SetColor("_Tint", tint);
        material.SetFloat("_SrcBlend", (float)(disableBlend ? BlendMode.One : BlendMode.SrcAlpha));
        material.SetFloat("_DstBlend", (float)(disableBlend ? BlendMode.Zero : BlendMode.OneMinusSrcAlpha));
        if (material.GetTexture("_MainTex") != supplied)
            throw new InvalidOperationException("actual_material_binding_mismatch");
        RenderTexture.active = target;
        GL.sRGBWrite = false;
        GL.Clear(false, true, Background);
        camera.Render();
        RenderTexture.active = target;
        readback.ReadPixels(new Rect(0, 0, Width, Height), 0, 0, false);
        Color[] observed = readback.GetPixels();
        if (observed.Length != Width * Height || rgba.Length != observed.Length)
            throw new InvalidOperationException("readback_pixel_count_mismatch");
        var row = new CaseResult {
            name = name, alpha_source = importer.alphaSource.ToString(), texture_format = imported.format.ToString(),
            graphics_format = imported.graphicsFormat.ToString(), asset_guid = AssetDatabase.AssetPathToGUID(PngPath),
            bound_texture = binding, filter_mode = imported.filterMode.ToString(), wrap_mode = imported.wrapMode.ToString(),
            texture_shape = importer.textureShape.ToString(), texture_type = importer.textureType.ToString(),
            compression = importer.textureCompression.ToString(), npot_scale = importer.npotScale.ToString(),
            png_sha256 = Hash(Path.Combine(Directory.GetParent(Application.dataPath).FullName, PngPath)),
            srgb_import = importer.sRGBTexture, srgb_graphics_format = GraphicsFormatUtility.IsSRGBFormat(imported.graphicsFormat),
            readable = imported.isReadable, mipmaps_enabled = importer.mipmapEnabled, alpha_is_transparency = importer.alphaIsTransparency,
            width = imported.width, height = imported.height, mip_count = imported.mipmapCount, aniso_level = imported.anisoLevel,
            material_id = material.GetInstanceID(), tint = Channels(material.GetColor("_Tint")),
            src_blend = (int)material.GetFloat("_SrcBlend"), dst_blend = (int)material.GetFloat("_DstBlend"),
            checked_pixel_count = observed.Length, samples = new Sample[observed.Length]
        };
        for (int i = 0; i < observed.Length; ++i)
        {
            for (int c = 0; c < 4; ++c)
                if (Single.IsNaN(observed[i][c]) || Single.IsInfinity(observed[i][c]))
                    throw new InvalidOperationException("nonfinite_pixel_readback");
            row.samples[i] = new Sample { x = i % Width, y = i / Width,
                imported_rgba8 = new[] { (int)rgba[i].r, (int)rgba[i].g, (int)rgba[i].b, (int)rgba[i].a },
                observed = Channels(observed[i]) };
        }
        result.Unity_render_executed = true;
        result.rendered_case_count++;
        result.cases.Add(row);
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
        string path = Option("RAFT_IMPORTED_ALPHA_REPORT", "-raftImportedAlphaReport");
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
