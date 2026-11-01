from pathlib import Path
import subprocess
import tempfile
import unittest
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
        for name in BANKS | {'Data.rgd', 'Haptics/test.wav'}:
            p = self.source / name
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(('synthetic unchanged fixture: ' + name).encode())
        self.commit()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.STDOUT)

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')

    def test_exact_copy_and_idempotence(self):
        stage(self.repo, self.project, self.report, True)
        stage(self.repo, self.project, self.report, True)
        for path in self.source.rglob('*'):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (self.project / 'Assets/StreamingAssets' / path.relative_to(self.source)).read_bytes())

    def test_modified_source_refused_before_copy(self):
        (self.source / 'Data.rgd').write_bytes(b'changed')
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True)
        self.assertFalse(self.project.exists())

    def test_existing_destination_conflict_is_preserved(self):
        target = self.project / 'Assets/StreamingAssets/Data.rgd'
        target.parent.mkdir(parents=True)
        target.write_bytes(b'original existing data')
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True)
        self.assertEqual(target.read_bytes(), b'original existing data')
        self.assertEqual(len(list(target.parent.rglob('*'))), 1)

    def test_lfs_pointer_never_copied_as_audio(self):
        (self.source / 'MasterBank.bank').write_bytes(b'version https://git-lfs.github.com/spec/v1\noid sha256:' + b'0' * 64 + b'\nsize 123\n')
        self.commit()
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True)
        self.assertFalse(self.project.exists())

    def test_missing_original_bank_refused(self):
        (self.source / 'MasterBank.strings.bank').unlink()
        self.commit()
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True)
        self.assertFalse(self.project.exists())

    def test_destination_escape_refused(self):
        self.project.mkdir()
        outside = self.root / 'outside'
        outside.mkdir()
        (self.project / 'Assets').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError): stage(self.repo, self.project, self.report, True)
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
