"""GT create a runner-private Unity Editor importer acceptance contract.

The 9 source GUIDs stay inside the transient Assets/Editor project and
never enter user-visible aggregate receipt or GitHub artifacts.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_write_unity_array_import_contract import (
    SCHEMA,RELATIVE,build,install,
)


class PrivateOriginalArrayEditorContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/"ExportedProject"
        (self.root/"Assets").mkdir(parents=True)
        self.original={
            ("sharedassets0.assets",i+1):{
                "width":1024,"height":1024,"depth":2 if i==0 else
                  (5 if i in (1,2) else 6 if i in (3,4,5,6) else 8),
                "source_mipmap_count":11,
                "original_stream_size":0 if i==0 else 100,
            } for i in range(9)
        }
        self.trace={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        self.arrays={
            ("sharedassets0.assets",i+1):(
                self.root/"Assets"/f"source-{i}.png",
                self.root/"Assets"/f"source-{i}.png.meta",
                f"{i+100:032x}")
            for i in range(9)
        }
        self.valid_links={
            "full_array_material_importer_links_verified":True,
            "exact_original_class187_array_material_refs":28,
            "distinct_source_array_guids_referenced_by_materials":9,
        }

    def patch_sources(self,links=None,arrays=None):
        from contextlib import ExitStack
        manager=ExitStack()
        manager.enter_context(patch(
            "scripts.gt_write_unity_array_import_contract.check",
            return_value=links or self.valid_links))
        manager.enter_context(patch(
            "scripts.gt_write_unity_array_import_contract.index_exported_array_meta",
            return_value={}))
        manager.enter_context(patch(
            "scripts.gt_write_unity_array_import_contract.exact_targets",
            return_value=arrays or self.arrays))
        return manager

    def test_real_style_nine_source_array_private_manifest_has_52_50_original_layers(self):
        with self.patch_sources():
            receipt=install(self.root,self.original,self.trace)
        data=json.loads((self.root/RELATIVE).read_text())
        self.assertEqual(data["schema"],SCHEMA)
        self.assertEqual(len(data["arrays"]),9)
        self.assertEqual(sum(x["depth"] for x in data["arrays"]),52)
        self.assertEqual(sum(x["depth"] for x in data["arrays"] if x["has_original_source_pixels"]),50)
        self.assertEqual(receipt["nine_original_source_guids_and_arrays_in_private_Editor_manifest"],9)
        self.assertEqual(receipt["original_class187_material_refs_source_proven"],28)
        self.assertFalse(receipt["Unity_Editor_import_execution_verified"])
        self.assertNotIn(self.arrays[("sharedassets0.assets",2)][2],json.dumps(receipt))
        self.assertEqual(len({x["guid"] for x in data["arrays"]}),9)

    def test_only_original_27_texture_links_cannot_publish_unverified_guid_manifest(self):
        incomplete=dict(self.valid_links,exact_original_class187_array_material_refs=27)
        with self.patch_sources(links=incomplete):
            with self.assertRaisesRegex(InventoryError,"links_not_verified"):
                install(self.root,self.original,self.trace)
        self.assertFalse((self.root/RELATIVE).exists())

    def test_wrong_original_depth_or_mipmap_cannot_create_import_contract(self):
        self.original[("sharedassets0.assets",1)]["depth"]=7
        with self.patch_sources():
            with self.assertRaisesRegex(InventoryError,"layer_scope_drift"):
                install(self.root,self.original,self.trace)
        self.assertFalse((self.root/RELATIVE).exists())

    def test_preexisting_private_manifest_is_not_overwritten(self):
        path=self.root/RELATIVE
        path.parent.mkdir(parents=True)
        path.write_text("existing owner content")
        with self.patch_sources():
            with self.assertRaisesRegex(InventoryError,"preexisting_target"):
                install(self.root,self.original,self.trace)
        self.assertEqual(path.read_text(),"existing owner content")

    def test_private_original_guid_duplicate_is_rejected(self):
        duplicated=dict(self.arrays)
        previous=duplicated[("sharedassets0.assets",1)]
        duplicated[("sharedassets0.assets",2)]=(
            *duplicated[("sharedassets0.assets",2)][:2],previous[2])
        with self.patch_sources(arrays=duplicated):
            with self.assertRaisesRegex(InventoryError,"layer_scope_drift"):
                install(self.root,self.original,self.trace)
        self.assertFalse((self.root/RELATIVE).exists())


if __name__=="__main__":
    unittest.main()
