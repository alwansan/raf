"""Guard the shared T5 Android SAF adapter against reintroducing the old unbounded hash."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ACTIVITY = ROOT / "apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java"
STREAM = ROOT / "apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/StreamSha256.java"


class UnifiedSafStreamContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.activity = ACTIVITY.read_text(encoding="utf-8")
        cls.stream = STREAM.read_text(encoding="utf-8")
        cls.hash_file = cls.activity.split("    void hashFile(Uri input){", 1)[1].split(
            "    Uri writeMedia(", 1
        )[0]

    def test_uses_existing_tested_stream_not_second_unbounded_hasher(self):
        self.assertIn("StreamSha256.Result result=StreamSha256.digest(in,bytes->", self.hash_file)
        self.assertNotIn('MessageDigest.getInstance("SHA-256")', self.hash_file)
        self.assertIn("16L * 1024 * 1024 * 1024", self.stream)
        self.assertIn("consecutiveEmptyReads >= 16", self.stream)

    def test_long_size_and_real_progress_appear_as_evidence_only(self):
        self.assertIn('"bytes="+result.bytes+" sha256="+result.hex', self.hash_file)
        self.assertIn('"file_sha_start"', self.hash_file)
        self.assertIn("fileDigestBusy=true", self.hash_file)
        self.assertIn("if(fileDigestBusy)", self.hash_file)
        self.assertIn("runOnUiThread(()->show", self.hash_file)

    def test_broken_input_is_blocked_not_passed(self):
        self.assertIn('store(c,"EVIDENCE_READY",observed,null)', self.hash_file)
        self.assertIn('store(c,"BLOCKED","No digest: "+error,null)', self.hash_file)
        self.assertIn('show("SHA-256 failed; no file hash claimed:', self.hash_file)
        self.assertIn("fileDigestThread.interrupt()", self.activity)

    def test_pack_and_image_picker_reject_zero_progress(self):
        self.assertIn("if(++emptyReads>=16)", self.activity)
        self.assertIn("Pack provider returned repeated empty reads", self.activity)
        self.assertIn("Image provider returned repeated empty reads", self.activity)
        self.assertIn('throw new IOException("Pack over 256KiB")', self.activity)
        self.assertIn('throw new IOException("Image over 20MiB")', self.activity)


if __name__ == "__main__":
    unittest.main()
