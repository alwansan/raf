"""V5 checks real native YAML payloads on same routes; no original assets."""
from copy import deepcopy
from hashlib import sha256
import unittest
from pathlib import Path
import test_gt_material_route_keyword_state as kw
import test_gt_renderer_submesh_routes as rf
from scripts import gt_renderer_submesh_routes as routes
from scripts import gt_texture_route_payload as tex


def trees(seed):
    data=bytes((seed+n*13)%256 for n in range(20))
    s=dict(m_Width=2,m_Height=2,m_TextureFormat=4,m_MipCount=2,m_ImageCount=1,
           m_TextureDimension=2,m_CompleteImageSize=20,m_MipsStripped=0,
           m_StreamData=dict(path="",offset=0,size=0))
    a=deepcopy(s)
    s["image data"]=list(data)
    a["image data"]=len(data);a["_typelessdata"]=data.hex()
    return s,a


class TextureRoutes(unittest.TestCase):
    def setUp(self):
        self.k=kw.KeywordPassRoutes("test_all_state_bound")
        self.k.setUp();self.addCleanup(self.k.doCleanups)
        self.f=self.k.f
        self.source=[];self.actual=[]
        for n in (5,6):
            s,a=trees(n)
            self.source.append(s);self.actual.append(a)
            p=self.f.assets/f"tex{n}.png"
            p.unlink();Path(str(p)+".meta").unlink()
            self.f.docs[(rf.guid(n+20),2800000)]=(28,a)

    def check(self,strict=True):
        objects,proofs=self.k.v.b.evidence()
        for n,s in zip((5,6),self.source,strict=True):
            objects[(self.f.owner,n+20)]=(28,tex.safe_proof(s))
        self.f.write()
        mapping={(r["source"]["owner"],r["source"]["path_id"]):
                 (r["class_id"],routes.trace_pointer(r["export"]),r["exportable"])
                 for r in self.f.mappings}
        files,docs=routes.actual_index(self.f.project,mapping,texture_payloads=strict)
        return routes.compare(objects,{self.f.owner:[]},mapping,files,docs,vertex_payloads=proofs,
                              material_values=True,material_keywords=True,texture_payloads=strict)

    def reject(self,reason,old_pass=True):
        if old_pass:
            self.assertTrue(self.check(False)["selected_same_route_material_keyword_pass_state_verified"])
        r=self.check()
        self.assertFalse(r["selected_renderer_routes_preserved"],r)
        self.assertFalse(r["selected_nonnull_same_route_texture_payloads_verified"])
        self.assertIn(reason,r["reason_counts"])
        self.assertNotIn(self.actual[0].get("_typelessdata","never"),str(r))

    def test_native_two_mips_same_route(self):
        r=self.check()
        self.assertEqual(r["schema_version"],5)
        self.assertTrue(r["selected_nonnull_same_route_texture_payloads_verified"],r)
        self.assertEqual(r["counts"]["complete_texture_payload_bound_submesh_routes"],2)
        self.assertEqual(r["counts"]["texture_payload_slots_matched"],2)
        self.assertEqual(r["counts"]["texture_payload_bytes_matched_per_route"],40)
        self.assertEqual(r["counts"]["texture_mip_levels_matched_per_route"],4)
        self.assertFalse(r["texture_sampler_import_colorspace_or_GPU_verified"])

    def test_v4_does_not_claim_payload(self):
        r=self.check(False)
        self.assertFalse(r["selected_nonnull_same_route_texture_payloads_verified"])
        self.assertEqual(r["schema_version"],4)

    def change_byte(self,n):
        raw=bytearray.fromhex(self.actual[0]["_typelessdata"]);raw[n]^=1
        self.actual[0]["_typelessdata"]=raw.hex()

    def test_RGB_drift(self):
        self.change_byte(0);self.reject("same_route_texture_payload_bytes_drift")

    def test_alpha_drift(self):
        self.change_byte(3);self.reject("same_route_texture_payload_bytes_drift")

    def test_lower_mip_drift(self):
        self.change_byte(16);self.reject("same_route_texture_payload_bytes_drift")

    def test_same_size_wrong_texture(self):
        self.actual[0]["_typelessdata"]=self.actual[1]["_typelessdata"]
        self.reject("same_route_texture_payload_bytes_drift")

    def test_equal_size_dimension_drift(self):
        # Both descriptors remain valid: 4x1 and 1x4 have equal lengths.
        for s,a in ((self.source[0],self.actual[0]),):
            s.update(m_Width=4,m_Height=1,m_MipCount=1,m_CompleteImageSize=16)
            s["image data"]=s["image data"][:16]
            a.update(m_Width=1,m_Height=4,m_MipCount=1,m_CompleteImageSize=16)
            a["image data"]=16;a["_typelessdata"]=a["_typelessdata"][:32]
        self.reject("same_route_texture_descriptor_drift")

    def test_unsupported_format(self):
        self.actual[0]["m_TextureFormat"]=5
        self.reject("unsupported_native_RGBA32_texture_layout")

    def test_mip_count_drift(self):
        self.actual[0]["m_MipCount"]=1
        self.reject("texture_mip_size_mismatch")

    def test_missing_descriptor(self):
        del self.actual[0]["m_ImageCount"]
        self.reject("missing_texture_descriptor")

    def test_missing_data(self):
        del self.actual[0]["image data"]
        self.reject("missing_texture_payload")

    def test_hex_size(self):
        self.actual[0]["_typelessdata"]=self.actual[0]["_typelessdata"][:-2]
        self.reject("texture_payload_hex_or_length_mismatch")

    def test_source_stream_unproved(self):
        self.source[0]["m_StreamData"]={"path":"a.resS","offset":0,"size":20}
        self.reject("unsupported_texture_stream_payload")

    def test_export_stream_unproved(self):
        self.actual[0]["m_StreamData"]={"path":"a.resS","offset":0,"size":20}
        self.reject("unsupported_texture_stream_payload")

    def test_stripped_mips(self):
        self.actual[0]["m_MipsStripped"]=1
        self.reject("unsupported_stripped_texture_mips")

    def test_missing_stream_not_empty(self):
        del self.source[0]["m_StreamData"]
        self.reject("missing_texture_stream_descriptor")

    def test_invalid_byte(self):
        self.source[0]["image data"][0]=True
        self.reject("invalid_texture_payload_byte")

    def test_wrong_keyword_still_rejected(self):
        self.k.actual[0]["m_ValidKeywords"].pop()
        self.reject("missing_material_valid_keyword",old_pass=False)

    def test_null_texture_not_payload_coverage(self):
        for n in (5,6):
            s=self.f.objects[(self.f.owner,n)][1]["m_SavedProperties"]["m_TexEnvs"][0][1]
            a=self.f.docs[(rf.guid(n),2100000)][1]["m_SavedProperties"]["m_TexEnvs"][0]["_MainTex"]
            s["m_Texture"]=rf.src(0);a["m_Texture"]=rf.loc(0)
        r=self.check()
        self.assertTrue(r["selected_renderer_routes_preserved"],r)
        self.assertFalse(r["selected_nonnull_same_route_texture_payloads_verified"])
        self.assertEqual(r["counts"]["submesh_routes_without_nonnull_textures"],2)
        self.assertEqual(r["counts"].get("complete_texture_payload_bound_submesh_routes",0),0)

    def test_requires_keyword_binding(self):
        with self.assertRaisesRegex(routes.Unknown,"texture_payload_gate_requires_keyword_binding"):
            routes.compare({}, {}, {}, {}, {}, texture_payloads=True)

    def test_per_mip_hashes(self):
        s,a=trees(7);p=tex.proof(s)
        data=bytes(s["image data"])
        self.assertEqual(p.mip_sha256,(sha256(data[:16]).hexdigest(),sha256(data[16:]).hexdigest()))
        self.assertEqual(p,tex.proof(a,exported=True))


if __name__=="__main__":
    unittest.main()
