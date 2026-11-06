import unittest

from scripts.t1_fft_site1_x_writer_lineage import analyze


HEADER = """
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%float = OpTypeFloat 32
%int = OpTypeInt 32 1
%uint = OpTypeInt 32 0
%bool = OpTypeBool
%v2f = OpTypeVector %float 2
%v2i = OpTypeVector %int 2
%ptrv = OpTypePointer Function %v2f
%ptrscalar = OpTypePointer Function %float
%ptrint = OpTypePointer Function %int
%ptrptr = OpTypePointer Function %ptrv
%i0 = OpConstant %int 0
%i1 = OpConstant %int 1
%f0 = OpConstant %float 0
%f1 = OpConstant %float 1
%fv0 = OpCompositeConstruct %v2f %f0 %f0
%fv1 = OpCompositeConstruct %v2f %f1 %f1
%iv = OpCompositeConstruct %v2i %i0 %i1
%condition = OpConstantTrue %bool
%void = OpTypeVoid
%funType = OpTypeFunction %void
%f = OpFunction %void None %funType
%entry = OpLabel
%local = OpVariable %ptrv Function
"""

READS = """
%read = OpLoad %v2f %local
%coord = OpBitcast %v2i %read
%fetch0 = OpImageFetch %v2f %source %coord
%fetch1 = OpImageFetch %v2f %butter %coord
%fetch2 = OpImageFetch %v2f %butter %coord
OpReturn
OpFunctionEnd
"""


def audit(body, header=HEADER, tail=READS):
    return analyze(header + body + tail, original_layout=True)


