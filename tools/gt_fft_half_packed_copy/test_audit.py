import struct
import unittest
from tools.gt_fft_half_packed_copy import audit as a
class PackedHalfTests(unittest.TestCase):
    def test_projection_and_expansion(self):
        raw=struct.pack("<4f",1+2**-11,1+3*2**-11,-.5,.25)*a.n.COUNT
        bits=a.scratch_to_half(raw,"RGHalf")
        self.assertEqual(bits,struct.pack("<2H",0x3c00,0x3c02)*a.n.COUNT)
        self.assertEqual(a.expanded_half(bits,"RGHalf"),struct.pack("<4f",1,1+2**-9,0,1)*a.n.COUNT)
    def test_subnormal_and_signed_zero(self):
        raw=struct.pack("<4f",2**-25,-2**-25,3*2**-25,-0.)*a.n.COUNT
        bits=a.scratch_to_half(raw,"ARGBHalf")
        self.assertEqual(bits,struct.pack("<4H",0,0x8000,2,0x8000)*a.n.COUNT)
    def test_nonfinite(self):
        raw=struct.pack("<4f",float("nan"),1,2,3)*a.n.COUNT
        with self.assertRaises(ValueError):a.scratch_to_half(raw,"RGHalf")
if __name__=="__main__":unittest.main()
