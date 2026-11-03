"""A12 synthetic only: strict original Blur wrapper construction boundaries."""
from unittest import mock
import unittest

from scripts.a12_build_original_blur_wrapper import TARGET, wrapper


def original():
    return {
        "m_Name": TARGET,
        "m_PropInfo": {"m_Props": []},
        "m_SubShaders": [{
            "m_LOD": 0,
            "m_Tags": {"tags": []},
            "m_Passes": [{"m_Type": 0, "m_State": {}},
                         {"m_Type": 0, "m_State": {}}],
        }],
        "m_FallbackName": "",
        "m_CustomEditorName": "",
    }


def stages():
    return {
        (0, 0): ("float4 main() : SV_Position {return 0;}",
                 "float4 main() : SV_Target {return 0;}", "5.0"),
        (0, 1): ("float4 main() : SV_Position {return 1;}",
                 "float4 main() : SV_Target {return 1;}", "5.0"),
    }


class OriginalBlurShaderLabTests(unittest.TestCase):
    def wrap(self, p=None, stage=None):
        with mock.patch("scripts.a12_build_original_blur_wrapper.render_state",
                        return_value="ZWrite Off"):
            return wrapper(original() if p is None else p,
                           stages() if stage is None else stage)

    def test_exact_two_original_passes_are_preserved(self):
        result = self.wrap()
        self.assertEqual(result.count("Pass {"), 2)
        self.assertIn('Shader "' + TARGET + '"', result)
        self.assertEqual(result.count("#pragma target 5.0"), 2)
        self.assertEqual(result.count("#pragma vertex main"), 2)
        self.assertEqual(result.count("#pragma fragment main"), 2)
        self.assertIn("Properties {}", result)
        self.assertTrue(result.endswith("}\n"))

    def test_original_name_cannot_be_switched(self):
        p = original()
        p["m_Name"] = "Synthetic/Unrelated"
        with self.assertRaisesRegex(ValueError, "name"):
            self.wrap(p)

    def test_original_nonempty_properties_cannot_be_discarded(self):
        p = original()
        p["m_PropInfo"]["m_Props"] = [{"m_Name": "_SyntheticTexture"}]
        with self.assertRaisesRegex(ValueError, "property"):
            self.wrap(p)

    def test_original_pass_count_must_be_exact(self):
        for n in (0, 1, 3):
            p = original()
            p["m_SubShaders"][0]["m_Passes"] = (
                [{"m_Type": 0, "m_State": {}} for _ in range(n)]
            )
            with self.subTest(n=n), self.assertRaisesRegex(ValueError, "two-pass"):
                self.wrap(p)

    def test_unknown_original_pass_kind_rejected(self):
        p = original()
        p["m_SubShaders"][0]["m_Passes"][0]["m_Type"] = 2
        with self.assertRaisesRegex(ValueError, "pass type"):
            self.wrap(p)

    def test_missing_or_unexpected_pass_source_rejected(self):
        d = stages()
        del d[(0, 1)]
        with self.assertRaisesRegex(ValueError, "stage pairs"):
            self.wrap(stage=d)
        d = stages()
        d[(0, 2)] = d[(0, 1)]
        with self.assertRaisesRegex(ValueError, "stage pairs"):
            self.wrap(stage=d)

    def test_unknown_original_shader_model_rejected(self):
        d = stages()
        v, f, _ = d[(0, 0)]
        d[(0, 0)] = (v, f, "6.0")
        with self.assertRaisesRegex(ValueError, "Shader Model"):
            self.wrap(stage=d)

    def test_fallback_and_custom_editor_metadata_not_silently_discarded(self):
        p = original()
        p["m_FallbackName"] = "Synthetic/Fallback"
        p["m_CustomEditorName"] = "SyntheticEditor"
        result = self.wrap(p)
        self.assertIn('Fallback "Synthetic/Fallback"', result)
        self.assertIn('CustomEditor "SyntheticEditor"', result)


if __name__ == "__main__":
    unittest.main()
