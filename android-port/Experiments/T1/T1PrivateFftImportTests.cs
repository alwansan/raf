// T1 / WATER-001. Private Unity2021 EditMode proof of translated ORIGINAL
// compiled FFT candidate import ONLY. No original shader source is embedded.
// No Unity serialized runtime kernel mapping, author HLSL or Adreno proof.
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

[Serializable]
internal sealed class T1PrivateFftCandidate
{
    public int compiled_slot;
    public string compute_asset;
    public string candidate_sha256;
    public string original_dxbc_sha256;
    public int expected_group_x;
    public bool runtime_kernel_identity_proven;
}

[Serializable]
internal sealed class T1PrivateFftManifest
{
    public int schema_version;
    public string provenance;
    public string original_fft_object_sha256;
    public int candidate_count;
    public T1PrivateFftCandidate[] rows;
    public bool original_runtime_kernel_mapping_proven;
    public bool unity_import_proven;
    public bool android_gpu_proven;
}

public sealed class T1PrivateFftImportTests
{
    private const string PrivateManifest = "Assets/T1OriginalDerived/PrivateCandidates.json";
    private const string OriginalObjectSha =
        "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247";
    private const string Provenance = "DXBC_VKD3D_SPIRVCROSS_ROUNDTRIP_NOT_AUTHORED";
    private const int Slots = 20;

    private static string Sha256(string path)
    {
        using (var sha = SHA256.Create())
        using (var input = File.OpenRead(path))
            return BitConverter.ToString(sha.ComputeHash(input))
                .Replace("-", "").ToLowerInvariant();
    }

    [Test]
    public void VerifiedTwentyOriginalDerivedCandidatesImportInUnity()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"),
            "The authentic compiler runner must match the target Unity Editor");
        Assert.That(SystemInfo.supportsComputeShaders, Is.True,
            "Headless Editor cannot certify original-derived kernel imports without compute support");
        string root = Directory.GetParent(Application.dataPath).FullName;
        string manifestFile = Path.Combine(root, PrivateManifest);
        Assert.That(File.Exists(manifestFile), Is.True, "Private manifest absent");
        var decoded = JsonUtility.FromJson<T1PrivateFftManifest>(
            File.ReadAllText(manifestFile));
        Assert.That(decoded, Is.Not.Null, "Private manifest parse rejected");
        Assert.That(decoded.schema_version, Is.EqualTo(1));
        Assert.That(decoded.original_fft_object_sha256, Is.EqualTo(OriginalObjectSha));
        Assert.That(decoded.provenance, Is.EqualTo(Provenance));
        Assert.That(decoded.candidate_count, Is.EqualTo(Slots));
        Assert.That(decoded.rows, Is.Not.Null);
        Assert.That(decoded.rows.Length, Is.EqualTo(Slots));
        Assert.That(decoded.original_runtime_kernel_mapping_proven, Is.False);
        Assert.That(decoded.unity_import_proven, Is.False);
        Assert.That(decoded.android_gpu_proven, Is.False);

        int imported = 0;
        int validKernel = 0;
        int exactGroups = 0;
        for (int n = 0; n < Slots; n++)
        {
            var candidate = decoded.rows[n];
            Assert.That(candidate, Is.Not.Null, "Original compiled candidate absent");
            string asset = "Assets/T1OriginalDerived/FFT_Candidate_" +
                n.ToString("00") + ".compute";
            int expectedX = 1 << (n % 10 / 2 + 6);
            Assert.That(candidate.compiled_slot, Is.EqualTo(n), "Original compiled slot drift");
            Assert.That(candidate.compute_asset, Is.EqualTo(asset), "Private candidate path drift");
            Assert.That(candidate.expected_group_x, Is.EqualTo(expectedX), "Original workgroup drift");
            Assert.That(candidate.runtime_kernel_identity_proven, Is.False);
            Assert.That(candidate.candidate_sha256, Has.Length.EqualTo(64));
            Assert.That(candidate.original_dxbc_sha256, Has.Length.EqualTo(64));
            Assert.That(Sha256(Path.Combine(root, asset)),
                Is.EqualTo(candidate.candidate_sha256), "Private shader source SHA mismatch");
            AssetDatabase.ImportAsset(asset,
                ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
            var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(asset);
            Assert.That(shader, Is.Not.Null, "Translated ComputeShader importer unavailable");
            imported++;
            Assert.That(shader.HasKernel("main"), Is.True,
                "Generated private candidate kernel was not imported");
            int kernelId = shader.FindKernel("main");
            validKernel++;
            uint x, y, z;
            shader.GetKernelThreadGroupSizes(kernelId, out x, out y, out z);
            Assert.That(x, Is.EqualTo((uint)expectedX), "Original workgroup X mismatch");
            Assert.That(y, Is.EqualTo(1U), "Original workgroup Y mismatch");
            Assert.That(z, Is.EqualTo(1U), "Original workgroup Z mismatch");
            exactGroups++;
        }
        Assert.That(imported, Is.EqualTo(Slots));
        Assert.That(validKernel, Is.EqualTo(Slots));
        Assert.That(exactGroups, Is.EqualTo(Slots));
        Debug.Log("RAFT_T1_PRIVATE_ORIGINAL_DERIVED_FFT_COMPUTE " +
            "sha_authentic_original_compiled_candidates=20 imported=20 " +
            "generated_main_kernel_resolved=20 group_xyz_matches=20 " +
            "original_authored_source_restored=false " +
            "original_runtime_kernel_mapping_proven=false " +
            "android_adreno_pixels_verified=false");
    }
}
