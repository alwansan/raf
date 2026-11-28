import unittest
from tools.gt_fft_live_module import audit as a
class CaptureTests(unittest.TestCase):
    def test_metadata_control(self):
        self.assertEqual(a.meta("64 64 1 0 0 Coordinate\n","control"),((64,64,1),0,0,"Coordinate"))
    def test_metadata_actual_slot(self):
        self.assertEqual(a.meta("1 512 1 2 8 main","indexed-16"),((1,512,1),2,8,"main"))
    def test_wrong_dispatch(self):
        for x in ("1 511 1 0 0 main","1 512 1 -1 0 main","1 512 1 0 0 ../main","1 512 1 0 0 main extra"):
            with self.assertRaises(ValueError):a.meta(x,"standalone-16")
    def test_unknown_marker(self):
        with self.assertRaises(ValueError):a.meta("1 512 1 0 0 main","unknown")
    def test_population(self):
        self.assertEqual(len(set(a.LABELS)),9)
if __name__=="__main__":unittest.main()
