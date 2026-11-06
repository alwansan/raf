"""Synthetic-only SPIR-V pseudo-assembly; no original shader or game data."""
import unittest
from scripts.t1_fft_site2_y_cfg import analyze

HEAD = """OpDecorate %src DescriptorSet 0
OpDecorate %src Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%f = OpTypeFloat 32
%i = OpTypeInt 32 1
%bool = OpTypeBool
%v2f = OpTypeVector %f 2
%v2i = OpTypeVector %i 2
%v4f = OpTypeVector %f 4
%ptr = OpTypePointer Function %v4f
%ptrf = OpTypePointer Function %f
%ptri = OpTypePointer Function %i
%zero = OpConstant %f 0
%one = OpConstant %f 1
%zero_i = OpConstant %i 0
%one_i = OpConstant %i 1
%two = OpConstant %i 2
%frombits = OpBitcast %f %one_i
%condition = OpIEqual %bool %one_i %zero_i
%two_f = OpCompositeConstruct %v2f %one %zero
%two_i = OpBitcast %v2i %two_f
%void = OpTypeVoid
%type = OpTypeFunction %void
%fmain = OpFunction %void None %type
%entry = OpLabel
%local = OpVariable %ptr Function
"""
TAIL = """%read = OpLoad %v4f %local
%swizzle = OpVectorShuffle %v2f %read %read 0 2
%third = OpBitcast %v2i %swizzle
%fetch0 = OpImageFetch %v2f %src %two_i
%fetch1 = OpImageFetch %v2f %butter %two_i
%fetch2 = OpImageFetch %v2f %butter %third
OpReturn
OpFunctionEnd
"""
def audit(body="", head=HEAD, tail=TAIL):
    return analyze(head + body + tail, require_original=True)

class Site2YTests(unittest.TestCase):
    def test_third_fetch_physical_y_maps_third_float_lane(self):
        r = audit("%p = OpAccessChain %ptrf %local %two\nOpStore %p %frombits\n")
        self.assertEqual(r["site"], 2)
        self.assertTrue(r["physical_lane_outside_xy"])
        self.assertEqual(r["final_writer_categories_possible"], ["sint32_bits_to_float32"])
        self.assertTrue(r["last_writer_evidence_available"])

    def test_exclusive_branch_writers(self):
        body = ("%p = OpAccessChain %ptrf %local %two\n"
                "OpBranchConditional %condition %branch_a %branch_b\n"
                "%branch_a = OpLabel\nOpStore %p %frombits\nOpBranch %join\n"
                "%branch_b = OpLabel\nOpStore %p %zero\nOpBranch %join\n"
                "%join = OpLabel\n")
        r = audit(body)
        self.assertEqual(r["final_writer_categories_possible"],
                         ["float32_constant", "sint32_bits_to_float32"])
        self.assertFalse(r["may_visit_bitcarrier_and_float_constant_on_same_cfg_path"])
        self.assertFalse(r["actual_invocation_branch_truth_proven"])

    def test_last_writer_overrides_previous(self):
        r = audit("%p = OpAccessChain %ptrf %local %two\n"
                  "OpStore %p %frombits\nOpStore %p %zero\n")
        self.assertEqual(r["final_writer_categories_possible"], ["float32_constant"])

    def test_branch_without_write_preserves_uninitialized(self):
        body = ("%p = OpAccessChain %ptrf %local %two\n"
                "OpBranchConditional %condition %yes %no\n"
                "%yes = OpLabel\nOpStore %p %frombits\nOpBranch %join\n"
                "%no = OpLabel\nOpBranch %join\n%join = OpLabel\n")
        self.assertTrue(audit(body)["uninitialized_final_path_possible"])

    def test_dynamic_index_unknown(self):
        r = audit("%ip = OpVariable %ptri Function\n%iindex = OpLoad %i %ip\n"
                  "%p = OpAccessChain %ptrf %local %iindex\nOpStore %p %zero\n")
        self.assertTrue(r["unknown_final_writer_path_possible"])

    def test_other_component_does_not_hide_y_writer(self):
        r = audit("%p = OpAccessChain %ptrf %local %two\n"
                  "%x = OpAccessChain %ptrf %local %zero_i\n"
                  "OpStore %p %frombits\nOpStore %x %zero\n")
        self.assertEqual(r["final_writer_categories_possible"], ["sint32_bits_to_float32"])

    def test_immediate_constant_coordinate_is_explicit_boundary(self):
        tail = TAIL.replace("%third = OpBitcast %v2i %swizzle",
                            "%third = OpCompositeConstruct %v2i %one_i %zero_i")
        r = audit(tail=tail)
        self.assertEqual(r["value_origin_boundary"], "constant")
        self.assertFalse(r["last_writer_evidence_available"])

    def test_wrong_descriptor_binding_rejected(self):
        with self.assertRaises(ValueError):
            audit(head=HEAD.replace("OpDecorate %butter Binding 1",
                                    "OpDecorate %butter Binding 3"))

    def test_missing_or_extra_fetch_rejected(self):
        with self.assertRaises(ValueError):
            audit(tail=TAIL.replace("%fetch2 = OpImageFetch %v2f %butter %third\n", ""))
        with self.assertRaises(ValueError):
            audit(tail=TAIL.replace("OpReturn", "%fetch3 = OpImageFetch %v2f %butter %third\nOpReturn"))

    def test_unknown_cfg_target_rejected(self):
        with self.assertRaises(ValueError):
            audit("OpBranch %absent\n%orphan = OpLabel\n")

    def test_source_private_ids_not_reported(self):
        r = audit("%p = OpAccessChain %ptrf %local %two\nOpStore %p %frombits\n")
        self.assertNotIn("%", str(r))
        self.assertFalse(r["original_private_ids_exported"])
        self.assertFalse(r["android_water_proven"])
        self.assertFalse(r["integer_numeric_semantics_proven"])

    def test_pointer_escape_stays_uncertain(self):
        head = HEAD.replace("%ptri = OpTypePointer Function %i",
                            "%ptri = OpTypePointer Function %i\n%ptrptr = OpTypePointer Function %ptr")
        r = audit("%pvar = OpVariable %ptrptr Function\nOpStore %pvar %local\n"
                  "%p = OpAccessChain %ptrf %local %two\nOpStore %p %frombits\n",
                  head=head)
        self.assertTrue(r["pointer_escape_seen_on_any_cfg_path"])

if __name__ == "__main__":
    unittest.main()
