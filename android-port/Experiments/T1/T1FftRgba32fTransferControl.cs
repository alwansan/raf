// Synthetic GPU transfer control for the T1 FFT parity fixture.
using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

public sealed class T1FftRgba32fTransferControl
{
    private const int Width = 1024;
    private const int Height = 32;

    private static Color Source(int x, int y) =>
        new Color(x + 1, -y - 1, 2 * x + y, -x - y);
    private static Color Butterfly(int x, int y) =>
        new Color(y + 2, -x - 2, x + 3 * y, 2 * x - y);

    private static void Upload(Texture2D texture, bool butterfly)
    {
        using (var stream = new MemoryStream(Width * Height * 16))
        using (var writer = new BinaryWriter(stream))
        {
            for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
            {
                var c = butterfly ? Butterfly(x, y) : Source(x, y);
                writer.Write(c.r);
                writer.Write(c.g);
                writer.Write(c.b);
                writer.Write(c.a);
            }
            texture.LoadRawTextureData(stream.ToArray());
            texture.Apply(false, false);
        }
    }

    private static RenderTexture Target() =>
        new RenderTexture(Width, Height, 0, RenderTextureFormat.ARGBFloat, RenderTextureReadWrite.Linear)
        {
            enableRandomWrite = true,
            filterMode = FilterMode.Point,
            wrapMode = TextureWrapMode.Clamp
        };

    private static void Dispatch(ComputeShader shader, Texture source, Texture butterfly, RenderTexture output)
    {
        int kernel = shader.FindKernel("T1Canary");
        shader.SetTexture(kernel, "Source", source);
        shader.SetTexture(kernel, "Butterfly", butterfly);
        shader.SetTexture(kernel, "Output", output);
        shader.Dispatch(kernel, Width / 64, Height, 1);
    }

    private static void Verify(RenderTexture target, Texture2D readback, int additions)
    {
        RenderTexture.active = target;
        readback.ReadPixels(new Rect(0, 0, Width, Height), 0, 0, false);
        readback.Apply(false, false);
        var pixels = readback.GetPixels();
        int mismatches = 0;
        for (int y = 0; y < Height; y++)
        for (int x = 0; x < Width; x++)
        {
            var expected = Source(x, y) + Butterfly(x, y) * additions;
            if (!pixels[y * Width + x].Equals(expected))
                mismatches++;
        }
        Assert.That(mismatches, Is.Zero, "RGBA32F transfer mismatches after pass " + additions);
    }

    [Test]
    public void FloatTextureAndIntermediateUavPreserveCoordinatesAndChannels()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        Assert.That(SystemInfo.supportsComputeShaders, Is.True);
        Assert.That(SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat), Is.True);
        Assert.That(SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat), Is.True);
        var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/T1Synthetic/FFTCanary.compute");
        Assert.That(shader, Is.Not.Null);

        var previous = RenderTexture.active;
        var source = new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true);
        var butterfly = new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true);
        var readback = new Texture2D(Width, Height, TextureFormat.RGBAFloat, false, true);
        var intermediate = Target();
        var output = Target();
        try
        {
            Upload(source, false);
            Upload(butterfly, true);
            Assert.That(intermediate.Create(), Is.True);
            Assert.That(output.Create(), Is.True);
            Dispatch(shader, source, butterfly, intermediate);
            Verify(intermediate, readback, 1);
            RenderTexture.active = previous;
            Dispatch(shader, intermediate, butterfly, output);
            Verify(output, readback, 2);
        }
        finally
        {
            RenderTexture.active = previous;
            foreach (var target in new[] { intermediate, output })
            {
                target.Release();
                Object.DestroyImmediate(target);
            }
            foreach (var texture in new[] { source, butterfly, readback })
                Object.DestroyImmediate(texture);
        }
    }
}
