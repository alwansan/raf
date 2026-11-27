import unittest
from tools.gt_next23b_retained_route_markers.trace import output_expression,expected_marker
# Deliberately tiny authored SPIR-V assembly shapes. Real decoded modules
# are validated independently in the replay workflow.
VS="""OpEntryPoint Vertex %main "main" %input %output
OpDecorate %input Location 0
OpDecorate %output BuiltIn Position
%void = OpTypeVoid
%fn = OpTypeFunction %void
%f = OpTypeFloat 32
%v = OpTypeVector %f 4
%i = OpTypeInt 32 0
%zero = OpConstant %i 0
%marker = OpConstant %f 0.000244140625
%pin = OpTypePointer Input %v
%pout = OpTypePointer Output %v
%input = OpVariable %pin Input
%output = OpVariable %pout Output
%main = OpFunction %void None %fn
%label = OpLabel
%p = OpLoad %v %input
%x = OpCompositeExtract %f %p 0
%add = OpFAdd %f %x %marker
%v2 = OpCompositeInsert %v %add %p 0
OpStore %output %v2
OpReturn
OpFunctionEnd
"""
FS="""OpEntryPoint Fragment %main "main" %output
OpDecorate %output Location 0
%void = OpTypeVoid
%fn = OpTypeFunction %void
%f = OpTypeFloat 32
%v = OpTypeVector %f 4
%r = OpConstant %f 0.0009765625
%p = OpConstant %f 0.25
%one = OpConstant %f 1
%color = OpConstantComposite %v %r %p %p %one
%ptr = OpTypePointer Output %v
%output = OpVariable %ptr Output
%main = OpFunction %void None %fn
%label = OpLabel
OpStore %output %color
OpReturn
OpFunctionEnd
"""
class Trace(unittest.TestCase):
    def test_vertex(self):self.assertEqual(output_expression(VS,0),expected_marker(0,0,0))
    def test_fragment(self):self.assertEqual(output_expression(FS,4),expected_marker(4,1,0))
    def test_unused_literal_not_proof(self):
        bad=VS.replace("OpStore %output %v2","OpStore %output %p")
        with self.assertRaisesRegex(ValueError,"not_add"):output_expression(bad,0)
    def test_wrong_axis(self):
        with self.assertRaisesRegex(ValueError,"not_add"):output_expression(VS.replace("%add %p 0","%add %p 1"),0)
    def test_wrong_input(self):
        with self.assertRaisesRegex(ValueError,"input_not_preserved"):output_expression(VS.replace("%p 0\n%add","%p 1\n%add"),0)
    def test_fragment_literal_in_wrong_lane(self):
        self.assertNotEqual(output_expression(FS.replace("%r %p %p %one","%p %r %p %one"),4),expected_marker(4,1,0))
    def test_position_member(self):
        bad=VS.replace("OpDecorate %output BuiltIn Position","OpMemberDecorate %s 0 BuiltIn Position").replace("%pout = OpTypePointer Output %v","%s = OpTypeStruct %v\n%pout = OpTypePointer Output %s\n%pvec = OpTypePointer Output %v").replace("OpStore %output %v2","%member = OpAccessChain %pvec %output %zero\nOpStore %member %v2")
        self.assertEqual(output_expression(bad,0),expected_marker(0,0,0))
    def test_multiple_blocks_rejected(self):
        with self.assertRaisesRegex(ValueError,"nonlinear_entrypoint"):output_expression(VS.replace("OpReturn","%other = OpLabel\nOpReturn"),0)
if __name__=="__main__":unittest.main()
