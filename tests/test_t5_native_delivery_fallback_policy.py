"""Source-only, fail-closed guards for the owner-authorized native delivery lane.

Run42058825739 compiled a genuine signed APK+OBB, but creation of a
GitHub Release returned 403. These tests check prevention of short-lived
artifact loss, not whether the host has granted Release write permissions.
"""
from pathlib import Path
import re
import unittest

PATH = Path(__file__).resolve().parents[1] / ".github/workflows/raft-unity-editor-android-import.yml"


def block_for(text, artifact):
    match = re.search(r"(?m)^          name: " + re.escape(artifact) + r"$", text)
    if not match:
        raise ValueError("native artifact missing: " + artifact)
    remain = text[match.end():]
    stop = re.search(r"(?m)^      - name:|^  [a-z][a-z-]+:", remain)
    return remain[:stop.start()] if stop else remain


def verify_source(text):
    for name in ("raft-android-test-delivery", "raft-android-signed-output-checkpoint",
                 "raft-android-audited-output-recovery"):
        block = block_for(text, name)
        for required in ("retention-days: 3", "compression-level: 0", "if-no-files-found: error"):
            if required not in block:
                raise ValueError("unsafe native retention: " + name + " / " + required)
    if "  publish-early-test:\n" not in text or "  delivery-result:\n" not in text:
        raise ValueError("missing publication/result job")
    publication = text.split("  publish-early-test:\n", 1)[1].split("  delivery-result:\n", 1)[0]
    result = text.split("  delivery-result:\n", 1)[1]
    expected = (
        "    needs: reconstruct",
        "needs.reconstruct.result == 'success'",
        "    permissions:\n      contents: write\n      actions: read",
        "GH_TOKEN: ${{ secrets.RAFT_RELEASE_TOKEN || github.token }}",
        'test "$GITHUB_REF" = "refs/heads/feature/android-native-port"',
        'gh release create "$tag" release-apk/*',
        'gh release view "$tag"',
        "assert actual==local, 'Published release is missing or changed delivery files'",
    )
    for token in expected:
        if token not in publication:
            raise ValueError("native release guard missing: " + token)
    if "continue-on-error: true" in publication or "|| true" in publication:
        raise ValueError("release failures must never be hidden")
    for token in ("set -eu", 'test "$RELEASE_RESULT" = "success"',
                  "RELEASE_RESULT: ${{ needs.publish-early-test.result }}",
                  'test "$NATIVE_RESULT" = "success"'):
        if token not in result:
            raise ValueError("strict native result guard missing: " + token)
    push = text.split("  push:\n", 1)[1].split("\n# Preserve", 1)[0]
    if ("'.github/raft-native-build-request.json'" not in push
            or "android-port/**" in push):
        raise ValueError("normal code push must not launch Unity")
    return True


class NativeDeliveryRetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = PATH.read_text(encoding="utf8")

    def test_current_source_contract(self):
        self.assertTrue(verify_source(self.original))

    def test_delivery_one_day_regression(self):
        idx = self.original.index("name: raft-android-test-delivery")
        changed = (self.original[:idx] +
                   self.original[idx:].replace("retention-days: 3", "retention-days: 1", 1))
        with self.assertRaisesRegex(ValueError, "retention"):
            verify_source(changed)

    def test_signed_checkpoint_short_retention(self):
        idx = self.original.index("name: raft-android-signed-output-checkpoint")
        changed = (self.original[:idx] +
                   self.original[idx:].replace("retention-days: 3", "retention-days: 2", 1))
        with self.assertRaisesRegex(ValueError, "retention"):
            verify_source(changed)

    def test_missing_recovery_artifact(self):
        changed = self.original.replace("name: raft-android-audited-output-recovery",
                                        "name: lost-audited-output")
        with self.assertRaisesRegex(ValueError, "missing"):
            verify_source(changed)

    def test_missing_optional_owner_token_route(self):
        changed = self.original.replace("GH_TOKEN: ${{ secrets.RAFT_RELEASE_TOKEN || github.token }}",
                                        "GH_TOKEN: ${{ github.token }}", 1)
        with self.assertRaisesRegex(ValueError, "release guard"):
            verify_source(changed)

    def test_release_403_cannot_be_suppressed(self):
        changed = self.original.replace('gh release create "$tag" release-apk/*',
                                        'gh release create "$tag" release-apk/* || true', 1)
        with self.assertRaisesRegex(ValueError, "hidden"):
            verify_source(changed)

    def test_dont_claim_release_success_with_missing_assets(self):
        changed = self.original.replace(
            "assert actual==local, 'Published release is missing or changed delivery files'",
            "assert len(actual) > 0", 1)
        with self.assertRaisesRegex(ValueError, "release guard"):
            verify_source(changed)

    def test_native_result_stays_strict(self):
        changed = self.original.replace('test "$RELEASE_RESULT" = "success"',
                                        'echo "$RELEASE_RESULT"', 1)
        with self.assertRaisesRegex(ValueError, "result guard"):
            verify_source(changed)

    def test_native_source_push_does_not_trigger_full_build(self):
        changed = self.original.replace("'      - nothing'",
                                        "'      - nothing'")
        changed = self.original.replace(
            "      - '.github/raft-native-build-request.json'",
            "      - 'android-port/**'", 1)
        self.assertNotEqual(changed, self.original)
        with self.assertRaisesRegex(ValueError, "normal code push"):
            verify_source(changed)


if __name__ == "__main__":
    unittest.main()
