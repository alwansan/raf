import unittest
from tools.gt_fft_bundle_serialized_copy import audit as a
class CopyControls(unittest.TestCase):
    def test_unique_replace(self):
        self.assertEqual(a.unique_replace(b"headabcend",b"abc",b"abd"),b"headabdend")
        with self.assertRaises(ValueError):a.unique_replace(b"abcabc",b"abc",b"abd")
        with self.assertRaises(ValueError):a.unique_replace(b"abc",b"abc",b"ab")
    def test_one_word_only(self):
        self.assertEqual(a.one_word_offsets(b"12345678",b"12345679",1),[7])
        with self.assertRaises(ValueError):a.one_word_offsets(b"12345678",b"02345679",1)
        with self.assertRaises(ValueError):a.one_word_offsets(b"12345678",b"12345678",1)
if __name__=="__main__":unittest.main()
