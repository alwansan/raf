"""T3 source-free original PS DXBC ReadWriteMask vs SPIR-V input lane tests."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_921_dxbc_readmask_spirv as probe
from scripts import t3_original_921_dxbc_semantic_join as sem

SECRET = "PRIVATE_ORIGINAL_SEMANTIC_SHOULD_NOT_BE_LOGGED"
CODE = b"ORIGINAL_PRIVATE_DXBC_SHOULD_NEVER_ESCAPE"


def row(*, declared=15, read=3, system=0, name=SECRET, reg=0):
    return {
        "semantic": name, "index": 0, "system_value": system,
        "type": 3, "register": reg, "mask": declared,
        "used_mask": read, "stream": 0,
    }


def fakes(code):
    if code.endswith(b"_vertex"):
        return {"input": [], "output": [row()], "input_tag": "ISGN",
                "output_tag": "OSGN"}
    return {"input": [row()], "output": [], "input_tag": "ISGN",
            "output_tag": "OSGN"}


def translated(_code, stage, root):
    assert stage == 0
    assert root.is_dir()
    return {"vulkan11_valid": True, "hlsl_recovered": True,
            "roundtrip_vulkan11_valid": True,
            "private_source_secret": SECRET}


def reflection(_spv):
    return {"inputs": [{"location": 2, "type": "vec2"}],
            "outputs": [], "resource_slots": {}}


class TestFragmentReadMaskDiagnostic(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix="t3-private-ps-readmask-")
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)
        self.samples = [
            (CODE + b"_vertex", CODE + b"_fragment") for _ in range(4)]

    def run_probe(self, **kwargs):
        return probe.evaluate_private_fourpass(
            self.samples, self.root, translator=translated,
            reflector=reflection, parser=fakes, **kwargs)

    def test_four_source_paired_actual_read_masks_agree_with_original_spirv(self):
        result = self.run_probe()
        c = result["counts"]
        self.assertEqual(c["passes_examined"], 4)
        self.assertEqual(c["source_ps_user_semantic_records"], 4)
        self.assertEqual(c["source_ps_declared_component_lanes"], 16)
        self.assertEqual(c["source_ps_read_component_lanes"], 8)
        self.assertEqual(c["source_ps_declared_but_unread_component_lanes"], 8)
        self.assertEqual(c["source_spirv_fragment_input_component_lanes"], 8)
        self.assertEqual(c["roundtrip_spirv_fragment_input_component_lanes"], 8)
        self.assertEqual(c["passes_readmask_equals_source_spirv_input_lane_count"], 4)
        self.assertEqual(c["passes_readmask_equals_roundtrip_spirv_input_lane_count"], 4)
        self.assertEqual(c["source_to_spirv_absolute_component_lane_count_difference"], 0)
        self.assertFalse(result["SPIRV_name_Location_to_original_DXBC_semantic_mapping_proven"])

    def test_declared_and_read_mask_components_are_independently_counted(self):
        d = probe.private_fragment_readmask([row(declared=15, read=5)])
        self.assertEqual(d["source_ps_declared_component_lanes"], 4)
        self.assertEqual(d["source_ps_read_component_lanes"], 2)
        self.assertEqual(d["source_ps_declared_but_unread_component_lanes"], 2)
        self.assertEqual(d["source_ps_partly_unread_user_semantic_records"], 1)

    def test_completely_unread_fragment_input_is_not_discarded(self):
        d = probe.private_fragment_readmask([row(read=0)])
        self.assertEqual(d["source_ps_read_component_lanes"], 0)
        self.assertEqual(d["source_ps_completely_unread_user_semantic_records"], 1)
        self.assertEqual(d["source_ps_declared_but_unread_component_lanes"], 4)

    def test_all_read_lanes_do_not_create_unused_mask(self):
        d = probe.private_fragment_readmask([row(read=15)])
        self.assertEqual(d["source_ps_declared_but_unread_component_lanes"], 0)
        self.assertEqual(d["source_ps_partly_unread_user_semantic_records"], 0)

    def test_input_read_mask_subset_is_mandatory(self):
        for used in (16, -1, 4, 15):
            d = row(declared=3, read=used)
            with self.subTest(used=used), self.assertRaisesRegex(ValueError, "read_mask_subset"):
                probe.private_fragment_readmask([d])

    def test_system_values_excluded_from_user_lane_counts(self):
        d = probe.private_fragment_readmask([row(), row(name="SV_Position", system=1, reg=0xffffffff)])
        self.assertEqual(d["source_ps_user_semantic_records"], 1)
        self.assertEqual(d["source_ps_system_value_records"], 1)
        self.assertEqual(d["source_ps_declared_component_lanes"], 4)

    def test_invalid_row_extra_private_attribute_rejected(self):
        d = row()
        d["unsafe_private_debug_path"] = SECRET
        with self.assertRaisesRegex(ValueError, "signature_record_shape"):
            probe.private_fragment_readmask([d])

    def test_boolean_like_int_masks_rejected(self):
        for key in ("mask", "used_mask", "register", "system_value"):
            d = row()
            d[key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "signature_field"):
                probe.private_fragment_readmask([d])

    def test_input_record_cap_rejected(self):
        with self.assertRaisesRegex(ValueError, "signature_list"):
            probe.private_fragment_readmask([row()] * 257)

    def test_reflection_scalar_and_vectors_are_counted_not_names(self):
        report = probe.safe_reflected_fragment_input_counts({
            "inputs": [
                {"location": 0, "type": "float"},
                {"location": 1, "type": "vec3"},
                {"location": 3, "type": "uvec2"}],
            "outputs": [], "resource_slots": {}
        })
        self.assertEqual(report, {"records": 3, "lanes": 6})

    def test_reflection_unknown_matrix_does_not_prove_match(self):
        with self.assertRaisesRegex(ValueError, "unsupported_SPIRV"):
            probe.safe_reflected_fragment_input_counts({
                "inputs": [{"location": 0, "type": "mat4"}],
                "outputs": [], "resource_slots": {}})

    def test_reflection_extra_private_name_rejected(self):
        with self.assertRaisesRegex(ValueError, "untrusted_private_SPIRV"):
            probe.safe_reflected_fragment_input_counts({
                "inputs": [{"location": 0, "type": "float", "name": SECRET}],
                "outputs": [], "resource_slots": {}})

    def test_reflection_bool_location_rejected(self):
        with self.assertRaisesRegex(ValueError, "untrusted_private_SPIRV"):
            probe.safe_reflected_fragment_input_counts({
                "inputs": [{"location": True, "type": "float"}],
                "outputs": [], "resource_slots": {}})

    def test_mismatched_source_input_count_is_observed_not_hidden(self):
        def changed(_path):
            return {"inputs": [{"location": 0, "type": "vec3"}],
                    "outputs": [], "resource_slots": {}}
        result = self.run_probe(reflector=changed)
        c = result["counts"]
        self.assertEqual(c["passes_readmask_equals_source_spirv_input_lane_count"], 0)
        self.assertEqual(c["source_to_spirv_absolute_component_lane_count_difference"], 4)

    def test_original_vs_roundtrip_differences_remain_visible(self):
        def derived_changed(path):
            typ = "vec4" if path.name == "roundtrip.spv" else "vec2"
            return {"inputs": [{"location": 0, "type": typ}],
                    "outputs": [], "resource_slots": {}}
        result = self.run_probe(reflector=derived_changed)
        c = result["counts"]
        self.assertEqual(c["passes_source_spirv_equals_roundtrip_spirv_input_lane_count"], 0)
        self.assertEqual(c["passes_readmask_equals_source_spirv_input_lane_count"], 4)
        self.assertEqual(c["passes_readmask_equals_roundtrip_spirv_input_lane_count"], 0)

    def test_missing_vertex_semantic_is_not_silent(self):
        def wrong_checker(v, f):
            d = sem.compare_original_vf(v, f)
            d["original_unmatched_fragment_semantic_records"] = 1
            return d
        with self.assertRaisesRegex(ValueError, "source_original_DXBC"):
            self.run_probe(match_checker=wrong_checker)

    def test_fragment_read_not_covered_by_vertex_mask_fails_structural_proof(self):
        def wrong_vertex_parser(code):
            d = fakes(code)
            if code.endswith(b"_vertex"):
                d["output"][0]["mask"] = 1
            return d
        with self.assertRaisesRegex(ValueError, "source_original_DXBC"):
            probe.evaluate_private_fourpass(
                self.samples, self.root, translator=translated,
                reflector=reflection, parser=wrong_vertex_parser)

    def test_missing_one_original_translator_phase_fails(self):
        def incomplete(_code, _stage, _root):
            return {"vulkan11_valid": True, "hlsl_recovered": True,
                    "roundtrip_vulkan11_valid": False}
        with self.assertRaisesRegex(ValueError, "partial_original_PS"):
            self.run_probe(translator=incomplete)

    def test_incomplete_private_fourpass_scope_rejected(self):
        with self.assertRaisesRegex(ValueError, "not_original_fourpass"):
            probe.evaluate_private_fourpass(self.samples[:3], self.root)

    def test_result_is_aggregate_only_no_private_semantic_or_code(self):
        s = json.dumps(self.run_probe(), sort_keys=True)
        for secret in (SECRET, CODE.decode(), str(self.root), "DXBC_SHOULD_NEVER"):
            self.assertNotIn(secret, s)
        self.assertFalse(self.run_probe_in_distinct_dir()["private_names_bytecode_or_compiler_code_published"])

    def run_probe_in_distinct_dir(self):
        # Avoid trying to reuse already created private output dirs.
        with tempfile.TemporaryDirectory(prefix="t3-distinct-sample-") as td:
            return probe.evaluate_private_fourpass(
                self.samples, Path(td), translator=translated,
                reflector=reflection, parser=fakes)

    def test_no_false_spirv_semantic_binding_claim(self):
        result = self.run_probe()
        self.assertFalse(result["original_DXBC_register_readmask_vs_SPIRV_same_component_identity_proven"])
        self.assertFalse(result["interpolation_ShaderLab_color_or_pixel_fidelity_proven"])
        self.assertFalse(result["Unity_Android_Adreno_pixels_verified"])


if __name__ == "__main__":
    unittest.main()
