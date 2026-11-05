"""Synthetic, source-free negative controls for immutable native delivery archive."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

from scripts.t5_verify_retained_delivery_archive import (
    verify_archive, PACKAGE, APK, XAPK,
)

VERSION = "89"
OBB = "main.89." + PACKAGE + ".obb"


def digest(content):
    return hashlib.sha256(content).hexdigest()


def record(name, parts):
    data = b"".join(blob for _, blob in parts)
    return {"name": name, "bytes": len(data), "sha256": digest(data),
            "parts": [{"name": n, "bytes": len(blob), "sha256": digest(blob)}
                      for n, blob in parts]}


class RetainedDeliveryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "source-free-native-delivery.zip"
        self.files = {
            APK: b"fixture-apk-only",
            OBB: b"fixture-obb-only",
            XAPK + ".part001": b"fixture-xapk-part-one",
            XAPK + ".part002": b"fixture-xapk-part-two",
        }
        self.rows = [
            record(APK, [(APK, self.files[APK])]),
            record(OBB, [(OBB, self.files[OBB])]),
            record(XAPK, [(XAPK + ".part001", self.files[XAPK + ".part001"]),
                          (XAPK + ".part002", self.files[XAPK + ".part002"])]),
        ]
        self.delivery = {
            "schema": 1, "package": PACKAGE, "version_code": VERSION,
            "companion_required": True, "transport_only_parts": True,
            "device_install_verified": False, "files": self.rows,
        }
        self.extra = {}
        self.sums_override = None
        self.regenerate()

    def regenerate(self):
        sums = "".join(p["sha256"] + "  " + p["name"] + "\n"
                       for row in self.rows for p in row["parts"])
        if self.sums_override is not None:
            sums = self.sums_override
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_STORED) as z:
                z.writestr("delivery.json", json.dumps(self.delivery))
                z.writestr("SHA256SUMS", sums)
                z.writestr("reassemble.py", "safe fixture")
                z.writestr("INSTALL_AR.md", "synthetic fixture only")
                for name, blob in self.files.items():
                    z.writestr(name, blob)
                for name, blob in self.extra.items():
                    z.writestr(name, blob)

    def verify(self, **kw):
        kwargs = {
            "expected_size": self.path.stat().st_size,
            "expected_sha": digest(self.path.read_bytes()),
            "expected_version": VERSION,
        }
        kwargs.update(kw)
        return verify_archive(self.path, **kwargs)

    def reject(self, message=None):
        with self.assertRaises(ValueError) as err:
            self.verify()
        if message:
            self.assertIn(message, str(err.exception))

    def test_success_three_original_logical_records_four_actual_parts(self):
        result = self.verify()
        self.assertEqual(result["actual_transport_part_hashes_verified"], 4)
        self.assertEqual(result["logical_file_whole_hashes_verified"], 3)
        self.assertFalse(result["apk_signature_verified"])
        self.assertFalse(result["unity_obb_internal_guid_verified"])

    def test_wrong_expected_archive_digest(self):
        with self.assertRaisesRegex(ValueError, "Actions archive SHA256"):
            self.verify(expected_sha="0" * 64)

    def test_wrong_expected_archive_size(self):
        with self.assertRaisesRegex(ValueError, "byte size differs"):
            self.verify(expected_size=self.path.stat().st_size + 1)

    def test_original_version_identity_drift(self):
        self.delivery["version_code"] = "90"
        self.regenerate()
        self.reject("package/version contract")

    def test_package_identity_drift(self):
        self.delivery["package"] = "org.other.game"
        self.regenerate()
        self.reject("package/version contract")

    def test_same_size_part_corruption(self):
        old = self.files[OBB]
        self.files[OBB] = old[:-1] + bytes([old[-1] ^ 1])
        self.regenerate()
        self.reject("Actual part bytes disagree")

    def test_declared_part_digest_changed(self):
        self.rows[0]["parts"][0]["sha256"] = "e" * 64
        self.regenerate()
        self.reject("Actual part bytes disagree")

    def test_declared_whole_digest_changed(self):
        self.rows[2]["sha256"] = "f" * 64
        self.regenerate()
        self.reject("Reconstructed logical output")

    def test_wrong_transport_size_sum(self):
        self.rows[1]["bytes"] += 1
        self.regenerate()
        self.reject("Reconstructed logical output")

    def test_missing_actual_part(self):
        self.files.pop(XAPK + ".part002")
        self.regenerate()
        self.reject("Missing or wrong-size actual ZIP part")

    def test_wrong_part_number(self):
        self.rows[2]["parts"][1]["name"] = XAPK + ".part003"
        self.regenerate()
        self.reject("Part order")

    def test_rogue_extra_member(self):
        self.extra["unknown.bin"] = b"not requested"
        self.regenerate()
        self.reject("Unexpected or missing payload")

    def test_traversal_member_name(self):
        self.extra["../outside"] = b"unsafe"
        self.regenerate()
        self.reject("Archive member count, duplicate or path unsafe")

    def test_duplicate_zip_member(self):
        self.extra[APK] = b"overlapping filename"
        self.regenerate()
        self.reject("Archive member count, duplicate or path unsafe")

    def test_sha256sums_mismatch(self):
        self.sums_override = "0" * 64 + "  " + APK + "\n"
        self.regenerate()
        self.reject("SHA256SUMS disagrees")

    def test_false_companion_claim(self):
        self.delivery["companion_required"] = False
        self.regenerate()
        self.reject("package/version contract")

    def test_invalid_zip_archive(self):
        self.path.write_bytes(b"not-a-zip")
        with self.assertRaises(zipfile.BadZipFile):
            self.verify()

    def test_malformed_metadata_json(self):
        self.delivery = ["not-object"]
        self.regenerate()
        self.reject("Invalid delivery")


if __name__ == "__main__":
    unittest.main()
