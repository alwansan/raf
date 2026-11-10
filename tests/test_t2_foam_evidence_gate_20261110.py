#!/usr/bin/env python3
"""Unit tests for the standalone T2 aggregate evidence publication gate."""
import unittest
from scripts.t2_foam_evidence_gate_20261110 import sanitize, EvidenceError


def valid():
    return {
        "schema": "t2-water-aggregate-v1",
        "run_id": 42058825739,
        "session_label": "220911-559",
        "source_commit": "e9c358eda01785b65e4eb14f18723da426635628",
        "status": "OBSERVED",
        "counts": {
            "water_pass_errors": 23884,
            "fft_kernel_errors": 3850,
            "cursor_warnings": 1333,
            "obb_guid_warnings": 1,
        },
    }


class EvidenceGateTests(unittest.TestCase):
    def test_owner_aggregate_passes(self):
        self.assertEqual(sanitize(valid())["counts"]["water_pass_errors"], 23884)

    def test_reject_raw_shader_or_path_field(self):
        v = valid()
        v["raw_shader"] = "confidential"
        with self.assertRaises(EvidenceError):
            sanitize(v)

    def test_reject_bool_as_integer(self):
        v = valid()
        v["counts"]["fft_kernel_errors"] = True
        with self.assertRaises(EvidenceError):
            sanitize(v)

    def test_reject_negative(self):
        v = valid()
        v["counts"]["fft_kernel_errors"] = -1
        with self.assertRaises(EvidenceError):
            sanitize(v)

    def test_reject_path_in_session_label(self):
        v = valid()
        v["session_label"] = "../secret"
        with self.assertRaises(EvidenceError):
            sanitize(v)

    def test_reject_missing_count(self):
        v = valid()
        del v["counts"]["cursor_warnings"]
        with self.assertRaises(EvidenceError):
            sanitize(v)

    def test_reject_wrong_sha(self):
        v = valid()
        v["source_commit"] = "private/asset"
        with self.assertRaises(EvidenceError):
            sanitize(v)

    def test_allow_unknown_counter(self):
        v = valid()
        v["counts"]["water_pass_errors"] = None
        self.assertIsNone(sanitize(v)["counts"]["water_pass_errors"])


if __name__ == "__main__":
    unittest.main()
