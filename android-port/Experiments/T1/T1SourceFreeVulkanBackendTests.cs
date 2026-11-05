// T1 source-free Unity Vulkan backend and numeric GPU Dispatch control.
// Authored synthetic shader only: zero original Raft assets, shaders or names.
// This is a backend/driver control, not original FFT numerical parity.
using System;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public sealed class T1SourceFreeVulkanBackendTests
{
    private const int Pixels = 64;

    private static Color[] SourceValues()
    {
        var values = new Color[Pixels];
        for (int i = 0; i < Pixels; i++)
            values[i] = new Color(i / 16f, i / 32f, i / 64f, 0.5f);
        return values;
    }

    private static Color[] ButterflyValues()
    {
        var values = new Color[Pixels];
        for (int i = 0; i < Pixels; i++)
            values[i] = new Color((Pixels - 1 - i) / 32f,
                                  (i % 7) / 8f, 0.125f, 0.25f);
        return values;
    }

    private static Texture2D CreateTexture(Color[] colors)
    {
        var texture = new Texture2D(Pixels, 1, TextureFormat.RGBAFloat, false, true);
        texture.filterMode = FilterMode.Point;
        texture.wrapMode = TextureWrapMode.Clamp;
        texture.SetPixels(colors);
        texture.Apply(false, false);
        return texture;
    }

    [Test]
    public void ActuallyUsesVulkanAndRunsSyntheticCompute()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        Assert.That(SystemInfo.graphicsDeviceType, Is.EqualTo(GraphicsDeviceType.Vulkan),
            "Do not mistake OpenGLCore fallback for Vulkan execution");
        Assert.That(SystemInfo.supportsComputeShaders, Is.True,
            "Requested Vulkan graphics device does not support compute");
        Assert.That(SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat),
            Is.True, "Vulkan RGBA32F storage output is unsupported");

        const string assetPath = "Assets/T1Synthetic/FFTCanary.compute";
        AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
        var compute = AssetDatabase.LoadAssetAtPath<ComputeShader>(assetPath);
        Assert.That(compute, Is.Not.Null);
        Assert.That(compute.HasKernel("T1Canary"), Is.True);
        int kernel = compute.FindKernel("T1Canary");
        uint gx, gy, gz;
        compute.GetKernelThreadGroupSizes(kernel, out gx, out gy, out gz);
        Assert.That(gx, Is.EqualTo((uint)Pixels));
        Assert.That(gy, Is.EqualTo(1u));
        Assert.That(gz, Is.EqualTo(1u));

        Texture2D source = null, butterfly = null, readback = null;
        RenderTexture target = null;
        var previous = RenderTexture.active;
        try
        {
            Color[] src = SourceValues();
            Color[] fly = ButterflyValues();
            source = CreateTexture(src);
            butterfly = CreateTexture(fly);
            target = new RenderTexture(Pixels, 1, 0, RenderTextureFormat.ARGBFloat)
            {
                enableRandomWrite = true,
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp
            };
            Assert.That(target.Create(), Is.True, "Vulkan storage RenderTexture not created");

            RenderTexture.active = target;
            GL.Clear(true, true, new Color(8192f, 8192f, 8192f, 8192f));
            RenderTexture.active = previous;

            compute.SetTexture(kernel, "Source", source);
            compute.SetTexture(kernel, "Butterfly", butterfly);
            compute.SetTexture(kernel, "Output", target);
            compute.Dispatch(kernel, 1, 1, 1);

            readback = new Texture2D(Pixels, 1, TextureFormat.RGBAFloat, false, true);
            RenderTexture.active = target;
            readback.ReadPixels(new Rect(0, 0, Pixels, 1), 0, 0, false);
            readback.Apply(false, false);
            Color[] result = readback.GetPixels();
            Assert.That(result.Length, Is.EqualTo(Pixels));
            for (int i = 0; i < Pixels; i++)
            {
                Color expected = src[i] + fly[i];
                Color got = result[i];
                Assert.That(float.IsNaN(got.r) || float.IsNaN(got.g)
                            || float.IsNaN(got.b) || float.IsNaN(got.a), Is.False);
                Assert.That(Mathf.Abs(got.r - expected.r), Is.LessThan(1e-5f));
                Assert.That(Mathf.Abs(got.g - expected.g), Is.LessThan(1e-5f));
                Assert.That(Mathf.Abs(got.b - expected.b), Is.LessThan(1e-5f));
                Assert.That(Mathf.Abs(got.a - expected.a), Is.LessThan(1e-5f));
            }
            Debug.Log("RAFT_T1_SOURCEFREE_VULKAN exact_backend=true dispatched=true " +
                      "numerically_matched_synthetic_texels=64 original_fft=false " +
                      "android_device=false");
        }
        finally
        {
            RenderTexture.active = previous;
            if (source != null) UnityEngine.Object.DestroyImmediate(source);
            if (butterfly != null) UnityEngine.Object.DestroyImmediate(butterfly);
            if (readback != null) UnityEngine.Object.DestroyImmediate(readback);
            if (target != null) { target.Release(); UnityEngine.Object.DestroyImmediate(target); }
        }
    }
}
