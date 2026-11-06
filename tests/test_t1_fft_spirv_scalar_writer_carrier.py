import unittest

from scripts.t1_fft_spirv_scalar_writer_carrier import analyze


HEADER = """
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%f32 = OpTypeFloat 32
%i32 = OpTypeInt 32 1
%u32 = OpTypeInt 32 0
%bool = OpTypeBool
%v2f = OpTypeVector %f32 2
%v2i = OpTypeVector %i32 2
%v4f = OpTypeVector %f32 4
%ptr4 = OpTypePointer Function %v4f
%ptrscalar = OpTypePointer Function %f32
%ptrindex = OpTypePointer Function %i32
%i0 = OpConstant %i32 0
%i1 = OpConstant %i32 1
%i2 = OpConstant %i32 2
%i3 = OpConstant %i32 3
%zero = OpConstant %f32 0
%one = OpConstant %f32 1
%signed = OpConstant %i32 1
%unsigned = OpConstant %u32 1
%cond = OpConstantTrue %bool
%void = OpTypeVoid
%ft = OpTypeFunction %void
%fun = OpFunction %void None %ft
%entry = OpLabel
%local = OpVariable %ptr4 Function
"""

READS = """
%read4 = OpLoad %v4f %local
%shuffled = OpVectorShuffle %v2f %read4 %read4 0 2
%coord = OpBitcast %v2i %shuffled
%a = OpImageFetch %v2f %source %coord
%b = OpImageFetch %v2f %butter %coord
%c = OpImageFetch %v2f %butter %coord
OpReturn
OpFunctionEnd
"""


def result(body, axis="y", read=READS):
    return analyze(HEADER + body + read, original_layout=True)["sites"][1]["lanes"][axis]


class OriginalScalarWriterCarrierTests(unittest.TestCase):
    def test_signed_int_bits_and_float_constant_remain_distinct_candidates(self):
        program = (
            "%frombits = OpBitcast %f32 %signed\n"
            "%p = OpAccessChain %ptrscalar %local %i2\n"
            "OpBranchConditional %cond %left %right\n"
            "%left = OpLabel\nOpStore %p %frombits\nOpBranch %join\n"
            "%right = OpLabel\nOpStore %p %zero\nOpBranch %join\n"
            "%join = OpLabel\n")
        r = result(program)
        self.assertEqual(r["physical_load_lane"], "other")
        self.assertEqual(r["component_producer_categories"], {
            "float32_constant": 1, "sint32_bits_to_float32": 1})
        self.assertEqual(r["may_reach_writer_count"], 2)
        self.assertFalse(r["numeric_origin_proven"])

    def test_unsigned_bitcast_distinct_from_signed(self):
        program = ("%frombits = OpBitcast %f32 %unsigned\n"
                   "%p = OpAccessChain %ptrscalar %local %i2\n"
                   "OpStore %p %frombits\n")
        self.assertEqual(result(program)["component_producer_categories"],
                         {"uint32_bits_to_float32": 1})

    def test_integer_numeric_conversion_is_not_a_bitcast(self):
        program = ("%numeric = OpConvertSToF %f32 %signed\n"
                   "%p = OpAccessChain %ptrscalar %local %i2\n"
                   "OpStore %p %numeric\n")
        self.assertEqual(result(program)["component_producer_categories"],
                         {"numeric_sint32_to_float32": 1})

    def test_copied_bitcast_value_preserves_type_and_category(self):
        program = ("%frombits = OpBitcast %f32 %signed\n"
                   "%copied = OpCopyObject %f32 %frombits\n"
                   "%p = OpAccessChain %ptrscalar %local %i2\n"
                   "OpStore %p %copied\n")
        self.assertEqual(result(program)["component_producer_categories"],
                         {"sint32_bits_to_float32": 1})

    def test_whole_vector_write_is_not_claimed_scalar_bitcarrier(self):
        program = ("%whole = OpCompositeConstruct %v4f %one %one %one %one\n"
                   "OpStore %local %whole\n")
        r=result(program)
        self.assertEqual(r["whole_vector_writer_candidates"], 1)
        self.assertEqual(r["component_producer_categories"], {})
        self.assertFalse(r["numeric_origin_proven"])

    def test_unrelated_physical_lane_does_not_reach_site1_y(self):
        program = ("%p = OpAccessChain %ptrscalar %local %i1\n"
                   "OpStore %p %zero\n")
        r = result(program)
        self.assertEqual(r["may_reach_writer_count"], 0)
        self.assertTrue(r["uninitialized_path_possible"])

    def test_dynamic_index_leaves_unknown_writer_flag(self):
        program = ("%iv = OpVariable %ptrindex Function\n"
                   "%index = OpLoad %i32 %iv\n"
                   "%p = OpAccessChain %ptrscalar %local %index\n"
                   "OpStore %p %zero\n")
        r = result(program)
        self.assertTrue(r["unknown_writer_possible"])
        self.assertFalse(r["numeric_origin_proven"])

    def test_single_branch_writer_leaves_uninitialized_path(self):
        program = ("%p = OpAccessChain %ptrscalar %local %i2\n"
                   "OpBranchConditional %cond %left %right\n"
                   "%left = OpLabel\nOpStore %p %zero\nOpBranch %join\n"
                   "%right = OpLabel\nOpBranch %join\n"
                   "%join = OpLabel\n")
        r=result(program)
        self.assertEqual(r["may_reach_writer_count"], 1)
        self.assertTrue(r["uninitialized_path_possible"])

    def test_later_store_after_read_does_not_reach(self):
        post_read = READS.replace("OpReturn", "OpStore %p %zero\nOpReturn")
        r = result("%p = OpAccessChain %ptrscalar %local %i2\n", read=post_read)
        self.assertEqual(r["may_reach_writer_count"], 0)

    def test_earlier_store_killed_by_later_constant_store(self):
        program = ("%b = OpBitcast %f32 %signed\n"
                   "%p = OpAccessChain %ptrscalar %local %i2\n"
                   "OpStore %p %b\nOpStore %p %zero\n")
        r = result(program)
        self.assertEqual(r["component_producer_categories"], {"float32_constant": 1})

    def test_earlier_store_and_loop_backedge_may_both_reach(self):
        program = ("%b = OpBitcast %f32 %signed\n"
                   "%p = OpAccessChain %ptrscalar %local %i2\n"
                   "OpStore %p %b\nOpBranch %loop\n"
                   "%loop = OpLabel\nOpBranchConditional %cond %body %join\n"
                   "%body = OpLabel\nOpStore %p %zero\nOpBranch %loop\n"
                   "%join = OpLabel\n")
        r = result(program)
        self.assertEqual(r["may_reach_writer_count"], 2)

    def test_wrong_original_descriptor_binding_fails_closed(self):
        with self.assertRaises(ValueError):
            analyze(HEADER.replace("OpDecorate %butter Binding 1",
                                   "OpDecorate %butter Binding 3")
                    + "OpStore %local %v\n" + READS, original_layout=True)

    def test_public_report_has_no_ssa_or_constant_values(self):
        raw = HEADER + ("%b = OpBitcast %f32 %signed\n"
                        "%p = OpAccessChain %ptrscalar %local %i2\n"
                        "OpStore %p %b\n") + READS
        report = analyze(raw, original_layout=True)
        self.assertFalse(report["private_ids_and_literals_exported"])
        self.assertFalse(report["original_integer_coordinate_semantics_proven"])
        self.assertNotIn("%", str(report))
        self.assertNotIn("source_value", str(report))


if __name__ == "__main__":
    unittest.main()
