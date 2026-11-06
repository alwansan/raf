import unittest

from scripts.t1_fft_site1_y_inequal_source import analyze


HEAD = """
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
%ptrint = OpTypePointer Function %i32
%ptrptr = OpTypePointer Function %ptr4
%i0 = OpConstant %i32 0
%i1 = OpConstant %i32 1
%i2 = OpConstant %i32 2
%f0 = OpConstant %f32 0
%f1 = OpConstant %f32 1
%bits = OpBitcast %f32 %i1
%full = OpCompositeConstruct %v4f %f1 %f1 %f1 %f1
%cond = OpINotEqual %bool %i0 %i1
%void = OpTypeVoid
%ft = OpTypeFunction %void
%fun = OpFunction %void None %ft
%entry = OpLabel
%local = OpVariable %ptr4 Function
"""

READ = """
%load4 = OpLoad %v4f %local
%shuffle = OpVectorShuffle %v2f %load4 %load4 0 2
%coord = OpBitcast %v2i %shuffle
%fetch0 = OpImageFetch %v2f %source %coord
%fetch1 = OpImageFetch %v2f %butter %coord
%fetch2 = OpImageFetch %v2f %butter %coord
OpReturn
OpFunctionEnd
"""


def probe(body, header=HEAD):
    return analyze(header + body + READ, original_layout=True)


