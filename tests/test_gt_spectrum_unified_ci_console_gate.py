"""Synthetic regression for finalized unified Spectrum Unity compiler log."""
import unittest

from scripts.gt_spectrum_unified_ci_console_gate import verify, RUNTIME_MARKER


class PrivateUnifiedConsole(unittest.TestCase):
    def good(self):
        return ("2026-11-12T19:21:05.000123Z "+
                RUNTIME_MARKER+
                "sevenPasses=true keywordVariants=2 Unity2021=true parity=false\n").encode()

    def test_accepts_only_real_timestamped_provisional_unity_marker(self):
        r=verify(self.good())
        self.assertEqual(r["status"],"PRIVATE_SPECTRUM_UNIFIED_KEYWORD_FINAL_CONSOLE_CLEAN")
        self.assertFalse(r["original_material_variant_runtime_parity_proven"])
        self.assertFalse(r["original_Adreno_pixels_verified"])

    def test_rejects_hidden_glsl_link_even_when_unity_reports_zero(self):
        r=verify(self.good()+b"GT_SPECTRUM_UNIFIED_KEYWORD_UNITY_SAFE shaderErrorCount=0\n"+
            b"GLSL link error: cb4_struct mismatch\n")
        self.assertEqual(r["status"],"REJECTED")
        self.assertEqual(r["GLSL_link_errors"],1)

    def test_rejects_internal_variant_failure(self):
        r=verify(self.good()+b"Note: Creation of internal variant of shader X failed.\n")
        self.assertEqual(r["status"],"REJECTED")
        self.assertEqual(r["internal_shader_variant_creation_errors"],1)

    def test_ignores_shell_echo_as_actual_unity_proof(self):
        fake=("2026-11-12T19:21:05.000123Z echo '"+RUNTIME_MARKER+"'").encode()
        r=verify(fake)
        self.assertEqual(r["status"],"REJECTED")
        self.assertFalse(r["unified_private_runtime_marker_confirmed"])

    def test_rejects_blank_or_non_text_log(self):
        with self.assertRaisesRegex(ValueError, "not_proven"):
            verify(b"")
        with self.assertRaisesRegex(ValueError, "not_proven"):
            verify(b"line\x00unsafe")


if __name__=="__main__":
    unittest.main()
