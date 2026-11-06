import unittest

from scripts.t1_fft_original_direct_keyed_recorder import instrument


BASE = """OpCapability Shader
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %gid
OpExecutionMode %main LocalSize 64 1 1
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
OpDecorate %gid BuiltIn GlobalInvocationId
%void = OpTypeVoid
%fn = OpTypeFunction %void
%s32 = OpTypeInt 32 1
%v3s32 = OpTypeVector %s32 3
%v2s32 = OpTypeVector %s32 2
%f32 = OpTypeFloat 32
%v4f32 = OpTypeVector %f32 4
%pin = OpTypePointer Input %v3s32
%gid = OpVariable %pin Input
%main = OpFunction %void None %fn
%entry = OpLabel
%coord = OpUndef %v2s32
%read0 = OpImageFetch %v4f32 %source %coord
%read1 = OpImageFetch %v4f32 %butter %coord
%read2 = OpImageFetch %v4f32 %butter %coord
OpReturn
OpFunctionEnd
"""

class OriginalDirectKeyedTraceTests(unittest.TestCase):
    def test_three_sites_generate_original_ssbo_trace(self):
        result = instrument(BASE)
        self.assertEqual(result.count("OpAtomicIAdd"), 3)
        self.assertEqual(result.count("OpULessThan"), 3)
        self.assertEqual(result.count("OpSelect"), 3)
        self.assertEqual(result.count("OpTypeRuntimeArray"), 1)
        self.assertIn("OpDecorate %t1_original_trace_buffer Binding 3", result)
        self.assertIn("OpDecorate %t1_original_trace_buffer DescriptorSet 0", result)
        self.assertIn("OpMemberDecorate %t1_original_trace_block 0 Offset 0", result)
        self.assertIn("OpDecorate %t1_original_trace_block Block", result)
        self.assertEqual(result.count("OpStore"), 39)

    def test_signed_original_builtin_reused_without_double_input(self):
        result = instrument(BASE)
        self.assertEqual(result.count("BuiltIn GlobalInvocationId"), 1)
        self.assertEqual(result.count("%gid = OpVariable"), 1)
        self.assertIn("OpLoad %v3s32 %gid", result)
        self.assertIn("OpBitcast %t1_original_trace_v3u", result)
        # SPIR-V 1.3 OpEntryPoint interfaces list Input/Output only.
        self.assertIn('OpEntryPoint GLCompute %main "main" %gid', result)
        self.assertNotIn('OpEntryPoint GLCompute %main "main" %gid %t1_original_trace_buffer', result)

    def test_storage_buffer_is_not_an_entrypoint_interface_in_vulkan_11(self):
        p = instrument(BASE)
        entry = next(row for row in p.splitlines() if row.startswith("OpEntryPoint"))
        self.assertEqual(entry.strip(), 'OpEntryPoint GLCompute %main "main" %gid')
        self.assertIn("%t1_original_trace_buffer = OpVariable", p)

    def test_all_three_site_occurrence_counters_are_function_local(self):
        result = instrument(BASE)
        for site in range(3):
            name=f"%t1_original_trace_occ_{site}"
            self.assertIn(f"{name} = OpVariable", result)
            self.assertIn(f"OpLoad", result)
            self.assertIn(f"OpStore {name}", result)
            self.assertIn(f"OpAtomicIAdd", result)
        self.assertLess(result.index("%t1_original_trace_occ_0 = OpVariable"),
                        result.index("%coord = OpUndef"))

    def test_pixel_bits_are_recorded_only_after_original_fetch(self):
        result = instrument(BASE)
        for site in range(3):
            self.assertLess(result.index(f"%read{site} = OpImageFetch"),
                            result.index(f"%t1_original_trace_s{site}_pixel_uint = OpBitcast"))
            self.assertIn(f"%t1_original_trace_s{site}_coord_signed_0 = OpCompositeExtract %s32 %coord 0", result)

    def test_original_expected_set0_binding3_is_checked(self):
        with self.assertRaisesRegex(ValueError, "collision"):
            instrument(BASE.replace("OpDecorate %gid BuiltIn",
                                    "OpDecorate %occupied DescriptorSet 0\n"
                                    "OpDecorate %occupied Binding 3\n"
                                    "OpDecorate %gid BuiltIn"))

    def test_wrong_global_invocation_signed_width_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "interface/type"):
            instrument(BASE.replace("%v3s32 = OpTypeVector %s32 3",
                                    "%v3s32 = OpTypeVector %s32 2"))

    def test_no_global_invocation_input_fails_closed(self):
        with self.assertRaises(ValueError):
            instrument(BASE.replace("OpDecorate %gid BuiltIn GlobalInvocationId", ""))

    def test_wrong_original_float_result_rejected(self):
        with self.assertRaisesRegex(ValueError, "fetched pixel"):
            instrument(BASE.replace("%v4f32 = OpTypeVector %f32 4",
                                    "%v4f32 = OpTypeVector %f32 2"))

    def test_wrong_original_fetch_role_rejected(self):
        with self.assertRaisesRegex(ValueError, "descriptor roles"):
            instrument(BASE.replace("OpDecorate %butter Binding 1",
                                    "OpDecorate %butter Binding 2"))

    def test_additional_fetch_fails_closed(self):
        with self.assertRaises(ValueError):
            instrument(BASE.replace("OpReturn", "%read3 = OpImageFetch %v4f32 %butter %coord\nOpReturn"))

    def test_multiple_entry_functions_rejected(self):
        with self.assertRaises(ValueError):
            instrument(BASE.replace("OpExecutionMode", 'OpEntryPoint GLCompute %main "other"\nOpExecutionMode'))

    def test_original_code_not_replaced_only_followed_by_instrumentation(self):
        p=instrument(BASE)
        self.assertEqual(p.count("%read0 = OpImageFetch"), 1)
        self.assertEqual(p.count("%read1 = OpImageFetch"), 1)
        self.assertEqual(p.count("%read2 = OpImageFetch"), 1)
        self.assertEqual(p.count("OpReturn"), 1)

    def test_double_instrumentation_rejected(self):
        with self.assertRaises(ValueError):
            instrument(instrument(BASE))

    def test_helper_function_fetches_are_not_misattributed_to_entrypoint(self):
        value = BASE.replace(
            "%read2 = OpImageFetch %v4f32 %butter %coord\n",
            "").replace("OpFunctionEnd", "OpFunctionEnd\n"
                       "%helper = OpFunction %void None %fn\n"
                       "%next = OpLabel\n"
                       "%read2 = OpImageFetch %v4f32 %butter %coord\n"
                       "OpReturn\nOpFunctionEnd")
        with self.assertRaisesRegex(ValueError, "not owned"):
            instrument(value)

    def test_unbounded_input_does_not_run(self):
        with self.assertRaises(ValueError):
            instrument(BASE + " " * (2*1024*1024))


if __name__ == "__main__":
    unittest.main()
