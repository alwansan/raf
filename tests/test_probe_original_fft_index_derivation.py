"""Synthetic original FFT index derivation checks; no Raft source content."""
import hashlib
import unittest
from scripts.probe_original_fft_index_derivation import index_source_links


class IndexDerivationTests(unittest.TestCase):
    def test_original_index_derived_from_resolution_not_passed(self):
        src = ("class FFT {\n"
               " void Run(ComputeShader shader, int resolution) {\n"
               "   int localIndex = (int)Mathf.Log(resolution, 2) - 6;\n"
               "   shader.SetTexture(localIndex, \"A\", src);\n"
               "   shader.Dispatch(localIndex, 1, 1, 1);\n"
               "   shader.SetTexture(localIndex + 1, \"A\", dst);\n"
               "   shader.Dispatch(localIndex + 1, 1, 1, 1);\n"
               " }}")
        data = index_source_links(src, hashlib.sha256(src.encode()).hexdigest())
        self.assertEqual(data["index_assignment_count"], 1)
        rhs = data["index_assignments"][0]["right_hand_side"]
        self.assertTrue(rhs["mathf_log2_call"])
        self.assertIn(6, rhs["integer_constants"])
        self.assertTrue(rhs["has_subtraction"])
        self.assertIn("V", rhs["anonymized_operator_shape"])
        self.assertNotIn("resolution", rhs["anonymized_operator_shape"])
        self.assertFalse(data["index_assignments"][0]["preceding_immediate_guard"]["simple_condition_verified"])
        self.assertFalse(data["first_and_second_pass_index_runtime_values_verified"])
        self.assertNotIn("localIndex", str(data))
        self.assertNotIn("resolution", str(data))


    def test_direct_condition_before_second_original_index_assignment(self):
        src = ("class Example {\n void Work(int size, bool conditional) {\n"
               "  int localIndex = (size >> 5) - 1;\n"
               "  if (conditional) {\n"
               "    localIndex += 10;\n"
               "  }\n"
               "  fft.SetTexture(localIndex, \"A\", foo);\n"
               "  fft.Dispatch(localIndex, 1, 1, 1);\n"
               "  fft.SetTexture(localIndex + 1, \"B\", bar);\n"
               "  fft.Dispatch(localIndex + 1, 1, 1, 1);\n"
               " }}")
        data = index_source_links(src, hashlib.sha256(src.encode()).hexdigest())
        self.assertEqual(data["index_assignment_count"], 2)
        self.assertEqual(data["index_assignments"][0]["right_hand_side"]["anonymized_operator_shape"],
                         "(V>>5)-1")
        self.assertTrue(data["index_assignments"][1]["preceding_immediate_guard"]["simple_condition_verified"])
        self.assertEqual(data["index_assignments"][1]["right_hand_side"]["integer_constants"], [10])
        self.assertNotIn("\'conditional\'", str(data))

    def test_constructor_parameter_and_boolean_bank_match_original_formula(self):
        src = ("class Dx11FFT {\n"
               " public Dx11FFT(ComputeShader cs, int exponent, bool dynamic, bool other) {\n"
               "   int localIndex = exponent - 5 << 1;\n"
               "   if (other) {\n"
               "     localIndex += 10;\n"
               "   }\n"
               "   cs.SetTexture(localIndex, \"A\", src);\n"
               "   cs.Dispatch(localIndex, 1, 1, 1);\n"
               "   cs.SetTexture(localIndex + 1, \"B\", dst);\n"
               "   cs.Dispatch(localIndex + 1, 1, 1, 1);\n"
               " }\n"
               "}")
        report = index_source_links(src, hashlib.sha256(src.encode()).hexdigest())
        contract = report["source_proven_original_constructor_kernel_bank_formula"]
        self.assertTrue(contract["constructor_signature_matched"])
        self.assertTrue(
            report["source_proven_original_kernel_index_formula_seed_lineage"]["seed_alias_of_constructor_int_proven"])
        self.assertTrue(contract["first_assignment_matches_constructor_int_parameter"])
        self.assertTrue(contract["bank_stride_guard_matches_fourth_bool_parameter"])
        self.assertEqual(contract["proven_formula_shape"], "(n-5)<<1, then conditional +10")
        self.assertFalse(contract["verified_runtime_kernel_lookup_index"])
        self.assertNotIn("exponent", str(report))
        self.assertNotIn("\'other\'", str(report))

    def test_local_seed_expression_is_detected_without_leaking_identifiers(self):
        src = ("class Dx11FFT {\n"
               "  public Dx11FFT(ComputeShader cs, int fftSize, bool a, bool b) {\n"
               "    int bits = (int)Mathf.Log(fftSize, 2);\n"
               "    int index = bits - 5 << 1;\n"
               "    if (b) index += 10;\n"
               "    cs.Dispatch(index, 1, 1, 1);\n"
               "    cs.Dispatch(index + 1, 1, 1, 1);\n"
               "  }\n}"
        )
        report = index_source_links(src, hashlib.sha256(src.encode()).hexdigest())
        seed = report["source_proven_original_kernel_index_formula_seed_lineage"]
        self.assertTrue(seed["first_formula_seed_identified"])
        self.assertFalse(seed["seed_alias_of_constructor_int_proven"])
        self.assertEqual(seed["seed_assignment_count"], 1)
        self.assertTrue(seed["seed_assignments"][0]["rhs"]["mathf_log2_call"])
        self.assertNotIn("fftSize", str(seed))
        self.assertNotIn("bits", str(seed))

    def test_wrong_source_and_missing_index_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "hash changed"):
            index_source_links("shader.Dispatch(index, 1, 1, 1);", "0" * 64)
        src = "shader.Dispatch(2, 1, 1, 1);"
        with self.assertRaisesRegex(ValueError, "not identifiable"):
            index_source_links(src, hashlib.sha256(src.encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
