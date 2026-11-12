"""GT source Texture2DArray export geometry metadata and exact class187 trace tests."""
import json
from pathlib import Path
from types import SimpleNamespace
import hashlib
import tempfile
import unittest

from scripts.gt_stage_serialized_owners import InventoryError, OWNERS
from scripts.gt_verify_original_array_export import match, source_arrays, COUNT_EXPECTED


def source(count=COUNT_EXPECTED):
    return {("sharedassets0.assets", i+1):
        {"width":16,"height":16,"depth":4,"has_stream_record":True,
         "has_image_data":False} for i in range(count)}


def rows(count=COUNT_EXPECTED,cls=187):
    return {"schema_version":1,"export_instance":"f"*32,"objects":[{
        "class_id":cls,
        "source":{"owner":"sharedassets0.assets","path_id":i+1},
        "export":{"file_id":18700000,"guid":f"{i+100:032x}","type":3},
        "exportable":True
        } for i in range(count)]}


def target(count=COUNT_EXPECTED,shape="3",is_image=True):
    return {f"{i+100:032x}":{"extension":".png" if is_image else ".asset",
        "image":is_image,"TextureImporter":is_image,"textureShape_enum":shape}
        for i in range(count)}


class OriginalTextureArrayExportTests(unittest.TestCase):
    def test_all_nine_source_array_objects_traced_exactly_with_layers(self):
        d=match(source(),rows(),target())
        self.assertEqual(d["original_Texture2DArray_class187_SHA256_verified"],9)
        self.assertEqual(d["array_real_export_source_GUIDs_exact_join"],9)
        self.assertEqual(d["counts"]["source_layers_total"],36)
        self.assertEqual(d["counts"]["array_export_fileID_18700000"],9)
        self.assertEqual(d["counts"]["array_importer_shape_3"],9)
        self.assertEqual(d["counts"]["exported_as_image"],9)
        self.assertFalse(d["all_arrays_exported_as_valid_Unity_Texture2DArray_assets_verified"])
        self.assertFalse(d["original_texture_array_layers_or_pixels_restored_for_Android"])
        self.assertNotIn("sharedassets",json.dumps(d))

    def test_missing_array_in_same_instance_export_refused(self):
        with self.assertRaisesRegex(InventoryError,"array_objects_missing_from_same_instance_export"):
            match(source(),rows(8),target())

    def test_untrusted_extra_traced_array_refused(self):
        t=rows(10)
        with self.assertRaisesRegex(InventoryError,"array_trace_missing_from_authenticated_source_or_duplicate"):
            match(source(),t,target(10))

    def test_wrong_output_image_meta_guid_refused(self):
        with self.assertRaisesRegex(InventoryError,"array_export_GUID_not_in_actual_meta"):
            match(source(),rows(),target(8))

    def test_two_original_array_objects_collapsed_to_one_target_rejected(self):
        t=rows()
        t["objects"][1]["export"]=dict(t["objects"][0]["export"])
        with self.assertRaisesRegex(InventoryError,"distinct_original_arrays_collapsed_to_one_export_pointer"):
            match(source(),t,target())

    def test_no_unauthorized_material_pointer_rewrite(self):
        d=match(source(),rows(),target(shape="4"))
        self.assertEqual(d["counts"]["array_importer_shape_4"],9)
        self.assertFalse(d["original_or_exported_assets_modified"])
        self.assertFalse(d["original_texture_array_layers_or_pixels_restored_for_Android"])

    def test_all_source_owner_metadata_fingerprints_and_nine_texture2darray_objects(self):
        with tempfile.TemporaryDirectory() as dirname:
            root=Path(dirname)
            stage=root/"staged"
            stage.mkdir()
            manifest=root/"manifest.tsv"
            lines=["kind\\tbytes\\tsha256\\tmode\\trelative_path_under_Raft"]
            for name in OWNERS:
                raw=name.encode("utf-8")
                (stage/name).write_bytes(raw)
                digest=hashlib.sha256(raw).hexdigest()
                lines.append(f"plain\\t{len(raw)}\\t{digest}\\t660\\tRaft_Data/{name}")
            manifest.write_text("\\n".join(lines)+"\\n")
            class Fake:
                type=SimpleNamespace(name="Texture2DArray")
                def __init__(self,idx):
                    self.path_id=idx+1
                def read_typetree(self,check_read=False):
                    return {"m_Width":16,"m_Height":16,"m_Depth":4,
                            "m_StreamData":{},"m_ImageData":b""}
            first=set(OWNERS[:9])
            def loader(path):
                return SimpleNamespace(objects=[Fake(0)] if path.name in first else [])
            data=source_arrays(stage,manifest,loader=loader)
            self.assertEqual(len(data),9)
            self.assertTrue(all(x["depth"]==4 for x in data.values()))
            self.assertTrue(all(x["has_stream_record"] for x in data.values()))
            (stage/OWNERS[0]).write_text("corrupt")
            with self.assertRaisesRegex(InventoryError,"fingerprint_mismatch"):
                source_arrays(stage,manifest,loader=loader)

    def test_source_arrays_rejects_missing_dimensions_without_claiming_integrity(self):
        with tempfile.TemporaryDirectory() as dirname:
            root=Path(dirname)
            stage=root/"staged"
            stage.mkdir()
            manifest=root/"manifest.tsv"
            rows=["kind\\tbytes\\tsha256\\tmode\\trelative_path_under_Raft"]
            for name in OWNERS:
                raw=name.encode("utf-8")
                (stage/name).write_bytes(raw)
                rows.append(f"plain\\t{len(raw)}\\t{hashlib.sha256(raw).hexdigest()}\\t660\\tRaft_Data/{name}")
            manifest.write_text("\\n".join(rows)+"\\n")
            class Broken:
                type=SimpleNamespace(name="Texture2DArray")
                path_id=1
                def read_typetree(self,check_read=False):
                    return {"m_Width":32,"m_Height":32}
            with self.assertRaisesRegex(InventoryError,"dimension_missing"):
                source_arrays(stage,manifest,loader=lambda path: SimpleNamespace(
                    objects=[Broken()] if path.name==OWNERS[0] else []))

    def test_wrong_original_count_refused(self):
        with self.assertRaisesRegex(InventoryError,"unexpected_authenticated_array_count"):
            match(source(8),rows(),target())


if __name__=="__main__":
    unittest.main()
