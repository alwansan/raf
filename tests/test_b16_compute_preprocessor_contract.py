"""B16: source-only negative/positive controls for conditional FFT kernel scanning."""
from pathlib import Path
import tempfile
import unittest
from scripts.b47_compute_kernel_contract import kernel_entrypoint_profile
from scripts.verify_water_render_contract import inspect

def function(name="Good"):
    return f"[numthreads(8,8,1)] void {name}(uint3 id:SV_DispatchThreadID) {{}}\n"

class B16ConditionalComputeTests(unittest.TestCase):
    def test_disabled_pragma_and_body(self):
        p = kernel_entrypoint_profile("#if 0\n#pragma kernel Fake\n" + function("Fake") + "#endif\n")
        self.assertEqual(p["kernel_count"], 0)
        self.assertFalse(p["all_kernel_entrypoints_structural"])

    def test_active_pragma_with_disabled_body(self):
        p = kernel_entrypoint_profile("#pragma kernel Good\n#if 0\n" + function() + "#endif\n")
        self.assertEqual(p["kernels_with_structural_entrypoints"], 0)

    def test_literal_if_one(self):
        self.assertTrue(kernel_entrypoint_profile("#if 1\n#pragma kernel Good\n" + function() + "#endif\n")["all_kernel_entrypoints_structural"])

    def test_else_enabled_when_if_zero(self):
        s = "#if 0\n#pragma kernel Fake\n" + function("Fake") + "#else\n#pragma kernel Good\n" + function() + "#endif\n"
        p = kernel_entrypoint_profile(s)
        self.assertEqual(p["kernel_count"], 1)
        self.assertTrue(p["all_kernel_entrypoints_structural"])

    def test_else_disabled_when_if_one(self):
        s = "#if 1\n#pragma kernel Good\n" + function() + "#else\n#pragma kernel Good\n" + function() + "#endif\n"
        self.assertTrue(kernel_entrypoint_profile(s)["all_kernel_entrypoints_structural"])

    def test_elif_and_nested_branches(self):
        for s in (
            "#if 0\n#pragma kernel Fake\n#elif 1\n#pragma kernel Good\n#endif\n" + function(),
            "#if 1\n#if 0\n#pragma kernel Fake\n#else\n#pragma kernel Good\n#endif\n#endif\n" + function(),
        ):
            with self.subTest(source=s[:15]):
                self.assertEqual(kernel_entrypoint_profile(s)["kernel_count"], 1)
                self.assertTrue(kernel_entrypoint_profile(s)["all_kernel_entrypoints_structural"])

    def test_unknown_conditions_fail_closed(self):
        for opening in ("#ifdef UNITY_ANDROID", "#ifndef UNITY_ANDROID", "#if FOO", "#if 1 || 0"):
            with self.subTest(directive=opening):
                s = opening + "\n#pragma kernel Good\n" + function() + "#else\n#pragma kernel Bad\n#endif\n"
                self.assertEqual(kernel_entrypoint_profile(s)["kernel_count"], 0)

    def test_unknown_elif_and_later_else_both_masked(self):
        s = "#if 0\n#pragma kernel Fake\n#elif PLATFORM_FLAG\n#pragma kernel Good\n#else\n#pragma kernel Other\n#endif\n" + function()
        self.assertEqual(kernel_entrypoint_profile(s)["kernel_count"], 0)

    def test_comment_fake_preprocessor_does_not_disable_source(self):
        s = "/* #if 0\n#endif */\n// #if 0\n#pragma kernel Good\n" + function()
        self.assertTrue(kernel_entrypoint_profile(s)["all_kernel_entrypoints_structural"])

    def test_malformed_conditional_is_rejected(self):
        for s in ("#endif\n", "#else\n", "#elif 1\n", "#if 0\n",
                  "#if 0\n#else\n#else\n#endif\n", "#if 0\n#elif\n#endif\n",
                  "#if 0\n#endif stray\n"):
            with self.subTest(source=s):
                with self.assertRaises(ValueError):
                    kernel_entrypoint_profile(s)

    def test_water_contract_ignores_disabled_fake_compute(self):
        with tempfile.TemporaryDirectory() as tmp:
            assets = Path(tmp) / "Assets"
            assets.mkdir()
            (assets / "FFT.compute").write_text("#if 0\n#pragma kernel Fake\n" + function("Fake") + "#endif\n")
            (assets / "FFT.compute.meta").write_text("guid: " + "b"*32)
            report = inspect(Path(tmp))
            self.assertFalse(report["water_compute_source_candidate_present"])
            self.assertEqual(report["compute_files_with_kernels"], 0)
            self.assertFalse(report["authentic_water_kernel_identity_verified"])

    def test_water_contract_retains_active_else_but_not_authenticity(self):
        with tempfile.TemporaryDirectory() as tmp:
            assets = Path(tmp) / "Assets"
            assets.mkdir()
            (assets / "FFT.compute").write_text("#if 0\n#pragma kernel Bad\n#else\n#pragma kernel Good\n" + function() + "#endif\n")
            (assets / "FFT.compute.meta").write_text("guid: " + "b"*32)
            report = inspect(Path(tmp))
            self.assertTrue(report["water_compute_source_candidate_present"])
            self.assertFalse(report["authentic_water_kernel_identity_verified"])
            self.assertFalse(report["device_execution_verified"])

if __name__ == "__main__":
    unittest.main()
