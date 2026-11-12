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

    def test_font_material_is_not_falsely_treated_as_missing_yaml(self):
        font_source=("sharedassets0.assets",42)
        self.original[font_source]={"_MainTex":((1,22),None)}
        font_row={
            "class_id":21,
            "source":{"owner":font_source[0],"path_id":font_source[1]},
            "collection_type": "AssetRipper.Export.UnityProjects.Miscellaneous.FontAssetExportCollection",
            "exportable":True,
            "export":{"file_id":2100000,"guid":"d"*32,"type":3},
            "font_source":{"owner":font_source[0],"path_id":43},
            "font_export":{"file_id":12800000,"guid":"d"*32,"type":3},
            "font_data_sha256":"e"*64,
        }
        self.trace["objects"].append(font_row)
        result=compare(self.original,self.tables,self.types,self.trace,self.exported)
        self.assertEqual(result["counts"]["source_material_without_normal_export"],1)
        self.assertEqual(result["exact_cross_owner_source_export_texture_links"],1)
        self.assertEqual(result["mismatched_source_to_export_external_links"],0)
        del font_row["font_data_sha256"]
        with self.assertRaisesRegex(InventoryError,"invalid_original_font_material_trace"):
            compare(self.original,self.tables,self.types,self.trace,self.exported)

    def test_untraced_ordinary_material_is_not_hidden_as_font(self):
        self.trace["objects"][0]["export"]["guid"]="c"*32
        with self.assertRaisesRegex(InventoryError,"original_exported_material_identity_missing"):
            compare(self.original,self.tables,self.types,self.trace,self.exported)

    def test_duplicate_font_material_and_normal_material_source_rejected(self):
        duplicate=dict(self.trace["objects"][0])
        duplicate["collection_type"]="AssetRipper.Export.UnityProjects.Miscellaneous.FontAssetExportCollection"
        duplicate["font_source"]={"owner":self.material[0],"path_id":55}
        duplicate["font_export"]={"file_id":12800000,"guid":"d"*32,"type":3}
        duplicate["font_data_sha256"]="e"*64
        self.trace["objects"].append(duplicate)
        with self.assertRaisesRegex(InventoryError,"duplicate_original_material_source_trace"):
            compare(self.original,self.tables,self.types,self.trace,self.exported)

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

    def test_safe_public_diagnostic_never_discloses_source_identity(self):
        from scripts.gt_external_original_texture_links import safe_failure
        err=InventoryError("private-original-Material-GUID-abcdef")
        result=safe_failure(err,"private_same_instance_export_join")
        self.assertEqual(result["status"],"INCONCLUSIVE")
        self.assertEqual(result["reason_code"],"unclassified_InventoryError")
        self.assertNotIn("abcdef",str(result))
        known=safe_failure(InventoryError("original_exported_material_identity_missing"),
                          "private_same_instance_export_join")
        self.assertEqual(known["reason_code"],"original_exported_material_identity_missing")

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
