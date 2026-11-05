"""Actual production manifest verification logic with synthetic safe bytes only.

Original 2,166-byte/727-byte release metadata are fetched in the separate CI
job; tests never download or publish any game binary or source.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.t5_verify_release_manifest_bytes import verify, PACKAGE

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/t5_raft_release_41812889049.json"


class SmallPublishedReleaseManifestTests(unittest.TestCase):
    def setUp(self):
        self.snap = json.loads(FIXTURE.read_text())
        self.live = deepcopy(self.snap["release"])
        self.claims = self.snap["release"]["logical_file_claims"]
        self.assets = self.snap["release"]["assets"]
        self.manifest = {
            "schema": 1,
            "package": PACKAGE,
            "version_code": "86",
            "companion_required": True,
            "transport_only_parts": True,
            "device_install_verified": False,
            "files": []
        }
        for name, claim in self.claims.items():
            parts = [a for a in self.assets if (
                a["name"] == name or a["name"].startswith(name + ".part")
            )]
            parts.sort(key=lambda x: x["name"])
            self.manifest["files"].append({
                "name": name,
                "bytes": claim["bytes"],
                "sha256": claim["sha256"],
                "parts": [{
                    "name": a["name"],
                    "bytes": a["size"],
                    "sha256": a["digest"].split(":")[1],
                } for a in parts]
            })
        self.sums_rows = [
            (x["name"], x["sha256"])
            for r in self.manifest["files"]
            for x in r["parts"]
        ]
        self.delivery_bytes = b""
        self.sums_bytes = b""
        self.resign_synthetic_small_metadata()

    def resign_synthetic_small_metadata(self):
        self.delivery_bytes = (json.dumps(
            self.manifest, ensure_ascii=False, sort_keys=True
        ) + "\n").encode()
        self.sums_bytes = "".join(
            f"{digest}  {name}\n" for name, digest in self.sums_rows
        ).encode()
        for name, data in (("delivery.json", self.delivery_bytes),
                           ("SHA256SUMS", self.sums_bytes)):
            asset = next(x for x in self.snap["release"]["assets"] if x["name"] == name)
            asset["size"] = len(data)
            asset["digest"] = "sha256:" + hashlib.sha256(data).hexdigest()
            current = next(x for x in self.live["assets"] if x["name"] == name)
            current["size"] = len(data)
            current["digest"] = asset["digest"]

    def result(self):
        return verify(self.snap, self.live, self.delivery_bytes, self.sums_bytes)

    def part(self, stem, index=0):
        return next(r for r in self.manifest["files"] if r["name"] == stem)["parts"][index]

    def test_three_logical_records_seven_parts_actual_small_bytes_verified(self):
        r = self.result()
        self.assertEqual(r["logical_file_declared_records_consistent"], 3)
        self.assertEqual(r["published_transport_part_records_bound_to_manifest"], 7)
        self.assertEqual(r["small_published_metadata_files_verified_by_actual_bytes"], 2)
        self.assertTrue(r["published_small_metadata_sha256_verified"])
        self.assertEqual(r["logical_transport_bytes_declared"], 5948194034)

    def test_original_large_download_content_signature_device_never_claimed(self):
        r = self.result()
        for key in ("actual_game_part_bytes_sha256_verified", "apk_signature_verified",
                    "obb_mounted_on_device", "xapk_reassembled_and_installed",
                    "device_world_save_reopen_verified"):
            self.assertFalse(r[key])

    def test_wrong_small_manifest_download_hash_rejected(self):
        self.delivery_bytes += b" "
        with self.assertRaisesRegex(ValueError, "metadata length"):
            self.result()

    def test_equal_size_modified_small_manifest_digest_rejected(self):
        self.delivery_bytes = b"X" + self.delivery_bytes[1:]
        with self.assertRaisesRegex(ValueError, "metadata SHA256"):
            self.result()

    def test_equal_size_modified_sha256sums_digest_rejected(self):
        self.sums_bytes = b"f" + self.sums_bytes[1:]
        with self.assertRaisesRegex(ValueError, "metadata SHA256"):
            self.result()

    def test_live_release_digest_drift_refused(self):
        a = next(x for x in self.live["assets"] if x["name"].endswith(".part002"))
        a["digest"] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(ValueError, "size/digest declarations drifted"):
            self.result()

    def test_live_release_target_drift_refused(self):
        self.live["target_commitish"] = "f" * 40
        with self.assertRaisesRegex(ValueError, "identity drift"):
            self.result()

    def test_missing_or_extra_live_asset_fails_closed(self):
        self.live["assets"].pop()
        with self.assertRaisesRegex(ValueError, "size/digest declarations drifted"):
            self.result()

    def test_manifest_wrong_package_name_refused(self):
        self.manifest["package"] = "different.package"
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "Delivery contract"):
            self.result()

    def test_manifest_claims_premature_device_install_refused(self):
        self.manifest["device_install_verified"] = True
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "Delivery contract"):
            self.result()

    def test_manifest_wrong_game_version_code_refused(self):
        self.manifest["version_code"] = "87"
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "Delivery contract"):
            self.result()

    def test_manifest_obb_whole_sha_mismatch_refused(self):
        self.manifest["files"][1]["sha256"] = "f" * 64
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "logical size/SHA256"):
            self.result()

    def test_manifest_part_hash_mismatch_with_release_api_refused(self):
        self.manifest["files"][2]["parts"][1]["sha256"] = "f" * 64
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "Release asset metadata differs"):
            self.result()

    def test_manifest_part_byte_count_mismatch_refused(self):
        self.manifest["files"][1]["parts"][1]["bytes"] -= 1
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "Release asset metadata differs"):
            self.result()

    def test_manifest_part_index_out_of_order_refused(self):
        self.manifest["files"][2]["parts"].reverse()
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "out of order"):
            self.result()

    def test_manifest_duplicate_logical_file_refused(self):
        self.manifest["files"][1] = deepcopy(self.manifest["files"][0])
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "duplicate logical"):
            self.result()

    def test_manifest_missing_part_refused(self):
        self.manifest["files"][2]["parts"].pop()
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "Transport byte sizes"):
            self.result()

    def test_manifest_duplicate_transport_part_refused(self):
        self.manifest["files"][2]["parts"][1] = deepcopy(self.manifest["files"][2]["parts"][0])
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "out of order or duplicated"):
            self.result()

    def test_manifest_missing_obb_refused(self):
        self.manifest["files"].pop(1)
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "three logical files"):
            self.result()

    def test_manifest_bool_part_size_refused(self):
        self.manifest["files"][2]["parts"][0]["bytes"] = True
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "out of order or duplicated"):
            self.result()

    def test_manifest_direct_apk_hash_disagrees_refused(self):
        self.manifest["files"][0]["parts"][0]["sha256"] = "f" * 64
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "Release asset metadata differs"):
            self.result()

    def test_sums_entry_mismatch_detected_even_if_file_metadata_digest_reissued(self):
        self.sums_rows[2] = (self.sums_rows[2][0], "f" * 64)
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "SHA256SUMS contents/order"):
            self.result()

    def test_sums_part_rows_reordered_refused(self):
        self.sums_rows.reverse()
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "contents/order"):
            self.result()

    def test_sums_extra_entry_refused(self):
        self.sums_rows.append(("extra.part001", "f" * 64))
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "contents/order"):
            self.result()

    def test_sums_invalid_name_refused(self):
        self.sums_rows[0] = ("../unsafe", self.sums_rows[0][1])
        self.resign_synthetic_small_metadata()
        with self.assertRaisesRegex(ValueError, "Malformed SHA256SUMS"):
            self.result()

    def test_sums_missing_terminal_newline_refused(self):
        self.resign_synthetic_small_metadata()
        self.sums_bytes = self.sums_bytes.rstrip(b"\n")
        for catalog in (self.snap["release"]["assets"], self.live["assets"]):
            a = next(x for x in catalog if x["name"] == "SHA256SUMS")
            a["size"] = len(self.sums_bytes)
            a["digest"] = "sha256:" + hashlib.sha256(self.sums_bytes).hexdigest()
        with self.assertRaisesRegex(ValueError, "newline terminated"):
            self.result()

    def test_baseline_bad_native_sha_refused_before_metadata(self):
        self.snap["run"]["head_sha"] = "f" * 40
        with self.assertRaisesRegex(ValueError, "Run source SHA"):
            self.result()

    def test_reader_rejects_symlink_and_large_file(self):
        from scripts.t5_verify_release_manifest_bytes import _read_small
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = root / "data"
            data.write_bytes(b"123456789")
            with self.assertRaisesRegex(ValueError, "size bound"):
                _read_small(data, max_bytes=8)
            link = root / "link"
            link.symlink_to(data)
            with self.assertRaisesRegex(ValueError, "unsafe"):
                _read_small(link, max_bytes=16)


if __name__ == "__main__":
    unittest.main()
