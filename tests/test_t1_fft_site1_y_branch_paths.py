import unittest

from scripts.t1_fft_site1_y_branch_paths import analyze


HEADER = """
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%f32 = OpTypeFloat 32
%i32 = OpTypeInt 32 1
%bool = OpTypeBool
%v2f = OpTypeVector %f32 2
%v2i = OpTypeVector %i32 2
%v4f = OpTypeVector %f32 4
%ptr4 = OpTypePointer Function %v4f
%ptrscalar = OpTypePointer Function %f32
%ptrindex = OpTypePointer Function %i32
%ptrptr = OpTypePointer Function %ptr4
%idx2 = OpConstant %i32 2
%idx0 = OpConstant %i32 0
%one_i = OpConstant %i32 1
%zero = OpConstant %f32 0
%one = OpConstant %f32 1
%condition = OpIEqual %bool %idx0 %one_i
%frombits = OpBitcast %f32 %one_i
%full = OpCompositeConstruct %v4f %one %zero %one %zero
%void = OpTypeVoid
%ft = OpTypeFunction %void
%f = OpFunction %void None %ft
%entry = OpLabel
%local = OpVariable %ptr4 Function
"""

READS = """
%read4 = OpLoad %v4f %local
%shuffled = OpVectorShuffle %v2f %read4 %read4 0 2
%coordinate = OpBitcast %v2i %shuffled
%fetch0 = OpImageFetch %v2f %source %coordinate
%fetch1 = OpImageFetch %v2f %butter %coordinate
%fetch2 = OpImageFetch %v2f %butter %coordinate
OpReturn
OpFunctionEnd
"""


def audit(body, head=HEADER, read=READS):
    return analyze(head + body + read, require_original=True)


