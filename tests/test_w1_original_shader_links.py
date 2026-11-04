import unittest
from scripts.w1_probe_original_shader_links import resolve_pointer, duplicate_groups, link_materials


class OriginalShaderLinks(unittest.TestCase):
    def setUp(self):
        self.key = ('private-name', ('_Color',))
        self.rows = {('one.assets', 1): {'key': self.key, 'payload_sha256': 'a' * 64,
                     'parsed_form_sha256': 'b' * 64, 'program_set_sha256': 'c' * 64},
                     ('two.assets', 1): {'key': self.key, 'payload_sha256': 'd' * 64,
                     'parsed_form_sha256': 'b' * 64, 'program_set_sha256': 'c' * 64}}

    def test_one_based_external_index_and_local_negative_pathid(self):
        self.assertEqual(resolve_pointer('local', ['archive:/first.assets', 'folder\\two.assets'],
                         {'m_FileID': 1, 'm_PathID': 8}), ('first.assets', 8))
        self.assertEqual(resolve_pointer('local', ['archive:/first.assets', 'folder\\two.assets'],
                         {'m_FileID': 2, 'm_PathID': 8}), ('two.assets', 8))
        self.assertEqual(resolve_pointer('local', [], {'m_FileID': 0, 'm_PathID': -1}), ('local', -1))

    def test_null_and_out_of_range_boolean_invalid_owner_controls(self):
        self.assertIsNone(resolve_pointer('local', [], {'m_FileID': 0, 'm_PathID': 0}))
        for pointer in ({'m_FileID': 1, 'm_PathID': 5}, {'m_FileID': -1, 'm_PathID': 5},
                        {'m_FileID': True, 'm_PathID': 5}, {'m_FileID': 0, 'm_PathID': True}):
            with self.assertRaises(ValueError):
                resolve_pointer('local', [], pointer)
        with self.assertRaises(ValueError):
            resolve_pointer('local', ['bad\x00owner'], {'m_FileID': 1, 'm_PathID': 5})

    def test_duplicate_key_preserves_distinct_original_objects_and_private_names(self):
        group = duplicate_groups(self.rows)[0]
        self.assertEqual(group['original_objects'], 2)
        self.assertEqual(group['distinct_serialized_payloads'], 2)
        self.assertTrue(group['byte_identical_parsed_forms_and_programs'])
        self.assertNotIn('private-name', str(group))
        self.assertNotIn('one.assets', str(group))
        self.assertEqual(len(set(m['object_identity_digest'] for m in group['member_fingerprints'])), 2)

    def test_changed_program_or_pass_state_is_not_equivalent(self):
        self.rows[('two.assets', 1)]['program_set_sha256'] = 'e' * 64
        self.assertFalse(duplicate_groups(self.rows)[0]['byte_identical_parsed_forms_and_programs'])
        self.rows[('two.assets', 1)]['program_set_sha256'] = 'c' * 64
        self.rows[('two.assets', 1)]['parsed_form_sha256'] = 'e' * 64
        self.assertFalse(duplicate_groups(self.rows)[0]['byte_identical_parsed_forms_and_programs'])

    def test_original_material_edges_not_collapsed_by_shader_name(self):
        materials = [('one.assets', [], {'m_FileID': 0, 'm_PathID': 1}),
                     ('one.assets', ['two.assets'], {'m_FileID': 1, 'm_PathID': 1}),
                     ('one.assets', ['two.assets'], {'m_FileID': 1, 'm_PathID': 1})]
        counts, refs, objects = link_materials(materials, self.rows, {self.key: [('extra', 46)]})
        self.assertEqual(counts['original_material_refs_to_engine_keys'], 3)
        self.assertEqual(refs[('extra', 46)], 3)
        self.assertEqual(objects[('one.assets', 1)], 1)
        self.assertEqual(objects[('two.assets', 1)], 2)

    def test_missing_owner_and_null_edges_remain_unresolved(self):
        materials = [('absent.assets', [], {'m_FileID': 0, 'm_PathID': 1}),
                     ('one.assets', [], {'m_FileID': 0, 'm_PathID': 0})]
        counts, refs, objects = link_materials(materials, self.rows, {})
        self.assertEqual(counts['shader_refs_outside_authenticated_shader_objects'], 1)
        self.assertEqual(counts['null_shader_refs'], 1)
        self.assertFalse(refs)
        self.assertFalse(objects)

    def test_unresolved_sources_are_classified_without_fabricating_shader_links(self):
        materials = [('one.assets', [], {'m_FileID': 0, 'm_PathID': 99})]
        for owner in ('unity_builtin_extra', 'unity default resources', 'One.assets', 'unknown.assets'):
            materials.append(('one.assets', [owner], {'m_FileID': 1, 'm_PathID': 1}))
        counts, refs, objects = link_materials(materials, self.rows, {})
        self.assertEqual(counts['shader_refs_outside_authenticated_shader_objects'], 5)
        self.assertEqual(counts['shader_refs_to_known_owner_missing_shader_object'], 1)
        self.assertEqual(counts['shader_refs_to_engine_resource_owner_not_loaded'], 2)
        self.assertEqual(counts['shader_refs_with_owner_case_mismatch'], 1)
        self.assertEqual(counts['shader_refs_to_other_owner_not_loaded'], 1)
        self.assertFalse(refs)
        self.assertFalse(objects)


if __name__ == '__main__':
    unittest.main()
