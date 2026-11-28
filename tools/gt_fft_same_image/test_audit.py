import struct
import unittest
from tools.gt_fft_same_image import audit as a
class CrossTests(unittest.TestCase):
    def setUp(self):
        self.saved=a.n.IMAGE_BYTES,a.n.COUNT
        a.n.IMAGE_BYTES=16;a.n.COUNT=1
    def tearDown(self):
        a.n.IMAGE_BYTES,a.n.COUNT=self.saved
    def pixel(self,value):return struct.pack("<4I",value,value,value,value)
    def test_localization(self):
        x=self.pixel(0x3f800000);y=self.pixel(0x40000000);nan=self.pixel(0x7fc00000)
        data={k:x if k.endswith("0") else y for k in a.LABELS}
        data["indexed-chain"]=nan
        r=a.compare_case(data,[x,y])
        self.assertEqual(r["outputs"]["indexed0"]["vs_cpu"]["raw_bit_different"],0)
        self.assertEqual(r["outputs"]["indexed-cpu"]["vs_cpu"]["raw_bit_different"],0)
        self.assertEqual(r["indexed_chain_vs_own_replay"]["class_mismatch"],4)
    def test_reject_incomplete(self):
        x=self.pixel(0);data={k:x for k in a.LABELS}
        data.pop("indexed-cpu")
        with self.assertRaises(ValueError):a.compare_case(data,[x,x])
    def test_device_fields(self):
        self.assertEqual(a.device_fields("  deviceName = llvmpipe (test)\n driverInfo = Mesa 22\n ignored = hidden\n"),{"deviceName":"llvmpipe (test)","driverInfo":"Mesa 22"})
    def test_capture_identity(self):
        self.assertEqual(a.image_name(6,"signed","native",0),"image-6-signed-native-0.rgba32f")
        with self.assertRaises(ValueError):a.image_name(7,"signed","native",0)
    def test_reject_sentinel(self):
        x=self.pixel(0)
        with self.assertRaises(ValueError):a.classify_pair(self.pixel(0x46000000),x)
if __name__=="__main__":unittest.main()
