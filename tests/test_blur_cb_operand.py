import unittest
from scripts.blur_cb_operand import decode
class Operand(unittest.TestCase):
 def test_nonidentity_swizzle_preserved(self):
  t=2|(1<<2)|(8<<12)|(2<<20)|(3<<4)|(2<<6)|(1<<8)
  self.assertEqual(decode([t,1,17])['byte_offsets'],[284,280,276,272])
 def test_single_component(self):
  t=2|(2<<2)|(8<<12)|(2<<20)|(2<<4)
  self.assertEqual(decode([t,0,3])['byte_offsets'],[56])
 def test_reject_unsupported_instead_of_scan(self):
  t=2|(1<<2)|(8<<12)|(2<<20)
  for words in ([t], [t|(1<<31),0,0], [t|(1<<22),0,0], [t,256,0], [t,0,-1], [t&~12,0,0]):
   with self.assertRaises(ValueError):decode(words)
