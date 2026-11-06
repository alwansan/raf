"""T5 real-source snapshot + adversarial native-milestone verifier controls."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from scripts.t5_native_milestone_gate import classify

RUN_ID = 42058825739
SHA = "e9c358eda01785b65e4eb14f18723da426635628"
ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/t5_native_milestones_42058825739.json"


class MilestoneGateTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def result(self):
        return classify(self.data, expected_id=RUN_ID, expected_sha=SHA)

    def job(self, name):
        return next(x for x in self.data["jobs"]["jobs"] if x["name"] == name)

    def stages(self):
        return self.job("reconstruct")["steps"]

    def advance(self, through):
        for stage in self.stages():
            if stage["name"].startswith("Unity Editor"):
                pass
            if stage["number"] <= through:
                stage["status"] = "completed"
                stage["conclusion"] = "success"
            else:
                stage["status"] = "pending"
                stage["conclusion"] = None

    def test_actual_immutable_source_and_unity_running(self):
        provenance = self.data["provenance"]
        self.assertEqual(provenance["run_id"], RUN_ID)
        self.assertEqual(provenance["source_sha"], SHA)
        self.assertEqual(
            provenance["run_url"],
            "https://github.com/alwansan/raf/actions/runs/42058825739",
        )
        result = self.result()
        self.assertEqual(result["phase"], "unity_editor_in_progress")
        self.assertEqual(result["run_status"], "in_progress")
        self.assertTrue(result["request_gate_passed"])
        self.assertTrue(result["unity_license_preflight_passed"])
        self.assertTrue(result["water_documented_trial_gate_passed"])
        self.assertFalse(result["authentic_original_water_fft_verified"])
        self.assertEqual(result["milestones"]["unity"], "in_progress")
        self.assertEqual(result["milestones"]["signature_step"], "pending")
        self.assertEqual(result["artifact_records"], 4)
        for key in (
            "signed_apk_bytes_digest_verified",
            "obb_contents_digest_verified",
            "xapk_contents_digest_verified",
            "published_release_asset_digest_verified",
            "android_device_offline_world_save_reopen_verified",
        ):
            self.assertFalse(result[key])

    def test_real_artifact_names_are_staging_not_installable_packages(self):
        names = [x["name"] for x in self.data["artifacts"]["artifacts"]]
        self.assertEqual(len(names), 4)
        self.assertTrue(all(not n.endswith((".apk", ".obb", ".xapk")) for n in names))
        self.assertFalse(self.result()["published_release_asset_digest_verified"])

    def test_unity_failure_is_not_a_completed_signed_release(self):
        self.data["run"]["status"] = "completed"
        self.data["run"]["conclusion"] = "failure"
        self.job("reconstruct")["status"] = "completed"
        self.job("reconstruct")["conclusion"] = "failure"
        self.stages()[4].update(status="completed", conclusion="failure")
        self.assertEqual(self.result()["phase"], "unity_failed")
        self.assertFalse(self.result()["signed_apk_bytes_digest_verified"])

    def test_unity_pass_only_does_not_claim_delivered_apk(self):
        self.advance(62)
        r = self.result()
        self.assertEqual(r["phase"], "unity_import_passed_signature_unverified")
        self.assertFalse(r["published_release_asset_digest_verified"])

    def test_signature_step_pass_without_package_is_unverified(self):
        self.advance(67)
        r = self.result()
        self.assertEqual(r["phase"], "signature_step_passed_package_unverified")
        self.assertFalse(r["signed_apk_bytes_digest_verified"])

    def test_package_step_pass_not_equivalent_to_artifact_release(self):
        self.advance(69)
        r = self.result()
        self.assertEqual(r["phase"], "package_step_passed_retention_unverified")
        self.assertFalse(r["xapk_contents_digest_verified"])

    def test_completed_workflow_even_with_every_step_pass_not_device_proof(self):
        self.advance(71)
        self.data["run"].update(status="completed", conclusion="success")
        self.job("reconstruct").update(status="completed", conclusion="success")
        r = self.result()
        self.assertEqual(r["phase"], "retention_step_passed_external_release_unverified")
        self.assertFalse(r["published_release_asset_digest_verified"])
        self.assertFalse(r["android_device_offline_world_save_reopen_verified"])

    def test_faked_apk_artifact_name_never_proves_signature_or_digest(self):
        self.data["artifacts"]["artifacts"].append(
            {"name": "fake-signed-full-xapk.apk", "size_in_bytes": 200000000, "expired": False}
        )
        r = self.result()
        self.assertEqual(r["artifact_records"], 5)
        self.assertFalse(r["signed_apk_bytes_digest_verified"])

    def test_later_package_success_with_failed_signature_is_refused(self):
        self.stages()[7].update(status="completed", conclusion="success")
        with self.assertRaisesRegex(ValueError, "Contradictory"):
            self.result()

    def test_later_unity_success_with_failed_water_is_refused(self):
        self.advance(62)
        self.stages()[2].update(status="completed", conclusion="failure")
        with self.assertRaisesRegex(ValueError, "Contradictory"):
            self.result()

    def test_completed_workflow_success_without_retained_native_is_refused(self):
        self.data["run"].update(status="completed", conclusion="success")
        self.job("reconstruct").update(status="completed", conclusion="success")
        with self.assertRaisesRegex(ValueError, "Workflow success"):
            self.result()

    def test_wrong_source_sha_rejected(self):
        self.data["run"]["head_sha"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "Immutable source SHA"):
            self.result()

    def test_wrong_run_id_rejected(self):
        self.data["run"]["id"] += 1
        with self.assertRaisesRegex(ValueError, "Immutable run id"):
            self.result()

    def test_duplicate_native_job_rejected(self):
        self.data["jobs"]["jobs"].append(deepcopy(self.job("reconstruct")))
        with self.assertRaisesRegex(ValueError, "Duplicate native job"):
            self.result()

    def test_2026_native_export_extra_step_shifts_all_later_milestones(self):
        # The real postrestorer Material->Texture guard added in November
        # shifts water/GUID/Unity/APK/signature/retention step numbers. A
        # run's source SHA, stage names and outcomes remain authoritative.
        for stage in self.stages():
            if stage["number"] >= 43:
                stage["number"] += 1
        result = self.result()
        self.assertEqual(result["phase"], "unity_editor_in_progress")
        self.assertTrue(result["water_documented_trial_gate_passed"])
        self.assertFalse(result["signed_apk_bytes_digest_verified"])

    def test_actual_full_job_extra_diagnostic_step_still_preserves_known_gates(self):
        for stage in self.stages():
            if stage["number"] >= 43:
                stage["number"] += 1
        self.stages().insert(2, {
            "number": 43,
            "name": "T5 inspect actual postrestorer Material-to-Texture references (non-mutating)",
            "status": "completed",
            "conclusion": "failure",  # diagnostic continue-on-error does not fake READY
        })
        result = self.result()
        self.assertEqual(result["phase"], "unity_editor_in_progress")
        self.assertTrue(result["water_documented_trial_gate_passed"])
        self.assertFalse(result["published_release_asset_digest_verified"])

    def test_new_step_name_cannot_replace_an_authentic_milestone(self):
        self.stages()[2]["name"] = "T5 read-only unrelated diagnostic"
        with self.assertRaisesRegex(ValueError, "milestone"):
            self.result()

    def test_duplicate_step_number_does_not_forge_a_native_stage(self):
        self.stages()[3]["number"] = self.stages()[2]["number"]
        with self.assertRaisesRegex(ValueError, "number|order|position"):
            self.result()

    def test_reordered_source_milestone_does_not_forge_success(self):
        # Even with valid stage names, source chronology must be coherent.
        self.stages()[2]["number"], self.stages()[3]["number"] = (
            self.stages()[3]["number"], self.stages()[2]["number"])
        with self.assertRaisesRegex(ValueError, "order|position"):
            self.result()

    def test_missing_required_milestone_rejected(self):
        self.stages().pop(2)
        with self.assertRaisesRegex(ValueError, "Missing or additional"):
            self.result()

    def test_malformed_step_number_rejected(self):
        self.stages()[4]["number"] = True
        with self.assertRaisesRegex(ValueError, "step number"):
            self.result()

    def test_nonterminal_conclusion_rejected(self):
        self.data["run"]["conclusion"] = "success"
        with self.assertRaisesRegex(ValueError, "nonterminal"):
            self.result()

    def test_duplicate_and_invalid_artifact_metadata_rejected(self):
        self.data["artifacts"]["artifacts"].append(
            deepcopy(self.data["artifacts"]["artifacts"][0])
        )
        with self.assertRaisesRegex(ValueError, "Duplicate artifact name"):
            self.result()
        self.data["artifacts"]["artifacts"][-1]["name"] = "different"
        self.data["artifacts"]["artifacts"][-1]["size_in_bytes"] = False
        with self.assertRaisesRegex(ValueError, "Malformed artifact"):
            self.result()

    def test_pending_unity_stage_is_not_compile_success(self):
        self.stages()[4]["status"] = "pending"
        self.assertEqual(self.result()["phase"], "pre_unity_or_unity_pending")

    def test_cli_uses_exact_safe_fixture_and_returns_aggregate_only(self):
        with TemporaryDirectory() as td:
            snapshot = Path(td) / "safe-native-snapshot.json"
            snapshot.write_text(json.dumps(self.data), encoding="utf-8")
            p = subprocess.run(
                [sys.executable, "-m", "scripts.t5_native_milestone_gate",
                 "--snapshot", str(snapshot), "--id", str(RUN_ID),
                 "--sha", SHA],
                cwd=ROOT, text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(p.returncode, 0, p.stderr)
            r = json.loads(p.stdout)
            self.assertEqual(r["phase"], "unity_editor_in_progress")
            self.assertNotIn("sharedassets", p.stdout)
            self.assertNotIn("UnityEditor.dll", p.stdout)


if __name__ == "__main__":
    unittest.main()
