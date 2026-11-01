"""Source-policy regression: never label a partial reconstructed scene build a Raft APK.

This lightweight check cannot replace Unity import or device tests.
"""
from pathlib import Path
import unittest


SOURCE = (Path(__file__).resolve().parents[1] /
          "android-port/Editor/AndroidNativeBuild.cs")


class OriginalSceneIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_exact_original_scene_count_required(self):
        self.assertIn("scenes.Length != 40", self.source)
        self.assertIn("scenes.Distinct(StringComparer.OrdinalIgnoreCase).Count() != 40", self.source)

    def test_scene_paths_exist_and_are_unity_scenes(self):
        self.assertIn('s.EndsWith(".unity", StringComparison.OrdinalIgnoreCase)', self.source)
        self.assertIn("!File.Exists(s)", self.source)
        self.assertIn("throw new BuildFailedException", self.source)

    def test_all_original_scenes_still_pass_to_build_pipeline(self):
        self.assertIn("EditorBuildSettings.scenes.Where(s => s.enabled)", self.source)
        self.assertIn("scenes = scenes,", self.source)
        self.assertIn('RAFT_ANDROID_SCENE_GATE originalScenes=40 uniquePaths=true', self.source)


if __name__ == "__main__":
    unittest.main()
