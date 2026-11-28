import unittest
import numpy as np
from tools.gt_top_resource_closure import selected_array_causal as c, selected_array_basis as b

class BasisTests(unittest.TestCase):
    def fill(self,v):
        return np.broadcast_to(np.asarray(v,dtype=np.float32),(2,2,4)).copy()
    def fixture(self):
        cal={m:self.fill(c.CAL) for m in b.MASKS}
        final={m:self.fill((0,0,0,1)) for m in b.MASKS}
        sites=[{m:(self.fill(c.HIT),self.fill(b.color(m))) for m in b.MASKS} for _ in range(3)]
        return final,cal,sites
    def test_channel_endpoints_and_alpha_only_response(self):
        self.assertEqual(b.color(8),(0,0,0,1))
        f,cal,s=self.fixture()
        for m in b.MASKS:f[m][...,0]=b.color(m)[3]
        r=b.summarize(f,cal,s)
        self.assertTrue(r["calibrated"])
        x=b.classify([r]*3,3)
        self.assertEqual(x["rgba_responsive_views"],dict(red=0,green=0,blue=0,alpha=3))
        self.assertEqual(x["rgb_responsive_views"]["alpha"],3)
        self.assertFalse(x["no_endpoint_response_in_test_views"])
    def test_reject_wrong_color_and_missing_site(self):
        f,cal,s=self.fixture()
        s[1][8]=(self.fill(c.HIT),self.fill(b.color(0)))
        self.assertFalse(b.summarize(f,cal,s)["calibrated"])
        f,cal,s=self.fixture()
        s[2]={m:(self.fill(c.MISS),self.fill(c.MISS)) for m in b.MASKS}
        r=b.summarize(f,cal,s)
        self.assertEqual(b.classify([r]*3,3)["status"],"INCONCLUSIVE_RGBA_ENDPOINT_BASIS")
    def test_all_endpoints_present_and_insensitive(self):
        f,cal,s=self.fixture()
        r=b.summarize(f,cal,s)
        self.assertTrue(b.classify([r]*3,3)["no_endpoint_response_in_test_views"])
        del f[8]
        with self.assertRaises(ValueError):b.summarize(f,cal,s)
    def test_no_shared_hit_rejected(self):
        f,cal,s=self.fixture()
        for row in s:
            row[8]=(self.fill(c.MISS),self.fill(c.MISS))
        self.assertFalse(b.summarize(f,cal,s)["calibrated"])

if __name__=="__main__":unittest.main()
