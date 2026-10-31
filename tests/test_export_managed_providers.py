from pathlib import Path
import tempfile
import unittest
from scripts.stage_export_managed_providers import select_providers, stage


class ExportProviderTests(unittest.TestCase):
    def test_only_known_exact_duplicate_identity_is_excluded(self):
        selected, excluded = select_providers({'PlayFab.dll': ('PlayFab', 1), 'PlayFab_o.dll': ('PlayFab', 1), 'Game.dll': ('Game', 1)})
        self.assertEqual(selected, ['Game.dll', 'PlayFab.dll'])
        self.assertEqual(excluded, ['PlayFab_o.dll'])

    def test_unknown_or_extra_duplicate_fails(self):
        for identities in ({'a.dll': ('Other',), 'b.dll': ('Other',)}, {'PlayFab.dll': ('PlayFab',), 'PlayFab_o.dll': ('PlayFab',), 'third.dll': ('PlayFab',)}, {'PlayFab.dll': ('PlayFab',1), 'PlayFab_o.dll': ('PlayFab',2)}):
            with self.assertRaises(ValueError):select_providers(identities)

    def test_preserves_every_original_and_refuses_destination_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);source = root/'source';source.mkdir();destination = root/'out'
            for name in ['PlayFab.dll', 'PlayFab_o.dll']:(source/name).write_bytes(name.encode())
            before = {p.name:p.read_bytes() for p in source.iterdir()}
            result = stage(source, destination, lambda p: ('PlayFab', 0))
            self.assertEqual(result['staged_providers'], 1)
            self.assertEqual({p.name:p.read_bytes() for p in source.iterdir()}, before)
            with self.assertRaises(FileExistsError):stage(source, destination, lambda p: ('PlayFab', 0))

    def test_unknown_duplicate_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);source = root/'source';source.mkdir();destination = root/'out'
            for name in ['a.dll','b.dll']:(source/name).touch()
            with self.assertRaises(ValueError):stage(source,destination,lambda p: ('Other', 0))
            self.assertFalse(destination.exists())
