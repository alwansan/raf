from pathlib import Path
import tempfile
import unittest
from scripts.restore_builtin_shaders import archive_sources, restore_project, rewrite, ROOT, NOTICE


class BuiltinShaderTests(unittest.TestCase):
    def fixture(self, root):
        project = root / 'project'
        path = project / 'Assets/Shader/standard.shader'
        path.parent.mkdir(parents=True)
        path.write_text('Shader "Standard" { SubShader { Pass {} } }')
        Path(str(path) + '.meta').write_bytes(b'guid: original-standard\n')
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
            Path(str(path) + '.meta').write_text('guid: original')
            custom.write_bytes(path.read_bytes())
            Path(str(custom) + '.meta').write_text('guid: another')
            with self.assertRaisesRegex(ValueError, 'Ambiguous'):
                restore_project(project, root / 'backup', shaders, files, b'notice')

    def test_relative_include_resolves_within_pinned_vendor_layout(self):
        files = {'DefaultResourcesExtra/Terrain/shader.shader': '#include "../common.cginc"',
                 'DefaultResourcesExtra/common.cginc': '// fixture'}
        source, dependencies = rewrite('DefaultResourcesExtra/Terrain/shader.shader', files)
        self.assertEqual(dependencies, {'DefaultResourcesExtra/common.cginc'})
        self.assertIn(ROOT + 'DefaultResourcesExtra/common.cginc', source)

    def test_in_project_backup_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path, custom, shaders, files = self.fixture(root)
            with self.assertRaisesRegex(ValueError, 'outside'):
                restore_project(project, project / 'backup', shaders, files, b'notice')
