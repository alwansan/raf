// Sourcefree Unity 2021 OpenGLCore one-dispatch provenance x precision float-address matrix.
// No original Raft bytes, source, privacy-sensitive compiler logs, or phone claims.
using System;
using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public sealed class T1FftAddressProvenanceTests
{
    const int Threads = 64, Categories = 16;

    static uint Bits(float f)
    {
        return BitConverter.ToUInt32(BitConverter.GetBytes(f), 0);
    }

    [Test]
    public void ComputedMaskedAndBufferLoadedFloatAddressContextsShareOneDispatch()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        Assert.That(SystemInfo.graphicsDeviceType, Is.EqualTo(GraphicsDeviceType.OpenGLCore));
        Assert.That(SystemInfo.supportsComputeShaders, Is.True);
        Assert.That(SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat), Is.True);
        const string asset = "Assets/T1Synthetic/T1FftAddressProvenance.compute";
        AssetDatabase.ImportAsset(asset, ImportAssetOptions.ForceSynchronousImport);
        var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(asset);
        Assert.That(shader, Is.Not.Null);
        Assert.That(shader.HasKernel("T1AddressProvenance"), Is.True);
        int kernel = shader.FindKernel("T1AddressProvenance");
        uint tx, ty, tz;
        shader.GetKernelThreadGroupSizes(kernel, out tx, out ty, out tz);
        Assert.That(tx, Is.EqualTo(64u));
        Assert.That(ty, Is.EqualTo(1u));
        Assert.That(tz, Is.EqualTo(1u));
        var image = new Texture2D(Threads, 1, TextureFormat.RGBAFloat, false, true)
        {
            wrapMode = TextureWrapMode.Clamp,
            filterMode = FilterMode.Point
        };
        try
        {
            var pixels = new Color[Threads];
            for (int i = 0; i < Threads; i++)
                pixels[i] = new Color(4096f + i, 0f, 0f, 1f);
            image.SetPixels(pixels);
            image.Apply(false, false);
            var staged = new uint[Threads];
            for (int i = 0; i < Threads; i++)
                staged[i] = (uint)((5 * i + 11) & 63);
            var observed = new uint[Threads * Categories];
            using (var a = new ComputeBuffer(Threads, sizeof(uint)))
            using (var o = new ComputeBuffer(Threads * Categories, sizeof(uint)))
            {
                a.SetData(staged);
                o.SetData(observed);
                shader.SetBuffer(kernel, "T1StagedAddress", a);
                shader.SetBuffer(kernel, "T1Observed", o);
                shader.SetTexture(kernel, "T1AddressImage", image);
                shader.SetInt("T1AddressOffset", 11);
                shader.SetFloat("T1CarrierScale", 1f);
                shader.Dispatch(kernel, 1, 1, 1);
                o.GetData(observed);
            }

            var mismatch = new int[Categories];
            // Complementary bounded signatures: subnormal-bit carrier became
            // signed +/-zero, or a texture read returned precisely pixel x=0.
            // Keep raw observed words PRIVATE; a signature is not FTZ causality.
            var zeroSignature = new int[Categories];
            uint zeroPixel = Bits(4096f);
            for (int i = 0; i < Threads; i++)
            {
                uint address = staged[i];
                uint sampled = Bits(4096f + address);
                uint normal = 0x3f800000u | address;
                uint[] expected =
                {
                    address, address, address, address,
                    address, address, address, address,
                    sampled, sampled, sampled, sampled,
                    sampled, sampled, address, normal
                };
                for (int category = 0; category < Categories; category++)
                {
                    uint actual = observed[i * Categories + category];
                    if (actual == expected[category])
                        continue;
                    mismatch[category]++;
                    // Category 2..7 carries expected subnormal bit patterns.
                    bool scalarCarrier = category >= 2 && category <= 7;
                    // Category 10..13 is a coordinate -> Texture2D.Load path.
                    bool fetchedImage = category >= 10 && category <= 13;
                    if ((scalarCarrier && (actual & 0x7fffffffu) == 0u) ||
                        (fetchedImage && actual == zeroPixel))
                        zeroSignature[category]++;
                }
            }

            string file = Path.Combine(Directory.GetParent(Application.dataPath).FullName,
                                       "t1-address-provenance-counts.txt");
            File.WriteAllLines(file, Array.ConvertAll(mismatch, m => m.ToString()));
            string signatureFile = Path.Combine(
                Directory.GetParent(Application.dataPath).FullName,
                "t1-address-provenance-zero-signatures.txt");
            File.WriteAllLines(signatureFile, Array.ConvertAll(zeroSignature, n => n.ToString()));
            // Fail only if integer/texture upload or normal float controls are broken.
            // Do NOT discard nonzero float/materialization/Texture2D.Load differences.
            Assert.That(mismatch[0], Is.Zero, "Computed integer address baseline");
            Assert.That(mismatch[1], Is.Zero, "Uploaded integer address baseline");
            Assert.That(mismatch[8], Is.Zero, "Direct Texture2D.Load computed address");
            Assert.That(mismatch[9], Is.Zero, "Direct Texture2D.Load staged address");
            Assert.That(mismatch[14], Is.Zero, "Static dispatch global buffer control");
            Assert.That(mismatch[15], Is.Zero, "Normalized precise float control");
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(image);
        }
    }
}
