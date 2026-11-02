"""Metadata-only compute tests; no original Raft assets or Unity required."""
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys

from scripts.audit_original_compute_metadata import summarize_tree, inspect, MAX_NODES


class ComputeMetadataAuditTests(unittest.TestCase):
    def test_reports_only_metadata_keys_and_counts_not_programs(self):
        original = {
            "m_Name": "ProprietaryFFT",
            "m_ComputeShaders": [
                {"m_Kernels": [
                    {"name": "PrivateKernelA", "m_CompiledProgram": bytes([1, 9, 22])},
                    {"name": "PrivateKernelB", "m_CompiledProgram": bytes([66, 77])},
                ], "m_Platforms": [12, 16]},
                {"m_Kernels": [{"name": "SecretKernel", "m_Program": "CODE-DO-NOT-PUBLISH"}]},
            ],
        }
        result = summarize_tree(original)
        self.assertGreaterEqual(result["metadata_fields"].get("m_Kernels", 0), 2)
        self.assertEqual(result["metadata_array_totals"]["m_Kernels"], 3)
        self.assertEqual(result["metadata_array_totals"]["m_Platforms"], 2)
        self.assertEqual(result["original_platform_numeric_codes"], {12: 1, 16: 1})
        self.assertFalse(result["platform_code_meanings_verified"])
        self.assertFalse(result["private_shader_programs_emitted"])
        self.assertNotIn("PrivateKernelA", str(result))
        self.assertNotIn("CODE-DO-NOT-PUBLISH", str(result))
        self.assertNotIn("ProprietaryFFT", str(result))
        self.assertNotIn("66, 77", str(result))


    def test_unrecognized_backend_values_are_not_treated_as_platform_codes(self):
        result = summarize_tree({"m_Platforms": [{"unknown": "secret"}], "m_Kernels": []})
        self.assertEqual(result["original_platform_numeric_codes"], {})
        self.assertFalse(result["platform_code_meanings_verified"])

    def test_requires_typetree_dict_and_bounded_paths(self):
        with self.assertRaisesRegex(ValueError, "dictionary"):
            summarize_tree([{"m_Kernels": []}])
        with self.assertRaisesRegex(ValueError, "metadata key"):
            summarize_tree({"X" * 140: 1})
        self.assertTrue(summarize_tree({"m_Kernels": []})["metadata_fields"])


    def test_original_inventory_checks_object_count_and_no_asset_edits(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / "sharedassets0.assets"
            path.write_bytes(b"original serialized compute fixture")
            before = path.read_bytes()
            def original(path_id):
                return SimpleNamespace(
                    type=SimpleNamespace(name="ComputeShader"),
                    path_id=path_id,
                    get_raw_data=lambda: b"private-object-binary",
                    read_typetree=lambda: {"m_Name": "hidden", "m_Platforms": [4],
                                           "m_Kernels": [{"compiled": b"no-output"}]},
                )
            objs = [original(100), original(200)]
            mock_unitypy = SimpleNamespace(load=lambda p: SimpleNamespace(file=SimpleNamespace(
                objects={1: objs[0], 2: objs[1]})))
            with patch.dict(sys.modules, {"UnityPy": mock_unitypy}), patch(
                    "scripts.audit_original_compute_metadata.serialized_sources",
                    return_value=[path]), patch(
                    "scripts.audit_original_compute_metadata.owned_objects",
                    return_value=objs):
                result = inspect(root, expected_objects=2)
                self.assertEqual(result["original_objects"], 2)
                self.assertFalse(result["source_mutated"])
                self.assertEqual(result["decoded_compute_sources"], 0)
                self.assertEqual(result["compute_objects"][0]["metadata"]["original_platform_numeric_codes"], {4: 1})
                self.assertNotIn("private-object-binary", str(result))
                with self.assertRaisesRegex(ValueError, "Expected 1 original"):
                    inspect(root, expected_objects=1)
            self.assertEqual(path.read_bytes(), before)

    def test_lfs_pointer_is_refused_before_unitypy_parse(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / "resources.assets"
            path.write_text("version https://git-lfs.github.com/spec/v1\\noid sha256:" +
                            "a" * 64 + "\\nsize 1000\\n")
            with patch("scripts.audit_original_compute_metadata.serialized_sources",
                       return_value=[path]), patch.dict(sys.modules, {"UnityPy": SimpleNamespace()}):
                with self.assertRaisesRegex(ValueError, "only a Git LFS pointer"):
                    inspect(root, expected_objects=1)

    def test_large_and_deep_nested_tables_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "array length"):
            summarize_tree({"m_Kernels": [None] * (MAX_NODES + 1)})
        child = {}
        current = child
        for i in range(15):
            current["m_Kernels"] = {}
            current = current["m_Kernels"]
        with self.assertRaisesRegex(ValueError, "nesting depth"):
            summarize_tree(child)


if __name__ == "__main__":
    unittest.main()
