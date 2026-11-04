import json
from pathlib import Path
import tempfile
import unittest

from scripts.restore_builtin_shaders import restore_project
from scripts.verify_builtin_export_ownership import verify


class EngineOwnershipTests(unittest.TestCase):
    def project(self, root):
        project = root / 'project'
        assets = project / 'Assets'
        assets.mkdir(parents=True)
        (assets / 'custom.shader').write_text('Shader "Custom/Original" { SubShader { Pass {} } }')
        (assets / 'custom.shader.meta').write_text('guid: ' + 'a' * 32 + '\n')
        (assets / 'material.mat').write_text('%YAML 1.1\n--- !u!21 &2100000\nMaterial:\n  m_Shader: {fileID: 5, guid: 0000000000000000f000000000000000, type: 0}\n')
        return project

    def test_no_loose_match_still_fails_without_original_trace_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = self.project(root)
            before = {str(p.relative_to(project)): p.read_bytes() for p in project.rglob('*') if p.is_file()}
            with self.assertRaisesRegex(ValueError, 'No exported built-in'):
                restore_project(project, root / 'backup', {}, {}, b'license')
            self.assertFalse((root / 'backup').exists())
            self.assertEqual(before, {str(p.relative_to(project)): p.read_bytes() for p in project.rglob('*') if p.is_file()})

    def test_forged_success_summary_cannot_replace_exact_reader(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = self.project(root)
            database, reader = root / 'database.json', root / 'reader.json'
            database.write_text('[]')
            reader.write_text(json.dumps({'engine_owned_shader_references_verified': True,
                                          'actual_export_reference_closure_verified': True}))
            with self.assertRaisesRegex(ValueError, 'fingerprint changed'):
                verify(project, root / 'no-originals', root / 'no-trace', database, reader)


if __name__ == '__main__':
    unittest.main()
