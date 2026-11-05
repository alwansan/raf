// T1 private Unity 2021 GPU Dispatch smoke for original-DXBC-derived FFT
// compiled slots 0/1. Names in JSON are generated HLSL property handles,
// NOT original author's CSharp SetTexture strings or runtime kernel IDs.
// No source/texture values or private names are logged to public Actions.
using System;
using System.IO;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

[Serializable]
internal sealed class T1GpuResourceRow
{
    public int compiled_slot;
    public string candidate_sha256;
    public int expected_group_x;
    public string source_property;
    public string butterfly_property;
    public string output_property;
}

[Serializable]
internal sealed class T1GpuResourceManifest
{
    public int schema_version;
    public string original_fft_object_sha256;
    public int[] selected_compiled_slots;
    public T1GpuResourceRow[] resources;
    public bool original_authored_resource_names_proven;
    public bool original_runtime_kernel_mapping_proven;
    public bool unity_gpu_dispatch_executed;
    public bool android_device_proven;
}

public sealed class T1PrivateFftGpuDispatchTests
{
    private const int Width = 1024, Height = 1;
    private const float Sentinel = 8192f;
    private const string ObjectSha = "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247";

    private static string FileSha(string path)
    {
        using (var stream = File.OpenRead(path))
        using (var sha = SHA256.Create())
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }

    private static bool Finite(Color c)
    {
        return !(float.IsNaN(c.r) || float.IsNaN(c.g) || float.IsNaN(c.b) || float.IsNaN(c.a) ||
                 float.IsInfinity(c.r) || float.IsInfinity(c.g) ||
                 float.IsInfinity(c.b) || float.IsInfinity(c.a));
    }

