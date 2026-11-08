"""Synthetic-only regression for orphan Shader.meta false resolution."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t3_material_shader_link_audit.py"
spec = importlib.util.spec_from_file_location("t3_material_shader_link_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
GUID = "abcdef0123456789abcdef0123456789"


class ShaderMetaOrphanTest(unittest.TestCase):
    def test_orphan_meta_does_not_resolve_material(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "smoke.mat").write_text(
                "%YAML 1.1\\nMaterial:\\n  m_Shader: {fileID: 4800000, guid: " + GUID + ", type: 3}\\n",
                encoding="utf-8",
            )
            (root / "smoke.shader.meta").write_text("fileFormatVersion: 2\\nguid: " + GUID + "\\n", encoding="utf-8")
            orphan = module.audit(root)
            self.assertEqual(orphan["shader_meta_without_source"], 1)
            self.assertEqual(orphan["shader_guid_unresolved_in_scan"], 1)
            self.assertEqual(orphan["shader_guid_resolved_in_scan"], 0)
            (root / "smoke.shader").write_text('Shader "Synthetic/Smoke" {}\\n', encoding="utf-8")
            paired = module.audit(root)
            self.assertEqual(paired["shader_meta_without_source"], 0)
            self.assertEqual(paired["shader_guid_unresolved_in_scan"], 0)
            self.assertEqual(paired["shader_guid_resolved_in_scan"], 1)


if __name__ == "__main__":
    unittest.main()
