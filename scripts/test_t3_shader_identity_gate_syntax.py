#!/usr/bin/env python3
"""Regression checks for T3 structural shader link gate (no original provenance claim)."""
import tempfile
import unittest
from pathlib import Path

from t3_shader_identity_gate import check

GUID = "a" * 32

class IdentityGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "particle.shader").write_text('Shader "Test" { SubShader { Pass {} } }')
        (self.root / "particle.shader.meta").write_text(f"guid: {GUID}\n")
        self.manifest = dict(source_sha256="b" * 64, source_shader_id=48,
                             export_shader_guid=GUID, shader_path="particle.shader",
                             material_paths=["particle.mat"])

    def material(self, text):
        (self.root / "particle.mat").write_text(text)

    def test_valid_pointer(self):
        self.material(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\n")
        self.assertEqual(check(self.root, self.manifest)["status"], "STRUCTURAL_LINK_ONLY")

    def test_comment_only_pointer_is_rejected(self):
        self.material(f"# m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\n")
        with self.assertRaisesRegex(ValueError, "material_shader_link_mismatch"):
            check(self.root, self.manifest)

    def test_inline_comment_accepted(self):
        self.material(f"  m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}} # authored\n")
        self.assertEqual(check(self.root, self.manifest)["matched_materials"], 1)

    def test_empty_shader_rejected(self):
        self.material(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\n")
        (self.root / "particle.shader").write_text("")
        with self.assertRaisesRegex(ValueError, "missing_shader_declaration"):
            check(self.root, self.manifest)

    def test_comment_only_shader_rejected(self):
        self.material(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\n")
        (self.root / "particle.shader").write_text("// Shader \"Fake\" { }\n")
        with self.assertRaisesRegex(ValueError, "missing_shader_declaration"):
            check(self.root, self.manifest)

    def test_multiline_shader_declaration_accepted(self):
        self.material(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\n")
        (self.root / "particle.shader").write_text('Shader "Test"\n{ SubShader { Pass {} } }')
        self.assertEqual(check(self.root, self.manifest)["status"], "STRUCTURAL_LINK_ONLY")

    def test_duplicate_real_pointer_rejected(self):
        line = f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\n"
        self.material(line + line)
        with self.assertRaisesRegex(ValueError, "material_shader_link_mismatch"):
            check(self.root, self.manifest)


    def test_block_comment_shader_declaration_rejected(self):
        self.material(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\\n")
        (self.root / "particle.shader").write_text('/*\\nShader "Fake" {}\\n*/')
        with self.assertRaisesRegex(ValueError, "missing_shader_declaration"):
            check(self.root, self.manifest)

    def test_unterminated_block_comment_declaration_rejected(self):
        self.material(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\\n")
        (self.root / "particle.shader").write_text('/* unclosed\\nShader "Fake" {}')
        with self.assertRaisesRegex(ValueError, "missing_shader_declaration"):
            check(self.root, self.manifest)

    def test_valid_declaration_after_block_comment(self):
        self.material(f"m_Shader: {{fileID: 4800000, guid: {GUID}, type: 3}}\\n")
        (self.root / "particle.shader").write_text('/* Shader "Fake" {} */\\nShader "Real" {}')
        self.assertEqual(check(self.root, self.manifest)["status"], "STRUCTURAL_LINK_ONLY")

if __name__ == "__main__":
    unittest.main()
