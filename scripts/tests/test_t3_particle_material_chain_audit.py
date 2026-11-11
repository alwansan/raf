#!/usr/bin/env python3
"""Synthetic regression fixtures: no game assets or original GUIDs."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from t3_particle_material_chain_audit import census

GUID = "0123456789abcdef0123456789abcdef"


class ParticleMaterialAuditTests(unittest.TestCase):
    def audit(self, materials):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.prefab").write_text(
                "--- !u!199 &123\nParticleSystemRenderer:\n  m_Materials: "
                + materials + "\n--- !u!1 &456\nGameObject:\n",
                encoding="utf-8",
            )
            return census(root, salt="test-salt")["counts"]

    def test_flow_array_external_and_null(self):
        counts = self.audit("[{fileID: 2100000, guid: " + GUID
                            + ", type: 2}, {fileID: 0}]")
        self.assertEqual(counts.get("particle_renderers"), 1)
        self.assertEqual(counts.get("external_material_slots"), 1)
        self.assertEqual(counts.get("null_material_slots"), 1)
        self.assertEqual(counts.get("unparsed_material_entries", 0), 0)

    def test_inline_empty_is_not_missing(self):
        counts = self.audit("[]")
        self.assertEqual(counts.get("renderers_with_empty_material_list"), 1)
        self.assertEqual(counts.get("renderers_without_material_list", 0), 0)

    def test_unknown_inline_is_explicitly_unsupported(self):
        counts = self.audit("[{fileID: 12}, invalid]")
        self.assertEqual(counts.get("unsupported_inline_material_lists"), 1)
        self.assertEqual(counts.get("local_or_builtin_material_slots", 0), 0)

    def test_block_array_still_supported(self):
        counts = self.audit("\n  - {fileID: 2100000, guid: " + GUID
                            + ", type: 2}")
        self.assertEqual(counts.get("external_material_slots"), 1)


if __name__ == "__main__":
    unittest.main()
