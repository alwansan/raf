import unittest
from tools.gt_fft_original_constructor import audit as a
class Controls(unittest.TestCase):
    def test_bool_forwarding(self):
        for x in (False,True):
            self.assertEqual(a.eval_bool("a",{"a":x}),x)
            self.assertEqual(a.eval_bool("! a",{"a":x}),not x)
        self.assertFalse(a.eval_bool("false",{}))
        self.assertTrue(a.eval_bool("true",{}))
        for invalid in ("a || b","unknown","1","!true"):
            with self.assertRaises(ValueError):a.eval_bool(invalid,{"a":True,"b":False})
    def test_constructor_signature(self):
        rows=a.unique_ctor("public Dx11FFT(ComputeShader s, int r, bool p, bool b) : base(r,p,b,true) {}","Dx11FFT")
        self.assertEqual(rows,[("ComputeShader","s"),("int","r"),("bool","p"),("bool","b")])
        with self.assertRaises(ValueError):a.unique_ctor("public Dx11FFT(int r) {}","Dx11FFT")
if __name__=="__main__":unittest.main()
