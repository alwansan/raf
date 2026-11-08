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
            lines = "".join("  - {fileID: 2100000, guid: " + g + ", type: 2}\r\n" for g in (a,b,c))
            (root / "effect.prefab").write_bytes(("\ufeff--- !u!199 &1\r\nParticleSystemRenderer:\r\n  m_Materials:\r\n" + lines).encode("utf-8"))
            result = module.audit(root)
            self.assertEqual(result["external_slots"], 3)
            self.assertEqual(result["external_guid_unique_mat_meta"], 1)
            self.assertEqual(result["external_guid_duplicate_mat_meta"], 1)
            self.assertEqual(result["external_guid_not_in_mat_meta_tree"], 1)

if __name__ == "__main__":
    unittest.main()
