"""Source-free regression checks for Android runtime units copied into the original managed compile."""
import tempfile
import unittest
from pathlib import Path

from scripts.verify_android_offline_candidate import (
    RUNTIME_COMPILE_SUPPORT_FILES,
    copy_runtime_compile_support_files,
)

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'android-port' / 'Runtime' / 'Platform'
PROBE = 'AndroidExpansionArchiveProbe.cs'


class OfflineRuntimeCompileDependencies(unittest.TestCase):
    def test_real_diagnostic_probe_reference_is_covered(self):
        self.assertIn(PROBE, RUNTIME_COMPILE_SUPPORT_FILES)
        self.assertIn('AndroidTestDiagnostics.cs', RUNTIME_COMPILE_SUPPORT_FILES)
        self.assertEqual(len(RUNTIME_COMPILE_SUPPORT_FILES), len(set(RUNTIME_COMPILE_SUPPORT_FILES)))
        diagnostics = (RUNTIME / 'AndroidTestDiagnostics.cs').read_text()
        probe = (RUNTIME / PROBE).read_text()
        self.assertIn('AndroidExpansionArchiveProbe.Inspect(', diagnostics)
        self.assertIn('public static class AndroidExpansionArchiveProbe', probe)
        self.assertIn('namespace RaftAndroid.Platform', probe)
        for filename in RUNTIME_COMPILE_SUPPORT_FILES:
            with self.subTest(filename=filename):
                self.assertTrue((RUNTIME / filename).is_file())

    def test_copies_all_bounded_synthetic_sources_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / 'runtime'
            source = root / 'original-private'
            runtime.mkdir()
            source.mkdir()
            for i, filename in enumerate(RUNTIME_COMPILE_SUPPORT_FILES):
                (runtime / filename).write_bytes(('fixture-' + str(i)).encode('ascii'))
            copy_runtime_compile_support_files(runtime, source)
            self.assertEqual(len(list(source.glob('RaftAndroid-*.cs'))),
                             len(RUNTIME_COMPILE_SUPPORT_FILES))
            for filename in RUNTIME_COMPILE_SUPPORT_FILES:
                self.assertEqual((runtime / filename).read_bytes(),
                                 (source / ('RaftAndroid-' + filename)).read_bytes())

    def test_missing_companion_refuses_copy_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / 'runtime'
            source = root / 'original-private'
            runtime.mkdir()
            source.mkdir()
            for filename in RUNTIME_COMPILE_SUPPORT_FILES:
                if filename != PROBE:
                    (runtime / filename).write_bytes(b'synthetic')
            with self.assertRaisesRegex(FileNotFoundError, PROBE):
                copy_runtime_compile_support_files(runtime, source)
            self.assertEqual(list(source.iterdir()), [])

    def test_symlink_companion_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / 'runtime'
            source = root / 'original-private'
            runtime.mkdir()
            source.mkdir()
            for filename in RUNTIME_COMPILE_SUPPORT_FILES:
                if filename != PROBE:
                    (runtime / filename).write_bytes(b'synthetic')
            try:
                (runtime / PROBE).symlink_to(runtime / RUNTIME_COMPILE_SUPPORT_FILES[0])
            except (OSError, NotImplementedError):
                self.skipTest('Symlink creation unsupported')
            with self.assertRaises(FileNotFoundError):
                copy_runtime_compile_support_files(runtime, source)
            self.assertEqual(list(source.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
