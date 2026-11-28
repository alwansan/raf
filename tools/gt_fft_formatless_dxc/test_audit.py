import unittest
import struct
from pathlib import Path
from tools.gt_fft_formatless_dxc import audit as a
class FormatTests(unittest.TestCase):
    def test_reversal(self):
        original=b"#pragma kernel main\nRWTexture2D<float4> u0 : register(u2);\n[numthreads(512,1,1)] void main(){}\n"
        self.assertEqual(a.reverse(a.modify(original,1),1),original)
        with self.assertRaises(ValueError):a.modify(original.replace(b"register(u2)",b"register(u3)"),1)
    def test_render_host(self):
        s=a.render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text())
        self.assertIn("ci.format=fmt.vk",s)
        self.assertIn("size_t(w)*fmt.stride()",s)
        self.assertIn("size_t(w)*imageFormat.stride());",s)
    def test_raw_compare(self):
        raw=struct.pack("<2e",.25,.5)*a.n.COUNT
        self.assertEqual(a.compare(raw,raw,"RGHalf")["raw_bit_different"],0)
        self.assertEqual(a.profile(raw,"RGHalf")["written_pixels"],a.n.COUNT)
if __name__=="__main__":unittest.main()
