"""Synthetic corruption tests; never include the original proprietary WAVs."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.probe_haptics_asset_manifest import audit, HapticsInventoryError, PREFIX


class TestHapticsInventory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        self.repo.mkdir()
        self.run_git('init', '-q')
        self.folder = self.repo / PREFIX
        self.folder.mkdir(parents=True)
        for name in ('A.wav', 'B.wav'):
            (self.folder / name).write_bytes(b'SYNTHETIC_WAV_FIXTURE_' + name.encode())
        self.run_git('add', '.')
        self.run_git('-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid',
                     'commit', '-qm', 'fixture')
        self.manifest = self.repo / 'manifest.json'
        self.write_manifest()

    def run_git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args],
                                       stderr=subprocess.STDOUT).decode().strip()

    def write_manifest(self):
        data = {'schema_version': 1, 'path_prefix': PREFIX, 'files': {}}
        for name in ('A.wav', 'B.wav'):
            data['files'][name] = {
                'git_blob_sha': self.run_git('rev-parse', 'HEAD:' + PREFIX + name),
                'bytes': (self.folder / name).stat().st_size}
        self.manifest.write_text(json.dumps(data))

    def test_exact_source_inventory(self):
        result = audit(self.repo, self.manifest, expected_count=2)
        self.assertEqual(result['tracked_wavs'], 2)
        self.assertFalse(result['runtime_apk_obb_path_verified'])

    def test_missing_tracked_asset_rejected(self):
        self.run_git('rm', '-q', PREFIX + 'A.wav')
        self.run_git('-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid',
                     'commit', '-qm', 'remove')
        with self.assertRaises(HapticsInventoryError): audit(self.repo, self.manifest, 2)

    def test_uncommitted_byte_mutation_rejected(self):
        (self.folder / 'A.wav').write_bytes(b'changed')
        with self.assertRaises(HapticsInventoryError): audit(self.repo, self.manifest, 2)

    def test_manifest_blob_tamper_rejected(self):
        data = json.loads(self.manifest.read_text())
        data['files']['B.wav']['git_blob_sha'] = '0' * 40
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(HapticsInventoryError): audit(self.repo, self.manifest, 2)

    def test_extra_tracked_asset_rejected(self):
        (self.folder / 'C.wav').write_bytes(b'extra')
        self.run_git('add', '.')
        self.run_git('-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid',
                     'commit', '-qm', 'add')
        with self.assertRaises(HapticsInventoryError): audit(self.repo, self.manifest, 2)

    def test_manifest_case_alias_rejected(self):
        data = json.loads(self.manifest.read_text())
        data['files']['a.wav'] = data['files']['A.wav']
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(HapticsInventoryError): audit(self.repo, self.manifest)

    def test_manifest_path_escape_rejected(self):
        data = json.loads(self.manifest.read_text())
        data['files']['../escape.wav'] = data['files'].pop('A.wav')
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(HapticsInventoryError): audit(self.repo, self.manifest)

    def test_co_mutated_tracked_wav_and_manifest_must_not_redefine_original(self):
        # Negative control: an unanchored manifest and matching re-committed
        # WAV can agree with each other but both differ from the audited original.
        immutable_anchor = self.run_git('hash-object', '--', str(self.manifest))
        (self.folder / 'A.wav').write_bytes(b'SYNTHETIC_CHANGED_WITH_MANIFEST')
        self.run_git('add', '.')
        self.run_git('-c', 'user.name=Fixture', '-c', 'user.email=test@example.invalid',
                     'commit', '-qm', 'co-mutated-test-source')
        self.write_manifest()
        self.assertTrue(audit(self.repo, self.manifest, expected_count=2)
                        ['original_manifest_and_worktree_match'])
        with self.assertRaises(HapticsInventoryError):
            audit(self.repo, self.manifest, expected_count=2,
                  expected_manifest_blob_sha=immutable_anchor)

    def test_count_policy_rejected(self):
        with self.assertRaises(HapticsInventoryError): audit(self.repo, self.manifest, 29)


if __name__ == '__main__':
    unittest.main()
