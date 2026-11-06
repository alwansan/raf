// T1 WATER-001: source-free Unity 2021 EditMode GPU variant proof.
// This fixture has no Raft shader binaries, source code, private keywords or assets.
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

public sealed class T1FftKeywordVariantRuntimeTests
{
    private const string ComputeAsset = "Assets/T1Synthetic/T1FftKeywordVariantRuntime.compute";
    private const string Keyword = "T1_VARIANT_ON";
    private const int WordCount = 64;

    private static ComputeShader Loaded()
    {
        AssetDatabase.ImportAsset(ComputeAsset, ImportAssetOptions.ForceSynchronousImport);
        var shader = AssetDatabase.LoadAssetAtPath<ComputeShader>(ComputeAsset);
        Assert.That(shader, Is.Not.Null, "Synthetic compute did not import");
        Assert.That(shader.HasKernel("T1VariantMain"), Is.True);
        return shader;
    }

    [Test]
    public void UndeclaredComputeKeywordCannotBeEnabled()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        var shader = Loaded();
        const string undeclared = "T1_UNDECLARED_KW";
        shader.DisableKeyword(undeclared);
        shader.EnableKeyword(undeclared);
        Assert.That(shader.IsKeywordEnabled(undeclared), Is.False,
            "An undeclared compute keyword must not appear enabled");
        shader.DisableKeyword(undeclared);
        Debug.Log("RAFT_T1_KEYWORD_RUNTIME undeclared_rejected=true original_source=false");
    }

    [Test]
    public void DeclaredComputeVariantsProduceDistinctGpuWords()
    {
        Assert.That(Application.unityVersion, Is.EqualTo("2021.3.45f2"));
        Assert.That(SystemInfo.supportsComputeShaders, Is.True,
            "Unity Editor backend lacks compute; no GPU variant proof");
        var shader = Loaded();
        int kernel = shader.FindKernel("T1VariantMain");
        uint x, y, z;
        shader.GetKernelThreadGroupSizes(kernel, out x, out y, out z);
        Assert.That(x, Is.EqualTo(64u));
        Assert.That(y, Is.EqualTo(1u));
        Assert.That(z, Is.EqualTo(1u));
        using (var output = new ComputeBuffer(WordCount, sizeof(uint)))
        {
            shader.SetBuffer(kernel, "T1Output", output);
            var observed = new uint[WordCount];
            try
            {
                shader.DisableKeyword(Keyword);
                Assert.That(shader.IsKeywordEnabled(Keyword), Is.False);
                shader.Dispatch(kernel, 1, 1, 1);
                output.GetData(observed);
                for (int i = 0; i < WordCount; i++)
                    Assert.That(observed[i], Is.EqualTo((uint)(i + 7)),
                        "Default compute keyword variant GPU output mismatch");

                shader.EnableKeyword(Keyword);
                Assert.That(shader.IsKeywordEnabled(Keyword), Is.True,
                    "Declared keyword did not activate in imported shader");
                shader.Dispatch(kernel, 1, 1, 1);
                output.GetData(observed);
                for (int i = 0; i < WordCount; i++)
                    Assert.That(observed[i], Is.EqualTo((uint)(i + 29)),
                        "Enabled compute keyword variant GPU output mismatch");

                shader.DisableKeyword(Keyword);
                Assert.That(shader.IsKeywordEnabled(Keyword), Is.False);
                shader.Dispatch(kernel, 1, 1, 1);
                output.GetData(observed);
                for (int i = 0; i < WordCount; i++)
                    Assert.That(observed[i], Is.EqualTo((uint)(i + 7)),
                        "Disabled keyword must restore default compiled variant");
                Debug.Log("RAFT_T1_KEYWORD_RUNTIME gpu_variants=2 verified_words=192 " +
                    "synthetic=true original_author_kernel=false android_water=false");
            }
            finally
            {
                shader.DisableKeyword(Keyword);
            }
        }
    }
}
