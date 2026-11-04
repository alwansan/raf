import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.b03_verify_renderer_material_links import LinkError, audit, parse_pointer, renderer_slots


class RendererMaterialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'game'
        self.assets = self.project / 'Assets'
        self.assets.mkdir(parents=True)
        self.m_guid = 'f' * 32
        self.r_guid = 'a' * 32
        self.material_path = self.assets / 'Primary.mat'
        self.renderer_path = self.assets / 'Level.prefab'
        self.save(self.material_path, self.material('2100000'), self.m_guid)
        self.save(self.renderer_path, self.renderer(), self.r_guid)

    def save(self, file, body, guid):
        file.write_text('%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n' + body)
        Path(str(file) + '.meta').write_text('fileFormatVersion: 2\nguid: ' + guid + '\n')

    def material(self, anchor):
        return f'--- !u!21 &{anchor}\nMaterial:\n  m_Name: authored\n'

    def renderer(self, pointer=None, header='--- !u!23 &123\nMeshRenderer:\n', extras=''):
        if pointer is None:
            pointer = f'{{fileID: 2100000, guid: {self.m_guid}, type: 2}}'
        return header + '  m_Enabled: 1\n  m_Materials:\n  - ' + pointer + '\n' + extras

    def test_valid_external_reference(self):
        out = audit(self.project)
        self.assertEqual(out['counts']['verified_local_material_references'], 1)
        self.assertTrue(out['local_reference_structure_valid'])
        self.assertTrue(out['all_material_slots_authenticated'])
        self.assertFalse(out['original_to_export_material_identity_verified'])

    def test_unresolved_shader_is_not_confused_with_material_pointer(self):
        self.save(self.renderer_path, self.renderer(pointer=f'{{fileID: 2100000, guid: {"1"*32}, type: 2}}'), self.r_guid)
        out = audit(self.project)
        self.assertFalse(out['local_reference_structure_valid'])
        self.assertEqual(out['errors']['unresolved_material_references'], 1)

    def test_wrong_fileid_refused(self):
        self.save(self.renderer_path, self.renderer(pointer=f'{{fileID: 2100001, guid: {self.m_guid}, type: 2}}'), self.r_guid)
        self.assertEqual(audit(self.project)['errors']['unresolved_material_references'], 1)

    def test_wrong_reference_type_refused(self):
        self.save(self.renderer_path, self.renderer(pointer=f'{{fileID: 2100000, guid: {self.m_guid}, type: 1}}'), self.r_guid)
        self.assertEqual(audit(self.project)['errors']['unexpected_pointer_type'], 1)

    def test_null_slot_is_unverified_not_falsely_fixed(self):
        self.save(self.renderer_path, self.renderer(pointer='{fileID: 0}'), self.r_guid)
        report = audit(self.project)
        self.assertEqual(report['counts']['null_slots_unverified'], 1)
        self.assertFalse(report['all_material_slots_authenticated'])

    def test_builtin_slot_is_unverified_not_falsely_fixed(self):
        self.save(self.renderer_path, self.renderer(pointer='{fileID: 10303, guid: 0000000000000000e000000000000000, type: 0}'), self.r_guid)
        report = audit(self.project)
        self.assertEqual(report['counts']['builtin_slots_unverified'], 1)
        self.assertFalse(report['all_material_slots_authenticated'])

    def test_local_embedded_material_link(self):
        self.save(self.renderer_path, self.renderer(pointer='{fileID: -321}') + self.material('-321'), self.r_guid)
        self.assertEqual(audit(self.project)['counts']['verified_local_material_references'], 1)

    def test_unrelated_mono_materials_field_ignored(self):
        extra = '--- !u!114 &99\nMonoBehaviour:\n  m_Materials:\n  - {fileID: 9}\n'
        self.save(self.renderer_path, self.renderer(extras=extra), self.r_guid)
        self.assertTrue(audit(self.project)['local_reference_structure_valid'])

    def test_known_renderer_class_and_type_must_agree(self):
        self.save(self.renderer_path, self.renderer(header='--- !u!137 &123\nMeshRenderer:\n'), self.r_guid)
        with self.assertRaises(LinkError):
            audit(self.project)

    def test_duplicate_material_field_refused(self):
        self.save(self.renderer_path, self.renderer(extras='  m_Materials: []\n'), self.r_guid)
        with self.assertRaises(LinkError):
            audit(self.project)

    def test_malformed_pointer_refused(self):
        with self.assertRaises(LinkError):
            parse_pointer('{fileID: 1, guid: BOGUS, type: 2}')
        with self.assertRaises(LinkError):
            parse_pointer('{fileID: 1, fileID: 1}')

    def test_missing_meta_refused(self):
        Path(str(self.renderer_path) + '.meta').unlink()
        with self.assertRaises(LinkError):
            audit(self.project)

    def test_duplicate_anchor_refused(self):
        self.save(self.material_path, self.material('2100000') + self.material('2100000'), self.m_guid)
        with self.assertRaises(LinkError):
            audit(self.project)

    def test_duplicate_guids_refused(self):
        Path(str(self.renderer_path) + '.meta').write_text('guid: ' + self.m_guid + '\n')
        with self.assertRaises(LinkError):
            audit(self.project)

    def test_symlink_refused(self):
        (self.assets / 'danger.asset').symlink_to(self.material_path)
        with self.assertRaises(LinkError):
            audit(self.project)

    def test_non_yaml_material_refused(self):
        self.material_path.write_bytes(b'BIN\x00material')
        with self.assertRaises(LinkError):
            audit(self.project)

    def test_report_is_aggregate_only_and_no_mutations(self):
        before = hashlib.sha256(self.material_path.read_bytes() + self.renderer_path.read_bytes()).hexdigest()
        report = audit(self.project)
        after = hashlib.sha256(self.material_path.read_bytes() + self.renderer_path.read_bytes()).hexdigest()
        self.assertEqual(before, after)
        self.assertNotIn(self.m_guid, json.dumps(report))
        self.assertEqual(report['changes_to_export'], 0)


if __name__ == '__main__':
    unittest.main()
