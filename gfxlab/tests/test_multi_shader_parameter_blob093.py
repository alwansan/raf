import struct,unittest,json
from gfxlab.tools.multi_shader_parameter_blob093 import parameter_blob_private,entries_private,VERSION

def ints(*x):return struct.pack('<%di'%len(x),*x)
def string(x):
 b=x.encode();out=ints(len(b))+b
 return out+b'\0'*((-len(out))%4)
def sample():
 # Empty global group, one CB with a vector member, plus texture and CB binding.
 return (ints(VERSION,2)+string('')+ints(0,0,0)+string('SyntheticCB')+ints(16,1)+
 string('SyntheticColor')+ints(0,1,4,0,0,0)+ints(0)+ints(2)+
 string('SyntheticTex')+ints(0,1,2,4)+string('SyntheticCB')+ints(1,3,0))
class ParameterBlob093(unittest.TestCase):
 def test_bounded_full_record(self):
  d=parameter_blob_private(sample());self.assertEqual(d['groups'][1]['parameters'][0]['index'],0)
  self.assertEqual(d['bindings'][0]['extra'],2)
  self.assertEqual(d['bindings'][1]['index'],3)
 def test_not_DXBC_or_program_record(self):
  with self.assertRaises(ValueError):parameter_blob_private(b'DXBC'+bytes(40))
 def test_trailing_bytes_rejected(self):
  with self.assertRaises(ValueError):parameter_blob_private(sample()+ints(0))
 def test_each_truncation_fails(self):
  raw=sample()
  for n in range(4,len(raw)):
   with self.assertRaises((ValueError,UnicodeError)):parameter_blob_private(raw[:n])
 def test_negative_group_count(self):
  with self.assertRaises(ValueError):parameter_blob_private(ints(VERSION,-1))
 def test_unknown_parameter_version(self):
  with self.assertRaises(ValueError):parameter_blob_private(ints(1,1)+sample()[8:])
 def test_entry_table_bounds(self):
  raw=ints(1,16,4,0,VERSION)
  self.assertEqual(entries_private(raw),[(16,4,0)])
  for off,length,segment in ((0,4,0),(16,99,0),(16,4,1),(-1,4,0)):
   with self.assertRaises(ValueError):entries_private(ints(1,off,length,segment,VERSION))
 def test_entry_partial_overlap_rejected(self):
  with self.assertRaises(ValueError):entries_private(ints(2,28,8,0,32,8,0)+bytes(12))
 def test_binding_type_unknown_rejected(self):
  raw=bytearray(sample());struct.pack_into('<i',raw,len(raw)-12,9)
  with self.assertRaises(ValueError):parameter_blob_private(bytes(raw))
 def test_wrong_CB_member_dimensions_rejected(self):
  raw=sample().replace(string('SyntheticColor')+ints(0,1,4),string('SyntheticColor')+ints(0,1,5))
  with self.assertRaises(ValueError):parameter_blob_private(raw)
if __name__=='__main__':unittest.main()
