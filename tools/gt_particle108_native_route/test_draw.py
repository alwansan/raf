import unittest
import numpy as np
from tools.gt_particle108_native_route import draw
class DrawTests(unittest.TestCase):
    def make_rows(self):
        base=np.zeros((2,2,4),np.float32);base[...,3]=.25
        rows={k:base.copy() for k in draw.CASES}
        rows["dummy"][...]=np.array([.91,.07,.61,1.],dtype=np.float32)
        for k in ("renderer_native","native","repeat","source_block","clone"):rows[k][...,:3]=.4
        rows["one"][...,:3]=.8
        return rows
    def test_rgb_alpha_effect_controls_and_mask(self):
        rows=self.make_rows();r=draw.summarize(rows)
        self.assertEqual(r["zero_vs_one"],4);self.assertEqual(r["native_vs_exact_clone"],0)
        self.assertTrue(r["source_alpha_channel_mask_preserved"])
        self.assertEqual(draw.classify_draw(r),"CALIBRATED_SOURCE_ROUTE_ALPHA_EFFECT")
        rows["clone"][0,0,0]=.2
        self.assertEqual(draw.classify_draw(draw.summarize(rows)),"EXACT_GPU_CLONE_OVERRIDE_CHANGED_DRAW")
        rows["one"][0,0,3]=1
        self.assertFalse(draw.summarize(rows)["source_alpha_channel_mask_preserved"])
        rows["one"][0,0,0]=np.nan
        with self.assertRaises(ValueError):draw.summarize(rows)
    def test_source_block_and_renderer_are_separate_gates(self):
        rows=self.make_rows();rows["source_block"][0,0,0]=.1
        self.assertEqual(draw.classify_draw(draw.summarize(rows)),"SAME_NATIVE_TEXTURE_PROPERTY_BLOCK_CHANGED_DRAW")
        rows=self.make_rows();rows["renderer_native"][0,0,0]=.1
        self.assertEqual(draw.classify_draw(draw.summarize(rows)),"ISOLATED_COMMAND_ALPHA_EFFECT_RENDERER_BASELINE_DIFFERS")
        rows=self.make_rows();rows["dummy"]=rows["clear"].copy()
        self.assertEqual(draw.classify_draw(draw.summarize(rows)),"COMMAND_DRAW_CONTROL_UNCALIBRATED")
    def test_alpha_observation_without_dummy_never_passes_strict_gate(self):
        rows=self.make_rows();rows["dummy"]=rows["clear"].copy()
        r=draw.summarize(rows)
        self.assertTrue(draw.alpha_effect_without_dummy(r))
        self.assertEqual(draw.classify_draw(r),"COMMAND_DRAW_CONTROL_UNCALIBRATED")
        r["dummy_direct_marker_pixels"]=4
        self.assertEqual(draw.classify_draw(r),"DUMMY_CAMERA_EVENT_UNCALIBRATED")
        rows["clone"][0,0,0]=.1
        self.assertFalse(draw.alpha_effect_without_dummy(draw.summarize(rows)))
        self.assertEqual(draw.dummy_marker(self.make_rows()["dummy"]),4)
        self.assertEqual(draw.dummy_marker(rows["clear"]),0)
    def test_independent_clone_gpu_probe_requires_rgb_and_alpha(self):
        exact=np.full((2,2,4),.5,dtype=np.float32)
        zero=exact.copy();zero[...,3]=0
        one=exact.copy();one[...,3]=1
        rows=dict(native=exact.copy(),clone=exact,zero=zero,one=one)
        r=draw.summarize_probe(rows);self.assertTrue(draw.probe_pass(r))
        rows["zero"][0,0,0]=0
        self.assertFalse(draw.probe_pass(draw.summarize_probe(rows)))
        rows["zero"][0,0,0]=.5;rows["native"][0,0,3]=.8
        self.assertFalse(draw.probe_pass(draw.summarize_probe(rows)))
if __name__=="__main__":unittest.main()
