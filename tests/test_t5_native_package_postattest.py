"""Source-only native delivery gate contract; no proprietary APK, OBB or Unity."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

from scripts.package_android_delivery import PACKAGE, PartsWriter, package, parse_badging


class NativeDeliveryPostAttestationTests(unittest.TestCase):
    def _inputs(self, base: Path):
        apk, obb = base / "synthetic-signed-placeholder.apk", base / "synthetic-native.obb"
        with zipfile.ZipFile(apk, "w", compression=zipfile.ZIP_STORED) as out:
            out.writestr("classes.dex", b"dex\n035\0" + b"FAKE" * 100)
        with zipfile.ZipFile(obb, "w", compression=zipfile.ZIP_STORED) as out:
            out.writestr("assets/bin/Data/globalgamemanagers", b"FAKE OBB" * 170)
        badging = ("package: name='" + PACKAGE + "' versionCode='97' "
                   "versionName='source-only'\nsdkVersion:'23'\ntargetSdkVersion:'35'")
        return apk, obb, parse_badging(badging, 97)

    def test_real_packager_success_is_independently_attested(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apk, obb, metadata = self._inputs(root)
            output = root / "delivery"
            from scripts.t5_verify_xapk_cross_delivery import verify
            original_verify = verify
            calls = []
            def instrument(actual_root):
                result = original_verify(actual_root)
                calls.append(result)
                return result
            with mock.patch("scripts.t5_verify_xapk_cross_delivery.verify",
                            side_effect=instrument):
                record = package(apk, obb, metadata, output, part_bytes=251,
                                 asset_limit=500)
            self.assertTrue(record["companion_required"])
            self.assertEqual(len(calls), 1, "Packager must run post-write nested SHA verification")
            self.assertTrue(calls[0]["nested_apk_obb_sha256_match_loose_delivery"])
            self.assertFalse((output / "Raft-Android-Test.xapk").exists())
            self.assertTrue((output / "Raft-Android-Test.xapk.part001").exists())

    def test_corrupted_xapk_after_writer_close_is_never_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apk, obb, metadata = self._inputs(root)
            output = root / "delivery"
            original_finish = PartsWriter.finish
            touched = []
            def tamper_after_close(writer):
                record = original_finish(writer)
                if record["name"] == "Raft-Android-Test.xapk":
                    part = output / record["parts"][0]["name"]
                    with part.open("r+b") as stream:
                        stream.seek(10)
                        char = stream.read(1)
                        stream.seek(10)
                        stream.write(bytes([char[0] ^ 1]))
                    touched.append(part.name)
                return record
            with mock.patch.object(PartsWriter, "finish", tamper_after_close):
                with self.assertRaisesRegex(ValueError, "transport part SHA256"):
                    package(apk, obb, metadata, output, part_bytes=251,
                            asset_limit=500)
            self.assertEqual(len(touched), 1)
            self.assertTrue((output / "delivery.json").is_file(), "Metadata exists but invalid package MUST NOT be reported as success")
            self.assertTrue(json.loads((output / "delivery.json").read_text())["companion_required"])

    def test_legacy_apk_only_packing_keeps_optional_obb_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            apk, _, metadata = self._inputs(root)
            output = root / "delivery"
            record = package(apk, None, metadata, output, part_bytes=251,
                             asset_limit=500)
            self.assertFalse(record["companion_required"])
            self.assertEqual([x["name"] for x in record["files"]],
                             ["Raft-Android-Test.apk", "Raft-Android-Test.xapk"])


if __name__ == "__main__":
    unittest.main()
