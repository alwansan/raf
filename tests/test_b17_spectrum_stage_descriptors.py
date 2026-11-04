"""Source-free controls for B17 Spectrum original resource table census."""
import math
import unittest
from scripts.b17_spectrum_stage_descriptors import (
    numeric_tree, stage_profile, summarize_passes, PASSES,
)


def program(slot=0, *, empty=False):
    return {"m_CommonParameters": {
        "m_TextureParameters": [] if empty else [{"m_NameIndex": 2,
                          "m_Index": slot, "m_ArraySize": 1}],
        "m_SamplerParameters": [] if empty else [{"m_NameIndex": 3,
                          "m_Index": 1, "m_ArraySize": 1}],
        "m_ConstantBuffers": [{"m_NameIndex": 0, "m_Size": 112}],
    }}


def passes():
    return [{"progVertex": program(i, empty=True),
             "progFragment": program(i)} for i in range(PASSES)]


class SpectrumDescriptorTests(unittest.TestCase):
    def test_valid_program(self):
        report = summarize_passes(passes())
        self.assertEqual(report["original_pass_count"], 7)
        self.assertEqual(report["stage_descriptor_table_counts"]["fragment_rows"], 14)
        self.assertEqual(report["stage_descriptor_table_counts"]["vertex_rows"], 0)
        self.assertFalse(report["ready_for_build"])

    def test_real_numeric_changes_are_detected(self):
        items = passes()
        a = summarize_passes(items)
        items[3]["progFragment"]["m_CommonParameters"]["m_TextureParameters"][0]["m_Index"] += 1
        b = summarize_passes(items)
        self.assertNotEqual(
            a["per_pass_stage_numeric_contract"][3]["progFragment"]["numeric_descriptor_sha256"],
            b["per_pass_stage_numeric_contract"][3]["progFragment"]["numeric_descriptor_sha256"])

    def test_fail_closed_missing_pass(self):
        with self.assertRaises(ValueError):
            summarize_passes(passes()[:-1])

    def test_fail_closed_missing_stage(self):
        items = passes()
        del items[0]["progFragment"]
        with self.assertRaises(ValueError):
            summarize_passes(items)

    def test_fail_closed_unknown_resource_alias(self):
        p = program()
        p["m_CommonParameters"]["m_TextureMagicalBindings"] = []
        with self.assertRaises(ValueError):
            stage_profile(p)

    def test_authenticated_uavparams_field_is_numeric_only(self):
        p = program()
        p["m_CommonParameters"]["m_UAVParams"] = [
            {"m_NameIndex": 1, "m_Index": 2, "m_ArraySize": 1},
        ]
        profile = stage_profile(p)
        self.assertEqual(profile["table_rows"]["m_UAVParams"], 1)
        self.assertEqual(profile["descriptor_rows"], 3)
        self.assertNotIn("m_Index", str(profile))


    def test_fail_closed_unknown_all_tables(self):
        for item in passes():
            for stage in ("progVertex", "progFragment"):
                item[stage]["m_CommonParameters"] = {"m_ConstantBuffers": []}
        with self.assertRaises(ValueError):
            summarize_passes(passes_empty := [{
                "progVertex": {"m_CommonParameters": {"m_ConstantBuffers": []}},
                "progFragment": {"m_CommonParameters": {"m_ConstantBuffers": []}},
            } for _ in range(PASSES)])

    def test_fail_closed_nonnumeric_name(self):
        with self.assertRaises(ValueError):
            numeric_tree({"m_NameIndex": "original-name-hidden"})

    def test_fail_closed_boolean_pretending_int(self):
        with self.assertRaises(ValueError):
            numeric_tree({"m_Index": True})

    def test_original_multisampled_bool_is_typed_not_integer_slot(self):
        base = numeric_tree({"m_NameIndex": 1, "m_Index": 2,
                             "m_MultiSampled": False})
        changed = numeric_tree({"m_NameIndex": 1, "m_Index": 2,
                                "m_MultiSampled": True})
        self.assertNotEqual(base, changed)
        self.assertEqual(base["m_MultiSampled"], {"__typed_multisampled_bool__": 0})
        self.assertEqual(changed["m_MultiSampled"], {"__typed_multisampled_bool__": 1})

    def test_original_multisampled_rejects_integer_substitution(self):
        with self.assertRaises(ValueError):
            numeric_tree({"m_MultiSampled": 1})
        with self.assertRaises(ValueError):
            numeric_tree({"m_MultiSampled": "false"})

    def test_fail_closed_nonfinite_float(self):
        with self.assertRaises(ValueError):
            numeric_tree({"m_Value": math.inf})

    def test_fail_closed_invalid_key(self):
        with self.assertRaises(ValueError):
            numeric_tree({"game proprietary name": 0})

    def test_fail_closed_deep_nested(self):
        nested = 1
        for _ in range(8):
            nested = {"m_Next": nested}
        with self.assertRaises(ValueError):
            numeric_tree(nested)

    def test_fail_closed_oversize_list(self):
        with self.assertRaises(ValueError):
            stage_profile({"m_CommonParameters": {"m_TextureParameters": [0] * 257}})

    def test_no_original_program_or_names_in_report(self):
        rendered = str(summarize_passes(passes()))
        for forbidden in ("original-name-hidden", "m_NameIndex", "m_Index",
                          "raw_shader", "compiled_program"):
            self.assertNotIn(forbidden, rendered)
        self.assertIn("ready_for_build': False", rendered)


if __name__ == "__main__":
    unittest.main()
