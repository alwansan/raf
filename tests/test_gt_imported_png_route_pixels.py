"""V8 separate top-mip route, exact RGBA including transparent RGB."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace as NS
import unittest
import yaml
from PIL import Image
import test_gt_material_route_keyword_state as kw
import test_gt_renderer_submesh_routes as rf
import test_gt_texture_route_payload as tf
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_renderer_submesh_routes as routes
from scripts import gt_mesh_vertex_payload as mesh
from scripts.t3_decoded_texture_pixel_parity import compare_pair


class PNGRoute(unittest.TestCase):
    def setUp(self):
        self.k=kw.KeywordPassRoutes("test_all_state_bound")
        self.k.setUp();self.addCleanup(self.k.doCleanups)
        self.f=self.k.f
        self.source=[];self.paths=[]
        for i,n in enumerate((5,6)):
            t,_=tf.trees(13+i*53);t["m_LightmapFormat"]=0
            t["image data"][3]=0
            self.source.append(t)
            p=self.f.assets/f"tex{n}.png";self.paths.append(p)
            png.decode_top((2,2),bytes(t["image data"])[:16]).save(p)
            meta=dict(fileFormatVersion=2,guid=rf.guid(n+20),TextureImporter=dict(textureShape=1,textureType=0,
                textureSettings=dict(filterMode=1,aniso=2,mipBias=.125,wrapU=0,wrapV=1,wrapW=2)))
            Path(str(p)+".meta").write_text(yaml.safe_dump(meta,sort_keys=False))
            next(r for r in self.f.mappings if r["source"]["path_id"]==n+20)["export"]["type"]=3
            self.f.docs[(rf.guid(n),2100000)][1]["m_SavedProperties"]["m_TexEnvs"][0]["_MainTex"]["m_Texture"]["type"]=3
        self.root=self.f.project/"providers";self.root.mkdir()
        self.raw=b"PADPAD!"+bytes(self.source[0]["image data"])+b"PADDING"+bytes(self.source[1]["image data"])+b"TAILPAD"
        self.provider=self.root/"authored.resS";self.provider.write_bytes(self.raw)
        self.pins={"Raft_Data/"+self.provider.name:("plain",len(self.raw),sha256(self.raw).hexdigest())}

    def make_stream(self,i):
        self.source[i]["image data"]=[]
        self.source[i]["m_StreamData"]={"path":self.provider.name,"offset":7+27*i,"size":20}

    def requests(self):
        return {(self.f.owner,n+20):png.safe_request(t) for n,t in zip((5,6),self.source,strict=True)}

    def check(self,strict=True,proofs_override=None):
        objects,vertices=self.k.v.b.evidence()
        proofs=png.resolve_requests(self.root,self.pins,self.requests()) if proofs_override is None else proofs_override
        self.f.write()
        mapping={(r["source"]["owner"],r["source"]["path_id"]):(r["class_id"],routes.trace_pointer(r["export"]),r["exportable"]) for r in self.f.mappings}
        files,docs=routes.actual_index(self.f.project,mapping)
        return routes.compare(objects,{self.f.owner:[]},mapping,files,docs,vertex_payloads=vertices,
            material_values=True,material_keywords=True,**({"png_top_mips":proofs} if strict else {}))

    def reject(self,reason,old=True):
        if old:self.assertTrue(self.check(False)["selected_same_route_material_keyword_pass_state_verified"])
        result=self.check()
        self.assertFalse(result["selected_same_route_imported_png_top_mip_verified"],result)
        self.assertIn(reason,result["reason_counts"])

    def edit(self,fn):
        with Image.open(self.paths[0]) as im:img=im.copy()
        fn(img).save(self.paths[0])

    def channel(self,index,xy=(0,0)):
        def change(im):
            v=list(im.getpixel(xy));v[index]^=1;im.putpixel(xy,tuple(v));return im
        self.edit(change)

    def meta(self,fn):
        p=Path(str(self.paths[0])+".meta");d=yaml.safe_load(p.read_text());fn(d);p.write_text(yaml.safe_dump(d,sort_keys=False))

    def test_inline_exact(self):
        r=self.check();self.assertEqual(r["schema_version"],8)
        self.assertTrue(r["selected_same_route_imported_png_top_mip_verified"],r)
        self.assertEqual(r["counts"]["imported_png_pixels_matched_per_route"],8)
        self.assertEqual(r["counts"]["imported_png_RGBA_channels_matched_per_route"],32)
        self.assertFalse(r["selected_nonnull_same_route_texture_payloads_verified"])
        self.assertFalse(r["selected_same_route_native_texture_sampler_verified"])
        self.assertFalse(r["imported_png_lower_mip_or_Unity_import_verified"])

    def test_source_orientation_independent(self):
        t=self.source[0];im=png.decode_top((2,2),bytes(t["image data"])[:16])
        self.assertEqual(im.tobytes(),bytes(t["image data"][8:16]+t["image data"][:8]))
        with Image.open(self.paths[0]) as actual:
            self.assertEqual(compare_pair(im,actual,original_id="x",exported_id="x",authenticated=True),"EXACT")

    def test_stream_two_ranges_once(self):
        self.make_stream(0);self.make_stream(1)
        with patch.object(png,"verified_range_digests",wraps=png.verified_range_digests) as rd:
            r=self.check();self.assertTrue(r["selected_same_route_imported_png_top_mip_verified"],r)
            self.assertEqual(rd.call_count,1);self.assertEqual(rd.call_args.args[2],{(7,16),(34,16)})
            self.assertEqual(r["counts"]["imported_png_stream_source_slots_matched"],2)

    def test_stream_inline_mixed(self):
        self.make_stream(0)
        r=self.check();self.assertTrue(r["selected_same_route_imported_png_top_mip_verified"],r)
        self.assertEqual(r["counts"]["imported_png_stream_source_slots_matched"],1)

    def test_RGB(self):
        self.channel(0);self.reject("same_route_png_RGB_DRIFT")

    def test_transparent_RGB(self):
        self.channel(1,(0,1));self.reject("same_route_png_RGB_DRIFT")

    def test_alpha(self):
        self.channel(3);self.reject("same_route_png_ALPHA_ONLY_DRIFT")

    def test_vertical(self):
        self.edit(lambda im:im.transpose(Image.Transpose.FLIP_TOP_BOTTOM));self.reject("same_route_png_VERTICAL_FLIP")

    def test_horizontal(self):
        self.edit(lambda im:im.transpose(Image.Transpose.FLIP_LEFT_RIGHT));self.reject("same_route_png_HORIZONTAL_FLIP")

    def test_rotate(self):
        self.edit(lambda im:im.transpose(Image.Transpose.ROTATE_180));self.reject("same_route_png_BOTH_AXES_FLIP")

    def test_swap(self):
        self.paths[0].write_bytes(self.paths[1].read_bytes());self.reject("same_route_png_RGB_DRIFT")

    def test_dimensions(self):
        self.edit(lambda im:im.resize((4,1)));self.reject("same_route_png_DIMENSION_MISMATCH")

    def test_wrong_RGB_mode(self):
        self.edit(lambda im:im.convert("RGB"));self.reject("unsupported_png_RGBA8_image")

    def test_invalid_png(self):
        self.paths[0].write_bytes(b"not-a-png"*5);self.reject("invalid_png_signature_or_IHDR")

    def test_missing_usage(self):
        del self.source[0]["m_LightmapFormat"];self.reject("unsupported_png_source_texture_usage")

    def test_normalmap_not_proved(self):
        self.source[0]["m_LightmapFormat"]=1;self.reject("unsupported_png_source_texture_usage")

    def test_platform_blob_not_proved(self):
        self.source[0]["m_PlatformBlob"]=[1];self.reject("unsupported_png_source_platform_blob")

    def test_wrong_format(self):
        self.source[0]["m_TextureFormat"]=5;self.reject("unsupported_native_RGBA32_texture_layout")

    def test_stream_missing_pin(self):
        self.make_stream(0);self.pins={};self.reject("png_stream_provider_not_pinned")

    def test_stream_provider_mutation(self):
        self.make_stream(0);self.provider.write_bytes(b"X"+self.raw[1:]);self.reject("png_stream_provider_SHA_mismatch")

    def test_stream_swap(self):
        self.make_stream(0);self.source[0]["m_StreamData"]["offset"]=34;self.reject("same_route_png_RGB_DRIFT")

    def test_stream_out_of_bounds(self):
        self.make_stream(0);self.source[0]["m_StreamData"]["offset"]=45;self.reject("png_stream_extent_out_of_bounds")

    def test_unverified_range_capture_atomic(self):
        captured={}
        with self.assertRaises(ValueError):
            mesh.verified_range_digests(self.provider,(len(self.raw),"0"*64),[(7,16)],captures=captured)
        self.assertEqual(captured,{})

    def test_lower_mip_not_claimed(self):
        self.source[0]["image data"][16]^=1
        r=self.check();self.assertTrue(r["selected_same_route_imported_png_top_mip_verified"])
        self.assertFalse(r["imported_png_lower_mip_or_Unity_import_verified"])

    def test_meta_bad_type(self):
        self.meta(lambda d:d["TextureImporter"].update(textureType=1))
        self.reject("unsupported_png_importer_shape_or_type")

    def test_meta_missing_sampler(self):
        self.meta(lambda d:d["TextureImporter"].pop("textureSettings"))
        self.reject("missing_png_importer_sampler_schema")

    def test_meta_invalid_filter(self):
        self.meta(lambda d:d["TextureImporter"]["textureSettings"].update(filterMode=99))
        self.reject("invalid_png_importer_sampler_schema")

    def test_meta_unset_bias_no_native_promotion(self):
        self.meta(lambda d:d["TextureImporter"]["textureSettings"].update(mipBias=-100))
        r=self.check();self.assertTrue(r["selected_same_route_imported_png_top_mip_verified"],r)
        self.assertEqual(r["counts"]["imported_png_importer_mip_bias_unset_slots"],1)
        self.assertFalse(r["selected_same_route_native_texture_sampler_verified"])

    def test_meta_duplicate_key(self):
        p=Path(str(self.paths[0])+".meta");p.write_text(p.read_text()+"fileFormatVersion: 2\n")
        self.reject("duplicate_png_importer_key")

    def test_guid_missing(self):
        self.meta(lambda d:d.update(guid="ab"*16));self.reject("missing_actual_export_target",old=False)

    def test_type2_imported_not_promoted(self):
        next(r for r in self.f.mappings if r["source"]["path_id"]==25)["export"]["type"]=2
        self.f.docs[(rf.guid(5),2100000)][1]["m_SavedProperties"]["m_TexEnvs"][0]["_MainTex"]["m_Texture"]["type"]=2
        self.reject("png_trace_importer_identity_mismatch")

    def test_native_and_png_gate_exclusive(self):
        with self.assertRaisesRegex(routes.Unknown,"png_gate_requires_V4_and_separate_native_scope"):
            routes.compare({}, {}, {}, {}, {}, texture_payloads=True,png_top_mips={})

    def test_null_only_not_promoted(self):
        for n in (5,6):
            src=self.f.objects[(self.f.owner,n)][1]["m_SavedProperties"]["m_TexEnvs"][0][1]
            dst=self.f.docs[(rf.guid(n),2100000)][1]["m_SavedProperties"]["m_TexEnvs"][0]["_MainTex"]
            src["m_Texture"]=rf.src(0);dst["m_Texture"]=rf.loc(0)
        r=self.check();self.assertTrue(r["selected_renderer_routes_preserved"])
        self.assertFalse(r["selected_same_route_imported_png_top_mip_verified"])

    def test_source_records_authenticates_owner_before_png_parse(self):
        p=self.root/self.f.owner;raw=b"authored owner metadata only";p.write_bytes(raw)
        pins=dict(self.pins);pins["Raft_Data/"+self.f.owner]=("plain",len(raw),sha256(raw).hexdigest())
        self.make_stream(0)
        seen=[]
        def loader(data):
            self.assertEqual(data,raw);seen.append(True)
            obj=NS(type=NS(name="Texture2D"),path_id=25,read_typetree=lambda:self.source[0])
            return NS(file=NS(objects={25:obj},externals=[]))
        proofmap={}
        objects,_=routes.source_records(self.root,pins,[self.f.owner],loader=loader,png_top_mips=proofmap)
        self.assertEqual(objects,{(self.f.owner,25):(28,None)})
        self.assertIsInstance(proofmap[(self.f.owner,25)],png.Proof)
        p.write_bytes(b"X"+raw[1:])
        with self.assertRaisesRegex(ValueError,"SHA_mismatch"):
            routes.source_records(self.root,pins,[self.f.owner],loader=loader,png_top_mips={})
        self.assertEqual(seen,[True])


if __name__=="__main__":unittest.main()
