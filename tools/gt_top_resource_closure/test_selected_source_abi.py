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
    def test_texture_plan_nonnull_only_retains_two_explicit_null_slots(self):
        uv=((1.0,1.0),(0.0,0.0))
        before={f"_T{i}":((0,100+i),uv) for i in range(4)}
        before.update({"_NullA":((0,0),uv),"_NullB":((0,0),uv)})
        after={key:((18700000 if i==0 else 2800000,"1"*32,3),uv)
               if ptr[1] else ((0,"0"*32,0),uv)
               for i,(key,(ptr,_)) in enumerate(before.items())}
        planned={key:{"stream_ready":True} for key,(ptr,_) in before.items() if ptr[1]}
        self.assertEqual(a.verify_texture_plan(before,after,planned),
            {"source_slots":6,"export_slots":6,"nonnull_planned":4,"null_source_slots":2})
        with self.assertRaisesRegex(ValueError,"selected_nonnull_texture_plan_drift"):
            a.verify_texture_plan(before,after,{**planned,"_NullA":{"stream_ready":True}})
        with self.assertRaisesRegex(ValueError,"selected_nonnull_texture_plan_drift"):
            a.verify_texture_plan(before,after,{k:v for k,v in planned.items() if k!="_T0"})
        with self.assertRaisesRegex(ValueError,"selected_texenv_names_drift"):
            a.verify_texture_plan(before,{k:v for k,v in after.items() if k!="_NullB"},planned)
        with self.assertRaisesRegex(ValueError,"selected_texture_plan_not_prepared"):
            a.verify_texture_plan(before,after,{**planned,"_T0":{"stream_ready":False}})

if __name__=="__main__":
    unittest.main()
