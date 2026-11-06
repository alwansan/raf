import unittest

from scripts.t1_fft_hlsl_nested_phi_lineage import analyze
HEAD = """
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%float = OpTypeFloat 32
%int = OpTypeInt 32 1
%v2f = OpTypeVector %float 2
%v2i = OpTypeVector %int 2
%bool = OpTypeBool
%f0 = OpConstant %float 0
%f1 = OpConstant %float 1
%i1 = OpConstant %int 1
%condition = OpConstantTrue %bool
%void = OpTypeVoid
%ft = OpTypeFunction %void
%func = OpFunction %void None %ft
%entry = OpLabel
"""



NESTED = """
%base = OpCompositeConstruct %v2f %f0 %f1
OpBranchConditional %condition %left %right
%left = OpLabel
%ivec = OpCompositeConstruct %v2i %i1 %i1
%bits = OpBitcast %v2f %ivec
OpBranch %join
%right = OpLabel
OpBranchConditional %condition %middle %fallback
%middle = OpLabel
%fvec = OpCompositeConstruct %v2f %f1 %f0
OpBranch %inner_join
%fallback = OpLabel
OpBranch %inner_join
%inner_join = OpLabel
%inner = OpPhi %v2f %fvec %middle %base %fallback
OpBranch %join
%join = OpLabel
%outer = OpPhi %v2f %bits %left %inner %inner_join
"""

READ = """
%coordf = OpCopyObject %v2f %outer
%coordi = OpBitcast %v2i %coordf
%fetch0 = OpImageFetch %v2f %source %coordi
%fetch1 = OpImageFetch %v2f %butter %coordi
%fetch2 = OpImageFetch %v2f %butter %coordi
OpReturn
OpFunctionEnd
"""


def result(flow=NESTED, read=READ, head=HEAD):
    return analyze(head + flow + read, original_layout=True)


class NestedPhiSourceTests(unittest.TestCase):
    def test_nested_phi_second_input_is_recursive_typed_merge(self):
        a=result()
        self.assertEqual(a["status"], "bounded_nested_phi_component_provenance")
        self.assertEqual(a["phi_expansions"], 2)
        self.assertEqual(a["top_phi_kind"], "float32_vector")
        self.assertEqual(a["top_selected_component"], "x")
        self.assertEqual(a["chain"]["incoming_count"], 2)
        nested=a["chain"]["incoming"][1]["source"]
        self.assertEqual(nested["status"], "phi_merge")
        self.assertEqual(nested["incoming_count"], 2)
        self.assertEqual(nested["incoming"][0]["source"]["status"], "component_routing")
        self.assertFalse(a["selected_runtime_predecessor_proven"])

    def test_first_source_integer_bitcast_remains_distinct(self):
        a=result()
        first=a["chain"]["incoming"][0]["source"]
        self.assertEqual(first["status"], "component_routing")
        self.assertEqual(first["opcode"], "OpBitcast")
        leaf=first["source"]
        self.assertEqual(leaf["status"], "component_routing")
        self.assertEqual(leaf["opcode"], "OpCompositeConstruct")
        self.assertNotIn("%", str(a))

    def test_phi_predecessors_must_have_real_edges(self):
        with self.assertRaises(ValueError):
            result(NESTED.replace("%fvec %middle", "%fvec %not_block"))

    def test_nested_incoming_value_type_must_match_vector(self):
        with self.assertRaises(ValueError):
            result(NESTED.replace("%base %fallback", "%f0 %fallback"))

    def test_phi_input_count_above_bound_is_rejected(self):
        pairs=" ".join(["%fvec %middle"]*13)
        with self.assertRaises(ValueError):
            result(NESTED.replace("%fvec %middle %base %fallback", pairs))

    def test_unknown_private_opcode_is_only_other_opcode(self):
        modified=NESTED.replace(
            "%fvec = OpCompositeConstruct %v2f %f1 %f0",
            "%fvec = OpSuperSecret %v2f %base %base")
        a=result(modified)
        terminal=a["chain"]["incoming"][1]["source"]["incoming"][0]["source"]
        self.assertEqual(terminal["status"], "typed_boundary")
        self.assertEqual(terminal["immediate_opcode"], "other_opcode")
        self.assertNotIn("OpSuperSecret", str(a))

    def test_shuffle_can_select_y_phi_component(self):
        read=READ.replace(
            "%coordf = OpCopyObject %v2f %outer",
            "%coordf = OpVectorShuffle %v2f %outer %outer 1 0")
        a=result(read=read)
        self.assertEqual(a["top_selected_component"], "y")
        self.assertEqual(a["chain"]["selected_component"], "y")

    def test_branch_cycle_is_annotated_not_falsely_resolved(self):
        flow="""
%initial = OpCompositeConstruct %v2f %f0 %f1
OpBranch %loop
%loop = OpLabel
%outer = OpPhi %v2f %initial %entry %outer %repeat
OpBranchConditional %condition %repeat %end
%repeat = OpLabel
OpBranch %loop
%end = OpLabel
"""
        a=result(flow=flow)
        self.assertEqual(a["phi_expansions"], 1)
        self.assertEqual(a["cycle_boundaries"], 1)
        self.assertEqual(a["chain"]["incoming"][1]["source"]["status"],
                         "loop_carried_or_cyclic_phi")
        self.assertFalse(a["actual_original_vs_unity_numeric_parity_proven"])

    def test_phis_do_not_prove_actual_branch_truth(self):
        a=result()
        self.assertFalse(a["selected_runtime_predecessor_proven"])
        self.assertFalse(a["adreno_water_proven"])
        self.assertFalse(a["private_values_exported"])

    def test_without_phi_in_selected_x_lane_returns_bounded_stop(self):
        read=READ.replace("%coordf = OpCopyObject %v2f %outer",
                          "%coordf = OpCompositeConstruct %v2f %f0 %f1")
        a=result(read=read)
        self.assertEqual(a["status"], "other_boundary")

    def test_large_composite_depth_stops_without_recursion_error(self):
        prefix=NESTED.replace(
            "%outer = OpPhi %v2f %bits %left %inner %inner_join",
            "%outer = OpPhi %v2f %bits %left %inner %inner_join")
        # Unexpected input path with 26 transparent copy instructions must
        # safely use the global depth cap.
        copies="\n".join(f"%copy{k} = OpCopyObject %v2f %copy{k-1}"
                          for k in range(1,27))
        flow=prefix.replace("%inner = OpPhi %v2f %fvec %middle %base %fallback",
                            "%copy0 = OpCopyObject %v2f %base\n"+copies+
                            "\n%inner = OpPhi %v2f %fvec %middle %copy26 %fallback")
        a=result(flow=flow)
        branch=a["chain"]["incoming"][1]["source"]["incoming"][1]["source"]
        while branch["status"]=="component_routing":
            branch=branch["source"]
        self.assertEqual(branch["status"], "bounded_unknown")

    def test_original_binding_mismatch_fails_closed(self):
        with self.assertRaises(ValueError):
            result(head=HEAD.replace("OpDecorate %butter Binding 1",
                                     "OpDecorate %butter Binding 8"))

    def test_privacy_output_never_contains_source_ids_or_literals(self):
        a=result()
        self.assertNotIn("%", str(a))
        self.assertNotIn("inner_join", str(a))
        self.assertNotIn("i1", str(a))
        self.assertNotIn("original_shader_bytes", str(a))


if __name__ == "__main__":
    unittest.main()
