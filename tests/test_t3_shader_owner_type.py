#!/usr/bin/env python3
"""Synthetic fixtures only: no proprietary game assets."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t3_material_shader_binding_audit.py"
spec = importlib.util.spec_from_file_location("t3_shader_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
G = "a" * 32

class ShaderOwnerTests(unittest.TestCase):
    def check(self, owners, expected):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sample.mat").write_text(
                "Material:\n  m_Shader: {fileID: 4800000, guid: " + G + ", type: 3}\n"
            )
            for idx, ext in enumerate(owners):
                (root / ("owner" + str(idx) + ext + ".meta")).write_text("guid: " + G + "\n")
            counts = module.audit(root)["counts"]
            self.assertEqual(counts.get(expected), 1, counts)

    def test_valid_shader(self):
        self.check([".shader"], "shader_guid_unique_in_supplied_tree")

    def test_texture_owner_is_not_shader(self):
        self.check([".png"], "shader_guid_points_to_non_shader_meta")

    def test_duplicate_shader_guid(self):
        self.check([".shader", ".shader"], "shader_guid_ambiguous_duplicate_meta")

if __name__ == "__main__":
    unittest.main()
