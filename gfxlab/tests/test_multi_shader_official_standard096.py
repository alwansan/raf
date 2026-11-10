import unittest
from gfxlab.tools.multi_shader_official_standard096 import official_properties,compare_original_private
SOURCE='''Shader "Standard" { Properties {
 [SyntheticAttr] SyntheticColor("Color", Color) = (1,0.5,0)
 SyntheticFloat("Scalar", Float) = 0.75
 SyntheticTex("Albedo", 2D) = "white" {}
} CGINCLUDE ENDCG SubShader { Pass { Name "FORWARD" } Pass { Name "META" } } FallBack "VertexLit" CustomEditor "StandardShaderGUI" }'''
def tree():
 props=[]
 for name,(typ,val) in official_properties(SOURCE).items():
  p={'m_Name':name,'m_Type':typ,'m_DefTexture':{'m_DefaultName':val if typ==4 else ''}}
  if typ!=4:p.update({'m_DefValue[%d]'%i:v for i,v in enumerate(val)})
  props.append(p)
 return {'m_ParsedForm':{'m_Name':'Standard','m_CustomEditorName':'StandardShaderGUI','m_FallbackName':'VertexLit','m_PropInfo':{'m_Props':props},'m_SubShaders':[{'m_Passes':[{'m_State':{'m_Name':'FORWARD'}}]}]}}
class OfficialStandard096(unittest.TestCase):
 def test_source_schema_not_bytecode_equality(self):
  d=compare_original_private(tree(),SOURCE)
  self.assertEqual(d['safe_counts']['name_match'],3)
  self.assertEqual(d['safe_counts']['default_value_float32_or_texture_name_equal'],3)
  self.assertTrue(d['runtime_pass_names_match_official_after_explicit_editor_META_exclusion'])
  self.assertFalse(d['source_schema_match_alone_proves_original_GPU_code'])
 def test_changed_default_not_accepted(self):
  t=tree();t['m_ParsedForm']['m_PropInfo']['m_Props'][0]['m_DefValue[0]']=.25
  self.assertEqual(compare_original_private(t,SOURCE)['safe_counts']['default_value_different'],1)
 def test_wrong_property_type_not_accepted(self):
  t=tree();t['m_ParsedForm']['m_PropInfo']['m_Props'][0]['m_Type']=1
  self.assertEqual(compare_original_private(t,SOURCE)['safe_counts']['type_mismatch'],1)
 def test_pass_name_mismatch_not_accepted(self):
  t=tree();t['m_ParsedForm']['m_SubShaders'][0]['m_Passes'][0]['m_State']['m_Name']='WRONG'
  self.assertFalse(compare_original_private(t,SOURCE)['runtime_pass_names_match_official_after_explicit_editor_META_exclusion'])
 def test_name_alone_insufficient(self):
  t=tree();t['m_ParsedForm']['m_PropInfo']['m_Props']=[]
  d=compare_original_private(t,SOURCE);self.assertEqual(d['safe_counts']['missing_original_property'],3)
  self.assertFalse(d['originalShaderRestored'])
if __name__=='__main__':unittest.main()
