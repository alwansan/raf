"""B09 original Spectrum seven-pass contract: source-free positive/mutation controls."""
import copy
from unittest import TestCase

from scripts.b09_spectrum_topology_contract import (
    TARGET, PASSES, BLOB_SEQUENCES, ORIGINAL_DESCRIPTORS, attest_spectrum,
)


def fixture():
    tree = {"m_ParsedForm": {"m_Name": TARGET, "m_KeywordNames": ["synthetic"] * 5,
                             "m_SubShaders": [{"m_Passes": [{} for _ in range(PASSES)]}]}}
    stages = {}
    for name, sequence in BLOB_SEQUENCES.items():
        stages[name] = [
            {"passIndex": i, "variants": [
                {"keywordIndices": [], "blobIndex": sequence[2 * i]},
                {"keywordIndices": [4], "blobIndex": sequence[2 * i + 1]},
            ]} for i in range(PASSES)
        ]
    topology = {"gate": "Spectrum-graph", "subshaderCount": 1, "passCount": 7,
                "keywordNameCount": 5, "stages": stages}
    descriptor = {"original_pass_count": 7, "stage_descriptor_table_counts": dict(ORIGINAL_DESCRIPTORS),
                  "original_stage_resource_tables_observed": True,
                  "per_pass_stage_numeric_contract": [{"pass_index": i, "synthetic": True}
                                                       for i in range(PASSES)]}
    return tree, topology, descriptor


class TestB09SevenPassContract(TestCase):
    def test_original_seven_pass_topology_accepted(self):
        result = attest_spectrum(*fixture())
        self.assertEqual(result["authenticated_original_passes"], 7)
        self.assertEqual(result["authenticated_variant_stage_programs"], 28)
        self.assertFalse(result["shaderlab_restored"])
        self.assertFalse(result["unity_or_device_verified"])
        self.assertEqual(len(result["numeric_descriptor_sha256"]), 64)

    def test_six_pass_device_minimum_is_not_original_identity(self):
        t, g, d = fixture()
        t["m_ParsedForm"]["m_SubShaders"][0]["m_Passes"].pop()
        with self.assertRaisesRegex(ValueError, "seven-pass"):
            attest_spectrum(t, g, d)

    def test_eighth_fabricated_pass_rejected(self):
        t, g, d = fixture()
        t["m_ParsedForm"]["m_SubShaders"][0]["m_Passes"].append({})
        with self.assertRaisesRegex(ValueError, "seven-pass"):
            attest_spectrum(t, g, d)

    def test_wrong_shader_name_rejected(self):
        t, g, d = fixture()
        t["m_ParsedForm"]["m_Name"] = "Another/Shader"
        with self.assertRaisesRegex(ValueError, "identity"):
            attest_spectrum(t, g, d)

    def test_multi_subshader_rejected(self):
        t, g, d = fixture()
        t["m_ParsedForm"]["m_SubShaders"].append({"m_Passes": []})
        with self.assertRaisesRegex(ValueError, "subshader"):
            attest_spectrum(t, g, d)

    def test_wrong_keyword_table_shape_rejected(self):
        t, g, d = fixture()
        t["m_ParsedForm"]["m_KeywordNames"].pop()
        with self.assertRaisesRegex(ValueError, "keyword-table"):
            attest_spectrum(t, g, d)

    def test_wrong_pass_blob_order_rejected(self):
        t, g, d = fixture()
        g["stages"]["progVertex"][4]["variants"][0]["blobIndex"] = 99
        with self.assertRaisesRegex(ValueError, "blob order"):
            attest_spectrum(t, g, d)

    def test_wrong_keyword_variant_rejected(self):
        t, g, d = fixture()
        g["stages"]["progFragment"][2]["variants"][1]["keywordIndices"] = [1]
        with self.assertRaisesRegex(ValueError, "keyword"):
            attest_spectrum(t, g, d)

    def test_missing_variant_rejected(self):
        t, g, d = fixture()
        g["stages"]["progVertex"][0]["variants"].pop()
        with self.assertRaisesRegex(ValueError, "variants"):
            attest_spectrum(t, g, d)

    def test_missing_resource_topology_rejected(self):
        t, g, d = fixture()
        d["stage_descriptor_table_counts"]["fragment_rows"] = 12
        with self.assertRaisesRegex(ValueError, "resource"):
            attest_spectrum(t, g, d)

    def test_dropped_resource_pass_rejected(self):
        t, g, d = fixture()
        d["per_pass_stage_numeric_contract"].pop()
        with self.assertRaisesRegex(ValueError, "descriptor"):
            attest_spectrum(t, g, d)

    def test_bools_are_not_original_blob_indices(self):
        t, g, d = fixture()
        g["stages"]["progVertex"][0]["variants"][0]["blobIndex"] = True
        with self.assertRaisesRegex(ValueError, "invalid original program"):
            attest_spectrum(t, g, d)

    def test_different_descriptor_observation_changes_safe_digest(self):
        t, g, d = fixture()
        before = attest_spectrum(t, g, d)
        changed = copy.deepcopy(d)
        changed["per_pass_stage_numeric_contract"][1]["pass_index"] = 99
        after = attest_spectrum(t, g, changed)
        self.assertNotEqual(before["numeric_descriptor_sha256"], after["numeric_descriptor_sha256"])
