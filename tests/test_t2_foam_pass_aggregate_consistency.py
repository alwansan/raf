import unittest
from scripts.t2_foam_pass_aggregate_consistency import check_counts, unique
P="field_api_Graphics_Blit_"
def fixture():
    d={P+"explicit_sites_pass_"+x:0 for x in ("literal0","literal1","other_literal","unknown","mixed")}
    d[P+"explicit_sites_pass_literal0"]=d[P+"explicit_sites_pass_literal1"]=1
    for role,vs in (("source",("Texture","RenderTexture","unknown")),("destination",("RenderTexture","null","unknown"))):
        for kind in ("explicit","pass0","pass1"):
            for v in vs: d[P+kind+"_"+role+"_"+v]=0
        d[P+"explicit_"+role+"_"+vs[0]]=1
        d[P+"explicit_"+role+"_"+vs[-1]]=1
        d[P+"pass0_"+role+"_"+vs[0]]=1
        d[P+"pass1_"+role+"_"+vs[-1]]=1
    return d
class Tests(unittest.TestCase):
    def test_valid(self): self.assertEqual(check_counts(fixture())["pass1"]["source"],"unknown")
    def test_bad_total(self):
        d=fixture();d[P+"explicit_source_Texture"]=0
        with self.assertRaises(ValueError): check_counts(d)
    def test_bad_pass(self):
        d=fixture();d[P+"explicit_sites_pass_unknown"]=1
        with self.assertRaises(ValueError): check_counts(d)
    def test_boolean(self):
        d=fixture();d[P+"pass0_source_Texture"]=True
        with self.assertRaises(ValueError): check_counts(d)
    def test_duplicate(self):
        with self.assertRaises(ValueError): unique([("x",1),("x",2)])
    def test_drift(self):
        d=fixture();d[P+"explicit_sites_pass_literal0"]=2
        with self.assertRaises(ValueError): check_counts(d)
if __name__=="__main__": unittest.main()
