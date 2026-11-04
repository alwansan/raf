import copy
import tempfile
from pathlib import Path
import unittest
from scripts.w1_verify_engine_export import (READER_PINS, exact_table, original_binding_map,
                                            verify_histogram, verify_export)


class EngineExportProof(unittest.TestCase):
    def setUp(self):
        self.key = ('OriginalShader', ('_Color',))
        self.custom = ('CustomShader', ('_Depth',))
        self.engine, self.non_engine = original_binding_map([self.key, self.custom], {self.key: [('extra', 46)]})
        self.graph = {'counts': {'internal_engine_references': 7}, 'internal_pointer_histogram': [
            {'engine_kind': 'extra', 'file_id': 46, 'references': 7}]}

    def test_actual_pointer_must_map_an_original_key(self):
        self.assertEqual(verify_histogram(self.graph, self.engine)['source_mapped_internal_references'], 7)
        for wrong in [200, 0, -1]:
            g = copy.deepcopy(self.graph)
            g['internal_pointer_histogram'][0]['file_id'] = wrong
            with self.assertRaises(ValueError):
                verify_histogram(g, self.engine)

    def test_changed_property_order_is_not_an_original_match(self):
        engine, custom = original_binding_map([('OriginalShader', ('_Other', '_Color'))],
                                             {('OriginalShader', ('_Color', '_Other')): [('extra', 46)]})
        self.assertFalse(engine)
        self.assertEqual(len(custom), 1)

    def test_ambiguous_and_duplicate_engine_original_keys_fail(self):
        with self.assertRaises(ValueError):
            original_binding_map([self.key], {self.key: [('extra', 46), ('extra', 200)]})
        with self.assertRaises(ValueError):
            original_binding_map([self.key, self.key], {self.key: [('extra', 46)]})

    def test_nameless_and_duplicate_custom_objects_are_retained_without_false_export_proof(self):
        engine, custom = original_binding_map([('', ()), self.custom, self.custom], {})
        self.assertFalse(engine)
        self.assertEqual(len(custom), 3)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                verify_export(Path(temp), self.engine, custom)

    def test_histogram_count_duplicate_kind_and_boolean_controls(self):
        for mode in ('count', 'duplicate', 'kind', 'boolean'):
            graph = copy.deepcopy(self.graph)
            if mode == 'count':
                graph['counts']['internal_engine_references'] = 8
            elif mode == 'duplicate':
                graph['internal_pointer_histogram'] *= 2
            elif mode == 'kind':
                graph['internal_pointer_histogram'][0]['engine_kind'] = 'default'
            else:
                graph['internal_pointer_histogram'][0]['references'] = True
            with self.assertRaises(ValueError):
                verify_histogram(graph, self.engine)

    def test_exact_reader_hashes_and_partition_required(self):
        rows = [{'name': 'Public%d' % i, 'properties': [], 'file_id': i,
                 'engine_kind': 'default' if i < 6 else 'extra'} for i in range(196)]
        self.assertEqual(len(exact_table(rows, READER_PINS)), 196)
        for key in ('tpk_sha256', 'dataset_json_sha256', 'generated_assembly_sha256'):
            reader = dict(READER_PINS, **{key: 'a' * 64})
            with self.assertRaises(ValueError):
                exact_table(rows, reader)
        reader = dict(READER_PINS, release_name_copy_verified=1)
        with self.assertRaises(ValueError):
            exact_table(rows, reader)
        rows[0]['engine_kind'] = 'extra'
        with self.assertRaises(ValueError):
            exact_table(rows, READER_PINS)

    def test_export_custom_identity_meta_and_internal_pointer_closure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assets = root / 'Assets'
            assets.mkdir()
            shader = assets / 'private.shader'
            shader.write_text('Shader "CustomShader" {}')
            meta = assets / 'private.shader.meta'
            meta.write_text('guid: ' + 'a' * 32 + '\n')
            mat = assets / 'private.mat'
            mat.write_text('%YAML 1.1\n--- !u!21 &21\nMaterial:\n  m_Shader: {fileID: 46, guid: 0000000000000000f000000000000000, type: 0}\n')
            before = {p.name: p.read_bytes() for p in assets.iterdir()}
            self.assertTrue(verify_export(root, self.engine, self.non_engine)['actual_export_reference_closure_verified'])
            self.assertEqual(before, {p.name: p.read_bytes() for p in assets.iterdir()})
            shader.write_text('Shader "WrongShader" {}')
            with self.assertRaises(ValueError):
                verify_export(root, self.engine, self.non_engine)
            shader.write_text('Shader "CustomShader" {}')
            meta.unlink()
            with self.assertRaises(ValueError):
                verify_export(root, self.engine, self.non_engine)


if __name__ == '__main__':
    unittest.main()
