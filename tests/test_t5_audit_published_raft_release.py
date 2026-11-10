"""T5 API-only verification of a real published Raft early-test release."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.t5_audit_published_raft_release import audit

RUN_ID = 41812889049
SHA = "d181ee7152580f49ee0b41dfd05fa2bfdacfafe5"
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/t5_raft_release_41812889049.json"


class PublishedRaftReleaseAuditTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def result(self):
        return audit(self.snapshot, expected_run_id=RUN_ID, expected_sha=SHA)

    def release(self):
        return self.snapshot["release"]

    def assets(self):
        return self.release()["assets"]

    def asset(self, name):
        return next(row for row in self.assets() if row["name"] == name)

    def test_real_apk86_official_source_and_multipart_metadata_consistent(self):
        result = self.result()
        self.assertTrue(result["workflow_completed_successfully"])
        self.assertTrue(result["release_target_source_consistent"])
        self.assertTrue(result["published_asset_metadata_complete"])
        self.assertEqual(result["native_run_id"], RUN_ID)
        self.assertEqual(result["native_source_sha"], SHA)
        self.assertEqual(result["logical_apk_obb_xapk_declared"], 3)
        self.assertEqual(result["reported_transport_assets"], 7)
        self.assertEqual(result["published_auxiliary_files"], 5)
        self.assertEqual(result["reported_total_transport_bytes"], 5948194034)

    def test_all_content_signature_device_verification_explicitly_false(self):
        result = self.result()
        for key in (
            "actual_download_bytes_and_sha256_verified",
            "actual_apk_signature_verified",
            "real_obb_contents_and_mount_verified",
            "real_xapk_reassembly_verified",
            "android_device_install_or_gameplay_verified",
        ):
            self.assertFalse(result[key])

    def test_release_provenance_follows_real_native_successful_run(self):
        self.assertEqual(self.snapshot["provenance"]["run_id"], RUN_ID)
        self.assertIn("41812889049", self.snapshot["provenance"]["release_url"])
        self.assertEqual(self.release()["target_commitish"], SHA)
        self.assertEqual(self.release()["source_claim"], SHA)

    def test_wrong_immutable_run_id_refused(self):
        self.snapshot["run"]["id"] += 1
        with self.assertRaisesRegex(ValueError, "run id mismatch"):
            self.result()

    def test_wrong_immutable_run_sha_refused(self):
        self.snapshot["run"]["head_sha"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "source SHA"):
            self.result()

    def test_native_run_not_terminal_success_refused(self):
        self.snapshot["run"]["status"] = "in_progress"
        self.snapshot["run"]["conclusion"] = None
        with self.assertRaisesRegex(ValueError, "No completed"):
            self.result()

    def test_other_success_workflow_rejected(self):
        self.snapshot["run"]["name"] = "Raft diagnostic"
        with self.assertRaisesRegex(ValueError, "original native"):
            self.result()

    def test_tag_wrong_run_id_rejected(self):
        self.release()["tag_name"] = "android-early-test-41812889048-1"
        with self.assertRaisesRegex(ValueError, "tag"):
            self.result()

    def test_tag_attempt_matches_actions_run_attempt(self):
        self.snapshot["run"]["run_attempt"] = 1
        self.assertTrue(self.result()["published_asset_metadata_complete"])

    def test_tag_attempt_mismatch_rejected(self):
        self.snapshot["run"]["run_attempt"] = 2
        with self.assertRaisesRegex(ValueError, "run attempt"):
            self.result()

    def test_invalid_run_attempt_rejected(self):
        self.snapshot["run"]["run_attempt"] = True
        with self.assertRaisesRegex(ValueError, "run attempt"):
            self.result()

    def test_release_target_disagrees_with_native_source(self):
        self.release()["target_commitish"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "target/body"):
            self.result()

    def test_release_body_claim_disagrees_with_native_source(self):
        self.release()["source_claim"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "target/body"):
            self.result()

    def test_non_prerelease_does_not_match_this_early_test_contract(self):
        self.release()["prerelease"] = False
        with self.assertRaisesRegex(ValueError, "prerelease"):
            self.result()

    def test_missing_required_release_delivery_json(self):
        self.release()["assets"] = [
            x for x in self.assets() if x["name"] != "delivery.json"
        ]
        with self.assertRaisesRegex(ValueError, "required delivery"):
            self.result()

    def test_missing_second_obb_part_fails_closed(self):
        self.release()["assets"] = [
            x for x in self.assets()
            if x["name"] != "main.86.com.alwansan.raft.androidtest.obb.part002"
        ]
        with self.assertRaisesRegex(ValueError, "Noncontiguous"):
            self.result()

    def test_part_index_gap_fails_closed(self):
        self.asset("Raft-Android-Test.xapk.part002")["name"] = (
            "Raft-Android-Test.xapk.part004"
        )
        with self.assertRaisesRegex(ValueError, "Noncontiguous"):
            self.result()

    def test_multipart_byte_count_mismatch_fails_closed(self):
        self.asset("Raft-Android-Test.xapk.part003")["size"] += 1
        with self.assertRaisesRegex(ValueError, "byte totals"):
            self.result()

    def test_multipart_part_limit_refused(self):
        self.asset("Raft-Android-Test.xapk.part001")["size"] += 1
        with self.assertRaisesRegex(ValueError, "1GiB limit"):
            self.result()

    def test_malformed_part_digest_refused(self):
        self.asset("Raft-Android-Test.xapk.part002")["digest"] = "sha256:broken"
        with self.assertRaisesRegex(ValueError, "asset digest"):
            self.result()

    def test_direct_apk_metadata_digest_disagrees_with_body_claim(self):
        self.asset("Raft-Android-Test.apk")["digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "digest disagrees"):
            self.result()

    def test_direct_apk_size_disagrees_with_logical_claim(self):
        self.asset("Raft-Android-Test.apk")["size"] -= 1
        with self.assertRaisesRegex(ValueError, "size mismatches"):
            self.result()

    def test_declared_obb_bytes_differ_from_transport_parts(self):
        key = "main.86.com.alwansan.raft.androidtest.obb"
        self.release()["logical_file_claims"][key]["bytes"] += 1
        with self.assertRaisesRegex(ValueError, "byte totals"):
            self.result()

    def test_missing_logical_xapk_claim_refused(self):
        self.release()["logical_file_claims"].pop("Raft-Android-Test.xapk")
        with self.assertRaisesRegex(ValueError, "exact APK/OBB/XAPK"):
            self.result()

    def test_disguised_asset_outside_manifest_refused(self):
        self.assets().append(
            {"name": "unexpected.bin", "size": 19, "digest": "sha256:" + "0" * 64}
        )
        with self.assertRaisesRegex(ValueError, "Unexpected extra"):
            self.result()

    def test_duplicate_asset_name_refused(self):
        self.assets().append(deepcopy(self.assets()[0]))
        with self.assertRaisesRegex(ValueError, "Duplicate public"):
            self.result()

    def test_ambiguous_whole_obb_plus_parts_refused(self):
        self.assets().append({
            "name": "main.86.com.alwansan.raft.androidtest.obb",
            "size": 12, "digest": "sha256:" + "0" * 64,
        })
        with self.assertRaisesRegex(ValueError, "Ambiguous both"):
            self.result()

    def test_invalid_obb_name_refused(self):
        row = self.release()["logical_file_claims"].pop(
            "main.86.com.alwansan.raft.androidtest.obb"
        )
        self.release()["logical_file_claims"]["main.86.other.obb"] = row
        with self.assertRaisesRegex(ValueError, "logical names"):
            self.result()

    def test_bool_size_not_treated_as_integer(self):
        self.asset("Raft-Android-Test.apk")["size"] = True
        with self.assertRaisesRegex(ValueError, "oversized release asset"):
            self.result()

    def test_valid_looking_part_hash_cannot_be_independently_authenticated(self):
        # API metadata has no downloaded bytes, so a syntactically valid
        # changed part hash is NOT independently detectable. Fail-closed
        # content verification flags remain false even for this case.
        self.asset("Raft-Android-Test.xapk.part001")["digest"] = (
            "sha256:" + "f" * 64
        )
        result = self.result()
        self.assertFalse(result["actual_download_bytes_and_sha256_verified"])
        self.assertFalse(result["real_xapk_reassembly_verified"])

    def test_cli_safe_metadata_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "public-release.json"
            path.write_text(json.dumps(self.snapshot), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-m", "scripts.t5_audit_published_raft_release",
                 "--snapshot", str(path), "--id", str(RUN_ID),
                 "--sha", SHA],
                cwd=ROOT, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            answer = json.loads(proc.stdout)
            self.assertEqual(answer["reported_transport_assets"], 7)
            self.assertNotIn("sharedassets", proc.stdout)
            self.assertFalse(answer["android_device_install_or_gameplay_verified"])


if __name__ == "__main__":
    unittest.main()
