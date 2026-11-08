import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/t3_particle_renderer_yaml_audit.py"
spec = importlib.util.spec_from_file_location("particle_audit", SCRIPT)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)

class ParticleRendererAuditTests(unittest.TestCase):
    def test_three_pointer_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "effect.prefab").write_text(
                "--- !u!1 &1\nGameObject:\n--- !u!199 &2\nParticleSystemRenderer:\n"
                "  m_Materials:\n  - {fileID: 0}\n"
                "  - {fileID: 2100000, guid: " + "a"*32 + ", type: 2}\n"
                "  - {fileID: 2100000}\n  m_Enabled: 1\n", encoding="utf-8")
            result = audit_module.audit(tmp)
            self.assertEqual(result["particle_renderers"], 1)
            self.assertEqual(result["material_slots"], 3)
            self.assertEqual(result["null_material_slots"], 1)
            self.assertEqual(result["external_material_slots"], 1)
            self.assertEqual(result["local_material_slots"], 1)

    def test_negative_fileid_is_not_valid_local_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "effect.prefab").write_text(
                "--- !u!199 &2\nParticleSystemRenderer:\n"
                "  m_Materials:\n  - {fileID: -2100000}\n"
                "  - {fileID: 2100000}\n", encoding="utf-8")
            result = audit_module.audit(tmp)
            self.assertEqual(result["material_slots"], 2)
            self.assertEqual(result["invalid_negative_fileid_slots"], 1)
            self.assertEqual(result["local_material_slots"], 1)

    def test_null_fileid_with_nonzero_guid_is_not_valid_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "effect.prefab").write_text(
                "--- !u!199 &2\nParticleSystemRenderer:\n"
                "  m_Materials:\n"
                "  - {fileID: 0, guid: " + "a"*32 + ", type: 2}\n"
                "  - {fileID: 0}\n"
                "  - {fileID: 0, guid: " + "0"*32 + ", type: 2}\n",
                encoding="utf-8")
            result = audit_module.audit(tmp)
            self.assertEqual(result["material_slots"], 3)
            self.assertEqual(result["invalid_null_fileid_with_guid_slots"], 1)
            self.assertEqual(result["null_material_slots"], 2)

    def test_local_material_anchor_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "effect.prefab").write_text(
                "--- !u!21 &2100000\nMaterial:\n"
                "--- !u!1 &3000000\nGameObject:\n"
                "--- !u!21 &4000000\nMaterial:\n"
                "--- !u!1 &4000000\nGameObject:\n"
                "--- !u!199 &2\nParticleSystemRenderer:\n"
                "  m_Materials:\n"
                "  - {fileID: 2100000}\n"
                "  - {fileID: 9999999}\n"
                "  - {fileID: 3000000}\n"
                "  - {fileID: 4000000}\n",
                encoding="utf-8")
            result = audit_module.audit(tmp)
            self.assertEqual(result["local_material_slots"], 4)
            self.assertEqual(result["local_material_target_valid"], 1)
            self.assertEqual(result["local_material_target_missing"], 1)
            self.assertEqual(result["local_material_target_wrong_class"], 1)
            self.assertEqual(result["local_material_target_ambiguous"], 1)

    def test_empty_and_malformed(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "effect.prefab").write_text(
                "--- !u!199 &1\nParticleSystemRenderer:\n  m_Materials: []\n"
                "--- !u!199 &2\nParticleSystemRenderer:\n"
                "  m_Materials:\n  - invalid\n", encoding="utf-8")
            result = audit_module.audit(tmp)
            self.assertEqual(result["empty_material_lists"], 1)
            self.assertEqual(result["unparsed_material_slots"], 1)

if __name__ == "__main__":
    unittest.main()
