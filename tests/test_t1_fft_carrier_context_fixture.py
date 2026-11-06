"""Source-only controls for exact sourcefree OpenGLCore float carrier context."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMPUTE = ROOT / "android-port/Experiments/T1/T1FftCarrierContext.compute"
EDITOR = ROOT / "android-port/Experiments/T1/T1FftCarrierContextTests.cs"


class CarrierContextFixtureTests(unittest.TestCase):
    def test_ten_categories_from_same_gpu_dispatch_are_sourcefree(self):
        data = COMPUTE.read_text(encoding="utf-8")
        self.assertEqual(data.count("#pragma kernel T1CarrierContext"), 1)
        self.assertEqual(data.count("[numthreads(64,1,1)]"), 1)
        self.assertEqual(data.count("T1Observed[baseIndex +"), 10)
        self.assertEqual(data.count("T1Image.Load"), 5)
        for s in ("static float T1ThreadCarrier", "asfloat(x)",
                  "asuint(xCarrier)", "ApplyScale(xCarrier)",
                  "asint(ApplyScale(yCarrier))", "DecodeThreadCarrier()"):
            self.assertIn(s, data)
        self.assertNotIn("Dx11FFT", data)
        self.assertNotIn("WavesRendererFFT", data)

    def test_exact_openglcore_nunit_uses_real_gpu_and_keeps_suspect_counts(self):
        data = EDITOR.read_text(encoding="utf-8")
        self.assertEqual(data.count("[Test]"), 1)
        self.assertIn("SameDispatchDistinguishesRawBitCarrierFromTextureFetchContexts", data)
        self.assertIn("GraphicsDeviceType.OpenGLCore", data)
        self.assertIn("shader.Dispatch(kernel, 1, 1, 1)", data)
        self.assertIn("o.GetData(observed)", data)
        self.assertIn("new ComputeBuffer(Threads * Categories, sizeof(uint))", data)
        self.assertIn("t1-carrier-context-mismatch-counts.txt", data)
        for x in (0, 3, 4):
            self.assertIn(f"Assert.That(mismatch[{x}], Is.Zero", data)
        for x in (1, 2, 5, 6, 7, 8, 9):
            self.assertNotIn(f"Assert.That(mismatch[{x}], Is.Zero", data)

    def test_no_original_shader_or_device_success_claim(self):
        data = COMPUTE.read_text(encoding="utf-8") + EDITOR.read_text(encoding="utf-8")
        for token in ("android_water_proven=true", "original_fft_kernel_mapping_proven=true",
                      "WorldHasBeenRecieved", "steam_api64.dll"):
            self.assertNotIn(token, data)


if __name__ == "__main__":
    unittest.main()
