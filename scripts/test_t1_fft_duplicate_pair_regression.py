"""Regression: duplicate trace events must never count as valid FFT pairs."""
import unittest
from t1_fft_dispatch_pair_audit import BEFORE, AFTER, audit


def row(event, sequence=1, result=None):
    message = f"sequence={sequence};kernel=FFT"
    if result is not None:
        message += f";result={result}"
    return {"event": event, "message": message}


class DuplicatePairRegression(unittest.TestCase):
    def test_normal_pair(self):
        result = audit([row(BEFORE), row(AFTER, result="returned")])
        self.assertEqual(result["paired_count"], 1)
        self.assertEqual(result["missing_return_sequences"], [])

    def test_duplicate_return_invalidates_earlier_pair(self):
        result = audit([row(BEFORE), row(AFTER, result="returned"), row(AFTER, result="returned")])
        self.assertEqual(result["paired_count"], 0)
        self.assertEqual(result["missing_return_sequences"], [1])
        self.assertIn("duplicate_event:1", result["errors"])

    def test_duplicate_before_invalidates_later_return(self):
        result = audit([row(BEFORE), row(BEFORE), row(AFTER, result="returned")])
        self.assertEqual(result["paired_count"], 0)
        self.assertEqual(result["missing_return_sequences"], [1])

    def test_distinct_sequences_remain_independent(self):
        result = audit([row(BEFORE, 1), row(AFTER, 1, "returned"), row(BEFORE, 2),
                        row(AFTER, 2, "returned"), row(AFTER, 2, "returned")])
        self.assertEqual(result["paired_count"], 1)
        self.assertEqual(result["missing_return_sequences"], [2])


if __name__ == "__main__":
    unittest.main()
