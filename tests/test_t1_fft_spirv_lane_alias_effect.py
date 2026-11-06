import unittest

from scripts.t1_fft_spirv_lane_alias_effect import analyze


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
%ptr = OpTypePointer Function %v2f
%ptrfloat = OpTypePointer Function %f32
%ptrint = OpTypePointer Function %i32
%idx0 = OpConstant %i32 0
%idx1 = OpConstant %i32 1
%idx2 = OpConstant %i32 2
%zero = OpConstant %f32 0
%one = OpConstant %f32 1
%v0 = OpCompositeConstruct %v2f %zero %zero
%cond = OpConstantTrue %bool
%void = OpTypeVoid
%ft = OpTypeFunction %void
%f = OpFunction %void None %ft
%entry = OpLabel
%local = OpVariable %ptr Function
"""

READ = """
%read = OpLoad %v2f %local
%coord = OpBitcast %v2i %read
%fetch0 = OpImageFetch %v2f %source %coord
%fetch1 = OpImageFetch %v2f %butter %coord
%fetch2 = OpImageFetch %v2f %butter %coord
OpReturn
OpFunctionEnd
"""

SWAPPED_READ = """
%read = OpLoad %v2f %local
%swapped = OpVectorShuffle %v2f %read %read 1 0
%coord = OpBitcast %v2i %swapped
%fetch0 = OpImageFetch %v2f %source %coord
%fetch1 = OpImageFetch %v2f %butter %coord
%fetch2 = OpImageFetch %v2f %butter %coord
OpReturn
OpFunctionEnd
"""


def lanes(body, ending=READ):
    return analyze(HEAD + body + ending, original_layout=True)["sites"][1]["lanes"]


class ComponentStoreTests(unittest.TestCase):
    def test_const_x_and_y_stores_reach_only_respective_lane(self):
        body = ("%px = OpAccessChain %ptrfloat %local %idx0\n"
                "%py = OpAccessChain %ptrfloat %local %idx1\n"
                "OpStore %px %zero\nOpStore %py %one\n")
        out = lanes(body)
        for axis in ("x", "y"):
            result = out[axis]
            self.assertEqual(result["static_same_lane_writers"], 1)
            self.assertEqual(result["static_other_lane_writers"], 1)
            self.assertEqual(result["reachable_writer_count"], 1)
            self.assertEqual(result["reachable_writer_forms"], {"same_lane": 1})
            self.assertFalse(result["uninitialized_possible"])
            self.assertFalse(result["unknown_write_possible"])
            self.assertFalse(result["full_value_proven"])

    def test_other_lane_only_does_not_initialize_target_lane(self):
        result = lanes("%py = OpAccessChain %ptrfloat %local %idx1\n"
                       "OpStore %py %one\n")["x"]
        self.assertEqual(result["static_other_lane_writers"], 1)
        self.assertEqual(result["reachable_writer_count"], 0)
        self.assertTrue(result["uninitialized_possible"])

    def test_full_vector_write_then_x_component_store(self):
        body = ("OpStore %local %v0\n"
                "%px = OpAccessChain %ptrfloat %local %idx0\n"
                "OpStore %px %one\n")
        out = lanes(body)
        self.assertEqual(out["x"]["reachable_writer_forms"], {"same_lane": 1})
        self.assertEqual(out["y"]["reachable_writer_forms"], {"whole": 1})
        self.assertFalse(out["y"]["unknown_write_possible"])

    def test_shader_shuffle_swaps_coordinate_and_physical_load_lane(self):
        body = ("%px = OpAccessChain %ptrfloat %local %idx0\n"
                "%py = OpAccessChain %ptrfloat %local %idx1\n"
                "OpStore %px %zero\nOpStore %py %one\n")
        out = lanes(body, SWAPPED_READ)
        self.assertEqual(out["x"]["physical_load_lane"], "y")
        self.assertEqual(out["y"]["physical_load_lane"], "x")
        self.assertEqual(out["x"]["reachable_writer_count"], 1)
        self.assertEqual(out["y"]["reachable_writer_count"], 1)

    def test_exact_copy_of_scalar_pointer_keeps_component_identity(self):
        result = lanes(
            "%px = OpAccessChain %ptrfloat %local %idx0\n"
            "%copy = OpCopyObject %ptrfloat %px\n"
            "OpStore %copy %zero\n")["x"]
        self.assertEqual(result["reachable_writer_forms"], {"same_lane": 1})

    def test_out_of_bounds_constant_cannot_be_trusted(self):
        result = lanes("%bad = OpAccessChain %ptrfloat %local %idx2\n"
                       "OpStore %bad %zero\n")["x"]
        self.assertTrue(result["unknown_write_possible"])
        self.assertEqual(result["static_unknown_alias_writers"], 1)
        self.assertEqual(result["reachable_writer_count"], 0)

    def test_dynamic_index_fails_closed_for_both_lanes(self):
        body = ("%i = OpVariable %ptrint Function\n"
                "%idx = OpLoad %i32 %i\n"
                "%px = OpAccessChain %ptrfloat %local %idx\n"
                "OpStore %px %zero\n")
        for result in lanes(body).values():
            self.assertTrue(result["unknown_write_possible"])
            self.assertFalse(result["full_value_proven"])

    def test_spec_constant_is_not_an_immutable_index(self):
        header = HEAD.replace("%idx2 = OpConstant %i32 2",
                              "%idx2 = OpSpecConstant %i32 0")
        report = analyze(header + "%p = OpAccessChain %ptrfloat %local %idx2\n"
                         "OpStore %p %zero\n" + READ, original_layout=True)
        self.assertTrue(report["sites"][1]["lanes"]["x"]["unknown_write_possible"])

    def test_pointer_phi_alias_is_not_guessed(self):
        body = ("%other = OpVariable %ptr Function\n"
                "%p = OpSelect %ptr %cond %local %other\n"
                "OpStore %p %v0\n")
        self.assertTrue(lanes(body)["x"]["unknown_write_possible"])

    def test_unreachable_store_must_not_be_a_reaching_writer(self):
        body = ("OpStore %local %v0\nOpBranch %join\n"
                "%dead = OpLabel\n"
                "%px = OpAccessChain %ptrfloat %local %idx0\n"
                "OpStore %px %zero\nOpReturn\n"
                "%join = OpLabel\n")
        out = lanes(body)["x"]
        self.assertEqual(out["static_same_lane_writers"], 1)
        self.assertEqual(out["reachable_writer_forms"], {"whole": 1})

    def test_conditional_writers_preserve_two_may_reach_values(self):
        body = ("OpBranchConditional %cond %left %right\n"
                "%left = OpLabel\nOpStore %local %v0\nOpBranch %join\n"
                "%right = OpLabel\n"
                "%px = OpAccessChain %ptrfloat %local %idx0\n"
                "OpStore %px %zero\nOpBranch %join\n"
                "%join = OpLabel\n")
        result = lanes(body)["x"]
        self.assertEqual(result["reachable_writer_count"], 2)
        self.assertEqual(result["reachable_writer_forms"], {"same_lane": 1, "whole": 1})
        self.assertFalse(result["uninitialized_possible"])

    def test_loop_component_write_keeps_initial_and_backedge_writer(self):
        body = ("OpStore %local %v0\nOpBranch %header\n"
                "%header = OpLabel\n"
                "OpBranchConditional %cond %body %join\n"
                "%body = OpLabel\n"
                "%px = OpAccessChain %ptrfloat %local %idx0\n"
                "OpStore %px %zero\nOpBranch %header\n"
                "%join = OpLabel\n")
        result = lanes(body)["x"]
        self.assertEqual(result["reachable_writer_count"], 2)

    def test_pointer_escape_remains_unknown_despite_later_direct_write(self):
        body = ("%ptrptr = OpTypePointer Function %ptr\n"
                "%other = OpVariable %ptrptr Function\n"
                "OpStore %other %local\n"
                "OpStore %local %v0\n")
        result = lanes(body)["x"]
        self.assertTrue(result["pointer_escape_possible"])

    def test_wrong_original_descriptor_bindings_rejected(self):
        with self.assertRaises(ValueError):
            analyze(HEAD.replace("OpDecorate %butter Binding 1",
                                 "OpDecorate %butter Binding 4") + "OpStore %local %v0\n" + READ,
                    original_layout=True)

    def test_report_has_no_ssa_ids_or_index_literals(self):
        report = analyze(HEAD + "OpStore %local %v0\n" + READ,
                         original_layout=True)
        self.assertTrue(report["no_private_identifiers_exported"])
        self.assertFalse(report["original_integer_origin_proven"])
        self.assertNotIn("%", str(report))


if __name__ == "__main__":
    unittest.main()
