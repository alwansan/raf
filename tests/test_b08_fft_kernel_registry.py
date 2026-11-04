"""B08 source-free FFT kernel name/compiled-slot identity tests."""
import unittest
from scripts.b08_probe_fft_kernel_registry import (
    summarize_kernel_registry, verify_registry_with_compiled_report,
)


def fixture(names=None):
    if names is None:
        names = ['shared'] * 20
    return {'variants': [{'kernels': [
        {'name': name, 'globalKeywords': [], 'localKeywords': [],
         'variantMap': [(1, {'a': 1})]}
        for name in names]}]}


def compiled():
    return {'original_compiled_program_order_sha256_correlated': True,
            'authentic_compiled_variants_verified_in_original_order': 20,
            'unity_runtime_kernel_index_mapping_verified': False,
            'ordered_compiled_programs': [
                {'compiled_variant_position': i,
                 'original_runtime_kernel_index_proven': False}
                for i in range(20)]}


class Registry(unittest.TestCase):
    def test_one_name_twenty_slots_not_twenty_runtime_ids(self):
        result = summarize_kernel_registry(fixture())
        self.assertEqual(result['kernel_name_alias_group_sizes'], [20])
        self.assertEqual(result['aliased_compiled_positions'], [list(range(20))])
        self.assertFalse(result['compiled_entry_position_is_runtime_kernel_id'])
        self.assertFalse(result['unity_findkernel_name_to_runtime_id_verified'])
        self.assertNotIn('shared', str(result))

    def test_unique_names_still_do_not_prove_runtime_mapping(self):
        r = summarize_kernel_registry(fixture(['k' + str(i) for i in range(20)]))
        self.assertTrue(r['all_compiled_names_unique'])
        self.assertEqual(r['aliased_compiled_positions'], [])
        self.assertFalse(r['unity_runtime_kernel_id_to_program_verified'])

    def test_partial_name_alias_positions(self):
        names = ['a'] * 3 + ['b'] * 2 + ['x' + str(i) for i in range(15)]
        r = summarize_kernel_registry(fixture(names))
        self.assertEqual(r['kernel_name_alias_group_sizes'][:2], [3, 2])
        self.assertEqual(r['aliased_compiled_positions'], [[0, 1, 2], [3, 4]])

    def test_missing_name_refused(self):
        tree = fixture()
        del tree['variants'][0]['kernels'][0]['name']
        with self.assertRaises(ValueError):
            summarize_kernel_registry(tree)

    def test_bad_variant_map_refused(self):
        tree = fixture()
        tree['variants'][0]['kernels'][0]['variantMap'] = []
        with self.assertRaises(ValueError):
            summarize_kernel_registry(tree)

    def test_bad_keyword_bundle_refused(self):
        tree = fixture()
        tree['variants'][0]['kernels'][0]['localKeywords'] = 'bad'
        with self.assertRaises(ValueError):
            summarize_kernel_registry(tree)

    def test_unexpected_compiled_count_refused(self):
        with self.assertRaises(ValueError):
            summarize_kernel_registry(fixture(['single']))

    def test_verified_original_compiled_join(self):
        r = verify_registry_with_compiled_report(
            summarize_kernel_registry(fixture()), compiled())
        self.assertTrue(r['same_slot_compiled_bytecode_sha_verified'])
        self.assertFalse(r['unity_gpu_or_android_tested'])

    def test_unverified_runtime_mapping_never_accepted(self):
        c = compiled()
        c['unity_runtime_kernel_index_mapping_verified'] = True
        with self.assertRaises(ValueError):
            verify_registry_with_compiled_report(
                summarize_kernel_registry(fixture()), c)

    def test_reordered_compiled_slots_refused(self):
        c = compiled()
        c['ordered_compiled_programs'][1]['compiled_variant_position'] = 5
        with self.assertRaises(ValueError):
            verify_registry_with_compiled_report(
                summarize_kernel_registry(fixture()), c)

    def test_fake_per_slot_runtime_id_proof_refused(self):
        c = compiled()
        c['ordered_compiled_programs'][4]['original_runtime_kernel_index_proven'] = True
        with self.assertRaises(ValueError):
            verify_registry_with_compiled_report(
                summarize_kernel_registry(fixture()), c)


if __name__ == '__main__':
    unittest.main()
