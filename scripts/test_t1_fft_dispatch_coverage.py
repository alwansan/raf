import unittest
from scripts.t1_fft_dispatch_coverage import validate

def sample():
    return dict(compute_shader_guid="a"*32, kernel_name="FFTButterfly",
                find_kernel_index=6, dispatch_kernel_index=6,
                numthreads=[8,8,1], dispatch_groups=[9,8,1],
                logical_extent=[65,64,1])

class CoverageTests(unittest.TestCase):
    def test_nonmultiple_ceiling(self):
        self.assertEqual(validate(sample())["required_groups"], [9,8,1])
    def test_underdispatch_rejected(self):
        a=sample(); a["dispatch_groups"]=[8,8,1]
        with self.assertRaises(ValueError): validate(a)
    def test_overdispatch_rejected(self):
        a=sample(); a["dispatch_groups"]=[10,8,1]
        with self.assertRaises(ValueError): validate(a)
    def test_kernel_mismatch(self):
        a=sample(); a["dispatch_kernel_index"]=7
        with self.assertRaises(ValueError): validate(a)
    def test_boolean_index_rejected(self):
        a=sample(); a["find_kernel_index"]=True
        with self.assertRaises(ValueError): validate(a)
    def test_missing_identity_rejected(self):
        a=sample(); del a["compute_shader_guid"]
        with self.assertRaises(ValueError): validate(a)

if __name__ == "__main__":
    unittest.main()
