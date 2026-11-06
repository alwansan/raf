"""Tiny synthetic fixtures only. No original Raft APK, OBB or assets."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.package_android_delivery import PACKAGE, package, parse_badging
from scripts.t5_verify_xapk_cross_delivery import verify


class SplitDeliveryAttestationTests(unittest.TestCase):
    def fixtures(self, root: Path, *, split=True):
        apk, obb = root / "synthetic.apk", root / "synthetic.obb"
        with zipfile.ZipFile(apk, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("classes.dex", b"dex\n035\0" + b"synthetic apk" * 90)
        with zipfile.ZipFile(obb, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("assets/bin/Data/sharedassets0.assets", b"synthetic obb" * 120)
        badging = ("package: name='" + PACKAGE
                   + "' versionCode='87' versionName='sourceonly'\n"
                   + "sdkVersion:'23'\ntargetSdkVersion:'35'")
        metadata = parse_badging(badging, 87)
        output = root / "delivery"
        package(apk, obb, metadata, output,
                **({"part_bytes": 257, "asset_limit": 500} if split else {}))
        return output

    def _rewrite_single_xapk(self, root, mutate):
        path = root / "Raft-Android-Test.xapk"
        replacement = root / "replacement.zip"
        with zipfile.ZipFile(path, "r") as z:
            source = [(name, z.read(name)) for name in z.namelist()]
        with zipfile.ZipFile(replacement, "w", compression=zipfile.ZIP_STORED) as z:
            for name, original in source:
                z.writestr(name, mutate(name, original))
        replacement.replace(path)
        data = json.loads((root / "delivery.json").read_text())
        row = data["files"][-1]
        row["bytes"] = path.stat().st_size
        row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        row["parts"][0]["bytes"] = row["bytes"]
        row["parts"][0]["sha256"] = row["sha256"]
        (root / "delivery.json").write_text(json.dumps(data))
        (root / "SHA256SUMS").write_text("".join(
            part["sha256"] + "  " + part["name"] + "\n"
            for item in data["files"] for part in item["parts"]
        ))

    def test_split_parts_cross_zip_boundaries_without_reassembly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixtures(Path(tmp), split=True)
            self.assertFalse((root / "Raft-Android-Test.xapk").exists())
            report = verify(root)
            self.assertTrue(report["nested_apk_obb_sha256_match_loose_delivery"])
            self.assertFalse(report["needs_multi_gigabyte_assembly_or_extraction"])
            self.assertGreater(report["actual_transport_parts_verified"], 3)

    def test_single_part_direct_outputs_remain_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixtures(Path(tmp), split=False)
            self.assertTrue((root / "Raft-Android-Test.xapk").is_file())
            self.assertEqual(verify(root)["actual_transport_parts_verified"], 3)

    def test_changed_split_xapk_part_rejected_even_with_same_length(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixtures(Path(tmp))
            p = root / "Raft-Android-Test.xapk.part001"
            raw = bytearray(p.read_bytes())
            raw[10] ^= 1
            p.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "transport part SHA256"):
                verify(root)

    def test_missing_split_part_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixtures(Path(tmp))
            (root / "Raft-Android-Test.xapk.part002").unlink()
            with self.assertRaisesRegex(ValueError, "transport part"):
                verify(root)

    def test_reject_parent_path_without_reading_external_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixtures(Path(tmp))
            data = json.loads((root / "delivery.json").read_text())
            data["files"][-1]["parts"][0]["name"] = "../outside"
            (root / "delivery.json").write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "transport part metadata"):
                verify(root)

    def test_xapk_manifest_mismatch_even_if_updated_sha_sums(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixtures(Path(tmp), split=False)
            def mutate(name, data):
                if name == "manifest.json":
                    obj = json.loads(data)
                    obj["version_code"] = "999"
                    return json.dumps(obj).encode()
                return data
            self._rewrite_single_xapk(root, mutate)
            with self.assertRaisesRegex(ValueError, "nested manifest differs"):
                verify(root)

    def test_nested_apk_mutation_even_if_updated_xapk_sha_sums(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.fixtures(Path(tmp), split=False)
            def mutate(name, data):
                if name == PACKAGE + ".apk":
                    return b"x" * len(data)
                return data
            self._rewrite_single_xapk(root, mutate)
            with self.assertRaisesRegex(ValueError, "Nested XAPK APK/OBB SHA256"):
                verify(root)


if __name__ == "__main__":
    unittest.main()
