import tempfile
from pathlib import Path
import unittest
from scripts.adapt_android_offline_startup import adapt, apply, enter, replace_exact


class AndroidOfflineStartupTests(unittest.TestCase):
    def test_unknown_original_revision_is_refused(self):
        with self.assertRaises(ValueError):
            adapt('SteamManager', 'class SteamManager {}')

    def test_method_anchor_requires_unique_original_signature(self):
        with self.assertRaises(ValueError):
            enter('void Start() {} void Start() {}', 'Start', 'return;')

    def test_call_count_drift_refused(self):
        with self.assertRaises(ValueError):
            replace_exact('native(); native();', 'native();', 'local();')

    def test_later_missing_original_leaves_prior_files_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'project/Assets'
            assets.mkdir(parents=True)
            path = assets / 'SteamManager.cs'
            path.write_text('unrecognized original')
            path.with_suffix('.cs.meta').write_text('original metadata')
            with self.assertRaises(ValueError):
                apply(root / 'project', root / 'backup', True)
            self.assertEqual(path.read_text(), 'unrecognized original')
            self.assertFalse((root / 'backup').exists())

    def test_local_delivery_remains_before_added_remote_boundary(self):
        text = 'void RPC() { DeliverLocal(); if (RemoteConnected()) SendRemote(); }'
        changed = replace_exact(text, 'if (RemoteConnected())', 'if (!LocalEnabled && RemoteConnected())')
        self.assertLess(changed.index('DeliverLocal();'), changed.index('!LocalEnabled'))
        self.assertEqual(changed.count('DeliverLocal();'), 1)
