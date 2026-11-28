import unittest
import numpy as np
from tools.gt_top_resource_closure import selected_stage_provider as p

class ProviderTests(unittest.TestCase):
    def fill(self,v):return np.broadcast_to(np.asarray(v,dtype=np.float32),(2,2,4)).copy()
    def test_independent_calibration_and_cpu_comparison(self):
        cfg={"provider_transport_version":2,"provider_rows":[dict(mode=2,role="vs",kind="camera_position",lanes=3),
                              dict(mode=3,role="fs",kind="unresolved",lanes=1)]}
        receipt={"views":[dict(view=v,expected=[dict(mode=2,known=True,compare_lanes=3,value=[v+1,2,3,0]),
                                                dict(mode=3,known=False)]) for v in range(3)]}
        def read(name):
            _,v,mode=name[:-4].split("-");v=int(v);mode=int(mode)
            if mode==256:return self.fill(p.CLASS_CAL_A)
            if mode==257:return self.fill(p.CLASS_CAL_B)
            if mode>=256:return self.fill([0,0,0,0])
            return self.fill(p.CAL_A if mode==0 else p.CAL_B if mode==1 else [v+1,2,3,0] if mode==2 else [0,0,0,0])
        r=p.summarize(cfg,receipt,read)
        self.assertEqual(r["counts"]["engine_numeric_cpu_matches"],3)
        self.assertEqual(r["counts"]["verified_view_dependent_engine_numeric_rows"],1)
        self.assertEqual(r["counts"]["unknown_provider_observations"],3)
        self.assertFalse(r["runtime_uniform_upload_verified"])
        with self.assertRaises(ValueError):p.summarize(cfg,receipt,lambda name:self.fill(p.CAL_A))
    def test_vertex_stage_is_not_fragment_stage(self):
        h="""HLSLPROGRAM
#pragma vertex gt_vs_main
#pragma fragment gt_fs_main
struct VOut { float4 pos : SV_POSITION; float2 uv : TEXCOORD15; };
struct FIn { float4 pos : SV_POSITION; float2 uv : TEXCOORD15; };
VOut gt_vs_main(float4 v) { VOut o; o.pos=v; return o; }
float4 gt_fs_main(FIn x) : SV_Target { float4 c=0; return c; }
ENDHLSL"""
        rows=[dict(mode=2,role="vs",kind="unresolved",expression="float(_X)",lanes=1),
              dict(mode=3,role="fs",kind="unresolved",expression="float2(_Y)",lanes=2)]
        t=p.instrument(h,rows)
        self.assertIn("nointerpolation float4 gt_provider_value : TEXCOORD14",t)
        self.assertIn("o.gt_provider_value=float4(float(_X)",t)
        self.assertIn("c=x.gt_provider_value",t)
        self.assertIn("c=float4(float2(_Y)",t)
        self.assertIn("gt_provider_class4(asuint(c))",t)
        self.assertIn("fmod(_GTSelectedTapMode,256.0)",t)
        with self.assertRaises(ValueError):p.instrument(h.replace("FIn x","float4 x : SV_POSITION"),rows)
    def test_nonuniform_and_nonfinite_not_accepted(self):
        a=self.fill([1,2,3,0]);mask=np.ones((2,2),dtype=bool)
        self.assertIsNotNone(p.finite_uniform(a,mask,3))
        a[0,0,0]=9;self.assertIsNone(p.finite_uniform(a,mask,3))
        a[0,0,0]=np.nan;self.assertIsNone(p.finite_uniform(a,mask,3))

    def test_nonfinite_transport_is_classified_not_accepted(self):
        mask=np.ones((2,2),dtype=bool)
        a=self.fill([np.nan,np.inf,-np.inf,0])
        encoded=self.fill([.25,.5,.75,0])
        status,stats=p.classify_row(a,encoded,mask,3)
        self.assertEqual(status,"shader_nonfinite")
        self.assertEqual(stats["raw_nan_lanes"],4)
        self.assertEqual(stats["encoded_positive_inf_lanes"],4)
        self.assertEqual(stats["encoded_negative_inf_lanes"],4)
        self.assertEqual(stats["raw_encoded_class_mismatch_lanes"],0)
        status,_=p.classify_row(a,self.fill([0,0,0,0]),mask,3)
        self.assertEqual(status,"transport_mismatch")
        with self.assertRaises(ValueError):p.classify_row(a,self.fill([.1,.5,.75,0]),mask,3)
        with self.assertRaises(ValueError):p.classify_row(a,self.fill([np.nan,.5,.75,0]),mask,3)
    def test_padding_and_background_not_accepted(self):
        mask=np.ones((2,2),dtype=bool)
        a=self.fill([1,2,3,np.inf]);encoded=self.fill([0,0,0,.5])
        self.assertEqual(p.classify_row(a,encoded,mask,3)[0],"invalid_padding")
        mask[0,0]=False
        a=self.fill([1,2,3,0]);a[0,0,0]=np.nan
        self.assertEqual(p.classify_row(a,self.fill([0,0,0,0]),mask,3)[0],"transport_mismatch")
    def test_provider_raw_reader_does_not_relax_draw_gate(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from tools.gt_top_resource_closure import selected_original_draw as draw
        with TemporaryDirectory() as tmp:
            file=Path(tmp)/"raw.f32"
            self.fill([np.nan,0,0,0]).astype("<f4").tofile(file)
            self.assertTrue(np.isnan(draw.read_provider_pixels(file,2)[0,0,0]))
            with self.assertRaisesRegex(ValueError,"draw_readback_nonfinite"):draw.read_pixels(file,2)
            with self.assertRaisesRegex(ValueError,"draw_readback_extent"):draw.read_provider_pixels(file,3)

if __name__=="__main__":unittest.main()
