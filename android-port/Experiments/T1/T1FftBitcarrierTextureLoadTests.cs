// T1 synthetic OpenGLCore FFT butterfly-coordinate bitcarrier control.
// Distinct from the real Raft shader; executes Texture2D.Load on GPU.
// No original game asset, resource names or private logs are printed.
using System;
using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public sealed class T1FftBitcarrierTextureLoadTests
{
    private const int Width = 64;
    private const int Height = 32;
    private const int Invocations = 64;
    private const int CapturesPerInvocation = 5;

    private static uint FloatBits(float value)
    {
        return BitConverter.ToUInt32(BitConverter.GetBytes(value), 0);
    }

    private static Texture2D Input(bool butterfly)
    {
        var result = new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true)
        {
            filterMode = FilterMode.Point,
            wrapMode = TextureWrapMode.Clamp
        };
        var pixels = new Color[Width * Height];
        for (int y = 0; y < Height; y++)
        for (int x = 0; x < Width; x++)
        {
            float encoded = (butterfly ? 4000f : 10000f) + y * Width + x;
            pixels[y * Width + x] = new Color(encoded, x + 1f, y + 1f, 1f);
        }
        result.SetPixels(pixels);
        result.Apply(false, false);
        return result;
    }

    private static string ReportPath
    {
        get
        {
            return Path.Combine(Directory.GetParent(Application.dataPath).FullName,
                                "t1-bitcarrier-texture-mismatches.txt");
        }
    }

    [Test]
    public void SourceAndButterflyBitcarriedFetchesMatchExactIntegerAddresses()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        Assert.That(SystemInfo.graphicsDeviceType, Is.EqualTo(GraphicsDeviceType.OpenGLCore),
                    "Synthetic test requires same OpenGLCore Unity backend as prior FFT mismatch");
        Assert.That(SystemInfo.supportsComputeShaders, Is.True);
        Assert.That(SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat), Is.True);

        const string path = "Assets/T1Synthetic/T1FftBitcarrierTextureLoad.compute";
        AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
        var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(path);
        Assert.That(shader, Is.Not.Null, "Synthetic bitcarrier compute shader import");
        Assert.That(shader.HasKernel("T1Fetch"), Is.True);
        int kernel = shader.FindKernel("T1Fetch");
        uint tx, ty, tz;
        shader.GetKernelThreadGroupSizes(kernel, out tx, out ty, out tz);
        Assert.That(tx, Is.EqualTo(64u));
        Assert.That(ty, Is.EqualTo(1u));
        Assert.That(tz, Is.EqualTo(1u));

        Texture2D source = null, butterfly = null;
        ComputeBuffer coordinates = null, output = null;
        try
        {
            source = Input(false);
            butterfly = Input(true);
            var payload = new uint[Invocations * 4];
            for (int i = 0; i < Invocations; ++i)
            {
                payload[i * 4] = (uint)((5 * i + 11) & 63);
                payload[i * 4 + 1] = (uint)((3 * i + 7) & 31);
                payload[i * 4 + 2] = (uint)((7 * i + 13) & 63);
                payload[i * 4 + 3] = (uint)((9 * i + 3) & 31);
            }
            coordinates = new ComputeBuffer(Invocations, sizeof(uint) * 4);
            output = new ComputeBuffer(Invocations * CapturesPerInvocation, sizeof(uint));
            coordinates.SetData(payload);
            var observed = new uint[Invocations * CapturesPerInvocation];
            output.SetData(observed);
            shader.SetTexture(kernel, "T1Source", source);
            shader.SetTexture(kernel, "T1Butterfly", butterfly);
            shader.SetBuffer(kernel, "T1Coords", coordinates);
            shader.SetBuffer(kernel, "T1Captured", output);
            shader.Dispatch(kernel, 1, 1, 1);
            output.GetData(observed);

            var mismatch = new int[CapturesPerInvocation];
            for (int i = 0; i < Invocations; ++i)
            {
                int x1 = (int)payload[i * 4], y1 = (int)payload[i * 4 + 1];
                int x2 = (int)payload[i * 4 + 2], y2 = (int)payload[i * 4 + 3];
                var expected = new[] {
                    FloatBits(10000f + i),
                    FloatBits(4000f + y1 * Width + x1),
                    FloatBits(4000f + y1 * Width + x1),
                    FloatBits(4000f + y2 * Width + x2),
                    FloatBits(4000f + y2 * Width + x2)
                };
                for (int k = 0; k < CapturesPerInvocation; ++k)
                    if (observed[i * CapturesPerInvocation + k] != expected[k])
                        mismatch[k]++;
            }

            // Public CI prints ONLY bounded category counts, never texture data,
            // coordinates per invocation or generated shader compiler diagnostics.
            File.WriteAllLines(ReportPath, new[] {
                mismatch[0].ToString(), mismatch[1].ToString(),
                mismatch[2].ToString(), mismatch[3].ToString(),
                mismatch[4].ToString()
            });
            Assert.That(mismatch[0], Is.Zero, "Source direct fetch changed");
            Assert.That(mismatch[1], Is.Zero, "Butterfly first direct fetch changed");
            Assert.That(mismatch[3], Is.Zero, "Butterfly second direct fetch changed");
            Assert.That(mismatch[2], Is.Zero, "First float-bitcarrier texture lookup changed");
            Assert.That(mismatch[4], Is.Zero, "Swizzled float4 bitcarrier lookup changed");
        }
        finally
        {
            if (source != null) UnityEngine.Object.DestroyImmediate(source);
            if (butterfly != null) UnityEngine.Object.DestroyImmediate(butterfly);
            if (coordinates != null) coordinates.Dispose();
            if (output != null) output.Dispose();
        }
    }
}
