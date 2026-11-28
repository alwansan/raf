import struct
import unittest
from tools.gt_fft_source_format_pair import audit as a
class FormatTests(unittest.TestCase):
    def table(self):return b"".join(struct.pack("<4f",i%512,(i+1)%512,.5,-.25) for i in range(a.SIZE*a.STAGES))
    def test_table(self):
        x=self.table();self.assertEqual(a.table_check(x,x)["integer_address_lanes"],8192)
    def test_invalid_address(self):
        x=self.table()
        with self.assertRaises(ValueError):a.table_check(struct.pack("<f",.25)+x[4:],x)
        with self.assertRaises(ValueError):a.table_check(x,x[:-4])
    def test_no_half_guess(self):
        x=self.table();y=bytearray(x);struct.pack_into("<f",y,8,.25)
        with self.assertRaises(ValueError):a.table_check(x,bytes(y))
if __name__=="__main__":unittest.main()
