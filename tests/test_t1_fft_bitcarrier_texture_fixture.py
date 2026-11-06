"""Source-only guards for T1 public OpenGLCore FFT bitcarrier Texture2D control."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMPUTE = ROOT / "android-port/Experiments/T1/T1FftBitcarrierTextureLoad.compute"
CS = ROOT / "android-port/Experiments/T1/T1FftBitcarrierTextureLoadTests.cs"


class BitcarrierFixtureTests(unittest.TestCase):
    def test_texture_load_sites_have_direct_and_float_bitcarrier_paths(self):
        shader = COMPUTE.read_text(encoding="utf-8")
        self.assertEqual(shader.count("#pragma kernel T1Fetch"), 1)
        self.assertEqual(shader.count("[numthreads(64,1,1)]"), 1)
        self.assertEqual(shader.count("T1Captured[baseIndex"), 5)
        self.assertEqual(shader.count("T1Butterfly.Load"), 4)
        self.assertEqual(shader.count("T1Source.Load"), 1)
        self.assertIn("return asfloat(coords)", shader)
        self.assertIn("return asint(carrier.xy)", shader)
        self.assertIn("carrier.zwxy", shader)
        self.assertNotIn("WavesRendererFFT", shader)
        self.assertNotIn("Dx11FFT", shader)

    def test_genuine_gpu_control_checks_320_u32_exact_image_reads(self):
        code = CS.read_text(encoding="utf-8")
        self.assertEqual(code.count("[Test]"), 1)
        self.assertIn("SourceAndButterflyBitcarriedFetchesMatchExactIntegerAddresses", code)
        self.assertIn("GraphicsDeviceType.OpenGLCore", code)
        self.assertIn("shader.Dispatch(kernel, 1, 1, 1)", code)
        self.assertIn("output.GetData(observed)", code)
        self.assertIn("FloatBits(4000f", code)
        self.assertIn('t1-bitcarrier-texture-mismatches.txt', code)
        self.assertIn("mismatch[4]", code)
        self.assertIn("new ComputeBuffer(Invocations * CapturesPerInvocation, sizeof(uint))", code)

    def test_no_proprietary_payload_or_forged_device_claim(self):
        source = COMPUTE.read_text(encoding="utf-8") + CS.read_text(encoding="utf-8")
        for token in ("original_unity_mapping_proven=true", "android_water_proven=true",
                      "WorldHasBeenRecieved", "steam_api64.dll", "RAFT_FILE_MANIFEST"):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
