import unittest
from gfxlab.tools.multi_shader_android_stage_pack094 import controlled_glsl_names
class GLSLNames094(unittest.TestCase):
 def test_stage_private_resources_and_common_IO(self):
  src='#version 310 es\nlayout(binding=0) uniform cb0 {vec4 a[4];} data;\nuniform highp sampler2D tex;\nout vec4 v0;void main(){v0=texture(tex,data.a[0].xy);}'
  out=controlled_glsl_names(src,{'outputs':[{'name':'v0','location':2}]},'vertex')
  self.assertIn('uniform vertex_cb0',out);self.assertIn('sampler2D vertex_tex',out)
  self.assertIn('gfx_io_2_c0=texture(vertex_tex',out)
  self.assertIn('data.a[0].xy',out)
 def test_identifier_substrings_unchanged(self):
  src='#version 310 es\nout vec4 v0;void main(){float v00=1.0;v0=vec4(v00);}'
  out=controlled_glsl_names(src,{'outputs':[{'name':'v0','location':0}]},'vertex')
  self.assertIn('float v00=1.0',out)
 def test_unknown_version_rejected(self):
  with self.assertRaises(ValueError):controlled_glsl_names('#version 450',{},'vertex')
 def test_interface_identifier_rejected(self):
  with self.assertRaises(ValueError):controlled_glsl_names('#version 310 es',{'inputs':[{'name':'bad;','location':0}]},'fragment')
if __name__=='__main__':unittest.main()
