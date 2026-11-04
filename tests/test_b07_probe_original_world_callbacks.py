"""Synthetic C# only. Original Raft source stays in ephemeral CI memory."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from scripts.b07_probe_original_world_callbacks import fingerprint, inspect, assert_original_dll


def make_fixture(root, *, fake_call=False, early_completion=False, no_stats=False, missing_save=False):
    n = ('class Raft_Network {\nprivate IEnumerator WorldHasBeenLoaded() { '
         + ('WorldHasBeenRecieved = true; Helper.BroadCastToScene(evt);' if early_completion else
            'Helper.BroadCastToScene(evt); WorldHasBeenRecieved = true;') + ' }\n}')
    m = ('class GameManager {\npublic void OnWorldRecieved() { '
         + ('string fake="SaveGame();";' if fake_call else '')
         + ('' if missing_save else 'save.SaveGame(true);') + ' }\n}')
    s = ('class SaveAndLoad {\npublic void SaveGame(bool b) { SaveWorld(); '
         + ('' if no_stats else 'SteamUserStats.StoreStats();') + ' }\n}')
    for name, val in [('Raft_Network', n), ('GameManager', m), ('SaveAndLoad', s)]:
        (root / (name + '.cs')).write_text(val)
    return n, m, s


class B07WorldCallbackTests(TestCase):
    def run_fixture(self, **kwargs):
        with TemporaryDirectory() as d:
            root = Path(d)
            n, m, s = make_fixture(root, **kwargs)
            with patch.dict('scripts.b07_probe_original_world_callbacks.PINS',
                            {'Raft_Network': fingerprint(n), 'SaveAndLoad': fingerprint(s)}):
                return inspect(root, fingerprint(m))

    def test_positive_is_structural_not_device(self):
        r = self.run_fixture()
        self.assertEqual(r['on_world_received_savegame_calls'], 1)
        self.assertEqual(r['savegame_store_stats_calls'], 1)
        self.assertTrue(r['broadcast_before_completion'])
        self.assertFalse(r['observed_on_device'])
        self.assertFalse(r['original_sources_modified'])
        self.assertNotIn('SaveWorld();', str(r))

    def test_reordered_completion_refused(self):
        with self.assertRaisesRegex(ValueError, 'broadcast/completion'):
            self.run_fixture(early_completion=True)

    def test_quoted_false_save_does_not_count(self):
        with self.assertRaisesRegex(ValueError, 'SaveGame callsite'):
            self.run_fixture(fake_call=True, missing_save=True)

    def test_missing_stats_refused(self):
        with self.assertRaisesRegex(ValueError, 'stats boundary'):
            self.run_fixture(no_stats=True)

    def test_digest_mismatch_refused(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            make_fixture(root)
            with self.assertRaisesRegex(ValueError, 'hash changed'):
                inspect(root)

    def test_non_original_dll_refused(self):
        with TemporaryDirectory() as d:
            p = Path(d) / 'Assembly-CSharp.dll'
            p.write_bytes(b'not original')
            with self.assertRaisesRegex(ValueError, 'size/type'):
                assert_original_dll(p)

    def test_duplicate_source_refused(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            n, m, s = make_fixture(root)
            (root / 'copy').mkdir()
            (root / 'copy/GameManager.cs').write_text(m)
            with patch.dict('scripts.b07_probe_original_world_callbacks.PINS',
                            {'Raft_Network': fingerprint(n), 'SaveAndLoad': fingerprint(s)}):
                with self.assertRaisesRegex(ValueError, 'Ambiguous'):
                    inspect(root, fingerprint(m))
