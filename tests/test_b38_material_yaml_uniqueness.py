"""B38 independent duplicate-YAML-key regression: synthetic data only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.b05_verify_material_texenv_bindings import exported_texenvs

GUID = 'a' * 32
TEX = 'b' * 32


def yaml_file(root, material):
    assets = Path(root) / 'Assets'
    assets.mkdir()
    path = assets / 'fixture.mat'
    path.write_text('%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n' + material, encoding='utf-8')
    (assets / 'fixture.mat.meta').write_text('fileFormatVersion: 2\nguid: ' + GUID + '\n', encoding='utf-8')
    return path


SLOT = ('    - _MainTex:\n'
        '        m_Texture: {fileID: 2800000, guid: ' + TEX + ', type: 3}\n'
        '        m_Scale: {x: 1, y: 1}\n'
        '        m_Offset: {x: 0, y: 0}\n')


class MaterialYamlUniqueness(unittest.TestCase):
    def assert_rejected(self, contents):
        with TemporaryDirectory() as tmp:
            yaml_file(tmp, contents)
            with self.assertRaisesRegex(ValueError, 'Duplicate exported Material YAML mapping key'):
                exported_texenvs(Path(tmp))

    def test_valid_material_is_unchanged(self):
        with TemporaryDirectory() as tmp:
            yaml_file(tmp, '  m_SavedProperties:\n    m_TexEnvs:\n' + SLOT)
            actual = exported_texenvs(Path(tmp))
            self.assertEqual(actual[(2100000, GUID)]['_MainTex'],
                             ((2800000, TEX, 3), (1., 1., 0., 0.)))

    def test_duplicate_top_level_saved_properties_is_rejected(self):
        self.assert_rejected('  m_SavedProperties:\n    m_TexEnvs: []\n'
                             '  m_SavedProperties:\n    m_TexEnvs:\n' + SLOT)

    def test_duplicate_saved_texenv_container_is_rejected(self):
        self.assert_rejected('  m_SavedProperties:\n    m_TexEnvs: []\n'
                             '    m_TexEnvs:\n' + SLOT)

    def test_duplicate_texture_slot_is_rejected_by_existing_normalizer(self):
        # Two list entries are not duplicate YAML *mapping* keys; the existing
        # slot normalizer rightly rejects the duplicate property name.
        with TemporaryDirectory() as tmp:
            yaml_file(tmp, '  m_SavedProperties:\n    m_TexEnvs:\n' + SLOT + SLOT)
            with self.assertRaisesRegex(ValueError, 'Malformed or duplicate Material texture slot'):
                exported_texenvs(Path(tmp))

    def test_duplicate_nested_texture_pointer_key_is_rejected(self):
        s = SLOT.replace('fileID: 2800000,', 'fileID: 0, fileID: 2800000,')
        self.assert_rejected('  m_SavedProperties:\n    m_TexEnvs:\n' + s)

    def test_duplicate_uv_vector_component_is_rejected(self):
        s = SLOT.replace('m_Scale: {x: 1, y: 1}', 'm_Scale: {x: 2, x: 1, y: 1}')
        self.assert_rejected('  m_SavedProperties:\n    m_TexEnvs:\n' + s)

    def test_duplicate_material_root_is_rejected(self):
        # Parses only the Material document, never silently overwrites it.
        self.assert_rejected('  m_SavedProperties:\n    m_TexEnvs:\n' + SLOT +
                             'Material:\n  m_SavedProperties:\n    m_TexEnvs:\n' + SLOT)


if __name__ == '__main__':
    unittest.main()