class ButterflyYGuardPathsTests(unittest.TestCase):
    def test_two_exclusive_branches_cannot_visit_both_writers(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %idx2\n"
            "OpBranchConditional %condition %bit %float\n"
            "%bit = OpLabel\nOpStore %p %frombits\nOpBranch %join\n"
            "%float = OpLabel\nOpStore %p %zero\nOpBranch %join\n"
            "%join = OpLabel\n")
        a = audit(body)
        self.assertTrue(a["physical_load_lane_is_outside_xy"])
        self.assertEqual(a["final_writer_categories_possible"],
                         ["float32_constant", "sint32_bits_to_float32"])
        self.assertFalse(a["may_visit_bitcarrier_and_float_constant_on_same_cfg_path"])
        for v in a["conditional_predicate_producers_seen_on_paths_by_final_writer"].values():
            self.assertEqual(v, ["OpIEqual"])
        self.assertFalse(a["full_execution_path_proven"])

    def test_sequential_bit_then_constant_is_a_single_last_writer(self):
        a = audit("%p = OpAccessChain %ptrscalar %local %idx2\n"
                  "OpStore %p %frombits\nOpStore %p %zero\n")
        self.assertEqual(a["final_writer_categories_possible"], ["float32_constant"])
        self.assertTrue(a["may_visit_bitcarrier_and_float_constant_on_same_cfg_path"])
        self.assertEqual(a["conditional_predicate_producers_seen_on_paths_by_final_writer"],
                         {"float32_constant": []})

    def test_sequence_reversed_selects_bitcarrier_as_last(self):
        a = audit("%p = OpAccessChain %ptrscalar %local %idx2\n"
                  "OpStore %p %zero\nOpStore %p %frombits\n")
        self.assertEqual(a["final_writer_categories_possible"], ["sint32_bits_to_float32"])
        self.assertTrue(a["may_visit_bitcarrier_and_float_constant_on_same_cfg_path"])

    def test_loop_backedge_could_visit_both_and_last_is_either(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %idx2\n"
            "OpStore %p %frombits\nOpBranch %head\n"
            "%head = OpLabel\nOpBranchConditional %condition %body %join\n"
            "%body = OpLabel\nOpStore %p %zero\nOpBranch %head\n"
            "%join = OpLabel\n")
        a = audit(body)
        self.assertEqual(a["final_writer_categories_possible"],
                         ["float32_constant", "sint32_bits_to_float32"])
        self.assertTrue(a["may_visit_bitcarrier_and_float_constant_on_same_cfg_path"])
        self.assertTrue(a["backward_cfg_edge_seen_by_final_writer"]["float32_constant"])

    def test_branch_without_write_produces_uninitialized_path(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %idx2\n"
            "OpBranchConditional %condition %left %right\n"
            "%left = OpLabel\nOpStore %p %frombits\nOpBranch %join\n"
            "%right = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\n")
        a = audit(body)
        self.assertTrue(a["uninitialized_final_path_possible"])
        self.assertFalse(a["may_visit_bitcarrier_and_float_constant_on_same_cfg_path"])

    def test_unknown_dynamic_index_write_is_not_claimed_safe(self):
        body = (
            "%indexptr = OpVariable %ptrindex Function\n"
            "%i = OpLoad %i32 %indexptr\n"
            "%p = OpAccessChain %ptrscalar %local %i\n"
            "OpStore %p %zero\n")
        a = audit(body)
        self.assertEqual(a["final_writer_categories_possible"], ["unknown_write"])
        self.assertTrue(a["unknown_final_writer_path_possible"])

    def test_write_to_other_component_does_not_change_last_writer(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %idx2\n"
            "%x = OpAccessChain %ptrscalar %local %idx0\n"
            "OpStore %p %frombits\nOpStore %x %zero\n")
        a = audit(body)
        self.assertEqual(a["final_writer_categories_possible"], ["sint32_bits_to_float32"])

    def test_whole_vector_store_is_not_scalar_bitcarrier(self):
        a = audit("OpStore %local %full\n")
        self.assertEqual(a["final_writer_categories_possible"], ["whole_vector"])
        self.assertFalse(a["may_visit_bitcarrier_and_float_constant_on_same_cfg_path"])

    def test_unknown_pointer_escape_blocks_original_proof(self):
        body = (
            "%ptrstorage = OpVariable %ptrptr Function\n"
            "OpStore %ptrstorage %local\n"
            "%p = OpAccessChain %ptrscalar %local %idx2\n"
            "OpStore %p %frombits\n")
        a = audit(body)
        self.assertTrue(a["pointer_escape_seen_on_any_cfg_path"])
        self.assertEqual(a["final_writer_categories_possible"],
                         ["sint32_bits_to_float32"])
        self.assertFalse(a["full_execution_path_proven"])

    def test_select_pointer_writer_is_conservative_unknown(self):
        body = (
            "%other = OpVariable %ptr4 Function\n"
            "%selected = OpSelect %ptr4 %condition %local %other\n"
            "OpStore %selected %full\n")
        a = audit(body)
        self.assertTrue(a["unknown_final_writer_path_possible"])

    def test_switch_conditions_are_classified_without_literal(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %idx2\n"
            "OpSwitch %idx0 %lbit 1 %lconstant\n"
            "%lbit = OpLabel\nOpStore %p %frombits\nOpBranch %join\n"
            "%lconstant = OpLabel\nOpStore %p %zero\nOpBranch %join\n"
            "%join = OpLabel\n")
        a = audit(body)
        categories=a["conditional_predicate_producers_seen_on_paths_by_final_writer"]
        self.assertEqual(categories["sint32_bits_to_float32"], ["OpSwitch"])
        self.assertEqual(categories["float32_constant"], ["OpSwitch"])

    def test_unreachable_writer_excluded_from_live_paths(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %idx2\n"
            "OpStore %p %frombits\nOpBranch %join\n"
            "%dead = OpLabel\nOpStore %p %zero\nOpReturn\n"
            "%join = OpLabel\n")
        a = audit(body)
        self.assertEqual(a["final_writer_categories_possible"], ["sint32_bits_to_float32"])
        self.assertEqual(a["static_writer_categories"]["float32_constant"], 1)

    def test_no_private_ssa_or_literal_values_exported(self):
        a = audit("%p = OpAccessChain %ptrscalar %local %idx2\n"
                  "OpStore %p %frombits\n")
        self.assertFalse(a["original_private_ids_exported"])
        self.assertNotIn("%", str(a))
        self.assertNotIn("idx2", str(a))
        self.assertTrue(a["branch_predicates_are_only_cfg_may_path_observations"])

    def test_wrong_original_descriptor_fails_closed(self):
        with self.assertRaises(ValueError):
            audit("OpStore %local %full\n",
                  head=HEADER.replace("OpDecorate %butter Binding 1",
                                      "OpDecorate %butter Binding 4"))

    def test_malformed_branch_fails_closed(self):
        with self.assertRaises(ValueError):
            audit("OpBranch %unknown\n" + "%new = OpLabel\n")

if __name__ == "__main__":
    unittest.main()