    private static Texture2D SeedTexture(int offset)
    {
        var tex = new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true);
        tex.filterMode = FilterMode.Point;
        tex.wrapMode = TextureWrapMode.Clamp;
        var pixels = new Color[Width * Height];
        for (int x = 0; x < Width; x++)
        {
            float phase = (x * 17 + offset * 19 + 7) % 1021 * 0.017f;
            pixels[x] = new Color(
                Mathf.Sin(phase) * .3f + Mathf.Cos(phase * .27f) * .15f,
                Mathf.Sin(phase + .22f) * .2f,
                Mathf.Cos(phase + .33f) * .15f, 1f);
        }
        tex.SetPixels(pixels);
        tex.Apply(false, false);
        return tex;
    }

    private static RenderTexture Target()
    {
        var rt = new RenderTexture(Width, Height, 0, RenderTextureFormat.ARGBFloat)
        {
            enableRandomWrite = true,
            filterMode = FilterMode.Point,
            wrapMode = TextureWrapMode.Clamp
        };
        Assert.That(rt.Create(), Is.True, "Original-derived FFT requires an actual float UAV");
        Assert.That(rt.IsCreated(), Is.True);
        return rt;
    }

    private static Color[] Read(RenderTexture rt)
    {
        var previous = RenderTexture.active;
        var data = new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true);
        try
        {
            RenderTexture.active = rt;
            data.ReadPixels(new Rect(0, 0, Width, Height), 0, 0, false);
            data.Apply(false, false);
            return data.GetPixels();
        }
        finally
        {
            RenderTexture.active = previous;
            UnityEngine.Object.DestroyImmediate(data);
        }
    }

    private static void ClearSentinel(RenderTexture target)
    {
        var prior = RenderTexture.active;
        try
        {
            RenderTexture.active = target;
            GL.Clear(true, true, new Color(Sentinel, Sentinel, Sentinel, Sentinel));
        }
        finally { RenderTexture.active = prior; }
        var colors = Read(target);
        Assert.That(colors.Length, Is.EqualTo(Width));
        // Clear/readback must be proven so an uninitialized output texture
        // cannot be mistaken for authentic shader writes.
        foreach (var c in colors)
        {
            Assert.That(Finite(c), Is.True, "Baseline GPU buffer not finite");
            Assert.That(Mathf.Abs(c.r - Sentinel), Is.LessThan(0.5f),
                "RenderTexture sentinel not initialized");
        }
    }

    private static int Dispatch(T1GpuResourceRow role, Texture input, Texture butterfly, RenderTexture output)
    {
        string root = Directory.GetParent(Application.dataPath).FullName;
        string asset = "Assets/T1OriginalDerived/FFT_Candidate_" + role.compiled_slot.ToString("00") + ".compute";
        string source = Path.Combine(root, asset);
        Assert.That(FileSha(source), Is.EqualTo(role.candidate_sha256),
            "Selected original-derived shader SHA mutated");
        AssetDatabase.ImportAsset(asset, ImportAssetOptions.ForceSynchronousImport);
        var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(asset);
        Assert.That(shader, Is.Not.Null, "Private original-derived ComputeShader not imported");
        Assert.That(shader.HasKernel("main"), Is.True);
        int kernel = shader.FindKernel("main");
        uint x, y, z;
        shader.GetKernelThreadGroupSizes(kernel, out x, out y, out z);
        Assert.That(x, Is.EqualTo((uint)role.expected_group_x));
        Assert.That(y, Is.EqualTo(1u));
        Assert.That(z, Is.EqualTo(1u));
        shader.SetTexture(kernel, role.source_property, input);
        shader.SetTexture(kernel, role.butterfly_property, butterfly);
        shader.SetTexture(kernel, role.output_property, output);
        shader.Dispatch(kernel, 1, Height, 1);
        var actual = Read(output);
        int changed = 0;
        foreach (var c in actual)
        {
            Assert.That(Finite(c), Is.True, "Original-derived FFT GPU produced NaN or Inf");
            if (Mathf.Abs(c.r - Sentinel) > 0.5f)
                changed++;
        }
        Assert.That(changed, Is.GreaterThan(0),
            "GPU Dispatch produced no observed writes to the intended UAV");
        Assert.That(changed, Is.LessThanOrEqualTo(Width));
        return changed;
    }

    [Test]
    public void AuthenticatedFirstPairActuallyDispatchesWithSampledImages()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        Assert.That(SystemInfo.supportsComputeShaders, Is.True,
            "No supported hardware GPU for genuine Unity Dispatch");
        Assert.That(SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat),
            Is.True, "Original FFT float GPU UAV format unsupported");
        string path = Path.Combine(Application.dataPath,
            "T1OriginalDerived/PrivateGpuResources.json");
        Assert.That(File.Exists(path), Is.True, "Private resource properties not staged");
        var manifest = JsonUtility.FromJson<T1GpuResourceManifest>(File.ReadAllText(path));
        Assert.That(manifest, Is.Not.Null);
        Assert.That(manifest.schema_version, Is.EqualTo(1));
        Assert.That(manifest.original_fft_object_sha256, Is.EqualTo(ObjectSha));
        Assert.That(manifest.resources, Is.Not.Null);
        Assert.That(manifest.resources.Length, Is.EqualTo(2));
        Assert.That(manifest.selected_compiled_slots, Is.EqualTo(new[] {0, 1}));
        Assert.That(manifest.original_authored_resource_names_proven, Is.False);
        Assert.That(manifest.original_runtime_kernel_mapping_proven, Is.False);
        Assert.That(manifest.unity_gpu_dispatch_executed, Is.False);
        Assert.That(manifest.android_device_proven, Is.False);
        for (int n = 0; n < 2; n++)
        {
            var row = manifest.resources[n];
            Assert.That(row, Is.Not.Null);
            Assert.That(row.compiled_slot, Is.EqualTo(n));
            Assert.That(row.expected_group_x, Is.EqualTo(64));
            Assert.That(row.candidate_sha256, Has.Length.EqualTo(64));
            Assert.That(row.source_property, Is.Not.Null.And.Not.Empty);
            Assert.That(row.butterfly_property, Is.Not.Null.And.Not.Empty);
            Assert.That(row.output_property, Is.Not.Null.And.Not.Empty);
            Assert.That(row.source_property, Is.Not.EqualTo(row.butterfly_property));
            Assert.That(row.output_property, Is.Not.EqualTo(row.source_property));
        }

        Texture2D source = null, butterfly = null;
        RenderTexture intermediate = null, final = null;
        try
        {
            source = SeedTexture(0);
            butterfly = SeedTexture(1);
            intermediate = Target();
            final = Target();
            ClearSentinel(intermediate);
            ClearSentinel(final);
            int pass0 = Dispatch(manifest.resources[0], source, butterfly, intermediate);
            int pass1 = Dispatch(manifest.resources[1], intermediate, butterfly, final);
            Assert.That(pass0, Is.GreaterThan(0));
            Assert.That(pass1, Is.GreaterThan(0));
            Debug.Log("RAFT_T1_PRIVATE_FFT_GPU_DISPATCH " +
                "authentic_derived_first_pass=true authentic_derived_second_pass=true " +
                "output_changed_both_passes=true original_in_game_kernel_mapping=false " +
                "adreno_device=false numeric_original_parity=false");
        }
        finally
        {
            if (source != null) UnityEngine.Object.DestroyImmediate(source);
            if (butterfly != null) UnityEngine.Object.DestroyImmediate(butterfly);
            if (intermediate != null) { intermediate.Release(); UnityEngine.Object.DestroyImmediate(intermediate); }
            if (final != null) { final.Release(); UnityEngine.Object.DestroyImmediate(final); }
        }
    }
}
