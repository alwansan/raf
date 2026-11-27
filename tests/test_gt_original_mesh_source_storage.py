"""Source-side Mesh storage type and range controls; all inputs authored."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from scripts import gt_verify_original_mesh_export as mesh
from test_gt_verify_original_mesh_export import TREE, YAML, FID

BYTE="invalid_original_mesh_byte_array"
WORDS="invalid_original_mesh_uint32_array"
STREAM="invalid_original_mesh_stream_descriptor"
VERTEX=("m_VertexData","m_DataSize")
INDEX=("m_IndexBuffer",)
PACKED=("m_CompressedMesh","m_Triangles","m_Data")
HASHES=("m_BoneNameHashes",)
WEIGHTS=("m_VariableBoneCountWeights","m_Data")
RAW=b"\0"*12


def assign(tree, keys, value):
    node=tree
    for key in keys[:-1]:
        node=node[key]
    node[keys[-1]]=value


def clean_source():
    tree=deepcopy(TREE)
    assign(tree,VERTEX,list(RAW))
    assign(tree,INDEX,[0,0])
    assign(tree,PACKED,[0])
    assign(tree,HASHES,[0,1])
    assign(tree,WEIGHTS,[0,1])
    tree["m_StreamData"]={"size":0,"offset":0,"path":""}
    return tree


def authored_export(tree):
    # The clean comparison uses the actual YAML consumer, not an equality
    # between two potentially coerced source trees.
    def words(values):
        return struct.pack(f"<{len(values)}I",*values).hex()
    raw=bytes(tree["m_VertexData"]["m_DataSize"])
    return (YAML.replace("    m_DataSize: 12",f"    m_DataSize: {len(raw)}")
            .replace("0000803f0000803f0000803f",raw.hex())
            .replace("  m_IndexBuffer: 0000","  m_IndexBuffer: "+bytes(tree["m_IndexBuffer"]).hex())
            .replace("      m_Data: 08","      m_Data: "+bytes(tree["m_CompressedMesh"]["m_Triangles"]["m_Data"]).hex())
            .replace("  m_BoneNameHashes: 010000c0","  m_BoneNameHashes: "+words(tree["m_BoneNameHashes"]))
            .replace("    m_Data:\n","    m_Data: "+words(tree["m_VariableBoneCountWeights"]["m_Data"])+"\n"))


def cases():
    # Each malformed variant used to have exactly the clean bytes/dictionary.
    rows=[]
    def variant(name,keys,clean,bad,reason):
        a=clean_source()
        assign(a,keys,clean)
        b=deepcopy(a)
        assign(b,keys,bad)
        rows.append((name,a,b,reason))
    variant("scalar_vertex_bytes",VERTEX,[0]*12,12,BYTE)
    variant("bool_vertex_element",VERTEX,[0]*12,[False]+[0]*11,BYTE)
    variant("mapping_vertex_bytes",VERTEX,list(range(12)),dict.fromkeys(range(12)),BYTE)
    variant("scalar_index_bytes",INDEX,[0,0],2,BYTE)
    variant("bool_index_element",INDEX,[0,1],[False,True],BYTE)
    variant("mapping_index_bytes",INDEX,[0,1],{0:"x",1:"y"},BYTE)
    variant("scalar_packed_bytes",PACKED,[0],1,BYTE)
    variant("bool_scalar_packed_bytes",PACKED,[0],True,BYTE)
    variant("bool_packed_element",PACKED,[0],[False],BYTE)
    variant("mapping_packed_bytes",PACKED,[0],{0:"ignored"},BYTE)
    variant("byte_array_as_bone_words",HASHES,[0,1],b"\0\1",WORDS)
    variant("bytearray_as_bone_words",HASHES,[0,1],bytearray(b"\0\1"),WORDS)
    variant("mapping_as_bone_words",HASHES,[0,1],{0:"x",1:"y"},WORDS)
    variant("bool_bone_words",HASHES,[0,1],[False,True],WORDS)
    variant("byte_array_as_weight_words",WEIGHTS,[0,1],b"\0\1",WORDS)
    variant("mapping_as_weight_words",WEIGHTS,[0,1],{0:"x",1:"y"},WORDS)
    variant("bool_weight_words",WEIGHTS,[0,1],[False,True],WORDS)
    for name,update in (
        ("float_zero_stream_size",{"size":0.0}),
        ("bool_zero_stream_size",{"size":False}),
        ("null_stream_size",{"size":None}),
        ("empty_string_stream_size",{"size":""}),
        ("empty_list_stream_size",{"size":[]}),
        ("positive_offset_empty_stream",{"offset":1}),
        ("negative_offset_empty_stream",{"offset":-1}),
        ("float_offset_empty_stream",{"offset":0.0}),
        ("bool_offset_empty_stream",{"offset":False}),
        ("null_offset_empty_stream",{"offset":None}),
        ("stale_provider_empty_stream",{"path":"authored.resS"}),
        ("numeric_provider_empty_stream",{"path":0}),
        ("bool_provider_empty_stream",{"path":False}),
        ("mapping_provider_empty_stream",{"path":{}}),
    ):
        a=clean_source()
        b=deepcopy(a)
        b["m_StreamData"].update(update)
        rows.append((name,a,b,STREAM))
    return rows


class OriginalMeshSourceStorage(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.target=self.root/"authored.asset"
        self.provider=self.root/"authored.resS"
        self.provider_bytes=b"pre"+RAW+b"post"
        self.provider.write_bytes(self.provider_bytes)
        self.records={"Raft_Data/authored.resS":
                      ("plain",len(self.provider_bytes),sha256(self.provider_bytes).hexdigest())}

    def proof(self,tree,seen=None):
        return mesh.source_geometry(tree,self.root,self.records,set() if seen is None else seen)

    def export(self,tree):
        self.target.write_text(authored_export(tree))
        return mesh.export_geometry(self.target,FID)

    def test_all_old_equalities_refused_by_source_consumer(self):
        for name,clean,bad,reason in cases():
            with self.subTest(case=name):
                self.assertEqual(self.proof(clean),self.export(clean))
                with self.assertRaisesRegex(ValueError,"^"+reason+"$"):
                    self.proof(bad)

    def test_explicit_byte_sequences_and_uint32_words(self):
        baseline=clean_source()
        expected=self.export(baseline)
        for kind in (list,tuple,bytes,bytearray):
            with self.subTest(byte_sequence=kind.__name__):
                t=clean_source()
                for path,value in ((VERTEX,RAW),(INDEX,b"\0\0"),(PACKED,b"\0")):
                    assign(t,path,kind(value))
                assign(t,HASHES,(0,1))
                assign(t,WEIGHTS,(0,1))
                self.assertEqual(self.proof(t),expected)
        t=clean_source()
        assign(t,HASHES,[0,0xc0000001,0xffffffff])
        assign(t,WEIGHTS,[0x80000000,0xffffffff])
        self.assertEqual(self.proof(t),self.export(t))

    def test_compressed_skin_and_multistream_metadata_not_narrowed(self):
        t=clean_source()
        t["m_VertexData"]["m_Channels"].append({"stream":2,"offset":0,"format":1,"dimension":2})
        t["m_CompressedMesh"]["m_UVInfo"]=9
        t["m_CompressedMesh"]["m_UV"]={"m_NumItems":2,"m_BitSize":8,"m_Range":1.0,"m_Start":-0.25,"m_Data":[0,255]}
        t["m_BindPose"]=[{f"e{r}{c}":(-0.0 if (r,c)==(0,0) else 1.0)
                          for r in range(4) for c in range(4)}]
        proof=self.proof(t)
        self.assertEqual(proof["compressed_attributes"][0],9)
        self.assertEqual(proof["compressed_attributes"][1]["m_UV"][-1],(2,sha256(b"\0\xff").hexdigest()))
        self.assertEqual(proof["vertex_channels"][-1],(2,0,1,2))
        self.assertEqual(proof["bind_pose_matrices"][0][0],struct.pack("<f",-0.0))
        self.assertEqual(proof["bone_name_hashes"],(8,sha256(struct.pack("<2I",0,1)).hexdigest()))

    def test_empty_inline_and_optional_empty_path(self):
        t=clean_source()
        for descriptor in ({"offset":0,"size":0},{"offset":0,"size":0,"path":None},
                           {"offset":0,"size":0,"path":""}):
            t["m_StreamData"]=descriptor
            with patch.object(mesh,"verified_range",side_effect=AssertionError("unexpected I/O")):
                self.assertEqual(self.proof(t),self.export(t))
        assign(t,VERTEX,[])
        assign(t,INDEX,[])
        assign(t,PACKED,[])
        assign(t,HASHES,[])
        assign(t,WEIGHTS,[])
        self.assertEqual(self.proof(t),self.export(t))

    def streamed(self,inline):
        t=clean_source()
        assign(t,VERTEX,inline)
        t["m_StreamData"]={"path":"authored.resS","offset":3,"size":12}
        return t

    def test_real_verified_range_and_equal_dual_storage(self):
        expected=self.export(clean_source())
        seen=set()
        with patch.object(mesh,"verified_range",wraps=mesh.verified_range) as read:
            self.assertEqual(self.proof(self.streamed([]),seen),expected)
            self.assertEqual(self.proof(self.streamed(list(RAW)),seen),expected)
            self.assertEqual(read.call_count,2)
        self.assertEqual(seen,{"authored.resS"})

    def test_conflicting_dual_storage_not_counted_as_verified(self):
        seen=set()
        with self.assertRaisesRegex(ValueError,"conflicting_original_mesh_vertex_payload"):
            self.proof(self.streamed([1]*12),seen)
        self.assertEqual(seen,set())

    def test_no_cached_trust_after_provider_mutation(self):
        seen=set()
        tree=self.streamed([])
        self.proof(tree,seen)
        self.provider.write_bytes(b"X"+self.provider_bytes[1:])
        with self.assertRaisesRegex(ValueError,"pinned_pixel_provider_SHA_mismatch"):
            self.proof(tree,seen)

    def test_positive_stream_invalid_types_and_extents_reject_before_read(self):
        for update,reason in (
            ({"offset":True},STREAM),({"size":12.0},STREAM),
            ({"size":-1},STREAM),({"offset":-1},STREAM),
            ({"path":"../authored.resS"},"invalid_original_mesh_stream_name"),
            ({"path":None},"invalid_original_mesh_stream_name"),
            ({"offset":len(self.provider_bytes)},"invalid_original_mesh_stream_extent"),
        ):
            t=self.streamed([])
            t["m_StreamData"].update(update)
            with self.subTest(update=update),patch.object(mesh,"verified_range",side_effect=AssertionError("unexpected I/O")):
                with self.assertRaisesRegex(ValueError,"^"+reason+"$"):
                    self.proof(t)
        t=self.streamed([])
        with patch.object(mesh,"verified_range",side_effect=AssertionError("unexpected I/O")):
            with self.assertRaises(KeyError):
                mesh.source_geometry(t,self.root,{},set())

    def test_bad_numeric_range_and_oversize_fail_without_allocation(self):
        for value in (-1,256,1.0,"1",None):
            with self.subTest(byte=value):
                with self.assertRaisesRegex(ValueError,BYTE):
                    mesh.source_byte_array([value])
        for value in (-1,2**32,1.0,"1",None,False):
            with self.subTest(word=value):
                with self.assertRaisesRegex(ValueError,WORDS):
                    mesh.source_uint32_array([value])
        with self.assertRaisesRegex(ValueError,BYTE):
            mesh.source_byte_array(10**12)
        with patch.object(mesh,"MAX_PAYLOAD",8):
            with self.assertRaisesRegex(ValueError,"oversized_original_mesh_payload"):
                mesh.source_byte_array(b"x"*9)
            with self.assertRaisesRegex(ValueError,"oversized_original_mesh_payload"):
                mesh.source_uint32_array([1,2,3])


if __name__=="__main__":
    unittest.main()
