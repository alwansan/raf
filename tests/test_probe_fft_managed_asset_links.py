"""Source-only synthetic FFT managed caller parsing tests."""
import hashlib
import unittest
from scripts.probe_fft_managed_asset_links import analyze_text, SERIALIZED_FFT_NAME_SHA256

class FftManagedLinkTests(unittest.TestCase):
    def test_callsite_hash_redacts_private_symbols(self):
        txt = 'ComputeShader privateFFT; privateFFT.SetTexture(oneKernelIndex,"privateTexture",target); privateFFT.Dispatch(oneKernelIndex,1,2,3);'
        digest = hashlib.sha256(txt.encode()).hexdigest()
        info = analyze_text(txt, digest)
        self.assertEqual(info["declared_compute_shader_identifier_count"], 1)
        self.assertEqual(info["dispatch_callsites"], 1)
        self.assertEqual(info["texture_bind_callsites"], 1)
        self.assertEqual(len(info["dispatch_identifiers_also_used_for_settexture"]), 1)
        self.assertNotIn("privateTexture", str(info))
        self.assertNotIn("oneKernelIndex", str(info))
        self.assertFalse(info["literal_match_proves_unity_asset_reference"])

    def test_source_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            analyze_text("private data", "0" * 64)

    def test_does_not_guess_asset_name_from_fft_word(self):
        txt = 'var str = "FFT"; var other = "UltimateWater";'
        info = analyze_text(txt, hashlib.sha256(txt.encode()).hexdigest())
        self.assertEqual(info["original_literal_matches_serialized_fft_asset_name"], 0)
        self.assertFalse(info["literal_match_proves_unity_asset_reference"])


if __name__ == "__main__":
    unittest.main()
