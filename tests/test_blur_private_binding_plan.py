import unittest
from scripts.blur_private_binding_plan import build,public_summary
class BindingPlan(unittest.TestCase):
 def source(self):
  return dict(m_ConstantBufferBindings=[dict(m_NameIndex=0,m_Index=1)],
   m_ConstantBuffers=[dict(m_NameIndex=0,m_Size=368,m_IsPartialCB=True,
    m_MatrixParams=[dict(m_NameIndex=1,m_Index=272,m_RowCount=4,m_Type=0,m_ArraySize=0)],
    m_VectorParams=[],m_StructParams=[])],
   m_TextureParams=[dict(m_NameIndex=2,m_Index=2,m_SamplerIndex=3,m_Dim=2)])
 def test_private_plan_preserves_original_offsets_and_size(self):
  p=build(self.source(),[('private_buffer',0),('private_matrix',1),('private_texture',2)])
  self.assertEqual(p['buffers'][0]['allocation_bytes'],368)
  self.assertEqual(p['buffers'][0]['members'][0]['serialized_index'],272)
  s=public_summary(p)
  self.assertEqual((s['named_buffers'],s['named_members'],s['named_textures']),(1,1,1))
  self.assertNotIn('private_matrix',str(s))
  self.assertFalse(s['upload_layout_or_gpu_verified'])
 def test_missing_or_duplicate_names_rejected(self):
  for names in ([('a',0)],[('a',0),('b',0)]):
   with self.assertRaises(ValueError):build(self.source(),names)
 def test_missing_binding_rejected(self):
  c=self.source();c['m_ConstantBufferBindings']=[]
  with self.assertRaises(ValueError):build(c,[('a',0),('b',1),('c',2)])
