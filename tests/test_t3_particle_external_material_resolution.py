import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/t3_particle_external_material_resolution.py"
spec = importlib.util.spec_from_file_location("external_particle_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ExternalParticleAuditTests(unittest.TestCase):
    def test_unique_missing_duplicate_and_bom_crlf(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a, b, c = "a"*32, "b"*32, "c"*32
            for name, guid in [("one", a), ("two", b), ("three", b)]:
                (root / (name + ".mat.meta")).write_text("guid: " + guid + "\n")
                (root / (name + ".mat")).write_text("%YAML 1.1\n")
            lines = "".join("  - {fileID: 2100000, guid: " + g + ", type: 2}\r\n" for g in (a,b,c))
            (root / "effect.prefab").write_bytes(("\ufeff--- !u!199 &1\r\nParticleSystemRenderer:\r\n  m_Materials:\r\n" + lines).encode("utf-8"))
            result = module.audit(root)
            self.assertEqual(result["external_slots"], 3)
            self.assertEqual(result["external_guid_unique_mat_meta"], 1)
            self.assertEqual(result["external_guid_duplicate_mat_meta"], 1)
            self.assertEqual(result["external_guid_not_in_mat_meta_tree"], 1)

    def test_orphan_metadata_does_not_resolve_missing_material(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            guid = "d" * 32
            (root / "orphan.mat.meta").write_text("guid: " + guid + "\n")
            (root / "effect.prefab").write_text(
                "--- !u!199 &1\nParticleSystemRenderer:\n  m_Materials:\n"
                "  - {fileID: 2100000, guid: " + guid + ", type: 2}\n"
            )
            result = module.audit(root)
            self.assertEqual(result["orphan_mat_meta"], 1)
            self.assertEqual(result["external_guid_not_in_mat_meta_tree"], 1)
            self.assertNotIn("external_guid_unique_mat_meta", result)

    def test_empty_material_does_not_resolve_guid(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            guid = "e" * 32
            (root / "empty.mat.meta").write_text("guid: " + guid + "\n")
            (root / "empty.mat").write_bytes(b"")
            (root / "effect.prefab").write_text(
                "--- !u!199 &1\nParticleSystemRenderer:\n  m_Materials:\n"
                "  - {fileID: 2100000, guid: " + guid + ", type: 2}\n"
            )
            result = module.audit(root)
            self.assertEqual(result["empty_mat_source"], 1)
            self.assertEqual(result["external_guid_not_in_mat_meta_tree"], 1)
            self.assertNotIn("external_guid_unique_mat_meta", result)

if __name__ == "__main__":
    unittest.main()
