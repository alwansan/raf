"""Source-only guard for T1 synthetic Unity keyword GPU fixture (no Raft)."""
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMPUTE = ROOT / "android-port/Experiments/T1/T1FftKeywordVariantRuntime.compute"
EDITOR = ROOT / "android-port/Experiments/T1/T1FftKeywordVariantRuntimeTests.cs"


class SourcefreeKeywordFixtureTests(unittest.TestCase):
    def test_authored_compute_has_exactly_one_keyword_and_two_numeric_branches(self):
        source = COMPUTE.read_text(encoding="utf-8")
        self.assertEqual(source.count("#pragma kernel T1VariantMain"), 1)
        self.assertEqual(source.count("#pragma multi_compile_local __ T1_VARIANT_ON"), 1)
        self.assertEqual(source.count("RWStructuredBuffer<uint> T1Output;"), 1)
        self.assertEqual(source.count("[numthreads(64,1,1)]"), 1)
        self.assertEqual(source.count("thread.x + 7u"), 1)
        self.assertEqual(source.count("thread.x + 29u"), 1)
        self.assertEqual(source.count("#if defined(T1_VARIANT_ON)"), 1)
        self.assertNotIn("WavesRenderer", source)
        self.assertNotIn("Dx11FFT", source)

    def test_managed_unity_gpu_test_has_two_exact_nunit_cases(self):
        source = EDITOR.read_text(encoding="utf-8")
        self.assertEqual(source.count("[Test]"), 2)
        self.assertIn("public void UndeclaredComputeKeywordCannotBeEnabled()", source)
        self.assertIn("public void DeclaredComputeVariantsProduceDistinctGpuWords()", source)
        self.assertEqual(source.count("shader.Dispatch(kernel, 1, 1, 1)"), 3)
        self.assertEqual(source.count("shader.IsKeywordEnabled(Keyword)"), 3)
        self.assertIn('shader.IsKeywordEnabled(undeclared)', source)
        self.assertIn("output.GetData(observed)", source)
        self.assertIn("SystemInfo.supportsComputeShaders", source)
        self.assertNotIn("original_water_proven=true", source)


if __name__ == "__main__":
    unittest.main()
