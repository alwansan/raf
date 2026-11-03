"""A9 synthetic exported ShaderLab identity tests. No original shader sources or assets."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from scripts.restore_builtin_shaders import restore_project


def fixture(root, shader_body):
    project = root / "project"
    file = project / "Assets/Shaders/exported.shader"
    file.parent.mkdir(parents=True)
    file.write_text(shader_body, encoding="utf-8")
    Path(str(file) + ".meta").write_bytes(b"guid: " + b"a" * 32 + b"\n")
    files = {
        "DefaultResourcesExtra/Standard.shader": 'Shader "Standard" { Pass { } }',
        "DefaultResourcesExtra/Legacy.shader": 'Shader "Legacy" { Pass { } }',
    }
    shaders = {
        "Standard": "DefaultResourcesExtra/Standard.shader",
        "Legacy": "DefaultResourcesExtra/Legacy.shader",
    }
    return project, file, shaders, files


class A9BuiltinIdentityTests(unittest.TestCase):
    def test_comment_only_builtin_name_does_not_replace_custom_shader(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = '/* Shader "Standard" */\nShader "Raft/PrivateCustom" { SubShader { Pass {} } }'
            project, file, shaders, files = fixture(root, original)
            with self.assertRaisesRegex(ValueError, "No exported built-in shader identities matched"):
                restore_project(project, root / "backup", shaders, files, b"license")
            self.assertEqual(file.read_text(), original)
            self.assertFalse((root / "backup").exists())

    def test_line_comment_cannot_preempt_actual_standard_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = '// Shader "Legacy"\nShader "Standard" { SubShader { Pass {} } }'
            project, file, shaders, files = fixture(root, original)
            self.assertEqual(restore_project(project, root / "backup", shaders, files, b"license"), 1)
            self.assertEqual(file.read_text(), files["DefaultResourcesExtra/Standard.shader"])
            self.assertEqual(Path(str(file) + ".meta").read_bytes(), b"guid: " + b"a" * 32 + b"\n")
            self.assertEqual((root / "backup/Shaders/exported.shader").read_text(), original)

    def test_comment_embedded_in_shader_name_does_not_strip_real_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = 'Shader "Foo//Bar" { SubShader { Pass {} } }'
            project, file, shaders, files = fixture(root, original)
            shaders["Foo//Bar"] = "DefaultResourcesExtra/Standard.shader"
            self.assertEqual(restore_project(project, root / "backup", shaders, files, b"license"), 1)
            self.assertEqual(file.read_text(), files["DefaultResourcesExtra/Standard.shader"])

    def test_zero_match_gives_aggregate_only_diagnostics_without_bypass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, file, shaders, files = fixture(root,
                '/* Shader "Standard" */\nShader "Raft/PrivateCustom" { SubShader { Pass {} } }')
            output = StringIO()
            with redirect_stdout(output), self.assertRaisesRegex(ValueError, "No exported built-in shader identities matched"):
                restore_project(project, root / "backup", shaders, files, b"license")
            audit = output.getvalue()
            self.assertIn("RAFT_BUILTIN_EXPORT_MATCH_AUDIT", audit)
            self.assertIn('"matched_identities": 0', audit)
            self.assertIn('"shader_files": 1', audit)
            self.assertNotIn("Raft/PrivateCustom", audit)
            self.assertNotIn("Standard", audit)
            self.assertFalse((root / "backup").exists())


if __name__ == "__main__":
    unittest.main()
