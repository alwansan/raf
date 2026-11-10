"""Unresolved GUID digest must be stable, countable and never leak raw identities."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t3_unity_guid_link_audit.py"
spec = importlib.util.spec_from_file_location("t3_guid_hash_audit", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HashedUnresolvedTests(unittest.TestCase):
    def test_repeat_unresolved_identity_across_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = "a" * 32
            present = "b" * 32
            (root / "known.mat.meta").write_text("guid: " + present, encoding="utf-8")
            (root / "item.mat").write_text(
                "m_Shader: {fileID: 4800000, guid: " + missing + ", type: 3}\n"
                "m_Texture: {guid: " + present + ", fileID: 2800000, type: 3}\n",
                encoding="utf-8",
            )
            (root / "smoke.prefab").write_text(
                "m_Material: {guid: " + missing + ", fileID: 2100000, type: 2}\n"
                "m_Material2: {fileID: 2100000, guid: " + missing + ", type: 2}\n",
                encoding="utf-8",
            )
            result = module.inspect(root)
            prefix = hashlib.sha256(missing.encode("ascii")).hexdigest()[:16]
            self.assertEqual(result["reference_counts"]["unresolved_in_supplied_tree"], 3)
            self.assertEqual(result["reference_counts"]["resolved_in_supplied_tree"], 1)
            self.assertEqual(result["unresolved_hashed_identity_by_source_extension"], [
                {"source_extension": ".mat", "guid_sha256_prefix16": prefix, "references": 1},
                {"source_extension": ".prefab", "guid_sha256_prefix16": prefix, "references": 2},
            ])
            self.assertNotIn(missing, str(result))
            self.assertNotIn(present, str(result))

    def test_no_unresolved_has_empty_digest_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "empty.mat").write_text("m_Shader: {fileID: 0}\n", encoding="utf-8")
            self.assertEqual(module.inspect(root)["unresolved_hashed_identity_by_source_extension"], [])


if __name__ == "__main__":
    unittest.main()
