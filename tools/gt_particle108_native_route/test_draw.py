import unittest
import numpy as np
from tools.gt_particle108_native_route import draw
class DrawTests(unittest.TestCase):
    def test_rgb_alpha_effect_controls_and_mask(self):
        base=np.zeros((2,2,4),np.float32);base[...,3]=.25
        rows={k:base.copy() for k in draw.CASES}
        rows["dummy"][...,:3]=.9
        for k in ("native","repeat","clone"):rows[k][...,:3]=.4
        rows["one"][...,:3]=.8
        r=draw.summarize(rows)
        self.assertEqual(r["zero_vs_one"],4)
        self.assertEqual(r["native_vs_exact_clone"],0)
        self.assertTrue(r["source_alpha_channel_mask_preserved"])
        rows["clone"][0,0,0]=.2
        self.assertEqual(draw.summarize(rows)["native_vs_exact_clone"],1)
        rows["one"][0,0,3]=1
        self.assertFalse(draw.summarize(rows)["source_alpha_channel_mask_preserved"])
        rows["one"][0,0,0]=np.nan
        with self.assertRaises(ValueError):draw.summarize(rows)
if __name__=="__main__":unittest.main()
