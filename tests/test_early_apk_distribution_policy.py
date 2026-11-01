"""Fail-closed static checks for public early-test APK delivery policy.

These checks inspect workflow text only; they do not assert actual distribution rights.
"""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/raft-unity-editor-android-import.yml"
RIGHTS = "vars.RAFT_ANDROID_DISTRIBUTION_RIGHTS_CONFIRMED == 'true'"


class EarlyApkDistributionPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_artifact_retention_requires_explicit_rights(self):
        marker = "- name: Retain only the explicitly requested early test APK for release delivery"
        self.assertEqual(self.workflow.count(marker), 1)
        block = self.workflow.split(marker, 1)[1].split("- name: Report validation boundary", 1)[0]
        self.assertIn(RIGHTS, block)
        self.assertIn("refs/heads/feature/android-native-port", block)
        self.assertIn("[raft-device-test]", block)

    def test_public_release_job_requires_explicit_rights(self):
        self.assertEqual(self.workflow.count("\n  publish-early-test:"), 1)
        release = self.workflow.split("\n  publish-early-test:", 1)[1]
        self.assertIn(RIGHTS, release.split("\n    runs-on:", 1)[0])
        self.assertIn("needs.reconstruct.result == 'success'", release.split("\n    runs-on:", 1)[0])
        self.assertIn("refs/heads/feature/android-native-port", release.split("\n    runs-on:", 1)[0])

    def test_release_step_rechecks_rights_before_gh_publish(self):
        release = self.workflow.split("\n  publish-early-test:", 1)[1]
        self.assertEqual(self.workflow.count("gh release create"), 1)
        self.assertIn("RAFT_DISTRIBUTION_RIGHTS_CONFIRMED: ${{ vars.RAFT_ANDROID_DISTRIBUTION_RIGHTS_CONFIRMED }}", release)
        self.assertIn('test "${RAFT_DISTRIBUTION_RIGHTS_CONFIRMED:-}" = "true"', release)
        self.assertLess(release.index('test "${RAFT_DISTRIBUTION_RIGHTS_CONFIRMED:-}" = "true"'),
                        release.index("gh release create"))

    def test_no_other_release_publisher_in_workflow(self):
        release = self.workflow.split("\n  publish-early-test:", 1)[1]
        before_release = self.workflow.split("\n  publish-early-test:", 1)[0]
        self.assertNotIn("gh release create", before_release)
        self.assertEqual(release.count("gh release create"), 1)


if __name__ == "__main__":
    unittest.main()
