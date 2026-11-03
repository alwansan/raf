"""A8: synthetic-only ZIP2 original-save source-authentication negative controls."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.verify_a8_zip2_local_save_provider import (
    HEADER, ORIGINALS, ZIP2_COMMIT, verify,
)

DLL = "Raft_Data/Managed/Assembly-CSharp.dll"
RGD = "Raft_Data/StreamingAssets/Data.rgd"


class Zip2LocalOriginalVerificationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="a8-zip2-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "zip2"
        (self.root / "Raft").mkdir(parents=True)
        self.payloads = {DLL: b"synthetic managed test only", RGD: b"\x00RGD-not-original"}
        self.pins = {name: (len(content), hashlib.sha256(content).hexdigest())
                     for name, content in self.payloads.items()}
        for name, data in self.payloads.items():
            path = self.root / "Raft" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.write_manifest()

    def write_manifest(self, *, kind="plain", wrong_sha=None, duplicate=False):
        lines = ["\t".join(HEADER)]
        for name, (size, sha) in self.pins.items():
            lines.append("\t".join(
                (kind, str(size), wrong_sha if name == DLL and wrong_sha else sha, "660", name)))
        if duplicate:
            lines.append(lines[-1])
        (self.root / "RAFT_FILE_MANIFEST.tsv").write_text("\n".join(lines) + "\n")

    def check(self):
        return verify(self.root, pins=self.pins)

    def test_positive_two_originals_exact_bytes_and_no_mutation(self):
        before = {p: (self.root / "Raft" / p).read_bytes() for p in self.pins}
        report = self.check()
        self.assertEqual(report["verified_original_count"], 2)
        self.assertEqual(report["verified_total_bytes"], sum(map(len, before.values())))
        self.assertFalse(report["original_data_modified"])
        self.assertFalse(report["unity_or_android_executed"])
        self.assertFalse(report["user_save_roundtrip_verified"])
        for name, original in before.items():
            self.assertEqual((self.root / "Raft" / name).read_bytes(), original)
            self.assertEqual(report["originals"][name]["sha256"], self.pins[name][1])

    def test_wrong_manifest_sha_rejected_even_if_payload_is_real(self):
        self.write_manifest(wrong_sha="0" * 64)
        with self.assertRaisesRegex(ValueError, "manifest conflicts"):
            self.check()

    def test_one_byte_changed_without_length_change_rejected(self):
        source = self.root / "Raft" / DLL
        data = source.read_bytes()
        source.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        with self.assertRaisesRegex(ValueError, "SHA256"):
            self.check()

    def test_shorter_original_and_missing_input_rejected(self):
        source = self.root / "Raft" / RGD
        source.write_bytes(b"x")
        with self.assertRaisesRegex(ValueError, "wrong-sized"):
            self.check()
        source.unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            self.check()

    def test_manifest_duplicates_and_nonplain_entry_rejected(self):
        self.write_manifest(duplicate=True)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.check()
        self.write_manifest(kind="split")
        with self.assertRaisesRegex(ValueError, "manifest conflicts"):
            self.check()

    def test_invalid_schema_and_missing_manifest_rejected(self):
        manifest = self.root / "RAFT_FILE_MANIFEST.tsv"
        manifest.write_text("not\toriginal\n")
        with self.assertRaisesRegex(ValueError, "schema"):
            self.check()
        manifest.unlink()
        with self.assertRaisesRegex(ValueError, "manifest"):
            self.check()

    def test_symlink_source_file_rejected(self):
        source = self.root / "Raft" / RGD
        source.unlink()
        source.symlink_to(self.root / "Raft" / DLL)
        with self.assertRaisesRegex(ValueError, "linked"):
            self.check()

    def test_symlink_source_parent_rejected(self):
        outside = Path(self.root.parent) / "outside"
        outside.mkdir()
        original = self.root / "Raft" / "Raft_Data" / "StreamingAssets" / "Data.rgd"
        data = original.read_bytes()
        original.unlink()
        original.parent.rmdir()
        (outside / "Data.rgd").write_bytes(data)
        original.parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "linked"):
            self.check()

    def test_symlink_manifest_and_checkout_rejected(self):
        manifest = self.root / "RAFT_FILE_MANIFEST.tsv"
        backup = self.root.parent / "backup.tsv"
        backup.write_bytes(manifest.read_bytes())
        manifest.unlink()
        manifest.symlink_to(backup)
        with self.assertRaisesRegex(ValueError, "manifest"):
            self.check()
        with self.assertRaisesRegex(ValueError, "checkout"):
            verify(self.root.parent / "absent", pins=self.pins)

    def test_oversized_manifest_and_bad_independent_pins_rejected(self):
        (self.root / "RAFT_FILE_MANIFEST.tsv").write_bytes(b"x" * (1024 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "manifest"):
            self.check()
        for pin in ({DLL: (1, "not-a-hash")}, {DLL: (-1, "0"*64)},
                    {"../escape": (1, "0"*64)}, {}):
            with self.subTest(pin=pin):
                with self.assertRaisesRegex(ValueError, "pin"):
                    verify(self.root, pins=pin)

    def test_independent_source_constants_are_not_manifest_controlled(self):
        self.assertEqual(ZIP2_COMMIT, "15964ea8f246b6e076ce26b60931ee2e1a9a2385")
        self.assertEqual(ORIGINALS[DLL],
                         (3211776, "0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e"))
        self.assertEqual(ORIGINALS[RGD],
                         (2941, "b2785187aa11e33872698adfa79ab252cf65a824d92bee7e88773ce4aa11cbba"))


if __name__ == "__main__":
    unittest.main()
