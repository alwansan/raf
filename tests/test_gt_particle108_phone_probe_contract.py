"""Standalone phone graphics probe safety assertions."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "android-port/Experiments/GT/Editor/GTParticlePhoneBuild.cs"
RUNTIME = ROOT / "android-port/Experiments/GT/Runtime/GTParticlePhoneRuntime.cs"

class ProbeSafetyTests(unittest.TestCase):
    def test_unproven_original_material_flags(self):
        editor = EDITOR.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        for text in ("originalMaterialBindingProven = false",
                     "originalShaderRestored = false",
                     "actualDevicePixelsVerified = false",
                     "approximateSamplerStates = true"):
            self.assertIn(text, editor)
        self.assertIn("originalAdrenoPixelsVerified = false", runtime)

    def test_native_target_and_phone_logging(self):
        editor = EDITOR.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("GraphicsDeviceType.Vulkan", editor)
        self.assertIn("AndroidArchitecture.ARM64", editor)
        self.assertIn("BuildPipeline.BuildPlayer", editor)
        self.assertIn("NewScene(NewSceneSetup.EmptyScene", editor)
        self.assertIn("new Material[4]", editor)
        self.assertIn("COPY LOG JSON", runtime)
        self.assertIn("GUIUtility.systemCopyBuffer", runtime)

if __name__ == "__main__":
    unittest.main()
