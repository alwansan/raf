"""GFX143 source-free regressions for two-run original Android capture auditing."""
from __future__ import annotations

import io
import json
from hashlib import sha256
from tempfile import TemporaryDirectory
from pathlib import Path
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from gfxlab.tests.test_gfx139_full_batch_replay import FullBatchReplay
from gfxlab.tools.gfx143_owner_dual_run_audit import analyze, pixel_statistics


class GFX143OwnerDualRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FullBatchReplay.setUpClass()
        cls.reference_sha = sha256(FullBatchReplay.apk.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        FullBatchReplay.tearDownClass()

    @classmethod
    def owner(cls):
        return FullBatchReplay.owner()

    def test_complete_two_run_replay_passes_against_real_batch_auditor(self):
        safe = analyze(self.owner(), self.owner(), FullBatchReplay.apk,
                       self.reference_sha)
        self.assertTrue(safe["production_gfx124_zip_audit_passed_twice"])
        self.assertTrue(safe["owner_zip_contents_byte_identical"])
        self.assertTrue(safe["all_coverage_masks_match_reference"])
        self.assertEqual(safe["validated_cases"], 9)
        self.assertEqual(safe["validated_captures"], 51)
        self.assertEqual(safe["capture_count_with_exact_rgba"], 51)
        self.assertFalse(safe["hotspots_rgb_channel_error_above30"])
        self.assertFalse(safe["phase_closed"])

    def test_different_valid_archive_contents_detected_not_silenced(self):
        baseline = self.owner()
        changed = io.BytesIO()
        with ZipFile(self.owner()) as original, ZipFile(changed, "w", ZIP_DEFLATED) as output:
            for entry in original.infolist():
                raw = original.read(entry.filename)
                if entry.filename == "summary.json":
                    data = json.loads(raw)
                    data["trial_number"] = 2
                    raw = json.dumps(data).encode()
                output.writestr(entry.filename, raw)
        changed.seek(0)
        safe = analyze(baseline, changed, FullBatchReplay.apk,
                       self.reference_sha)
        self.assertFalse(safe["owner_zip_contents_byte_identical"])
        self.assertTrue(safe["production_gfx124_zip_audit_passed_twice"])

    def test_rejects_bad_reference_apk_hash(self):
        with self.assertRaisesRegex(ValueError, "Wrong signed original"):
            analyze(self.owner(), self.owner(), FullBatchReplay.apk, "0" * 64)

    def test_rejects_incomplete_case_even_if_other_eight_are_valid(self):
        with self.assertRaisesRegex(ValueError, "Not all nine"):
            analyze(self.owner(), FullBatchReplay.owner(failed="M02-deferred"),
                    FullBatchReplay.apk, self.reference_sha)

    def test_rejects_modified_raw_image_with_unmodified_summary(self):
        altered = io.BytesIO()
        with ZipFile(self.owner()) as original, ZipFile(altered, "w", ZIP_DEFLATED) as output:
            for entry in original.infolist():
                raw = original.read(entry.filename)
                if entry.filename == "M00-0-light.png":
                    raw = raw[:-1] + bytes([raw[-1] ^ 1])
                output.writestr(entry.filename, raw)
        altered.seek(0)
        with self.assertRaises((ValueError, OSError)):
            analyze(self.owner(), altered, FullBatchReplay.apk, self.reference_sha)

    def test_detects_single_pixel_high_error_with_exact_coverage(self):
        ref = bytearray(256 * 256 * 4)
        actual = bytearray(ref)
        pos = (3 * 256 + 4) * 4
        ref[pos:pos+4] = bytes([20, 30, 40, 255])
        actual[pos:pos+4] = bytes([80, 30, 40, 255])
        report = pixel_statistics(bytes(actual), bytes(ref))
        self.assertEqual(report["max_rgb_channel_error"], 60)
        self.assertEqual(report["rgb_outlier_pixels_gt30"], 1)
        self.assertEqual(report["outlier_bbox_xyxy"], [4, 3, 4, 3])
        self.assertEqual(report["alpha_byte_differing_pixels"], 0)

    def test_alpha_channel_numeric_drift_is_not_lost_with_mrt_mask(self):
        ref = bytearray(256 * 256 * 4)
        actual = bytearray(ref)
        ref[:4] = bytes([10, 20, 30, 90])
        actual[:4] = bytes([10, 20, 30, 91])
        mask = bytes([255] + [0] * (256 * 256 - 1))
        result = pixel_statistics(bytes(actual), bytes(ref), covered_mask=mask)
        self.assertEqual(result["alpha_byte_differing_pixels"], 1)
        self.assertEqual(result["max_alpha_byte_error"], 1)
        self.assertEqual(result["covered_pixels"], 1)
        self.assertEqual(result["max_rgb_channel_error"], 0)


if __name__ == "__main__":
    unittest.main()
