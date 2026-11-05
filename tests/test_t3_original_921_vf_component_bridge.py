"""Source-free security and component checks for real Shader48 bridge."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_921_vf_component_bridge as bridge

PRIVATE = "PRIVATE_SHADER_INTERFACE_NAME_DO_NOT_UPLOAD"
CODE = b"PRIVATE_SYNTHETIC_DXBC_NEVER_UPLOAD"


def raw_row(location=0, typ="vec4", component=0):
    return {"location": location, "component": component, "type": typ,
            "name": PRIVATE, "id": 42}


def raw_data(path: Path):
    vertex = path.parent.name.endswith("stage-1")
    loc = 4 if path.name == "roundtrip.spv" else 0
    row = raw_row(loc)
    return {"inputs": [] if vertex else [row],
            "outputs": [row] if vertex else []}


def old_data(path: Path):
    vertex = path.parent.name.endswith("stage-1")
    loc = 4 if path.name == "roundtrip.spv" else 0
    row = {"type": "vec4", "location": loc}
    return {"inputs": [] if vertex else [row],
            "outputs": [row] if vertex else [],
            "resource_slots": {"ubos": [[0, 0]]}}


def fake_translate(_code, _stage, destination):
    assert destination.is_dir()
    return {"vulkan11_valid": True, "hlsl_recovered": True,
            "roundtrip_vulkan11_valid": True, "private_hash": PRIVATE}


class PrivateComponentBridgeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="t3-vf-original-sourcefree-")
        self.addCleanup(tmp.cleanup)
        self.temp = Path(tmp.name)
        self.pairs = [(CODE + b"vertex", CODE + b"fragment") for _ in range(4)]

    def run_original(self, **kwargs):
        return bridge.classify_real_pairs(
            self.pairs, self.temp, translator=fake_translate,
            old_reflector=old_data, raw_reflector=raw_data, **kwargs)

    def test_four_original_source_and_roundtrip_pairs_structural_candidates(self):
        result = self.run_original()
        c = result["counts"]
        self.assertEqual(result["status"], bridge.STATUS)
        self.assertEqual(c["stage_spirv_source_and_roundtrip_reflections"], 8)
        self.assertEqual(c["source_passes_classified"], 4)
        self.assertEqual(c["roundtrip_passes_classified"], 4)
        self.assertEqual(c["source_status_STRUCTURAL_CANDIDATE_ONLY"], 4)
        self.assertEqual(c["roundtrip_status_STRUCTURAL_CANDIDATE_ONLY"], 4)
        self.assertEqual(c["source_fragment_input_components"], 16)
        self.assertEqual(c["roundtrip_vertex_output_components"], 16)
        self.assertFalse(result["Unity_Vulkan_Adreno_device_pixels_verified"])

    def test_generated_shader_names_ids_hashes_and_private_bytes_not_published(self):
        blob = json.dumps(self.run_original())
        self.assertNotIn(PRIVATE, blob)
        self.assertNotIn(CODE.decode(), blob)
        self.assertNotIn(str(self.temp), blob)
        self.assertNotIn("private_hash", blob)

    def test_location_component_retained_but_names_stripped(self):
        raw = {"outputs": [raw_row(10, "vec2", 2)]}
        old = {"outputs": [{"location": 10, "type": "vec2"}]}
        safe = bridge.sanitize_private_side(raw, old, "outputs")
        self.assertEqual(safe, [{"type": "vec2", "location": 10, "component": 2}])
        self.assertNotIn(PRIVATE, json.dumps(safe))

    def test_private_reflection_disagreeing_with_existing_safe_reflector_fails(self):
        old = {"outputs": [{"location": 2, "type": "vec4"}]}
        with self.assertRaisesRegex(ValueError, "disagrees_with_prior"):
            bridge.sanitize_private_side({"outputs": [raw_row(1)]}, old, "outputs")

    def test_duplicate_locations_disjoint_components_are_kept_for_classification(self):
        raw = {"outputs": [raw_row(0, "vec2", 0), raw_row(0, "vec2", 2)]}
        old = {"outputs": [{"type": "vec2", "location": 0}] * 2}
        safe = bridge.sanitize_private_side(raw, old, "outputs")
        self.assertEqual(len(safe), 2)

    def test_conflicting_component_lanes_are_not_reported_as_pass(self):
        def bad_raw(path):
            src = raw_data(path)
            if path.parent.name.endswith("stage-1"):
                src["outputs"] = [raw_row(0, "vec2", 0),
                                  raw_row(0, "vec2", 1)]
            return src
        def bad_old(path):
            src = old_data(path)
            if path.parent.name.endswith("stage-1"):
                src["outputs"] = [{"location": 0, "type": "vec2"}] * 2
            return src
        with self.assertRaisesRegex(ValueError, "duplicate occupied"):
            bridge.classify_real_pairs(self.pairs, self.temp,
                                       translator=fake_translate,
                                       raw_reflector=bad_raw,
                                       old_reflector=bad_old)

    def test_layout_array_decoration_is_not_silently_ignored(self):
        row = raw_row()
        row["array"] = [4]
        with self.assertRaisesRegex(ValueError, "unsupported_private"):
            bridge.sanitize_private_side({"inputs": [row]},
                                         {"inputs": [{"location": 0, "type": "vec4"}]},
                                         "inputs")

    def test_boolean_location_and_component_are_rejected(self):
        for field in ("location", "component"):
            row = raw_row()
            row[field] = True
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "invalid_private"):
                bridge.sanitize_private_side({"outputs": [row]},
                                             {"outputs": [{"location": 0, "type": "vec4"}]},
                                             "outputs")

    def test_unlocated_private_builtin_is_excluded_without_export(self):
        self.assertEqual(bridge.sanitize_private_side(
            {"outputs": [{"name": PRIVATE, "type": "vec4"}]},
            {"outputs": []}, "outputs"), [])

    def test_malicious_classifier_result_rejected(self):
        def leaking(_v, _f):
            return {"status": "STRUCTURAL_CANDIDATE_ONLY",
                    "private_name": PRIVATE}
        with self.assertRaisesRegex(ValueError, "untrusted_private"):
            self.run_original(classifier=leaking)

    def test_malicious_semantic_or_pixel_claim_is_rejected(self):
        from scripts.t3_vf_spirv_component_coverage import classify_vf_components
        def lying(v, f):
            r = classify_vf_components(v, f)
            r["pixel_fidelity_verified"] = True
            return r
        with self.assertRaisesRegex(ValueError, "unproven_component"):
            self.run_original(classifier=lying)

    def test_partial_translation_fails_closed(self):
        def partially_bad(_code, stage, _destination):
            return {"vulkan11_valid": stage == 1,
                    "hlsl_recovered": True, "roundtrip_vulkan11_valid": True}
        with self.assertRaisesRegex(ValueError, "incomplete_original_DXBC"):
            bridge.classify_real_pairs(self.pairs, self.temp,
                                       translator=partially_bad,
                                       old_reflector=old_data,
                                       raw_reflector=raw_data)

    def test_private_reflection_failure_fails_closed(self):
        def missing(_path):
            raise RuntimeError(PRIVATE)
        with self.assertRaises(RuntimeError):
            bridge.classify_real_pairs(self.pairs, self.temp,
                                       translator=fake_translate,
                                       old_reflector=old_data,
                                       raw_reflector=missing)

    def test_status_deficit_is_measured_and_aggregate_only(self):
        def fragment_drift(path):
            d = raw_data(path)
            if path.name == "roundtrip.spv" and path.parent.name.endswith("stage-0"):
                d["inputs"] = [raw_row(5)]
            return d
        def old_fragment_drift(path):
            d = old_data(path)
            if path.name == "roundtrip.spv" and path.parent.name.endswith("stage-0"):
                d["inputs"] = [{"location": 5, "type": "vec4"}]
            return d
        result = bridge.classify_real_pairs(
            self.pairs, self.temp, translator=fake_translate,
            old_reflector=old_fragment_drift, raw_reflector=fragment_drift)
        c = result["counts"]
        self.assertEqual(c["source_status_STRUCTURAL_CANDIDATE_ONLY"], 4)
        self.assertEqual(c["roundtrip_status_STRUCTURAL_DEFICIT"], 4)
        self.assertEqual(c["roundtrip_missing_fragment_components"], 16)

    def test_unknown_matrix_layout_is_inconclusive(self):
        def matrix_raw(path):
            d = raw_data(path)
            key = "outputs" if path.parent.name.endswith("stage-1") else "inputs"
            d[key][0]["type"] = "mat4"
            return d
        def matrix_old(path):
            d = old_data(path)
            key = "outputs" if path.parent.name.endswith("stage-1") else "inputs"
            d[key][0]["type"] = "mat4"
            return d
        result = bridge.classify_real_pairs(
            self.pairs, self.temp, translator=fake_translate,
            old_reflector=matrix_old, raw_reflector=matrix_raw)
        self.assertEqual(result["counts"]["source_status_INCONCLUSIVE_UNSUPPORTED_TYPE"], 4)
        self.assertEqual(result["counts"]["roundtrip_status_INCONCLUSIVE_UNSUPPORTED_TYPE"], 4)

    def test_scope_requires_four_true_compiled_stage_pairs(self):
        with self.assertRaisesRegex(ValueError, "invalid_original_four_pass"):
            bridge.classify_real_pairs(self.pairs[:3], self.temp)

    def test_aggregate_does_not_allow_arbitrary_status(self):
        from scripts.t3_vf_spirv_component_coverage import classify_vf_components
        x = classify_vf_components([], [])
        x["status"] = PRIVATE
        with self.assertRaisesRegex(ValueError, "invalid_component_classification_status"):
            bridge.safe_aggregate(x)


if __name__ == "__main__":
    unittest.main()
