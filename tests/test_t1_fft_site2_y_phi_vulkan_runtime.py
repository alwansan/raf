"""Synthetic numeric fixture tests only; no game source or real GPU in unit tests."""
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from scripts import t1_fft_site2_y_phi_vulkan_runtime as run

ZERO = b"\x00" * run.COUNTER_BYTES
PIXEL = struct.Struct("<4f")


def encoded(entries, loops):
    if len(entries) != 64 or len(loops) != 64:
        raise ValueError("Unit fixture must have 64 groups")
    return run.COUNTERS.pack(*(x for pair in zip(entries, loops) for x in pair))


class OriginalSite2YPhiVulkanControls(unittest.TestCase):
    def test_64_invocations_entry_and_loop_histogram(self):
        result = run.counter_profile(ZERO, encoded([1]*64, [3]*64))
        self.assertTrue(result["zeroed_untagged_buffer_verified"])
        self.assertEqual(result["entry_execution_hists"], {"zero": 0, "one": 64, "multiple": 0})
        self.assertEqual(result["loop_backedge_execution_hists"],
                         {"zero": 0, "one": 0, "multiple": 64})
        self.assertEqual(result["threads_with_both_entry_and_loop_edges"], 64)
        self.assertEqual(result["total_loop_backedge_visits"], 192)
        self.assertTrue(result["all_invocations_have_entry_edge"])
        self.assertFalse(result["all_64_invocations_have_exactly_four_backedges"])
        self.assertEqual(result["loop_backedge_visit_buckets"]["three"], 64)
        self.assertFalse(result["actual_shader_choice_at_site2_fetch_proven"])

    def test_exactly_four_loop_edges_requires_per_thread_evidence(self):
        result = run.counter_profile(ZERO, encoded([1]*64, [4]*64))
        self.assertTrue(result["all_64_invocations_have_exactly_four_backedges"])
        self.assertEqual(result["loop_backedge_visit_buckets"]["four"], 64)
        self.assertEqual(result["total_loop_backedge_visits"], 256)
        self.assertFalse(result["actual_shader_choice_at_site2_fetch_proven"])

    def test_untagged_shader_must_leave_private_buffer_zero(self):
        wrong = bytearray(ZERO)
        wrong[12] = 1
        with self.assertRaises(ValueError):
            run.counter_profile(bytes(wrong), encoded([1]*64, [0]*64))

    def test_short_or_oversized_private_counter_rejected(self):
        for invalid in (ZERO[:-4], ZERO + b"\0" * 4, b"", b"\0"*128):
            with self.subTest(length=len(invalid)), self.assertRaises(ValueError):
                run.counter_profile(ZERO, invalid)

    def test_unknown_mutable_counter_objects_rejected(self):
        with self.assertRaises(ValueError):
            run.counter_profile(bytearray(ZERO), encoded([1]*64, [0]*64))

    def test_loop_counter_overflow_rejected(self):
        with self.assertRaises(ValueError):
            run.counter_profile(ZERO, encoded([1]*63+[4097], [0]*64))

    def test_zero_observed_branch_does_not_claim_execution(self):
        result = run.counter_profile(ZERO, ZERO)
        self.assertFalse(result["all_invocations_have_entry_edge"])
        self.assertFalse(result["any_loop_backedge_observed"])
        self.assertEqual(result["threads_with_no_entry_but_loop_edge"], 0)
        self.assertFalse(result["actual_shader_choice_at_site2_fetch_proven"])

    def test_backedge_without_entry_not_hidden(self):
        result = run.counter_profile(ZERO, encoded([0]*64, [2]*63 + [0]))
        self.assertEqual(result["threads_with_no_entry_but_loop_edge"], 63)
        self.assertFalse(result["all_invocations_have_entry_edge"])

    def test_first_two_slot_mapping_is_distinct(self):
        starts = [0]*64
        loops = [0]*64
        starts[0] = 1
        loops[0] = 2
        starts[1] = 3
        report = run.counter_profile(ZERO, encoded(starts, loops))
        self.assertEqual(report["total_entry_edge_visits"], 4)
        self.assertEqual(report["total_loop_backedge_visits"], 2)
        self.assertEqual(report["threads_with_both_entry_and_loop_edges"], 1)
        self.assertEqual(report["threads_with_only_entry_edge"], 1)

    def test_no_private_invocation_or_counter_words_exported(self):
        report = run.counter_profile(ZERO, encoded([1]*64, [2]*64))
        self.assertFalse(report["counter_bytes_or_invocation_keys_exported"])
        self.assertFalse(report["actual_Unity_compiled_shader_execution_proven"])
        self.assertFalse(report["android_Adreno_water_proven"])
        self.assertNotIn("%", json.dumps(report))

    def fixture(self, *, left_value=1.0, right_value=1.0, bad=None):
        stack = tempfile.TemporaryDirectory()
        root = Path(stack.name)
        a = root / "plain"; b = root / "tagged"
        a.mkdir(); b.mkdir()
        for d, v in ((a, left_value), (b, right_value)):
            for item in (*run.INPUTS, *run.OUTPUTS):
                # Source, butterfly and original controls deliberately stable.
                value = 1.0 if item in (*run.INPUTS, *run.OUTPUTS[:2]) else v
                (d / item).write_bytes(PIXEL.pack(value, 2.0, 3.0, 4.0))
        if bad:
            (b / bad).write_bytes(PIXEL.pack(9.0, 2.0, 3.0, 4.0))
        return stack, a, b

    def test_byte_identical_candidate_control_positive(self):
        stack, a, b = self.fixture()
        try:
            with patch.object(run, "BYTES", PIXEL.size):
                result = run.readback_pair(a, b)
            self.assertTrue(result["tagging_did_not_change_candidate_outputs_bitwise"])
            self.assertTrue(result["tagging_did_not_change_candidate_outputs_within_tolerance"])
            self.assertTrue(result["two_physical_runs_with_byte_identical_inputs"])
        finally:
            stack.cleanup()

    def test_distinct_candidate_values_prevent_false_bitwise_parity(self):
        stack, a, b = self.fixture(right_value=3.0)
        try:
            with patch.object(run, "BYTES", PIXEL.size):
                result = run.readback_pair(a, b)
            self.assertFalse(result["tagging_did_not_change_candidate_outputs_bitwise"])
            self.assertFalse(result["tagging_did_not_change_candidate_outputs_within_tolerance"])
        finally:
            stack.cleanup()

    def test_input_mismatch_rejected(self):
        stack, a, b = self.fixture(bad=run.INPUTS[0])
        try:
            with patch.object(run, "BYTES", PIXEL.size), self.assertRaises(ValueError):
                run.readback_pair(a, b)
        finally:
            stack.cleanup()

    def test_original_control_output_mismatch_rejected(self):
        stack, a, b = self.fixture(bad=run.OUTPUTS[0])
        try:
            with patch.object(run, "BYTES", PIXEL.size), self.assertRaises(ValueError):
                run.readback_pair(a, b)
        finally:
            stack.cleanup()

    def test_symlinked_output_rejected_without_data_leak(self):
        stack, a, b = self.fixture()
        try:
            output = b / run.OUTPUTS[3]
            output.unlink()
            output.symlink_to(a / run.OUTPUTS[3])
            with patch.object(run, "BYTES", PIXEL.size), self.assertRaises(ValueError):
                run.readback_pair(a, b)
        finally:
            stack.cleanup()

    def test_aliased_run_dirs_rejected(self):
        stack, a, b = self.fixture()
        try:
            with self.assertRaises(ValueError):
                run.readback_pair(a, a)
        finally:
            stack.cleanup()

    def test_nonfinite_candidate_cannot_pass_tolerance(self):
        stack, a, b = self.fixture(right_value=float("nan"))
        try:
            with patch.object(run, "BYTES", PIXEL.size):
                result = run.readback_pair(a, b)
            self.assertFalse(result["tagging_did_not_change_candidate_outputs_within_tolerance"])
            self.assertEqual(result["candidate_output_parity_by_pass"]["pass0"]["nonfinite_pixels"], 1)
        finally:
            stack.cleanup()

    def test_private_cli_error_cannot_disclose_source(self):
        output = io.StringIO()
        with (patch("sys.argv", ["runner", "--original-data", "/private/secret"]),
              patch.object(run, "inspect", side_effect=ValueError("secret original %shader")),
              redirect_stderr(output)):
            with self.assertRaises(SystemExit) as exited:
                run.main()
        self.assertEqual(exited.exception.code, 2)
        self.assertNotIn("secret", output.getvalue())
        self.assertNotIn("/private", output.getvalue())


if __name__ == "__main__":
    unittest.main()
