import struct
import unittest
from tools.gt_fft_half_attachment_probe import audit as a
class AttachmentTests(unittest.TestCase):
    def test_signed_ties(self):
        raw=struct.pack("<4f",1+2**-11,1+3*2**-11,-.5,.25)*a.n.COUNT
        self.assertEqual(a.scratch_to_half(raw,"RGHalf"),struct.pack("<2H",0x3c00,0x3c02)*a.n.COUNT)
    def test_exact_control_selection(self):
        good=dict(raw_bit_different=0,nonfinite_lanes=0,written_pixels=a.n.COUNT)
        bad=dict(good,raw_bit_different=1)
        rows=[dict(method=0,sources={"texture2d":good,"render_texture":bad}),
              dict(method=1,sources={"texture2d":good}),
              dict(method=2,sources={"texture2d":good,"render_texture":good})]
        self.assertEqual(a.exact_methods(rows),[2])
    def test_diagnostic(self):
        raw=struct.pack("<2H",0,0x8000)*a.n.COUNT
        report=a.diagnostic(raw,raw,"RGHalf")
        self.assertEqual(report["raw_bit_different"],0)
        self.assertEqual(report["zero_lanes"],[a.n.COUNT,0])
        self.assertEqual(report["negative_zero_lanes"],[0,a.n.COUNT])
        self.assertEqual(report["coordinate_pixel_mismatch"],dict(x0y0=0,x0y1=0,x1y0=0,x1y1=0))
if __name__=="__main__":unittest.main()
