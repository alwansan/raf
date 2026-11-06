"""Source-free SPIR-V controls for CFG-backedge vs actual SSA self-data path."""
import io
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch
from scripts.t1_fft_site2_y_phi_recurrence import analyze, main

HEADER = """OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%f = OpTypeFloat 32
%i = OpTypeInt 32 1
%boolean = OpTypeBool
%v2f = OpTypeVector %f 2
%v2i = OpTypeVector %i 2
%v4f = OpTypeVector %f 4
%ptri = OpTypePointer Function %i
%zero = OpConstant %f 0
%one = OpConstant %f 1
%one_i = OpConstant %i 1
%base = OpCompositeConstruct %v4f %zero %one %zero %one
%simple = OpCompositeConstruct %v2f %one %zero
%othercoords = OpBitcast %v2i %simple
%condition = OpIEqual %boolean %one_i %one_i
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

def check(body=BODY, head=HEADER, tail=TAIL):
    return analyze(head + body + tail, require_original=True)


class ThirdButterflyYPhiSSA(unittest.TestCase):
    def test_recurring_selected_lane_is_real_static_ssa_dependency(self):
        r = check()
        self.assertEqual(r["incoming_count"], 2)
        self.assertFalse(r["inputs"][0]["predecessor_on_structural_backedge"])
        self.assertTrue(r["inputs"][1]["predecessor_on_structural_backedge"])
        self.assertFalse(r["inputs"][0]["same_selected_phi_component_data_edge_possible"])
        self.assertTrue(r["inputs"][1]["same_selected_phi_component_data_edge_possible"])
        self.assertEqual(r["inputs"][1]["recurrence_class"], "selected_component_cycle")
        self.assertFalse(r["selected_runtime_branch_proven"])

    def test_backedge_without_selected_data_recurrence_is_distinguished(self):
        body = BODY.replace("%int = OpBitcast %i %lane",
                            "%int = OpCopyObject %i %one_i")
        r = check(body)
        self.assertTrue(r["inputs"][1]["predecessor_on_structural_backedge"])
        self.assertFalse(r["inputs"][1]["same_selected_phi_component_data_edge_possible"])
        self.assertEqual(r["inputs"][1]["recurrence_class"],
                         "no_direct_selected_component_cycle_in_supported_SSA")

    def test_cross_component_dependency_not_claimed_as_selected_component(self):
        body = BODY.replace("%lane = OpCompositeExtract %f %phi 2",
                            "%lane = OpCompositeExtract %f %phi 0")
        r = check(body)
        self.assertFalse(r["inputs"][1]["same_selected_phi_component_data_edge_possible"])
        self.assertTrue(r["inputs"][1]["different_phi_component_data_edge_possible"])
        self.assertEqual(r["inputs"][1]["recurrence_class"], "cross_component_only")

    def test_function_load_makes_absence_undecidable(self):
        body = BODY.replace("%int = OpBitcast %i %lane",
                            "%ptr = OpVariable %ptri Function\n%int = OpLoad %i %ptr")
        r = check(body)
        self.assertTrue(r["inputs"][1]["unknown_dataflow_possible"])
        self.assertEqual(r["inputs"][1]["recurrence_class"], "unresolved")
        self.assertIn("load", r["inputs"][1]["uncertainty_categories"])

    def test_unsupported_opcode_fails_to_unknown_not_no_recurrence(self):
        body = BODY.replace("%int = OpBitcast %i %lane",
                            "%int = OpFoo %i %lane")
        r = check(body)
        self.assertTrue(r["inputs"][1]["unknown_dataflow_possible"])
        self.assertIn("unknown_opcode", r["inputs"][1]["uncertainty_categories"])

    def test_bad_type_or_routing_is_not_proven_independent(self):
        body = BODY.replace("%int = OpBitcast %i %lane",
                            "%int = OpCompositeExtract %i %base 4")
        r = check(body)
        self.assertTrue(r["inputs"][1]["unknown_dataflow_possible"])

    def test_duplicate_pred_and_bad_binding_rejected(self):
        with self.assertRaises(ValueError):
            check(head=HEADER.replace("OpDecorate %butter Binding 1",
                                      "OpDecorate %butter Binding 7"))
        with self.assertRaises(ValueError):
            check(head=HEADER.replace("%update %body", "%update %entry"))

    def test_missing_third_imagefetch_rejected(self):
        with self.assertRaises(ValueError):
            check(tail=TAIL.replace("%fetch2 = OpImageFetch %v2f %butter %coordinate\n", ""))

    def test_private_ssa_ids_and_constants_not_emitted(self):
        r = check()
        self.assertNotIn("%", str(r))
        self.assertNotIn("%one_i", str(r))
        self.assertFalse(r["private_shader_SSA_constants_or_pixels_exported"])
        self.assertFalse(r["original_or_unity_numeric_parity_proven"])
        self.assertFalse(r["android_water_proven"])

    def test_bounded_cycle_does_not_hang(self):
        # Other SSA cycle not equal to selected Phi is unknowable, never safe.
        body = BODY.replace("%int = OpBitcast %i %lane",
                            "%int = OpCopyObject %i %another\n%another = OpCopyObject %i %int")
        r = check(body)
        self.assertTrue(r["inputs"][1]["unknown_dataflow_possible"])
        self.assertIn("other_cycle", r["inputs"][1]["uncertainty_categories"])

    def test_private_cli_error_redacts_source(self):
        stream = io.StringIO()
        with (patch("sys.argv", ["phi", "/private/SECRET.spv"]),
              redirect_stderr(stream)):
            with self.assertRaises(SystemExit) as err:
                main()
        self.assertEqual(err.exception.code, 2)
        self.assertNotIn("SECRET", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
