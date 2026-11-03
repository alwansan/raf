"""A13 read-only original PPtr model negative controls; no assets or Unity."""
import unittest
from scripts.probe_a13_material_shader_links import pointer_kind, summarize


class OriginalShaderLinksTests(unittest.TestCase):
    @staticmethod
    def shader(owner='resources.assets', path_id=8):
        return owner, path_id

    @staticmethod
    def mat(owner='resources.assets', path_id=10, file_id=0, target=8):
        return owner, path_id, {'m_FileID': file_id, 'm_PathID': target}

    def test_internal_material_link_is_resolved_by_exact_owner(self):
        result = summarize([self.shader()], [self.mat()])
        self.assertEqual(result['internal_resolved'], 1)
        self.assertEqual(result['referenced_distinct_local_shader_objects'], 1)
        self.assertFalse(result['failed_native_full_export_examined'])

    def test_two_materials_same_shader_have_distinct_and_multiplicity_counts(self):
        result = summarize([self.shader()], [self.mat(), self.mat(path_id=11)])
        self.assertEqual(result['referenced_distinct_local_shader_objects'], 1)
        self.assertEqual(result['max_materials_per_local_shader'], 2)

    def test_cross_owner_path_id_must_never_resolve(self):
        result = summarize([self.shader()], [self.mat(owner='sharedassets0.assets')])
        self.assertEqual(result['internal_unresolved'], 1)
        self.assertEqual(result.get('internal_resolved', 0), 0)

    def test_external_file_id_with_matching_path_id_stays_unresolved(self):
        result = summarize([self.shader()], [self.mat(file_id=1)])
        self.assertEqual(result['shader_reference_external_unresolved'], 1)
        self.assertEqual(result.get('internal_resolved', 0), 0)

    def test_null_pointer_is_not_a_shader_reference(self):
        result = summarize([self.shader()], [self.mat(file_id=0, target=0)])
        self.assertEqual(result['shader_reference_null'], 1)
        self.assertEqual(result.get('internal_resolved', 0), 0)

    def test_missing_pointer_field_and_extra_field_rejected(self):
        for bad in (None, {'m_FileID': 0}, {'m_FileID': 0, 'm_PathID': 8, 'extra': 9}):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'schema'):
                summarize([self.shader()], [('resources.assets', 10, bad)])

    def test_invalid_pointer_fields_fail_closed(self):
        for file_id, target in ((-1, 8), (0, -8), (True, 8), (0, False), (1, 0)):
            with self.subTest(file_id=file_id, target=target), self.assertRaisesRegex(ValueError, 'Invalid|Malformed'):
                pointer_kind({'m_FileID': file_id, 'm_PathID': target})

    def test_duplicate_shader_id_same_owner_fails(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate original Shader'):
            summarize([self.shader(), self.shader()], [self.mat()])

    def test_duplicate_material_id_same_owner_fails(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate original Material'):
            summarize([self.shader()], [self.mat(), self.mat()])

    def test_empty_inventory_fails(self):
        with self.assertRaisesRegex(ValueError, 'No original Shader'):
            summarize([], [self.mat()])
        with self.assertRaisesRegex(ValueError, 'No original Material'):
            summarize([self.shader()], [])

    def test_unknown_owner_or_negative_id_fails(self):
        with self.assertRaisesRegex(ValueError, 'Invalid original Shader'):
            summarize([self.shader('unverified.assets')], [self.mat()])
        with self.assertRaisesRegex(ValueError, 'Invalid original Material'):
            summarize([self.shader()], [self.mat(path_id=-12)])

    def test_no_original_shader_names_or_identifiers_in_report(self):
        report = summarize([self.shader()], [self.mat()])
        self.assertNotIn('m_Shader', str(report))
        self.assertNotIn('m_PathID', str(report))
        self.assertNotIn('original shader', str(report).lower())
        self.assertTrue(report['two_owner_scope_only'])


if __name__ == '__main__':
    unittest.main()
