"""Only synthetic SPIR-V-like source, no original Raft shader, pixels or literals."""
import io
import json
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

from scripts.t1_fft_site2_y_phi_path_tag import instrument, main

HEADER = """OpCapability Shader
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %gid
OpExecutionMode %main LocalSize 64 1 1
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
OpDecorate %gid BuiltIn GlobalInvocationId
%f = OpTypeFloat 32
%i = OpTypeInt 32 1
%u = OpTypeInt 32 0
%b = OpTypeBool
%v2f = OpTypeVector %f 2
%v2i = OpTypeVector %i 2
%v4f = OpTypeVector %f 4
%v3u = OpTypeVector %u 3
%pinu = OpTypePointer Input %v3u
%gid = OpVariable %pinu Input
%zero = OpConstant %f 0
%one = OpConstant %f 1
%one_i = OpConstant %i 1
%base = OpCompositeConstruct %v4f %zero %one %zero %one
%simple = OpCompositeConstruct %v2f %one %zero
%othercoords = OpBitcast %v2i %simple
%condition = OpIEqual %b %one_i %one_i
%void = OpTypeVoid
%fn = OpTypeFunction %void
%main = OpFunction %void None %fn
%entry = OpLabel
OpBranch %loop
%loop = OpLabel
%phi = OpPhi %v4f %base %entry %update %body
OpBranchConditional %condition %body %finish
%body = OpLabel
"""
BODY = """%lane = OpCompositeExtract %f %phi 2
%int = OpBitcast %i %lane
%sum = OpIAdd %i %int %one_i
%nextfloat = OpBitcast %f %sum
%update = OpCompositeInsert %v4f %nextfloat %phi 2
OpBranch %loop
"""
TAIL = """%finish = OpLabel
%shuffled = OpVectorShuffle %v2f %phi %phi 0 2
%coordinate = OpBitcast %v2i %shuffled
%fetch0 = OpImageFetch %v2f %source %othercoords
%fetch1 = OpImageFetch %v2f %butter %othercoords
%fetch2 = OpImageFetch %v2f %butter %coordinate
OpReturn
OpFunctionEnd
"""


def one(header=HEADER, body=BODY, tail=TAIL):
    return instrument(header + body + tail)


