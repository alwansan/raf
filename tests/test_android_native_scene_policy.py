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

    def test_android_launch_orientation_is_landscape_before_unity_runtime(self):
        self.assertIn("PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;", self.source)
        self.assertIn("PlayerSettings.allowedAutorotateToPortrait = false;", self.source)
        self.assertIn("PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;", self.source)
        self.assertIn("PlayerSettings.allowedAutorotateToLandscapeLeft = true;", self.source)
        self.assertIn("PlayerSettings.allowedAutorotateToLandscapeRight = true;", self.source)

    def test_all_original_scenes_still_pass_to_build_pipeline(self):
        self.assertIn("EditorBuildSettings.scenes.Where(s => s.enabled)", self.source)
        self.assertIn("scenes = scenes,", self.source)
        self.assertIn('RAFT_ANDROID_SCENE_GATE originalScenes=40 uniquePaths=true', self.source)


    def test_android_texture_budget_is_bounded_and_preserves_original_overrides(self):
        budget = (SOURCE.parent / "AndroidTextureBudget.cs").read_text(encoding="utf-8")
        self.assertIn("AndroidTextureBudget.Apply();", self.source)
        self.assertIn("MobileTextureSubtarget.ASTC", self.source)
        self.assertIn("TextureImporterType.Default", budget)
        self.assertIn("TextureImporterShape.Texture2D", budget)
        self.assertIn("GetSourceTextureWidthAndHeight", budget)
        self.assertIn("Math.Max(width, height) <= MaxDimension", budget)
        self.assertIn("if (settings.overridden)", budget)
        self.assertIn("Math.Min(importer.maxTextureSize, MaxDimension)", budget)
        self.assertIn("TextureImporterFormat.ASTC_6x6", budget)
        self.assertIn("importer.SaveAndReimport();", budget)
        self.assertNotIn("File.Delete(", budget)
        self.assertNotIn("TextureImporterType.Sprite", budget)

    def test_generated_gradle_payload_is_audited_before_compression(self):
        budget = (SOURCE.parent / "AndroidTextureBudget.cs").read_text(encoding="utf-8")
        self.assertIn("IPostGenerateGradleAndroidProject", budget)
        self.assertIn("OnPostGenerateGradleAndroidProject(string path)", budget)
        self.assertIn('Path.Combine(path, "src/main/assets")', budget)
        self.assertIn("overJavaArrayLimit=", budget)
        self.assertIn("size > int.MaxValue", budget)
        self.assertIn("fileNamesLogged=false", budget)
        self.assertIn("throw new BuildFailedException", budget)

if __name__ == "__main__":
    unittest.main()
