"""B04 regression: preserve B12 delayed scene renderer snapshot and add quality evidence.

Synthetic/source-policy checks only. The original-managed offline workflow
separately compiles the actual C# with the recovered game's libraries.
No Android device, Unity Editor or pixel output is exercised here.
"""
from pathlib import Path
import re
import unittest

SOURCE = Path("android-port/Runtime/Platform/AndroidTestDiagnostics.cs")


def quality_section(source):
    prefix = "private static string OriginalQualityStateSnapshot()"
    suffix = "private System.Collections.IEnumerator ReportSceneShaderSnapshot(Scene scene)"
    if source.count(prefix) != 1 or source.count(suffix) != 1:
        raise ValueError("B04/B12 quality and scene methods must be unique")
    before, tail = source.split(prefix, 1)
    body, after = tail.split(suffix, 1)
    if "return" not in body or "QualitySettings" not in body:
        raise ValueError("Quality snapshot body missing")
    return body, after


def enforce_read_only_quality_state(source):
    method, scene = quality_section(source)
    # Model a deliberately inserted setter in otherwise valid synthetic text.
    # Never change the quality level, project settings, GUI or rendering state.
    forbidden = (r"QualitySettings\s*\.\s*SetQualityLevel\s*\(",
                 r"QualitySettings\s*\.\s*[A-Za-z_]\w*\s*=(?!=)",
                 r"PlayerPrefs\s*\.\s*Set\w*\s*\(",
                 r"Screen\s*\.\s*SetResolution\s*\(")
    if any(re.search(pattern, method) for pattern in forbidden):
        raise ValueError("B04 must not change Android quality or settings")
    wanted = ("quality_level_index=", "quality_tier_count=", "pixel_light_count=",
              "master_texture_limit=", "anti_aliasing=", "shadow_mode=",
              "shadow_distance=", "quality_snapshot_error_type=")
    if any(method.count(x) != 1 for x in wanted):
        raise ValueError("Expected exact bounded quality evidence fields")
    required_getters = ("QualitySettings.GetQualityLevel()", "QualitySettings.names",
                        "QualitySettings.pixelLightCount",
                        "QualitySettings.masterTextureLimit",
                        "QualitySettings.antiAliasing",
                        "QualitySettings.shadows",
                        "QualitySettings.shadowDistance")
    if any(method.count(x) != 1 for x in required_getters):
        raise ValueError("Quality getters missing or duplicated")
    if "catch (Exception ex)" not in method or 'return "; quality_snapshot_error_type="' not in method:
        raise ValueError("Quality getter error must not suppress shader snapshot")
    if scene.count("OriginalQualityStateSnapshot() +") != 1:
        raise ValueError("Quality evidence must attach exactly once to the existing scene snapshot")
    if scene.count('AndroidRuntimeLog.Write("render", "scene_shader_snapshot",') != 1:
        raise ValueError("B12 per-scene render evidence must be retained")
    if "yield return new WaitForSecondsRealtime(3f);" not in scene:
        raise ValueError("Original delayed scene snapshot not preserved")
    if "if (!scene.isLoaded) yield break;" not in scene:
        raise ValueError("Unloaded scene must not be sampled")


class RuntimeQualitySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SOURCE.read_text(encoding="utf-8")

    def test_read_only_report_in_existing_delayed_scene_snapshot(self):
        enforce_read_only_quality_state(self.src)

    def test_b12_original_material_mesh_and_color_fields_unchanged(self):
        for field in ("visible_renderers_sampled=", "material_slots=",
                      "unsupported_shaders=", "zero_pass_materials=",
                      "missing_mesh_filters=", "missing_skinned_meshes=",
                      "color_space=", "ambient_mode=", "original_shader_pixels_verified=false"):
            self.assertIn(field, self.src)

    def test_no_quality_mutation_or_per_frame_sampling(self):
        method, scene = quality_section(self.src)
        self.assertNotIn("SetQualityLevel", method)
        self.assertNotIn("Screen.SetResolution", method)
        self.assertNotIn("PlayerPrefs.Set", method)
        self.assertIn("WaitForSecondsRealtime(3f)", scene)
        self.assertEqual(self.src.count("OriginalQualityStateSnapshot() +"), 1)
        self.assertNotIn("OriginalQualityStateSnapshot()", self.src.split("private void Update()", 1)[-1]
                         if "private void Update()" in self.src else "")

    def test_reject_injected_quality_level_setter(self):
        with self.assertRaisesRegex(ValueError, "must not change"):
            enforce_read_only_quality_state(
                self.src.replace("QualitySettings.GetQualityLevel()",
                                 "QualitySettings.SetQualityLevel(4); QualitySettings.GetQualityLevel()", 1))

    def test_reject_injected_quality_property_write(self):
        with self.assertRaisesRegex(ValueError, "must not change"):
            enforce_read_only_quality_state(
                self.src.replace("QualitySettings.pixelLightCount +",
                                 "(QualitySettings.pixelLightCount = 100) +", 1))

    def test_reject_loss_of_b12_snapshot_link(self):
        with self.assertRaisesRegex(ValueError, "exactly once"):
            enforce_read_only_quality_state(
                self.src.replace("OriginalQualityStateSnapshot() +", '"" +', 1))

    def test_reject_unhandled_getter_failures(self):
        with self.assertRaisesRegex(ValueError, "Quality getter error"):
            enforce_read_only_quality_state(
                self.src.replace('return "; quality_snapshot_error_type="',
                                 'return "; quality_error="', 1))

    def test_reject_duplicate_quality_snapshot(self):
        with self.assertRaisesRegex(ValueError, "duplicated"):
            enforce_read_only_quality_state(
                self.src.replace("QualitySettings.antiAliasing",
                                 "QualitySettings.antiAliasing + QualitySettings.antiAliasing", 1))

    def test_reject_loss_of_three_second_delay(self):
        with self.assertRaisesRegex(ValueError, "delayed"):
            enforce_read_only_quality_state(
                self.src.replace("yield return new WaitForSecondsRealtime(3f);",
                                 "yield return null;", 1))


if __name__ == "__main__":
    unittest.main()
