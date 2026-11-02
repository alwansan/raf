"""Synthetic APK/OBB validation without game assets or LFS."""
from pathlib import Path
import tempfile
import struct
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
            make(obb, {"assets/bin/Data/level1": b"original-scene-data", "assets/bin/Data/StreamingAssets/a.bank": b"bank"})
            result = audit_companion(apk, obb)
            self.assertEqual(result["obbUnityDataMembers"], 2)
            self.assertTrue(result["companionRequired"])
            self.assertEqual(len(result["obbSha256"]), 64)
            self.assertNotIn("original-scene-data", str(result))
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

    def test_reports_obb_size_and_member_limits_without_asset_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            make(obb, {"assets/bin/Data/level1": b"original-scene-data",
                       "assets/bin/Data/StreamingAssets/a.bank": b"bank"})
            normal = audit_companion(apk, obb, digest=False)
            self.assertFalse(normal["obbPlayLimitExceeded"])
            self.assertEqual(normal["obbPlayLimitBytes"], 2_000_000_000)
            self.assertEqual(normal["obbUnityLargestMemberBytes"], len(b"original-scene-data"))
            self.assertEqual(normal["obbUnityCompressedBytes"], len(b"original-scene-data") + len(b"bank"))
            self.assertEqual(normal["obbUnityMembersOverJavaArray"], 0)
            constrained = audit_companion(apk, obb, digest=False,
                                          play_limit_bytes=obb.stat().st_size - 1,
                                          java_array_limit_bytes=4)
            self.assertTrue(constrained["obbPlayLimitExceeded"])
            self.assertEqual(constrained["obbUnityMembersOverJavaArray"], 1)
            self.assertNotIn("level1", str(constrained))
            self.assertNotIn("a.bank", str(constrained))

    def test_crc_checks_detect_modified_payload_without_leaking_member_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"initial-scene"})
            make(obb, {"assets/bin/Data/level1": b"original-data"})
            self.assertTrue(audit_companion(apk, obb, digest=False,
                                            verify_crc=True)["zipCrcVerified"])
            self.assertFalse(audit_companion(apk, obb, digest=False)["zipCrcVerified"])

            def damage(path):
                with ZipFile(path) as archive:
                    item = archive.infolist()[0]
                with path.open("r+b") as stream:
                    stream.seek(item.header_offset + 26)
                    name_len, extra_len = struct.unpack("<HH", stream.read(4))
                    stream.seek(item.header_offset + 30 + name_len + extra_len)
                    first = stream.read(1)
                    self.assertTrue(first)
                    stream.seek(-1, 1)
                    stream.write(bytes([first[0] ^ 1]))

            damage(obb)
            with self.assertRaisesRegex(ValueError, "CRC") as caught:
                audit_companion(apk, obb, digest=False, verify_crc=True)
            self.assertNotIn("level1", str(caught.exception))
            make(obb, {"assets/bin/Data/level1": b"original-data"})
            damage(apk)
            with self.assertRaisesRegex(ValueError, "CRC") as caught:
                audit_companion(apk, obb, digest=False, verify_crc=True)
            self.assertNotIn("first", str(caught.exception))

    def test_reports_lossless_compression_feasibility_without_claiming_compatibility(self):
        from zipfile import ZIP_DEFLATED
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            with ZipFile(obb, "w", compression=ZIP_DEFLATED) as archive:
                archive.writestr("assets/bin/Data/level1", b"x" * 4096)
            report = audit_companion(apk, obb, digest=False)
            self.assertEqual(report["obbUnityStoredMembers"], 0)
            self.assertEqual(report["obbUnityDeflatedMembers"], 1)
            self.assertEqual(report["obbUnityStoredBytes"], 0)
            self.assertGreater(report["obbZipContainerOverheadBytes"], 0)
            self.assertEqual(report["obbPlayExcessBytes"], 0)

    def test_rejects_unsafe_obb_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            make(obb, {"assets/bin/Data/level1": b"data", "../outside": b"unsafe"})
            with self.assertRaises(ValueError):
                audit_companion(apk, obb, digest=False)


if __name__ == "__main__":
    unittest.main()
