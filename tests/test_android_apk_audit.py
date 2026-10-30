import tempfile
import struct
import unittest
from pathlib import Path
from zipfile import ZipFile

from scripts.audit_android_apk import audit


def elf(machine=183, elf_class=2, byte_order=1, kind=3):
    header = bytearray(64)
    header[:7] = b'\x7fELF' + bytes((elf_class, byte_order, 1))
    struct.pack_into('<HHI', header, 16, kind, machine, 1)
    struct.pack_into('<H', header, 52, 64)
    return bytes(header)


ARM64 = elf()
DEX = b"dex\n035\0" + b"\0" * 8
BASE = {
    "AndroidManifest.xml": b"\x03\x00\x08\x00" + b"\0" * 8,
    "classes.dex": DEX,
    "lib/arm64-v8a/libil2cpp.so": ARM64,
    "lib/arm64-v8a/libunity.so": ARM64,
    "assets/bin/Data/globalgamemanagers": b"UnityTestData",
}


def sample(path, *, exclude=(), extra=None):
    values = {key: val for key, val in BASE.items() if key not in exclude}
    values.update(extra or {})
    with ZipFile(path, "w") as archive:
        for key, value in values.items():
            archive.writestr(key, value)


class AndroidApkAuditTests(unittest.TestCase):
    def test_genuine_structure_counts_without_raw_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            apk = Path(temporary) / "test.apk"
            sample(apk, extra={"lib/arm64-v8a/libfmod.so": ARM64})
            result = audit(apk, min_size=0)
            self.assertEqual(result["abis"], ["arm64-v8a"])
            self.assertEqual(result["unity_data_files"], 1)
            self.assertTrue(result["fmod_native_library_present"])
            self.assertEqual(len(result["apk_sha256"]), 64)
            self.assertNotIn("UnityTestData", repr(result))
            self.assertEqual(result['validated_aarch64_shared_libraries'], 3)

    def test_reject_mislabeled_abi_and_invalid_optional_plugin(self):
        with tempfile.TemporaryDirectory() as temporary:
            apk = Path(temporary) / 'test.apk'
            for bad in (elf(machine=62), elf(elf_class=1), elf(byte_order=2),
                        elf(kind=2), ARM64[:16]):
                sample(apk, extra={'lib/arm64-v8a/libfmod.so': bad})
                with self.subTest(bad=bad[:20]), self.assertRaises(ValueError):
                    audit(apk, min_size=0, digest=False)

    def test_reject_missing_native_binary_or_game_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            apk = Path(temporary) / "test.apk"
            for excluded in ("lib/arm64-v8a/libil2cpp.so", "assets/bin/Data/globalgamemanagers"):
                sample(apk, exclude=(excluded,))
                with self.subTest(excluded=excluded), self.assertRaises(ValueError):
                    audit(apk, min_size=0, digest=False)

    def test_reject_invalid_arm64_elf_and_dex(self):
        with tempfile.TemporaryDirectory() as temporary:
            apk = Path(temporary) / "test.apk"
            for name, value in (("lib/arm64-v8a/libunity.so", b"NotELF"),
                                ("classes.dex", b"NotDEX")):
                sample(apk, extra={name: value})
                with self.subTest(name=name), self.assertRaises(ValueError):
                    audit(apk, min_size=0, digest=False)

    def test_reject_path_traversal(self):
        with tempfile.TemporaryDirectory() as temporary:
            apk = Path(temporary) / "test.apk"
            sample(apk, extra={"../outside": b"invalid"})
            with self.assertRaises(ValueError):
                audit(apk, min_size=0, digest=False)

    def test_nonexistent_or_tiny_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            apk = Path(temporary) / "test.apk"
            with self.assertRaises(FileNotFoundError):
                audit(apk)
            sample(apk)
            with self.assertRaises(ValueError):
                audit(apk)  # production-sized game check


if __name__ == "__main__":
    unittest.main()

