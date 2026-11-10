import unittest,struct
from gfxlab.tools.multi_shader_material_cb_payload095 import partial_payload_private,saved_values_private

def group(name='Tint',offset=16,columns=4,typ=0):
 m=dict(name=name,index=offset,columns=columns,type=typ,matrix=False,array=0)
 return {'bindings':[dict(name='SyntheticCB',type=1,index=2)],'groups':[dict(name='SyntheticCB',parameters={name:m})]}
class MaterialPayload095(unittest.TestCase):
 def test_authentic_offset_float32_byte_write_and_unknowns(self):
  buffers,c=partial_payload_private(group(),{2:4},{'Tint':('color',(0.1,0.2,0.3,0.4))},{'Tint':0})
  data,known=buffers[2];self.assertEqual(data[16:32],struct.pack('<4f',.1,.2,.3,.4))
  self.assertEqual(sum(known),16);self.assertEqual(c['unknown_runtime_byte_count'],48)
  self.assertFalse(any(known[:16]))
 def test_scalar_saved_value_only_supported(self):
  buffers,c=partial_payload_private(group('Scalar',4,1),{2:1},{'Scalar':('float',(.75,))},{'Scalar':2})
  self.assertEqual(buffers[2][0][4:8],struct.pack('<f',.75))
 def test_outside_source_declared_size_rejected(self):
  with self.assertRaises(ValueError):partial_payload_private(group(offset=60),{2:4},{'Tint':('color',(1,1,1,1))},{'Tint':0})
 def test_undeclared_CB_never_written(self):
  buffers,c=partial_payload_private(group(),{3:4},{'Tint':('color',(1,1,1,1))},{'Tint':0})
  self.assertEqual(buffers,{})
 def test_engine_unknown_not_fabricated(self):
  buffers,c=partial_payload_private(group(),{2:4},{},{'Tint':0})
  self.assertEqual(c['known_material_byte_count'],0);self.assertEqual(c['unknown_runtime_byte_count'],64)
 def test_property_type_mismatch_rejected(self):
  with self.assertRaises(ValueError):partial_payload_private(group(),{2:4},{'Tint':('color',(1,1,1,1))},{'Tint':2})
 def test_nonfloat_member_not_reinterpreted(self):
  buffers,c=partial_payload_private(group(typ=1),{2:4},{'Tint':('color',(1,1,1,1))},{'Tint':0})
  self.assertEqual(c['saved_member_type_or_array_not_supported'],1);self.assertEqual(c['known_material_byte_count'],0)
 def test_unaligned_offset_rejected(self):
  with self.assertRaises(ValueError):partial_payload_private(group(offset=3),{2:4},{'Tint':('color',(1,1,1,1))},{'Tint':0})
if __name__=='__main__':unittest.main()
