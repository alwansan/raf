"""B07: tests only with synthetic C#; private original code never recorded."""
import unittest
from scripts.b07_probe_original_world_callbacks import fingerprint, method_body
from scripts.instrument_android_runtime_operations import instrument, wrap_original_world_callback


def fixture():
    return (
        'public class GameManager {\n'
        '    public void OnWorldRecieved() {\n'
        '        string decoy = "SaveGame();";\n'
        '        if (primary) SaveGame(true);\n'
        '        else if (secondary) SaveGame(false);\n'
        '        else SaveGame(true);\n'
        '    }\n'
        '    public void Other() { return; }\n'
        '}\n'
    )


def manifest(source):
    return {'sources': {'GameManager': {
        'sha256': fingerprint(source),
        'area': 'world',
        'methods': [{'name': 'OnWorldRecieved',
                     'body_sha256': fingerprint(method_body(source, 'OnWorldRecieved')[1])}]
    }}}


class OriginalWorldTraceTests(unittest.TestCase):
    def test_wrap_pinned_three_branch_game_manager_and_preserve_body(self):
        source = fixture()
        updated = instrument('GameManager', source, manifest(source))
        self.assertEqual(updated.count('SaveGame(true);'), source.count('SaveGame(true);'))
        self.assertEqual(updated.count('SaveGame(false);'), source.count('SaveGame(false);'))
        self.assertEqual(updated.count('"SaveGame();"'), 1)
        self.assertIn('BeginOperation("world", "OnWorldRecieved"', updated)
        self.assertIn('OnWorldRecieved.exception', updated)
        self.assertIn('EndOperation("world", "OnWorldRecieved"', updated)
        self.assertIn('throw;', updated)
        self.assertIn('#if UNITY_ANDROID && !UNITY_EDITOR', updated)
        self.assertIn('public void Other() { return; }', updated)
        body = method_body(source, 'OnWorldRecieved')[1]
        self.assertIn(body, updated)

    def test_callback_body_sha_drifts_fail_closed(self):
        source = fixture()
        with self.assertRaisesRegex(ValueError, 'callback body'):
            wrap_original_world_callback(source, 'OnWorldRecieved', '0' * 64, 'world')

    def test_nonvoid_callback_refused(self):
        source = fixture().replace('public void OnWorldRecieved()', 'public bool OnWorldRecieved()')
        sha = fingerprint(method_body(source, 'OnWorldRecieved')[1])
        with self.assertRaisesRegex(ValueError, 'callback body'):
            wrap_original_world_callback(source, 'OnWorldRecieved', sha, 'world')

    def test_comment_decoy_and_duplicate_method_refused(self):
        source = fixture() + 'public void OnWorldRecieved() { SaveGame(true); }\n'
        with self.assertRaisesRegex(ValueError, 'one original'):
            wrap_original_world_callback(source, 'OnWorldRecieved', '0'*64, 'world')

    def test_unknown_original_revision_not_instrumented(self):
        source = fixture()
        mf = manifest(source)
        with self.assertRaisesRegex(ValueError, 'Unknown adapted'):
            instrument('GameManager', source.replace('primary', 'different'), mf)

    def test_duplicate_instrumentation_not_accepted(self):
        source = fixture()
        changed = instrument('GameManager', source, manifest(source))
        with self.assertRaises(ValueError):
            instrument('GameManager', changed, manifest(source))

    def test_synthetic_executable_is_fully_confined_to_callback(self):
        source = fixture()
        updated = instrument('GameManager', source, manifest(source))
        # No success/ready flags are inserted, and original branches survive.
        self.assertNotIn('WorldHasBeenRecieved = true', updated)
        self.assertNotIn('return true;', updated)
        self.assertEqual(updated.count('SaveGame('), source.count('SaveGame('))


if __name__ == '__main__':
    unittest.main()
