"""T1 SHA-authentic Dx11FFT Android hook staging: source-free adversarial controls."""
import unittest
from unittest.mock import patch
from scripts import t1_stage_original_fft_dispatch_trace as hooks
from scripts.probe_original_fft_kernel_callsites import sha

BASE = "public class GpuFFT { protected int originalExponent; }\n"
ORIGINAL = """public class Dx11FFT : GpuFFT {
    void Run()
    {
        shader.SetTexture(k, "A", a);
        shader.SetTexture(k, "B", b);
        shader.SetTexture(k, "C", c);
        shader.Dispatch(k, 1, target.height, 1);
        shader.SetTexture(k + 1, "A", a);
        shader.SetTexture(k + 1, "B", b);
        shader.SetTexture(k + 1, "C", c);
        shader.Dispatch(k + 1, 1, target.height, 1);
    }
}
"""


def run_synthetic(original=ORIGINAL, adapted=None, base=BASE):
    if adapted is None:
        adapted = original
    verified = {"protected_inherited_seed_identifier_sha256": sha("originalExponent")}
    summary = {
        "calls_by_api": {"Dispatch": 2, "SetTexture": 6},
        "compute_api_callsites": [
            {"call_kind": "Dispatch", "kernel_index_affine_offset_from_first_dispatch": 0},
            {"call_kind": "Dispatch", "kernel_index_affine_offset_from_first_dispatch": 1},
        ],
    }
    with patch.object(hooks, "ORIGINAL_SHA", sha(original)), \
         patch.object(hooks, "BASE_SHA256", sha(base)), \
         patch.object(hooks, "prove", return_value=verified), \
         patch.object(hooks, "analyze_source", return_value=summary), \
         patch.object(hooks, "adapt", return_value=original):
        return hooks.rewrite(original, adapted, base)


class OriginalFftAndroidHookTests(unittest.TestCase):
    def test_wraps_two_dispatches_without_replacing_either(self):
        out = run_synthetic()
        self.assertEqual(out.count("BeforeDispatch("), 2)
        self.assertEqual(out.count("AfterDispatch("), 2)
        self.assertIn("shader.Dispatch(k, 1, target.height, 1);", out)
        self.assertIn("shader.Dispatch(k + 1, 1, target.height, 1);", out)
        self.assertEqual(out.count("shader.SetTexture("), 6)

    def test_source_exponent_read_directly_from_inherited_field(self):
        out = run_synthetic()
        self.assertEqual(out.count("this.originalExponent"), 2)
        self.assertIn("this.originalExponent, 0", out)
        self.assertIn("this.originalExponent, 1", out)
        self.assertNotIn("FindKernel", out)

    def test_disabling_android_sections_leaves_original_statements(self):
        out = run_synthetic()
        statements = [line.strip() for line in out.splitlines()
                      if ".Dispatch(" in line and "BeforeDispatch" not in line]
        self.assertEqual(statements, [
            "shader.Dispatch(k, 1, target.height, 1);",
            "shader.Dispatch(k + 1, 1, target.height, 1);",
        ])

    def test_instrumenting_twice_rejected(self):
        modified = run_synthetic()
        with self.assertRaisesRegex(ValueError, "differs|already patched"):
            run_synthetic(adapted=modified)

    def test_extra_original_dispatch_rejected(self):
        extra = ORIGINAL.replace("    }", "        shader.Dispatch(k + 1, 1, target.height, 1);\n    }")
        with self.assertRaisesRegex(ValueError, "two standalone"):
            run_synthetic(original=extra)

    def test_comment_fake_dispatch_does_not_satisfy_original_two_calls(self):
        source = ORIGINAL.replace(
            "shader.Dispatch(k + 1, 1, target.height, 1);",
            "// shader.Dispatch(k + 1, 1, target.height, 1);")
        with self.assertRaisesRegex(ValueError, "two standalone|non-executable"):
            run_synthetic(original=source)

    def test_changed_shader_receiver_rejected(self):
        altered = ORIGINAL.replace(
            "shader.Dispatch(k + 1", "shaderTwo.Dispatch(k + 1")
        with self.assertRaisesRegex(ValueError, "different ComputeShader"):
            run_synthetic(original=altered)

    def test_changed_dispatch_y_expression_rejected(self):
        altered = ORIGINAL.replace("target.height, 1", "GetHeight(), 1")
        with self.assertRaisesRegex(ValueError, "pure texture height"):
            run_synthetic(original=altered)

    def test_side_effect_in_kernel_expression_rejected(self):
        altered = ORIGINAL.replace("shader.Dispatch(k, 1", "shader.Dispatch(k++, 1")
        with self.assertRaisesRegex(ValueError, "side-effect-free"):
            run_synthetic(original=altered)

    def test_swapped_pass_offset_rejected(self):
        altered = ORIGINAL.replace(
            "shader.Dispatch(k + 1, 1", "shader.Dispatch(k + 2, 1")
        with self.assertRaisesRegex(ValueError, "argument relation drift"):
            run_synthetic(original=altered)

    def test_changed_group_x_rejected(self):
        altered = ORIGINAL.replace(
            "shader.Dispatch(k, 1", "shader.Dispatch(k, 2")
        with self.assertRaisesRegex(ValueError, "X/Z"):
            run_synthetic(original=altered)

    def test_mismatch_between_backup_and_current_fails(self):
        with self.assertRaisesRegex(ValueError, "differs"):
            run_synthetic(adapted=ORIGINAL + "// drift\n")

    def test_wrong_base_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA changed"):
            # The synthetic fixture utility computes SHA from BASE; bypass
            # its fixture match to force original digest guard.
            with patch.object(hooks, "ORIGINAL_SHA", sha(ORIGINAL)), \
                 patch.object(hooks, "BASE_SHA256", sha(BASE)):
                hooks.rewrite(ORIGINAL, ORIGINAL, BASE + " changed")

    def test_android_helper_has_bounded_nonintrusive_log_contract(self):
        from pathlib import Path
        source = Path("android-port/Runtime/Platform/T1FftDirectDispatchTrace.cs").read_text()
        for marker in ("#if UNITY_ANDROID && !UNITY_EDITOR", "MaxCalls = 16",
                       "original_runtime_mapping=unverified", "gpu_result=unverified",
                       "managed_dispatch_call_returned=true", "catch (Exception)"):
            self.assertIn(marker, source)
        self.assertNotIn("FindKernel(", source)
        self.assertNotIn("shader.Dispatch(", source)


if __name__ == "__main__":
    unittest.main()
