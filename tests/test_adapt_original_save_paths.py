from collections import Counter
from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest
from scripts.adapt_original_save_paths import adapt, apply, fingerprint, SUFFIX


class SavePathTests(unittest.TestCase):
    def test_path_expression_preserves_literal_and_every_other_source_character(self):
        text = 'var path = root + "World\\\\"; var extension = ".rgd";'
        result = adapt(text, fingerprint(text), Counter({'World\\': 1}))
        self.assertEqual(result.replace(SUFFIX, ''), text)
        self.assertIn('"World\\\\"' + SUFFIX, result)
        self.assertEqual(adapt(result, fingerprint(text), Counter({'World\\': 1})), result)

    def test_comment_and_verbatim_content_are_not_path_expressions(self):
        text = '// "C:\\\\example"\n/* "\\\\" */ var a = @"C:\test"; var b = "\\\\";'
        result = adapt(text, fingerprint(text), Counter({'\\': 1}))
        self.assertEqual(result.count(SUFFIX), 1)

    def test_unknown_source_and_path_inventory_fail(self):
        text = 'var path = "World\\\\";'
        with self.assertRaises(ValueError):
            adapt(text)
        with self.assertRaises(ValueError):
            adapt(text, fingerprint(text), Counter({'Player\\': 1}))

    def test_misplaced_existing_adaptation_fails(self):
        text = 'var path = "World\\\\";'
        with self.assertRaises(ValueError):
            adapt(text + SUFFIX, fingerprint(text), Counter({'World\\': 1}))


    def test_symlinked_assets_root_is_rejected_before_original_save_source_is_touched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'project'
            project.mkdir()
            external = root / 'external-originals' / 'Assembly-CSharp'
            external.mkdir(parents=True)
            source = external / 'SaveAndLoad.cs'
            metadata = source.with_suffix('.cs.meta')
            original = b'class SaveAndLoad { /* synthetic only */ }\n'
            meta_bytes = b'guid: synthetic-original\n'
            source.write_bytes(original)
            metadata.write_bytes(meta_bytes)
            try:
                (project / 'Assets').symlink_to(external.parent, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            backup = root / 'backup'
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// synthetic adapted'):
                with self.assertRaisesRegex(ValueError, 'Unsafe.*Assets'):
                    apply(project, backup, write=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(metadata.read_bytes(), meta_bytes)
            self.assertFalse(backup.exists())

    def test_dangling_backup_leaf_cannot_redirect_original_save_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            source.write_bytes(b'class SaveAndLoad {}\n')
            meta = source.with_suffix('.cs.meta')
            meta.write_bytes(b'guid: synthetic-save\n')
            backup = root / 'backup'
            backup.mkdir()
            outside = root / 'outside-source.cs'
            try:
                (backup / 'SaveAndLoad.cs').symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest('File symlinks unavailable')
            self.assertFalse((backup / 'SaveAndLoad.cs').exists())
            self.assertTrue((backup / 'SaveAndLoad.cs').is_symlink())
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// synthetic adapted'):
                with self.assertRaisesRegex(ValueError, 'backup'):
                    apply(root / 'project', backup, write=True)
            self.assertFalse(outside.exists())
            self.assertEqual(source.read_bytes(), b'class SaveAndLoad {}\n')
            self.assertEqual(meta.read_bytes(), b'guid: synthetic-save\n')

    def test_successful_original_backup_is_complete_and_guid_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            before = b'class SaveAndLoad {}\n'
            meta_before = b'guid: original-guid-must-not-change\n'
            source.write_bytes(before)
            meta = source.with_suffix('.cs.meta')
            meta.write_bytes(meta_before)
            backup = root / 'backup/original-save'
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                result = apply(root / 'project', backup, write=True)
            self.assertTrue(result['changed'])
            self.assertEqual((backup / source.name).read_bytes(), before)
            self.assertEqual((backup / meta.name).read_bytes(), meta_before)
            self.assertEqual(meta.read_bytes(), meta_before)
            self.assertIn(b'// adapted', source.read_bytes())
            self.assertEqual(len(list(backup.iterdir())), 2)

    def test_external_edit_after_complete_backup_must_not_be_overwritten(self):
        # A complete backup proves the OLD original bytes were preserved,
        # not that Unity's source/.meta remained unchanged after promotion.
        # Inject a deterministic independent write after stage.rename(backup).
        for target_name in ("SaveAndLoad.cs", "SaveAndLoad.cs.meta"):
            with self.subTest(target_name=target_name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                source = root / "project/Assets/Assembly-CSharp/SaveAndLoad.cs"
                source.parent.mkdir(parents=True)
                before = b"class SaveAndLoad {}\\n"
                source.write_bytes(before)
                meta = source.with_suffix(".cs.meta")
                metadata = b"guid: original-immutable-until-external-edit\\n"
                meta.write_bytes(metadata)
                backup = root / "original-save-backup"
                external_target = source if target_name.endswith(".cs") else meta
                new_bytes = external_target.read_bytes() + b"// synthetic concurrent source/meta edit\\n"
                rename = Path.rename
                promoted = False

                def external_writer_after_promotion(stage, destination):
                    nonlocal promoted
                    outcome = rename(stage, destination)
                    if destination == backup:
                        promoted = True
                        external_target.write_bytes(new_bytes)
                    return outcome

                with patch("scripts.adapt_original_save_paths.adapt",
                           side_effect=lambda text: text + "\\n// portable paths installed"):
                    with patch.object(Path, "rename", external_writer_after_promotion):
                        with self.assertRaisesRegex(ValueError, "changed after backup staging"):
                            apply(root / "project", backup, write=True)
                    self.assertTrue(promoted)
                    self.assertEqual(external_target.read_bytes(), new_bytes)
                    self.assertFalse(backup.exists(), "new backup should be removed on prewrite refusal")
                    if external_target == meta:
                        self.assertEqual(source.read_bytes(), before)
                    else:
                        self.assertEqual(meta.read_bytes(), metadata)
                    # A later healthy retry recomputes against the CURRENT
                    # source rather than discarding the other writer's edit.
                    report = apply(root / "project", backup, write=True)
                    self.assertTrue(report["changed"])
                    self.assertEqual((backup / target_name).read_bytes(), new_bytes)
                    if external_target == source:
                        self.assertIn(b"synthetic concurrent source", source.read_bytes())
                    else:
                        self.assertEqual(meta.read_bytes(), new_bytes)


    def test_swapped_backup_root_does_not_approve_install_or_delete_foreign_backup(self):
        # A second process may move our just-published backup and create a
        # DIFFERENT directory at the same path. The backup pathname alone is
        # not proof that the bytes belong to this transaction.
        for edit_source in (False, True):
            with self.subTest(edit_source=edit_source), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
                source.parent.mkdir(parents=True)
                before = b'class SaveAndLoad {}\n'
                source.write_bytes(before)
                meta = source.with_suffix('.cs.meta')
                metadata = b'guid: do-not-change\n'
                meta.write_bytes(metadata)
                backup = root / 'original-backup'
                moved = root / 'original-backup-moved-by-other-writer'
                foreign = backup / 'owned-by-another-process.txt'
                original_rename = Path.rename
                promoted = False
                edited = before + b'// independent source edit\n'

                def swap_backup_after_promotion(path, destination):
                    nonlocal promoted
                    outcome = original_rename(path, destination)
                    if destination == backup:
                        promoted = True
                        original_rename(backup, moved)
                        backup.mkdir()
                        foreign.write_bytes(b'FOREIGN BACKUP: NEVER DELETE')
                        if edit_source:
                            source.write_bytes(edited)
                    return outcome

                with patch('scripts.adapt_original_save_paths.adapt',
                           side_effect=lambda text: text + '\n// synthetic portable paths'):
                    with patch.object(Path, 'rename', swap_backup_after_promotion):
                        with self.assertRaises(ValueError):
                            apply(root / 'project', backup, write=True)
                self.assertTrue(promoted)
                self.assertEqual(source.read_bytes(), edited if edit_source else before)
                self.assertEqual(meta.read_bytes(), metadata)
                self.assertEqual(foreign.read_bytes(), b'FOREIGN BACKUP: NEVER DELETE')
                self.assertEqual((moved / source.name).read_bytes(), before)
                self.assertEqual((moved / meta.name).read_bytes(), metadata)

    def test_swapped_backup_root_is_not_deleted_during_write_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            before = b'class SaveAndLoad {}\n'
            source.write_bytes(before)
            meta = source.with_suffix('.cs.meta')
            metadata = b'guid: original\n'
            meta.write_bytes(metadata)
            backup = root / 'backup'
            moved = root / 'owned-backup-moved'
            foreign = backup / 'foreign-owner-proof'
            original_rename = Path.rename
            original_write = Path.write_bytes
            swapped = False

            def replace_backup_then_fail(path, data):
                nonlocal swapped
                if path == source and b'// synthetic portable paths' in data and not swapped:
                    original_write(path, data)
                    original_rename(backup, moved)
                    backup.mkdir()
                    foreign.write_bytes(b'FOREIGN OWNER')
                    swapped = True
                    raise OSError('synthetic failure after source mutation')
                return original_write(path, data)

            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// synthetic portable paths'):
                with patch.object(Path, 'write_bytes', replace_backup_then_fail):
                    with self.assertRaises((ValueError, OSError)):
                        apply(root / 'project', backup, write=True)
            self.assertTrue(swapped)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(meta.read_bytes(), metadata)
            self.assertEqual(foreign.read_bytes(), b'FOREIGN OWNER')
            self.assertEqual((moved / source.name).read_bytes(), before)

    def test_interrupted_metadata_backup_has_no_partial_backup_and_can_retry(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            before = b'class SaveAndLoad {}\n'
            source.write_bytes(before)
            meta = source.with_suffix('.cs.meta')
            meta_before = b'guid: genuine\n'
            meta.write_bytes(meta_before)
            backup = root / 'backups/original-save'
            original_copy = shutil.copy2
            copies = 0

            def fail_second_copy(*args, **kwargs):
                nonlocal copies
                copies += 1
                if copies == 2:
                    raise OSError('synthetic second original backup copy failure')
                return original_copy(*args, **kwargs)

            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                with patch('scripts.adapt_original_save_paths.shutil.copy2',
                           side_effect=fail_second_copy):
                    with self.assertRaisesRegex(OSError, 'second original backup'):
                        apply(root / 'project', backup, write=True)
                self.assertFalse(backup.exists())
                self.assertEqual(list(backup.parent.iterdir()), [])
                self.assertEqual(source.read_bytes(), before)
                self.assertEqual(meta.read_bytes(), meta_before)
                apply(root / 'project', backup, write=True)
            self.assertEqual((backup / source.name).read_bytes(), before)
            self.assertEqual((backup / meta.name).read_bytes(), meta_before)

    def test_source_write_failure_rolls_back_and_allows_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            before = b'class SaveAndLoad {}\n'
            source.write_bytes(before)
            meta = source.with_suffix('.cs.meta')
            meta_before = b'guid: unmodified\n'
            meta.write_bytes(meta_before)
            backup = root / 'backup'
            original_write = Path.write_bytes
            failed = False

            def torn_write(path, data):
                nonlocal failed
                if path == source and b'// adapted' in data and not failed:
                    failed = True
                    original_write(path, b'partial')
                    raise OSError('synthetic partial source install')
                return original_write(path, data)

            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                with patch.object(Path, 'write_bytes', torn_write):
                    with self.assertRaisesRegex(OSError, 'partial source install'):
                        apply(root / 'project', backup, write=True)
                self.assertEqual(source.read_bytes(), before)
                self.assertEqual(meta.read_bytes(), meta_before)
                self.assertFalse(backup.exists())
                apply(root / 'project', backup, write=True)
            self.assertIn(b'// adapted', source.read_bytes())
            self.assertEqual((backup / meta.name).read_bytes(), meta_before)

    def test_existing_empty_backup_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            original = b'class SaveAndLoad {}\n'
            source.write_bytes(original)
            source.with_suffix('.cs.meta').write_bytes(b'guid: original\n')
            backup = root / 'backup'
            backup.mkdir()
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                with self.assertRaisesRegex(ValueError, 'backup already exists'):
                    apply(root / 'project', backup, write=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(list(backup.iterdir()), [])


    def test_linked_project_root_cannot_redirect_save_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            real = root / 'real-project'
            source = real / 'Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            original = b'class SaveAndLoad {}'
            source.write_bytes(original)
            source.with_suffix('.cs.meta').write_bytes(b'guid: synthetic\\n')
            alias = root / 'linked-project'
            try:
                alias.symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            self.assertFalse((alias / 'Assets').is_symlink())
            with self.assertRaisesRegex(ValueError, 'project root'):
                apply(alias, root / 'backup', write=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse((root / 'backup').exists())

    def test_linked_backup_root_cannot_redirect_save_backups(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            original = b'class SaveAndLoad {}'
            source.write_bytes(original)
            source.with_suffix('.cs.meta').write_bytes(b'guid: synthetic\\n')
            outside = root / 'outside'
            outside.mkdir()
            backup = root / 'linked-backup'
            try:
                backup.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            with self.assertRaisesRegex(ValueError, 'backup root'):
                apply(root / 'project', backup, write=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(list(outside.iterdir()), [])

    def test_linked_backup_ancestor_rejected_before_source_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'project'
            (project / 'Assets').mkdir(parents=True)
            outside = root / 'outside'
            outside.mkdir()
            linked = root / 'linked-parent'
            try:
                linked.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Directory symlinks unavailable')
            with self.assertRaisesRegex(ValueError, 'backup root'):
                apply(project, linked / 'backup-folder', write=True)
            self.assertFalse((outside / 'backup-folder').exists())

    def test_hardlinked_source_cannot_mutate_external_original_inode(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            original = b'class SaveAndLoad { /* synthetic */ }\n'
            source.write_bytes(original)
            meta = source.with_suffix('.cs.meta')
            meta_bytes = b'guid: synthetic-unchanged\n'
            meta.write_bytes(meta_bytes)
            outside = root / 'outside-original.cs'
            try:
                outside.hardlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest('Hard links unavailable')
            self.assertFalse(source.is_symlink())
            self.assertGreater(source.stat().st_nlink, 1)
            backup = root / 'backup-original'
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                with self.assertRaisesRegex(ValueError, 'hardlinked'):
                    apply(root / 'project', backup, write=True)
            self.assertEqual(outside.read_bytes(), original)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(meta.read_bytes(), meta_bytes)
            self.assertFalse(backup.exists())

    def test_hardlinked_meta_sidecar_is_refused_without_backup_or_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'project/Assets/Assembly-CSharp/SaveAndLoad.cs'
            source.parent.mkdir(parents=True)
            source_bytes = b'class SaveAndLoad { /* synthetic */ }\n'
            source.write_bytes(source_bytes)
            meta = source.with_suffix('.cs.meta')
            meta_bytes = b'guid: synthetic-unchanged\n'
            meta.write_bytes(meta_bytes)
            outside = root / 'outside-original.cs.meta'
            try:
                outside.hardlink_to(meta)
            except (OSError, NotImplementedError):
                self.skipTest('Hard links unavailable')
            self.assertFalse(meta.is_symlink())
            self.assertGreater(meta.stat().st_nlink, 1)
            backup = root / 'backup-original'
            with patch('scripts.adapt_original_save_paths.adapt',
                       side_effect=lambda text: text + '\n// adapted'):
                with self.assertRaisesRegex(ValueError, 'hardlinked'):
                    apply(root / 'project', backup, write=True)
            self.assertEqual(outside.read_bytes(), meta_bytes)
            self.assertEqual(source.read_bytes(), source_bytes)
            self.assertEqual(meta.read_bytes(), meta_bytes)
            self.assertFalse(backup.exists())
