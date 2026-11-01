from pathlib import Path
import tempfile
import unittest
from scripts.restore_tmp_shaders import restore,rewrite_includes,ROOT

class ShaderTests(unittest.TestCase):
    def fixture(self,root,name='TextMeshPro/Distance Field'):
        target=root/'project/Assets/Shader/font.shader';target.parent.mkdir(parents=True)
        target.write_text('Shader "'+name+'" { SubShader { Pass {} } }')
        Path(str(target)+'.meta').write_bytes(b'guid: abcdef0123456789abcdef0123456789\n')
        return target
    def test_real_program_replaces_placeholder_with_same_guid_and_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);target=self.fixture(root);original=target.read_bytes();meta=Path(str(target)+'.meta').read_bytes()
            shader='Shader "TextMeshPro/Distance Field" {\n#include "TMPro.cginc"\n}'
            restore(root/'project',root/'backup',{'TextMeshPro/Distance Field':shader},{'TMPro.cginc':'#include "UnityCG.cginc"'},b'notice')
            self.assertEqual(Path(str(target)+'.meta').read_bytes(),meta)
            self.assertEqual((root/'backup/Shader/font.shader').read_bytes(),original)
            self.assertIn(ROOT+'TMPro.cginc',target.read_text())
            self.assertEqual((root/'project'/ROOT/'LICENSE.md').read_bytes(),b'notice')
    def test_unknown_shader_refuses_without_modifying(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);target=self.fixture(root,'TextMeshPro/Unknown');original=target.read_bytes()
            with self.assertRaises(ValueError):restore(root/'project',root/'backup',{}, {},b'notice')
            self.assertEqual(target.read_bytes(),original)
    def test_only_vendor_local_includes_relocated(self):
        s='#include "UnityCG.cginc"\n#include "TMPro.cginc"'
        out=rewrite_includes(s,{'TMPro.cginc':'x'})
        self.assertIn('#include "UnityCG.cginc"',out)
        self.assertIn(ROOT+'TMPro.cginc',out)
