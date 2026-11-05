// T1 / WATER-001: private Unity 2021 Editor probe only, not playable game code.
// This measures *staged authored* ComputeShader kernel lookup and groups;
// serialized original compiled candidate slots are NOT proven runtime indices.
// Never upload the private manifest or authored compute source to public CI.
using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

[Serializable]
public sealed class T1FftCandidateRow
{
    public int compiled_slot;
    public int resolution;
    public int bank;
    public int pass_index;
    public int expected_group_x;
    public string kernel_name;
    public string[] keywords;
}

[Serializable]
public sealed class T1FftPrivateManifest
{
    public int schema_version;
    public string original_fft_object_sha256;
    public string authored_compute_sha256;
    public string candidate_provenance;
    public bool original_unity_kernel_mapping_proven;
    public T1FftCandidateRow[] rows;
}

public static class T1FftKernelRuntimeProbe
{
    // Invoked via Unity -batchmode -executeMethod T1FftKernelRuntimeProbe.Run.
    public static void Run()
    {
        const string computePath = "Assets/T1Private/FFTProbe.compute";
        const string manifestPath = "Assets/T1Private/PrivateProbeManifest.json";
        var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(computePath);
        var json = AssetDatabase.LoadAssetAtPath<TextAsset>(manifestPath);
        if (shader == null || json == null)
            throw new InvalidOperationException("T1 private authored FFT compute asset/manifest missing");
        var manifest = JsonUtility.FromJson<T1FftPrivateManifest>(json.text);
        if (manifest == null || manifest.schema_version != 1 ||
            manifest.rows == null || manifest.rows.Length != 20 ||
            manifest.original_unity_kernel_mapping_proven ||
            manifest.candidate_provenance != "B48_SOURCE_SELECTED_COMPILED_CANDIDATES_ONLY" ||
            manifest.original_fft_object_sha256 != "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247")
            throw new InvalidOperationException("T1 original compiled candidate proof absent or false runtime proof");
        using (var sha = SHA256.Create())
        {
            var digest = BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(Path.Combine(Application.dataPath, "T1Private/FFTProbe.compute"))))
                .Replace("-", "").ToLowerInvariant();
            if (digest != manifest.authored_compute_sha256)
                throw new InvalidOperationException("T1 private authored compute file SHA256 mismatch after staging");
        }
        if (!SystemInfo.supportsComputeShaders)
            throw new InvalidOperationException("T1 Unity probe graphics device lacks compute support");

        var visited = new bool[20];
        int observed = 0;
        int mismatches = 0;
        foreach (var row in manifest.rows)
        {
            if (row == null || row.compiled_slot < 0 || row.compiled_slot >= 20 ||
                visited[row.compiled_slot] || row.bank < 0 || row.bank > 1 ||
                row.pass_index < 0 || row.pass_index > 1 ||
                row.resolution < 32 || row.resolution > 512 ||
                (row.resolution & (row.resolution - 1)) != 0 ||
                row.expected_group_x != row.resolution * 2 ||
                String.IsNullOrEmpty(row.kernel_name))
                throw new InvalidOperationException("T1 compiled candidate row invalid");
            visited[row.compiled_slot] = true;
            int n = 0, v = row.resolution;
            while (v > 1) { n++; v >>= 1; }
            if (row.compiled_slot != ((n - 5) * 2) + row.bank * 10 + row.pass_index)
                throw new InvalidOperationException("T1 original source selector/compiled position mismatch");
            var keywords = row.keywords ?? new string[0];
            try
            {
                foreach (var keyword in keywords)
                    shader.EnableKeyword(keyword);
                if (!shader.HasKernel(row.kernel_name))
                    throw new InvalidOperationException("T1 staged authored runtime kernel name absent");
                int kernelId = shader.FindKernel(row.kernel_name);
                uint x, y, z;
                shader.GetKernelThreadGroupSizes(kernelId, out x, out y, out z);
                bool matched = x == (uint)row.expected_group_x && y == 1U && z == 1U;
                if (!matched) mismatches++;
                observed++;
                // The private kernel names, shader code, keywords and source stay private.
                Debug.Log("RAFT_T1_FFT_UNITY_CANDIDATE compiled_slot=" + row.compiled_slot +
                    " staged_runtime_kernel_id=" + kernelId + " group_xyz=" +
                    x + "," + y + "," + z + " expected_match=" + matched +
                    " original_unity_mapping_proven=false");
            }
            finally
            {
                foreach (var keyword in keywords)
                    shader.DisableKeyword(keyword);
            }
        }
        foreach (bool present in visited)
            if (!present) throw new InvalidOperationException("T1 missing compiled candidate slot");
        if (observed != 20 || mismatches != 0)
            throw new InvalidOperationException("T1 authored Unity FFT group mismatch; not ready");
        Debug.Log("RAFT_T1_FFT_UNITY_PROBE observed=20 group_matches=20 " +
            "original_unity_mapping_proven=false android_device_proven=false");
    }
}
