// Public synthetic sourcefree Unity2021 OpenGLCore GPU transport control.
// No original Raft shader, source, compiler log or texture data leaves runner.
using System;
using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public sealed class T1FftCarrierContextTests
{
    private const int Width = 64, Height = 32, Threads = 64, Categories = 10;

    private static uint Bits(float v)
    {
        return BitConverter.ToUInt32(BitConverter.GetBytes(v), 0);
    }

    [Test]
    public void SameDispatchDistinguishesRawBitCarrierFromTextureFetchContexts()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        Assert.That(SystemInfo.graphicsDeviceType, Is.EqualTo(GraphicsDeviceType.OpenGLCore));
        Assert.That(SystemInfo.supportsComputeShaders, Is.True);
        Assert.That(SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat), Is.True);
        const string path = "Assets/T1Synthetic/T1FftCarrierContext.compute";
        AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
        var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(path);
        Assert.That(shader, Is.Not.Null);
        Assert.That(shader.HasKernel("T1CarrierContext"), Is.True);
        int kernel = shader.FindKernel("T1CarrierContext");
        uint tx, ty, tz;
        shader.GetKernelThreadGroupSizes(kernel, out tx, out ty, out tz);
        Assert.That(tx, Is.EqualTo(64u));
        Assert.That(ty, Is.EqualTo(1u));
        Assert.That(tz, Is.EqualTo(1u));
        var image = new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true)
        {
            filterMode = FilterMode.Point,
            wrapMode = TextureWrapMode.Clamp
        };
        try
        {
            var pixels = new Color[Width * Height];
            for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
                pixels[y * Width + x] = new Color(4000f + y * Width + x, x, y, 1f);
            image.SetPixels(pixels);
            image.Apply(false, false);

            var coords = new uint[Threads * 2];
            for (int i = 0; i < Threads; i++)
            {
                coords[2 * i] = (uint)((i % 63) + 1);
                coords[2 * i + 1] = (uint)(((i * 3) % 31) + 1);
            }
            var observed = new uint[Threads * Categories];
            using (var c = new ComputeBuffer(Threads, sizeof(uint) * 2))
            using (var o = new ComputeBuffer(Threads * Categories, sizeof(uint)))
            {
                c.SetData(coords);
                o.SetData(observed);
                shader.SetTexture(kernel, "T1Image", image);
                shader.SetBuffer(kernel, "T1Coordinates", c);
                shader.SetBuffer(kernel, "T1Observed", o);
                shader.SetFloat("T1Scale", 1.0f);
                shader.Dispatch(kernel, 1, 1, 1);
                o.GetData(observed);
            }

            int[] mismatch = new int[Categories];
            for (int i = 0; i < Threads; i++)
            {
                uint x = coords[2 * i], y = coords[2 * i + 1];
                uint sample = Bits(4000f + y * Width + x);
                uint[] expected = {
                    x, x, x, 0x3f800000u | x,
                    sample, sample, sample, sample, sample, x
                };
                for (int site = 0; site < Categories; site++)
                    if (observed[i * Categories + site] != expected[site])
                        mismatch[site]++;
            }

            // Only bounded aggregate mismatch counts leave Unity's private scratch.
            string name = "t1-carrier-context-mismatch-counts.txt";
            var pathOut = Path.Combine(Directory.GetParent(Application.dataPath).FullName, name);
            File.WriteAllLines(pathOut, Array.ConvertAll(mismatch, value => value.ToString()));
            Assert.That(mismatch[0], Is.Zero, "Direct integer transfer baseline failed");
            Assert.That(mismatch[3], Is.Zero, "Normal float control must be stable");
            Assert.That(mismatch[4], Is.Zero, "Direct Texture2D.Load control failed");
            // Categories 1/2/5/6/7/8/9 are diagnostic: nonzero is a valid,
            // proven backend difference, not a reason to suppress results.
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(image);
        }
    }
}
