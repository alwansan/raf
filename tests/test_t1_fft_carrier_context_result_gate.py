"""Adversarial regression controls for the T1 sourcefree Unity carrier gate."""

import io
import tempfile
from pathlib import Path
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

from scripts.t1_fft_carrier_context_result_gate import (
    CASE, MAX_METRICS, MAX_XML, analyze, main, parse_metrics, read_bounded,
    require_unity_pass,
)


def xml(*, name=CASE, result="Passed", case="Passed", total=1,
        passed=1, failed=0, skipped=0, inconclusive=0, suite="Passed",
        extra=""):
    return (
        f'<test-run result="{result}" total="{total}" testcasecount="{total}" '
        f'passed="{passed}" failed="{failed}" skipped="{skipped}" '
        f'inconclusive="{inconclusive}">'
        f'<test-suite result="{suite}">'
        f'<test-case fullname="{name}" result="{case}">{extra}</test-case>'
        '</test-suite></test-run>'
    ).encode("utf-8")


def payload(*values):
    return ("\n".join(map(str, values)) + "\n").encode("ascii")


ZERO = payload(*([0] * 10))


class CarrierContextGateTests(unittest.TestCase):
    def test_exact_ten_zero_report_accepted(self):
        self.assertEqual(parse_metrics(ZERO), (0,) * 10)
        result = analyze(xml(), 0, ZERO)
        self.assertTrue(result["positive_controls_passed"])
        self.assertEqual(result["classification"], "no_synthetic_context_difference")
        self.assertFalse(result["diagnostic_mismatch_found"])
        self.assertFalse(result["android_adreno_water_proven"])
        self.assertFalse(result["original_fft_runtime_mapping_proven"])

    def test_nonzero_materialization_is_valid_diagnostic(self):
        a = [0] * 10
        a[1] = a[2] = a[9] = 64
        result = analyze(xml(), 0, payload(*a))
        self.assertTrue(result["sourcefree_unity_nunit_exact_case_passed"])
        self.assertEqual(result["classification"], "float_materialization_difference")

    def test_nonzero_texture_fetch_is_valid_diagnostic(self):
        a = [0] * 10
        a[5] = a[6] = a[7] = a[8] = 63
        result = analyze(xml(), 0, payload(*a))
        self.assertEqual(result["classification"], "texture_fetch_context_difference")

    def test_mixed_signals_are_classified_without_causal_proof(self):
        a = [0] * 10
        a[1] = 62
        a[7] = 14
        row = analyze(xml(), 0, payload(*a))
        self.assertEqual(row["classification"], "mixed_context_differences")
        self.assertFalse(row["original_raft_shader_compiled_or_compared"])

    def test_positive_control_mismatches_fail_closed(self):
        for index in (0, 3, 4):
            counts = [0] * 10
            counts[index] = 1
            with self.subTest(index=index), self.assertRaises(ValueError):
                analyze(xml(), 0, payload(*counts))

    def test_bounds_include_64_and_reject_65(self):
        a = [0] * 10
        a[1] = 64
        self.assertEqual(parse_metrics(payload(*a))[1], 64)
        a[1] = 65
        with self.assertRaises(ValueError):
            parse_metrics(payload(*a))

    def test_metric_count_truncation_extras_noncanonical_rejected(self):
        samples = (b"", b"0\n", payload(*([0] * 9)), payload(*([0] * 11)),
                   b"00\n" * 10, b" 0\n" * 10, b"+0\n" * 10,
                   b"-0\n" * 10, b"0\r\n" * 10, b"0\n" * 9 + b"0\n\n",
                   b"\xef\xbb\xbf" + ZERO, b"\xff" + ZERO,
                   b"0\n" * 10 + b"secret", b"9" * (MAX_METRICS + 1))
        for blob in samples:
            with self.subTest(blob=blob[:8]), self.assertRaises(ValueError):
                parse_metrics(blob)

    def test_optional_last_newline_is_accepted(self):
        self.assertEqual(parse_metrics(ZERO.rstrip(b"\n")), (0,) * 10)

    def test_xml_wrong_identity_or_duplicate_cases_fails_closed(self):
        for name in ("Different.Test", "T1FftCarrierContextTests.Forged"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                require_unity_pass(xml(name=name), 0)
        duplicate = xml().replace(b"</test-suite>",
                                  b'<test-case fullname="' + CASE.encode() +
                                  b'" result="Passed"/></test-suite>')
        with self.assertRaises(ValueError):
            require_unity_pass(duplicate, 0)

    def test_xml_failed_skipped_or_nonzero_process_fails(self):
        pairs = ((xml(result="Failed"), 0), (xml(case="Failed"), 0),
                 (xml(failed=1, passed=0), 0), (xml(skipped=1), 0),
                 (xml(inconclusive=1), 0), (xml(suite="Failed"), 0),
                 (xml(), 1), (xml(), True))
        for blob, code in pairs:
            with self.subTest(code=code, blob=blob[:20]), self.assertRaises(ValueError):
                require_unity_pass(blob, code)

    def test_failure_nodes_and_private_messages_never_accepted(self):
        for marker in ('<failure><message>PRIVATE SHADER SECRET</message></failure>',
                       '<reason><message>PRIVATE SHADER SECRET</message></reason>'):
            with self.subTest(marker=marker[:8]), self.assertRaises(ValueError):
                require_unity_pass(xml(extra=marker), 0)
        result = str(analyze(xml(), 0, ZERO))
        self.assertNotIn("PRIVATE SHADER SECRET", result)
        self.assertNotIn(CASE, result)

    def test_xml_wrong_root_missing_counts_and_unsafe_declarations(self):
        cases = (b"", b"bad", b"<other/>", b"<test-run/>",
                 xml(total=2, passed=2),
                 b'<!DOCTYPE foo [<!ENTITY leak "x">]>' + xml(),
                 b"x" * (MAX_XML + 1))
        for blob in cases:
            with self.subTest(blob=blob[:24]), self.assertRaises(ValueError):
                require_unity_pass(blob, 0)

    def test_read_bounded_rejects_symlinks_and_oversized_file(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            good = root / "counts.txt"
            good.write_bytes(ZERO)
            self.assertEqual(read_bounded(good, MAX_METRICS), ZERO)
            link = root / "linked.txt"
            link.symlink_to(good)
            with self.assertRaises(ValueError):
                read_bounded(link, MAX_METRICS)
            good.write_bytes(b"x" * (MAX_METRICS + 1))
            with self.assertRaises(ValueError):
                read_bounded(good, MAX_METRICS)

    def test_cli_public_marker_is_bounded_and_does_not_print_xml(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            x = root / "nunit.xml"
            m = root / "metrics.txt"
            x.write_bytes(xml())
            m.write_bytes(ZERO)
            import sys
            with patch.object(sys, "argv", ["gate", "--xml", str(x),
                                            "--metrics", str(m), "--exit-code", "0"]):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    self.assertEqual(main(), 0)
            report = stdout.getvalue()
            self.assertIn("RAFT_T1_CARRIER_CONTEXT_GATE", report)
            self.assertNotIn(CASE, report)
            self.assertNotIn("<test-run", report)


if __name__ == "__main__":
    unittest.main()
