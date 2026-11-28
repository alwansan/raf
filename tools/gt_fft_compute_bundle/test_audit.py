import unittest
from tools.gt_fft_compute_bundle import audit as a
class BundleTests(unittest.TestCase):
    def test_byte_fields(self):
        raw=bytes(range(32))
        self.assertEqual(list(a.byte_leaves({"code":list(raw),"other":[1,2]})),[(("code",),raw)])
        self.assertEqual(list(a.byte_leaves({"code":raw})),[(("code",),raw)])
    def test_reject_unbounded_field(self):
        with self.assertRaises(ValueError):list(a.byte_leaves({"x"*97:bytes(32)}))
    def test_missing_bundle_rejected(self):
        with self.assertRaises(ValueError):a.join_captures([],{},"RGHalf")
if __name__=="__main__":unittest.main()
