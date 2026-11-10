"""Regression for private FFT capture SHA gate (synthetic bytes only)."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from scripts.t1_fft_capture_integrity_gate import verify_captures

class CaptureGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data = b"\x00" * 16
        (self.root / "v.bin").write_bytes(self.data)
        (self.root / "u.bin").write_bytes(self.data)
        digest = hashlib.sha256(self.data).hexdigest()
        self.manifest = {"build_sha": "a" * 40, "session_id": "phone",
            "passes": [{"name": "pass0", "vulkan_sha256": digest,
            "unity_sha256": digest, "vulkan_bytes": 16, "unity_bytes": 16}]}
        self.paths = {"pass0": {"vulkan": "v.bin", "unity": "u.bin"}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_verified_hash_is_not_gpu_proof(self):
        result = verify_captures(self.manifest, self.paths, self.root)
        self.assertTrue(result["capture_hashes_verified"])
        self.assertFalse(result["gpu_execution_proven"])

    def test_tampered_capture_rejected(self):
        (self.root / "u.bin").write_bytes(b"\x01" * 16)
        with self.assertRaisesRegex(ValueError, "digest"):
            verify_captures(self.manifest, self.paths, self.root)

    def test_escape_rejected(self):
        self.paths["pass0"]["unity"] = "../outside"
        with self.assertRaisesRegex(ValueError, "unsafe"):
            verify_captures(self.manifest, self.paths, self.root)

    def test_missing_capture_rejected(self):
        (self.root / "u.bin").unlink()
        with self.assertRaises(FileNotFoundError):
            verify_captures(self.manifest, self.paths, self.root)

if __name__ == "__main__":
    unittest.main()
