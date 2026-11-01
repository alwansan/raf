"""Keep explicitly requested test APK delivery scoped to successful native runs."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/raft-unity-editor-android-import.yml"
NATIVE_REQUEST = "contains(github.event.head_commit.message, '[raft-native-build]')"


class EarlyApkDistributionPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_artifact_retention_requires_explicit_native_and_device_request(self):
        marker = "- name: Retain only the explicitly requested early test APK for release delivery"
        self.assertEqual(self.workflow.count(marker), 1)
        block = self.workflow.split(marker, 1)[1].split("- name: Report validation boundary", 1)[0]
        self.assertIn(NATIVE_REQUEST, block)
        self.assertIn("refs/heads/feature/android-native-port", block)
        self.assertIn("[raft-device-test]", block)

    def test_public_release_job_requires_success_and_explicit_device_request(self):
        self.assertEqual(self.workflow.count("\n  publish-early-test:"), 1)
        release = self.workflow.split("\n  publish-early-test:", 1)[1]
        self.assertIn("[raft-device-test]", release.split("\n    runs-on:", 1)[0])
        self.assertIn("needs.reconstruct.result == 'success'", release.split("\n    runs-on:", 1)[0])
        self.assertIn("refs/heads/feature/android-native-port", release.split("\n    runs-on:", 1)[0])

    def test_release_step_rechecks_request_and_branch_before_gh_publish(self):
        release = self.workflow.split("\n  publish-early-test:", 1)[1]
        self.assertEqual(self.workflow.count("gh release create"), 1)
        self.assertIn("EARLY_TEST_REQUESTED:", release)
        self.assertIn('test "${EARLY_TEST_REQUESTED:-}" = "true"', release)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/feature/android-native-port"', release)
        self.assertLess(release.index('test "${EARLY_TEST_REQUESTED:-}" = "true"'),
                        release.index("gh release create"))

    def test_non_opt_in_changes_cannot_start_native_or_cancel_active_build(self):
        self.assertIn("cancel-in-progress: false", self.workflow)
        self.assertNotIn("cancel-in-progress: true", self.workflow)
        self.assertEqual(self.workflow.count("\n  reconstruct:"), 1)
        reconstruct = self.workflow.split("\n  reconstruct:", 1)[1]
        condition = reconstruct.split("\n    runs-on:", 1)[0]
        self.assertIn("needs.unity-license-preflight.outputs.ready == 'true'", condition)
        self.assertIn("inputs.build_mode == 'native'", condition)
        self.assertIn("contains(github.event.head_commit.message, '[raft-native-build]')", condition)

    def test_no_other_release_publisher_in_workflow(self):
        release = self.workflow.split("\n  publish-early-test:", 1)[1]
        before_release = self.workflow.split("\n  publish-early-test:", 1)[0]
        self.assertNotIn("gh release create", before_release)
        self.assertEqual(release.count("gh release create"), 1)


if __name__ == "__main__":
    unittest.main()
