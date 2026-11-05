import unittest

from t3_vf_spirv_component_coverage import classify_vf_components


def v(typ, loc=0, component=0):
    return {"type": typ, "location": loc, "component": component}


class VertexFragmentCoverageTests(unittest.TestCase):
    def test_split_compatible_components_are_only_structural_candidate(self):
        out = classify_vf_components([v("vec4")], [v("vec2", component=1), v("float", component=3)])
        self.assertEqual(out["status"], "STRUCTURAL_CANDIDATE_ONLY")
        self.assertEqual(out["fragment_input_components"], 3)
        self.assertEqual(out["extra_vertex_components"], 1)
        self.assertFalse(out["original_dxbc_semantics_verified"])
        self.assertFalse(out["interpolation_verified"])
        self.assertFalse(out["pixel_fidelity_verified"])

    def test_missing_fragment_lane(self):
        out = classify_vf_components([v("vec2")], [v("vec3")])
        self.assertEqual(out["status"], "STRUCTURAL_DEFICIT")
        self.assertEqual(out["missing_fragment_components"], 1)

    def test_equal_width_different_type_fails(self):
        out = classify_vf_components([v("ivec3")], [v("vec3")])
        self.assertEqual(out["typed_mismatch_components"], 3)
        self.assertEqual(out["status"], "STRUCTURAL_DEFICIT")

    def test_different_locations_never_assumed_corresponding(self):
        out = classify_vf_components([v("vec2", loc=1)], [v("vec2", loc=2)])
        self.assertEqual(out["missing_fragment_components"], 2)

    def test_extra_vertex_output_is_not_missing_fragment_input(self):
        out = classify_vf_components([v("vec2"), v("float", loc=3)], [v("vec2")])
        self.assertEqual(out["status"], "STRUCTURAL_CANDIDATE_ONLY")
        self.assertEqual(out["extra_vertex_components"], 1)

    def test_matrix_unsupported_is_inconclusive_not_a_match(self):
        out = classify_vf_components([v("mat4")], [v("vec4")])
        self.assertEqual(out["status"], "INCONCLUSIVE_UNSUPPORTED_TYPE")
        self.assertEqual(out["unsupported_type_records"], 1)

    def test_empty_user_varyings_never_claimed_proven(self):
        out = classify_vf_components([], [])
        self.assertEqual(out["status"], "NO_USER_VARYINGS")

    def test_builtin_only_does_not_create_fake_user_varying(self):
        out = classify_vf_components([{"builtin": "Position", "type": "vec4"}], [])
        self.assertEqual(out["excluded_builtin_records"], 1)
        self.assertEqual(out["status"], "NO_USER_VARYINGS")

    def test_same_location_disjoint_components_are_valid(self):
        out = classify_vf_components([v("vec2"), v("vec2", component=2)], [v("vec4")])
        self.assertEqual(out["status"], "STRUCTURAL_CANDIDATE_ONLY")

    def test_duplicate_component_rejected(self):
        with self.assertRaises(ValueError):
            classify_vf_components([v("vec2"), v("float", component=1)], [])

    def test_vector_crosses_location_rejected(self):
        with self.assertRaises(ValueError):
            classify_vf_components([v("vec4", component=1)], [])

    def test_unsanitized_name_rejected(self):
        with self.assertRaises(ValueError):
            classify_vf_components([{"location": 0, "type": "vec4", "name": "sensitive"}], [])

    def test_boolean_as_location_is_not_integer(self):
        with self.assertRaises(ValueError):
            classify_vf_components([{"location": True, "type": "vec4"}], [])

    def test_boolean_as_component_is_not_integer(self):
        with self.assertRaises(ValueError):
            classify_vf_components([{"location": 0, "type": "float", "component": False}], [])

    def test_unapproved_builtin_rejected(self):
        with self.assertRaises(ValueError):
            classify_vf_components([{"builtin": "secret_value"}], [])

    def test_bounded_input_rejected(self):
        with self.assertRaises(ValueError):
            classify_vf_components([v("float")] * 257, [])

    def test_output_contains_only_aggregate_fields(self):
        out = classify_vf_components([v("float", loc=2048)], [v("float", loc=2048)])
        self.assertNotIn("location", out)
        self.assertNotIn("type", out)
        self.assertNotIn("name", out)
        self.assertEqual(out["status"], "STRUCTURAL_CANDIDATE_ONLY")


if __name__ == "__main__":
    unittest.main()
