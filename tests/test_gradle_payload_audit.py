"""Synthetic size fixtures: no original Raft assets or LFS required."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_gradle_asset_payload import JAVA_ARRAY_LIMIT, audit, classify


class GradlePayloadAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.gradle = self.project / "Library/Bee/Android/Prj/IL2CPP/Gradle"

    def file(self, module, name, size):
        path = self.gradle / module / "src/main/assets" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as output:
            output.truncate(size)
        return path

    def test_missing_gradle_assets_is_explicitly_unavailable(self):
        result = audit(self.project)
        self.assertFalse(result["available"])
        self.assertEqual(result["reason"], "gradle_assets_not_generated")
        self.assertEqual(result["fileCount"], 0)

    def test_both_gradle_modules_and_asset_classes_are_counted(self):
        self.file("unityLibrary", "bin/Data/data.unity3d", 123)
        self.file("unityLibrary", "bin/Data/StreamingAssets/audio.bank", 17)
        self.file("launcher", "config.bin", 5)
        result = audit(self.project)
        self.assertTrue(result["available"])
        self.assertEqual(result["fileCount"], 3)
        self.assertEqual(result["totalBytes"], 145)
        self.assertEqual(result["categoryBytes"], {
            "unity_data": 123, "streaming_assets": 17, "other_assets": 5})
        self.assertEqual(result["modules"]["launcher"]["totalBytes"], 5)
        self.assertEqual(result["topFiveBytes"], [123, 17, 5])
        self.assertNotIn("audio.bank", json.dumps(result))
        self.assertNotIn("data.unity3d", json.dumps(result))

    def test_sparse_oversized_asset_detected_without_reading_content(self):
        self.file("unityLibrary", "bin/Data/oversized.bin", JAVA_ARRAY_LIMIT + 1)
        result = audit(self.project)
        self.assertEqual(result["atOrAboveJavaArrayLimit"], 1)
        self.assertTrue(result["totalAtOrAboveJavaArrayLimit"])
        self.assertEqual(result["largestBytes"], JAVA_ARRAY_LIMIT + 1)
        self.assertFalse(result["assetContentRead"])

    def test_symlinks_are_not_followed(self):
        normal = self.file("unityLibrary", "bin/Data/safe.bin", 11)
        assets = self.gradle / "unityLibrary/src/main/assets"
        (assets / "outside-link").symlink_to(normal)
        (assets / "linked-dir").symlink_to(normal.parent, target_is_directory=True)
        result = audit(self.project)
        self.assertEqual(result["fileCount"], 1)
        self.assertEqual(result["skippedNonRegularOrUnreadable"], 1)

    def test_classification_does_not_depend_on_proprietary_names(self):
        self.assertEqual(classify(("bin", "Data", "StreamingAssets", "x")), "streaming_assets")
        self.assertEqual(classify(("bin", "Data", "x")), "unity_data")
        self.assertEqual(classify(("Haptics", "x")), "other_assets")


if __name__ == "__main__":
    unittest.main()
