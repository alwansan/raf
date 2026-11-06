"""Source-free bounded regression contract for the T1 private Unity FFT NUnit gate."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

GATE_PATH = Path(__file__).with_name("t1_fft_unity_gpu_result_gate.py")
spec = importlib.util.spec_from_file_location("t1_fft_unity_gpu_result_gate", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def sample():
    root = ET.Element("test-run", {
        "total": "2", "testcasecount": "2", "passed": "2",
        "failed": "0", "skipped": "0", "inconclusive": "0", "result": "Passed",
    })
    suite = ET.SubElement(root, "test-suite", {"result": "Passed"})
    for name in sorted(gate.KNOWN):
        ET.SubElement(suite, "test-case", {"fullname": name, "result": "Passed"})
    return root


def check(root, exit_code=0):
    return gate.classify(ET.tostring(root, encoding="utf-8"), exit_code)


class FftGateContractTests(unittest.TestCase):
    def test_valid_two_real_case_names_accepted_only_with_successful_process(self):
        self.assertTrue(check(sample())["all_private_unity_tests_passed"])
        self.assertFalse(check(sample(), 1)["all_private_unity_tests_passed"])

    def test_nested_suite_failure_rejected_despite_successful_root_counters(self):
        root = sample()
        ET.SubElement(root.find("test-suite"), "test-suite", {"result": "Failed"})
        self.assertFalse(check(root)["all_private_unity_tests_passed"])

    def test_nested_reason_rejected_despite_successful_root_counters(self):
        root = sample()
        ET.SubElement(root.find(".//test-case"), "reason")
        self.assertFalse(check(root)["all_private_unity_tests_passed"])

    def test_nested_failure_rejected_despite_successful_root_counters(self):
        root = sample()
        ET.SubElement(root.find("test-suite"), "failure")
        self.assertFalse(check(root)["all_private_unity_tests_passed"])

    def test_duplicate_known_case_does_not_count_as_both_tests(self):
        root = sample()
        cases = root.findall(".//test-case")
        cases[1].set("fullname", cases[0].get("fullname"))
        self.assertFalse(check(root)["all_private_unity_tests_passed"])

    def test_positive_is_not_original_kernel_or_phone_proof(self):
        result = check(sample())
        for field in ("original_author_kernel_names_or_runtime_mapping_proven",
                      "android_adreno_water_pixels_proven",
                      "numeric_original_pixel_parity_proven",
                      "private_original_names_shader_logs_or_pixel_values_exported"):
            self.assertFalse(result[field], field)

    def test_malformed_or_oversized_xml_fails_closed(self):
        with self.assertRaises(ValueError):
            gate.classify(b"<test-run", 0)
        with self.assertRaises(ValueError):
            gate.classify(b"X" * (gate.MAX_XML + 1), 0)


if __name__ == "__main__":
    unittest.main()
