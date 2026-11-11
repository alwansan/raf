#!/usr/bin/env python3
"""Synthetic-only provenance tests for T1 FFT pass proximity."""
import unittest
from t1_fft_pass_proximity import summarize


def valid():
    return {
        "session_id": "synthetic-220911",
        "source_sha256": "a" * 64,
        "sample_errors_only": True,
        "original_kernel_identity_proven": False,
        "events": [],
    }


class ProvenanceTests(unittest.TestCase):
    def test_valid_metadata_preserved(self):
        scan = valid()
        result = summarize(scan)
        self.assertEqual(result["session_id"], scan["session_id"])
        self.assertEqual(result["source_sha256"], scan["source_sha256"])
        self.assertEqual(result["sampled_errors"], 0)

    def test_missing_and_malformed_session(self):
        for value in (None, "", " ", 12, [], "x" * 161):
            with self.subTest(value=repr(value)):
                scan = valid()
                scan["session_id"] = value
                with self.assertRaisesRegex(ValueError, "session_id"):
                    summarize(scan)
        scan = valid()
        del scan["session_id"]
        with self.assertRaisesRegex(ValueError, "session_id"):
            summarize(scan)

    def test_missing_and_malformed_digest(self):
        for value in (None, "", 1, True, "A" * 64, "g" * 64, "a" * 63, "a" * 65):
            with self.subTest(value=repr(value)):
                scan = valid()
                scan["source_sha256"] = value
                with self.assertRaisesRegex(ValueError, "source_sha256"):
                    summarize(scan)
        scan = valid()
        del scan["source_sha256"]
        with self.assertRaisesRegex(ValueError, "source_sha256"):
            summarize(scan)


if __name__ == "__main__":
    unittest.main()
