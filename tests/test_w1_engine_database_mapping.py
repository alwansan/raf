import unittest
from scripts.w1_match_embedded_engine_shaders import index_records, classify


class EngineDatabaseMapping(unittest.TestCase):
    def fixture(self):
        return ([{'name':'synthetic', 'properties':['a','b'], 'file_id':1, 'engine_kind':'extra'}],
                {'release_name_copy_verified':True, 'editor_name_copy_verified':True,
                 'selected_unity_version':'2021.3.45f2', 'generated_assembly_sha256':'a'*64,
                 'default_shader_records':0, 'extra_shader_records':1})

    def test_exact_name_and_properties_with_controls(self):
        rows, reader = self.fixture()
        result = classify([('synthetic',('a','b'))],index_records(rows,reader),{'synthetic'})
        self.assertEqual(result['vendor_keys_uniquely_mapped'],1)
        self.assertEqual(result['wrong_name_and_property_controls_detected'],2)

    def test_reordered_properties_unresolved(self):
        rows, reader = self.fixture()
        result = classify([('synthetic',('b','a'))],index_records(rows,reader),{'synthetic'})
        self.assertEqual(result['vendor_keys_unresolved_or_ambiguous'],1)

    def test_unverified_reader_rejected(self):
        rows, reader = self.fixture()
        reader['release_name_copy_verified'] = False
        with self.assertRaises(ValueError): index_records(rows,reader)

    def test_duplicate_pointer_rejected(self):
        rows, reader = self.fixture()
        rows.append(dict(rows[0])); reader['extra_shader_records'] = 2
        with self.assertRaises(ValueError): index_records(rows,reader)

    def test_same_key_multiple_pointers_remains_ambiguous(self):
        rows, reader = self.fixture()
        rows.append({**rows[0], 'file_id':2}); reader['extra_shader_records'] = 2
        result = classify([('synthetic',('a','b'))],index_records(rows,reader),{'synthetic'})
        self.assertEqual(result['ambiguous_engine_keys'],1)
        self.assertEqual(result['vendor_keys_unresolved_or_ambiguous'],1)


if __name__ == '__main__': unittest.main()
