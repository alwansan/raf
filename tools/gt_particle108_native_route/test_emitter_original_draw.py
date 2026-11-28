import unittest
import numpy as np
from tools.gt_particle108_native_route.emitter_original_draw import classify,SIZE,BACKGROUNDS,MARKER
class ActualDraw(unittest.TestCase):
    def rows(self):
        base=np.tile(BACKGROUNDS[0],(SIZE,SIZE,1))
        rows={k:base.copy() for k in ("clear","native","repeat","marker")}
        rows["marker"][10:14,10:14]=MARKER
        for k in ("native","repeat"):rows[k][10:14,10:14,:3]=(.4,.2,.1)
        return rows
    def test_calibrated_original_visible(self):
        r=classify(self.rows(),0)
        self.assertTrue(r["calibrated_original_rgb_observed"])
        self.assertEqual(r["native_visible_pixels"],16)
    def test_empty_marker_or_native_rejected(self):
        r=self.rows();r["native"]=r["clear"].copy()
        self.assertFalse(classify(r,0)["calibrated_original_rgb_observed"])
        r=self.rows();r["marker"]=r["clear"].copy()
        self.assertFalse(classify(r,0)["calibrated_original_rgb_observed"])
    def test_repeat_and_alpha_mask(self):
        r=self.rows();r["repeat"][10,10,0]=.9
        self.assertFalse(classify(r,0)["calibrated_original_rgb_observed"])
        r=self.rows();r["native"][10,10,3]=1
        self.assertFalse(classify(r,0)["calibrated_original_rgb_observed"])
    def test_marker_overlap_required(self):
        r=self.rows();r["marker"]=r["clear"].copy();r["marker"][20:24,20:24]=MARKER
        self.assertFalse(classify(r,0)["calibrated_original_rgb_observed"])
if __name__=="__main__":unittest.main()
