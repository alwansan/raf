import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.b44_verify_material_colors import compare, exported_colors, normalize_colors, ENGINE, FONT_COLLECTION


def color(r=0.12, g=0.5, b=1., a=1.):
    return dict(r=r, g=g, b=b, a=a)


def fixture():
    ident = ('original.assets', 12)
    ptr = (2100000, 'a'*32)
    source = {ident: {'_Tint': (0.12, 0.5, 1., 1.)}}
    actual = {ptr: {'_Tint': (0.12, 0.5, 1., 1.)}}
    row = dict(class_id=21, source=dict(owner=ident[0], path_id=ident[1]),
               export=dict(file_id=ptr[0], guid=ptr[1], type=2), exportable=True)
    return dict(schema_version=1, export_instance='b'*32, objects=[row]), source, actual


class MaterialColorsTests(unittest.TestCase):
    def test_positive_identity_and_nonidentity(self):
        t, s, a = fixture()
        result = compare(t, s, a)
        self.assertEqual(result['color_slots_compared'], 1)
        self.assertEqual(result['materials_with_original_nonidentity_colors'], 1)
        self.assertTrue(result['original_material_color_values_preserved'])
        self.assertFalse(result['shader_program_or_device_fidelity_verified'])
        self.assertNotIn('_Tint', json.dumps(result))
        self.assertNotIn('0.12', json.dumps(result))

    def test_wrong_color_and_dropped_color(self):
        t, s, a = fixture()
        a[(2100000, 'a'*32)]['_Tint'] = (1., 1., 1., 1.)
        result = compare(t, s, a)
        self.assertEqual(result['changed_color_values'], 1)
        self.assertFalse(result['original_material_color_values_preserved'])
        a[(2100000, 'a'*32)] = {}
        self.assertEqual(compare(t, s, a)['missing_color_slots'], 1)

    def test_unexpected_color_and_wrong_material(self):
        t, s, a = fixture()
        a[(2100000, 'a'*32)]['_Extra'] = (1, 1, 1, 1)
        self.assertEqual(compare(t, s, a)['unexpected_color_slots'], 1)
        with self.assertRaisesRegex(ValueError, 'identities differ'):
            compare(t, s, {(2100000, 'c'*32): {}})

    def test_float_rounding_and_large_hdr(self):
        t, s, a = fixture()
        s[('original.assets', 12)]['_Tint'] = (9.1234567, -0.1, 0.5, 1.)
        a[(2100000, 'a'*32)]['_Tint'] = (9.12346, -.10000002, .5, 1.)
        self.assertTrue(compare(t, s, a)['original_material_color_values_preserved'])
        a[(2100000, 'a'*32)]['_Tint'] = (9.2, -.1, .5, 1.)
        self.assertFalse(compare(t, s, a)['original_material_color_values_preserved'])

    def test_duplicate_slot_nan_or_bad_entry_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicated'):
            normalize_colors([('_Tint', color()), ('_Tint', color())])
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            normalize_colors([('_Tint', color(float('nan')))])
        with self.assertRaisesRegex(ValueError, 'RGBA'):
            normalize_colors([('_Tint', dict(r=1, g=1, b=1))])
        with self.assertRaisesRegex(ValueError, 'shape'):
            normalize_colors([{'bad': 10}])

    def test_source_and_export_dict_shapes(self):
        expected = {'_Tint': (.12, .5, 1., 1.)}
        self.assertEqual(normalize_colors([{'m_First': '_Tint', 'm_Second': color()}]), expected)
        self.assertEqual(normalize_colors([{'_Tint': color()}], exported=True), expected)

    def test_exported_yaml_color_property_map_without_original_relaxation(self):
        actual={'_Tint':color()}
        self.assertEqual(normalize_colors(actual,exported=True),
                         {'_Tint':(.12,.5,1.,1.)})
        self.assertEqual(normalize_colors({},exported=True),{})
        with self.assertRaisesRegex(ValueError, 'array'):
            normalize_colors(actual)
        with self.assertRaisesRegex(ValueError, 'Malformed or duplicated'):
            normalize_colors({19:color()},exported=True)
        with self.assertRaisesRegex(ValueError, 'RGBA'):
            normalize_colors({'_Tint':dict(r=1,g=1,b=1)},exported=True)

    def test_exported_yaml_color_mapping_actual_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            assets=Path(tmp)/'Assets';assets.mkdir()
            path=assets/'material.mat'
            path.write_text('%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n'
                            '  m_SavedProperties:\n'
                            '    m_Colors:\n'
                            '      _Tint: {r: 0.12, g: 0.5, b: 1, a: 1}\n')
            (assets/'material.mat.meta').write_text('guid: '+'a'*32+'\n')
            self.assertEqual(exported_colors(Path(tmp)),
                             {(2100000,'a'*32):{'_Tint':(.12,.5,1.,1.)}})

    def test_unpinned_selected_material_colors_refused_before_source_loading(self):
        from scripts.b44_verify_material_colors import original_colors
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'Unpinned'):
                original_colors(Path(tmp), selected_owners={'../unsafe.assets'})
            with self.assertRaisesRegex(ValueError, 'Unpinned'):
                original_colors(Path(tmp), selected_owners=set())

    def test_engine_redirect_and_font_material_are_excluded(self):
        t, s, a = fixture()
        t['objects'].append(dict(class_id=21, source=dict(owner='original.assets', path_id=13),
                                 export=dict(file_id=23, guid=next(iter(ENGINE)), type=0), exportable=False))
        t['objects'].append(dict(class_id=21, source=dict(owner='original.assets', path_id=14),
                                 export=dict(file_id=2100000, guid='c'*32, type=3),
                                 collection_type=FONT_COLLECTION, exportable=True))
        s[('original.assets', 13)] = {}
        s[('original.assets', 14)] = {}
        r = compare(t, s, a)
        self.assertEqual(r['engine_material_redirects_excluded'], 1)
        self.assertEqual(r['font_importer_materials_excluded'], 1)

    def test_mixed_duplicate_or_missing_source_rejected(self):
        t, s, a = fixture()
        t['objects'].append(copy.deepcopy(t['objects'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            compare(t, s, a)
        t['objects'] = []
        with self.assertRaisesRegex(ValueError, 'missing'):
            compare(t, s, a)

    def test_yaml_document_with_color_and_embedded_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root/'Assets'
            assets.mkdir()
            path = assets/'embedded.asset'
            path.write_text('%YAML 1.1\n--- !u!128 &12800000\nFont:\n  m_Name: safe\n--- !u!21 &2100000\nMaterial:\n  m_SavedProperties:\n    m_Colors:\n    - _Tint: {r: 0.12, g: 0.5, b: 1, a: 1}\n')
            (assets/'embedded.asset.meta').write_text('fileFormatVersion: 2\nguid: ' + 'a'*32 + '\n')
            self.assertEqual(exported_colors(root), {(2100000, 'a'*32): {'_Tint': (.12, .5, 1., 1.)}})
            path.write_text(path.read_text().replace('    m_Colors:\n', '    m_Colors: []\n'))
            with self.assertRaisesRegex(ValueError, 'Malformed exported Material YAML'):
                exported_colors(root)

    def test_duplicate_yaml_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root/'Assets'
            assets.mkdir()
            path = assets/'bad.mat'
            path.write_text('%YAML 1.1\\n--- !u!21 &2100000\\nMaterial:\\n  m_SavedProperties:\\n    m_Colors: []\\n    m_Colors: []\\n'.replace('\\n', '\n'))
            (assets/'bad.mat.meta').write_text('guid: ' + 'a'*32 + '\n')
            with self.assertRaisesRegex(ValueError, 'Duplicate YAML'):
                exported_colors(root)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'Assets').mkdir()
            (root/'Assets'/'redirect').symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                exported_colors(root)


if __name__ == '__main__':
    unittest.main()
