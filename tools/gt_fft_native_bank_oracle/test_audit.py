import struct
import unittest
from pathlib import Path
from tools.gt_fft_native_bank_oracle import audit as a
class NativeTests(unittest.TestCase):
    def test_host_exact_anchors(self):
        s=a.render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text())
        self.assertIn("ci.extent={w,texH,1}",s)
        self.assertIn("4,postBarriers.data()",s)
        self.assertIn("GT_FFT_NATIVE_HOST exact_mapped_inputs=true",s)
        with self.assertRaises(ValueError):a.render_host("broken")
    def test_classes(self):
        self.assertEqual([a.cls(x) for x in (0,0x7fc12345,0x7f800000,0xff800000)],[0,1,2,3])
    def test_compare(self):
        old=a.IMAGE_BYTES
        try:
            a.IMAGE_BYTES=16
            x=struct.pack("<4I",0,0x7fc12345,0x7f800000,0x3f800000)
            y=struct.pack("<4I",0,0x7fc54321,0xff800000,0x40000000)
            self.assertEqual(a.compare(x,y),dict(raw_bit_different=3,class_mismatch=1,finite_different=1,finite_over_tolerance=1))
        finally:a.IMAGE_BYTES=old
    def test_signed_input(self):
        x=a.input_bytes("signed")
        self.assertEqual(len(x),a.IMAGE_BYTES)
        self.assertEqual(struct.unpack_from("<4f",x),((368-510)/1024,(368%113-56)/256,(368%59-29)/128,1))
        self.assertEqual(a.input_bytes("zero"),bytes(a.IMAGE_BYTES))
if __name__=="__main__":unittest.main()
