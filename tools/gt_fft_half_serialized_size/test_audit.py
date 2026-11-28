import unittest
from pathlib import Path
from tools.gt_fft_half_serialized_size import audit as a
class SizeControls(unittest.TestCase):
    def test_prior_pins_all_sizes(self):
        for size in a.matrix.SIZES:
            self.assertEqual(len(a.prior_pins(size)),8)
    def test_host_dimensions(self):
        text=Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text()
        for size in a.matrix.SIZES:
            stages,_=a.matrix.dimensions(size)
            host=a.copy.render_host(text,[("main",[0,1,2])]*4,size,stages)
            self.assertIn(f"dispatchGroupY=={size}",host)
            self.assertIn(f"size_t(w)*(i?{stages}:h)",host)
            self.assertIn(f"texH=t==1?{stages}:h",host)
    def test_rg_widths(self):
        self.assertEqual(a.FORMATS["RGFloat"],("rg32f",2,4))
        self.assertEqual(a.FORMATS["RGHalf"],("rg16f",2,2))
    def test_rgfloat_missing_bundle_rejected(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as root:
            p=Path(root)
            with self.assertRaises(ValueError):a.read_rgfloat(p,p/"out",{"bundle_sha256":["0"*64]*5},(0,1,10,11))
if __name__=="__main__":unittest.main()
