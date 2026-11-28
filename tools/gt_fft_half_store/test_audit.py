import struct
import unittest
from tools.gt_fft_half_store import audit as a
class HalfStoreTests(unittest.TestCase):
    def test_tie_and_projection(self):
        v=(1+2**-11,1+3*2**-11,-.5,.25)
        raw=struct.pack("<4f",*v)*a.n.COUNT
        self.assertEqual(a.scratch_to_half(raw,"RGHalf"),struct.pack("<2H",0x3c00,0x3c02)*a.n.COUNT)
        self.assertEqual(a.scratch_to_half(raw,"ARGBHalf"),struct.pack("<4H",0x3c00,0x3c02,0xb800,0x3400)*a.n.COUNT)
    def test_nonfinite_and_extent(self):
        with self.assertRaises(ValueError):a.scratch_to_half(b"","RGHalf")
        raw=struct.pack("<4f",float("nan"),1,2,3)*a.n.COUNT
        with self.assertRaises(ValueError):a.scratch_to_half(raw,"ARGBHalf")
    def test_pins(self):
        self.assertEqual(len(a.PINS),8)
        self.assertEqual(set(a.PINS),set(a.live.LABELS)-{"control"})
if __name__=="__main__":unittest.main()
