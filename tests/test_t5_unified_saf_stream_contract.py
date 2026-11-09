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
        self.assertIn('show("فشل حساب SHA256؛ لا يمكن اعتماد بصمة غير مكتملة: "+error)', self.hash_file)
        self.assertIn("fileDigestThread.interrupt()", self.activity)

    def test_pack_and_image_picker_reject_zero_progress(self):
        self.assertIn("if(++emptyReads>=16)", self.activity)
        self.assertIn("Pack provider returned repeated empty reads", self.activity)
        self.assertIn("Image provider returned repeated empty reads", self.activity)
        self.assertIn('throw new IOException("Pack over 256KiB")', self.activity)
        self.assertIn('throw new IOException("Image over 20MiB")', self.activity)


    def test_media_store_file_is_private_until_full_write_finishes(self):
        # The new image/log is not made public before the stream is closed.
        method = self.activity.split("    Uri writeMedia(", 1)[1].split(
            "    void log(", 1
        )[0]
        self.assertIn("if(Build.VERSION.SDK_INT<29)", method)
        self.assertIn("v.put(MediaStore.MediaColumns.IS_PENDING,1)", method)
        self.assertIn('openOutputStream(uri,"wt")', method)
        self.assertIn("out.write(bytes);out.flush()", method)
        self.assertIn("ready.put(MediaStore.MediaColumns.IS_PENDING,0)", method)
        self.assertLess(method.index("IS_PENDING,1"), method.index("insert("))
        self.assertLess(method.index("out.write(bytes);out.flush()"),
                        method.index("IS_PENDING,0"))
        self.assertLess(method.index("IS_PENDING,0"), method.index("update(uri,ready"))

    def test_media_store_failure_rolls_back_incomplete_media(self):
        method = self.activity.split("    Uri writeMedia(", 1)[1].split(
            "    void log(", 1
        )[0]
        self.assertIn("boolean published=false", method)
        self.assertIn('throw new IOException("MediaStore failed to publish completed file")', method)
        self.assertIn("if(getContentResolver().update(uri,ready,null,null)!=1)", method)
        self.assertIn("published=true", method)
        self.assertIn("finally{", method)
        self.assertIn("if(!published)", method)
        self.assertIn("getContentResolver().delete(uri,null,null)", method)
        self.assertLess(method.index("update(uri,ready"), method.index("published=true"))
        self.assertLess(method.index("published=true"), method.index("return uri;"))


if __name__ == "__main__":
    unittest.main()
