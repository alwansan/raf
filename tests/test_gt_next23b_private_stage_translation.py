"""Source-free NEXT23b translation gates; fixtures are synthetic byte strings."""
import tempfile
from pathlib import Path
import unittest
from scripts.gt_next23b_private_stage_translation import (
    validate_topology, recover_programs, STATUS,
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
