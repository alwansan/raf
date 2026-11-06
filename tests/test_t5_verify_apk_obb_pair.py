"""Source-free adversarial checks for completed Raft APK+OBB pairing."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import warnings
import zipfile

from scripts.t5_verify_apk_obb_pair import APK_NAME, PACKAGE, XAPK_NAME, verify_pair

VERSION = "86"
OBB_NAME = "main." + VERSION + "." + PACKAGE + ".obb"
AAPT = "package: name='" + PACKAGE + "' versionCode='86' versionName='1.1.01'\n"


def fake_elf():
    header = bytearray(64)
    header[:7] = b"\x7fELF\x02\x01\x01"
    struct.pack_into("<HHI", header, 16, 3, 183, 1)
    struct.pack_into("<H", header, 52, 64)
    return bytes(header)


def row(name, content):
    digest = hashlib.sha256(content).hexdigest()
    return {"name": name, "bytes": len(content), "sha256": digest,
            "parts": [{"name": name, "bytes": len(content), "sha256": digest}]}


class PairTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.apk = self.root / APK_NAME
        self.obb = self.root / OBB_NAME
        self.delivery = self.root / "delivery.json"
        self.make_apk()
        self.make_obb()
        self.write_manifest()

    def make_apk(self):
        with zipfile.ZipFile(self.apk, "w") as archive:
            archive.writestr("AndroidManifest.xml", b"binary-manifest-fixture")
            archive.writestr("classes.dex", b"dex\n035\x00fixture")
            archive.writestr("lib/arm64-v8a/libil2cpp.so", fake_elf())
            archive.writestr("lib/arm64-v8a/libunity.so", fake_elf())
            archive.writestr("assets/bin/Data/globalgamemanagers", b"synthetic-unity")

    def make_obb(self, entries=None):
        if entries is None:
            entries = [("assets/bin/Data/resources.assets", b"synthetic-obb")]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(self.obb, "w") as archive:
                for name, value in entries:
                    archive.writestr(name, value)

    def write_manifest(self, modify=None):
        data = {"schema": 1, "package": PACKAGE, "version_code": VERSION,
                "companion_required": True, "transport_only_parts": True,
                "device_install_verified": False,
                "files": [row(self.apk.name, self.apk.read_bytes()),
                          row(self.obb.name, self.obb.read_bytes()),
                          row(XAPK_NAME, b"synthetic-xapk-declaration")]}
        if modify:
            modify(data)
        self.delivery.write_text(json.dumps(data), encoding="utf8")
        return data

    def check(self, badging=AAPT):
        return verify_pair(self.delivery, self.apk, self.obb, badging)

    def rejected(self, message):
        with self.assertRaisesRegex(ValueError, message):
            self.check()

    def test_valid_synthetic_pair(self):
        result = self.check()
        self.assertTrue(result["aapt_apk_package_version_match"])
        self.assertTrue(result["completed_apk_and_obb_sha256_match_local_delivery_manifest"])
        self.assertFalse(result["unity_obb_internal_guid_checked"])
        self.assertFalse(result["delivery_manifest_authenticated"])
        self.assertFalse(result["apk_crypto_signature_checked"])

    def test_badging_wrong_package(self):
        with self.assertRaisesRegex(ValueError, "aapt APK identity"):
            self.check(AAPT.replace(PACKAGE, "com.invalid.game"))

    def test_badging_wrong_version(self):
        with self.assertRaisesRegex(ValueError, "aapt APK identity"):
            self.check(AAPT.replace("versionCode='86'", "versionCode='87'"))

    def test_changed_apk_rejected(self):
        with self.apk.open("ab") as stream:
            stream.write(b"x")
        self.rejected("Completed APK size/SHA256")

    def test_same_size_obb_corruption(self):
        data = self.obb.read_bytes()
        self.obb.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
        self.rejected("Completed OBB size/SHA256")

    def test_wrong_obb_name(self):
        wrong = self.root / ("main.87." + PACKAGE + ".obb")
        self.obb.rename(wrong)
        with self.assertRaisesRegex(ValueError, "OBB filename"):
            verify_pair(self.delivery, self.apk, wrong, AAPT)

    def test_bad_manifest_package(self):
        self.write_manifest(lambda d: d.update(package="com.fake"))
        self.rejected("Delivery package/version")

    def test_bad_manifest_version(self):
        self.write_manifest(lambda d: d.update(version_code="../86"))
        self.rejected("Delivery package/version")

    def test_duplicate_logical_names(self):
        self.write_manifest(lambda d: d["files"].__setitem__(2, copy.deepcopy(d["files"][0])))
        self.rejected("repeated logical")

    def test_inaccurate_transport_bytes(self):
        self.write_manifest(lambda d: d["files"][1]["parts"][0].update(bytes=2))
        self.rejected("Transport sizes")

    def test_apk_core_missing_even_when_hash_matches(self):
        with zipfile.ZipFile(self.apk, "w") as archive:
            archive.writestr("AndroidManifest.xml", b"x")
            archive.writestr("assets/bin/Data/resource", b"something")
        self.write_manifest()
        self.rejected("APK has no complete")

    def test_bad_obb_zip_even_when_hash_matches(self):
        self.obb.write_bytes(b"not-a-zip")
        self.write_manifest()
        self.rejected("ZIP structure invalid")

    def test_obb_path_traversal(self):
        self.make_obb([("../outside", b"x"), ("assets/valid", b"x")])
        self.write_manifest()
        self.rejected("Unsafe or duplicate")

    def test_obb_repeated_separator_rejected_even_with_matching_hash(self):
        self.make_obb([("assets//unexpected", b"x"), ("assets/valid", b"x")])
        self.write_manifest()
        self.rejected("Unsafe or duplicate")

    def test_obb_dot_segment_rejected_even_with_matching_hash(self):
        self.make_obb([("assets/./unexpected", b"x"), ("assets/valid", b"x")])
        self.write_manifest()
        self.rejected("Unsafe or duplicate")

    def test_apk_unix_symlink_entry_rejected(self):
        with zipfile.ZipFile(self.apk, "a") as archive:
            link = zipfile.ZipInfo("assets/bin/Data/synthetic-link")
            link.create_system = 3
            link.external_attr = (0o120777 << 16)
            archive.writestr(link, b"assets/bin/Data/globalgamemanagers")
        self.write_manifest()
        self.rejected("symbolic link")

    def test_apk_encrypted_flag_rejected(self):
        payload = bytearray(self.apk.read_bytes())
        # Mutate one local and its matching central directory header.
        for signature, offset in ((b"PK\\x03\\x04", 6), (b"PK\\x01\\x02", 8)):
            pos = payload.find(signature)
            self.assertGreaterEqual(pos, 0)
            flags = struct.unpack_from("<H", payload, pos + offset)[0]
            struct.pack_into("<H", payload, pos + offset, flags | 1)
        self.apk.write_bytes(payload)
        self.write_manifest()
        self.rejected("Encrypted ZIP member")

    def test_obb_unix_symlink_entry_rejected(self):
        with zipfile.ZipFile(self.obb, "w") as archive:
            link = zipfile.ZipInfo("assets/link")
            link.create_system = 3
            link.external_attr = (0o120777 << 16)
            archive.writestr(link, b"assets/target")
            archive.writestr("assets/target", b"synthetic-asset")
        self.write_manifest()
        self.rejected("symbolic link")

    def test_obb_encrypted_flag_rejected(self):
        # A synthetic flagged member suffices: no encryption keys or game data.
        payload = bytearray(self.obb.read_bytes())
        for signature, offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
            pos = payload.find(signature)
            self.assertGreaterEqual(pos, 0)
            flags = struct.unpack_from("<H", payload, pos + offset)[0]
            struct.pack_into("<H", payload, pos + offset, flags | 1)
        self.obb.write_bytes(payload)
        self.write_manifest()
        self.rejected("Encrypted ZIP member")

    def test_obb_duplicate_entries(self):
        self.make_obb([("assets/entry", b"x"), ("assets/entry", b"y")])
        self.write_manifest()
        self.rejected("Unsafe or duplicate")

    def test_empty_obb_data(self):
        self.make_obb([("not-assets", b"x")])
        self.write_manifest()
        self.rejected("No populated Unity")

    def test_apk_symlink(self):
        original = self.root / "actual.apk"
        self.apk.rename(original)
        try:
            self.apk.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("filesystem does not support links")
        self.rejected("linked input")

    def test_manifest_symlink(self):
        original = self.root / "actual.json"
        self.delivery.rename(original)
        try:
            self.delivery.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("filesystem does not support links")
        self.rejected("linked input")


if __name__ == "__main__":
    unittest.main()
