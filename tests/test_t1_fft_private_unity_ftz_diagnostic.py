"""Sourcefree regression checks for private invocation taxonomy; no game assets."""
import hashlib
import io
import json
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from scripts.t1_fft_invocation_pair_gate import SCHEMA
from scripts.t1_fft_private_unity_ftz_diagnostic import classify, main
from scripts.t1_fft_trace_compare import CAPACITY, INVOCATION_RECORD


def rows():
    # Three sites, one invocation each; coordinates are synthetic.
    return [
        [site, site, 0, 0, 0, site + 1, 4, 0,
         0x3f800000, 0x00000001, 0x80000001, 0x40000000]
        for site in range(3)
    ]


def packed(data):
    body = b"".join(INVOCATION_RECORD.pack(*row) for row in data)
    return (struct.pack("<I", len(data)) + body +
            bytes((CAPACITY-len(data)) * INVOCATION_RECORD.size))


def digest(data):
    return hashlib.sha256(data).hexdigest()


class PrivateUnityFtzDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.original = self.root / "original.trace"
        self.unity = self.root / "unity.trace"
        self.manifest = self.root / "manifest.json"

    def fixture(self, original=None, unity=None, *, stage="unity_compute_spirv",
                input_change=False, dispatch_change=False):
        a = packed(rows() if original is None else original)
        b = packed(rows() if unity is None else unity)
        self.original.write_bytes(a)
        self.unity.write_bytes(b)
        base = dict(input_sha256="a" * 64, dispatch_sha256="b" * 64)
        original_meta = dict(base, role="original_spirv",
                             shader_sha256="c" * 64, trace_sha256=digest(a))
        unity_meta = dict(base, role=stage,
                          shader_sha256="d" * 64, trace_sha256=digest(b))
        if input_change:
            unity_meta["input_sha256"] = "e" * 64
        if dispatch_change:
            unity_meta["dispatch_sha256"] = "f" * 64
        self.manifest.write_text(json.dumps({
            "schema": SCHEMA, "reference": original_meta,
            "candidate": unity_meta, "expected_records_by_site": [1, 1, 1],
        }))
        return classify(self.manifest, self.original, self.unity)

    def test_match_has_no_diagnostic_mismatches(self):
        report = self.fixture()
        self.assertFalse(report["signed_unity_producer_attestation"])
        self.assertFalse(report["float32_FTZ_causality_proven"])
        self.assertFalse(report["android_water_or_pixels_proven"])
        self.assertEqual(len(report["diagnostics"]), 3)
        for s in report["diagnostics"]:
            self.assertEqual(s["paired_invocations"], 1)
            self.assertEqual(s["same_coordinate_bitwise_value_mismatches"], 0)
            self.assertEqual(s["coordinate_mismatching_invocations"], 0)

    def test_coordinate_zero_collapse_is_not_float_value_ftz(self):
        altered = rows()
        altered[0][5] = 0
        s = self.fixture(unity=altered)["diagnostics"][0]
        self.assertEqual(s["coordinate_zero_collapse_by_axis"]["x"], 1)
        self.assertEqual(s["other_coordinate_drift_by_axis"]["x"], 0)
        self.assertEqual(s["same_coordinate_subnormal_to_zero_channels"], 0)
        self.assertEqual(s["value_comparison_skipped_after_coordinate_drift"], 1)

    def test_nonzero_coordinate_drift_is_not_zero_collapse(self):
        altered = rows()
        altered[1][6] = 14
        s = self.fixture(unity=altered)["diagnostics"][1]
        self.assertEqual(s["other_coordinate_drift_by_axis"]["y"], 1)
        self.assertEqual(s["coordinate_zero_collapse_by_axis"]["y"], 0)

    def test_subnormal_positive_negative_value_to_signed_zero(self):
        altered = rows()
        altered[2][9] = 0x00000000
        altered[2][10] = 0x80000000
        s = self.fixture(unity=altered)["diagnostics"][2]
        self.assertEqual(s["same_coordinate_subnormal_to_zero_channels"], 2)
        self.assertEqual(s["same_coordinate_bitwise_value_mismatches"], 2)
        self.assertEqual(s["same_coordinate_other_value_mismatch_channels"], 0)
        self.assertEqual(s["coordinate_mismatching_invocations"], 0)

    def test_non_subnormal_value_difference_is_not_ftz(self):
        altered = rows()
        altered[0][8] = 0x3f800001
        s = self.fixture(unity=altered)["diagnostics"][0]
        self.assertEqual(s["same_coordinate_other_value_mismatch_channels"], 1)
        self.assertEqual(s["same_coordinate_subnormal_to_zero_channels"], 0)

    def test_signed_zero_bitwise_difference_still_counted(self):
        altered = rows()
        altered[0][9] = 0x80000000
        ref = rows()
        ref[0][9] = 0x00000000
        s = self.fixture(original=ref, unity=altered)["diagnostics"][0]
        self.assertEqual(s["same_coordinate_other_value_mismatch_channels"], 1)
        self.assertEqual(s["same_coordinate_subnormal_to_zero_channels"], 0)

    def test_coordinate_drift_cannot_be_misattributed_to_value_ftz(self):
        altered = rows()
        altered[0][5] = 0
        altered[0][9] = 0
        s = self.fixture(unity=altered)["diagnostics"][0]
        self.assertEqual(s["coordinate_zero_collapse_by_axis"]["x"], 1)
        self.assertEqual(s["same_coordinate_subnormal_to_zero_channels"], 0)

    def test_missing_extra_invocations_counted_without_values(self):
        altered = rows()
        altered[0][1] = 99
        s = self.fixture(unity=altered)["diagnostics"][0]
        self.assertEqual(s["paired_invocations"], 0)
        self.assertEqual(s["reference_only_invocations"], 1)
        self.assertEqual(s["unity_only_invocations"], 1)

    def test_candidate_stage_must_be_claimed_unity_not_vulkan(self):
        with self.assertRaises(ValueError):
            self.fixture(stage="hlsl_roundtrip_spirv")

    def test_mismatched_input_or_dispatch_declarations_rejected(self):
        for option in ("input_change", "dispatch_change"):
            with self.subTest(option=option), self.assertRaises(ValueError):
                self.fixture(**{option: True})

    def test_reject_tampered_digest(self):
        self.fixture()
        with self.unity.open("ab") as out:
            out.write(b"x")
        with self.assertRaises(ValueError):
            classify(self.manifest, self.original, self.unity)

    def test_reject_samefile_even_with_hardlink(self):
        self.fixture()
        self.unity.unlink()
        self.unity.hardlink_to(self.original)
        with self.assertRaises(ValueError):
            classify(self.manifest, self.original, self.unity)

    def test_reject_symlink_input_without_reading(self):
        self.fixture()
        link = self.root / "linked.trace"
        link.symlink_to(self.unity)
        with self.assertRaises(ValueError):
            classify(self.manifest, self.original, link)

    def test_reject_duplicate_invocation_keys(self):
        duplicate = rows()
        duplicate.insert(0, duplicate[0][:])
        with self.assertRaises(ValueError):
            self.fixture(original=duplicate)

    def test_public_report_and_cli_hide_hashes_keys_and_value_bits(self):
        report = self.fixture()
        serialized = json.dumps(report)
        for private in ("aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb",
                        "3f800000", "80000001", "original.trace"):
            self.assertNotIn(private, serialized)
        import sys
        with patch.object(sys, "argv", ["gate", "--manifest", str(self.manifest),
                                        "--original", str(self.original),
                                        "--unity", str(self.unity)]):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(), 0)
        self.assertEqual(out.getvalue().count("RAFT_T1_FTZ_TRACE "), 1)
        self.assertNotIn(str(self.root), out.getvalue())

    def test_reject_duplicate_json_manifest_field(self):
        self.fixture()
        metadata = self.manifest.read_text()
        self.manifest.write_text(metadata.replace('"schema":', '"schema": "duplicate", "schema":', 1))
        with self.assertRaises(ValueError):
            classify(self.manifest, self.original, self.unity)


if __name__ == "__main__":
    unittest.main()
