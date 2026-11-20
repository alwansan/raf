"""Native builds must consume the accepted same-export shader recovery chain."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/raft-unity-editor-android-import.yml'
GROUPS = ('30', '23', '18', '17', '15', '11', '10p33', '10p31', '7p11', '7p33')


def steps():
    document = yaml.safe_load(WORKFLOW.read_text())
    return [step for job in document['jobs'].values() for step in job.get('steps', [])]


class NativeAcceptedPost23Tests(unittest.TestCase):
    def test_each_accepted_group_compiles_verifies_and_installs_before_player(self):
        all_steps = steps()
        last = -1
        for group in GROUPS:
            marker = 'python3 -m scripts.gt_install_next' + group + '_original_shader48'
            matching = [(i, s) for i, s in enumerate(all_steps) if marker in s.get('run', '')]
            self.assertEqual(len(matching), 1, f'missing native install for NEXT{group}')
            index, install = matching[0]
            self.assertGreater(index, last)
            self.assertNotIn('continue-on-error', install)
            self.assertIn('--trace "$RUNNER_TEMP/private-export-lineage.json"', install['run'])
            self.assertIn('--project "$RUNNER_TEMP/project/ExportedProject"', install['run'])
            self.assertIn('--receipt ', install['run'])
            segment = all_steps[last + 1:index]
            builders = [s for s in segment if s.get('uses') == 'game-ci/unity-builder@v4']
            self.assertTrue(builders)
            builder = builders[-1]
            self.assertNotIn('continue-on-error', builder)
            self.assertEqual(builder['with']['dockerMemoryLimit'], '12g')
            self.assertEqual(builder['with']['customParameters'], '-job-worker-count 2')
            self.assertEqual(builder['with']['targetPlatform'], 'Android')
            self.assertNotEqual(builder['with']['projectPath'], 'unity-candidate')
            self.assertTrue(any('scripts.gt_verify_921_shader_bundle' in s.get('run', '') for s in segment))
            last = index
        self.assertTrue(any('Build()' in s.get('run', '') or 'RaftAndroid.Editor.AndroidNativeBuild.Build' in str(s) for s in all_steps[last + 1:]))

    def test_real_censuses_keep_333_then_246_then_98_and_yaml_hash_guards(self):
        all_steps = steps()
        post9 = next((i for i,s in enumerate(all_steps) if s.get('name') == 'GT record strict native post9 shader census and protected YAML baseline'), -1)
        post13 = next((i for i,s in enumerate(all_steps) if s.get('name') == 'GT record strict native post13 shader census'), -1)
        particle = next(i for i,s in enumerate(all_steps) if s.get('name') == 'Recover original Particle108 ShaderLab from ZIP2 for the native export')
        self.assertGreater(post9, -1)
        self.assertLess(post9, particle)
        self.assertLess(particle, post13)
        self.assertIn('==333', all_steps[post9]['run'])
        self.assertIn('==246', all_steps[post13]['run'])
        final = next(s for s in all_steps if s.get('name', '').startswith('Audit real post23 original custom material programs'))
        self.assertNotIn('continue-on-error', final)
        self.assertIn('assert sha==before', final['run'])
        self.assertIn('["material_docs_using_dummy_Shader"]==98', final['run'])
        self.assertIn('["material_docs_using_non_dummy_Shader"]==688', final['run'])
        self.assertIn('["material_docs_with_unknown_or_broken_Shader"]==0', final['run'])

    def test_next_chain_uses_fresh_all82_pristine_owners(self):
        all_steps = steps()
        stage = next((i for i, s in enumerate(all_steps)
                      if s.get('name') == 'Stage all 82 pristine ZIP2 owners for remaining original shader recovery'), None)
        self.assertIsNotNone(stage, '14 W1 shader owners cannot satisfy NEXT all82 gather')
        run = all_steps[stage]['run']
        self.assertIn('python3 -m scripts.gt_stage_serialized_owners', run)
        self.assertIn('--source zip2-original/Raft/Raft_Data', run)
        self.assertIn('--destination "$RUNNER_TEMP/gt-native-remaining-original/Raft_Data"', run)
        self.assertIn('all_82_serialized_owners', run)
        self.assertIn('selected_owners"]==82', run)
        for group in GROUPS:
            install = next(s for s in all_steps if 'python3 -m scripts.gt_install_next' + group + '_original_shader48' in s.get('run', ''))
            self.assertGreater(all_steps.index(install), stage)
            self.assertIn('--original "$RUNNER_TEMP/gt-native-remaining-original"', install['run'])
            translate = next(s for s in all_steps if 'scripts.gt_translate_next_remaining_' + group + '_shader48' in s.get('run', ''))
            self.assertIn('--original "$RUNNER_TEMP/gt-native-remaining-original/Raft_Data"', translate['run'])
        cleanup = next(s for s in all_steps if 'rm -rf -- "$RUNNER_TEMP/gt-native-remaining-original"' in s.get('run', ''))
        self.assertEqual(cleanup.get('if'), 'always()')
        final = next(s for s in all_steps if s.get('name', '').startswith('Audit real post23'))
        self.assertGreater(all_steps.index(cleanup), all_steps.index(final))

    def test_each_private_validation_project_is_scrubbed_even_on_failure(self):
        all_steps = steps()
        for group in GROUPS:
            project = f'gt-next{group}-full-export-unity'
            cleanup = [s for s in all_steps if 'sudo rm -rf -- "$GITHUB_WORKSPACE/' + project + '"' in s.get('run', '')]
            self.assertEqual(len(cleanup), 1, project)
            self.assertEqual(cleanup[0].get('if'), 'always()')
        text = WORKFLOW.read_text()
        for stale in ('gt-project/ExportedProject', 'gt-private-export-lineage.json', '.gt-zip2'):
            self.assertNotIn(stale, text)

    def test_new_receipt_uploads_never_publish_original_programs(self):
        for step in steps():
            if step.get('uses') != 'actions/upload-artifact@v4' or not any('next' + group + '-' in step.get('with', {}).get('name', '') for group in GROUPS):
                continue
            for path in step['with']['path'].splitlines():
                self.assertTrue(path.endswith('.json'), path)

if __name__ == '__main__':
    unittest.main()
