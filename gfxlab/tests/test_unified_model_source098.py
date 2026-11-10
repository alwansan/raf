import unittest,struct
from gfxlab.tools.unified_model_source098 import normal_AG_candidate,material_record,chunk_hashes_private
class Source098(unittest.TestCase):
 def test_normal_uses_original_A_G_and_reconstructs_Z(self):
  from PIL import Image
  source=Image.new('RGBA',(1,1),(255,128,12,128));out=normal_AG_candidate(source)
  self.assertEqual(out.getpixel((0,0)),(128,128,255,255))
  self.assertEqual(source.getpixel((0,0)),(255,128,12,128))
 def test_nonunit_red_rejects_AG_assumption(self):
  from PIL import Image
  with self.assertRaises(ValueError):normal_AG_candidate(Image.new('RGBA',(1,1),(100,128,12,128)))
 def test_source_saved_float_is_not_replaced_with_lab_constant(self):
  material={'m_SavedProperties':{'m_Floats':[('SyntheticFloat',.375)],'m_Colors':[('SyntheticColor',dict(r=.1,g=.2,b=.3,a=1))]},'m_ValidKeywords':['SYNTHETIC_KEYWORD'],'m_InvalidKeywords':[],'m_CustomRenderQueue':-1,'m_EnableInstancingVariants':True,'m_DoubleSidedGI':False,'m_LightmapFlags':0,'stringTagMap':[]}
  record=material_record(material,'MAT_00')
  self.assertEqual(record['floats'][0]['value'],.375);self.assertEqual(record['keywords'],['SYNTHETIC_KEYWORD'])
  self.assertEqual(record['renderQueue'],-1)
 def test_invalid_keyword_source_not_silently_dropped(self):
  material={'m_SavedProperties':{},'m_ValidKeywords':[],'m_InvalidKeywords':['unknown']}
  with self.assertRaises(ValueError):material_record(material,'MAT_00')
if __name__=='__main__':unittest.main()
