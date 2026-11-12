"""No original code: negative controls for completed Unity job GLSL log acceptance."""
import unittest
from scripts.gt_spectrum_ci_console_gate import verify_console, _SUCCESS_MARKERS


def good():
    return ("Setup\n" + "\n".join(
        "2026-11-12T18:47:59.4994121Z " + marker for marker in _SUCCESS_MARKERS
    ) + "\nDone: completed success\n").encode()


class UnityConsoleCleanRequired(unittest.TestCase):
    def test_two_variant_markers_and_no_link_errors(self):
        r=verify_console(good())
        self.assertEqual(r["status"],"PRIVATE_SPECTRUM_UNITY_FINAL_LOG_CLEAN")
        self.assertEqual(r["Unity_GL_link_errors"],0)
        self.assertTrue(r["unity_variant1_success_marker_seen"])
        self.assertFalse(r["Android_Adreno_pixels_verified"])

    def test_glsl_error_when_editor_says_zero_shader_errors_fails(self):
        hidden=(good()+b"GT_SPECTRUM_SEVENPASS_UNITY_SAFE shaderErrorCount=0\n"+
                b"-------- GLSL link error: error: definitions of uniform block cb4_struct do not match\n")
        r=verify_console(hidden)
        self.assertEqual(r["status"],"PRIVATE_SPECTRUM_UNITY_FINAL_LOG_HAS_HIDDEN_ERRORS")
        self.assertEqual(r["Unity_GL_link_errors"],1)

    def test_internal_variant_creation_failed_not_silent(self):
        r=verify_console(good()+b"Note: Creation of internal variant of shader X failed.\n")
        self.assertEqual(r["Unity_hidden_internal_variant_failures"],1)
        self.assertEqual(r["status"],"PRIVATE_SPECTRUM_UNITY_FINAL_LOG_HAS_HIDDEN_ERRORS")

    def test_shader_import_compiler_errors_are_detected(self):
        r=verify_console(good()+b"Shader error in a: Vertex program unknown sampler\n")
        self.assertEqual(r["Unity_Shader_import_errors"],1)
        self.assertEqual(r["status"],"PRIVATE_SPECTRUM_UNITY_FINAL_LOG_HAS_HIDDEN_ERRORS")

    def test_variant1_marker_missing_is_inconclusive_not_clean(self):
        with self.assertRaisesRegex(ValueError,"marker_missing"):
            verify_console(("2026-11-12T18:47:28.8584174Z " +
                            _SUCCESS_MARKERS[0]).encode())

    def test_echoed_shell_script_print_string_is_not_success(self):
        fake=("\n".join(
            '2026-11-12T18:47:28.100Z print("'+marker+'")'
            for marker in _SUCCESS_MARKERS)).encode()
        with self.assertRaisesRegex(ValueError,"marker_missing"):
            verify_console(fake)

    def test_malformed_binary_or_empty_log_is_rejected(self):
        for candidate in (b"",b"hello\x00world"):
            with self.subTest(sample=candidate),self.assertRaisesRegex(
                    ValueError,"missing_or_invalid"):
                verify_console(candidate)


if __name__=="__main__":
    unittest.main()
