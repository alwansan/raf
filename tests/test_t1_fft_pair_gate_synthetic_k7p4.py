"""Synthetic, source-free regression checks for T1 paired FFT evidence admission.

No proprietary shader, trace, or asset bytes. Run:
python -m unittest discover -s tests -p 'test_t1_fft_pair_gate_synthetic_k7p4.py'
"""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from scripts.t1_fft_invocation_pair_gate import analyze
from scripts.t1_fft_trace_compare import CAPACITY, INVOCATION_RECORD, INVOCATION_SIZE


def trace(change=False):
    records = []
    for site in range(3):
        coordinate_x = 10 + site + (1 if change and site == 1 else 0)
        records.append(INVOCATION_RECORD.pack(
            site, 1, 2, 3, 0, coordinate_x, 5, 0, 0x3f800000, 0, 0, 0))
    payload = struct.pack("<I", len(records)) + b"".join(records)
    return payload.ljust(INVOCATION_SIZE, b"\\x00")


class PairGateSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.ref = root / "original.bin"
        self.candidate = root / "candidate.bin"
        self.manifest_path = root / "pair.json"
        self.ref.write_bytes(trace())
        self.candidate.write_bytes(trace())
        digest = lambda raw: hashlib.sha256(raw).hexdigest()
        same_input = digest(b"synthetic-input")
        same_dispatch = digest(b"synthetic-dispatch")
        self.manifest = {
            "schema": "t1-fft-invocation-pair-v1",
            "reference": {"role": "original_spirv", "shader_sha256": digest(b"original"),
                          "trace_sha256": digest(self.ref.read_bytes()),
                          "input_sha256": same_input, "dispatch_sha256": same_dispatch},
            "candidate": {"role": "unity_compute_spirv", "shader_sha256": digest(b"candidate"),
                          "trace_sha256": digest(self.candidate.read_bytes()),
                          "input_sha256": same_input, "dispatch_sha256": same_dispatch},
            "expected_records_by_site": [1, 1, 1],
        }
        self.save()

    def save(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def check(self):
        return analyze(self.manifest_path, self.ref, self.candidate)

    def test_equal_traces_are_admitted_but_not_authenticated(self):
        result = self.check()
        self.assertTrue(result["comparison"]["match"])
        self.assertFalse(result["source_authenticity_verified_by_gate"])
        self.assertTrue(result["producer_manifest_is_unsigned"])

    def test_coordinate_divergence_is_reported(self):
        self.candidate.write_bytes(trace(change=True))
        self.manifest["candidate"]["trace_sha256"] = hashlib.sha256(self.candidate.read_bytes()).hexdigest()
        self.save()
        result = self.check()
        self.assertFalse(result["comparison"]["match"])
        self.assertEqual(result["comparison"]["sites"][1]["coordinate_mismatches"], 1)

    def test_digest_mismatch_rejected(self):
        self.candidate.write_bytes(trace(change=True))
        with self.assertRaisesRegex(ValueError, "digest"):
            self.check()

    def test_input_mismatch_rejected(self):
        self.manifest["candidate"]["input_sha256"] = hashlib.sha256(b"different").hexdigest()
        self.save()
        with self.assertRaisesRegex(ValueError, "input/dispatch"):
            self.check()

    def test_dispatch_mismatch_rejected(self):
        self.manifest["candidate"]["dispatch_sha256"] = hashlib.sha256(b"different").hexdigest()
        self.save()
        with self.assertRaisesRegex(ValueError, "input/dispatch"):
            self.check()

    def test_same_underlying_file_rejected(self):
        with self.assertRaisesRegex(ValueError, "identical underlying"):
            analyze(self.manifest_path, self.ref, self.ref)

    def test_wrong_site_coverage_rejected(self):
        self.manifest["expected_records_by_site"] = [2, 1, 1]
        self.save()
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.check()

    def test_boolean_coverage_rejected(self):
        self.manifest["expected_records_by_site"] = [True, 1, 1]
        self.save()
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.check()

    def test_duplicate_json_key_rejected(self):
        raw = self.manifest_path.read_text()
        self.manifest_path.write_text(raw.replace('"schema":', '"schema":"bad", "schema":', 1))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check()

    def test_invalid_trace_length_rejected(self):
        self.candidate.write_bytes(b"short")
        with self.assertRaisesRegex(ValueError, "byte size"):
            self.check()


if __name__ == "__main__":
    unittest.main()
