"""GT synthetic-only external Material TexEnv source fileID resolution."""
from types import SimpleNamespace
import unittest

from scripts.gt_external_original_texture_links import (
    exact_owner, compare, trace_targets,
)
from scripts.gt_stage_serialized_owners import InventoryError


class ExternalTextureBindingsTests(unittest.TestCase):
    def setUp(self):
        self.material=("sharedassets0.assets",11)
        self.texture=("sharedassets1.assets",22)
        self.guid="a"*32
        self.mat_guid="b"*32
        self.original={self.material:{"_MainTex":((1,22),None)}}
        self.tables={"sharedassets0.assets":["archive:/CAB-blob/sharedassets1.assets"]}
        self.types={self.texture:28}
        self.trace={"schema_version":1,"export_instance":"f"*32,"objects":[
            {"class_id":21,"source":{"owner":self.material[0],"path_id":11},
             "export":{"file_id":2100000,"guid":self.mat_guid,"type":3}},
            {"class_id":28,"source":{"owner":self.texture[0],"path_id":22},
             "export":{"file_id":2800000,"guid":self.guid,"type":3}},
        ]}
        self.exported={(2100000,self.mat_guid):{
            "_MainTex":((2800000,self.guid,3),None)}}

    def test_exact_source_external_file_table_and_pointer(self):
        result=compare(self.original,self.tables,self.types,self.trace,self.exported)
        self.assertEqual(result["original_external_texture_slots"],1)
        self.assertEqual(result["exact_cross_owner_source_export_texture_links"],1)
        self.assertEqual(result["external_links_not_yet_proven"],0)
        self.assertEqual(result["mismatched_source_to_export_external_links"],0)
        self.assertTrue(result["all_external_links_verified"])
        self.assertNotIn(self.guid,str(result))
        self.assertNotIn("sharedassets",str(result))

    def test_unmatched_external_owner_never_guessed(self):
        self.tables["sharedassets0.assets"]=["archive:/CAB/unavailable.assets"]
        result=compare(self.original,self.tables,self.types,self.trace,self.exported)
        self.assertEqual(result["external_links_not_yet_proven"],1)
        self.assertEqual(result["counts"]["external_owner_unproven"],1)
        self.assertFalse(result["all_external_links_verified"])

    def test_wrong_exported_pointer_fails_closed_without_guid_leak(self):
        self.exported[(2100000,self.mat_guid)]["_MainTex"]=(
            (2800000,"c"*32,3),None)
        result=compare(self.original,self.tables,self.types,self.trace,self.exported)
        self.assertEqual(result["mismatched_source_to_export_external_links"],1)
        self.assertEqual(result["status"],"EXTERNAL_TEXTURE_SOURCE_EXPORT_LINKS_REJECTED")
        self.assertNotIn(self.guid,str(result))

    def test_texture_source_class_mismatch_not_promoted(self):
        self.types[self.texture]=187
        result=compare(self.original,self.tables,self.types,self.trace,self.exported)
        self.assertEqual(result["counts"]["wrong_original_external_texture_class"],1)

    def test_invalid_untrusted_trace_is_rejected(self):
        self.trace["export_instance"]="not-a-guid"
        with self.assertRaisesRegex(InventoryError,"invalid_private_same_instance"):
            compare(self.original,self.tables,self.types,self.trace,self.exported)

    def test_original_external_owner_path_rejects_traversal(self):
        self.assertIsNone(exact_owner("../sharedassets1.assets"))
        self.assertIsNone(exact_owner("archive:/abc/./sharedassets1.assets"))
        self.assertEqual(exact_owner("archive:/CAB/sharedassets1.assets"),
                         "sharedassets1.assets")


if __name__=="__main__":
    unittest.main()
