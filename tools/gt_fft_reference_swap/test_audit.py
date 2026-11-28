import unittest
from tools.gt_fft_reference_swap import audit as a
class SwapTests(unittest.TestCase):
    def test_scope(self):
        lines=[x.split() for x in a.map_lines().splitlines()]
        self.assertEqual([int(x[2]) for x in lines],[6,7,16,17])
        self.assertEqual(len({x[0] for x in lines}),4)
        self.assertTrue(all(x[0]!=x[1] and len(x[0])==len(x[1])==64 for x in lines))
        self.assertFalse(set(x[0] for x in lines)&{a.PINS[f"indexed-{i}"] for i in a.live.SLOTS})
    def test_reference_pins(self):
        self.assertEqual(set(a.REFERENCES),{"6","7","16","17"})
if __name__=="__main__":unittest.main()
