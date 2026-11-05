"""Source-free fault-isolation controls for the T1 Vulkan bank1 experiment."""
import unittest
from scripts.t1_fft_bank1_validation import classify_process, MAX_CAPTURE


class Bank1ValidatorControls(unittest.TestCase):
    def test_sigsegv_is_recorded_as_failure(self):
        result = classify_process(-11, b"", b"")
        self.assertEqual(result["outcome"], "segmentation_fault")
        self.assertFalse(result["numeric_report_valid"])
        self.assertIsNone(result["same_source_comparator"])

    def test_timeout_cannot_pass(self):
        result = classify_process(-1, b"", b"", timed_out=True)
        self.assertEqual(result["outcome"], "timeout")
        self.assertFalse(result["numeric_report_valid"])

    def test_api_validation_error_is_counted_without_disclosure(self):
        stderr = b"Validation Error: [ VUID-vkCmdDispatch-TEST-10000 ] private-text\n"
        result = classify_process(1, b"some private text", stderr)
        self.assertEqual(result["validation_error_markers"], 1)
        self.assertEqual(result["vuid_markers"], 1)
        self.assertEqual(result["outcome"], "nonzero")
        self.assertNotIn("private-text", str(result))
        self.assertNotIn("vkCmdDispatch", str(result))

    def test_missing_layer_fails_closed(self):
        result = classify_process(1, b"", b"VK_ERROR_LAYER_NOT_PRESENT")
        self.assertTrue(result["layer_missing"])
        self.assertFalse(result["numeric_report_valid"])

    def test_arbitrary_stdout_cannot_fabricate_numeric_success(self):
        result = classify_process(0, b"no original benchmark report", b"")
        self.assertEqual(result["outcome"], "exit_zero")
        self.assertFalse(result["numeric_report_valid"])
        self.assertIsNone(result["within_selected_tolerance"])

    def test_overlong_or_nonbinary_output_rejected(self):
        with self.assertRaises(ValueError):
            classify_process(0, b"x" * (MAX_CAPTURE + 1), b"")
        with self.assertRaises(ValueError):
            classify_process(0, "private", b"")


if __name__ == "__main__":
    unittest.main()
