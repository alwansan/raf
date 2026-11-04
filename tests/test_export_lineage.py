import copy
from pathlib import Path
import tempfile
import unittest

from scripts.verify_export_lineage import check, actual_graph


class ExportLineageTests(unittest.TestCase):
    def fixture(self):
        # Two distinct shaders remain distinct even if all name-based keys agree.
        ids = [('owner.assets', 1), ('owner.assets', 2)]
        ptrs = [(4800000, '1' * 32, '3'), (4800000, '2' * 32, '3')]
        rows, actual, edges = [], {}, {}
        for n in range(2):
            source = ('owner.assets', 10 + n)
            target = (2100000, str(n + 3) * 32, '3')
            edges[source] = ids[n]
            actual[target] = ptrs[n]
            rows.append({'class_id': 21, 'source': {'owner': source[0], 'path_id': source[1]},
                         'exportable': True,
                         'export': dict(zip(('file_id', 'guid', 'type'), (target[0], target[1], 3))),
                         'shader_source': {'owner': ids[n][0], 'path_id': ids[n][1]},
                         'shader_export': dict(zip(('file_id', 'guid', 'type'), (ptrs[n][0], ptrs[n][1], 3)))})
            rows.append({'class_id': 48, 'source': {'owner': ids[n][0], 'path_id': ids[n][1]},
                         'exportable': True, 'export': rows[-1]['shader_export']})
        return {'schema_version': 1, 'export_instance': 'a' * 32, 'objects': rows}, edges, set(ids), actual

    def test_two_distinct_objects_and_edges_preserved(self):
        result = check(*self.fixture())
        self.assertEqual(result['source_shader_objects_traced'], 2)
        self.assertTrue(result['original_exported_material_shader_assignments_verified'])
        self.assertFalse(result['shader_program_equivalence_verified'])

    def test_changed_source_edge_rejected(self):
        trace, edges, shaders, actual = self.fixture()
        trace['objects'][0]['shader_source']['path_id'] = 2
        with self.assertRaisesRegex(ValueError, 'PPtr changed'):
            check(trace, edges, shaders, actual)

    def test_swapped_actual_guid_rejected(self):
        trace, edges, shaders, actual = self.fixture()
        keys = list(actual)
        actual[keys[0]] = actual[keys[1]]
        with self.assertRaisesRegex(ValueError, 'Actual YAML'):
            check(trace, edges, shaders, actual)

    def test_serialized_reference_type_still_identifies_exported_document(self):
        # DefaultYamlExporter records AssetType.Serialized (2) for materials
        # while the YAML document is identified by anchor + meta GUID; the
        # document carries no type of its own.
        trace, edges, shaders, actual = self.fixture()
        for row in trace['objects']:
            if row['class_id'] == 21:
                row['export']['type'] = 2
        result = check(trace, edges, shaders, actual)
        self.assertEqual(result['source_material_edges_verified'], 2)
        self.assertTrue(result['original_exported_material_shader_assignments_verified'])

    def test_cached_reference_type_is_rejected(self):
        trace, edges, shaders, actual = self.fixture()
        trace['objects'][0]['export']['type'] = 1
        with self.assertRaisesRegex(ValueError, 'reference type'):
            check(trace, edges, shaders, actual)

    def test_omitted_original_shader_rejected(self):
        trace, edges, shaders, actual = self.fixture()
        trace['objects'].pop()
        with self.assertRaisesRegex(ValueError, 'omitted'):
            check(trace, edges, shaders, actual)

    def test_distinct_custom_shaders_cannot_share_export_pointer(self):
        trace, edges, shaders, actual = self.fixture()
        trace['objects'][3]['export'] = copy.deepcopy(trace['objects'][1]['export'])
        with self.assertRaisesRegex(ValueError, 'collapsed'):
            check(trace, edges, shaders, actual)

    def test_material_pointer_must_match_traced_shader_object(self):
        trace, edges, shaders, actual = self.fixture()
        trace['objects'][0]['shader_export'] = copy.deepcopy(trace['objects'][3]['export'])
        with self.assertRaisesRegex(ValueError, 'traced source Shader'):
            check(trace, edges, shaders, actual)

    def test_implicit_font_requires_original_bytes_and_actual_importer(self):
        trace, edges, shaders, actual = self.fixture()
        row = trace['objects'][0]
        row['collection_type'] = 'AssetRipper.Export.UnityProjects.Miscellaneous.FontAssetExportCollection'
        row['font_source'] = {'owner': 'owner.assets', 'path_id': 50}
        row['font_export'] = {'file_id': 12800000, 'guid': '3' * 32, 'type': 3}
        row['font_data_sha256'] = 'f' * 64
        del actual[(2100000, '3' * 32, '3')]
        fonts = {(12800000, '3' * 32, '3'): 'f' * 64}
        original = {('owner.assets', 50): 'f' * 64}
        result = check(trace, edges, shaders, actual, fonts, original)
        self.assertEqual(result['original_font_importer_materials_verified'], 1)
        self.assertFalse(result['font_importer_runtime_shader_assignment_verified'])
        fonts[(12800000, '3' * 32, '3')] = 'e' * 64
        with self.assertRaisesRegex(ValueError, 'original font bytes'):
            check(trace, edges, shaders, actual, fonts, original)

    def test_mixed_instance_duplicate_source_rejected(self):
        trace, edges, shaders, actual = self.fixture()
        trace['objects'].append(copy.deepcopy(trace['objects'][0]))
        with self.assertRaisesRegex(ValueError, 'multiple export collections'):
            check(trace, edges, shaders, actual)

    def test_embedded_font_material_uses_parent_meta_guid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'Assets').mkdir()
            font = root / 'Assets/font.asset'
            font.write_text('%YAML 1.1\n--- !u!128 &12800000\nFont:\n  m_Name: font\n--- !u!21 &-456\nMaterial:\n  m_Shader: {fileID: 4800000, guid: ' + '1' * 32 + ', type: 3}\n')
            Path(str(font) + '.meta').write_text('fileFormatVersion: 2\nguid: ' + '3' * 32 + '\n')
            self.assertEqual(actual_graph(root), {(-456, '3' * 32, '3'): (4800000, '1' * 32, '3')})

    def test_duplicate_actual_guid_and_fileid_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'Assets').mkdir()
            for name in ('a', 'b'):
                mat = root / 'Assets' / (name + '.mat')
                mat.write_text('%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n  m_Shader: {fileID: 4800000, guid: ' + '1' * 32 + ', type: 3}\n')
                Path(str(mat) + '.meta').write_text('guid: ' + '3' * 32 + '\n')
            with self.assertRaisesRegex(ValueError, 'Duplicate actual'):
                actual_graph(root)


if __name__ == '__main__':
    unittest.main()
