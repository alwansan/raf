"""T3 original four-Pass opt-in reflected-name I/O privacy integration tests."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_top_shader_fourpass_translation as translator
from scripts.t3_spirv_interface_name_drift import classify_reflected_names
from scripts.t3_stage_io_drift import classify_stage_io

SECRET = "PRIVATE_COMPILER_GENERATED_INTERFACE_NAME"


def fake_translate(_code, _stage, _destination):
    return {"vulkan11_valid": True, "hlsl_recovered": True,
            "roundtrip_vulkan11_valid": True, "private_source_sha": SECRET}


def sanitized(path):
    loc = 4 if path.name == "roundtrip.spv" else 0
    if path.parent.name.endswith("stage-1"):
        return {"inputs": [], "outputs": [{"location": loc, "type": "vec4"}],
                "resource_slots": {"ubos": [[0, 0]]}}
    return {"inputs": [{"location": loc, "type": "vec4"}], "outputs": [],
            "resource_slots": {"ubos": [[0, 0]]}}


def names(path):
    result = sanitized(path)
    for side in ("inputs", "outputs"):
        for row in result[side]:
            row["name"] = SECRET
    return result


class FourPassNamedIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="t3-spv-names-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_four(self, **kwargs):
        pairs = [(b"synthetic-private-vertex", b"synthetic-private-fragment") for _ in range(4)]
        return translator.evaluate_samples(pairs, self.root, translator=fake_translate,
                                           reflector=sanitized, **kwargs)

    def test_exact_four_passes_relocated_names_not_original_semantic_proof(self):
        out = self.run_four(io_classifier=classify_stage_io,
                            name_classifier=classify_reflected_names,
                            named_reflector=names)
        c = out["counts"]
        self.assertEqual(out["status"], translator.NAME_STATUS)
        self.assertTrue(out["reflected_names_are_NOT_authenticated_source_DXBC_semantics"])
        self.assertTrue(out["source_to_roundtrip_reflected_name_all_eight_stages_compared"])
        self.assertEqual(c["name_drift_stage_reflection_pairs_classified"], 8)
        self.assertEqual(c["name_drift_inputs_source_name_type_relocated"], 4)
        self.assertEqual(c["name_drift_outputs_source_name_type_relocated"], 4)
        self.assertEqual(c["name_drift_inputs_name_type_complete_preservation"], 8)
        self.assertEqual(c["name_drift_outputs_name_type_complete_preservation"], 8)
        self.assertEqual(c["io_drift_stage_reflection_pairs_classified"], 8)
        self.assertNotIn(SECRET, json.dumps(out))

    def test_default_original_stage_status_unchanged(self):
        out = self.run_four()
        self.assertEqual(out["status"], translator.STATUS)
        self.assertFalse(out["source_to_roundtrip_reflected_name_comparison_opt_in"])
        self.assertFalse(any(k.startswith("name_drift") for k in out["counts"]))

    def test_name_classifier_requires_simultaneous_IO_baseline(self):
        with self.assertRaisesRegex(ValueError, "requires_concurrent_stage_IO_baseline"):
            self.run_four(name_classifier=classify_reflected_names,
                          named_reflector=names)

    def test_malicious_classifier_fields_not_published(self):
        def malicious(_a, _b, _c, _d):
            return {"secret_material_name": SECRET}
        with self.assertRaisesRegex(ValueError, "untrusted_private_SPIRV_name_classifier"):
            self.run_four(io_classifier=classify_stage_io,
                          name_classifier=malicious, named_reflector=names)

    def test_nonconforming_raw_names_must_match_sanitized_previous_reflection(self):
        def forged(_path):
            return {"inputs": [], "outputs": []}
        with self.assertRaisesRegex(ValueError, "disagrees_with_safe_IO_baseline"):
            self.run_four(io_classifier=classify_stage_io,
                          name_classifier=classify_reflected_names,
                          named_reflector=forged)


if __name__ == "__main__":
    unittest.main()
