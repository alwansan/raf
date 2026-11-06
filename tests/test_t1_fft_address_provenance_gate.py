"""Adversarial sourcefree regression tests for real Unity address-provenance matrix."""
import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.t1_fft_address_provenance_gate import (
    CASE, MAX_METRICS, MAX_XML, analyze, main, parse_metrics, read_bounded,
    require_unity_pass,
)

HERE = Path(__file__).resolve().parents[1]
SHADER = HERE / "android-port/Experiments/T1/T1FftAddressProvenance.compute"
EDITOR = HERE / "android-port/Experiments/T1/T1FftAddressProvenanceTests.cs"


def xml(*, case_name=CASE, run="Passed", case="Passed", suite="Passed",
        total=1, passed=1, failed=0, skipped=0, inconclusive=0, extra=""):
    return (f'<test-run result="{run}" total="{total}" testcasecount="{total}" '
            f'passed="{passed}" failed="{failed}" skipped="{skipped}" '
            f'inconclusive="{inconclusive}"><test-suite result="{suite}">'
            f'<test-case fullname="{case_name}" result="{case}">{extra}</test-case>'
            '</test-suite></test-run>').encode("ascii")


def metric(*values):
    return ("\n".join(str(v) for v in values) + "\n").encode("ascii")


ZERO = metric(*([0] * 16))


