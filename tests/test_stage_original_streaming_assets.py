from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from unittest import mock
from scripts import stage_original_streaming_assets as source_stage
from scripts.stage_original_streaming_assets import BANKS, stage


class OriginalStreamingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.source = self.repo / 'Raft/Raft_Data/StreamingAssets'
        self.source.mkdir(parents=True)
        self.project = self.root / 'project'
        self.report = self.root / 'report.json'
        self.git('init', '-q')
        # Test-owned WAV bytes, never original game audio.
        self.wav_names = [f'Haptics/Haptic{i:02d}.wav' for i in range(29)]
        for name in BANKS | {'Data.rgd'} | set(self.wav_names):
            p = self.source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(('synthetic unchanged fixture: ' + name).encode())
        entries = {}
        for relative in self.wav_names:
            source = self.source / relative
            blob = self.git('hash-object', '--',
                            'Raft/Raft_Data/StreamingAssets/' + relative).decode().strip()
            entries[Path(relative).name] = {'git_blob_sha': blob,
                                            'bytes': source.stat().st_size}
        config = self.repo / 'config'
        config.mkdir()
        (config / 'original-haptics-manifest.json').write_text(json.dumps({
            'schema_version': 1,
            'path_prefix': 'Raft/Raft_Data/StreamingAssets/Haptics/',
            'files': entries}, sort_keys=True))
        self.commit()
        # Synthetic fixture has its own immutable reference, fixed at setup.
        # The default production stage instead pins the real original SHA.
        self.haptics_manifest_blob_sha = self.git(
            'hash-object', '--', 'config/original-haptics-manifest.json').decode().strip()

        # Fixture-owned Git blobs are deliberately not the private original
        # archive's immutable root blobs. Rebind only inside this synthetic
        # test lifetime; no production runtime override is exposed.
        self.synthetic_root_blobs = {
            name: self.git('rev-parse', '--verify',
                           'HEAD:Raft/Raft_Data/StreamingAssets/' + name).decode().strip()
            for name in BANKS | {'Data.rgd', 'UnityServicesProjectConfiguration.json'}
            if (self.source / name).is_file()
        }
        if hasattr(source_stage, 'ORIGINAL_ROOT_BLOB_SHAS'):
            original_root_blob_patcher = mock.patch.object(
                source_stage, 'ORIGINAL_ROOT_BLOB_SHAS', self.synthetic_root_blobs)
            original_root_blob_patcher.start()
            self.addCleanup(original_root_blob_patcher.stop)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.STDOUT)

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')

    def test_exact_copy_and_idempotence(self):
        stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        for path in self.source.rglob('*'):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (self.project / 'Assets/StreamingAssets' / path.relative_to(self.source)).read_bytes())

    def test_modified_source_refused_before_copy(self):
        (self.source / 'Data.rgd').write_bytes(b'changed')
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())

    def test_existing_destination_conflict_is_preserved(self):
        target = self.project / 'Assets/StreamingAssets/Data.rgd'
        target.parent.mkdir(parents=True)
        target.write_bytes(b'original existing data')
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertEqual(target.read_bytes(), b'original existing data')
        self.assertEqual(len(list(target.parent.rglob('*'))), 1)

    def test_lfs_pointer_never_copied_as_audio(self):
        (self.source / 'MasterBank.bank').write_bytes(b'version https://git-lfs.github.com/spec/v1\noid sha256:' + b'0' * 64 + b'\nsize 123\n')
        self.commit()
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())

    def test_missing_original_bank_refused(self):
        (self.source / 'MasterBank.strings.bank').unlink()
        self.commit()
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())

    def test_missing_original_haptic_rejected_before_any_staging(self):
        (self.source / self.wav_names[0]).unlink()
        self.commit()
        with self.assertRaises(ValueError):
            stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())
        self.assertFalse(self.report.exists())

    def test_changed_committed_original_haptic_rejected(self):
        (self.source / self.wav_names[1]).write_bytes(b'changed synthetic WAV')
        self.commit()
        with self.assertRaises(ValueError):
            stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())

    def test_uncommitted_haptic_mutation_rejected(self):
        (self.source / self.wav_names[2]).write_bytes(b'uncommitted tamper')
        with self.assertRaises(ValueError):
            stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())

    def test_extra_tracked_original_haptic_rejected(self):
        (self.source / 'Haptics/new_unknown.wav').write_bytes(b'extra synthetic WAV')
        self.commit()
        with self.assertRaises(ValueError):
            stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())

    def test_corrupted_manifest_identity_rejected(self):
        manifest = self.repo / 'config/original-haptics-manifest.json'
        data = json.loads(manifest.read_text())
        data['files'][Path(self.wav_names[3]).name]['git_blob_sha'] = '0' * 40
        manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())

    def test_co_mutated_original_wav_and_manifest_cannot_rebase_trust(self):
        # Both current HEAD WAV bytes and mutable manifest are changed in lockstep.
        # The trust anchor captured at fixture setup must still detect drift.
        target = self.source / self.wav_names[0]
        target.write_bytes(b'SYNTHETIC_REPLACEMENT_SAME_ORIGINAL_NAME')
        manifest = self.repo / 'config/original-haptics-manifest.json'
        data = json.loads(manifest.read_text(encoding='utf-8'))
        name = Path(self.wav_names[0]).name
        data['files'][name]['bytes'] = target.stat().st_size
        data['files'][name]['git_blob_sha'] = self.git(
            'hash-object', '--', 'Raft/Raft_Data/StreamingAssets/' + self.wav_names[0]).decode().strip()
        manifest.write_text(json.dumps(data))
        self.commit()
        with self.assertRaises(ValueError):
            stage(self.repo, self.project, self.report, True,
                  haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())
        self.assertFalse(self.report.exists())

    def test_destination_escape_refused(self):
        self.project.mkdir()
        outside = self.root / 'outside'
        outside.mkdir()
        (self.project / 'Assets').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True,
              haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
