"""GT source-free guards for SHA-original Spectrum seven-pass state packet.

No Raft proprietary state text, property value, DXBC, ShaderLab or material used.
"""
from __future__ import annotations
import copy
import unittest

from scripts.gt_spectrum_original_pass_states import validate
from scripts.b09_spectrum_topology_contract import PASSES


def synthetic_original():
    return {
        "m_Name": "UltimateWater/Spectrum/Water Spectrum",
        "m_PropInfo": {"m_Props": [{"m_Type": 4}, {"m_Type": 1}]},
        "m_SubShaders": [{"m_Passes": [
            {"m_Type": 0, "m_State": {"test_index": i}} for i in range(PASSES)
        ]}],
    }


def fake_source_state(state, *, allow_selective_color_mask=False):
    if allow_selective_color_mask is not True:
        raise ValueError("colour write mask support must be enabled")
    return "Blend One Zero\nZWrite On\nCull Back\nSourcePass " + str(
        state["test_index"])


class OriginalSpectrumStateTests(unittest.TestCase):
    def test_exact_seven_source_states_and_property_shape(self):
        result, texts = validate(
            synthetic_original(), serializer=fake_source_state)
        self.assertEqual(result["original_passes"], 7)
        self.assertEqual(result["original_property_count"], 2)
        self.assertEqual(result["original_texture_property_count"], 1)
        self.assertEqual(result["different_original_pass_state_blobs"], 7)
        self.assertEqual(result["state_hashes_privately_verified"], 7)
        self.assertEqual(len(texts), 7)
        self.assertFalse(result["Unity_ShaderLab_installed"])
        self.assertFalse(result["Android_Adreno_pixels_verified"])
        self.assertFalse(result["original_serialized_values_published"])

    def test_spectrum_phone_six_pass_floor_not_source_complete(self):
        scene = synthetic_original()
        scene["m_SubShaders"][0]["m_Passes"].pop()
        with self.assertRaisesRegex(ValueError, "seven_passes"):
            validate(scene, serializer=fake_source_state)

    def test_unsupported_pass_kind_or_state_fails_closed(self):
        for change in ("kind", "state"):
            scene = synthetic_original()
            if change == "kind":
                scene["m_SubShaders"][2-2]["m_Passes"][1]["m_Type"] = 1
            else:
                scene["m_SubShaders"][0]["m_Passes"][1]["m_State"] = None
            with self.subTest(change=change), self.assertRaisesRegex(
                ValueError, "pass_or_state"):
                validate(scene, serializer=fake_source_state)

    def test_unbound_original_property_schema_rejected(self):
        for invalid in (None, [{"m_Type": True}], [{"m_Type": "4"}]):
            scene = synthetic_original()
            scene["m_PropInfo"]["m_Props"] = invalid
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                ValueError, "property_schema"):
                validate(scene, serializer=fake_source_state)

    def test_unsupported_dynamic_source_state_refused(self):
        def never_fake_state(_state, *, allow_selective_color_mask=False):
            raise ValueError("dynamic unknown blend property")
        with self.assertRaisesRegex(ValueError, "dynamic unknown"):
            validate(synthetic_original(), serializer=never_fake_state)

    def test_blank_or_oversized_state_not_passed(self):
        for output in ("", "\x00", "x"*65537):
            with self.subTest(length=len(output)), self.assertRaisesRegex(
                    ValueError, "state_serialization_incomplete"):
                validate(synthetic_original(),
                         serializer=lambda _state, **_kw: output)

    def test_source_order_matters(self):
        scene = synthetic_original()
        scene["m_SubShaders"][0]["m_Passes"][3]["m_State"]["test_index"] = 13
        result, texts = validate(scene, serializer=fake_source_state)
        self.assertEqual(result["original_passes"], 7)
        self.assertIn(b"SourcePass 13", texts[3])
        self.assertNotIn(b"SourcePass 3", texts[3])


if __name__ == "__main__":
    unittest.main()
