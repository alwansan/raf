// T1 WATER-001 — isolated private candidate import observation for Unity 2021.
// Every asset is reconstructed from SHA-verified original compiled DXBC, NOT
// original authored source. Never copy this probe or generated shaders into Raft.
using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;

[Serializable]
internal sealed class T1DerivedRow
{
    public int compiled_slot;
    public string compute_asset;
    public string candidate_sha256;
    public string original_dxbc_sha256;
    public int expected_group_x;
    public bool runtime_kernel_identity_proven;
}

[Serializable]
internal sealed class T1DerivedManifest
{
    public int schema_version;
    public string provenance;
    public string original_fft_object_sha256;
    public int candidate_count;
    public T1DerivedRow[] rows;
    public bool original_runtime_kernel_mapping_proven;
    public bool unity_import_proven;
    public bool android_gpu_proven;
}

public static class T1PrivateOriginalDerivedImport
{
    private const int ExpectedSlots = 20;
    private const string Provenance = "DXBC_VKD3D_SPIRVCROSS_ROUNDTRIP_NOT_AUTHORED";
    private const string ObjectSha = "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247";

    private static string ShaFile(string path)
    {
        using (var stream = File.OpenRead(path))
        using (var sha = SHA256.Create())
        {
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
    }

    private static string Json(bool unityRan, bool supported, int imported,
                               int resolved, int groups, int errors)
    {
        // No shader names, source, compiler messages, runtime kernel identity
        // inference or unpublished blob SHA are included in stdout.
        return "{\"editor_invoked\":" + (unityRan ? "true" : "false") +
               ",\"editor_supports_compute\":" + (supported ? "true" : "false") +
               ",\"candidate_assets_imported\":" + imported +
               ",\"candidate_main_kernels_resolved\":" + resolved +
               ",\"expected_threadgroups_matched\":" + groups +
               ",\"observed_errors\":" + errors +
               ",\"original_authored_compute_restored\":false" +
               ",\"original_runtime_kernel_mapping_proven\":false" +
               ",\"android_gpu_or_pixels_verified\":false}";
    }

    // Called only via the isolated T1 private GitHub Actions Unity container.
    public static void Run()
    {
        int imported = 0, resolved = 0, groups = 0, errors = 0;
        bool compute = SystemInfo.supportsComputeShaders;
        var project = Directory.GetParent(Application.dataPath).FullName;
        var resultPath = Path.Combine(project, "t1-private-import-result.json");
        try
        {
            if (Application.unityVersion != "2021.3.45f2")
                throw new InvalidOperationException("Unity version differs from original target");
            var manifestPath = Path.Combine(Application.dataPath,
                "T1OriginalDerived", "PrivateCandidates.json");
            var data = JsonUtility.FromJson<T1DerivedManifest>(File.ReadAllText(manifestPath));
            if (data == null || data.schema_version != 1 ||
                data.provenance != Provenance || data.original_fft_object_sha256 != ObjectSha ||
                data.candidate_count != ExpectedSlots || data.rows == null ||
                data.rows.Length != ExpectedSlots || data.original_runtime_kernel_mapping_proven ||
                data.unity_import_proven || data.android_gpu_proven)
                throw new InvalidOperationException("Candidate provenance fails closed");
            for (int slot = 0; slot < ExpectedSlots; ++slot)
            {
                var row = data.rows[slot];
                string relative = "Assets/T1OriginalDerived/FFT_Candidate_" + slot.ToString("00") + ".compute";
                int required = (1 << ((slot % 10) / 2 + 6));
                if (row == null || row.compiled_slot != slot || row.compute_asset != relative ||
                    row.expected_group_x != required || row.runtime_kernel_identity_proven ||
                    String.IsNullOrEmpty(row.candidate_sha256) || row.candidate_sha256.Length != 64)
                    throw new InvalidOperationException("Compiled candidate slot/source mapping invalid");
                var local = Path.Combine(project, relative.Replace('/', Path.DirectorySeparatorChar));
                if (ShaFile(local) != row.candidate_sha256)
                    throw new InvalidOperationException("Private reconstructed compute SHA mismatch");
                AssetDatabase.ImportAsset(relative, ImportAssetOptions.ForceUpdate |
                    ImportAssetOptions.ForceSynchronousImport);
                var asset = AssetDatabase.LoadAssetAtPath<ComputeShader>(relative);
                if (asset == null)
                {
                    errors++;
                    continue;
                }
                imported++;
                // Count, but never emit Unity shader compiler diagnostics. A
                // warning is conservatively treated as an unresolved import.
                int messages = ShaderUtil.GetComputeShaderMessageCount(asset);
                if (messages > 0)
                {
                    errors++;
                    continue;
                }
                if (!compute)
                    continue; // Headless Editor may import without GPU execution.
                try
                {
                    if (!asset.HasKernel("main"))
                    {
                        errors++;
                        continue;
                    }
                    int kernel = asset.FindKernel("main");
                    resolved++;
                    uint x, y, z;
                    asset.GetKernelThreadGroupSizes(kernel, out x, out y, out z);
                    if (x == (uint)required && y == 1 && z == 1) groups++;
                    else errors++;
                }
                catch (Exception)
                {
                    // Never emit Unity compiler messages that may include private identifiers.
                    errors++;
                }
            }
        }
        catch (Exception)
        {
            errors++;
        }
        File.WriteAllText(resultPath, Json(true, compute, imported, resolved, groups, errors), Encoding.UTF8);
        // Failing import/unsupported compute must NOT be promoted to a green
        // runtime-kernel proof, but can still preserve the classified result.
        bool positive = compute && imported == ExpectedSlots && resolved == ExpectedSlots &&
                        groups == ExpectedSlots && errors == 0;
        EditorApplication.Exit(positive ? 0 : 3);
    }
}
