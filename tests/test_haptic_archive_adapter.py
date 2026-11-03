"""Fail-closed checks for SHA-pinned original HapticAudio single-call adapter."""
import hashlib
import unittest
from unittest.mock import patch

from scripts.adapt_android_render_lifetimes import PINS, adapt


class OriginalHapticReaderAdapterTests(unittest.TestCase):
    def _adapt_pinned(self, source):
        original_hash = hashlib.sha256(source.replace('\r\n', '\n').encode()).hexdigest()
        with patch.dict('scripts.adapt_android_render_lifetimes.PINS',
                        {'HapticAudio': (original_hash, 0)}):
            return adapt('HapticAudio', source)

    def test_real_adapter_only_replaces_one_original_file_read(self):
        source = ('using System.IO;\nclass HapticAudio {\n'
                  '  byte[] CreateAudioSources(string path) {\n'
                  '    byte[] original = File.ReadAllBytes(path);\n'
                  '    return original;\n  }\n}\n')
        transformed = self._adapt_pinned(source)
        expected = source.replace('File.ReadAllBytes(',
                                  'RaftAndroid.Platform.AndroidStreamingAssets.ReadAllBytes(', 1)
        self.assertEqual(transformed, expected)
        self.assertIn('CreateAudioSources', transformed)
        self.assertNotIn('catch (', transformed)
        self.assertNotIn('return null', transformed)

    def test_unknown_original_revision_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unknown original source revision'):
            adapt('HapticAudio', 'class HapticAudio { altered }')

    def test_two_original_reads_are_not_silently_rewritten(self):
        source = 'class HapticAudio { void Start() { File.ReadAllBytes(a); File.ReadAllBytes(b); } }'
        with self.assertRaisesRegex(ValueError, 'Original haptic reader changed'):
            self._adapt_pinned(source)

    def test_different_original_read_api_is_not_silently_accepted(self):
        source = 'class HapticAudio { void Start() { File.ReadAllText(a); } }'
        with self.assertRaisesRegex(ValueError, 'Original haptic reader changed'):
            self._adapt_pinned(source)


if __name__ == '__main__':
    unittest.main()
