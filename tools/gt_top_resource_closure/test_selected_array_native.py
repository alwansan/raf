import unittest
import numpy as np
from tools.gt_top_resource_closure import selected_array_native as n

class NativeArrayTests(unittest.TestCase):
    def test_ranges_cover_all_22_without_padding_or_overlap(self):
        rr=list(n.ranges(1024,1024,2,11))
        self.assertEqual(len(rr),22)
        self.assertEqual(rr[-1][2]+rr[-1][3],2796256)
        self.assertEqual(rr[10][3],16)
        self.assertEqual(rr[11][2],1398128)
    def test_authored_all_mips_and_controls(self):
        cal=n.cal_payload()
        expected=n.decoded(cal,8,8,2,4)
        self.assertEqual(len(cal),224)
        self.assertEqual(n.calibrate(expected,expected),"raw_first")
        self.assertEqual(n.calibrate([x[:,::-1] for x in expected],expected),"flipped")
        with self.assertRaises(n.old.Failure):
            n.calibrate([x[::-1] for x in expected],expected)
        wrong=[x.copy() for x in expected]
        wrong[1]=wrong[0][:,::2,::2].copy()
        with self.assertRaises(n.old.Failure):n.calibrate(wrong,expected)
    def test_compare_preserves_alpha_error_and_wrong_layer(self):
        e=n.decoded(n.cal_payload(),8,8,2,4)
        a=[x.copy() for x in e]
        a[0][0,0,0,3]=1-a[0][0,0,0,3]
        rows=n.summarize(a,e,"raw_first")
        self.assertEqual(rows[0]["per_layer"][0]["alpha_mismatches_over_1e_5"],1)
        self.assertGreater(rows[0]["reversed_layer_control"][0]["RGBA_mismatches_over_1_div_255"],0)
if __name__=="__main__": unittest.main()
