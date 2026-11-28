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
if __name__=="__main__":unittest.main()
