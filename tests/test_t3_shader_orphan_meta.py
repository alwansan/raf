#!/usr/bin/env python3
"""Synthetic-only regression: .shader.meta is not a real shader asset."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t3_material_shader_binding_audit.py"
spec = importlib.util.spec_from_file_location("t3_shader_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ShaderOrphanMetaTest(unittest.TestCase):
    def test_orphan_then_present(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            guid = "1234567890abcdef1234567890abcdef"
            (root / "Example.shader.meta").write_text("fileFormatVersion: 2\nguid: " + guid + "\n", encoding="utf-8")
            (root / "Example.mat").write_text(
                "%YAML 1.1\nMaterial:\n  m_Shader: {fileID: 4800000, guid: " + guid + ", type: 3}\n",
                encoding="utf-8")
            result = module.audit(root)["counts"]
            self.assertEqual(result.get("shader_guid_orphan_meta_without_asset"), 1)
            self.assertEqual(result.get("shader_guid_unique_in_supplied_tree", 0), 0)
            (root / "Example.shader").write_text('Shader "Synthetic" {}\n', encoding="utf-8")
            result = module.audit(root)["counts"]
            self.assertEqual(result.get("shader_guid_unique_in_supplied_tree"), 1)
            self.assertEqual(result.get("shader_guid_orphan_meta_without_asset", 0), 0)

if __name__ == "__main__":
    unittest.main()
