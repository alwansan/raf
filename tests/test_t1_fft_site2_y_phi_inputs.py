"""Synthetic source-free OpPhi CFG controls, no proprietary bytes or GPU invocations."""
import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch
from scripts.t1_fft_site2_y_phi_inputs import analyze, main

HEAD = """OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%f = OpTypeFloat 32
%i = OpTypeInt 32 1
%bool = OpTypeBool
%v2f = OpTypeVector %f 2
%v2i = OpTypeVector %i 2
%zero = OpConstant %f 0
%one = OpConstant %f 1
%one_i = OpConstant %i 1
%two = OpCompositeConstruct %v2f %one %zero
%coordsimple = OpBitcast %v2i %two
%bitfloat = OpBitcast %f %one_i
%condition = OpIEqual %bool %one_i %one_i
%void = OpTypeVoid
%funct = OpTypeFunction %void
%main = OpFunction %void None %funct
%entry = OpLabel
"""
BRANCH = """OpBranchConditional %condition %left %right
%left = OpLabel
OpBranch %join
%right = OpLabel
OpBranch %join
%join = OpLabel
%phi = OpPhi %f %zero %left %bitfloat %right
"""
TAIL = """%vector = OpCompositeConstruct %v2f %zero %phi
%coordinate = OpBitcast %v2i %vector
%fetch0 = OpImageFetch %v2f %source %coordsimple
%fetch1 = OpImageFetch %v2f %butter %coordsimple
%fetch2 = OpImageFetch %v2f %butter %coordinate
OpReturn
OpFunctionEnd
"""

def inspect(branch=BRANCH, head=HEAD, tail=TAIL):
    return analyze(head + branch + tail, require_original=True)

class Site2PhiTests(unittest.TestCase):
    def test_two_original_derived_phi_incoming_producers(self):
        x = inspect()
        self.assertEqual(x["status"], "verified_translated_site2_y_phi_incoming_cfg")
        self.assertEqual(x["incoming_count"], 2)
        self.assertEqual(x["site"], 2)
        self.assertEqual(x["role"], "butterfly")
        self.assertEqual(x["phi_value_kind"], "float32_scalar")
        self.assertEqual(x["selected_phi_lane"], "x")
        self.assertEqual([i["immediate_value_opcode"] for i in x["incoming"]],
                         ["OpConstant", "OpBitcast"])
        self.assertFalse(x["actual_branch_truth_proven"])

    def test_bitcarrier_trace_is_typed_without_private_bits(self):
        x = inspect()
        data = str(x["incoming"][1]["typed_input_component"])
        self.assertIn("sint32_bits_to_float32", data)
        self.assertNotIn("%one_i", data)
        self.assertNotIn("%", str(x))

    def test_predecessors_are_actual_incoming_cfg_edges(self):
        x = inspect()
        for v in x["incoming"]:
            self.assertEqual(v["predecessor"]["terminator"], "OpBranch")
            self.assertEqual(v["predecessor"]["edge"], "unconditional")
            self.assertFalse(v["predecessor_in_structural_cfg_cycle"])

    def test_non_phi_is_honestly_unresolved(self):
        r = inspect(branch=BRANCH.replace(
            "%phi = OpPhi %f %zero %left %bitfloat %right",
            "%phi = OpCopyObject %f %zero"))
        self.assertEqual(r["status"], "translated_site2_y_no_verifiable_phi")
        self.assertFalse(r["actual_branch_or_numeric_parity_proven"])

    def test_duplicate_incoming_predecessor_is_rejected(self):
        with self.assertRaises(ValueError):
            inspect(branch=BRANCH.replace("%bitfloat %right", "%bitfloat %left"))

    def test_incoming_type_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            inspect(branch=BRANCH.replace("%zero %left", "%one_i %left"))

    def test_nonincoming_predecessor_not_trusted(self):
        with self.assertRaises(ValueError):
            inspect(branch=BRANCH.replace("OpBranch %join", "OpBranch %right", 1))

    def test_wrong_butterfly_binding_rejected(self):
        with self.assertRaises(ValueError):
            inspect(head=HEAD.replace("OpDecorate %butter Binding 1",
                                      "OpDecorate %butter Binding 3"))

    def test_missing_third_fetch_rejected(self):
        with self.assertRaises(ValueError):
            inspect(tail=TAIL.replace("%fetch2 = OpImageFetch %v2f %butter %coordinate\n", ""))

    def test_loop_phi_backedge_recognized_as_structural_only(self):
        branch = ("""OpBranch %loop
%loop = OpLabel
%phi = OpPhi %f %zero %entry %bitfloat %loop
OpBranchConditional %condition %loop %join
%join = OpLabel
""")
        x = inspect(branch=branch)
        self.assertTrue(x["incoming"][1]["predecessor_in_structural_cfg_cycle"])
        self.assertFalse(x["actual_branch_truth_proven"])

    def test_report_is_explicitly_not_numeric_or_android_proof(self):
        x = inspect()
        self.assertFalse(x["original_to_translated_numeric_parity_proven"])
        self.assertFalse(x["unity_gpu_compiler_executed"])
        self.assertFalse(x["android_water_proven"])
        self.assertFalse(x["private_identifiers_exported"])

    def test_private_cli_failure_does_not_emit_operands(self):
        out = io.StringIO()
        with (patch("sys.argv", ["phi", "/private/some-module.spv"]),
              redirect_stderr(out)):
            with self.assertRaises(SystemExit) as res:
                main()
        self.assertEqual(res.exception.code, 2)
        self.assertNotIn("some-module", out.getvalue())

if __name__ == "__main__":
    unittest.main()
