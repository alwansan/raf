"""Source-free adversarial fixture controls for exact signed APK+OBB selection."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile
from unittest.mock import patch
import errno

from scripts.t5_extract_actual_signed_pair import extract_pair, PACKAGE, APK, XAPK

VERSION = "89"
OBB = "main." + VERSION + "." + PACKAGE + ".obb"


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def row(name, parts):
    whole = b"".join(body for _, body in parts)
    return {"name": name, "bytes": len(whole), "sha256": sha(whole),
            "parts": [{"name": n, "bytes": len(body), "sha256": sha(body)}
                      for n, body in parts]}


class ActualPairExtractionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "delivery.zip"
        self.target = self.root / "extracted"
        self.blobs = {APK: b"synthetic-apk-content-only", OBB+".part001": b"synthetic-obb-A",
                      OBB+".part002": b"synthetic-obb-B", XAPK: b"synthetic-xapk"}
        self.records = [
            row(APK, [(APK, self.blobs[APK])]),
            row(OBB, [(OBB+".part001", self.blobs[OBB+".part001"]),
                      (OBB+".part002", self.blobs[OBB+".part002"])]),
            row(XAPK, [(XAPK, self.blobs[XAPK])]),
        ]
        self.meta = {"schema": 1, "package": PACKAGE, "version_code": VERSION,
                     "companion_required": True, "transport_only_parts": True,
                     "device_install_verified": False, "files": self.records}
        self.extra = {}
        self.pack()

    def pack(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.source, "w") as zipout:
                zipout.writestr("delivery.json", json.dumps(self.meta))
                zipout.writestr("SHA256SUMS", "fixture-hash-list")
                for name, blob in self.blobs.items():
                    zipout.writestr(name, blob)
                for name, blob in self.extra.items():
                    zipout.writestr(name, blob)

    def call(self, **kwargs):
        vals = {"expected_bytes": self.source.stat().st_size,
                "expected_sha": sha(self.source.read_bytes()),
                "expected_version": VERSION}
        vals.update(kwargs)
        return extract_pair(self.source, self.target, **vals)

    def rejected(self, phrase):
        with self.assertRaisesRegex(ValueError, phrase):
            self.call()

    def test_valid_actual_source_bytes_and_two_outputs(self):
        report = self.call()
        self.assertEqual(report["signed_pair_files_materialized"], 2)
        self.assertEqual((self.target / APK).read_bytes(), self.blobs[APK])
        self.assertEqual((self.target / OBB).read_bytes(),
                         self.blobs[OBB+".part001"]+self.blobs[OBB+".part002"])
        self.assertEqual(json.loads((self.target/"delivery.json").read_text()), self.meta)
        self.assertFalse(report["apk_signature_verified"])
        self.assertFalse(report["obb_guid_validated"])
        self.assertFalse((self.target / XAPK).exists())

    def test_android_without_os_link_copies_exclusively(self):
        with patch("scripts.t5_extract_actual_signed_pair.os.link",
                   side_effect=AttributeError("os.link unavailable")):
            report = self.call()
        self.assertTrue(report["signed_apk_and_obb_sha256_verified"])
        self.assertEqual((self.target / APK).read_bytes(), self.blobs[APK])
        self.assertEqual((self.target / OBB).read_bytes(),
                         self.blobs[OBB+".part001"] + self.blobs[OBB+".part002"])
        self.assertFalse((self.target / (APK+".staging")).exists())

    def test_android_unsupported_hardlinks_copy_exclusively(self):
        with patch("scripts.t5_extract_actual_signed_pair.os.link",
                   side_effect=OSError(errno.EOPNOTSUPP, "no hardlinks")):
            self.call()
        self.assertEqual((self.target / APK).read_bytes(), self.blobs[APK])

    def test_unexpected_hardlink_error_fails_closed_and_cleans(self):
        with patch("scripts.t5_extract_actual_signed_pair.os.link",
                   side_effect=OSError(errno.EIO, "storage failure")):
            with self.assertRaises(OSError):
                self.call()
        self.assertFalse(self.target.exists())

    def test_wrong_zip_sha_refused_before_writing(self):
        with self.assertRaisesRegex(ValueError, "ZIP SHA256 mismatch"):
            self.call(expected_sha="0"*64)
        self.assertFalse(self.target.exists())

    def test_wrong_zip_bytes_refused(self):
        with self.assertRaisesRegex(ValueError, "size/path mismatch"):
            self.call(expected_bytes=self.source.stat().st_size+1)
        self.assertFalse(self.target.exists())

    def test_symlink_zip_rejected(self):
        original = self.root / "real.zip"
        self.source.rename(original)
        try:
            self.source.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        with self.assertRaisesRegex(ValueError, "size/path mismatch"):
            self.call()

    def test_existing_output_dir_is_preserved(self):
        self.target.mkdir()
        (self.target / "keep").write_text("user-data")
        self.rejected("overwrite existing extraction")
        self.assertEqual((self.target/"keep").read_text(), "user-data")

    def test_existing_target_symlink_is_preserved(self):
        outside = self.root / "outside"
        outside.mkdir()
        try:
            self.target.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        self.rejected("overwrite existing extraction")
        self.assertTrue(self.target.is_symlink())

    def test_wrong_package_refused(self):
        self.meta["package"] = "com.other.game"
        self.pack()
        self.rejected("identity mismatch")
        self.assertFalse(self.target.exists())

    def test_wrong_version_refused(self):
        self.meta["version_code"] = "90"
        self.pack()
        self.rejected("identity mismatch")

    def test_missing_last_obb_part_no_output(self):
        self.blobs.pop(OBB+".part002")
        self.pack()
        self.rejected("Missing actual signed transport")
        self.assertFalse(self.target.exists())

    def test_same_size_corruption_of_second_obb_part_cleanup(self):
        body = self.blobs[OBB+".part002"]
        self.blobs[OBB+".part002"] = body[:-1] + bytes([body[-1] ^ 1])
        self.pack()
        self.rejected("Actual native transport part SHA")
        self.assertFalse(self.target.exists())

    def test_declared_apk_full_digest_mismatch(self):
        self.records[0]["sha256"] = "f"*64
        self.pack()
        self.rejected("Actual complete native file SHA")
        self.assertFalse(self.target.exists())

    def test_wrong_obb_part_number(self):
        self.records[1]["parts"][1]["name"] = OBB+".part003"
        self.pack()
        self.rejected("Transport part identity")
        self.assertFalse(self.target.exists())

    def test_malformed_logical_order(self):
        self.records[0], self.records[1] = self.records[1], self.records[0]
        self.pack()
        self.rejected("Logical output name")

    def test_zip_member_traversal(self):
        self.extra["../outside"] = b"x"
        self.pack()
        self.rejected("Delivery ZIP paths unsafe")
        self.assertFalse(self.target.exists())

    def test_duplicate_member_name(self):
        self.extra[APK] = b"different"
        self.pack()
        self.rejected("duplicate names")

    def test_invalid_companion_flag(self):
        self.meta["companion_required"] = False
        self.pack()
        self.rejected("identity mismatch")

    def test_true_boolean_rejected_as_length(self):
        self.records[0]["bytes"] = True
        self.pack()
        self.rejected("Logical output name")


if __name__ == "__main__":
    unittest.main()