class ProvenanceGateTests(unittest.TestCase):
    def test_real_fixture_has_exact_matrix_pairs_and_one_dispatch(self):
        gpu = SHADER.read_text()
        editor = EDITOR.read_text()
        self.assertEqual(gpu.count("#pragma kernel T1AddressProvenance"), 1)
        self.assertEqual(gpu.count("T1Observed[at +"), 16)
        self.assertEqual(gpu.count("[numthreads(64,1,1)]"), 1)
        self.assertIn("((i << 2) + i + T1AddressOffset) & 63u", gpu)
        self.assertIn("T1StagedAddress[i]", gpu)
        self.assertIn("precise float computedPrecise", gpu)
        self.assertIn("precise float stagedPrecise", gpu)
        self.assertIn("T1StagedAddress[T1DispatchId.x]", gpu)
        self.assertEqual(editor.count("[Test]"), 1)
        self.assertIn("ComputedMaskedAndBufferLoadedFloatAddressContextsShareOneDispatch", editor)
        self.assertIn("GraphicsDeviceType.OpenGLCore", editor)
        self.assertIn("shader.Dispatch(kernel, 1, 1, 1)", editor)
        self.assertIn("o.GetData(observed)", editor)
        self.assertIn("t1-address-provenance-counts.txt", editor)
        self.assertIn("t1-address-provenance-zero-signatures.txt", editor)
        self.assertIn("(actual & 0x7fffffffu) == 0u", editor)
        self.assertIn("fetchedImage && actual == zeroPixel", editor)
        for index in (0, 1, 8, 9, 14, 15):
            self.assertIn(f"Assert.That(mismatch[{index}], Is.Zero", editor)
        for index in (2, 3, 4, 5, 6, 7, 10, 11, 12, 13):
            self.assertNotIn(f"Assert.That(mismatch[{index}], Is.Zero", editor)
        self.assertNotIn("Dx11FFT", gpu)
        self.assertNotIn("WavesRendererFFT", gpu)

    def test_clean_sixteen_category_gpu_report(self):
        self.assertEqual(parse_metrics(ZERO), (0,) * 16)
        report = analyze(xml(), 0, ZERO, ZERO)
        self.assertEqual(report["classification"], "no_synthetic_context_difference")
        self.assertFalse(report["diagnostic_mismatch_found"])
        self.assertTrue(report["positive_controls_passed"])
        self.assertEqual(report["synthetic_gpu_words_expected"], 1024)
        self.assertFalse(report["original_fft_runtime_mapping_proven"])
        self.assertFalse(report["float32_FTZ_cause_proven"])

    def test_computed_only_difference_without_failed_baseline(self):
        values = [0] * 16
        for i in (2, 4, 6, 10, 12):
            values[i] = 63
        r = analyze(xml(), 0, metric(*values), ZERO)
        self.assertEqual(r["classification"], "computed_only_context_difference")
        self.assertEqual(r["computed_address_category_mismatches"], [63] * 5)
        self.assertEqual(r["buffered_address_category_mismatches"], [0] * 5)

    def test_buffered_only_difference_without_failed_baseline(self):
        values = [0] * 16
        values[3] = values[7] = values[13] = 64
        r = analyze(xml(), 0, metric(*values), ZERO)
        self.assertEqual(r["classification"], "buffered_only_context_difference")
        self.assertEqual(r["computed_address_category_mismatches"], [0] * 5)
        self.assertEqual(r["buffered_address_category_mismatches"], [64, 0, 64, 0, 64])

    def test_mixed_provenance_differences(self):
        a = [0] * 16
        a[4], a[11] = 17, 1
        r = analyze(xml(), 0, metric(*a), ZERO)
        self.assertEqual(r["classification"], "computed_and_buffered_context_differences")
        self.assertEqual(len(r["pair_names"]), 5)

    def test_all_six_positive_controls_are_mandatory(self):
        for index in (0, 1, 8, 9, 14, 15):
            values = [0] * 16
            values[index] = 1
            with self.subTest(index=index), self.assertRaises(ValueError):
                analyze(xml(), 0, metric(*values), ZERO)

    def test_metric_boundaries_and_noncanonical_rejection(self):
        bad = [
            b"", b"0\n", metric(*([0] * 15)), metric(*([0] * 17)),
            b"00\n" * 16, b"0\r\n" * 16,
            b"-0\n" * 16, b"+0\n" * 16,
            b" 0\n" * 16, b"0 \n" * 16,
            ZERO + b"SECRET", b"\xef\xbb\xbf" + ZERO,
            b"0\n" * 15 + b"65\n",
            b"a" * (MAX_METRICS + 1),
        ]
        for data in bad:
            with self.subTest(data=data[:12]), self.assertRaises(ValueError):
                parse_metrics(data)
        a = [0] * 16
        a[12] = 64
        self.assertEqual(parse_metrics(metric(*a))[12], 64)
        self.assertEqual(parse_metrics(ZERO[:-1]), (0,) * 16)

    def test_nunit_requires_exact_one_real_pass_and_successful_process(self):
        invalid = [
            (xml(run="Failed"), 0), (xml(case="Failed"), 0),
            (xml(suite="Failed"), 0),
            (xml(total=2, passed=2), 0), (xml(failed=1, passed=0), 0),
            (xml(skipped=1), 0), (xml(inconclusive=1), 0),
            (xml(case_name=CASE + "Forged"), 0),
            (xml(), 1), (xml(), True),
            (b"<broken />", 0), (xml() + b"extra", 0),
        ]
        for blob, code in invalid:
            with self.subTest(blob=blob[:30]), self.assertRaises(ValueError):
                require_unity_pass(blob, code)

    def test_private_markup_and_duplicate_cases_rejected(self):
        duplicate = xml().replace(b"</test-suite>", 
            ('<test-case fullname="' + CASE + '" result="Passed"/></test-suite>').encode("ascii"))
        for blob in (
            b'<!DOCTYPE foo [<!ENTITY x "PRIVATE">]>' + xml(),
            duplicate,
            xml(extra="<failure><message>PRIVATE_SHADER_NAME</message></failure>"),
            xml(extra="<reason><message>PRIVATE_SHADER_NAME</message></reason>"),
            b"x" * (MAX_XML + 1),
        ):
            with self.subTest(blob=blob[:20]), self.assertRaises(ValueError):
                require_unity_pass(blob, 0)

    def test_symlink_and_oversized_xml_or_metric_files_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            marker = root / "proof.txt"
            marker.write_bytes(ZERO)
            self.assertEqual(read_bounded(marker, MAX_METRICS), ZERO)
            link = root / "link"
            link.symlink_to(marker)
            with self.assertRaises(ValueError):
                read_bounded(link, MAX_METRICS)
            marker.write_bytes(b"x" * (MAX_METRICS + 1))
            with self.assertRaises(ValueError):
                read_bounded(marker, MAX_METRICS)

    def test_bitcarrier_zero_and_image_x0_signatures_are_distinct(self):
        # On this canary, computed paths are even 2,4,6,10,12;
        # image signatures indicate a pixel sampled from x=0, not zero-pixel data.
        count = [0] * 16
        sign = [0] * 16
        for lane in (2, 4, 6, 10, 12):
            count[lane] = 63
            sign[lane] = 63
        r = analyze(xml(), 0, metric(*count), metric(*sign))
        self.assertEqual(r["computed_zero_signatures"], [63] * 5)
        self.assertEqual(r["buffered_zero_signatures"], [0] * 5)
        self.assertEqual(r["computed_other_mismatches"], [0] * 5)
        self.assertFalse(r["zero_signature_is_float_FTZ_causality"])
        self.assertFalse(r["float32_FTZ_cause_proven"])

    def test_other_mismatch_kept_when_signature_only_partial(self):
        count = [0] * 16
        sign = [0] * 16
        count[2], sign[2] = 63, 42
        count[10], sign[10] = 63, 0
        report = analyze(xml(), 0, metric(*count), metric(*sign))
        self.assertEqual(report["computed_other_mismatches"], [21, 0, 0, 63, 0])
        self.assertEqual(report["computed_zero_signatures"], [42, 0, 0, 0, 0])

    def test_signature_count_must_not_exceed_mismatch_in_any_path(self):
        count = [0] * 16
        signatures = [0] * 16
        signatures[2] = 1
        with self.assertRaises(ValueError):
            analyze(xml(), 0, metric(*count), metric(*signatures))
        count[2] = 2
        signatures[2] = 3
        with self.assertRaises(ValueError):
            analyze(xml(), 0, metric(*count), metric(*signatures))

    def test_signature_on_positive_control_is_invalid(self):
        for category in (0, 1, 8, 9, 14, 15):
            count = [0] * 16
            signatures = [0] * 16
            count[category] = signatures[category] = 1
            with self.subTest(category=category), self.assertRaises(ValueError):
                analyze(xml(), 0, metric(*count), metric(*signatures))

    def test_bad_signature_payload_rejected_independent_of_valid_metrics(self):
        for payload in (b"", b"0\\n", metric(*([0] * 15)),
                        metric(*([0] * 17)), b"00\\n" * 16,
                        b"0\\r\\n" * 16, b"9" * (MAX_METRICS + 1)):
            with self.subTest(payload=payload[:8]), self.assertRaises(ValueError):
                analyze(xml(), 0, ZERO, payload)

    def test_public_cli_redacts_private_data(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            x, m, z = root / "unity-nunit.xml", root / "private-metrics.txt", root / "signatures.txt"
            x.write_bytes(xml())
            m.write_bytes(ZERO)
            z.write_bytes(ZERO)
            import sys
            with patch.object(sys, "argv", ["gate", "--xml", str(x),
                                            "--metrics", str(m), "--signatures", str(z),
                                            "--exit-code", "0"]):
                out = io.StringIO()
                with redirect_stdout(out):
                    self.assertEqual(main(), 0)
            report = out.getvalue()
            self.assertIn("RAFT_T1_ADDRESS_PROVENANCE_GATE", report)
            for private in (str(root), CASE, "PRIVATE_SHADER_NAME", "<test-run"):
                self.assertNotIn(private, report)


if __name__ == "__main__":
    unittest.main()
