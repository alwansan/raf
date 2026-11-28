import unittest
from tools.gt_top_resource_closure import selected_source_abi as a

class SelectedSourceABITests(unittest.TestCase):
    def test_source_channel_availability_distinguishes_absence_and_lanes(self):
        def row(name,index,mask):
            return dict(semantic=name,index=index,mask=mask,system_value=0)
        channels=[dict(dimension=x) for x in [3,0,4,4,2]]
        result=a.vertex_channel_observation([row("POSITION",0,7),row("NORMAL",0,7),
            row("TEXCOORD",0,7),row("UNKNOWN",0,1)],channels)
        self.assertEqual(result["present_channels"],2)
        self.assertEqual(result["absent_channels"],1)
        self.assertEqual(result["fewer_declared_lanes"],1)
        self.assertEqual(result["unsupported_semantics"],1)
    def test_selected_array_type_and_sampler_distinguish_wrong_and_unused(self):
        rows=[{"source_texture_sampler_bindings":[
            {"kind":"t","slot":0,"source_texture_name":"_Array"},
            {"kind":"s","slot":0,"source_texture_name":"_Array"}]}]
        src="Texture2DArray<float4> t0 : register(t0, space0); SamplerState s0 : register(s1);"
        good=a.resource_observation(rows,[src],{"_Array":1},{"_Array":187},"_Array")
        self.assertEqual(good["selected_array_type_matches"],1)
        self.assertEqual(good["selected_array_sampler_declarations"],1)
        wrong=a.resource_observation(rows,[src.replace("Texture2DArray","Texture2D")],
            {"_Array":1},{"_Array":187},"_Array")
        self.assertEqual(wrong["selected_array_type_mismatches"],1)
        unused=a.resource_observation(rows,[src],{"_Array":1},{"_Array":187},"_Other")
        self.assertFalse(unused["selected_array_used_by_this_explicit_route"])
        with self.assertRaises(ValueError):
            a.resource_observation(rows,[src.replace("SamplerState s0","SamplerState s2")],
                {"_Array":1},{"_Array":187},"_Array")
if __name__=="__main__":
    unittest.main()
