import unittest
from tools.gt_fft_indexed_dxc import audit as a
class IndexedTests(unittest.TestCase):
    def source(self):
        return b"".join(f"#pragma kernel {a.indexed.entry(i)} RAFT_FFT_SLOT={i}\n".encode() for i in range(20))+b"\n// authored body\n"
    def test_exact_reversal(self):
        source=self.source()
        self.assertEqual(a.strip_indexed(a.indexed_source(source)),source)
    def test_order_or_missing_rejected(self):
        with self.assertRaises(ValueError):a.indexed_source(self.source().replace(b"RAFT_FFT_SLOT=0\n",b"RAFT_FFT_SLOT=1\n"))
        with self.assertRaises(ValueError):a.indexed_source(self.source().replace(b"#pragma kernel ",b"// kernel ",1))
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):a.indexed_source(a.indexed_source(self.source()))
if __name__=="__main__":unittest.main()
