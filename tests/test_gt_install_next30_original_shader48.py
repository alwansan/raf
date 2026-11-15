"""Fail-closed fake-source tests for exact original next30 Shader48 GUID installer."""
import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.gt_install_next30_original_shader48 import (
    ROUTES, source_identity, verify_receipt,
)


class Next30OriginalSourceGUIDTests(unittest.TestCase):
    def test_post13_exact_246_dummy_47_guid_source_is_required(self):
        with TemporaryDirectory() as tmp:
            report=Path(tmp)/"quality.json"
            props={
                "status":"NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY",
                "counts":{
                    "material_documents":1536,
                    "material_docs_using_local_custom_Shader":786,
                    "material_docs_using_dummy_Shader":246,
                    "distinct_dummy_Shader_targets_referenced":47,
                },
                "dummy_shader_material_counts_by_name_digest":{"f"*64:30},
            }
            report.write_text(json.dumps(props))
            data={("resources.assets",i):("f"*64 if i==1 else format(i,"064x"))
                  for i in range(1,166)}
            with patch("scripts.gt_install_next30_original_shader48.gather",return_value=(data,14)):
                self.assertEqual(source_identity(Path(tmp),Path(tmp)/"manifest",report),("resources.assets",1))
                props["counts"]["material_docs_using_dummy_Shader"]=333
                report.write_text(json.dumps(props))
                with self.assertRaisesRegex(ValueError,"unverified_post13_remaining_Dummy_Shader_scope"):
                    source_identity(Path(tmp),Path(tmp)/"manifest",report)

    def test_bundle_receipt_requires_exact_both_stage_routes_and_source_sha(self):
        candidate=b'Shader "Sample" {}'
        receipt={
            "candidate_sha256":sha256(candidate).hexdigest(),
            "compiled_program_table_verified":True,
            "vertex_and_fragment_entrypoints_verified":True,
            "vulkan_platform_only":True,
            "vertex_routes_by_pass":list(ROUTES),
            "fragment_routes_by_pass":list(ROUTES),
        }
        verify_receipt(candidate,receipt)
        receipt["fragment_routes_by_pass"]=[8,13,8,3]
        with self.assertRaisesRegex(ValueError,"unverified_next30"):
            verify_receipt(candidate,receipt)
        receipt["fragment_routes_by_pass"]=list(ROUTES)
        receipt["candidate_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"unverified_next30"):
            verify_receipt(candidate,receipt)


if __name__=="__main__":
    unittest.main()
