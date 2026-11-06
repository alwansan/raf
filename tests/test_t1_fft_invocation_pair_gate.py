import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest

from scripts.t1_fft_invocation_pair_gate import SCHEMA, analyze, _read_manifest
from scripts.t1_fft_trace_compare import INVOCATION_RECORD, INVOCATION_SIZE


def trace(values=(1, 2, 3), coords=((1, 2, 0), (1, 2, 0), (1, 2, 0))):
    out = bytearray(INVOCATION_SIZE)
    struct.pack_into("<I", out, 0, 3)
    for site in range(3):
        row = INVOCATION_RECORD.pack(site, 4, 5, 0, 0, *coords[site],
                                     values[site], 0, 0, 0)
        offset = 4 + site * INVOCATION_RECORD.size
        out[offset:offset + INVOCATION_RECORD.size] = row
    return bytes(out)


def digest(b):
    return hashlib.sha256(b).hexdigest()


class StrictPairedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.original = root / "original.bin"
        self.candidate = root / "candidate.bin"
        self.manifest = root / "manifest.json"
        self.original.write_bytes(trace())
        self.candidate.write_bytes(trace())
        self.metadata = {
            "schema": SCHEMA, "expected_records_by_site": [1, 1, 1],
            "reference": {
                "role": "original_spirv", "shader_sha256": "a"*64,
                "input_sha256": "b"*64, "dispatch_sha256": "c"*64,
                "trace_sha256": digest(self.original.read_bytes())},
            "candidate": {
                "role": "hlsl_roundtrip_spirv", "shader_sha256": "d"*64,
                "input_sha256": "b"*64, "dispatch_sha256": "c"*64,
                "trace_sha256": digest(self.candidate.read_bytes())}}
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.metadata), encoding="utf-8")

    def compare(self):
        return analyze(self.manifest, self.original, self.candidate)

    def test_independent_files_can_legitimately_have_identical_bytes(self):
        result = self.compare()
        self.assertTrue(result["comparison"]["match"])
        self.assertTrue(result["independent_trace_files_verified"])
        self.assertFalse(result["source_authenticity_verified_by_gate"])
        self.assertEqual([s["paired_reads"] for s in result["comparison"]["sites"]], [1, 1, 1])
        self.assertNotIn("a"*64, str(result))

    def test_same_file_is_not_a_pair(self):
        with self.assertRaisesRegex(ValueError, "identical underlying"):
            analyze(self.manifest, self.original, self.original)

    def test_symlink_to_same_file_is_not_a_pair(self):
        link = Path(self.tmp.name) / "link.bin"
        link.symlink_to(self.original)
        with self.assertRaisesRegex(ValueError, "identical underlying"):
            analyze(self.manifest, self.original, link)

    def test_hardlinked_file_is_not_a_pair(self):
        link = Path(self.tmp.name) / "hardlink.bin"
        os.link(self.original, link)
        with self.assertRaisesRegex(ValueError, "identical underlying"):
            analyze(self.manifest, self.original, link)

    def test_input_mismatch_rejected(self):
        self.metadata["candidate"]["input_sha256"] = "e"*64
        self.save()
        with self.assertRaisesRegex(ValueError, "input/dispatch"):
            self.compare()

    def test_dispatch_mismatch_rejected(self):
        self.metadata["candidate"]["dispatch_sha256"] = "f"*64
        self.save()
        with self.assertRaisesRegex(ValueError, "input/dispatch"):
            self.compare()

    def test_wrong_original_role_rejected(self):
        self.metadata["reference"]["role"] = "unity_compute_spirv"
        self.save()
        with self.assertRaisesRegex(ValueError, "original source stage"):
            self.compare()

    def test_invalid_candidate_role_rejected(self):
        self.metadata["candidate"]["role"] = "unverified"
        self.save()
        with self.assertRaisesRegex(ValueError, "candidate stage"):
            self.compare()

    def test_trace_digest_is_authenticated_against_manifest(self):
        self.metadata["reference"]["trace_sha256"] = "0"*64
        self.save()
        with self.assertRaisesRegex(ValueError, "digest"):
            self.compare()

    def test_expected_site_coverage_must_match_actual_capture(self):
        self.metadata["expected_records_by_site"] = [1, 2, 1]
        self.save()
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.compare()

    def test_empty_trace_is_not_accepted_even_when_declared_digest_matches(self):
        data = bytes(INVOCATION_SIZE)
        self.original.write_bytes(data)
        self.metadata["reference"]["trace_sha256"] = digest(data)
        self.save()
        with self.assertRaisesRegex(ValueError, "Empty or overflowed"):
            self.compare()

    def test_truncated_trace_rejected(self):
        self.original.write_bytes(trace()[:-1])
        with self.assertRaisesRegex(ValueError, "byte size"):
            self.compare()

    def test_oversized_trace_rejected(self):
        self.original.write_bytes(trace() + b"extra")
        with self.assertRaisesRegex(ValueError, "byte size"):
            self.compare()

    def test_coordinate_mismatch_not_reported_as_parity(self):
        data = trace(coords=((1, 2, 0), (9, 2, 0), (1, 2, 0)))
        self.candidate.write_bytes(data)
        self.metadata["candidate"]["trace_sha256"] = digest(data)
        self.save()
        report = self.compare()["comparison"]
        self.assertFalse(report["match"])
        self.assertEqual(report["sites"][1]["coordinate_mismatches"], 1)

    def test_value_mismatch_not_reported_as_parity(self):
        data = trace(values=(1, 9, 3))
        self.candidate.write_bytes(data)
        self.metadata["candidate"]["trace_sha256"] = digest(data)
        self.save()
        report = self.compare()["comparison"]
        self.assertFalse(report["match"])
        self.assertEqual(report["sites"][1]["same_coordinate_value_mismatches"], 1)

    def test_manifest_duplicate_fields_rejected(self):
        self.manifest.write_text('{"schema":"x","schema":"x"}')
        with self.assertRaisesRegex(ValueError, "duplicate"):
            _read_manifest(self.manifest)

    def test_manifest_size_bounded_before_parsing(self):
        self.manifest.write_bytes(b" " * 8193)
        with self.assertRaisesRegex(ValueError, "size"):
            _read_manifest(self.manifest)

    def test_zero_site_coverage_is_invalid(self):
        self.metadata["expected_records_by_site"] = [0, 1, 1]
        self.save()
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.compare()

    def test_coverage_over_capacity_rejected(self):
        self.metadata["expected_records_by_site"] = [512, 1, 1]
        self.save()
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.compare()

    def test_digest_must_be_sha256_hex(self):
        self.metadata["reference"]["shader_sha256"] = "bad"
        self.save()
        with self.assertRaisesRegex(ValueError, "SHA256"):
            self.compare()


if __name__ == "__main__":
    unittest.main()