class ButterflyXWriterLineageTests(unittest.TestCase):
    def test_first_shuffle_input_preserves_signed_bits_without_numeric_conversion(self):
        body = (
            "%bits = OpBitcast %v2f %iv\n"
            "%shuffle = OpVectorShuffle %v2f %bits %fv0 0 1\n"
            "OpStore %local %shuffle\n"
        )
        a = audit(body)
        self.assertEqual(a["reachable_last_writer_count"], 1)
        self.assertEqual(a["possible_last_writer_component_sources"][0]["status"],
                         "constant_boundary")
        s = a["possible_last_writer_component_sources"][0]
        self.assertEqual(s["shuffle_inputs"], ["first"])
        self.assertEqual(s["cast_kinds"], ["sint32_bits_to_float32"])
        self.assertEqual(s["ssa_ops"][:3],
                         ["OpVectorShuffle", "OpBitcast", "OpCompositeConstruct"])
        self.assertFalse(a["original_numeric_semantics_proven"])

    def test_second_shuffle_input_selected_without_index_literal_exposure(self):
        body = (
            "%bits = OpBitcast %v2f %iv\n"
            "%shuffle = OpVectorShuffle %v2f %fv0 %bits 2 3\n"
            "OpStore %local %shuffle\n"
        )
        a = audit(body)
        self.assertEqual(a["possible_last_writer_component_sources"][0]["shuffle_inputs"],
                         ["second"])
        self.assertEqual(a["possible_last_writer_component_sources"][0]["cast_kinds"],
                         ["sint32_bits_to_float32"])

    def test_function_local_load_boundary_not_mistaken_for_constant(self):
        body = (
            "%inputVar = OpVariable %ptrv Function\n"
            "%input = OpLoad %v2f %inputVar\n"
            "%shuffle = OpVectorShuffle %v2f %input %fv0 0 1\n"
            "OpStore %local %shuffle\n"
        )
        s = audit(body)["possible_last_writer_component_sources"][0]
        self.assertEqual(s["status"], "memory_load_boundary")
        self.assertEqual(s["leaf_storage_class"], "Function")
        self.assertEqual(s["leaf_numeric_kind"], "float32_vector")

    def test_arithmetic_is_explicit_unresolved_numeric_boundary(self):
        body = (
            "%math = OpFAdd %v2f %fv0 %fv1\n"
            "%shuffle = OpVectorShuffle %v2f %math %fv0 0 1\n"
            "OpStore %local %shuffle\n"
        )
        s = audit(body)["possible_last_writer_component_sources"][0]
        self.assertEqual(s["status"], "arithmetic_boundary")
        self.assertEqual(s["arithmetic_opcode"], "OpFAdd")
        self.assertFalse(audit(body)["complete_proof"])

    def test_two_conditional_whole_vector_writers_remain_candidates(self):
        body = (
            "OpBranchConditional %condition %left %right\n"
            "%left = OpLabel\nOpStore %local %fv0\nOpBranch %join\n"
            "%right = OpLabel\nOpStore %local %fv1\nOpBranch %join\n"
            "%join = OpLabel\n"
        )
        a = audit(body)
        self.assertEqual(a["reachable_last_writer_count"], 2)
        self.assertEqual(a["static_affecting_store_count"], 2)
        self.assertFalse(a["possible_uninitialized_path"])

    def test_overwritten_original_writer_not_claimed_reaching(self):
        body = (
            "%bits = OpBitcast %v2f %iv\n"
            "%first = OpVectorShuffle %v2f %bits %fv0 0 1\n"
            "OpStore %local %first\nOpStore %local %fv1\n"
        )
        a = audit(body)
        self.assertEqual(a["static_affecting_store_count"], 2)
        self.assertEqual(a["reachable_last_writer_count"], 1)
        self.assertEqual(a["possible_last_writer_component_sources"][0]["status"],
                         "constant_boundary")

    def test_noninitializing_branch_preserves_uninitialized_flag(self):
        body = (
            "OpBranchConditional %condition %left %right\n"
            "%left = OpLabel\nOpStore %local %fv0\nOpBranch %join\n"
            "%right = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\n"
        )
        a = audit(body)
        self.assertEqual(a["reachable_last_writer_count"], 1)
        self.assertTrue(a["possible_uninitialized_path"])

    def test_other_lane_component_write_does_not_overwrite_x_whole_writer(self):
        body = (
            "OpStore %local %fv0\n"
            "%py = OpAccessChain %ptrscalar %local %i1\n"
            "OpStore %py %f1\n"
        )
        a = audit(body)
        self.assertEqual(a["static_affecting_store_count"], 1)
        self.assertEqual(a["reachable_last_writer_count"], 1)
        self.assertEqual(a["possible_last_writer_component_sources"][0]["write_form"],
                         "whole")

    def test_same_x_scalar_component_writer_replaces_whole_writer(self):
        body = (
            "OpStore %local %fv0\n"
            "%px = OpAccessChain %ptrscalar %local %i0\n"
            "OpStore %px %f1\n"
        )
        a = audit(body)
        self.assertEqual(a["reachable_last_writer_count"], 1)
        self.assertEqual(a["possible_last_writer_component_sources"][0]["write_form"],
                         "same_lane")
        self.assertEqual(a["possible_last_writer_component_sources"][0]["status"],
                         "constant_boundary")

    def test_unknown_dynamic_index_is_retained_as_hazard(self):
        body = (
            "OpStore %local %fv0\n"
            "%indexVar = OpVariable %ptrint Function\n"
            "%index = OpLoad %int %indexVar\n"
            "%p = OpAccessChain %ptrscalar %local %index\n"
            "OpStore %p %f1\n"
        )
        a = audit(body)
        self.assertTrue(a["possible_unknown_alias_write"])
        self.assertFalse(a["complete_proof"])

    def test_escaped_pointer_retained_even_after_subsequent_direct_write(self):
        body = (
            "%sink = OpVariable %ptrptr Function\n"
            "OpStore %sink %local\n"
            "OpStore %local %fv0\n"
        )
        a = audit(body)
        self.assertTrue(a["possible_pointer_escape"])
        self.assertEqual(a["reachable_last_writer_count"], 1)
        self.assertFalse(a["complete_proof"])

    def test_loop_two_last_writers_if_backedge_can_be_taken(self):
        body = (
            "OpStore %local %fv0\nOpBranch %head\n"
            "%head = OpLabel\n"
            "OpBranchConditional %condition %body %join\n"
            "%body = OpLabel\nOpStore %local %fv1\nOpBranch %head\n"
            "%join = OpLabel\n"
        )
        a = audit(body)
        self.assertEqual(a["reachable_last_writer_count"], 2)

    def test_unreachable_other_writer_excluded(self):
        body = (
            "OpStore %local %fv0\nOpBranch %join\n"
            "%dead = OpLabel\nOpStore %local %fv1\nOpReturn\n"
            "%join = OpLabel\n"
        )
        a = audit(body)
        self.assertEqual(a["static_affecting_store_count"], 2)
        self.assertEqual(a["reachable_last_writer_count"], 1)

    def test_malformed_middle_of_block_terminator_rejected(self):
        with self.assertRaises(ValueError):
            audit("OpBranch %join\nOpStore %local %fv0\n"
                  "%join = OpLabel\n")

    def test_unexpected_original_image_descriptor_binding_rejected(self):
        with self.assertRaises(ValueError):
            audit("OpStore %local %fv0\n",
                  header=HEADER.replace("OpDecorate %butter Binding 1",
                                        "OpDecorate %butter Binding 3"))

    def test_private_identifiers_not_exported(self):
        a = audit("OpStore %local %fv0\n")
        self.assertFalse(a["original_ids_and_constants_exported"])
        self.assertNotIn("%", str(a))
        self.assertNotIn("i0", str(a))
        self.assertFalse(a["numeric_parity_proven"])


if __name__ == "__main__":
    unittest.main()
