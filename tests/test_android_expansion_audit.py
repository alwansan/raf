"""Synthetic APK/OBB validation without game assets or LFS."""
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from scripts.audit_android_expansion import audit_companion


def make(path, files):
    with ZipFile(path, "w") as archive:
        for name, value in files.items():
            archive.writestr(name, value)


class ExpansionAuditTests(unittest.TestCase):
    def test_requires_both_parts_and_original_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            with self.assertRaises(FileNotFoundError):
                audit_companion(apk, obb)
            make(obb, {"assets/bin/Data/level1": b"original", "assets/bin/Data/StreamingAssets/a.bank": b"bank"})
            result = audit_companion(apk, obb)
            self.assertEqual(result["obbUnityDataMembers"], 2)
            self.assertTrue(result["companionRequired"])
            self.assertEqual(len(result["obbSha256"]), 64)
            self.assertNotIn("original", str(result))
            self.assertFalse(result["deviceMountedVerified"])

    def test_rejects_missing_original_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            make(obb, {"metadata": b"no data"})
            with self.assertRaises(ValueError):
                audit_companion(apk, obb, digest=False)

    def test_identity_mismatch_and_matching_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first", "assets/unity_obb_guid": b"A"})
            make(obb, {"assets/bin/Data/level1": b"data", "assets/unity_obb_guid": b"B"})
            with self.assertRaises(ValueError):
                audit_companion(apk, obb, digest=False)
            make(obb, {"assets/bin/Data/level1": b"data", "assets/unity_obb_guid": b"A"})
            self.assertEqual(audit_companion(apk, obb, digest=False)["expansionIdentityCheck"], "verified")

    def test_rejects_unsafe_obb_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            make(obb, {"assets/bin/Data/level1": b"data", "../outside": b"unsafe"})
            with self.assertRaises(ValueError):
                audit_companion(apk, obb, digest=False)


if __name__ == "__main__":
    unittest.main()
