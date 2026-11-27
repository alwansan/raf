import unittest
from scripts import gt_dxt5nm_texel_policy as p

class TestPolicy(unittest.TestCase):
    def test_one_exact_meta_byte(self):
        b=b"TextureImporter:\n  alphaIsTransparency: 1\n  other: 1\n"
        off,pos=p.policy_byte(b)
        self.assertEqual(off,b.replace(b"alphaIsTransparency: 1",b"alphaIsTransparency: 0"))
        self.assertEqual(off[:pos]+b"1"+off[pos+1:],b)
    def test_reject_missing_and_duplicate(self):
        for b in (b"",b"  alphaIsTransparency: 0\n",b"  alphaIsTransparency: 1\n"*2):
            with self.assertRaises(ValueError):p.policy_byte(b)
    def test_bottom_top_involution(self):
        b=bytes(range(24))
        self.assertEqual(p.flip(p.flip(b,3,2),3,2),b)
        self.assertEqual(p.flip(b,3,2),b[12:]+b[:12])
    def test_repack_not_original_alpha(self):
        self.assertEqual(p.repack(bytes([48,243,127,0])),bytes([255,243,243,48]))
    def test_zero_alpha_classification(self):
        src=bytes([48,243,127,0])+bytes([80,130,245,255])*34
        exp=p.repack(src);actual=bytes([255,130,130,80])+exp[4:]
        d=p.comparison(exp,actual,src)
        self.assertEqual(d["matches"],34)
        self.assertTrue(d["all_mismatches_zero_source_alpha"])
        d=p.comparison(exp,exp[:4]+bytes([0,0,0,0])+exp[8:],src)
        self.assertFalse(d["all_mismatches_zero_source_alpha"])
    def test_unity_not_executed(self):
        with self.assertRaises(ValueError):p.verify({}, {}, {"status":"PREPARED"}, "run", 0)
