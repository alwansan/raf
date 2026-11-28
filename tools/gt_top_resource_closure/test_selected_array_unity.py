import unittest
import numpy as np
from tools.gt_top_resource_closure import selected_array_unity as u

class SelectedArrayUnityTests(unittest.TestCase):
    def test_calibration_fixed_orientation_and_wrong_layer(self):
        expected=u.calibration_expected()
        self.assertEqual(u.calibrate(expected),"bottom_first")
        self.assertEqual(u.calibrate(expected[:,::-1]),"top_first")
        with self.assertRaises(u.Failure):u.calibrate(expected[::-1])
        with self.assertRaises(u.Failure):u.calibrate(np.zeros_like(expected))
    def test_srgb_only_RGB_and_alpha_unchanged(self):
        p=np.array([[[[0,128,255,128]]]],dtype=np.uint8)
        q=u.expected_linear(p)
        self.assertAlmostEqual(float(q[0,0,0,1]),0.2158605,places=6)
        self.assertAlmostEqual(float(q[0,0,0,3]),128/255,places=6)
        self.assertEqual(float(q[0,0,0,2]),1)
    def test_pixel_comparison_controls(self):
        expected=u.calibration_expected()
        self.assertTrue(all(x["RGBA_mismatches_over_2_div_255"]==0 for x in u.compare(expected,expected)))
        self.assertTrue(all(x["RGBA_mismatches_over_2_div_255"]==16 for x in u.compare(expected[::-1],expected)))
        wrong=expected.copy();wrong[0,0,0,3]=0
        self.assertEqual(u.compare(wrong,expected)[0]["alpha_mismatches_over_1e_5"],1)
        wrong[0,0,0,0]=np.nan
        with self.assertRaises(u.Failure):u.compare(wrong,expected)
if __name__=="__main__":unittest.main()
