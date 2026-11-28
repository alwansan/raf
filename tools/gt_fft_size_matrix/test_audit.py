import unittest
from pathlib import Path
from tools.gt_fft_size_matrix import audit as a
class MatrixTests(unittest.TestCase):
    def test_dimensions(self):
        self.assertEqual([a.dimensions(s) for s in a.SIZES],[(5,(0,1,10,11)),(6,(2,3,12,13)),(7,(4,5,14,15)),(9,(8,9,18,19))])
    def test_templates(self):
        for size in a.SIZES:
            stages,slots=a.dimensions(size)
            h=a.render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text(),size)
            self.assertIn(f"dispatchGroupY=={size}",h)
            self.assertIn(f"uint32_t texH=t==1?{stages}:h;",h)
            c=a.render_editor(Path("tools/gt_fft_indexed_dxc/IndexedPair.cs").read_text(),size)
            self.assertIn(f"const int Size={size}, Count=Size*Size, Stages={stages};",c)
            l=a.render_layer(Path("tools/gt_fft_live_module/layer.cpp").read_text(),size)
            self.assertIn(f"x==1&&y=={size}&&z==1",l)
            self.assertIn(f'label!="indexed-{slots[0]}"',l)
            self.assertIn("x==64&&y==64&&z==1",l)
    def test_refuse_unknown_size(self):
        with self.assertRaises(ValueError):a.dimensions(512)
if __name__=="__main__":unittest.main()
