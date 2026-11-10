#!/usr/bin/env python3
"""Unit tests for the standalone T2 aggregate evidence publication gate."""
import unittest
import json
from scripts.t2_foam_evidence_gate_20261110 import sanitize, EvidenceError, parse_aggregate_json


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
    def test_strict_json_accepts_owner_aggregate(self):
        result = parse_aggregate_json(json.dumps(valid()).encode("utf-8"))
        self.assertEqual(result["counts"]["fft_kernel_errors"], 3850)

    def test_reject_duplicate_top_level_key(self):
        raw = json.dumps(valid()).replace('"status": "OBSERVED"',
                                          '"status": "UNKNOWN", "status": "OBSERVED"')
        with self.assertRaises(EvidenceError):
            parse_aggregate_json(raw.encode("utf-8"))

    def test_reject_duplicate_nested_counter(self):
        raw = json.dumps(valid()).replace('"fft_kernel_errors": 3850',
                                          '"fft_kernel_errors": 1, "fft_kernel_errors": 3850')
        with self.assertRaises(EvidenceError):
            parse_aggregate_json(raw.encode("utf-8"))

    def test_reject_nonfinite_json_extension(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                raw = json.dumps(valid()).replace('"fft_kernel_errors": 3850',
                                                  '"fft_kernel_errors": ' + value)
                with self.assertRaises(EvidenceError):
                    parse_aggregate_json(raw.encode("utf-8"))

    def test_reject_python_integer_digit_limit_without_traceback(self):
        # Under Python 3.11+, int conversion raises ValueError at >4300 digits.
        # This input remains below MAX_BYTES and must fail as EvidenceError.
        raw = json.dumps(valid()).replace('"fft_kernel_errors": 3850',
                                          '"fft_kernel_errors": ' + "9" * 5000)
        with self.assertRaises(EvidenceError):
            parse_aggregate_json(raw.encode("utf-8"))

    def test_reject_malformed_utf8_via_public_parser(self):
        # Input can be under MAX_BYTES yet fail strict UTF-8 decoding.
        # The public API must fail closed using its own exception type.
        for raw in (b"\xff", b'{"schema":"\xc0\xaf"}', b"\xed\xa0\x80"):
            with self.subTest(raw=raw):
                with self.assertRaises(EvidenceError):
                    parse_aggregate_json(raw)

    def test_reject_oversize_before_parse(self):
        with self.assertRaises(EvidenceError):
            parse_aggregate_json(b" " * 65537)

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
