"""T3 original ParticleShader48 Texture2D target/stream source-only contracts.

Synthetic Texture2D records only; no proprietary resource names, PathIDs or
shader bytes from Raft are used in fixtures. The CLI real run separately
authenticates six original scenes and four immutable owner SHA fingerprints.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_particle_texture_targets as m


class OriginalParticleThreeTextureTargets(unittest.TestCase):
    def fixture(self):
        keys=[("resources.assets",301),("resources.assets",302),
              ("sharedassets0.assets",303)]
        targets={keys[0]:6,keys[1]:3,keys[2]:1}
        normal={"m_Width":64,"m_Height":128,
                "m_TextureFormat":4,"m_CompleteImageSize":1024}
        records={
            keys[0]:("Texture2D",{**normal,"m_StreamData":{
                "path":"archive:/some/fake/assets/fake.resS","offset":7,"size":22}}),
            keys[1]:("Texture2D",{**normal,"m_StreamData":{
                "path":"","offset":0,"size":0}}),
            keys[2]:("Texture2D",normal)}
        provider={"fake.resS":(4096,"a"*64)}
        return targets,records,provider

    def test_typed_original_three_targets_and_ten_material_bindings(self):
        target,rows,providers=self.fixture()
        with tempfile.TemporaryDirectory() as d:
            result=m.assess(target,rows,providers,Path(d))
        self.assertEqual(result["status"],m.STATUS)
        self.assertEqual(result["original_selected_typed_Texture2D28_targets"],3)
        self.assertEqual(result["original_selected_Texture2D28_material_bindings"],10)
        self.assertEqual(result["original_selected_Texture2D28_manifest_verified_streamed"],1)
        self.assertEqual(result["original_selected_Texture2D28_inline_or_unstreamed"],1)
        self.assertEqual(result["original_selected_Texture2D28_without_stream_field"],1)
        self.assertEqual(result["original_selected_Texture2D28_stream_provider_not_staged"],1)
        self.assertEqual(result["original_selected_distinct_manifest_stream_providers"],1)
        self.assertFalse(result["full_original_Texture2D28_pixel_content_verified"])
        self.assertFalse(result["same_export_Texture2D28_GUID_or_Android_sampler_binding_verified"])
        public=json.dumps(result,sort_keys=True)
        for private in ("fake.resS","resources.assets","sharedassets0.assets",
                        "path_id","301","302","303","archive:",'"path"'):
            self.assertNotIn(private,public)

    def test_wrong_or_missing_original_Texture2D_typed_target_fails_closed(self):
        targets,records,providers=self.fixture()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            del records[next(iter(records))]
            with self.assertRaisesRegex(ValueError,"scope"):
                m.assess(targets,records,providers,root)
        targets,records,providers=self.fixture()
        first=next(iter(records))
        records[first]=("Sprite",records[first][1])
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"class28"):
                m.assess(targets,records,providers,Path(d))

    def test_extents_must_fit_SHA_pinned_original_manifest(self):
        targets,records,providers=self.fixture()
        with tempfile.TemporaryDirectory() as d:
            providers["fake.resS"]=(20,"a"*64)
            with self.assertRaisesRegex(ValueError,"beyond_manifest"):
                m.assess(targets,records,providers,Path(d))
            providers.clear()
            with self.assertRaisesRegex(ValueError,"missing_manifest_pin"):
                m.assess(targets,records,providers,Path(d))

    def test_original_stream_malformed_and_ambiguous_data_rejected(self):
        for value in (
            {"path":"../fake.resS","size":2,"offset":1},
            {"path":"fake.resS","size":0,"offset":1},
            {"path":"","size":5,"offset":0},
            {"path":"fake.resS","size":True,"offset":0},
            {"path":"fake.png","size":5,"offset":0},
            {"path":"fake.resS","size":5,"offset":-1},
            {"path":"fake.resS","offset":0},
        ):
            targets,records,providers=self.fixture()
            first=next(iter(records))
            records[first][1]["m_StreamData"]=value
            with self.subTest(value=value),tempfile.TemporaryDirectory() as d:
                with self.assertRaisesRegex(ValueError,"StreamData|stream_path"):
                    m.assess(targets,records,providers,Path(d))

    def test_corrupted_staged_stream_is_rejected_even_when_manifest_looks_right(self):
        targets,records,providers=self.fixture()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            content=b"safe-synthetic-resource-stream-fixture"
            (root/"fake.resS").write_bytes(content)
            providers["fake.resS"]=(len(content),"b"*64)
            with self.assertRaisesRegex(ValueError,"staged_SHA_mismatch"):
                m.assess(targets,records,providers,root)
            providers["fake.resS"]=(len(content),hashlib.sha256(content).hexdigest())
            good=m.assess(targets,records,providers,root)
            self.assertEqual(good["original_selected_Texture2D28_stream_payload_SHA_verified"],1)
            self.assertEqual(good["original_selected_Texture2D28_stream_provider_not_staged"],0)

    def test_bad_dimension_format_size_and_material_use_identity(self):
        for key,value in (("m_Width",0),("m_Height",-1),("m_Width",True),
                          ("m_TextureFormat","4"),("m_CompleteImageSize",False)):
            targets,records,providers=self.fixture()
            first=next(iter(records))
            records[first][1][key]=value
            with self.subTest(field=key),tempfile.TemporaryDirectory() as d:
                with self.assertRaisesRegex(ValueError,"metadata"):
                    m.assess(targets,records,providers,Path(d))
        targets,records,providers=self.fixture()
        first=next(iter(targets))
        targets[first]=0
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"class28"):
                m.assess(targets,records,providers,Path(d),expected_local=4)

    def test_private_original_texture_identity_never_serialized_into_report(self):
        targets,records,providers=self.fixture()
        with tempfile.TemporaryDirectory() as d:
            result=m.assess(targets,records,providers,Path(d))
        self.assertTrue(result["raw_Shader_Texture_Material_IDs_names_stream_paths_disclosed"] is False)
        self.assertTrue(result["original_selected_Texture2D28_type_and_stream_metadata_verified"])
        self.assertNotIn("objects",result)
        self.assertNotIn("providers",result)


if __name__=="__main__":
    unittest.main()
