import unittest
import numpy as np
from tools.gt_top_resource_closure import selected_original_draw as d

class SelectedOriginalDrawTests(unittest.TestCase):
    def test_pixel_controls_do_not_accept_blank_or_identical_reference(self):
        clear=np.zeros((3,3,4),dtype=np.float32)
        dummy=np.ones_like(clear)
        fixed=clear.copy();fixed[1,1]=.5
        rows=dict(clear=clear,dummy=dummy,type3=clear,type2=fixed,type2_repeat=fixed,wrong_guid=clear,wrong_fileid=clear)
        result=d.pixel_summary(rows)
        self.assertEqual(result["dummy_vs_clear"],9)
        self.assertEqual(result["type2_vs_clear"],1)
        self.assertEqual(result["type2_vs_wrong_guid"],1)
        self.assertEqual(result["type2_repeat_difference"],0)
        self.assertEqual(d.pixel_summary(dict(rows,wrong_guid=fixed))["type2_vs_wrong_guid"],0)
        self.assertEqual(d.pixel_summary(dict(rows,type2=clear))["type2_vs_clear"],0)
        with self.assertRaises(ValueError):d.pixel_summary(dict(rows,type2=np.full_like(clear,np.nan)))
    def test_source_material_controls_retain_original_shader(self):
        g="1"*32;s="2"*32;w="3"*32
        body=("\nMaterial:\n  m_Shader: {fileID: 4800000, guid: "+s+", type: 3}\n  m_SavedProperties:\n    m_TexEnvs:\n    - _Array:\n        m_Texture: {fileID: 18700000, guid: "+g+", type: 3}\n        m_Scale: {x: 1, y: 1}\n        m_Offset: {x: 0, y: 0}\n")
        rows=d.variants(body,"_Array",g,18700000,3,w)
        self.assertEqual(rows["type3"],body)
        self.assertEqual(sum(x!=y for x,y in zip(rows["type2"],body)),1)
        self.assertIn("guid: "+s+", type: 3",rows["wrong_guid"])
        self.assertIn("guid: "+w+", type: 2",rows["wrong_guid"])
        self.assertIn("fileID: 18700001",rows["wrong_fileid"])

    def test_tap_instrumentation_preserves_sample_arguments_and_original_return(self):
        from tools.gt_top_resource_closure import selected_array_causal as c
        source="""HLSLPROGRAM
#pragma vertex gt_vs_main
#pragma fragment gt_fs_main
Texture2DArray<float4> _Array;
SamplerState sampler_Array;
struct gt_fs_Out { float4 color : SV_Target0; };
void helper() { float4 v=_Array.Sample(sampler_Array,float3(1,2,0)); }
// _Array.Sample(sampler_Array, xyz) is only a comment
gt_fs_Out gt_fs_main(float3 uv) {
  helper();
  gt_fs_Out result;
  result.color=_Array.SampleLevel(sampler_Array,uv,0);
  return result;
}
ENDHLSL"""
        tap,n=c.instrument(source,"_Array")
        self.assertEqual(n,2)
        self.assertIn("GTSelectedTapCapture(_Array.Sample(sampler_Array,float3(1,2,0)))",tap)
        self.assertIn("GTSelectedTapCapture(_Array.SampleLevel(sampler_Array,uv,0))",tap)
        self.assertIn("// _Array.Sample(sampler_Array, xyz) is only a comment",tap)
        self.assertIn("result.color=("+c.MODE,tap)
        self.assertIn("return result;",tap)
        self.assertIn("gt_selected_tap_hit=0.0",tap)
        with self.assertRaises(ValueError):c.instrument(source.replace("return result;","return result; return result;"),"_Array")
        with self.assertRaises(ValueError):c.instrument(source.replace(".SampleLevel",".GetDimensions"),"_Array")
    def test_causal_calibration_and_insensitivity_are_separate_from_original_repair(self):
        from tools.gt_top_resource_closure import selected_array_causal as c
        def fill(color):return np.broadcast_to(np.asarray(color,dtype=np.float32),(2,2,4)).copy()
        base=fill([0,0,0,1])
        rows={k:base.copy() for k in c.BASE_CASES}
        rows.update(tap_cal=fill(c.CAL),tap_hit_source=fill(c.HIT),tap_hit_red=fill(c.HIT),
                    tap_hit_green=fill(c.HIT),tap_source=fill(c.RED),tap_red=fill(c.RED),tap_green=fill(c.GREEN))
        result=c.summarize(rows,base,True)
        self.assertTrue(result["tap_calibrated"])
        self.assertEqual(c.classify([result])["status"],"INSTRUMENTED_SAMPLE_CALIBRATED_FINAL_CANDIDATE_INSENSITIVE_IN_TEST_SCENE")
        wrong=c.summarize(dict(rows,tap_green=fill(c.RED)),base,True)
        self.assertFalse(wrong["tap_calibrated"])
        self.assertEqual(c.classify([wrong])["status"],"INCONCLUSIVE_SAMPLE_CAUSALITY")
        responsive=c.summarize(dict(rows,override_green=fill(c.GREEN)),base,True)
        self.assertEqual(c.classify([responsive])["status"],"ORIGINAL_CANDIDATE_RESPONDS_TO_AUTHORED_ARRAY_SUBSTITUTION")
        drift=c.summarize(dict(rows,override_source=fill(c.GREEN)),base,True)
        self.assertEqual(c.classify([drift])["status"],"INCONCLUSIVE_SAMPLE_CAUSALITY")

    def test_tap_import_success_is_not_capture_admission(self):
        cfg={"tap_available":True,"tap_expected_properties":35}
        r=dict(tap_imported=True,tap_shader_supported=True,tap_shader_compiled=True,tap_materials_ready=True,
               tap_phase="capture_complete",tap_failure_category="",tap_shader_errors=0,tap_shader_passes=1,
               tap_copied_properties_source=35,tap_copied_properties_red=35,tap_copied_properties_green=35,causal_tap_views=3)
        self.assertTrue(d.tap_observation(cfg,r)["tap_capture_admitted"])
        for changed in (dict(tap_materials_ready=False,tap_phase="typed_green_clone",tap_failure_category="InvalidOperationException"),
                        dict(tap_copied_properties_red=34),dict(tap_shader_errors=1),dict(causal_tap_views=2),
                        dict(tap_phase="unexpected_raw_value"),dict(tap_failure_category="private unexpected text")):
            self.assertFalse(d.tap_observation(cfg,dict(r,**changed))["tap_capture_admitted"])
        self.assertEqual(d.tap_observation(cfg,dict(r,tap_failure_category="private unexpected text"))["tap_failure_category"],"other")
        self.assertFalse(d.tap_observation(dict(cfg,tap_available=False),r)["tap_capture_admitted"])

if __name__=="__main__":unittest.main()
