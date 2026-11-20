"""Source-free NEXT23b translation gates; fixtures are synthetic byte strings."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts.gt_next23b_private_stage_translation import (
    validate_topology, recover_programs, compose_private, STATUS,
)


class Next23BStageTranslation(unittest.TestCase):
    def test_topology_is_exact_observed_source_not_prior_next23(self):
        profile = dict(original_source_Shader48_pass_count=4,
                       matched_vertex_fragment_permutation_pairs=1156,
                       unmatched_vertex_permutations=0,
                       unmatched_fragment_permutations=0,
                       distinct_original_linked_D3D11_programs=134)
        validate_topology(profile)
        for key in profile:
            drift = dict(profile)
            drift[key] += 1
            with self.assertRaises(ValueError):
                validate_topology(drift)
        profile['unmatched_vertex_permutations'] = False
        with self.assertRaises(ValueError):
            validate_topology(profile)

    def test_each_distinct_program_is_translated_once_and_failures_are_not_success(self):
        distinct = {(i % 2, str(i)): dict(stage=i % 2, source_code=bytes([i]))
                    for i in range(134)}
        seen = []
        def translator(code, stage, folder):
            seen.append((code, stage))
            return dict(vulkan11_valid=True, hlsl_recovered=True,
                        roundtrip_vulkan11_valid=code != b'\x08')
        with tempfile.TemporaryDirectory() as tmp:
            refs, counters = recover_programs(distinct, Path(tmp), translator)
        self.assertEqual(len(seen), 134)
        self.assertEqual(len(refs), 134)
        self.assertEqual(counters['attempted'], 134)
        self.assertEqual(counters['roundtrip_vulkan11_valid'], 133)
        self.assertNotEqual(counters['roundtrip_vulkan11_valid'], 134)

    def test_roundtrip_alone_does_not_satisfy_all_three_gates(self):
        distinct = {(i % 2, str(i)): dict(stage=i % 2, source_code=bytes([i]))
                    for i in range(134)}
        with tempfile.TemporaryDirectory() as tmp:
            _, counts = recover_programs(distinct, Path(tmp), lambda *_: dict(
                vulkan11_valid=False, hlsl_recovered=True,
                roundtrip_vulkan11_valid=True))
        self.assertEqual(counts['all_three_valid'], 0)

    def test_workflow_publishes_only_safe_report_and_has_no_unity_build(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / '.github/workflows/raft-gt-next23b-private-stage-translation.yml').read_text()
        self.assertIn('            .github/workflows/raft-gt-next23b-private-stage-translation.yml', workflow)
        self.assertIn('cancel-in-progress: false', workflow)
        self.assertIn('gt-next23b-private-stage-safe.json', workflow)
        self.assertIn('> "$RUNNER_TEMP/gt-next23b-private-compiler.log" 2>&1', workflow)
        self.assertNotIn('game-ci/', workflow)
        self.assertNotIn('UNITY_LICENSE', workflow)
        self.assertNotIn('raft-native-build-request', workflow)

    def test_composition_failure_retains_numeric_translation_proof_without_success(self):
        report = {'status': 'TRANSLATED', 'all_three_compiler_gates_valid': 134}
        with tempfile.TemporaryDirectory() as tmp:
            compose_private({}, [], [], [], [], {}, Path(tmp), report)
        self.assertEqual(report['status'], 'INCONCLUSIVE_NEXT23B_PRIVATE_COMPOSITION')
        self.assertEqual(report['all_three_compiler_gates_valid'], 134)
        self.assertEqual(report['composition_safe_checkpoint'], 'source_keyword_routes')
        self.assertNotIn('error_message', report)

    def test_all_1156_routes_required_and_strict_binding_failure_stops_composition(self):
        module = 'scripts.gt_next23b_private_stage_translation'
        packet = [{'routes': [{'vs': (1, 'v'), 'fs': (0, 'f')} for _ in range(289)]} for _ in range(4)]
        routing = {'source_exact_keyword_routes_by_pass': [289] * 4}
        report = {'all_three_compiler_gates_valid': 134}
        with tempfile.TemporaryDirectory() as tmp, \
                patch(module + '.keyword_routes', return_value=(packet, routing)), \
                patch(module + '.compile_routed_stages', return_value=2312), \
                patch(module + '.shaderlab_layout', return_value=('layout', {})), \
                patch(module + '.stage_parameter_records', side_effect=ValueError('private member name')), \
                patch(module + '.compose') as composer:
            compose_private({'m_PropInfo': {'m_Props': []}}, [], [], [], [],
                            {(1, 'v'): 'program-0', (0, 'f'): 'program-1'}, Path(tmp), report)
            composer.assert_not_called()
        self.assertEqual(report['status'], 'INCONCLUSIVE_NEXT23B_PRIVATE_COMPOSITION')
        self.assertEqual(report['composition_safe_checkpoint'], 'source_CB_sampler_and_varying_bindings')
        self.assertNotIn('private member name', str(report))
        self.assertEqual(report['private_exact_keyword_routed_stages_compiled'], 2312)

    def test_success_requires_all_routes_bindings_and_composed_entrypoint_validation(self):
        module = 'scripts.gt_next23b_private_stage_translation'
        packet = [{'routes': [{'vs': (1, 'v'), 'fs': (0, 'f')} for _ in range(289)]} for _ in range(4)]
        named = dict(original_variant_stages_with_parameter_records=2312,
                     original_vertex_fragment_varying_records_matched=1156,
                     named_constant_buffer_reflected_offsets_verified=2312)
        report = {}
        with tempfile.TemporaryDirectory() as tmp, \
                patch(module + '.keyword_routes', return_value=(packet, {'source_exact_keyword_routes_by_pass': [289] * 4})), \
                patch(module + '.compile_routed_stages', return_value=2312), \
                patch(module + '.shaderlab_layout', return_value=('layout', {})), \
                patch(module + '.stage_parameter_records', return_value=named), \
                patch(module + '.compose', return_value='shader'), \
                patch(module + '.verify_entrypoints') as verifier:
            compose_private({'m_PropInfo': {'m_Props': []}}, [], [], [], [],
                            {(1, 'v'): 'program-0', (0, 'f'): 'program-1'}, Path(tmp), report)
            self.assertEqual(sum(map(len, verifier.call_args.kwargs['routes'])), 1156)
        self.assertEqual(report['status'], STATUS)
        self.assertEqual(report['private_ShaderLab_vertex_fragment_entrypoints_validated'], 2312)

    def test_missing_route_stops_before_any_compilation(self):
        module = 'scripts.gt_next23b_private_stage_translation'
        report = {}
        with tempfile.TemporaryDirectory() as tmp, \
                patch(module + '.keyword_routes', return_value=([], {'source_exact_keyword_routes_by_pass': [289, 289, 289, 288]})), \
                patch(module + '.compile_routed_stages') as compiler:
            compose_private({}, [], [], [], [], {}, Path(tmp), report)
            compiler.assert_not_called()
        self.assertEqual(report['status'], 'INCONCLUSIVE_NEXT23B_PRIVATE_COMPOSITION')

    def test_only_allowlisted_property_failure_category_is_public(self):
        from scripts.t3_particle108_source_propstate import PrivateContractError
        module = 'scripts.gt_next23b_private_stage_translation'
        report = {}
        with tempfile.TemporaryDirectory() as tmp, \
                patch(module + '.keyword_routes', side_effect=PrivateContractError('PROPERTY_RANGE')):
            compose_private({}, [], [], [], [], {}, Path(tmp), report)
        self.assertEqual(report['composition_safe_failure_category'], 'PROPERTY_RANGE')
        self.assertEqual(report['status'], 'INCONCLUSIVE_NEXT23B_PRIVATE_COMPOSITION')

    def test_truthy_compiler_strings_do_not_prove_translation(self):
        distinct = {(i % 2, str(i)): dict(stage=i % 2, source_code=bytes([i]))
                    for i in range(134)}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'untrusted_next23b_compiler_result'):
                recover_programs(distinct, Path(tmp), lambda *_: dict(
                    vulkan11_valid='true', hlsl_recovered=True,
                    roundtrip_vulkan11_valid=True))
        self.assertIn('PRIVATE_STAGES', STATUS)


if __name__ == '__main__':
    unittest.main()
