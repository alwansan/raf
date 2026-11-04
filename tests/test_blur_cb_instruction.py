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

 def test_extended_cb_negation_preserved(self):
  dest=2|(15<<4)|(1<<20);cb=2|(1<<2)|(228<<4)|(8<<12)|(2<<20)|(1<<31)
  r=read([54|(7<<24),dest,0,cb,1|(1<<6),1,17])[0]
  self.assertEqual(r['source_modifier'],1)
  self.assertEqual(r['byte_offsets'],[272,276,280,284])
 def test_extended_chain_or_precision_refused(self):
  dest=2|(15<<4)|(1<<20);cb=2|(1<<2)|(8<<12)|(2<<20)|(1<<31)
  for ext in (1|(1<<31),1|(1<<14),2):
   with self.assertRaises(ValueError):read([54|(7<<24),dest,0,cb,ext,0,0])

 def test_relative_cb_index_is_not_immediate_zero(self):
  dest=2|(15<<4)|(1<<20)
  cb=2|(1<<2)|(228<<4)|(8<<12)|(2<<20)|(2<<25)
  relative=2|(2<<2)|(1<<4)|(1<<20)
  r=read([54|(7<<24),dest,0,cb,1,relative,7])[0]
  self.assertTrue(r['dynamic_index'])
  self.assertEqual(r['byte_offsets'],[])
  self.assertEqual(r['index_expression'][1]['relative']['indices'][0]['immediate'],7)
 def test_relative_payload_truncated_rejected(self):
  dest=2|(15<<4)|(1<<20);cb=2|(1<<2)|(8<<12)|(2<<20)|(2<<25)
  with self.assertRaises(ValueError):read([54|(5<<24),dest,0,cb,1])
