import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scripts.restore_postfx_compute import restore, verified_source
from scripts.restore_postfx_shaders import INCLUDES


class HistogramRecoveryTests(unittest.TestCase):
    def fixture(self, root):
        project = root/'project'
        old = project/'Assets/ComputeShader/EyeHistogram.asset'
        old.parent.mkdir(parents=True)
        old.write_text('%YAML 1.1\n--- !u!72 &7200000\nComputeShader:\n  m_Name: EyeHistogram\n')
        Path(str(old)+'.meta').write_text('fileFormatVersion: 2\nguid: '+ 'a'*32 +'\nNativeFormatImporter: {}\n')
        inc = project/INCLUDES
        inc.mkdir(parents=True)
        (inc/'Common.cginc').write_text('// common')
        (inc/'EyeAdaptation.cginc').write_text('#define HISTOGRAM_BINS 64\n#define HISTOGRAM_THREAD_X 16\n#define HISTOGRAM_THREAD_Y 16\n')
        return project, old

    def test_untrusted_bytecode_or_source_rejected(self):
        with self.assertRaises(ValueError): verified_source(b'not the official program')

    @patch('scripts.restore_postfx_compute.verified_source', return_value='#include "Common.cginc"\n#include "EyeAdaptation.cginc"\n#pragma kernel KEyeHistogram\n')
    def test_resource_lookup_guid_and_backup(self, _):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); project, old = self.fixture(root)
            original, meta = old.read_bytes(), Path(str(old)+'.meta').read_bytes()
            restore(project, root/'backup', b'fixture')
            output = project/'Assets/RaftAndroid/Resources/Shaders/EyeHistogram.compute'
            self.assertFalse(old.exists())
            self.assertIn(INCLUDES+'Common.cginc', output.read_text())
            self.assertIn('guid: '+'a'*32, Path(str(output)+'.meta').read_text())
            self.assertIn('ComputeShaderImporter:', Path(str(output)+'.meta').read_text())
            self.assertEqual((root/'backup'/old.relative_to(project)).read_bytes(), original)
            self.assertEqual(Path(str(root/'backup'/old.relative_to(project))+'.meta').read_bytes(), meta)

    @patch('scripts.restore_postfx_compute.verified_source', return_value='// source')
    def test_unknown_file_id_or_conflict_fails_without_mutation(self, _):
        for mode in ('fileid', 'resource', 'include', 'duplicate', 'backup'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                root = Path(temp); project, old = self.fixture(root)
                if mode == 'fileid': old.write_text(old.read_text().replace('&7200000','&7200001'))
                elif mode == 'resource':
                    other = project/'Assets/Other/Resources/Shaders/EyeHistogram.compute'
                    other.parent.mkdir(parents=True); other.write_text('// existing')
                elif mode == 'include': (project/INCLUDES/'Common.cginc').unlink()
                elif mode == 'duplicate':
                    other = project/'Assets/Other/EyeHistogram.asset'
                    other.parent.mkdir(parents=True); other.write_bytes(old.read_bytes())
                else:
                    other = root/'backup'/old.relative_to(project)
                    other.parent.mkdir(parents=True); other.write_text('existing backup')
                original = old.read_bytes()
                with self.assertRaises(ValueError): restore(project, root/'backup', b'fixture')
                self.assertEqual(old.read_bytes(), original)
                self.assertTrue(Path(str(old)+'.meta').exists())

    @patch('scripts.restore_postfx_compute.verified_source', return_value='// source')
    def test_failure_after_original_unlink_restores_exact_original_and_meta(self, _):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); project, old = self.fixture(root)
            meta = Path(str(old)+'.meta')
            original, original_meta = old.read_bytes(), meta.read_bytes()
            unlink = Path.unlink
            def fail_original_meta(path, *args, **kwargs):
                if path == meta:
                    raise OSError('simulated original-meta unlink failure')
                return unlink(path, *args, **kwargs)
            with patch.object(Path, 'unlink', autospec=True, side_effect=fail_original_meta):
                with self.assertRaisesRegex(OSError, 'simulated original-meta'):
                    restore(project, root/'backup', b'fixture')
            self.assertEqual(old.read_bytes(), original)
            self.assertEqual(meta.read_bytes(), original_meta)
            output = project/'Assets/RaftAndroid/Resources/Shaders/EyeHistogram.compute'
            self.assertFalse(output.exists())
            self.assertFalse(Path(str(output)+'.meta').exists())
            self.assertEqual((root/'backup'/old.relative_to(project)).read_bytes(), original)

    @patch('scripts.restore_postfx_compute.verified_source', return_value='// source')
    def test_symlink_original_is_rejected_before_backup(self, _):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); project, old = self.fixture(root)
            actual = root/'outside.asset'
            actual.write_bytes(old.read_bytes())
            old.unlink()
            old.symlink_to(actual)
            with self.assertRaisesRegex(ValueError, 'regular files'):
                restore(project, root/'backup', b'fixture')
            self.assertEqual(actual.read_bytes(), old.read_bytes())
            self.assertFalse((root/'backup').exists())



if __name__ == '__main__': unittest.main()
