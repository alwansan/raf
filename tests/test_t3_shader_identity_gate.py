import tempfile
import unittest
from pathlib import Path
from scripts.t3_shader_identity_gate import check

G = 'a' * 32

def fixture(root):
    (root/'x.shader').write_text('Shader "test" { SubShader { Pass { CGPROGRAM\nENDCG } } }')
    (root/'x.shader.meta').write_text('guid: '+G+'\n')
    (root/'m.mat').write_text('m_Shader: {fileID: 4800000, guid: '+G+', type: 3}')
    return dict(source_sha256='b'*64, source_shader_id=48, export_shader_guid=G,
                shader_path='x.shader', material_paths=['m.mat'])

class GateTests(unittest.TestCase):
    def test_link_structural_only(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d))
            self.assertEqual(check(d,m)['status'],'STRUCTURAL_LINK_ONLY')
    def test_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d)); m['export_shader_guid']='c'*32
            with self.assertRaisesRegex(ValueError,'shader_guid_mismatch'): check(d,m)
    def test_dummy(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d)); (Path(d)/'x.shader').write_text('//DummyShaderTextExporter')
            with self.assertRaisesRegex(ValueError,'placeholder'): check(d,m)
    def test_traversal(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d)); m['shader_path']='../x.shader'
            with self.assertRaisesRegex(ValueError,'unsafe_relative_path'): check(d,m)
    def test_unpinned(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d)); m['source_sha256']='bad'
            with self.assertRaisesRegex(ValueError,'unverified_source_pin'): check(d,m)
    def test_bad_material(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d)); (Path(d)/'m.mat').write_text('no shader')
            with self.assertRaisesRegex(ValueError,'material_shader_link_mismatch'): check(d,m)


    def test_block_comment_cannot_supply_shader_declaration(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d))
            (Path(d)/'x.shader').write_text('/* Shader "fake" { } */')
            with self.assertRaisesRegex(ValueError,'missing_shader_declaration'): check(d,m)

    def test_line_comment_cannot_supply_shader_declaration(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d))
            (Path(d)/'x.shader').write_text('// Shader "fake" { }')
            with self.assertRaisesRegex(ValueError,'missing_shader_declaration'): check(d,m)

    def test_empty_shader_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d))
            (Path(d)/'x.shader').write_text('')
            with self.assertRaisesRegex(ValueError,'missing_shader_declaration'): check(d,m)

    def test_multiline_shader_declaration_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d))
            (Path(d)/'x.shader').write_text('Shader "valid"\\n{ SubShader { Pass {} } }')
            self.assertEqual(check(d,m)['status'],'STRUCTURAL_LINK_ONLY')

    def test_comment_material_pointer_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d))
            (Path(d)/'m.mat').write_text('# m_Shader: {fileID: 4800000, guid: '+G+', type: 3}')
            with self.assertRaisesRegex(ValueError,'material_shader_link_mismatch'): check(d,m)

    def test_duplicate_material_pointer_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d))
            line='m_Shader: {fileID: 4800000, guid: '+G+', type: 3}'
            (Path(d)/'m.mat').write_text(line+'\\n'+line)
            with self.assertRaisesRegex(ValueError,'material_shader_link_mismatch'): check(d,m)

    def test_block_comment_with_real_shader_declaration_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            m=fixture(Path(d))
            (Path(d)/'x.shader').write_text('/* Shader "fake" { } */\\nShader "valid" { SubShader { Pass {} } }')
            self.assertEqual(check(d,m)['status'],'STRUCTURAL_LINK_ONLY')

if __name__ == '__main__': unittest.main()
