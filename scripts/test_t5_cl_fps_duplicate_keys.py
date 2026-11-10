#!/usr/bin/env python3
"""T5 regression: LogRaft cohort must reject ambiguous JSONL provenance."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.t5_cl_fps_cohort_gate import load_samples


class CohortDuplicateKeysTest(unittest.TestCase):
    def _load(self, line):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.jsonl"
            path.write_text(line + "\n", encoding="utf-8")
            return load_samples(path)

    def test_valid_single_row(self):
        row = {"schema": 1, "source": "lograf_shell",
               "package": "com.alwansan.raft.androidtest",
               "sample": 1, "timestamp_unix_ms": 100}
        self.assertEqual(self._load(json.dumps(row)), [row])

    def test_duplicate_package_rejected(self):
        line = ('{"schema":1,"source":"lograf_shell",'
                '"package":"other","package":"com.alwansan.raft.androidtest",'
                '"sample":1,"timestamp_unix_ms":100}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON telemetry key"):
            self._load(line)

    def test_duplicate_nested_key_rejected(self):
        line = ('{"schema":1,"source":"lograf_shell",'
                '"package":"com.alwansan.raft.androidtest",'
                '"sample":1,"timestamp_unix_ms":100,'
                '"metadata":{"pid":1,"pid":2}}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON telemetry key"):
            self._load(line)


if __name__ == "__main__":
    unittest.main()
