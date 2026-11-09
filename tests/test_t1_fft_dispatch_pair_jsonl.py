"""Regression controls for T1 FFT trace JSONL parsing (synthetic data only)."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t1_fft_dispatch_pair_audit import (
    BEFORE, AFTER, audit, reject_duplicate_json_keys,
)


class TraceJsonContract(unittest.TestCase):
    def parse(self, line):
        return json.loads(line, object_pairs_hook=reject_duplicate_json_keys)

    def test_duplicate_top_level_event_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON trace key"):
            self.parse('{"event":"a","event":"b","message":"sequence=1"}')

    def test_duplicate_nested_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON trace key"):
            self.parse('{"event":"a","meta":{"build":"a","build":"b"}}')

    def test_valid_pair_is_accepted_without_gpu_proof(self):
        rows = [
            self.parse(json.dumps({"event": BEFORE, "message": "sequence=1;kernel=K;groups_x=1"})),
            self.parse(json.dumps({"event": AFTER, "message": "sequence=1;kernel=K;groups_x=1"})),
        ]
        result = audit(rows)
        self.assertEqual(result["missing_return_sequences"], [])
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["gpu_execution_proven"])
        self.assertFalse(result["runtime_kernel_identity_proven"])

    def test_mismatched_kernel_still_detected(self):
        rows = [
            {"event": BEFORE, "message": "sequence=1;kernel=K1"},
            {"event": AFTER, "message": "sequence=1;kernel=K2"},
        ]
        result = audit(rows)
        self.assertIn("identity_mismatch:1:kernel", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [1])


if __name__ == "__main__":
    unittest.main()
