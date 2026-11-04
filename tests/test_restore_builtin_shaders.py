from pathlib import Path
import os
import tempfile
import unittest
from unittest import mock
from scripts.restore_builtin_shaders import archive_sources, restore_project, rewrite, ROOT, NOTICE


class BuiltinShaderTests(unittest.TestCase):
    def fixture(self, root):
        project = root / 'project'
        path = project / 'Assets/Shader/standard.shader'
        path.parent.mkdir(parents=True)
        path.write_text('Shader "Standard" { SubShader { Pass {} } }')
        Path(str(path) + '.meta').write_bytes(b'guid: ' + b'a' * 32 + b'\n')
        custom = project / 'Assets/Shader/raft.shader'
        custom.write_text('Shader "Raft/Custom" { SubShader { Pass {} } }')
        files = {'DefaultResourcesExtra/Standard.shader': 'Shader "Standard" { CGPROGRAM\n#include "UnityCG.cginc"\nENDCG }',
                 'CGIncludes/UnityCG.cginc': '#include "UnityVariables.cginc"',
                 'CGIncludes/UnityVariables.cginc': '// actual fixture include'}
        return project, path, custom, {'Standard': 'DefaultResourcesExtra/Standard.shader'}, files

    def test_changed_or_non_archive_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            archive_sources(b'not authenticated')

    def test_restore_preserves_metadata_custom_shader_and_exact_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            before, metadata, untouched = path.read_bytes(), Path(str(path) + '.meta').read_bytes(), custom.read_bytes()
            self.assertEqual(restore_project(project, root / 'backup', shaders, files, b'MIT notice'), 1)
            self.assertEqual(Path(str(path) + '.meta').read_bytes(), metadata)
            self.assertEqual(custom.read_bytes(), untouched)
            self.assertEqual((root / 'backup/Shader/standard.shader').read_bytes(), before)
            self.assertIn(ROOT + 'CGIncludes/UnityCG.cginc', path.read_text())
            self.assertIn(ROOT + 'CGIncludes/UnityVariables.cginc', (project / ROOT / 'CGIncludes/UnityCG.cginc').read_text())
            self.assertEqual((project / NOTICE).read_bytes(), b'MIT notice')

    def test_missing_dependency_fails_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            before = path.read_bytes()
            del files['CGIncludes/UnityVariables.cginc']
            with self.assertRaisesRegex(ValueError, 'Unresolved'):
                restore_project(project, root / 'backup', shaders, files, b'notice')
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse((root / 'backup').exists())

    def test_conflicting_include_fails_without_modification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            before = path.read_bytes()
            include = project / ROOT / 'CGIncludes/UnityCG.cginc'
            include.parent.mkdir(parents=True)
            include.write_text('different version')
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                restore_project(project, root / 'backup', shaders, files, b'notice')
            self.assertEqual(path.read_bytes(), before)

    def test_missing_meta_and_duplicate_identity_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            Path(str(path) + '.meta').unlink()
            with self.assertRaisesRegex(ValueError, 'metadata'):
                restore_project(project, root / 'backup', shaders, files, b'notice')
            Path(str(path) + '.meta').write_text('guid: ' + 'a' * 32)
            custom.write_bytes(path.read_bytes())
            Path(str(custom) + '.meta').write_text('guid: ' + 'b' * 32)
            with self.assertRaisesRegex(ValueError, 'Ambiguous'):
                restore_project(project, root / 'backup', shaders, files, b'notice')

    def test_relative_include_resolves_within_pinned_vendor_layout(self):
        files = {'DefaultResourcesExtra/Terrain/shader.shader': '#include "../common.cginc"',
                 'DefaultResourcesExtra/common.cginc': '// fixture'}
        source, dependencies = rewrite('DefaultResourcesExtra/Terrain/shader.shader', files)
        self.assertEqual(dependencies, {'DefaultResourcesExtra/common.cginc'})
        self.assertIn(ROOT + 'DefaultResourcesExtra/common.cginc', source)

    def test_line_comment_include_is_not_a_dependency(self):
        files = {'DefaultResourcesExtra/a.shader': 'Shader "Standard" {\n// #include "missing.cginc"\n#include "active.cginc"\n}',
                 'CGIncludes/active.cginc': '// official include fixture'}
        text, deps = rewrite('DefaultResourcesExtra/a.shader', files)
        self.assertEqual(deps, {'CGIncludes/active.cginc'})
        self.assertIn('// #include "missing.cginc"', text)
        self.assertIn(ROOT + 'CGIncludes/active.cginc', text)

    def test_inactive_block_and_unterminated_comment_includes_are_not_dependencies(self):
        for comment in ('/* #include "missing.cginc" */', '/*\n#include "missing.cginc"'):
            files = {'DefaultResourcesExtra/a.shader': 'Shader "Standard" {\n' + comment}
            text, deps = rewrite('DefaultResourcesExtra/a.shader', files)
            self.assertEqual(deps, set())
            self.assertEqual(text, files['DefaultResourcesExtra/a.shader'])

    def test_include_path_with_literal_comment_markers_is_still_active(self):
        files = {'DefaultResourcesExtra/a.shader': '#include "dir//active.cginc"',
                 'DefaultResourcesExtra/dir/active.cginc': '// official include fixture'}
        text, deps = rewrite('DefaultResourcesExtra/a.shader', files)
        self.assertEqual(deps, {'DefaultResourcesExtra/dir/active.cginc'})
        self.assertIn(ROOT + 'DefaultResourcesExtra/dir/active.cginc', text)

    def test_in_project_backup_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            with self.assertRaisesRegex(ValueError, 'outside'):
                restore_project(project, project / 'backup', shaders, files, b'notice')

    def test_b13_rename_failure_cannot_truncate_original_shader(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            original = path.read_bytes()
            metadata = Path(str(path) + '.meta').read_bytes()
            with mock.patch('scripts.restore_builtin_shaders.os.replace',
                            side_effect=OSError('injected shader rename failure')):
                with self.assertRaisesRegex(OSError, 'injected shader rename failure'):
                    restore_project(project, root / 'backup', shaders, files, b'notice')
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(Path(str(path) + '.meta').read_bytes(), metadata)
            self.assertEqual((root / 'backup/Shader/standard.shader').read_bytes(), original)
            self.assertEqual((root / 'backup/Shader/standard.shader.meta').read_bytes(), metadata)
            self.assertFalse(list(path.parent.glob('*.b13.tmp')))
            self.assertFalse(list(path.parent.glob('.*.b13.tmp')))
            self.assertFalse((project / NOTICE).exists())
            self.assertTrue(custom.is_file())

    def test_b13_concurrent_source_edit_after_backup_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            before = path.read_bytes()
            outside_change = b'Shader "Standard" { /* external post-backup edit */ }'
            backup_meta = root / 'backup/Shader/standard.shader.meta'
            saved_write = Path.write_bytes

            def inject_change(target, content):
                result = saved_write(target, content)
                if target == backup_meta:
                    saved_write(path, outside_change)
                return result

            with mock.patch.object(Path, 'write_bytes', autospec=True,
                                   side_effect=inject_change):
                with self.assertRaisesRegex(ValueError, 'changed after backup'):
                    restore_project(project, root / 'backup', shaders, files, b'notice')
            self.assertEqual(path.read_bytes(), outside_change)
            self.assertEqual((root / 'backup/Shader/standard.shader').read_bytes(), before)
            self.assertFalse((project / NOTICE).exists())
            self.assertFalse(list(path.parent.glob('.*.b13.tmp')))

    def test_b13_second_shader_failure_rolls_back_first_atomically(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            second = path.parent / 'z_second.shader'
            second.write_text('Shader "Diffuse" { SubShader { Pass {} } }')
            Path(str(second) + '.meta').write_bytes(b'guid: ' + b'b' * 32 + b'\n')
            shaders['Diffuse'] = 'DefaultResourcesExtra/Diffuse.shader'
            files['DefaultResourcesExtra/Diffuse.shader'] = 'Shader "Diffuse" { HLSLPROGRAM\nENDHLSL }'
            first_original, second_original = path.read_bytes(), second.read_bytes()
            original_replace = os.replace

            def fail_second(source, target):
                if Path(target) == second:
                    raise OSError('injected second shader failure')
                return original_replace(source, target)

            with mock.patch('scripts.restore_builtin_shaders.os.replace',
                            side_effect=fail_second):
                with self.assertRaisesRegex(OSError, 'injected second shader failure'):
                    restore_project(project, root / 'backup', shaders, files, b'notice')
            self.assertEqual(path.read_bytes(), first_original)
            self.assertEqual(second.read_bytes(), second_original)
            self.assertEqual((root / 'backup/Shader/standard.shader').read_bytes(), first_original)
            self.assertEqual((root / 'backup/Shader/z_second.shader').read_bytes(), second_original)
            self.assertFalse((project / NOTICE).exists())
            self.assertFalse(list(path.parent.glob('.*.b13.tmp')))

    def test_b13_corrupt_backup_fails_before_any_shader_source_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            original = path.read_bytes()
            backup_meta = root / 'backup/Shader/standard.shader.meta'
            backed_shader = root / 'backup/Shader/standard.shader'
            saved_write = Path.write_bytes

            def corrupt_backup(target, content):
                result = saved_write(target, content)
                if target == backup_meta:
                    saved_write(backed_shader, b'corrupted backup')
                return result

            with mock.patch.object(Path, 'write_bytes', autospec=True,
                                   side_effect=corrupt_backup):
                with self.assertRaisesRegex(ValueError, 'Incomplete original.*backup'):
                    restore_project(project, root / 'backup', shaders, files, b'notice')
            self.assertEqual(path.read_bytes(), original)
            self.assertFalse((root / 'backup').exists())
            self.assertFalse((project / NOTICE).exists())
