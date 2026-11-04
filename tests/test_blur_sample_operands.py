import unittest
from scripts.blur_sample_operands import sample
class Sampling(unittest.TestCase):
 def words(self):
  dest=2|(15<<4)|(1<<20);coord=2|(1<<2)|(228<<4)|(1<<20)
  tex=2|(1<<2)|(228<<4)|(7<<12)|(1<<20);sam=(6<<12)|(1<<20)
  return [69|(9<<24),dest,0,coord,1,tex,2,sam,3]
 def test_original_binding_pair(self):
  self.assertTrue(sample(self.words(),[dict(m_Index=2,m_SamplerIndex=3)])['unique_original_pair'])
 def test_wrong_sampler_not_accepted(self):
  self.assertFalse(sample(self.words(),[dict(m_Index=2,m_SamplerIndex=4)])['unique_original_pair'])
 def test_bad_extent(self):
  with self.assertRaises(ValueError):sample(self.words()[:-1],[])