class ActualThirdYPathTagSourceTests(unittest.TestCase):
    def test_two_exact_edges_and_layout(self):
        program, report = one()
        self.assertTrue(report["two_unconditional_Cfg_predecessor_edges_tagged"])
        self.assertEqual(report["source_local_group_size"], [64, 1, 1])
        self.assertEqual(report["required_zeroed_counter_words"], 128)
        self.assertEqual(report["counter_storage_binding"], 3)
        self.assertEqual(program.count(" = OpAtomicIAdd "), 2)
        self.assertIn("%t1_phi_route_edge0_atomic = OpAtomicIAdd", program)
        self.assertIn("%t1_phi_route_edge1_atomic = OpAtomicIAdd", program)
        self.assertFalse(report["actual_GPU_counter_readback_proven"])
        self.assertFalse(report["output_invariance_proven"])

    def test_atomic_before_both_original_terminators(self):
        program, _ = one()
        entry = program.index("%entry = OpLabel")
        loop = program.index("%loop = OpLabel")
        body = program.index("%body = OpLabel")
        finish = program.index("%finish = OpLabel")
        self.assertLess(entry, program.index("%t1_phi_route_edge0_atomic"))
        self.assertLess(program.index("%t1_phi_route_edge0_atomic"), loop)
        self.assertLess(body, program.index("%t1_phi_route_edge1_atomic"))
        self.assertLess(program.index("%t1_phi_route_edge1_atomic"), finish)
        self.assertEqual(program.count("OpBranch %loop"), 2)
        self.assertIn("%phi = OpPhi %v4f %base %entry %update %body", program)

    def test_phi_pair_order_does_not_change_entry_backedge_tagging(self):
        head = HEADER.replace("%base %entry %update %body",
                              "%update %body %base %entry")
        program, result = one(header=head)
        self.assertEqual(program.count(" = OpAtomicIAdd "), 2)
        self.assertLess(program.index("%t1_phi_route_edge0_atomic"),
                        program.index("%loop = OpLabel"))
        self.assertLess(program.index("%t1_phi_route_edge1_atomic"),
                        program.index("%finish = OpLabel"))
        self.assertEqual(result["branch_tags"], ["entry", "backedge"])

    def test_binding3_collision_rejected(self):
        with self.assertRaises(ValueError):
            one(header=HEADER.replace("OpDecorate %gid BuiltIn",
                    "OpDecorate %other DescriptorSet 0\nOpDecorate %other Binding 3\nOpDecorate %gid BuiltIn"))

    def test_duplicate_source_owner_binding_rejected(self):
        with self.assertRaises(ValueError):
            one(header=HEADER.replace("OpDecorate %source Binding 0",
                                      "OpDecorate %source Binding 0\nOpDecorate %source Binding 0"))

    def test_wrong_gid_builtin_rejected(self):
        with self.assertRaises(ValueError):
            one(header=HEADER.replace("GlobalInvocationId", "LocalInvocationId"))

    def test_wrong_gid_uint_vector_shape_rejected(self):
        with self.assertRaises(ValueError):
            one(header=HEADER.replace("%v3u = OpTypeVector %u 3",
                                      "%v3u = OpTypeVector %i 3"))

    def test_other_workgroup_shape_rejected(self):
        with self.assertRaises(ValueError):
            one(header=HEADER.replace("LocalSize 64 1 1", "LocalSize 128 1 1"))

    def test_unverified_counter_id_prefix_rejected(self):
        with self.assertRaises(ValueError):
            one(header=HEADER.replace("OpCapability Shader",
                    "OpCapability Shader\n; %t1_phi_route_conflict"))

    def test_missing_third_read_rejected(self):
        with self.assertRaises(ValueError):
            one(tail=TAIL.replace("%fetch2 = OpImageFetch %v2f %butter %coordinate\n", ""))

    def test_structural_backedge_without_value_recurrence_rejected(self):
        altered = BODY.replace("%int = OpBitcast %i %lane",
                               "%int = OpCopyObject %i %one_i")
        with self.assertRaises(ValueError):
            one(body=altered)

    def test_nonbranch_predecessor_rejected(self):
        altered = BODY.replace("OpBranch %loop", "OpBranchConditional %condition %loop %finish")
        with self.assertRaises(ValueError):
            one(body=altered)

    def test_duplicate_predecessor_rejected(self):
        with self.assertRaises(ValueError):
            one(header=HEADER.replace("%update %body", "%update %entry"))

    def test_second_incoming_phi_type_drift_rejected(self):
        with self.assertRaises(ValueError):
            one(header=HEADER.replace("%base %entry", "%one %entry"))

    def test_private_source_bytes_ssa_and_sample_values_not_in_report(self):
        _, report = one()
        encoded = json.dumps(report)
        self.assertNotIn("%", encoded)
        self.assertNotIn("source", encoded.split('"status":')[0])
        self.assertFalse(report["private_original_shader_bytes_logged"])
        self.assertFalse(report["authored_unity_runtime_kernel_identity_proven"])
        self.assertFalse(report["android_water_proven"])

    def test_cli_errors_cannot_expose_private_inputs(self):
        stderr = io.StringIO()
        with (patch("sys.argv", ["tag", "/secret/original.spvasm", "/private/tagged.spvasm"]),
              redirect_stderr(stderr)):
            with self.assertRaises(SystemExit) as x:
                main()
        self.assertEqual(x.exception.code, 2)
        self.assertNotIn("secret", stderr.getvalue())
        self.assertNotIn("/private", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
