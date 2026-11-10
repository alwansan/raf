"""Integration contract for the executable T2 aggregate evidence publication gate.

Runs the actual CLI with a temporary file. It does not touch original game data,
Unity, shaders or private logs. The CLI stdout is the only publishable output.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "t2_foam_evidence_gate_20261110.py"
SHA = "e9c358eda01785b65e4eb14f18723da426635628"


def sample():
    return {
        "schema": "t2-water-aggregate-v1",
        "run_id": 42058825739,
        "session_label": "220911-559",
        "source_commit": SHA,
        "status": "OBSERVED",
        "counts": {
            "water_pass_errors": 23884,
            "fft_kernel_errors": 3850,
            "cursor_warnings": 1333,
            "obb_guid_warnings": 1,
        },
    }


def execute(raw):
    with tempfile.TemporaryDirectory(prefix="t2-evidence-cli-") as folder:
        path = Path(folder) / "aggregate.json"
        path.write_bytes(raw)
        return subprocess.run(
            [sys.executable, str(GATE), str(path)],
            cwd=str(ROOT), capture_output=True, text=True, timeout=15,
            check=False,
        )


class EvidenceCliBoundary(unittest.TestCase):
    def assert_rejected(self, raw):
        proc = execute(raw)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertEqual(proc.stdout, "", "Rejected report leaked publishable stdout")
        self.assertIn("REJECTED:", proc.stderr)
        self.assertNotIn("water_pass_errors", proc.stderr)

    def test_valid_roundtrip_emits_only_aggregate_json(self):
        original = sample()
        proc = execute(json.dumps(original).encode("utf-8"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), original)
        self.assertEqual(len(proc.stdout.splitlines()), 1)
        self.assertEqual(proc.stderr, "")

    def test_raw_path_injection_is_rejected(self):
        payload = sample()
        payload["raw_shader_path"] = "/private/original/source"
        self.assert_rejected(json.dumps(payload).encode())

    def test_duplicate_nested_key_is_rejected(self):
        raw = json.dumps(sample()).replace(
            '"water_pass_errors": 23884',
            '"water_pass_errors": 23884, "water_pass_errors": 0',
        )
        self.assert_rejected(raw.encode())

    def test_invalid_utf8_is_rejected(self):
        # A literal b"\\\\xff" is ASCII, not an invalid UTF-8 byte.
        # Exercise the decoder boundary with a genuinely invalid octet.
        self.assert_rejected(bytes([0xff]))

    def test_valid_utf8_malformed_json_is_rejected(self):
        # Keep JSON syntax rejection distinct from invalid UTF-8 coverage.
        self.assert_rejected(b"\\xff")

    def test_nonfinite_json_is_rejected(self):
        raw = json.dumps(sample()).replace("23884", "NaN")
        self.assert_rejected(raw.encode())

    def test_oversized_file_is_rejected_without_output(self):
        self.assert_rejected(b" " * 65537)

    def test_deep_nesting_is_rejected_without_traceback(self):
        proc = execute(b"[" * 4000 + b"]" * 4000)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertEqual(proc.stdout, "")
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
