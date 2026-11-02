"""Queue separation plus execution of the actual native request/result gates."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import re
import yaml

ROOT=Path(__file__).resolve().parents[1]
WORKFLOWS=ROOT/'.github/workflows'


def read(name):return yaml.safe_load((WORKFLOWS/name).read_text())
def triggers(workflow):return workflow.get('on',workflow.get(True))


class NativeWorkflowIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main=read('raft-unity-editor-android-import.yml')
        cls.preflight=read('raft-reconstruction-preflight.yml')
        cls.experiment=read('raft-unity-android-experiment.yml')

    def test_full_build_only_enters_queue_for_dedicated_request(self):
        event=triggers(self.main)
        self.assertEqual(event['push']['paths'],['.github/raft-native-build-request.json'])
        self.assertEqual(event['push']['branches'],['feature/android-native-port'])
        self.assertEqual(event['workflow_dispatch']['inputs']['build_mode']['options'],['native'])
        self.assertTrue(event['workflow_dispatch']['inputs']['publish_early_test']['default'])
        self.assertIn('workflow_call',event)

    def test_delivery_and_unit_tests_do_not_share_concurrency(self):
        for workflow in (self.main,self.preflight):
            self.assertIs(workflow['concurrency']['cancel-in-progress'],False)
            self.assertEqual(workflow['concurrency']['queue'],'max')
        self.assertNotEqual(self.main['concurrency']['group'],self.preflight['concurrency']['group'])
        self.assertIn('raft-unity-editor-android',self.main['concurrency']['group'])
        self.assertIn('raft-unity-android-experiment',self.main['concurrency']['group'])
        engine=self.main['jobs']['reconstruct']['concurrency']
        self.assertEqual(engine['group'],'raft-native-engine-${{ github.ref }}')
        self.assertIs(engine['cancel-in-progress'],False)
        self.assertEqual(engine['queue'],'max')

    def test_sidecar_is_unit_only_without_unity_or_license_environment(self):
        self.assertIn('scripts/overlay_ilspy_gameplay.py',str(triggers(self.preflight)))
        jobs=self.preflight['jobs']
        self.assertNotIn('reconstruct',jobs)
        self.assertNotIn('publish-early-test',jobs)
        self.assertNotIn('game-ci/unity-builder',str(jobs))
        self.assertNotIn('UNITY_LICENSE',str(jobs))
        self.assertNotIn('environment',jobs['source-contracts'])
        self.assertIn('lfs: false',(WORKFLOWS/'raft-reconstruction-preflight.yml').read_text())

    def test_experiment_has_dedicated_request_and_reuses_private_lane(self):
        self.assertEqual(triggers(self.experiment)['push']['paths'],['.github/raft-native-experiment-request.json'])
        job=self.experiment['jobs']['experiment']
        self.assertEqual(job['uses'],'./.github/workflows/raft-unity-editor-android-import.yml')
        self.assertEqual(job['with']['build_lane'],'experiment')
        self.assertIs(job['with']['publish_early_test'],False)
        self.assertIn('[raft-native-experiment]',job['if'])
        self.assertIn("!contains(github.event.head_commit.message, '[raft-device-test]')",job['if'])

    def run_gate(self, job, variables, request=None, experiment=False):
        script=self.main['jobs'][job]['steps'][-1]['run']
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            if request is not None:
                (root/'.github').mkdir()
                name='raft-native-experiment-request.json' if experiment else 'raft-native-build-request.json'
                (root/'.github'/name).write_text(json.dumps(request))
            env=dict(os.environ,**variables)
            return subprocess.run(['bash','-euo','pipefail','-c',script],cwd=root,env=env,capture_output=True,text=True)

    def test_actual_request_gate_accepts_only_explicit_delivery(self):
        env={'GITHUB_REF':'refs/heads/feature/android-native-port','NATIVE_REQUESTED':'true',
             'DELIVERY_REQUESTED':'true','BUILD_LANE':'delivery','REQUEST_EVENT':'push'}
        request={'request_id':'fixture-1','reason':'Validate current source','requested_from_sha':'a'*40}
        self.assertEqual(self.run_gate('native-request-gate',env,request).returncode,0)
        self.assertNotEqual(self.run_gate('native-request-gate',env).returncode,0)
        for change in ({'NATIVE_REQUESTED':'false'},{'DELIVERY_REQUESTED':'false'},
                       {'GITHUB_REF':'refs/heads/main'},{'BUILD_LANE':'unknown'}):
            with self.subTest(change=change):
                self.assertNotEqual(self.run_gate('native-request-gate',dict(env,**change),request).returncode,0)

    def test_actual_experiment_gate_disallows_public_delivery(self):
        env={'GITHUB_REF':'refs/heads/feature/android-native-port','NATIVE_REQUESTED':'true',
             'DELIVERY_REQUESTED':'false','BUILD_LANE':'experiment','REQUEST_EVENT':'workflow_dispatch'}
        self.assertEqual(self.run_gate('native-request-gate',env).returncode,0)
        self.assertNotEqual(self.run_gate('native-request-gate',dict(env,DELIVERY_REQUESTED='true')).returncode,0)
        request={'request_id':'experiment-1','reason':'Private hypothesis','requested_from_sha':'a'*40}
        self.assertEqual(self.run_gate('native-request-gate',dict(env,REQUEST_EVENT='push'),request,True).returncode,0)

    def test_actual_final_gate_fails_missing_apk_or_skipped_release(self):
        job=self.main['jobs']['delivery-result']
        self.assertEqual(job['if'],'always()')
        self.assertIn('reconstruct',job['needs'])
        self.assertIn('publish-early-test',job['needs'])
        base={'REQUEST_RESULT':'success','NATIVE_RESULT':'success','RELEASE_RESULT':'success','BUILD_LANE':'delivery'}
        self.assertEqual(self.run_gate('delivery-result',base).returncode,0)
        for change in ({'REQUEST_RESULT':'failure'},{'NATIVE_RESULT':'failure'},
                       {'NATIVE_RESULT':'skipped'},{'RELEASE_RESULT':'skipped'},{'RELEASE_RESULT':'failure'}):
            with self.subTest(change=change):
                self.assertNotEqual(self.run_gate('delivery-result',dict(base,**change)).returncode,0)
        self.assertEqual(self.run_gate('delivery-result',dict(base,BUILD_LANE='experiment',RELEASE_RESULT='skipped')).returncode,0)

    def test_actual_published_asset_gate_rejects_incomplete_remote_release(self):
        run=self.main['jobs']['publish-early-test']['steps'][-1]['run']
        scripts=re.findall("<<'PY'\\n(.*?)\\nPY",run,re.S)
        self.assertEqual(len(scripts),2)
        script=scripts[1]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'release-apk').mkdir()
            (root/'release-apk/test.apk').write_bytes(b'synthetic package')
            remote={'url':'https://github.com/example/repo/releases/tag/test','assets':[{'name':'test.apk','size':17}]}
            (root/'published-delivery.json').write_text(json.dumps(remote))
            from unittest.mock import patch
            previous=Path.cwd()
            try:
                os.chdir(root)
                with patch.dict(os.environ,{'RUNNER_TEMP':str(root),'GITHUB_STEP_SUMMARY':str(root/'summary.md')}):
                    exec(compile(script,'actual-remote-release-gate','exec'),{})
                    self.assertIn(remote['url'],(root/'summary.md').read_text())
                    remote['assets']=[];(root/'published-delivery.json').write_text(json.dumps(remote))
                    with self.assertRaises(AssertionError):exec(compile(script,'actual-remote-release-gate','exec'),{})
            finally:os.chdir(previous)


if __name__=='__main__':unittest.main()
