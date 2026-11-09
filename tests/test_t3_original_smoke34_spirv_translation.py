"""Source-free synthetic controls for private smoke34 2x original DXBC V/F pairs.

No original code, shader names, GUIDs, bytecode, hashes, or phone assertions.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_smoke34_spirv_translation as t3


def metadata(idx, keyword):
    return {
        "m_BlobIndex": idx, "m_ShaderHardwareTier": 0,
        "m_KeywordIndices": [keyword],
        "m_GlobalKeywordIndices": [], "m_LocalKeywordIndices": [],
    }


def parsed():
    return {"m_SubShaders": [{"m_Passes": [{
        "m_Type": 0,
        "progVertex": {
            "m_SubPrograms": [metadata(0, 0), metadata(0, 1)],
            "m_PlayerSubPrograms": [],
        },
        "progFragment": {
            "m_SubPrograms": [metadata(1, 1), metadata(1, 0)],
            "m_PlayerSubPrograms": [],
        },
    }]}]}


def table():
    return [(0, b"synthetic-not-original-dxbc") for _ in range(8)]


def fake_link(meta, rows, stage):
    assert len(rows) == 8
    assert meta["m_BlobIndex"] == (0 if stage == 1 else 1)
    return (b"fake-code-" + bytes((stage, meta["m_KeywordIndices"][0])), {})


def translate(code, stage, folder):
    assert code.startswith(b"fake-code-") and folder.is_dir()
    return {
        "stage": stage, "vulkan11_valid": True,
        "hlsl_recovered": True, "roundtrip_vulkan11_valid": True,
        "secret_hash": "NEVER_COPY_PRIVATE_HASH",
        "secret_hlsl": "NEVER_COPY_PRIVATE_PROGRAM",
    }


def reflect(path):
    stage = int(path.parent.name.rsplit("-stage-", 1)[1])
    if stage == 1:
        return {"inputs": [], "outputs": [{"location": 0, "type": "vec4"}],
                "resource_slots": {}}
    return {"inputs": [{"location": 0, "type": "vec4"}],
            "outputs": [], "resource_slots": {"textures": [[0, 1]]}}


class SyntheticPrivateSmoke34(unittest.TestCase):
    def pair(self):
        return t3.exact_two_pairs(parsed(), table(), linker=fake_link)

    def evaluate(self, **kwargs):
        with tempfile.TemporaryDirectory() as temp:
            return t3.evaluate(self.pair(), Path(temp),
                               translator=kwargs.get("translator", translate),
                               reflector=kwargs.get("reflector", reflect),
                               checker=kwargs.get("checker", lambda _v, _f: True),
                               io_classifier=kwargs.get("io_classifier", t3.classify_stage_io))

    def test_exact_two_original_keyword_pairs_not_array_position(self):
        pairs = self.pair()
        self.assertEqual(len(pairs), 2)
        self.assertEqual([(vs[-1], fs[-1]) for vs, fs in pairs], [(0, 0), (1, 1)])

    def test_drifted_keyword_refused_instead_of_selecting_nearest(self):
        value = parsed()
        value["m_SubShaders"][0]["m_Passes"][0]["progFragment"]["m_SubPrograms"][0]["m_KeywordIndices"] = [7]
        with self.assertRaisesRegex(ValueError, "keyword_bucket_pair_mismatch"):
            t3.exact_two_pairs(value, table(), linker=fake_link)

    def test_duplicate_and_changed_original_variant_counts_refused(self):
        value = parsed()
        p = value["m_SubShaders"][0]["m_Passes"][0]["progFragment"]["m_SubPrograms"]
        p[1]["m_KeywordIndices"] = [1]
        with self.assertRaisesRegex(ValueError, "duplicate_original"):
            t3.exact_two_pairs(value, table(), linker=fake_link)
        value = parsed()
        value["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_SubPrograms"].pop()
        with self.assertRaisesRegex(ValueError, "changed_original_stage_variant_count"):
            t3.exact_two_pairs(value, table(), linker=fake_link)

    def test_different_stage_missing_pass_and_short_table_fail_closed(self):
        value = parsed()
        value["m_SubShaders"][0]["m_Passes"][0]["m_Type"] = 1
        with self.assertRaisesRegex(ValueError, "pass_not_normal"):
            t3.exact_two_pairs(value, table(), linker=fake_link)
        with self.assertRaisesRegex(ValueError, "changed_original_dxbc_table"):
            t3.exact_two_pairs(parsed(), table()[:-1], linker=fake_link)
        value = parsed()
        del value["m_SubShaders"][0]["m_Passes"][0]["progFragment"]
        with self.assertRaisesRegex(ValueError, "missing_original_stage"):
            t3.exact_two_pairs(value, table(), linker=fake_link)

    def test_valid_four_original_and_roundtrip_stages_only_counts_public(self):
        result = self.evaluate()
        self.assertEqual(result["status"], t3.STATUS)
        counters = result["counts"]
        self.assertEqual(counters["translation_attempts"], 4)
        for key in (
            "original_stage_spirv_vulkan11_valid", "hlsl_recovered",
            "roundtrip_stage_spirv_vulkan11_valid",
            "original_stage_reflection_valid", "roundtrip_stage_reflection_valid",
            "original_roundtrip_io_equal", "original_roundtrip_resource_shapes_equal",
        ):
            self.assertEqual(counters[key], 4, key)
        for key in (
            "original_stage_pairs_interfaces_compared", "original_stage_pairs_compatible",
            "roundtrip_stage_pairs_interfaces_compared", "roundtrip_stage_pairs_compatible",
            "pairs_both_original_spirv_valid", "pairs_both_roundtrip_spirv_valid",
        ):
            self.assertEqual(counters[key], 2, key)
        text = json.dumps(result, sort_keys=True)
        for value in ("NEVER_COPY_PRIVATE_HASH", "NEVER_COPY_PRIVATE_PROGRAM",
                      "synthetic-not-original-dxbc", "fake-code-", "textures"):
            self.assertNotIn(value, text)
        self.assertFalse(result["native_Unity_Android_Adreno_pixels_verified"])
        self.assertFalse(result["authored_original_ShaderLab_restored"])

    def test_failed_fragment_cpu_translation_is_not_vulkan_pair_success(self):
        def partial(code, stage, folder):
            return {"stage": stage, "vulkan11_valid": stage == 1,
                    "hlsl_recovered": False, "roundtrip_vulkan11_valid": False}
        result = self.evaluate(translator=partial)
        self.assertEqual(result["counts"]["translation_attempts"], 4)
        self.assertEqual(result["counts"]["original_stage_spirv_vulkan11_valid"], 2)
        self.assertEqual(result["counts"]["pairs_both_original_spirv_valid"], 0)
        self.assertEqual(result["counts"]["original_stage_pairs_interfaces_compared"], 0)

    def test_invalid_private_compiler_contract_rejected(self):
        def invalid(code, stage, folder):
            return {"stage": stage, "vulkan11_valid": False,
                    "hlsl_recovered": False, "roundtrip_vulkan11_valid": True}
        with self.assertRaisesRegex(ValueError, "invalid_private_translator_result"):
            self.evaluate(translator=invalid)

    def test_drifted_roundtrip_locations_counted_as_mismatch(self):
        def drift(path):
            result = reflect(path)
            if path.name == "roundtrip.spv" and result["inputs"]:
                result["inputs"] = [{"location": 3, "type": "vec4"}]
            return result
        def compare(v, f):
            return v["outputs"] == f["inputs"]
        result = self.evaluate(reflector=drift, checker=compare)
        self.assertEqual(result["counts"]["original_stage_pairs_compatible"], 2)
        self.assertEqual(result["counts"]["roundtrip_stage_pairs_compatible"], 0)
        self.assertEqual(result["counts"]["original_roundtrip_io_equal"], 2)
        self.assertEqual(result["counts"]["io_drift_inputs_location_only_remap_candidate"], 2)
        self.assertEqual(result["counts"]["io_drift_inputs_same_location_type_changes"], 0)

    def test_invalid_reflected_per_program_private_metadata_not_published(self):
        def wrong(path):
            result = reflect(path)
            if path.name == "roundtrip.spv":
                result["resource_slots"] = {"internal_secret": [[3, 4]]}
            return result
        result = self.evaluate(reflector=wrong)
        self.assertEqual(result["counts"]["roundtrip_stage_reflection_valid"], 0)
        self.assertNotIn("internal_secret", json.dumps(result))

    def test_private_io_classifier_rejects_unknown_labels_and_negative_counts(self):
        with self.assertRaisesRegex(ValueError, "drift_category_shape"):
            self.evaluate(io_classifier=lambda a, b: {"private_name": "secret"})
        def wrong_value(a, b):
            result = t3.classify_stage_io(a, b)
            result["inputs_removed_locations"] = -1
            return result
        with self.assertRaisesRegex(ValueError, "drift_category_value"):
            self.evaluate(io_classifier=wrong_value)

    def test_safe_aggregated_io_counts_when_reflection_equivalent(self):
        result = self.evaluate()
        counters = result["counts"]
        self.assertEqual(counters["io_drift_inputs_identical"], 4)
        self.assertEqual(counters["io_drift_outputs_identical"], 4)
        self.assertEqual(counters["io_drift_inputs_location_only_remap_candidate"], 0)
        self.assertEqual(counters["io_drift_outputs_location_only_remap_candidate"], 0)

    def test_untrusted_interface_checker_is_not_trusted(self):
        with self.assertRaisesRegex(ValueError, "invalid_private_stage_interface_check"):
            self.evaluate(checker=lambda v, f: "untrusted")


if __name__ == "__main__":
    unittest.main()
