"""Source-only negative guard for synthetic Unity branch/nested/loop Phi GPU test."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SHADER = ROOT / "android-port/Experiments/T1/T1FftPhiMergeTextureLoad.compute"
TEST = ROOT / "android-port/Experiments/T1/T1FftPhiMergeTextureLoadTests.cs"


class T1PhiTextureFixtureTests(unittest.TestCase):
    def test_public_kernel_contains_all_genuine_phi_sources(self):
        code = SHADER.read_text(encoding="utf-8")
        self.assertEqual(code.count("#pragma kernel T1PhiFetch"), 1)
        self.assertEqual(code.count("[numthreads(64,1,1)]"), 1)
        self.assertEqual(code.count("T1Observed[offset + "), 5)
        self.assertEqual(code.count("T1Butterfly.Load"), 5)
        for token in ("float2 branchMerge;", "float2 nestedMerge;",
                      "float2 loopMerge = a;", "uint rounds = (i % 3u) + 1u;",
                      "[loop]", "asfloat(coord.xy)", "asfloat(coord.zw)",
                      "asint(branchMerge)", "asint(nestedMerge)", "asint(loopMerge)"):
            self.assertIn(token, code)
        self.assertNotIn("Dx11FFT", code)
        self.assertNotIn("WavesRendererFFT", code)

    def test_actual_unity_test_exercises_320_samples_and_exact_backend(self):
        code = TEST.read_text(encoding="utf-8")
        self.assertEqual(code.count("[Test]"), 1)
        self.assertIn("GraphicsDeviceType.OpenGLCore", code)
        self.assertIn("shader.Dispatch(kernel, 1, 1, 1)", code)
        self.assertIn("observationBuffer.GetData(observed)", code)
        self.assertIn("Threads * Sites", code)
        self.assertIn("Sourcefree Phi test requires", code)
        for token in ("nestedB", "loopB", "mismatches[4]", "t1-phi-merge-counts.txt"):
            self.assertIn(token, code)

    def test_public_fixture_never_affirms_android_or_original_source(self):
        combined = SHADER.read_text(encoding="utf-8") + TEST.read_text(encoding="utf-8")
        for token in ("android_water_proven=true", "original_unity_mapping_proven=true",
                      "WorldHasBeenRecieved", "steam_api64.dll"):
            self.assertNotIn(token, combined)


if __name__ == "__main__":
    unittest.main()
