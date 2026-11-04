"""B45 strict original Blur texture-property synthetic contract tests."""
import copy
import math
import unittest

from scripts.b45_blur_properties import serialize_properties


def fixture():
    return {"m_PropInfo": {"m_Props": [{
        "m_Name": "_SyntheticTex", "m_Description": "Test texture",
        "m_Attributes": [], "m_Type": 4, "m_Flags": 0,
        "m_DefValue[0]": 0.0, "m_DefValue[1]": 0.0,
        "m_DefValue[2]": 0.0, "m_DefValue[3]": 0.0,
        "m_DefTexture": {"m_DefaultName": "white", "m_TexDim": 2},
    }]}}


class BlurMaterialPropertyTests(unittest.TestCase):
    def test_exact_original_fields_are_preserved(self):
        result = serialize_properties(fixture())
        self.assertIn('_SyntheticTex ("Test texture", 2D) = "white" {}', result)
        self.assertTrue(result.startswith("Properties {"))
        self.assertEqual(result.count("_SyntheticTex"), 1)

    def test_original_other_dimensions_and_defaults_not_guessed(self):
        for dim, label in {1: "any", 3: "3D", 4: "Cube", 5: "2DArray", 6: "CubeArray"}.items():
            instance = fixture()
            prop = instance["m_PropInfo"]["m_Props"][0]
            prop["m_DefTexture"]["m_TexDim"] = dim
            prop["m_DefTexture"]["m_DefaultName"] = ""
            self.assertIn(f", {label}) = \"\" {{}}", serialize_properties(instance))

    def test_reject_unexpected_counts_and_raw_property_keys(self):
        for mutate in ("none", "two", "unknown"):
            instance = fixture()
            props = instance["m_PropInfo"]["m_Props"]
            if mutate == "none": props.clear()
            if mutate == "two": props.append(copy.deepcopy(props[0]))
            if mutate == "unknown": props[0]["private_unknown"] = 123
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                serialize_properties(instance)

    def test_reject_unrecognized_semantics_without_defaults(self):
        for field, value in (("m_Type", 3), ("m_Flags", 1),
                             ("m_Attributes", ["HDR"]), ("m_Name", "bad Name"),
                             ("m_Description", "evil\nnew line"),
                             ("m_DefValue[0]", math.nan)):
            instance = fixture()
            instance["m_PropInfo"]["m_Props"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                serialize_properties(instance)

    def test_reject_bad_texture_dim_default_and_injection(self):
        for key, value in (("m_TexDim", 99), ("m_TexDim", True),
                           ("m_DefaultName", "custom/asset"),
                           ("m_DefaultName", 'black\" {}\nPass {')):
            instance = fixture()
            instance["m_PropInfo"]["m_Props"][0]["m_DefTexture"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                serialize_properties(instance)

    def test_does_not_mutate_original_data(self):
        instance = fixture()
        snapshot = copy.deepcopy(instance)
        serialize_properties(instance)
        self.assertEqual(instance, snapshot)


if __name__ == "__main__":
    unittest.main()
