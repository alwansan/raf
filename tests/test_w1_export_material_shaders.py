import tempfile
from pathlib import Path
import unittest
from scripts.w1_audit_export_material_shaders import inventory


class ExportReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.assets = self.root / 'Assets'
        self.assets.mkdir()
        self.guid = '1234567890abcdef1234567890abcdef'
        self.shader('one')

    def shader(self, name):
        (self.assets / (name + '.shader')).write_text('Shader "private" {}')
        (self.assets / (name + '.shader.meta')).write_text('guid: ' + self.guid + '\n')

    def material(self, ref, suffix='.mat'):
        p = self.assets / ('private' + suffix)
        p.write_text('%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n  m_Shader: ' + ref + '\n')
        return p

    def test_mixed_embedded_and_custom_preserves_every_byte(self):
        p = self.material('{fileID: 4800000, guid: ' + self.guid + ', type: 3}', '.asset')
        p.write_text(p.read_text() + '--- !u!21 &2100001\nMaterial:\n  m_Shader: {fileID: 46, guid: 0000000000000000f000000000000000, type: 0}\n')
        before = {p.name: p.read_bytes() for p in self.assets.iterdir()}
        r = inventory(self.root)
        self.assertTrue(r['reference_inventory_complete'])
        self.assertEqual(r['counts']['material_documents'], 2)
        self.assertEqual(r['counts']['internal_engine_references'], 1)
        self.assertFalse(r['internal_pointer_authenticity_verified'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.assets.iterdir()})
        self.assertNotIn(self.guid, str(r))
        self.assertNotIn('private', str(r))

    def test_null_fails(self):
        self.material('{fileID: 0}')
        self.assertEqual(inventory(self.root)['errors']['null_shader_reference'], 1)

    def test_unresolved_custom_guid_fails(self):
        self.material('{fileID: 4800000, guid: ' + 'a' * 32 + ', type: 3}')
        self.assertFalse(inventory(self.root)['reference_inventory_complete'])

    def test_duplicate_shader_guid_fails(self):
        self.shader('two')
        self.material('{fileID: 4800000, guid: ' + self.guid + ', type: 3}')
        self.assertEqual(inventory(self.root)['errors']['duplicate_shader_guids'], 1)

    def test_non_shader_document_field_is_ignored(self):
        p = self.material('{fileID: 0}')
        p.write_text(p.read_text().replace('!u!21', '!u!114'))
        r = inventory(self.root)
        self.assertIn('no_material_documents', r['errors'])
        self.assertNotIn('null_shader_reference', r['errors'])

    def test_multiline_or_duplicate_field_is_not_silently_accepted(self):
        p = self.material('{fileID: 0}')
        p.write_text(p.read_text() + '  m_Shader: {fileID: 0}\n')
        self.assertIn('missing_or_ambiguous_shader_field', inventory(self.root)['errors'])
        p.write_text(p.read_text().replace('{fileID: 0}', '{\nfileID: 0\n}'))
        self.assertFalse(inventory(self.root)['reference_inventory_complete'])

    def test_wrong_fileid_and_engine_type_are_not_resolved(self):
        self.material('{fileID: 1, guid: ' + self.guid + ', type: 3}')
        self.assertFalse(inventory(self.root)['reference_inventory_complete'])
        self.material('{fileID: 46, guid: 0000000000000000f000000000000000, type: 3}')
        self.assertFalse(inventory(self.root)['reference_inventory_complete'])

    def test_missing_meta_and_symlink_rejected(self):
        (self.assets / 'one.shader.meta').unlink()
        self.material('{fileID: 4800000, guid: ' + self.guid + ', type: 3}')
        self.assertIn('shader_missing_meta', inventory(self.root)['errors'])
        (self.assets / 'redirect').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            inventory(self.root)


if __name__ == '__main__':
    unittest.main()
