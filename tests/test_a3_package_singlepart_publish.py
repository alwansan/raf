"""A3 DELIVERY-014: single-part Android delivery publication no-clobber controls.

Only synthetic file bytes. This runs the real production PartsWriter; it never
builds, signs, copies or uploads proprietary APK/OBB/XAPK files.
"""
import errno
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.package_android_delivery import PartsWriter


class A3SinglePartPublicationTests(unittest.TestCase):
    def test_single_part_roundtrip_without_extra_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name = "Raft-Android-Test.apk"
            payload = b"FAKE-APK-ONLY-" * 23
            sink = PartsWriter(root, name, limit=4096)
            sink.write(payload)
            record = sink.finish()
            self.assertEqual((root / name).read_bytes(), payload)
            self.assertFalse((root / (name + ".part001")).exists())
            self.assertEqual(record["parts"], [{
                "name": name, "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest()}])
            self.assertEqual(record["sha256"], hashlib.sha256(payload).hexdigest())

    def test_competing_single_part_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name = "Raft-Android-Test.xapk"
            original = b"FAKE-XAPK-UNPUBLISHED-" * 8
            competitor = b"OTHER-ALREADY-PUBLISHED-SIGNED-DELIVERY"
            sink = PartsWriter(root, name, limit=4096)
            sink.write(original)
            (root / name).write_bytes(competitor)
            # The old Path.rename silently replaces competitor on POSIX.
            with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
                sink.finish()
            self.assertEqual((root / name).read_bytes(), competitor)
            self.assertEqual((root / (name + ".part001")).read_bytes(), original)

    def test_single_part_hardlink_denial_never_publishes_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name = "Raft-Android-Test.apk"
            original = b"FAKE-APK-DATA" * 11
            sink = PartsWriter(root, name, limit=4096)
            sink.write(original)
            with patch("scripts.package_android_delivery.os.link",
                       side_effect=OSError(errno.EPERM, "hardlink denied")):
                with self.assertRaisesRegex(OSError, "hard-link"):
                    sink.finish()
            self.assertFalse((root / name).exists())
            self.assertEqual((root / (name + ".part001")).read_bytes(), original)

    def test_multi_part_files_remain_unmodified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name = "Raft-Android-Test.xapk"
            payload = b"12345678"
            sink = PartsWriter(root, name, limit=3)
            sink.write(payload)
            record = sink.finish()
            self.assertEqual([r["name"] for r in record["parts"]],
                             [name + ".part001", name + ".part002", name + ".part003"])
            self.assertEqual(b"".join((root / r["name"]).read_bytes()
                                      for r in record["parts"]), payload)
            self.assertFalse((root / name).exists())


if __name__ == "__main__":
    unittest.main()
