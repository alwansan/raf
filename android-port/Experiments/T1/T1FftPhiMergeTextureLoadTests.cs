// T1 WATER-001: public authored Unity 2021 OpenGLCore nested-Phi texture load.
using System;
using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public sealed class T1FftPhiMergeTextureLoadTests
{
    private const int Width = 64, Height = 32, Threads = 64, Sites = 5;

    private static uint Bits(float value)
    {
        return BitConverter.ToUInt32(BitConverter.GetBytes(value), 0);
    }

    [Test]
    public void BranchNestedAndDynamicLoopFloatCarriersMatchDirectTextureCoordinates()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        Assert.That(SystemInfo.graphicsDeviceType, Is.EqualTo(GraphicsDeviceType.OpenGLCore),
            "Sourcefree Phi test requires the original divergent OpenGLCore backend");
        Assert.That(SystemInfo.supportsComputeShaders, Is.True);
        Assert.That(SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat), Is.True);

        const string path = "Assets/T1Synthetic/T1FftPhiMergeTextureLoad.compute";
        AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
        var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(path);
        Assert.That(shader, Is.Not.Null);
        Assert.That(shader.HasKernel("T1PhiFetch"), Is.True);
        int kernel = shader.FindKernel("T1PhiFetch");
        uint tx, ty, tz;
        shader.GetKernelThreadGroupSizes(kernel, out tx, out ty, out tz);
        Assert.That(tx, Is.EqualTo(64u));
        Assert.That(ty, Is.EqualTo(1u));
        Assert.That(tz, Is.EqualTo(1u));

        Texture2D image = null;
        try
        {
            image = new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true)
            {
                wrapMode = TextureWrapMode.Clamp,
                filterMode = FilterMode.Point
            };
            var colors = new Color[Width * Height];
            for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
            {
                float v = 4000f + y * Width + x;
                colors[y * Width + x] = new Color(v, x + 1f, y + 1f, 1f);
            }
            image.SetPixels(colors);
            image.Apply(false, false);

            var coords = new uint[Threads * 4];
            for (int i = 0; i < Threads; i++)
            {
                coords[i * 4] = (uint)((5 * i + 11) & 63);
                coords[i * 4 + 1] = (uint)((3 * i + 7) & 31);
                coords[i * 4 + 2] = (uint)((7 * i + 13) & 63);
                coords[i * 4 + 3] = (uint)((9 * i + 3) & 31);
            }
            var observed = new uint[Threads * Sites];
            using (var coordBuffer = new ComputeBuffer(Threads, sizeof(uint) * 4))
            using (var observationBuffer = new ComputeBuffer(Threads * Sites, sizeof(uint)))
            {
                coordBuffer.SetData(coords);
                observationBuffer.SetData(observed);
                shader.SetTexture(kernel, "T1Butterfly", image);
                shader.SetBuffer(kernel, "T1Coords", coordBuffer);
                shader.SetBuffer(kernel, "T1Observed", observationBuffer);
                shader.Dispatch(kernel, 1, 1, 1);
                observationBuffer.GetData(observed);
            }

            var mismatches = new int[Sites];
            for (int i = 0; i < Threads; i++)
            {
                int xa = (int)coords[i * 4], ya = (int)coords[i * 4 + 1];
                int xb = (int)coords[i * 4 + 2], yb = (int)coords[i * 4 + 3];
                bool odd = (i & 1) != 0;
                bool nestedB = (i & 2) != 0 ? !odd : odd;
                int rounds = (i % 3) + 1;
                bool loopB = ((rounds - 1) & 1) == 0 ? (i & 4) != 0 : (i & 4) == 0;
                uint expectedA = Bits(4000f + ya * Width + xa);
                uint expectedB = Bits(4000f + yb * Width + xb);
                var expected = new[] {
                    expectedA,
                    expectedB,
                    odd ? expectedB : expectedA,
                    nestedB ? expectedB : expectedA,
                    loopB ? expectedB : expectedA
                };
                for (int site = 0; site < Sites; ++site)
                    if (observed[i * Sites + site] != expected[site])
                        mismatches[site]++;
            }

            // Only public synthetic aggregate counts. The GPU buffer and
            // per-invocation coordinates are never uploaded or logged.
            var metrics = Path.Combine(Directory.GetParent(Application.dataPath).FullName,
                                       "t1-phi-merge-counts.txt");
            File.WriteAllLines(metrics, Array.ConvertAll(mismatches, x => x.ToString()));
            Assert.That(mismatches[0], Is.Zero, "Direct first butterfly sampled read");
            Assert.That(mismatches[1], Is.Zero, "Direct second butterfly sampled read");
            Assert.That(mismatches[2], Is.Zero, "Single branch float32 Phi merge");
            Assert.That(mismatches[3], Is.Zero, "Nested branch float32 Phi merge");
            Assert.That(mismatches[4], Is.Zero, "Dynamic loop-carried float32 Phi merge");
        }
        finally
        {
            if (image != null)
                UnityEngine.Object.DestroyImmediate(image);
        }
    }
}
