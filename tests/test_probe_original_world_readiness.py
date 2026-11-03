"""Synthetic-only source-contract tests; no original Raft source in fixtures."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.adapt_android_offline_startup import fingerprint
from scripts.probe_original_world_readiness import inspect


def fixture(before=True, received=True, event=True):
    before_call = 'Helper.BroadCastToScene(secretEvent);\n' if before and event else ''
    after_call = 'Helper.BroadCastToScene(secretEvent);\n' if not before and event else ''
    received_call = 'WorldHasBeenRecieved = true;\n' if received else ''
    return ('class Raft_Network {\nprivate IEnumerator WorldHasBeenLoaded() {\n'
            'while (!gameManagerStartCalled) yield return null;\n'
            + before_call + received_call + after_call + ' }\n}')


class WorldReadinessProbeTests(unittest.TestCase):
    def inspect_fixture(self, source):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / 'Raft_Network.cs').write_text(source)
            with patch.dict('scripts.probe_original_world_readiness.PINS',
                            {'Raft_Network': fingerprint(source)}):
                return inspect(Path(temp))

    def test_broadcast_precedes_real_world_completion(self):
        report = self.inspect_fixture(fixture())
        self.assertTrue(report['coroutine_returns_enumerator'])
        self.assertEqual(report['broadcasts_before_received_assignment'], 1)
        self.assertEqual(report['received_true_assignments'], 1)
        self.assertEqual(report['game_manager_start_references'], 1)
        self.assertFalse(report['modified_original_source'])
        self.assertFalse(report['unity_or_device_executed'])
        self.assertNotIn('secretEvent', str(report))

    def test_missing_or_reordered_world_gate_is_not_certified(self):
        for source in (fixture(before=False), fixture(received=False), fixture(event=False)):
            with self.subTest(source=source[:20]):
                with self.assertRaisesRegex(ValueError, 'readiness|broadcast'):
                    self.inspect_fixture(source)

    def test_comment_or_string_literal_is_not_world_progress(self):
        real = fixture()
        cases = (
            real.replace('Helper.BroadCastToScene(secretEvent);',
                         '// Helper.BroadCastToScene(secretEvent);'),
            real.replace('Helper.BroadCastToScene(secretEvent);',
                         '/* Helper.BroadCastToScene(secretEvent); */'),
            real.replace('Helper.BroadCastToScene(secretEvent);',
                         'string info = "Helper.BroadCastToScene(secretEvent);";'),
            real.replace('WorldHasBeenRecieved = true;',
                         'string info = "WorldHasBeenRecieved = true;";'),
            real.replace('WorldHasBeenRecieved = true;',
                         'string info = @"note ""WorldHasBeenRecieved = true;""";'),
        )
        for index, source in enumerate(cases):
            with self.subTest(index=index):
                with self.assertRaisesRegex(ValueError, 'readiness|broadcast'):
                    self.inspect_fixture(source)

    def test_false_earlier_broadcast_does_not_hide_real_wrong_order(self):
        source = fixture(before=False).replace(
            'WorldHasBeenRecieved = true;',
            '// Helper.BroadCastToScene(secretEvent);\n'
            'WorldHasBeenRecieved = true;')
        with self.assertRaisesRegex(ValueError, 'no longer follows'):
            self.inspect_fixture(source)

    def test_lexical_decoys_do_not_inflate_counts(self):
        source = fixture().replace(
            'WorldHasBeenRecieved = true;',
            'string link = "https://example.invalid/WorldHasBeenRecieved";\n'
            'char slash = \'/\';\n'
            'string note = @"// Helper.BroadCastToScene(fake);";\n'
            'WorldHasBeenRecieved = true;')
        report = self.inspect_fixture(source)
        self.assertEqual(report['scene_broadcast_calls'], 1)
        self.assertEqual(report['received_true_assignments'], 1)

    def test_source_revision_and_ambiguity_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'Raft_Network.cs').write_text(fixture())
            with self.assertRaisesRegex(ValueError, 'Unknown original'):
                inspect(root)
            (root / 'copy').mkdir()
            (root / 'copy/Raft_Network.cs').write_text(fixture())
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                inspect(root)

    def test_does_not_modify_original_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            file = root / 'Raft_Network.cs'
            file.write_text(fixture())
            old = file.read_bytes()
            with patch.dict('scripts.probe_original_world_readiness.PINS',
                            {'Raft_Network': fingerprint(fixture())}):
                inspect(root)
            self.assertEqual(file.read_bytes(), old)


if __name__ == '__main__':
    unittest.main()
