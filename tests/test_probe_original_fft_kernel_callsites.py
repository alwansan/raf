"""No-private-code regression tests for original compute argument correlation."""
import hashlib
import unittest

from scripts.probe_original_fft_kernel_callsites import (
    analyze_source, parse_original_args, sanitized_argument,
)


class KernelCallsiteTests(unittest.TestCase):
    def test_splits_nested_calls_and_does_not_report_original_strings(self):
        src = ('class Example {\n'
               'void Test() {\n'
               '  cpu.Dispatch(6, div(10, 2), 1, 1);\n'
               '  cpu.SetTexture(2, "_SecretTex", new Texture2D(1, 1));\n'
               '}}\n')
        expected = hashlib.sha256(src.encode()).hexdigest()
        report = analyze_source(src, expected)
        self.assertEqual(report["calls_by_api"], {"Dispatch": 1, "SetTexture": 1})
        d, st = report["compute_api_callsites"]
        self.assertEqual(d["kernel_or_first_arg"]["value"], 6)
        self.assertEqual(st["kernel_or_first_arg"]["value"], 2)
        self.assertEqual(st["argument_count"], 3)
        self.assertNotIn("_SecretTex", str(report))
        self.assertFalse(report["runtime_kernel_index_to_serialized_program_proven"])

    def test_fail_closed_on_wrong_source_and_unbalanced_call(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            analyze_source("x.Dispatch(2, 3)", "0"*64)
        with self.assertRaisesRegex(ValueError, "Unterminated"):
            parse_original_args('foo(1, nested(3, 4)', 3)

    def test_original_argument_values_are_not_source_code(self):
        self.assertEqual(sanitized_argument("2048")["value"], 2048)
        self.assertEqual(sanitized_argument("ComputeFFT")["kind"], "identifier_or_member")
        self.assertNotIn("ComputeFFT", str(sanitized_argument("ComputeFFT")))
        self.assertEqual(sanitized_argument('"secret"')["kind"], "literal_string")


if __name__ == "__main__":
    unittest.main()
