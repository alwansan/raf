"""Authored independent byte/range controls on the same renderer route."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import struct
import unittest
from types import SimpleNamespace as NS
from unittest.mock import patch

import test_gt_renderer_submesh_routes as fixture
from scripts import gt_mesh_vertex_payload as payload
from scripts import gt_renderer_submesh_routes as routes
from scripts.gt_verify_original_mesh_export import source_geometry
import test_gt_verify_original_mesh_export as legacy


class ByteRoutes(unittest.TestCase):
    def setUp(self):
        self.f=fixture.OrderedRoutes("test_actual_yaml_ordered_two_submeshes")
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.root=self.f.project/"authored-source"
        self.root.mkdir()
        self.key=(self.f.owner,4)
        self.target=(self.f.mesh,4300000)
        self.raw=struct.pack("<30f",*range(30))
        self.other=struct.pack("<30f",*(i+.25 for i in range(30)))
        self.source=deepcopy(self.f.docs[self.target][1])
        self.source["m_IndexBuffer"]=list(self.f.indices)
        self.source["m_VertexData"]["m_DataSize"]=list(self.raw)
        self.source["m_CompressedMesh"]={"m_UVInfo":0}
        self.source["m_StreamData"]={"path":"","offset":0,"size":0}
        exp=self.f.docs[self.target][1]
        exp["m_VertexData"].update(m_DataSize=len(self.raw),_typelessdata=self.raw.hex())
        exp["m_CompressedMesh"]={"m_UVInfo":0}
        exp["m_StreamData"]={"path":"","offset":0,"size":0}
        self.owner_bytes=b"authored parser injection, not serialized Unity"
        (self.root/self.f.owner).write_bytes(self.owner_bytes)
        self.provider=self.root/"test.resS"
        self.provider_bytes=b"pre"+self.raw+self.other+b"post"
        self.provider.write_bytes(self.provider_bytes)
        self.records={"Raft_Data/"+self.f.owner:("plain",len(self.owner_bytes),sha256(self.owner_bytes).hexdigest()),
                      "Raft_Data/test.resS":("plain",len(self.provider_bytes),sha256(self.provider_bytes).hexdigest())}

    def stream(self,offset=3):
        self.source["m_VertexData"]["m_DataSize"]=[]
        self.source["m_StreamData"]={"path":"test.resS","offset":offset,"size":120}

    def evidence(self):
        def loader(data):
            self.assertEqual(data,self.owner_bytes)
            obj=NS(type=NS(name="Mesh"),path_id=4,read_typetree=lambda:deepcopy(self.source))
            return NS(file=NS(objects={4:obj},externals=[]))
        proofs={}
        meshes,_=routes.source_records(self.root,self.records,[self.f.owner],loader=loader,
                                      vertex_payloads=proofs)
        return {**self.f.objects,**meshes},proofs

    def check(self,strict=True):
        objects,proofs=self.evidence()
        self.f.write()
        mapping={(r["source"]["owner"],r["source"]["path_id"]):
                  (r["class_id"],routes.trace_pointer(r["export"]),r["exportable"])
                  for r in self.f.mappings}
        files,docs=routes.actual_index(self.f.project,mapping)
        return routes.compare(objects,{self.f.owner:[]},mapping,files,docs,
                              vertex_payloads=proofs if strict else None)

    def assert_bound(self):
        r=self.check()
        self.assertTrue(r["selected_same_route_vertex_and_UV_bytes_verified"],r)
        self.assertEqual(r["counts"]["complete_vertex_byte_bound_renderer_routes"],1)
        self.assertEqual(r["counts"]["complete_vertex_byte_bound_submesh_routes"],2)

    def assert_rejected(self,reason):
        r=self.check()
        self.assertFalse(r["selected_renderer_routes_preserved"],r)
        self.assertFalse(r["selected_same_route_vertex_and_UV_bytes_verified"])
        self.assertIn(reason,r["reason_counts"])
        self.assertFalse(r["counts"].get("complete_vertex_byte_bound_renderer_routes",0))
        self.assertNotIn("test.resS",str(r))

    def test_inline_exact_same_route(self):
        self.assert_bound()

    def test_stream_exact_same_route(self):
        self.stream()
        self.assert_bound()

    def test_same_size_provider_change_after_first_success(self):
        self.stream()
        self.assert_bound()
        self.provider.write_bytes(b"X"+self.provider_bytes[1:])
        self.assert_rejected("vertex_provider_SHA_mismatch")

    def test_swapped_equal_length_stream_range(self):
        self.stream(123)
        self.assertTrue(self.check(False)["selected_renderer_routes_preserved"])
        self.assert_rejected("same_route_vertex_or_UV_bytes_drift")

    def test_UV_bytes_only_changed_same_layout_and_indices(self):
        v=self.f.docs[self.target][1]["m_VertexData"]
        raw=bytearray(self.raw)
        raw[12:16]=struct.pack("<f",.125)
        v["_typelessdata"]=raw.hex()
        self.assertTrue(self.check(False)["selected_renderer_routes_preserved"])
        self.assert_rejected("same_route_vertex_or_UV_bytes_drift")

    def test_position_bytes_only_changed(self):
        v=self.f.docs[self.target][1]["m_VertexData"]
        raw=bytearray(self.raw)
        raw[:4]=struct.pack("<f",-1)
        v["_typelessdata"]=raw.hex()
        self.assert_rejected("same_route_vertex_or_UV_bytes_drift")

    def test_wrong_material_not_promoted_by_correct_vertex_bytes(self):
        self.f.docs[(self.f.scene,102)][1]["m_Materials"].reverse()
        self.assert_rejected("ordered_pointer_target_mismatch")

    def test_missing_pin(self):
        self.stream()
        del self.records["Raft_Data/test.resS"]
        self.assert_rejected("unbound_source_vertex_stream")

    def test_out_of_range(self):
        self.stream(len(self.provider_bytes)-1)
        self.assert_rejected("invalid_vertex_provider_range")

    def test_inline_and_stream(self):
        self.stream()
        self.source["m_VertexData"]["m_DataSize"]=list(self.raw)
        self.assert_rejected("ambiguous_inline_and_stream_vertex_payload")

    def test_compressed_not_promoted(self):
        self.source["m_CompressedMesh"]["m_UV"]={"m_NumItems":1,"m_Data":[1]}
        self.assert_rejected("unsupported_compressed_vertex_payload")

    def test_export_unbound_stream(self):
        self.f.docs[self.target][1]["m_StreamData"]={"path":"test.resS","offset":3,"size":120}
        self.assert_rejected("unbound_export_vertex_stream")

    def test_multi_stream_layout_unproven(self):
        self.source["m_VertexData"]["m_Channels"][4]["stream"]=1
        self.f.docs[self.target][1]["m_VertexData"]["m_Channels"][4]["stream"]=1
        self.assert_rejected("unsupported_multi_vertex_stream_layout")

    def test_multi_range_hashes_one_read_across_blocks(self):
        pin=(len(self.provider_bytes),sha256(self.provider_bytes).hexdigest())
        with patch.object(payload,"CHUNK",17), patch.object(payload,"regular_open",wraps=payload.regular_open) as op:
            got=payload.verified_range_digests(self.provider,pin,[(3,120),(123,120),(13,22),(3,120)])
            self.assertEqual(op.call_count,1)
        for (off,n),digest in got.items():
            self.assertEqual(digest,sha256(self.provider_bytes[off:off+n]).hexdigest())

    def test_legacy_never_reuses_provider_verification(self):
        t=deepcopy(legacy.TREE)
        t["m_VertexData"]["m_DataSize"]=[]
        t["m_StreamData"]={"path":"test.resS","offset":3,"size":12}
        t["m_IndexBuffer"]=[0,0]
        seen=set()
        expected=source_geometry(t,self.root,self.records,seen)
        self.assertEqual(expected["vertex_buffer"],(12,sha256(self.raw[:12]).hexdigest()))
        self.provider.write_bytes(b"X"+self.provider_bytes[1:])
        with self.assertRaisesRegex(ValueError,"SHA_mismatch"):
            source_geometry(t,self.root,self.records,seen)


if __name__=="__main__":
    unittest.main()
