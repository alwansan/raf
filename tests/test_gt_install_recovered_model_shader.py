"""Exercise restored model shader installation on a synthetic Unity export."""
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from scripts.gt_install_recovered_model_shader import install
from scripts.gt_original_921_shaderlab import EXPECTED_ROUTES


class RecoveredModelShaderInstallationTests(unittest.TestCase):
    def test_swaps_only_shader_bytes_after_receipt_and_preserves_guid(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            assets = project / "Assets"
            assets.mkdir(parents=True)
            shader = assets / "Model.shader"
            meta = shader.with_suffix(".shader.meta")
            guid = "a" * 32
            original = b'Shader "Model" {} // DummyShaderTextExporter\n'
            candidate = b'Shader "Model" { SubShader { Pass {} } }\n'
            metadata = f"fileFormatVersion: 2\nguid: {guid}\n".encode()
            shader.write_bytes(original)
            meta.write_bytes(metadata)
            trace = {"schema_version": 1, "export_instance": "b" * 32, "objects": [{
                "class_id": 48,
                "source": {"owner": "sharedassets0.assets", "path_id": 110},
                "export": {"file_id": 4800000, "guid": guid, "type": 3},
            }]}
            receipt = {
                "candidate_sha256": sha256(candidate).hexdigest(),
                "compiled_program_table_verified": True,
                "engine_keywords_verified": True,
                "vertex_and_fragment_entrypoints_verified": True,
                "vulkan_platform_only": True,
                "vertex_routes_by_pass": list(EXPECTED_ROUTES),
                "fragment_routes_by_pass": list(EXPECTED_ROUTES),
            }
            source_key = "sharedassets0.assets", 110
            backup = root / "backup"
            with self.assertRaisesRegex(ValueError, "bundle_evidence_missing"):
                install(project, trace, source_key, candidate + b" ", receipt, backup)
            self.assertFalse(backup.exists())
            self.assertEqual(shader.read_bytes(), original)

            result = install(project, trace, source_key, candidate, receipt, backup)
            self.assertEqual(result["vulkan_routes_installed"], 33)
            self.assertEqual(shader.read_bytes(), candidate)
            self.assertEqual(meta.read_bytes(), metadata)
            self.assertEqual((backup / "original.shader").read_bytes(), original)
            self.assertEqual((backup / "original.shader.meta").read_bytes(), metadata)

    def test_billboard_requires_both_vulkan_forward_passes_before_guid_preserving_install(self):
        from scripts.gt_original_921_shaderlab import BILLBOARD_ROUTES
        self.assertEqual(list(BILLBOARD_ROUTES), [4, 5])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            project = root / "project"
            assets = project / "Assets"
            assets.mkdir(parents=True)
            shader = assets / "Billboard.shader"
            meta = assets / "Billboard.shader.meta"
            guid = "c" * 32
            original = b'Shader "BillboardFade" {} // DummyShaderTextExporter\n'
            candidate = b'Shader "BillboardFade" { SubShader { Pass {} Pass {} } }\n'
            original_meta = f"fileFormatVersion: 2\nguid: {guid}\n".encode()
            shader.write_bytes(original)
            meta.write_bytes(original_meta)
            trace = {"schema_version": 1, "export_instance": "d" * 32, "objects": [{
                "class_id": 48,
                "source": {"owner": "sharedassets0.assets", "path_id": 111},
                "export": {"file_id": 4800000, "guid": guid, "type": 3},
            }]}
            receipt = {
                "candidate_sha256": sha256(candidate).hexdigest(),
                "compiled_program_table_verified": True,
                "engine_keywords_verified": True,
                "vertex_and_fragment_entrypoints_verified": True,
                "vulkan_platform_only": True,
                "vertex_routes_by_pass": [4, 5],
                "fragment_routes_by_pass": [4, 4],
            }
            source_key = "sharedassets0.assets", 111
            backup = root / "backup"
            with self.assertRaisesRegex(ValueError, "model_shader_bundle_evidence_missing"):
                install(project, trace, source_key, candidate, receipt, backup)
            self.assertEqual(shader.read_bytes(), original)
            self.assertEqual(meta.read_bytes(), original_meta)
            self.assertFalse(backup.exists())
            receipt["fragment_routes_by_pass"] = [4, 5]
            result = install(project, trace, source_key, candidate, receipt, backup)
            self.assertEqual(result["vulkan_routes_installed"], 9)
            self.assertTrue(result["original_export_guid_preserved"])
            self.assertEqual(shader.read_bytes(), candidate)
            self.assertEqual(meta.read_bytes(), original_meta)
            self.assertEqual((backup / "original.shader.meta").read_bytes(), original_meta)
