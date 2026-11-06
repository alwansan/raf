"""Source-free T4 axis/cursor-lock rewrite controls; no original game code included."""
import tempfile
import unittest
from unittest.mock import patch as mock_patch
from pathlib import Path
from scripts.t4_adapt_original_mouse_axes import replacement_plan, patch, EXPECTED, SHIM


def fixture(root, *, tamper=False):
    for idx in range(4):
        text = ('class Camera%d { void Tick() {\n' % idx
                + '  float a = Input.GetAxis("Mouse X");\n'
                + '  float b = UnityEngine.Input.GetAxisRaw("Mouse Y");\n'
                + ('  Cursor.lockState = (gameplay ? CursorLockMode.Locked : CursorLockMode.None);\n' if idx < 2 else '')
                + '}}\n')
        if tamper and idx == 3:
            text = text.replace('Mouse X', 'Mouse Z')
        (root / ('Camera%d.cs' % idx)).write_text(text)


class MouseOriginalPatchTests(unittest.TestCase):
    def _source_and_backup(self, temp):
        root = Path(temp)
        source_root = root / "original"
        source_root.mkdir()
        fixture(source_root)
        original = {p: p.read_bytes() for p in source_root.glob("*.cs")}
        return root, source_root, root / "private-original-backup", original

    def _invoke(self, source_root, backup):
        # Synthetic only. The production call still authenticates the original
        # 3,211,776-byte Raft DLL before it may modify project C#.
        with mock_patch("scripts.t4_adapt_original_mouse_axes.assert_original"):
            return patch(source_root, source_root / "synthetic.dll",
                         apply=True, backup=backup)

    def test_authentic_mouse_rewrite_keeps_a_complete_original_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            _, source_root, backup, original = self._source_and_backup(temp)
            record = self._invoke(source_root, backup)
            self.assertTrue(record["applied"])
            self.assertEqual(record["matched"], EXPECTED)
            for path, before in original.items():
                self.assertEqual((backup / path.name).read_bytes(), before)
                self.assertIn(SHIM, path.read_text(encoding="utf-8"))
            self.assertEqual(len(list(backup.rglob("*.cs"))), 4)

    def test_original_changes_after_replacement_plan_must_not_be_overwritten(self):
        # The external Unity stage could rewrite a C# source after a lexical
        # replacement plan was computed. A later backup of the new bytes is NOT
        # proof that installing the old planned result is safe.
        from scripts import t4_adapt_original_mouse_axes as stage
        with tempfile.TemporaryDirectory() as temp:
            _, source_root, backup, originals = self._source_and_backup(temp)
            changed = source_root / "Camera0.cs"
            authentic_plan = stage.replacement_plan
            intervening_edit = b"// synthetic independent source edit after planning\n"

            def change_after_plan(*args, **kwargs):
                plan = authentic_plan(*args, **kwargs)
                changed.write_bytes(changed.read_bytes() + intervening_edit)
                return plan

            with mock_patch("scripts.t4_adapt_original_mouse_axes.replacement_plan",
                            side_effect=change_after_plan):
                with self.assertRaisesRegex(ValueError, "changed after source plan"):
                    self._invoke(source_root, backup)
            self.assertEqual(changed.read_bytes(),
                             originals[changed] + intervening_edit)
            for source, original_bytes in originals.items():
                if source != changed:
                    self.assertEqual(source.read_bytes(), original_bytes)
            self.assertFalse(backup.exists(), "stale original plan cannot acquire backup or mutate")
            # Retrying against the now-current sources must recalculate the
            # plan and retain the other writer's addition byte-for-byte.
            self.assertTrue(self._invoke(source_root, backup)["applied"])
            self.assertIn(intervening_edit, changed.read_bytes())
            self.assertEqual((backup / changed.name).read_bytes(),
                             originals[changed] + intervening_edit)

    def test_interrupted_original_backup_copy_leaves_all_originals_and_retryable(self):
        with tempfile.TemporaryDirectory() as temp:
            _, source_root, backup, original = self._source_and_backup(temp)
            original_write = Path.write_bytes
            broken = backup / "Camera1.cs"

            def interrupted(path, data):
                if path == broken:
                    original_write(path, b"partial-private-backup")
                    raise OSError("synthetic backup write interruption")
                return original_write(path, data)

            with mock_patch.object(Path, "write_bytes", interrupted):
                with self.assertRaisesRegex(OSError, "backup write interruption"):
                    self._invoke(source_root, backup)
            self.assertFalse(backup.exists(), "Incomplete newly-owned backup blocks legitimate retry")
            self.assertEqual({p: p.read_bytes() for p in original}, original)
            self._invoke(source_root, backup)
            for source, before in original.items():
                self.assertEqual((backup / source.name).read_bytes(), before)

    def test_silent_backup_corruption_must_fail_before_any_original_write(self):
        with tempfile.TemporaryDirectory() as temp:
            _, source_root, backup, original = self._source_and_backup(temp)
            original_write = Path.write_bytes
            broken = backup / "Camera0.cs"

            def silent_corruption(path, data):
                if path == broken:
                    return original_write(path, b"silent-corruption")
                return original_write(path, data)

            with mock_patch.object(Path, "write_bytes", silent_corruption):
                with self.assertRaisesRegex(ValueError, "backup.*byte|byte.*backup"):
                    self._invoke(source_root, backup)
            self.assertEqual({p: p.read_bytes() for p in original}, original)
            self.assertFalse(backup.exists())
            self._invoke(source_root, backup)
            for source, before in original.items():
                self.assertEqual((backup / source.name).read_bytes(), before)

    def test_mid_original_source_torn_write_rolls_back_all_files_and_retries(self):
        with tempfile.TemporaryDirectory() as temp:
            _, source_root, backup, original = self._source_and_backup(temp)
            original_write = Path.write_text
            original_write_bytes = Path.write_bytes
            broken = source_root / "Camera1.cs"
            faulted = False

            def interrupted(path, data, *args, **kwargs):
                nonlocal faulted
                if path == broken and not faulted:
                    faulted = True
                    original_write_bytes(path, b"partial-mutated-original")
                    raise OSError("synthetic source install interruption")
                return original_write(path, data, *args, **kwargs)

            def interrupted_bytes(path, data):
                nonlocal faulted
                if path == broken and SHIM.encode("utf-8") in data and not faulted:
                    faulted = True
                    original_write_bytes(path, b"partial-mutated-original")
                    raise OSError("synthetic source install interruption")
                return original_write_bytes(path, data)

            # Fault both original pre-fix write_text() and byte-preserving
            # post-fix write_bytes(), without intercepting restore writes.
            with mock_patch.object(Path, "write_text", interrupted), \
                    mock_patch.object(Path, "write_bytes", interrupted_bytes):
                with self.assertRaisesRegex(OSError, "source install interruption"):
                    self._invoke(source_root, backup)
            self.assertEqual({p: p.read_bytes() for p in original}, original,
                             "Cannot leave an earlier camera source adapted or a torn one")
            self.assertFalse(backup.exists(), "Complete verified rollback permits safe retry")
            self._invoke(source_root, backup)
            for source, before in original.items():
                self.assertEqual((backup / source.name).read_bytes(), before)

    def test_successful_but_corrupt_installed_source_is_reverted(self):
        with tempfile.TemporaryDirectory() as temp:
            _, source_root, backup, original = self._source_and_backup(temp)
            original_write = Path.write_bytes
            broken = source_root / "Camera1.cs"
            injected = False

            def silently_damage_original(path, data):
                nonlocal injected
                if path == broken and SHIM.encode("utf-8") in data and not injected:
                    injected = True
                    return original_write(path, b"silent-source-corruption")
                return original_write(path, data)

            with mock_patch.object(Path, "write_bytes", silently_damage_original):
                with self.assertRaisesRegex(ValueError, "[Ii]nstalled|byte|source"):
                    self._invoke(source_root, backup)
            self.assertTrue(injected)
            self.assertEqual({p: p.read_bytes() for p in original}, original)
            self.assertFalse(backup.exists())
            self._invoke(source_root, backup)
            for source, before in original.items():
                self.assertEqual((backup / source.name).read_bytes(), before)

    def test_original_utf8_bom_survives_exact_mouse_adaptation(self):
        with tempfile.TemporaryDirectory() as temp:
            _, source_root, backup, original = self._source_and_backup(temp)
            first = source_root / "Camera0.cs"
            first.write_bytes(b"\xef\xbb\xbf" + first.read_bytes())
            original[first] = first.read_bytes()
            self._invoke(source_root, backup)
            self.assertTrue(first.read_bytes().startswith(b"\xef\xbb\xbf"))
            self.assertEqual((backup / first.name).read_bytes(), original[first])

    def test_external_hardlinked_original_source_cannot_be_mutated(self):
        with tempfile.TemporaryDirectory() as temp:
            root, source_root, backup, original = self._source_and_backup(temp)
            outside = root / "external-original.cs"
            try:
                outside.hardlink_to(source_root / "Camera0.cs")
            except (OSError, NotImplementedError):
                self.skipTest("Hard links unavailable in test filesystem")
            with self.assertRaisesRegex(ValueError, "[Hh]ardlink"):
                self._invoke(source_root, backup)
            self.assertEqual(outside.read_bytes(), original[source_root / "Camera0.cs"])
            self.assertEqual({p: p.read_bytes() for p in original}, original)
            self.assertFalse(backup.exists())

    def test_exact_counts_and_raw_preservation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            changed, counts = replacement_plan(root)
            self.assertEqual(counts, EXPECTED)
            self.assertEqual(len(changed), 4)
            first = changed[root / 'Camera0.cs']
            self.assertIn(SHIM + '.GetAxis("Mouse X")', first)
            self.assertIn(SHIM + '.GetAxisRaw("Mouse Y")', first)
            self.assertIn(SHIM + '.ApplyCursorLock((gameplay ? CursorLockMode.Locked : CursorLockMode.None));', first)
            self.assertIn('class Camera0', first)
            self.assertIn('Cursor.lockState', (root / 'Camera0.cs').read_text()) # no apply
            self.assertNotIn(SHIM, (root / 'Camera0.cs').read_text())

    def test_unexpected_site_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root, tamper=True)
            with self.assertRaises(ValueError):
                replacement_plan(root)

    def test_comment_spoof_cannot_pass_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            fake = root / "Fake.cs"
            fake.write_text('/* Input.GetAxis("Mouse X"); Cursor.lockState = CursorLockMode.Locked; */\n'
                            '// Input.GetAxis("Mouse Y");\n')
            _, counts = replacement_plan(root)
            self.assertEqual(counts, EXPECTED)

    def test_source_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            (root / "Linked.cs").symlink_to(root / 'Camera0.cs')
            with self.assertRaises(ValueError):
                replacement_plan(root)

    def test_double_patch_cannot_silently_reapply(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            patches, _ = replacement_plan(root)
            for path, text in patches.items():
                path.write_text(text)
            with self.assertRaises(ValueError):
                replacement_plan(root)

    def test_assets_filter_prevents_sdk_rewrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = root / 'Scripts' / 'Assembly-CSharp'
            original.mkdir(parents=True)
            fixture(original)
            vendor = root / 'ThirdParty'
            vendor.mkdir()
            (vendor / 'Vendor.cs').write_text('Input.GetAxis("Mouse X");')
            changed, counts = replacement_plan(root, project_assets=True)
            self.assertEqual(counts, EXPECTED)
            self.assertEqual(len(changed), 4)
            self.assertNotIn(vendor / 'Vendor.cs', changed)

    def test_no_missing_input_silently_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Camera.cs").write_text('class Camera {}')
            with self.assertRaises(ValueError):
                replacement_plan(root)


if __name__ == "__main__":
    unittest.main()
