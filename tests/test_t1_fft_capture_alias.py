"""Reject false Vulkan/Unity independence in private FFT capture verification."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from scripts.t1_fft_capture_integrity_gate import verify_captures


class CaptureAliasTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        payload = bytes(16)
        for name in ("vk.bin", "unity.bin"):
            (self.root / name).write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        self.manifest = {
            "build_sha": "a" * 40, "session_id": "t1-alias-test",
            "passes": [{
                "name": "fft0", "vulkan_sha256": digest, "unity_sha256": digest,
                "vulkan_bytes": 16, "unity_bytes": 16
            }]
        }

    def test_distinct_files_are_accepted_without_gpu_proof(self):
        result = verify_captures(self.manifest, {
            "fft0": {"vulkan": "vk.bin", "unity": "unity.bin"}}, self.root)
        self.assertTrue(result["capture_hashes_verified"])
        self.assertFalse(result["gpu_execution_proven"])

    def test_same_file_cannot_be_both_backends(self):
        with self.assertRaisesRegex(ValueError, "reused"):
            verify_captures(self.manifest, {
                "fft0": {"vulkan": "vk.bin", "unity": "vk.bin"}}, self.root)

    def test_hardlink_alias_cannot_be_both_backends(self):
        try:
            os.link(self.root / "vk.bin", self.root / "alias.bin")
        except OSError as exc:
            self.skipTest(f"hardlinks unavailable: {exc}")
        with self.assertRaisesRegex(ValueError, "reused"):
            verify_captures(self.manifest, {
                "fft0": {"vulkan": "vk.bin", "unity": "alias.bin"}}, self.root)


if __name__ == "__main__":
    unittest.main()
