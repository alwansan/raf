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
    def test_partial_raw_matches_and_fail_closed_extent(self):
        raw=n.cal_payload()
        self.assertEqual(n.raw_matches(raw,raw,8,8,2,4),8)
        changed=bytearray(raw);changed[0]^=1
        self.assertEqual(n.raw_matches(raw,bytes(changed),8,8,2,4),7)
        with self.assertRaises(n.old.Failure):
            n.raw_matches(raw,raw[:-1],8,8,2,4)
    def test_safe_transfer_does_not_disclose_names_or_accept_truthy_values(self):
        record=n.safe_transfer({"phase":"private-name","failure_category":"private-path","accepted":1,"loaded_array":True,"guid":"secret"})
        self.assertEqual(record["phase"],"unknown")
        self.assertEqual(record["failure_category"],"other")
        self.assertIs(record["accepted"],False)
        self.assertIs(record["loaded_array"],True)
        self.assertNotIn("guid",record)
if __name__=="__main__": unittest.main()
