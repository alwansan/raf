import unittest
from scripts.t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER


def row(event, seq, extra=""):
    return {"event": event, "message": "sequence=" + str(seq) + extra}


class PairAuditTests(unittest.TestCase):
    def test_paired_is_not_gpu_proof(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1)])
        self.assertEqual(result["missing_return_sequences"], [])
        self.assertFalse(result["gpu_execution_proven"])
        self.assertFalse(result["runtime_kernel_identity_proven"])

    def test_missing_return_is_visible(self):
        self.assertEqual(audit([row(BEFORE, 2)])["missing_return_sequences"], [2])

    def test_return_without_before_is_visible(self):
        self.assertIn("return_without_before:3", audit([row(AFTER, 3)])["errors"])

    def test_duplicate_trace_event_is_visible(self):
        self.assertIn("duplicate_event:1", audit([row(BEFORE, 1), row(BEFORE, 1)])["errors"])

    def test_duplicate_sequence_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit([row(BEFORE, 1, "; sequence=2")])

    def test_unbounded_sequence_rejected(self):
        with self.assertRaisesRegex(ValueError, "bounded"):
            audit([row(BEFORE, 17)])

    def test_return_before_start_does_not_mask_missing_return(self):
        result = audit([row(AFTER, 4), row(BEFORE, 4)])
        self.assertIn("return_without_before:4", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [4])

    def test_orphan_return_followed_by_valid_pair_still_reports_orphan(self):
        result = audit([row(AFTER, 5), row(BEFORE, 5), row(AFTER, 5)])
        self.assertIn("return_without_before:5", result["errors"])
        self.assertIn("duplicate_event:5", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [5])

    def test_duplicate_before_cannot_erase_valid_pair(self):
        result = audit([row(BEFORE, 6), row(BEFORE, 6), row(AFTER, 6)])
        self.assertIn("duplicate_event:6", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [])

    def test_other_events_ignored(self):
        self.assertEqual(audit([{"event": "unrelated"}])["before_count"], 0)


if __name__ == "__main__":
    unittest.main()
