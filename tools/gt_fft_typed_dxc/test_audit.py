import unittest
import struct
from pathlib import Path
from tools.gt_fft_typed_dxc import audit as a
class TypedTests(unittest.TestCase):
    def test_reversal_and_projection(self):
        original=b"#pragma kernel main\nRWTexture2D<float4> u0 : register(u2);\n[numthreads(512,1,1)] void main(){u0[int2(0,0)] = float4(1,2,3,4);}\n"
        for fmt,(typ,_) in a.TYPES.items():
            changed=a.modify(original,1,fmt)
            self.assertEqual(a.reverse(changed,1,fmt),original)
            self.assertIn(b"RWTexture2D<"+typ+b">",changed)
            if typ.endswith(b"2"):self.assertIn(b"(float4(1,2,3,4)).xy",changed)
        with self.assertRaises(ValueError):a.modify(original.replace(b"register(u2)",b"register(u3)"),1,"RGFloat")
        with self.assertRaises(ValueError):a.modify(original.replace(b"float4(1,2,3,4)",b"u0[int2(1,1)]"),1,"RGFloat")
    def test_indexed_reversal(self):
        original=b"".join(f"#pragma kernel {a.indexed.entry(i)} RAFT_FFT_SLOT={i}\n".encode() for i in range(20))+b"\n"+b"".join(f"#if RAFT_FFT_SLOT == {i}\nRWTexture2D<float4> _TargetTex : register(u2);\nvoid {a.indexed.entry(i)}() {{_TargetTex[int2(0,0)] = float4(1,2,3,4);}}\n#endif\n".encode() for i in range(20))
        self.assertEqual(a.reverse(a.modify(original,20,"RGHalf"),20,"RGHalf"),original)
    def test_render_host(self):
        s=a.render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text())
        self.assertIn("ci.format=fmt.vk",s)
        self.assertIn("size_t(w)*fmt.stride()",s)
    def test_raw_compare(self):
        raw=struct.pack("<2e",.25,.5)*a.n.COUNT
        self.assertEqual(a.compare(raw,raw,"RGHalf")["raw_bit_different"],0)
        self.assertEqual(a.profile(raw,"RGHalf")["written_pixels"],a.n.COUNT)
if __name__=="__main__":unittest.main()
