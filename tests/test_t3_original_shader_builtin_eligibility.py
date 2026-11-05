"""T3 source-only exact Unity 2021 built-in-name candidacy: privacy/negative tests."""
import json
import unittest

from scripts import t3_original_shader_builtin_eligibility as b
from scripts import t3_original_renderer_shader_impact as original


def fixture():
    keys = [
        ("sharedassets0.assets", 101),
        ("sharedassets0.assets", 202),
        ("sharedassets0.assets", 303),
    ]
    weights = dict(zip(keys, (5, 3, 1)))
    names = {
        keys[0]: ("synthetic-built-in", None),
        keys[1]: ("synthetic-custom", None),
        keys[2]: ("synthetic-built-in-two", None),
    }
    result = {
        "status": original.STATUS,
        "six_original_scenes_sha_verified": True,
        "original_selected_shader_owners_sha_verified": 4,
        "original_material_target_owners_sha_verified": 3,
        "original_distinct_typed_Shader48_targets": 3,
        "counts": {"original_slots_to_verified_Shader48": 9},
        "top_ten_typed_Shader48_slot_counts_no_identity": [5, 3, 1],
    }
    return keys, weights, names, result


def compare(weights, names, report, vendors):
    return b.compare(weights, names, vendors, report,
                     target_count=3, slot_count=9, top_use=5)


class OriginalBuiltinEligibility(unittest.TestCase):
    def test_top_921_analog_official_candidate_and_weighted_totals(self):
        keys, weights, names, report = fixture()
        output = compare(weights, names, report,
                         {"synthetic-built-in", "synthetic-built-in-two"})
        self.assertEqual(output["source_Shaders_checked"], 3)
        self.assertTrue(output["top_921_source_Shader_name_exactly_in_2021_builtin_list"])
        self.assertEqual(output["source_Shader48_objects_with_exact_official_builtin_names"], 2)
        self.assertEqual(output["original_renderer_slots_using_exact_official_builtin_name_candidates"], 6)
        self.assertEqual(output["original_renderer_slots_with_nonbuiltin_name_candidates"], 3)
        self.assertFalse(output["original_to_export_Shader_GUID_program_or_compiled_variant_verified"])

    def test_top_not_official_no_silent_promotion(self):
        keys, weights, names, report = fixture()
        output = compare(weights, names, report, {"synthetic-built-in-two"})
        self.assertFalse(output["top_921_source_Shader_name_exactly_in_2021_builtin_list"])
        self.assertEqual(output["original_renderer_slots_using_exact_official_builtin_name_candidates"], 1)

    def test_every_name_and_original_identifier_remains_private(self):
        keys, weights, names, report = fixture()
        output = compare(weights, names, report, {"synthetic-built-in"})
        blob = json.dumps(output)
        for secret in ("synthetic-built-in", "synthetic-custom", "synthetic-built-in-two",
                       "sharedassets0.assets", "101", "202", "303"):
            # Check private strings, not arbitrary integers embedded in published counts.
            if secret.isdigit():
                continue
            self.assertNotIn(secret, blob)
        self.assertTrue(output["source_shader_names_ids_guids_per_identity_hashes_disclosed"] is False)

    def test_duplicate_name_rejected(self):
        keys, weights, names, report = fixture()
        names[keys[1]] = names[keys[0]]
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            compare(weights, names, report, {"synthetic-built-in"})

    def test_conflicting_parser_and_serialized_name_rejected(self):
        keys, weights, names, report = fixture()
        names[keys[1]] = ("real", "different")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            compare(weights, names, report, {"real"})

    def test_missing_source_name_does_not_count_as_nonvendor(self):
        keys, weights, names, report = fixture()
        names[keys[0]] = (None, None)
        with self.assertRaisesRegex(ValueError, "missing_or_ambiguous"):
            compare(weights, names, report, {"synthetic-built-in"})

    def test_wrong_or_unverified_source_population_rejected(self):
        keys, weights, names, report = fixture()
        report["six_original_scenes_sha_verified"] = False
        with self.assertRaisesRegex(ValueError, "untrusted_source"):
            compare(weights, names, report, {"synthetic-built-in"})
        report["six_original_scenes_sha_verified"] = True
        report["original_selected_shader_owners_sha_verified"] = 3
        with self.assertRaisesRegex(ValueError, "untrusted_source"):
            compare(weights, names, report, {"synthetic-built-in"})

    def test_reject_missing_original_shader_identity_even_if_counts_match(self):
        keys, weights, names, report = fixture()
        names.pop(keys[0])
        with self.assertRaisesRegex(ValueError, "untrusted_source"):
            compare(weights, names, report, {"synthetic-built-in"})

    def test_wrong_or_ambiguous_921_slot_target_rejected(self):
        keys, weights, names, report = fixture()
        weights[keys[0]] = 4
        weights[keys[1]] = 4
        weights[keys[2]] = 1
        with self.assertRaisesRegex(ValueError, "invalid_original"):
            compare(weights, names, report, {"synthetic-built-in"})
        weights[keys[0]] = 5
        weights[keys[1]] = 5
        weights[keys[2]] = 1
        with self.assertRaisesRegex(ValueError, "invalid_original"):
            compare(weights, names, report, {"synthetic-built-in"})

    def test_nonpositive_shader_identity_and_bool_weight_rejected(self):
        keys, weights, names, report = fixture()
        bad_key = ("sharedassets0.assets", 0)
        weights[bad_key] = weights.pop(keys[2])
        names[bad_key] = names.pop(keys[2])
        with self.assertRaisesRegex(ValueError, "invalid_source_Shader48_identity_shape"):
            compare(weights, names, report, {"synthetic-built-in"})
        weights[bad_key] = True
        with self.assertRaises(ValueError):
            compare(weights, names, report, {"synthetic-built-in"})

    def test_vendor_name_membership_must_be_exact_and_case_sensitive(self):
        keys, weights, names, report = fixture()
        output = compare(weights, names, report, {"SYNTHETIC-BUILT-IN"})
        self.assertFalse(output["top_921_source_Shader_name_exactly_in_2021_builtin_list"])
        self.assertEqual(output["source_Shader48_objects_with_exact_official_builtin_names"], 0)
        with self.assertRaisesRegex(ValueError, "bad_authentic_official"):
            compare(weights, names, report, ["synthetic-built-in"])


if __name__ == "__main__":
    unittest.main()
