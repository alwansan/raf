"""V6 strict source range identity with same-route native export proofs."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import unittest
import test_gt_texture_route_payload as vf
import test_gt_renderer_submesh_routes as rf
from scripts import gt_renderer_submesh_routes as routes
from scripts import gt_texture_route_payload as inline
from scripts import gt_streamed_texture_route_payload as stream


class StreamRoutes(unittest.TestCase):
    def setUp(self):
        self.v=vf.TextureRoutes("test_native_two_mips_same_route")
        self.v.setUp();self.addCleanup(self.v.doCleanups)
        self.f=self.v.f
        self.root=self.f.project/"providers";self.root.mkdir()
        self.name="authored.resS"
        self.path=self.root/self.name
        self.data=b"PADPAD!"+bytes(self.v.source[0]["image data"])+b"PADDING"+bytes(self.v.source[1]["image data"])+b"TAILPAD"
        self.path.write_bytes(self.data)
        self.pins={"Raft_Data/"+self.name:("plain",len(self.data),sha256(self.data).hexdigest())}
        for i,t in enumerate(self.v.source):
            t["image data"]=[]
            t["m_StreamData"]={"path":self.name,"offset":7+27*i,"size":20}

    def requests(self):
        return {(self.f.owner,n+20):stream.safe_request(t) for n,t in zip((5,6),self.v.source,strict=True)}

    def check(self,strict=True):
        objects,proofs=self.v.k.v.b.evidence()
        resolved=stream.resolve_requests(self.root,self.pins,self.requests())
        objects.update((key,(28,p)) for key,p in resolved.items())
        self.f.write()
        mapping={(r["source"]["owner"],r["source"]["path_id"]):
                 (r["class_id"],routes.trace_pointer(r["export"]),r["exportable"])
                 for r in self.f.mappings}
        files,docs=routes.actual_index(self.f.project,mapping,texture_payloads=True)
        return routes.compare(objects,{self.f.owner:[]},mapping,files,docs,vertex_payloads=proofs,
                              material_values=True,material_keywords=True,texture_payloads=True,
                              streamed_textures=strict)

    def reject(self,reason):
        r=self.check()
        self.assertFalse(r["selected_renderer_routes_preserved"],r)
        self.assertFalse(r["selected_same_route_streamed_texture_payloads_verified"])
        self.assertIn(reason,r["reason_counts"])
        self.assertNotIn(self.name,str(r))

    def test_same_route_two_streams(self):
        r=self.check()
        self.assertEqual(r["schema_version"],6)
        self.assertTrue(r["selected_same_route_streamed_texture_payloads_verified"],r)
        self.assertEqual(r["counts"]["streamed_texture_payload_slots_matched"],2)
        self.assertEqual(r["counts"]["streamed_texture_payload_bytes_matched_per_route"],40)
        self.assertEqual(r["counts"]["streamed_texture_mip_levels_matched_per_route"],4)

    def test_v5_rejects_stream_proofs(self):
        r=self.check(False)
        self.assertFalse(r["selected_renderer_routes_preserved"])
        self.assertFalse(r["selected_same_route_streamed_texture_payloads_verified"])

    def test_single_provider_read(self):
        with patch.object(stream,"verified_range_digests",wraps=stream.verified_range_digests) as read:
            r=self.check()
            self.assertTrue(r["selected_same_route_streamed_texture_payloads_verified"])
            self.assertEqual(read.call_count,1)
            self.assertEqual(sorted(read.call_args.args[2]),[(7,16),(7,20),(23,4),(34,16),(34,20),(50,4)])

    def test_swapped_same_size_extent(self):
        self.v.source[0]["m_StreamData"]["offset"]=34
        self.reject("same_route_texture_payload_bytes_drift")

    def test_padding_mutation_rejected_even_if_mips_match(self):
        self.path.write_bytes(b"Z"+self.data[1:])
        self.reject("texture_stream_provider_SHA_mismatch")

    def test_lower_mip_mutation_rejected_by_provider_pin(self):
        raw=bytearray(self.data);raw[23]^=1;self.path.write_bytes(raw)
        self.reject("texture_stream_provider_SHA_mismatch")

    def test_wrong_export_alpha_rejected(self):
        self.v.change_byte(3)
        self.reject("same_route_texture_payload_bytes_drift")

    def test_wrong_export_lower_mip_rejected(self):
        self.v.change_byte(16)
        self.reject("same_route_texture_payload_bytes_drift")

    def test_wrong_provider(self):
        self.v.source[0]["m_StreamData"]["path"]="different.resS"
        self.reject("texture_stream_provider_not_pinned")

    def test_unsafe_provider_path(self):
        for path in ("../authored.resS","archive:/CAB-123/authored.resS","/authored.resS","sub/authored.resS","sub\\authored.resS"):
            with self.subTest(path=path):
                self.v.source[0]["m_StreamData"]["path"]=path
                self.reject("unsupported_texture_stream_provider")

    def test_ambiguous_inline_and_stream(self):
        self.v.source[0]["image data"]=[0]*20
        self.reject("ambiguous_inline_and_stream_texture_payload")

    def test_out_of_bounds(self):
        self.v.source[0]["m_StreamData"]["offset"]=60
        self.reject("texture_stream_extent_out_of_bounds")

    def test_wrong_extent_size(self):
        self.v.source[0]["m_StreamData"]["size"]=16
        self.reject("invalid_texture_stream_extent")

    def test_negative_offset(self):
        self.v.source[0]["m_StreamData"]["offset"]=-1
        self.reject("invalid_texture_stream_extent")

    def test_bool_offset(self):
        self.v.source[0]["m_StreamData"]["offset"]=True
        self.reject("invalid_texture_stream_extent")

    def test_missing_manifest_pin(self):
        self.pins={}
        self.reject("texture_stream_provider_not_pinned")

    def test_invalid_manifest_pin(self):
        self.pins["Raft_Data/"+self.name]=("plain",len(self.data),"bad")
        self.reject("invalid_texture_stream_provider_pin")

    def test_truncated_provider(self):
        self.path.write_bytes(self.data[:-1])
        self.reject("texture_stream_provider_size_mismatch")

    def test_symlink_provider(self):
        target=self.root/"other";target.write_bytes(self.data)
        self.path.unlink();self.path.symlink_to(target)
        self.reject("unreadable_or_unproved_texture_stream_provider")

    def test_mixed_inline_stream(self):
        t=self.v.source[0];t["image data"]=list(self.data[7:27]);t["m_StreamData"]={"path":"","offset":0,"size":0}
        r=self.check()
        self.assertTrue(r["selected_same_route_streamed_texture_payloads_verified"],r)
        self.assertEqual(r["counts"]["streamed_texture_payload_slots_matched"],1)
        self.assertEqual(r["counts"]["texture_payload_slots_matched"],2)

    def test_inline_only_V6_does_not_claim_stream(self):
        for i,t in enumerate(self.v.source):
            t["image data"]=list(self.data[7+27*i:27+27*i])
            t["m_StreamData"]={"path":"","offset":0,"size":0}
        r=self.check()
        self.assertTrue(r["selected_nonnull_same_route_texture_payloads_verified"],r)
        self.assertFalse(r["selected_same_route_streamed_texture_payloads_verified"])

    def test_source_request_hashes(self):
        p=stream.resolve_requests(self.root,self.pins,self.requests())[(self.f.owner,25)]
        self.assertEqual(p.content.sha256,sha256(self.data[7:27]).hexdigest())
        self.assertEqual(p.content.mip_sha256,(sha256(self.data[7:23]).hexdigest(),sha256(self.data[23:27]).hexdigest()))
        self.assertEqual(p.provider_sha256,sha256(self.data).hexdigest())

    def test_requires_payload_binding(self):
        with self.assertRaisesRegex(routes.Unknown,"streamed_texture_gate_requires_payload_binding"):
            routes.compare({}, {}, {}, {}, {}, streamed_textures=True)


if __name__=="__main__":
    unittest.main()
