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
        self.assertEqual(result["missing_return_sequences"], [6])

    def test_failed_return_not_counted_as_successful_pair(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1, ";result=exception")])
        self.assertEqual(result["returned_count"], 1)
        self.assertEqual(result["paired_count"], 0)
        self.assertEqual(result["failed_return_sequences"], [1])
        self.assertEqual(result["missing_return_sequences"], [1])
        self.assertIn("dispatch_result_failure:1", result["errors"])

    def test_success_and_failure_outcomes_are_distinct(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1, ";result=returned"),
                        row(BEFORE, 2), row(AFTER, 2, ";result=error")])
        self.assertEqual(result["returned_count"], 2)
        self.assertEqual(result["paired_count"], 1)
        self.assertEqual(result["failed_return_sequences"], [2])
        self.assertEqual(result["missing_return_sequences"], [2])
        self.assertFalse(result["gpu_execution_proven"])

    def test_failed_return_and_identity_mismatch_both_reported(self):
        result = audit([row(BEFORE, 1, ";kernel=6"),
                        row(AFTER, 1, ";kernel=7;result=exception")])
        self.assertIn("identity_mismatch:1:kernel", result["errors"])
        self.assertIn("dispatch_result_failure:1", result["errors"])
        self.assertEqual(result["failed_return_sequences"], [1])
        self.assertEqual(result["paired_count"], 0)
        self.assertEqual(result["missing_return_sequences"], [1])

    def test_successful_return_with_mismatched_kernel_not_paired(self):
        result = audit([row(BEFORE, 2, ";kernel=6"),
                        row(AFTER, 2, ";kernel=7;result=returned")])
        self.assertIn("identity_mismatch:2:kernel", result["errors"])
        self.assertEqual(result["failed_return_sequences"], [])
        self.assertEqual(result["paired_count"], 0)

    def test_cross_session_pairs_not_counted(self):
        result = audit([row(BEFORE, 1, ";session_id=alpha;build_sha=aaa"),
                        row(AFTER, 1, ";session_id=alpha;build_sha=aaa"),
                        row(BEFORE, 2, ";session_id=beta;build_sha=aaa"),
                        row(AFTER, 2, ";session_id=beta;build_sha=aaa")])
        self.assertIn("cross_session_provenance:session_id:2", result["errors"])
        self.assertEqual(result["paired_count"], 0)
        self.assertEqual(result["missing_return_sequences"], [1, 2])

    def test_cross_build_pairs_not_counted(self):
        result = audit([row(BEFORE, 1, ";build_sha=aaa"),
                        row(AFTER, 1, ";build_sha=aaa"),
                        row(BEFORE, 2, ";build_sha=bbb"),
                        row(AFTER, 2, ";build_sha=bbb")])
        self.assertIn("cross_session_provenance:build_sha:2", result["errors"])
        self.assertEqual(result["paired_count"], 0)

    def test_single_session_multiple_sequences_still_paired(self):
        result = audit([row(BEFORE, 1, ";session_id=alpha;build_sha=aaa"),
                        row(AFTER, 1, ";session_id=alpha;build_sha=aaa"),
                        row(BEFORE, 2, ";session_id=alpha;build_sha=aaa"),
                        row(AFTER, 2, ";session_id=alpha;build_sha=aaa")])
        self.assertEqual(result["paired_count"], 2)
        self.assertEqual(result["errors"], [])

    def test_missing_session_provenance_invalidates_all_pairs(self):
        result = audit([row(BEFORE, 1, ";session_id=alpha"),
                        row(AFTER, 1, ";session_id=alpha"),
                        row(BEFORE, 2), row(AFTER, 2)])
        self.assertIn("cross_session_provenance_presence:session_id:2", result["errors"])
        self.assertEqual(result["paired_count"], 0)
        self.assertEqual(result["missing_return_sequences"], [1, 2])

    def test_late_build_provenance_invalidates_legacy_pair(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1),
                        row(BEFORE, 2, ";build_sha=abc"),
                        row(AFTER, 2, ";build_sha=abc")])
        self.assertIn("cross_session_provenance_presence:build_sha:2", result["errors"])
        self.assertEqual(result["paired_count"], 0)

    def test_all_legacy_rows_remain_parseable(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1),
                        row(BEFORE, 2), row(AFTER, 2)])
        self.assertEqual(result["paired_count"], 2)
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["gpu_execution_proven"])

    def test_other_events_ignored(self):
        self.assertEqual(audit([{"event": "unrelated"}])["before_count"], 0)


if __name__ == "__main__":
    unittest.main()
