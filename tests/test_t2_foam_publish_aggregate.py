"""Source-only subprocess regression of the opt-in aggregate publisher."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "scripts" / "t2_foam_publish_aggregate.py"


def sample():
    return {"schema": "t2-water-aggregate-v1", "run_id": 42058825739,
            "session_label": "220911-559",
            "source_commit": "e9c358eda01785b65e4eb14f18723da426635628",
            "status": "OBSERVED",
            "counts": {"water_pass_errors": 23884, "fft_kernel_errors": 3850,
                       "cursor_warnings": 1333, "obb_guid_warnings": 1}}


class PublishContract(unittest.TestCase):
    def execute(self, raw, old=None):
        with tempfile.TemporaryDirectory() as td:
            source, output = Path(td) / "input.json", Path(td) / "output.json"
            source.write_bytes(raw)
            if old is not None:
                output.write_bytes(old)
            proc = subprocess.run([sys.executable, str(ADAPTER), "--input", str(source),
                                   "--output", str(output)], cwd=ROOT,
                                  capture_output=True, text=True, timeout=15)
            return proc, output.read_bytes() if output.exists() else None, list(Path(td).glob(".t2-aggregate-*"))

    def test_valid_canonical_publication(self):
        proc, content, temporary = self.execute(json.dumps(sample()).encode())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(content), sample())
        self.assertEqual(proc.stdout + proc.stderr, "")
        self.assertEqual(temporary, [])

    def test_invalid_does_not_create_publishable_output(self):
        proc, content, temporary = self.execute(b"{bad")
        self.assertEqual(proc.returncode, 2)
        self.assertIsNone(content)
        self.assertEqual(temporary, [])
        self.assertNotIn("bad", proc.stderr)

    def test_invalid_utf8_preserves_previous_report(self):
        proc, content, temporary = self.execute(bytes([255]), b"previous")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(content, b"previous")
        self.assertEqual(temporary, [])

    def test_private_path_is_rejected_without_leak(self):
        data = sample()
        data["private_shader_path"] = "/private/asset.shader"
        proc, content, _ = self.execute(json.dumps(data).encode())
        self.assertEqual(proc.returncode, 2)
        self.assertIsNone(content)
        self.assertNotIn("/private", proc.stderr)

    def test_valid_replaces_old_report(self):
        proc, content, _ = self.execute(json.dumps(sample()).encode(), b"previous")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(content), sample())

    def test_symlink_input_rejected_without_reading_target(self):
        with tempfile.TemporaryDirectory() as td:
            target, link, output = (Path(td) / name for name in ("private", "input", "output"))
            target.write_text(json.dumps(sample()))
            link.symlink_to(target)
            proc = subprocess.run([sys.executable, str(ADAPTER), "--input", str(link),
                                   "--output", str(output)], cwd=ROOT, capture_output=True,
                                  text=True, timeout=15)
            self.assertEqual(proc.returncode, 2)
            self.assertFalse(output.exists())
            self.assertNotIn(str(target), proc.stderr)

    def test_directory_input_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "output"
            proc = subprocess.run([sys.executable, str(ADAPTER), "--input", td,
                                   "--output", str(output)], cwd=ROOT, capture_output=True,
                                  text=True, timeout=15)
            self.assertEqual(proc.returncode, 2)
            self.assertFalse(output.exists())

    def test_symlink_output_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            source, target, link = (Path(td) / name for name in ("input", "protected", "link"))
            source.write_text(json.dumps(sample()))
            target.write_bytes(b"protected")
            link.symlink_to(target)
            proc = subprocess.run([sys.executable, str(ADAPTER), "--input", str(source),
                                   "--output", str(link)], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(target.read_bytes(), b"protected")


if __name__ == "__main__":
    unittest.main()
