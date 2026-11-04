"""Source-free B48 negative controls for composed FFT candidate contracts."""
import copy
import unittest
from scripts.probe_b48_fft_selector_program_compat import (
    verify_candidate_pair_contract, SOURCE_FORMULA,
)


def original_fixture():
    examples = []
    programs = []
    for bank in (0, 1):
        for n in range(5, 10):
            for stage in (0, 1):
                pos = len(programs)
                programs.append({
                    'compiled_variant_position': pos,
                    'original_runtime_kernel_index_proven': False,
                    'original_dxbc_byte_count': 1024 + pos,
                    'original_dxbc_sha256': format(pos + 1, '064x'),
                    'original_serialized_workgroup_xyz': [2 * (1 << n), 1, 1],
                })
    for n in range(5, 10):
        examples.append({'n': n, 'r': 1 << n,
                         'bank0': [(n - 5) * 2, (n - 5) * 2 + 1],
                         'bank1': [(n - 5) * 2 + 10, (n - 5) * 2 + 11]})
    seed = {'inherited_seed_dataflow_verified': True,
            'derived_second_int_forwarded_to_base_first_int': True,
            'first_pass_source_selector': SOURCE_FORMULA,
            'second_pass_relative_offset': 1,
            'unity_runtime_kernel_lookup_mapping_verified': False,
            'algebraic_examples_only': examples}
    compiled = {'authentic_compiled_variants_verified_in_original_order': 20,
                'original_compiled_program_order_sha256_correlated': True,
                'original_workgroup_mapping_correlated': True,
                'unity_runtime_kernel_index_mapping_verified': False,
                'ordered_compiled_programs': programs}
    return seed, compiled


class B48FftCandidateTests(unittest.TestCase):
    def test_20_sha_proven_compiled_slots_join_10_source_selector_pairs(self):
        seed, programs = original_fixture()
        report = verify_candidate_pair_contract(seed, programs)
        self.assertTrue(report['proven_candidate_selector_workgroup_compatibility'])
        self.assertEqual(report['source_selectors_checked'], 10)
        self.assertEqual(report['authentic_compiled_slots_checked'], 20)
        self.assertFalse(report['actual_unity_kernel_index_to_compiled_slot_proven'])
        self.assertFalse(report['native_unity_compilation_or_android_gpu_execution'])
        pairs = report['candidate_groups']
        self.assertEqual(pairs[0]['compiled_candidate_first_slot'], 0)
        self.assertEqual(pairs[8]['compiled_candidate_second_slot'], 9)
        self.assertEqual(pairs[1]['compiled_candidate_first_slot'], 10)
        self.assertEqual(pairs[-1]['compiled_candidate_second_slot'], 19)
        self.assertEqual(pairs[-1]['serialized_threads_per_group'], [1024, 1, 1])

    def test_reject_unproven_runtime_kernel_mapping(self):
        seed, programs = original_fixture()
        for field, row in ((seed, 'unity_runtime_kernel_lookup_mapping_verified'),
                           (programs, 'unity_runtime_kernel_index_mapping_verified')):
            bad = copy.deepcopy(field)
            bad[row] = True
            with self.assertRaises(ValueError):
                verify_candidate_pair_contract(bad if field is seed else seed,
                                               bad if field is programs else programs)
        programs['ordered_compiled_programs'][0]['original_runtime_kernel_index_proven'] = True
        with self.assertRaises(ValueError):
            verify_candidate_pair_contract(seed, programs)

    def test_reject_wrong_selector_bank_and_offset(self):
        seed, programs = original_fixture()
        for key, wrong in (('first_pass_source_selector', 'n-5'),
                           ('second_pass_relative_offset', 2),
                           ('derived_second_int_forwarded_to_base_first_int', False)):
            bad = copy.deepcopy(seed); bad[key] = wrong
            with self.assertRaises(ValueError): verify_candidate_pair_contract(bad, programs)
        bad = copy.deepcopy(seed); bad['algebraic_examples_only'][2]['bank1'] = [12, 13]
        with self.assertRaises(ValueError): verify_candidate_pair_contract(bad, programs)

    def test_reject_swapped_missing_or_forged_compiled_slot(self):
        seed, programs = original_fixture()
        for mutation in ('swap', 'drop', 'negative_bytes', 'wrong_position'):
            bad = copy.deepcopy(programs); p = bad['ordered_compiled_programs']
            if mutation == 'swap': p[2], p[3] = p[3], p[2]
            elif mutation == 'drop': p.pop()
            elif mutation == 'negative_bytes': p[4]['original_dxbc_byte_count'] = 0
            else: p[5]['compiled_variant_position'] = 999
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                verify_candidate_pair_contract(seed, bad)

    def test_reject_group_size_drift_in_either_bank(self):
        seed, programs = original_fixture()
        for index in (0, 1, 9, 10, 19):
            bad = copy.deepcopy(programs)
            bad['ordered_compiled_programs'][index]['original_serialized_workgroup_xyz'] = [1, 1, 1]
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, 'workgroup'):
                verify_candidate_pair_contract(seed, bad)


if __name__ == '__main__':
    unittest.main()
