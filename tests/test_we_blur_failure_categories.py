import unittest
from scripts.we_blur_failure_categories import census
class Census(unittest.TestCase):
 def test_original_gap_classes_stay_distinct(self):
  dst=2|(15<<4)|(1<<20)
  unknown=2|(99<<12)
  relative=2|(1<<20)|(1<<22)
  r=census([[54|(4<<24),dst,0,unknown],[54|(5<<24),dst,0,relative,0]])
  self.assertEqual(r['failure_categories'],{'operand type':1,'relative operand':1})
  self.assertFalse(r['complete_coverage'])
 def test_payload_not_disclosed_or_scanned(self):
  dst=2|(15<<4)|(1<<20);imm=2|(4<<12)
  r=census([[54|(8<<24),dst,0,imm,0x208e46,1,17,0]])
  self.assertEqual(r['decoded_cb_reads'],0)
  self.assertTrue(r['complete_coverage'])
  self.assertFalse(r['shader_reconstructed'])
 def test_truncation_counted(self):
  self.assertEqual(census([[54|(1<<24)]])['failure_categories'],{'truncated operand':1})
if __name__=='__main__':unittest.main()
