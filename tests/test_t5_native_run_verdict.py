"""T5 bounded native run verdict: original public run metadata + controls."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.t5_audit_native_run_verdict import classify

RUN_ID = 42042902522
SHA = "753802d75196210d721cca0f4fdec6ce7800bf0d"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "t5_native_run_42042902522.json"


class NativeRunVerdictTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text())
        self.run = self.data["run"]
        self.jobs = self.data["jobs"]
        self.artifacts = self.data["artifacts"]

    def audit(self):
        return classify(
            self.run, self.jobs, self.artifacts,
            expected_id=RUN_ID, expected_sha=SHA
        )

    def job(self, name):
        return next(j for j in self.jobs["jobs"] if j["name"] == name)

    def test_official_filtered_cancelled_run_outcome(self):
        self.assertEqual(self.data["provenance"]["run_id"], RUN_ID)
        self.assertEqual(self.data["provenance"]["source_sha"], SHA)
        self.assertEqual(
            self.data["provenance"]["github_run_url"],
            "https://github.com/alwansan/raf/actions/runs/42042902522"
        )
        result = self.audit()
        self.assertEqual(result["run_conclusion"], "cancelled")
        self.assertEqual(result["native_conclusion"], "cancelled")
        self.assertEqual(
            result["verdict"], "native_job_cancelled_no_source_failure_established"
        )
        self.assertEqual(result["native_stage"], "original_mesh_restoration")
        self.assertTrue(result["request_gate_passed"])
        self.assertTrue(result["license_preflight_passed"])
        self.assertTrue(result["downstream_failure_follows_cancelled_native"])
        self.assertEqual(result["artifact_records"], 0)
        self.assertEqual(result["cancellation_initiator"], "unknown")
        for field in [
            "delivery_package_sha_verified", "signed_release_assets_verified",
            "android_install_verified"
        ]:
            self.assertFalse(result[field])

    def test_cancelled_native_with_failed_step_preserves_failure_evidence(self):
        self.job("reconstruct")["steps"][0]["conclusion"] = "failure"
        result = self.audit()
        self.assertEqual(
            result["verdict"],
            "native_job_cancelled_failed_step_causality_unresolved"
        )
        self.assertEqual(result["native_stage"], "original_mesh_restoration")
        self.assertEqual(result["cancellation_initiator"], "unknown")
        self.assertFalse(result["signed_release_assets_verified"])

    def test_cancelled_native_with_cancelled_step_remains_unproven(self):
        self.job("reconstruct")["steps"][0]["conclusion"] = "cancelled"
        self.assertEqual(
            self.audit()["verdict"],
            "native_job_cancelled_no_source_failure_established"
        )

    def test_cancelled_native_malformed_steps_fails_closed(self):
        self.job("reconstruct")["steps"] = "invalid"
        with self.assertRaisesRegex(ValueError, "steps must be an array"):
            self.audit()

    def test_genuine_reconstruct_failure_is_not_cancelled(self):
        self.run["conclusion"] = "failure"
        self.job("reconstruct")["conclusion"] = "failure"
        self.job("reconstruct")["steps"][0]["conclusion"] = "failure"
        result = self.audit()
        self.assertEqual(result["verdict"], "native_job_failed_or_timed_out")
        self.assertFalse(result["downstream_failure_follows_cancelled_native"])

    def test_timeout_is_not_source_failure(self):
        self.run["conclusion"] = "timed_out"
        self.job("reconstruct")["conclusion"] = "timed_out"
        self.job("reconstruct")["steps"][0]["conclusion"] = "timed_out"
        result = self.audit()
        self.assertEqual(result["verdict"], "native_job_failed_or_timed_out")
        self.assertEqual(result["native_stage"], "original_mesh_restoration")

    def test_queued_nonterminal_is_not_accepted_as_success(self):
        self.run["status"] = "queued"
        self.run["conclusion"] = None
        self.job("reconstruct")["conclusion"] = None
        result = self.audit()
        self.assertEqual(result["verdict"], "awaiting_terminal_workflow")
        self.assertFalse(result["signed_release_assets_verified"])

    def test_even_completed_success_does_not_verify_signed_release(self):
        self.run["conclusion"] = "success"
        self.job("reconstruct")["conclusion"] = "success"
        self.job("reconstruct")["steps"] = []
        self.job("delivery-result")["conclusion"] = "success"
        self.job("publish-early-test")["conclusion"] = "success"
        result = self.audit()
        self.assertEqual(
            result["verdict"],
            "native_job_passed_publish_job_passed_but_release_unverified"
        )
        self.assertFalse(result["delivery_package_sha_verified"])
        self.assertFalse(result["signed_release_assets_verified"])
        self.assertFalse(result["android_install_verified"])

    def test_artifact_record_alone_does_not_verify_release_sha(self):
        self.artifacts["artifacts"] = [
            {"name": "claimed-delivery", "size_in_bytes": 999}
        ]
        result = self.audit()
        self.assertEqual(result["artifact_records"], 1)
        self.assertFalse(result["signed_release_assets_verified"])

    def test_native_success_publish_skipped_is_unverified(self):
        self.run["conclusion"] = "failure"
        self.job("reconstruct")["conclusion"] = "success"
        self.job("delivery-result")["conclusion"] = "failure"
        self.job("publish-early-test")["conclusion"] = "skipped"
        self.assertEqual(self.audit()["verdict"],
                         "native_job_passed_delivery_unverified")

    def test_missing_required_artifacts_array_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Artifacts must be"):
            classify(self.run, self.jobs, {}, expected_id=RUN_ID,
                     expected_sha=SHA)

    def test_wrong_source_sha_fails_closed(self):
        self.run["head_sha"] = "a" * 40
        with self.assertRaisesRegex(ValueError, "Immutable run"):
            self.audit()

    def test_wrong_run_id_fails_closed(self):
        self.run["id"] = RUN_ID + 1
        with self.assertRaisesRegex(ValueError, "Immutable run"):
            self.audit()

    def test_invalid_sha_fails_closed(self):
        self.run["head_sha"] = "Z" * 40
        with self.assertRaisesRegex(ValueError, "Invalid or missing"):
            self.audit()

    def test_duplicate_native_job_fails_closed(self):
        self.jobs["jobs"].append(deepcopy(self.job("reconstruct")))
        with self.assertRaisesRegex(ValueError, "Duplicate native"):
            self.audit()

    def test_completed_success_with_cancelled_reconstruct_is_contradiction(self):
        self.run["conclusion"] = "success"
        with self.assertRaisesRegex(ValueError, "Contradictory"):
            self.audit()

    def test_nonterminal_with_conclusion_is_contradiction(self):
        self.run["status"] = "in_progress"
        with self.assertRaisesRegex(ValueError, "Nonterminal"):
            self.audit()

    def test_unknown_canceled_step_is_not_guessed(self):
        self.job("reconstruct")["steps"][0]["name"] = "other unknown worker step"
        self.assertEqual(self.audit()["native_stage"], "other_or_unknown_stage")

    def test_cli_reads_separate_github_metadata_and_emits_redacted_verdict(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = [root / (n + ".json") for n in ["run", "jobs", "artifacts"]]
            for f, v in zip(paths, [self.run, self.jobs, self.artifacts]):
                f.write_text(json.dumps(v))
            result = subprocess.run(
                [sys.executable, "-m", "scripts.t5_audit_native_run_verdict",
                 "--run", str(paths[0]), "--jobs", str(paths[1]),
                 "--artifacts", str(paths[2]), "--id", str(RUN_ID),
                 "--sha", SHA],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=10
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output["native_stage"], "original_mesh_restoration")
            self.assertNotIn("sharedassets", result.stdout)
            self.assertFalse(output["signed_release_assets_verified"])


if __name__ == "__main__":
    unittest.main()
