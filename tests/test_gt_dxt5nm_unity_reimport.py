"""V13 independent source-only oracle checks; never substitute for Unity."""
import unittest
from scripts import gt_dxt5nm_unity_reimport as v13

class OracleTests(unittest.TestCase):
    def test_dxt5nm(self):
        self.assertEqual(v13.normal_oracle((1,.5,.2,.5),0),(0,0,1))
    def test_RG_or_DXT5nm_packing(self):
        self.assertEqual(v13.normal_oracle((.5,.5,.9,1),0),(0,0,1))
        self.assertEqual(v13.normal_oracle((1,.5,.9,.5),0),(0,0,1))
    def test_clamp(self):
        self.assertEqual(v13.normal_oracle((1,1,0,1),0),(1,1,0))
    def test_no_DXT5nm_branch(self):
        self.assertEqual(v13.normal_oracle((.5,.75,0,1),1),(0,.5,-1))
    def test_exact_asset_identity(self):
        d=dict(path="Assets/x.png",guid="a"*32,file_id=2800000,sha256="b"*64,meta_sha256="c"*64)
        self.assertTrue(v13.identity(d,d))
        for k,v in (("guid","d"*32),("file_id",1),("sha256","d"*64),("path","Assets/y.png")):
            with self.subTest(k=k):
                with self.assertRaises(ValueError):v13.identity(dict(d,**{k:v}),d)
        self.assertFalse(v13.identity(dict(d,meta_sha256="d"*64),d))
    def test_invalid_vectors(self):
        for v in ([0,0],[float("nan"),0,0,0],[False,0,0,0]):
            with self.assertRaises(ValueError):v13.float_vec(v,4)
    def test_fake_editor_cannot_pass(self):
        with self.assertRaises(ValueError):v13.verify({},dict(status="PREPARED"),"run",0)
    def test_failed_editor_cannot_pass(self):
        with self.assertRaises(ValueError):v13.verify({},dict(status="OBSERVED_AUTHORED_UNITY_REIMPORT"),"run",1)
