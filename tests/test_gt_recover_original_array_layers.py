"""GT private source-staged Texture2DArray GPU payload extraction controls.

Tests use synthetic streams only; original proprietary array bytes and all
same-instance exported GUIDs remain runner-private and out of artifacts.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.gt_zip2_payloads import SourceFailure
from scripts.gt_recover_original_array_layers import (
    safe_stream_basename,exact_streams,recover,
)


class RealOriginalArrayStreamRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source=self.root/"Raft_Data"
        self.source.mkdir()
        self.provider=self.source/"sharedassets0.assets.resS"
        self.provider.write_bytes(bytes(range(100)))
        self.expected={"Raft_Data/"+self.provider.name:(
            "plain",100,hashlib.sha256(bytes(range(100))).hexdigest())}
        self.arrays={
            ("sharedassets0.assets",i+1):{
                "private_stream_path":self.provider.name,
                "private_stream_offset":i*10,
                "original_stream_size":10,
                "source_format_enum":12,
                "source_mipmap_count":1,
                "has_stream_record":True,"has_image_data":False,
                "width":16,"height":16,"depth":4,
            } for i in range(9)}
        self.trace={"schema_version":1,"export_instance":"f"*32,
            "objects":[{
                "class_id":187,
                "source":{"owner":"sharedassets0.assets","path_id":i+1},
                "export":{"file_id":18700000,"guid":f"{i+100:032x}","type":3}
            } for i in range(9)]}
        self.destinations={f"{i+100:032x}":{
            "extension":".png","image":True,"TextureImporter":True,
            "textureShape_enum":"3"} for i in range(9)}
        self.stage=self.root/"private_payloads"

    def test_reassembles_original_nine_streamed_array_payloads_exactly_without_2d_fake(self):
        result=recover(self.source,self.arrays,self.trace,
            self.destinations,self.expected,self.stage)
        self.assertEqual(result["sha256_authenticated_streamed_payloads_copied"],9)
        self.assertEqual(result["original_source_streamed_bytes_restored_to_private_stage"],90)
        self.assertEqual(result["source_total_layer_count"],36)
        self.assertEqual(result["original_export_GUIDs_same_instance_matched"],9)
        self.assertFalse(result["Unity_Editor_Texture2DArray_assets_created"])
        self.assertFalse(result["Unity_Android_texture_array_import_or_GPU_render_verified"])
        private=json.loads((self.stage/"private-array-import-manifest.json").read_text())
        self.assertEqual(len(private["arrays"]),9)
        for i,row in enumerate(private["arrays"]):
            raw=(self.stage/row["relative_payload"]).read_bytes()
            self.assertEqual(raw,bytes(range(i*10,i*10+10)))
            self.assertEqual(row["sha256"],hashlib.sha256(raw).hexdigest())
        self.assertNotIn("guid",json.dumps(result).lower())
        self.assertEqual(self.provider.read_bytes(),bytes(range(100)))

    def test_corrupted_original_stream_fails_before_creating_stage(self):
        self.provider.write_bytes(b"!"*100)
        with self.assertRaisesRegex(SourceFailure,"sha256_mismatch"):
            recover(self.source,self.arrays,self.trace,
                    self.destinations,self.expected,self.stage)
        self.assertFalse(self.stage.exists())

    def test_out_of_bounds_refused_without_copy(self):
        self.arrays[("sharedassets0.assets",9)]["private_stream_offset"]=99
        with self.assertRaisesRegex(SourceFailure,"outside_authenticated_provider"):
            exact_streams(self.source,self.expected,self.arrays)
        self.assertFalse(self.stage.exists())

    def test_path_traversal_and_unknown_extensions_rejected(self):
        for bad in ("../other.resS","other.png","/../texture.resS","","../x.resource"):
            with self.assertRaises(SourceFailure):
                safe_stream_basename(bad)

    def test_missing_original_gpu_format_mip_metadata_is_not_accepted(self):
        self.arrays[("sharedassets0.assets",1)]["source_format_enum"]=None
        with self.assertRaisesRegex(SourceFailure,"format_or_mips_missing"):
            exact_streams(self.source,self.expected,self.arrays)

    def test_missing_array_trace_cannot_copy_original_bytes(self):
        self.trace["objects"].pop()
        with self.assertRaisesRegex(Exception,"array_objects_missing"):
            recover(self.source,self.arrays,self.trace,
                    self.destinations,self.expected,self.stage)
        self.assertFalse(self.stage.exists())

    def test_missing_original_immutable_sha_manifest_record_rejected(self):
        with self.assertRaisesRegex(SourceFailure,"unlisted_original_array_stream_provider"):
            exact_streams(self.source,{},self.arrays)


if __name__=="__main__":
    unittest.main()
