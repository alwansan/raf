import unittest
from pathlib import Path
import tempfile
from tools.gt_fft_live_replay import audit as a
class ReplayTests(unittest.TestCase):
    def test_host_independent(self):
        s=a.render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text())
        self.assertIn("const std::array<int,4> passSource={0,0,0,0};",s)
        self.assertNotIn("if(i==2) {",s)
        self.assertIn("stage.pName=entry.c_str();",s)
        self.assertEqual(s.count(a.MARKER),1)
        self.assertIn("std::array<VkImageMemoryBarrier,4> postBarriers",s)
    def test_output_order(self):
        self.assertEqual(a.FILES,("native0","round0","native1","round1"))
    def test_exact_mounted_module_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);outside=root/"outside.spv";outside.write_bytes(bytes(range(32)))
            mount=root/"mount";mount.mkdir()
            x=a.mount_modules(mount,6,{"reference":outside})
            self.assertEqual(x["reference"].read_bytes(),outside.read_bytes())
            self.assertEqual(x["reference"].parent.parent,mount)
    def test_stages(self):
        self.assertEqual([(s-s%2,s%2) for s in a.live.SLOTS],[(6,0),(6,1),(16,0),(16,1)])
if __name__=="__main__":unittest.main()
