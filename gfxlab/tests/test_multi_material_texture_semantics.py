import unittest
from gfxlab.tools.multi_material_texture_semantics import (
    named_entries, safe_enum_code, uv_is_identity, channel_variability,
)

class FakeChannel:
    def __init__(self, extrema):
        self.extrema = extrema
    def getextrema(self):
        return self.extrema

class FakeImage:
    def __init__(self, extrema):
        self.extrema = extrema
    def convert(self, mode):
        if mode != "RGBA":
            raise AssertionError(mode)
        return self
    def split(self):
        return [FakeChannel(x) for x in self.extrema]

class TestMaterialTextureSemantics(unittest.TestCase):
    def test_named_entries_accepts_tuple_and_unity_pair_dict(self):
        result = named_entries([
            ("private_name_a", {"v": 1}),
            {"m_First": "private_name_b", "m_Second": 2.0},
        ])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1][1], 2.0)

    def test_named_entries_accepts_singleton_mapping(self):
        self.assertEqual(named_entries([{"private_name": 7}])[0][1], 7)

    def test_named_entries_rejects_duplicate_names(self):
        with self.assertRaises(ValueError):
            named_entries([("same", 1), ("same", 2)])

    def test_named_entries_rejects_malformed_pair(self):
        with self.assertRaises(ValueError):
            named_entries([{"unexpected": 1, "shape": 2}])

    def test_safe_enum_code_does_not_infer_unknown(self):
        self.assertEqual(safe_enum_code(12), "12")
        self.assertEqual(safe_enum_code(None), "unknown")
        self.assertEqual(safe_enum_code("DXT5"), "unknown")

    def test_uv_identity_requires_unit_scale_and_zero_offset(self):
        self.assertTrue(uv_is_identity([1.0, 1.0], [0.0, 0.0]))
        self.assertFalse(uv_is_identity([2.0, 1.0], [0.0, 0.0]))
        self.assertFalse(uv_is_identity([1.0, 1.0], [0.25, 0.0]))

    def test_channel_variability_is_boolean_only(self):
        image = FakeImage([(0, 0), (1, 200), (0, 0), (255, 255)])
        result = channel_variability(image)
        self.assertEqual(result, {
            "R": False, "G": True, "B": False, "A": False,
            "alpha_fully_opaque": True,
        })

    def test_channel_variability_rejects_bad_channel_range(self):
        image = FakeImage([(0, 256), (0, 1), (0, 1), (0, 1)])
        with self.assertRaises(ValueError):
            channel_variability(image)

    def test_channel_variability_rejects_wrong_channel_count(self):
        class BadImage(FakeImage):
            def split(self):
                return [FakeChannel((0, 1))]
        with self.assertRaises(ValueError):
            channel_variability(BadImage([(0, 1)]))
