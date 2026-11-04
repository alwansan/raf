"""No-private-code regression tests for original compute argument correlation."""
import hashlib
import unittest

from scripts.probe_original_fft_kernel_callsites import (
    analyze_source, parse_original_args, sanitized_argument, constant_offset_from_base,
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

    def test_sha_pinned_original_two_pass_kernel_expression_offsets(self):
        src = ("class F {\n"
               "  void Fft(int originalIndex) {\n"
               "    fft.SetTexture(originalIndex, \"A\", src);\n"
               "    fft.Dispatch(originalIndex, 1, 4, 1);\n"
               "    fft.SetTexture(originalIndex + 1, \"B\", dest);\n"
               "    fft.Dispatch(originalIndex + 1, 1, 4, 1);\n"
               "  }\n"
               "}\n")
        expected = hashlib.sha256(src.encode()).hexdigest()
        report = analyze_source(src, expected)
        self.assertEqual(report["verified_affine_kernel_index_offsets"], [0, 1])
        self.assertEqual([x["kernel_index_affine_offset_from_first_dispatch"]
                          for x in report["compute_api_callsites"]], [0, 0, 1, 1])
        self.assertTrue(report["no_numeric_runtime_base_kernel_index_inferred"])
        self.assertIsNone(constant_offset_from_base("1 / originalIndex", "originalIndex"))

    def test_fail_closed_on_wrong_source_and_unbalanced_call(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            analyze_source("x.Dispatch(2, 3)", "0"*64)
        with self.assertRaisesRegex(ValueError, "Unterminated"):
            parse_original_args('foo(1, nested(3, 4)', 3)

    def test_fake_calls_in_comments_and_literals_do_not_count(self):
        src = ('class F {\n'
               ' // hidden.Dispatch(900, 1, 1, 1);\n'
               ' /* hidden.SetTexture(9, "X", y); */\n'
               ' string s = "hidden.FindKernel(\\"Bad\\")";\n'
               ' string verbatim = @"hidden.Dispatch(9, 9, 9, 9)";\n'
               ' void Go() { fft.Dispatch(3, 1, 1, 1); }\n'
               '}\n')
        report = analyze_source(src, hashlib.sha256(src.encode()).hexdigest())
        self.assertEqual(report["calls_by_api"], {"Dispatch": 1})
        self.assertEqual(report["compute_api_callsites"][0]["kernel_or_first_arg"]["value"], 3)

    def test_unterminated_block_comment_fails_closed(self):
        src = "fft.Dispatch(2, 1, 1, 1); /* never closed"
        with self.assertRaisesRegex(ValueError, "Unterminated"):
            analyze_source(src, hashlib.sha256(src.encode()).hexdigest())

    def test_original_argument_values_are_not_source_code(self):
        self.assertEqual(sanitized_argument("2048")["value"], 2048)
        self.assertEqual(sanitized_argument("ComputeFFT")["kind"], "identifier_or_member")
        self.assertNotIn("ComputeFFT", str(sanitized_argument("ComputeFFT")))
        self.assertEqual(sanitized_argument('"secret"')["kind"], "literal_string")


if __name__ == "__main__":
    unittest.main()
