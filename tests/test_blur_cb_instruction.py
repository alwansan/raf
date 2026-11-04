import unittest
from scripts.blur_cb_instruction import read
class Instruction(unittest.TestCase):
 def test_mov_reads_actual_operand_boundary(self):
  dest=2|(15<<4)|(1<<20);cb=2|(1<<2)|(228<<4)|(8<<12)|(2<<20)
  self.assertEqual(read([54|(6<<24),dest,0,cb,1,17])[0]['byte_offsets'],[272,276,280,284])
 def test_immediate_payload_cannot_be_misread_as_cb(self):
  dest=2|(15<<4)|(1<<20);imm=2|(4<<12)
  self.assertEqual(read([54|(8<<24),dest,0,imm,0x208e46,1,17,0]),[])
 def test_fail_closed(self):
  for w in ([54|(1<<24)],[999|(1<<24)],[54|(2<<24),1<<31]):
   with self.assertRaises(ValueError):read(w)
