import unittest

from scripts.t1_fft_original_keyed_preflight import analyze


BASE = """
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
OpDecorate %gid BuiltIn GlobalInvocationId
OpEntryPoint GLCompute %main "main" %gid
%float = OpTypeFloat 32
%int = OpTypeInt 32 1
%uint = OpTypeInt 32 0
%ivec = OpTypeVector %int 2
%uvec3 = OpTypeVector %uint 3
%v4f = OpTypeVector %float 4
%ptrin = OpTypePointer Input %uvec3
%gid = OpVariable %ptrin Input
%i0 = OpConstant %int 0
%coordinate = OpCompositeConstruct %ivec %i0 %i0
%r0 = OpImageFetch %v4f %source %coordinate
%r1 = OpImageFetch %v4f %butter %coordinate
%r2 = OpImageFetch %v4f %butter %coordinate
"""


class OriginalKeyedPrerequisitesTests(unittest.TestCase):
    def test_expected_original_three_sites_and_dispatch_builtin(self):
        x=analyze(BASE)
        self.assertEqual(x["roles"], ["source", "butterfly", "butterfly"])
        self.assertEqual(x["global_invocation_id_input"], "direct_input")
        self.assertEqual([s["coordinate_width"] for s in x["sites"]], [2, 2, 2])
        self.assertTrue(x["set0_storage_binding3_available"])
        self.assertFalse(x["direct_original_spirv_instrumented"])
        self.assertFalse(x["paired_numeric_parity_proven"])

    def test_integer_coordinates_and_float32_vector_results_only(self):
        x=analyze(BASE)
        self.assertEqual(x["sites"][0]["coordinate_type"], "sint32_vector")
        self.assertEqual(x["sites"][2]["fetched_value_type"], "float32_vector")
        self.assertEqual(x["sites"][2]["fetched_value_width"], 4)

    def test_descriptor_binding3_collision_detected(self):
        other = "OpDecorate %occupied DescriptorSet 0\nOpDecorate %occupied Binding 3\n"
        x=analyze(other + BASE)
        self.assertFalse(x["set0_storage_binding3_available"])
        self.assertTrue(x["set1_storage_binding3_available"])

    def test_different_descriptor_set3_binding3_not_false_collision(self):
        other = "OpDecorate %occupied DescriptorSet 3\nOpDecorate %occupied Binding 3\n"
        x=analyze(other + BASE)
        self.assertTrue(x["set0_storage_binding3_available"])

    def test_direct_builtin_not_listed_in_entrypoint_is_not_proven(self):
        x=analyze(BASE.replace('OpEntryPoint GLCompute %main "main" %gid',
                               'OpEntryPoint GLCompute %main "main"'))
        self.assertEqual(x["global_invocation_id_input"], "not_proven")

    def test_scalar_or_nonunsigned_builtin_is_rejected_as_proven(self):
        x=analyze(BASE.replace('%ptrin = OpTypePointer Input %uvec3',
                               '%ptrin = OpTypePointer Input %ivec'))
        self.assertEqual(x["global_invocation_id_input"], "not_proven")

    def test_struct_member_builtin_is_supported(self):
        x=analyze(BASE.replace('OpDecorate %gid BuiltIn GlobalInvocationId',
                               'OpMemberDecorate %inputstruct 0 BuiltIn GlobalInvocationId')
                  .replace('%ptrin = OpTypePointer Input %uvec3',
                           '%inputstruct = OpTypeStruct %uvec3\n'
                           '%ptrin = OpTypePointer Input %inputstruct'))
        self.assertEqual(x["global_invocation_id_input"], "struct_member_input")

    def test_float_coordinates_are_not_misreported_as_integer(self):
        value = BASE.replace('%coordinate = OpCompositeConstruct %ivec %i0 %i0',
                             '%coordinate = OpCompositeConstruct %v4f %i0 %i0')
        with self.assertRaisesRegex(ValueError, "integer vector"):
            analyze(value)

    def test_nonoriginal_source_descriptor_layout_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "roles"):
            analyze(BASE.replace('OpDecorate %butter Binding 1',
                                 'OpDecorate %butter Binding 4'))

    def test_duplicate_descriptor_decorations_rejected(self):
        with self.assertRaises(ValueError):
            analyze('OpDecorate %source Binding 0\n' + BASE)

    def test_four_fetches_do_not_claim_original_fixture(self):
        with self.assertRaises(ValueError):
            analyze(BASE + '%r3 = OpImageFetch %v4f %butter %coordinate\n')

    def test_private_ids_and_literal_values_not_in_summary(self):
        x=analyze(BASE)
        self.assertFalse(x["private_identifiers_or_values_exported"])
        self.assertNotIn("%", str(x))
        self.assertNotIn("coordinate", str(x["sites"]))
        self.assertNotIn("i0", str(x))


if __name__ == "__main__":
    unittest.main()
