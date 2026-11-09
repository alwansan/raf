"""No-game synthetic linked PS and explicit SPIR-V metadata pipeline controls."""
from pathlib import Path
import json
import tempfile
import unittest

from scripts import t3_original_smoke34_usersemantic_probe as t3
from test_t3_smoke34_spirv_usersemantic_annotations import module, SECRET

PRIVATE_CODE = b"PRIVATE_FAKE_COMPILED_DXBC"


def pairs():
    return [(PRIVATE_CODE+b"_VS_0", PRIVATE_CODE+b"_PS_0"),
            (PRIVATE_CODE+b"_VS_1", PRIVATE_CODE+b"_PS_1")]


def parser(code):
    suffix = code.rsplit(b"_", 2)
    stage, idx = suffix[-2], int(suffix[-1])
    n = 3 + idx
    source = [{"semantic": SECRET, "index": k, "system_value": 0,
               "type": 3, "register": k, "mask": 15, "used_mask": 7,
               "stream": 0} for k in range(n)]
    if stage == b"VS":
        return {"input": [], "output": source, "input_tag": "ISGN",
                "output_tag": "OSGN"}
    if stage == b"PS":
        return {"input": source, "output": [], "input_tag": "ISGN",
                "output_tag": "OSGN"}
    raise ValueError("malicious_stage")


def translator(_code, stage, folder):
    assert stage == 0 and folder.is_dir()
    idx = int(folder.name.split("-")[3])
    locs = tuple(range(3+idx))
    for filename in ("original.spv", "roundtrip.spv"):
        (folder/filename).write_bytes(module(locations=locs))
    return {"stage": 0, "vulkan11_valid": True,
            "hlsl_recovered": True, "roundtrip_vulkan11_valid": True,
            "original_private_bytecode": PRIVATE_CODE.decode()}


def reflector(path):
    idx = int(path.parent.name.split("-")[3])
    return {"inputs": [{"location": i, "type": "vec4"}
                       for i in range(3+idx)], "outputs": [], "resource_slots": {}}


class OriginalSmokeUserSemanticProbeTests(unittest.TestCase):
    def setUp(self):
        private = tempfile.TemporaryDirectory(prefix="t3-spv-usermetadata-")
        self.addCleanup(private.cleanup)
        self.root = Path(private.name)

    def evaluate(self, **kwargs):
        return t3.evaluate(kwargs.get("pairs", pairs()), self.root,
                           reader=kwargs.get("reader", parser),
                           translator=kwargs.get("translator", translator),
                           reflector=kwargs.get("reflector", reflector),
                           scanner=kwargs.get("scanner",
                                              t3.annotations.parse_private_spirv),
                           classifier=kwargs.get("classifier",
                                                t3.annotations.classify_original_and_spirv))

    def test_empty_metadata_yields_only_structural_numeric_candidates(self):
        report = self.evaluate()
        c = report["counts"]
        self.assertEqual(c["genuine_fragment_pairs_examined"], 2)
        self.assertEqual(c["original_original_dx_user_input_records"], 7)
        self.assertEqual(c["roundtrip_original_dx_declared_lanes"], 28)
        self.assertEqual(c["original_reflected_spirv_input_records"], 7)
        self.assertEqual(c["original_register_location_same_number_candidates"], 7)
        self.assertEqual(c["original_spv_explicit_semantic_matches_original"], 0)
        self.assertEqual(c["roundtrip_spv_semantic_decorated_input_variables"], 0)
        self.assertFalse(report["original_DXBC_semantics_to_SPIRV_instruction_dataflow_proven"])
        self.assertFalse(report["numerical_register_Location_coincidence_is_provenance"])

    def test_explicit_compiler_annotations_are_only_labels_not_dataflow(self):
        def annotating(code, stage, folder):
            result = translator(code, stage, folder)
            i = int(folder.name.split("-")[3])
            from test_t3_smoke34_spirv_usersemantic_annotations import module
            for filename in ("original.spv", "roundtrip.spv"):
                (folder/filename).write_bytes(module(
                    extension=True, annotations=True, locations=tuple(range(3+i))))
            return result
        report = self.evaluate(translator=annotating)
        c = report["counts"]
        self.assertEqual(c["original_spv_explicit_semantic_matches_original"], 7)
        self.assertEqual(c["roundtrip_spv_explicit_semantic_matches_original"], 7)
        self.assertFalse(report["original_DXBC_semantics_to_SPIRV_instruction_dataflow_proven"])

    def test_untrusted_ambiguous_private_classifier_data_cannot_leak(self):
        def leak(_src, _ref, _parsed):
            return {"PRIVATE_SOURCE_NAME": SECRET}
        with self.assertRaisesRegex(ValueError, "untrusted_private_SPIRV_annotation_classifier_fields"):
            self.evaluate(classifier=leak)

    def test_bool_counter_rejected_as_noninteger(self):
        def lying(src, ref, parsed):
            result = t3.annotations.classify_original_and_spirv(src, ref, parsed)
            result["spv_hlsl_semantic_extension_present"] = True
            return result
        with self.assertRaisesRegex(ValueError, "untrusted_private_SPIRV_annotation_count"):
            self.evaluate(classifier=lying)

    def test_real_stage_must_be_truly_compiled_and_validated(self):
        def failure(code, stage, folder):
            output = translator(code, stage, folder)
            output["vulkan11_valid"] = False
            return output
        with self.assertRaisesRegex(ValueError, "translator_not_complete"):
            self.evaluate(translator=failure)

    def test_unsafe_fragment_source_or_reflection_mismatch(self):
        def changed(path):
            result = reflector(path)
            result["inputs"][0]["location"] = 700
            return result
        with self.assertRaisesRegex(ValueError, "disagrees_with_safe_reflection"):
            self.evaluate(reflector=changed)

    def test_invalid_pair_scope_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid_original_smoke34_explicit_provenance_scope"):
            self.evaluate(pairs=pairs()[:1])

    def test_no_source_private_names_code_ids_locations_in_report(self):
        serialized = json.dumps(self.evaluate(), sort_keys=True)
        for term in (SECRET, PRIVATE_CODE.decode(), '"location":',
                     '"register":', '"semantic":', '"shader_name":'):
            self.assertNotIn(term, serialized)


if __name__ == "__main__":
    unittest.main()