class OriginalInequalityProbeTests(unittest.TestCase):
    def test_comparison_gates_read_on_true_successor(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %i2\n"
            "OpBranchConditional %cond %yes %no\n"
            "%yes = OpLabel\nOpStore %p %f0\nOpBranch %join\n"
            "%no = OpLabel\nOpReturn\n"
            "%join = OpLabel\n")
        a = probe(body)
        self.assertEqual(a["inequality_branches_relevant_to_read"], 1)
        x = a["anonymous_branches"][0]
        self.assertEqual(x["read_gate"], "only_true_successor_may_reach_read")
        self.assertEqual(x["inputs"], [
            {"kind": "sint32", "producer": "OpConstant"},
            {"kind": "sint32", "producer": "OpConstant"}])
        self.assertEqual(x["true_successor"]["possible_last_writes_since_branch"],
                         ["float32_constant"])
        self.assertFalse(x["false_successor"]["read_can_be_reached"])

    def test_comparison_gates_read_on_false_successor(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %i2\n"
            "OpBranchConditional %cond %no %yes\n"
            "%no = OpLabel\nOpReturn\n"
            "%yes = OpLabel\nOpStore %p %f0\nOpBranch %join\n"
            "%join = OpLabel\n")
        self.assertEqual(probe(body)["anonymous_branches"][0]["read_gate"],
                         "only_false_successor_may_reach_read")

    def test_comparison_may_select_distinct_postbranch_writers(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %i2\n"
            "OpBranchConditional %cond %bit %float\n"
            "%bit = OpLabel\nOpStore %p %bits\nOpBranch %join\n"
            "%float = OpLabel\nOpStore %p %f0\nOpBranch %join\n"
            "%join = OpLabel\n")
        x=probe(body)["anonymous_branches"][0]
        self.assertEqual(x["read_gate"], "both_successors_may_reach_read")
        self.assertEqual(x["true_successor"]["possible_last_writes_since_branch"],
                         ["sint32_bits_to_float32"])
        self.assertEqual(x["false_successor"]["possible_last_writes_since_branch"],
                         ["float32_constant"])
        self.assertTrue(x["suffix_last_writer_sets_differ"])
        self.assertFalse(x["condition_selects_runtime_value_proven"]
                         if "condition_selects_runtime_value_proven" in x else x["branch_truth_proven"])

    def test_postjoin_writer_overwrites_both_paths(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %i2\n"
            "OpBranchConditional %cond %left %right\n"
            "%left = OpLabel\nOpBranch %join\n"
            "%right = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\nOpStore %p %f0\n")
        x = probe(body)["anonymous_branches"][0]
        self.assertFalse(x["suffix_last_writer_sets_differ"])
        self.assertEqual(x["true_successor"]["possible_last_writes_since_branch"],
                         ["float32_constant"])

    def test_loaded_integer_operand_is_typed_without_values(self):
        body = (
            "%pint = OpVariable %ptrint Function\n"
            "%int = OpLoad %i32 %pint\n"
            "%ineq = OpINotEqual %bool %int %i0\n"
            "OpBranchConditional %ineq %left %right\n"
            "%left = OpLabel\nOpStore %local %full\nOpBranch %join\n"
            "%right = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\n")
        x = probe(body)["anonymous_branches"][0]
        self.assertEqual(x["inputs"][0], {"kind": "sint32", "producer": "OpLoad"})
        self.assertEqual(x["inputs"][1], {"kind": "sint32", "producer": "OpConstant"})
        self.assertEqual(x["predicate"], "OpINotEqual")

    def test_dynamic_component_index_keeps_unknown(self):
        body = (
            "%indexptr = OpVariable %ptrint Function\n"
            "%idx = OpLoad %i32 %indexptr\n"
            "%p = OpAccessChain %ptrscalar %local %idx\n"
            "OpBranchConditional %cond %write %skip\n"
            "%write = OpLabel\nOpStore %p %f0\nOpBranch %join\n"
            "%skip = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\n")
        x = probe(body)["anonymous_branches"][0]
        self.assertIn("unknown_write", x["true_successor"]["possible_last_writes_since_branch"])

    def test_unreachable_inequality_branch_does_not_contaminate_report(self):
        body = (
            "OpBranch %join\n"
            "%dead = OpLabel\nOpBranchConditional %cond %one %two\n"
            "%one = OpLabel\nOpStore %local %full\nOpBranch %join\n"
            "%two = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\n")
        self.assertEqual(probe(body)["inequality_branches_relevant_to_read"], 0)

    def test_other_condition_opcode_not_mistaken_for_inequality(self):
        header = HEAD.replace("%cond = OpINotEqual %bool %i0 %i1",
                              "%cond = OpIEqual %bool %i0 %i1")
        body = (
            "OpBranchConditional %cond %yes %no\n"
            "%yes = OpLabel\nOpBranch %join\n"
            "%no = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\n")
        self.assertEqual(probe(body, header=header)["inequality_branches_relevant_to_read"], 0)

    def test_no_conditional_has_no_branch(self):
        self.assertEqual(probe("OpStore %local %full\n")["anonymous_branches"], [])

    def test_loop_terminates_under_bounded_state_model(self):
        body = (
            "%p = OpAccessChain %ptrscalar %local %i2\n"
            "OpBranch %loop\n"
            "%loop = OpLabel\n"
            "OpBranchConditional %cond %repeat %join\n"
            "%repeat = OpLabel\nOpStore %p %f0\nOpBranch %loop\n"
            "%join = OpLabel\n")
        x=probe(body)["anonymous_branches"][0]
        self.assertTrue(x["true_successor"]["read_can_be_reached"])
        self.assertEqual(x["read_gate"], "both_successors_may_reach_read")

    def test_pointer_escape_tracked_separately_from_store(self):
        body = (
            "%out = OpVariable %ptrptr Function\n"
            "%p = OpAccessChain %ptrscalar %local %i2\n"
            "OpBranchConditional %cond %left %right\n"
            "%left = OpLabel\nOpStore %out %local\nOpStore %p %f0\nOpBranch %join\n"
            "%right = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\n")
        x=probe(body)["anonymous_branches"][0]
        self.assertTrue(x["true_successor"]["escaped_pointer_possible"])

    def test_wrong_original_descriptor_fails_closed(self):
        with self.assertRaises(ValueError):
            probe("OpStore %local %full\n",
                  header=HEAD.replace("OpDecorate %butter Binding 1",
                                      "OpDecorate %butter Binding 8"))

    def test_no_private_ids_or_literal_values_exported(self):
        a=probe("OpStore %local %full\n")
        self.assertFalse(a["original_ids_and_literal_values_exported"])
        self.assertFalse(a["dynamic_truth_proven"])
        self.assertNotIn("%", str(a))
        self.assertNotIn("i0", str(a))

    def test_invalid_successor_rejected(self):
        with self.assertRaises(ValueError):
            probe("OpBranchConditional %cond %missing %missing\n")


if __name__ == "__main__":
    unittest.main()
