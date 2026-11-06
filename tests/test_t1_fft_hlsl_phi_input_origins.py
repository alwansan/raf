import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import sys

import scripts.t1_fft_hlsl_phi_input_origins as phi
from scripts.t1_fft_hlsl_phi_input_origins import analyze


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

END = """
%coordf = OpCompositeConstruct %v2f %phi %f0
%coordi = OpBitcast %v2i %coordf
%fetch0 = OpImageFetch %v2f %source %coordi
%fetch1 = OpImageFetch %v2f %butter %coordi
%fetch2 = OpImageFetch %v2f %butter %coordi
OpReturn
OpFunctionEnd
"""

FLOW = """
OpBranchConditional %condition %left %right
%left = OpLabel
%bits = OpBitcast %float %i1
OpBranch %join
%right = OpLabel
%sum = OpFAdd %float %f0 %f1
OpBranch %join
%join = OpLabel
%phi = OpPhi %float %bits %left %sum %right
"""


def report(flow=FLOW, end=END, head=HEAD):
    return analyze(head + flow + end, original_source_layout=True)


class HlslPhiInputOriginsTests(unittest.TestCase):
    def test_phi_reports_two_typed_sources_without_values(self):
        result = report()
        self.assertEqual(result["status"], "source_safe_phi_incoming_census")
        self.assertEqual(result["phi_result_kind"], "float32_scalar")
        self.assertEqual(result["incoming_count"], 2)
        incoming = result["incoming_sources"]
        self.assertEqual([x["immediate_producer_opcode"] for x in incoming],
                         ["OpBitcast", "OpFAdd"])
        self.assertEqual(incoming[0]["bounded_component_chain"]["cast_kinds"],
                         ["sint32_bits_to_float32"])
        self.assertEqual(incoming[1]["bounded_component_chain"]["status"],
                         "arithmetic_boundary")
        self.assertFalse(result["original_integer_bitcarrier_parity_proven"])
        self.assertNotIn("%", str(result))

    def test_incoming_predecessors_terminators_are_checked(self):
        sources = report()["incoming_sources"]
        self.assertEqual([x["predecessor"]["terminator"] for x in sources],
                         ["OpBranch", "OpBranch"])
        self.assertEqual([x["predecessor"]["edge"] for x in sources],
                         ["unconditional", "unconditional"])

    def test_missing_predecessor_is_rejected(self):
        with self.assertRaises(ValueError):
            report(FLOW.replace("%bits %left", "%bits %no_block"))

    def test_predecessor_not_connected_to_phi_block_rejected(self):
        flow = FLOW.replace("OpBranch %join\n%right", "OpBranch %other\n%right")
        flow = flow.replace("%join = OpLabel", "%other = OpLabel\nOpReturn\n%join = OpLabel")
        with self.assertRaises(ValueError):
            report(flow)

    def test_wrong_original_descriptor_identity_rejected(self):
        with self.assertRaises(ValueError):
            report(head=HEAD.replace("OpDecorate %butter Binding 1",
                                     "OpDecorate %butter Binding 5"))

    def test_actual_coordinate_x_without_phi_does_not_claim_provenance(self):
        end = END.replace("%phi %f0", "%f0 %phi")
        result = report(end=end)
        self.assertEqual(result["status"], "other_boundary")
        self.assertFalse(result["runtime_branch_truth_proven"])

    def test_phi_incoming_must_have_matching_numeric_type(self):
        flow = FLOW.replace("%bits %left", "%i1 %left")
        with self.assertRaises(ValueError):
            report(flow)

    def test_phi_malformed_odd_number_of_incoming_operands_rejected(self):
        flow = FLOW.replace("%sum %right", "%sum")
        with self.assertRaises(ValueError):
            report(flow)

    def test_phi_may_have_true_false_predecessor_sides(self):
        flow = """
OpBranch %first
%first = OpLabel
%bits = OpBitcast %float %i1
OpBranchConditional %condition %join %second
%second = OpLabel
%sum = OpFAdd %float %f0 %f1
OpBranch %join
%join = OpLabel
%phi = OpPhi %float %bits %first %sum %second
"""
        sources = report(flow)["incoming_sources"]
        self.assertEqual(sources[0]["predecessor"]["terminator"],
                         "OpBranchConditional")
        self.assertEqual(sources[0]["predecessor"]["edge"], "true")
        self.assertEqual(sources[0]["predecessor"]["predicate_opcode"],
                         "OpConstantTrue")

    def test_allowlisted_unknown_producer_is_not_printed(self):
        flow = FLOW.replace("%sum = OpFAdd %float %f0 %f1",
                            "%sum = OpPrivateSecret %float %f0 %f1")
        result = report(flow)
        self.assertEqual(result["incoming_sources"][1]["immediate_producer_opcode"],
                         "other_opcode")
        self.assertNotIn("OpPrivateSecret", str(result))

    def test_component_trace_stops_on_float_constant(self):
        flow = FLOW.replace("%bits = OpBitcast %float %i1",
                            "%bits = OpCopyObject %float %f1")
        result = report(flow)
        self.assertEqual(result["incoming_sources"][0]["bounded_component_chain"]["status"],
                         "constant_boundary")

    def test_beyond_supported_phi_inputs_fails_closed(self):
        # 13 same-predecessor pairs is malformed SPIR-V but still must
        # hit the source-budget guard before constructing an unbounded report.
        more = " ".join(["%bits %left"] * 13)
        flow = FLOW.replace("%bits %left %sum %right", more)
        with self.assertRaises(ValueError):
            report(flow)

    def test_resolved_lane_does_not_leak_raw_ssa_or_constant(self):
        result = report()
        self.assertFalse(result["private_values_exported"])
        self.assertNotIn("%", str(result))
        self.assertNotIn("predecessor_id", str(result))


    def test_private_error_diagnostic_does_not_leak_unknown_exception(self):
        with tempfile.TemporaryDirectory() as d:
            blob = Path(d) / "fake.spv"
            blob.write_bytes(b"x" * 32)
            out = StringIO()
            with patch.object(sys, "argv", ["phi_probe", str(blob)]), \
                 patch.object(phi.subprocess, "run", return_value=SimpleNamespace(stdout="fixture")), \
                 patch.object(phi, "analyze", side_effect=ValueError("secret_%privateID=42")), \
                 redirect_stdout(out), self.assertRaises(SystemExit) as caught:
                phi.main()
        self.assertEqual(caught.exception.code, 2)
        self.assertIn('"reason": "unclassified_validation"', out.getvalue())
        self.assertNotIn("secret_", out.getvalue())

    def test_allowlisted_failure_reason_is_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            blob = Path(d) / "fake.spv"
            blob.write_bytes(b"x" * 32)
            out = StringIO()
            with patch.object(sys, "argv", ["phi_probe", str(blob)]), \
                 patch.object(phi.subprocess, "run", return_value=SimpleNamespace(stdout="fixture")), \
                 patch.object(phi, "analyze", side_effect=ValueError("Phi predecessor is not a CFG incoming block")), \
                 redirect_stdout(out), self.assertRaises(SystemExit):
                phi.main()
        self.assertIn('"reason": "Phi predecessor is not a CFG incoming block"', out.getvalue())
        self.assertNotIn("%", out.getvalue())


if __name__ == "__main__":
    unittest.main()
