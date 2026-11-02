"""Synthetic SPIR-V reflection contract; never uses original game shader bytes."""
import struct
import unittest
from scripts.probe_authentic_fft_dxbc_translation import spirv_resource_bindings, compare_roundtrip_contracts, sanitize_spirv_cross_reflection

def make_spv(instructions):
    words = [0x07230203, 0x00010000, 0, 16, 0]
    for op, operands in instructions:
        words.extend([(1 + len(operands)) << 16 | op, *operands])
    return struct.pack("<" + "I" * len(words), *words)

class FftSpirvBindingTests(unittest.TestCase):
    def test_returns_numeric_set_binding_only(self):
        spv = make_spv([(71, [7, 33, 2]), (71, [7, 34, 0]),
                        (71, [9, 33, 6]), (71, [9, 34, 1])])
        info = spirv_resource_bindings(spv)
        self.assertEqual(info["descriptor_binding_pairs"], [[0, 2], [1, 6]])
        self.assertEqual(info["targets_with_explicit_binding"], 2)
        self.assertFalse(info["resource_names_disclosed"])

    def test_unset_descriptor_set_does_not_fabricate_set_zero(self):
        spv = make_spv([(71, [7, 33, 12])])
        self.assertEqual(spirv_resource_bindings(spv)["descriptor_binding_pairs"], [[None, 12]])

    def test_rejects_truncation_and_wrong_magic(self):
        with self.assertRaisesRegex(ValueError, "truncated"):
            spirv_resource_bindings(b"\x00" * 8)
        spv = make_spv([(71, [7, 33, 2])])
        with self.assertRaisesRegex(ValueError, "header"):
            spirv_resource_bindings(b"NOPE" + spv[4:])
        with self.assertRaisesRegex(ValueError, "instruction boundary"):
            spirv_resource_bindings(spv[:-4])


    def test_roundtrip_comparison_does_not_claim_semantic_equivalence(self):
        original = {"entrypoint_execution_models": {5: 1},
                    "declared_local_workgroup_sizes": [[128, 1, 1]]}
        reb = {"entrypoint_execution_models": {5: 1},
               "declared_local_workgroup_sizes": [[256, 1, 1]]}
        bindings = {"descriptor_binding_pairs": [[0, 0], [0, 1], [0, 2]]}
        damaged = {"descriptor_binding_pairs": [[0, 0], [0, 1]]}
        result = compare_roundtrip_contracts(original, bindings, reb, damaged)
        self.assertTrue(result["compute_entrypoint_model_preserved"])
        self.assertFalse(result["compute_workgroup_shape_preserved"])
        self.assertFalse(result["descriptor_binding_pairs_preserved"])
        self.assertFalse(result["original_numeric_results_equal"])
        self.assertFalse(result["unity_gpu_execution_proven"])
        equal = compare_roundtrip_contracts(original, bindings, original, bindings)
        self.assertTrue(equal["compute_workgroup_shape_preserved"])
        self.assertFalse(equal["original_numeric_results_equal"])


    def test_private_spirv_cross_resource_kind_sanitization(self):
        reflection = {
            "ubos": [{"name": "secretGlobal", "set": 0, "binding": 3}],
            "images": [{"name": "originalWaterTex", "set": 0, "binding": 2}],
            "ssbos": [{"name": "hiddenFFTBuffer", "set": 1, "binding": 0}],
            "types": {"_14": {"name": "PrivateShaderData"}},
        }
        output = sanitize_spirv_cross_reflection(reflection)
        self.assertEqual(output["original_resource_kind_counts"],
                         {"ubos": 1, "ssbos": 1, "images": 1})
        self.assertEqual(output["original_resource_kind_descriptor_pairs"]["images"],
                         [[0, 2]])
        self.assertEqual(output["resource_records_total"], 3)
        for name in ("secretGlobal", "originalWaterTex",
                     "hiddenFFTBuffer", "PrivateShaderData"):
            self.assertNotIn(name, str(output))
        self.assertFalse(output["private_names_or_type_contents_disclosed"])

    def test_reflection_fails_on_invalid_numeric_bindings(self):
        with self.assertRaisesRegex(ValueError, "descriptor binding"):
            sanitize_spirv_cross_reflection({"images": [{"binding": True}]})
        with self.assertRaisesRegex(ValueError, "resource class"):
            sanitize_spirv_cross_reflection({"images": [{}] * 129})



if __name__ == "__main__":
    unittest.main()
