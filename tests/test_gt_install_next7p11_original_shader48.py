"""Fail-closed source-free tests for exact next7p11 original GUID installer."""
import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.gt_install_next7p11_original_shader48 import (
    ROUTES, install, source_identity, verify_receipt,
)


class OriginalNext7p11SameExportTests(unittest.TestCase):
    def quality(self, path):
        q = {
            "status": "NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY",
            "counts": {
                "material_documents": 1536,
                "material_docs_using_Unity_builtin_Shader": 750,
                "material_docs_using_local_custom_Shader": 786,
                "material_docs_using_dummy_Shader": 112,
                "material_docs_using_non_dummy_Shader": 674,
                "distinct_dummy_Shader_targets_referenced": 39,
                "material_docs_with_unknown_or_broken_Shader": 0,
            },
            "dummy_shader_material_counts_by_name_digest": {
                "f" * 64: 7, "a" * 64: 7,
                "b" * 64: 98,
            },
        }
        path.write_text(json.dumps(q))
        return q

    def test_source_quality_and_two_7_objects_7p11_must_be_topology_checked(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            qfile = root / "post21.json"
            q = self.quality(qfile)
            original_key = ("sharedassets5.assets", 123)
            source_names = {("sharedassets5.assets", i): format(i, "064x")
                            for i in range(1, 166)}
            source_names[original_key] = "f" * 64
            with (patch("scripts.gt_install_next7p11_original_shader48.gather",
                        return_value=(source_names, 14)),
                  patch("scripts.gt_install_next7p11_original_shader48.choose_original_7p11_by_topology",
                        return_value=original_key) as checker):
                self.assertEqual(source_identity(root, root / "manifest", qfile), original_key)
                checker.assert_called_once()
                self.assertEqual(checker.call_args.args[0], root / "Raft_Data")
                self.assertEqual(checker.call_args.args[3],
                                 {"f" * 64: 7, "a" * 64: 7, "b" * 64: 98})
            q["dummy_shader_material_counts_by_name_digest"]["a" * 64] += 1
            q["dummy_shader_material_counts_by_name_digest"]["b" * 64] -= 1
            qfile.write_text(json.dumps(q))
            with self.assertRaisesRegex(ValueError,"invalid_original_two_7_Material_digest_population"):
                source_identity(root, root / "manifest", qfile)
            q["dummy_shader_material_counts_by_name_digest"]["a" * 64] -= 1
            q["dummy_shader_material_counts_by_name_digest"]["b" * 64] += 1
            q["counts"]["material_docs_using_dummy_Shader"] = 216
            qfile.write_text(json.dumps(q))
            with self.assertRaisesRegex(ValueError, "unverified_post21"):
                source_identity(root, root / "manifest", qfile)

    def test_receipt_matches_both_stages_all_33_routes_and_candidate_sha(self):
        source = b'Shader "Sample" {}'
        receipt = {
            "candidate_sha256": sha256(source).hexdigest(),
            "compiled_program_table_verified": True,
            "vertex_and_fragment_entrypoints_verified": True,
            "vulkan_platform_only": True,
            "vertex_routes_by_pass": list(ROUTES),
            "fragment_routes_by_pass": list(ROUTES),
        }
        verify_receipt(source, receipt)
        receipt["fragment_routes_by_pass"] = [4, 5, 1]
        with self.assertRaisesRegex(ValueError, "unverified_next7p11"):
            verify_receipt(source, receipt)
        receipt["fragment_routes_by_pass"] = list(ROUTES)
        receipt["candidate_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "unverified_next7p11"):
            verify_receipt(source, receipt)

    def test_install_changes_only_shader_not_meta_and_rejects_non_dummy(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            project = root / "export"
            assets = project / "Assets"
            assets.mkdir(parents=True)
            target = assets / "a.shader"
            meta = assets / "a.shader.meta"
            original = b'Shader "Sample" { //DummyShaderTextExporter\\n }'
            candidate = b'Shader "Sample" { SubShader { Pass {} } }'
            target.write_bytes(original)
            metadata = b"fileFormatVersion: 2\\nguid: " + b"a" * 32 + b"\\n"
            meta.write_bytes(metadata)
            receipt = {
                "candidate_sha256": sha256(candidate).hexdigest(),
                "compiled_program_table_verified": True,
                "vertex_and_fragment_entrypoints_verified": True,
                "vulkan_platform_only": True,
                "vertex_routes_by_pass": list(ROUTES),
                "fragment_routes_by_pass": list(ROUTES),
            }
            with patch("scripts.gt_install_next7p11_original_shader48.traced_shader",
                       return_value=(target, meta)):
                result = install(project, {}, ("original", 1), candidate,
                                 receipt, root / "backup")
                self.assertEqual(result["vulkan_routes_installed"], 11)
                self.assertEqual(target.read_bytes(), candidate)
                self.assertEqual(meta.read_bytes(), metadata)
                self.assertEqual((root / "backup/original.shader").read_bytes(), original)
                with self.assertRaisesRegex(ValueError, "unsafe_next7p11_backup"):
                    install(project, {}, ("original", 1), candidate,
                            receipt, root / "backup")
                with self.assertRaisesRegex(ValueError, "not_unique_dummy"):
                    install(project, {}, ("original", 1), candidate,
                            receipt, root / "second_backup")


if __name__ == "__main__":
    unittest.main()
