"""Actual PyYAML parser + geometry-consumer counterfactuals, authored data only."""
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from scripts.compare_exported_mesh_geometry import load_mesh_yaml, positions, inspect
from scripts.gt_verify_original_mesh_export import export_geometry, geometry, compare_geometry
from test_gt_verify_original_mesh_export import YAML, TREE, FID

HEX="0000803f"*3
DUPLICATE="mesh_yaml_duplicate_mapping_key"
MERGE="mesh_yaml_merge_key_unsupported"


def replace_once(text, old, new):
    assert text.count(old)==1, old
    return text.replace(old,new,1)


def matrix_yaml():
    lines=["  - e00: -0"]+[f"    e{r}{c}: 1" for r in range(4) for c in range(4) if (r,c)!=(0,0)]
    return replace_once(YAML,"  m_BindPose: []","  m_BindPose:\n"+"\n".join(lines))


def cases():
    # Insert a conflicting *earlier* value, leaving the good final bytes and
    # layout untouched. Old default YAML loaders silently retain the latter.
    base=YAML
    fields=[
        ("duplicate_Mesh_root","\nMesh:\n","\nMesh: {}\nMesh:\n"),
        ("duplicate_vertex_mapping","  m_VertexData:\n","  m_VertexData: {}\n  m_VertexData:\n"),
        ("duplicate_vertex_count","    m_VertexCount: 1","    m_VertexCount: 2\n    m_VertexCount: 1"),
        ("duplicate_vertex_size","    m_DataSize: 12","    m_DataSize: 11\n    m_DataSize: 12"),
        ("duplicate_vertex_payload","    _typelessdata: "+HEX,"    _typelessdata: "+"00"*12+"\n    _typelessdata: "+HEX),
        ("duplicate_channel_sequence","    m_Channels:\n","    m_Channels: []\n    m_Channels:\n"),
        ("duplicate_channel_stream","    - stream: 0","    - stream: 1\n      stream: 0"),
        ("duplicate_channel_offset","      offset: 0","      offset: 4\n      offset: 0"),
        ("duplicate_channel_format","      format: 0","      format: 1\n      format: 0"),
        ("duplicate_channel_dimension","      dimension: 3","      dimension: 2\n      dimension: 3"),
        ("duplicate_compressed_mapping","  m_CompressedMesh:\n","  m_CompressedMesh: {}\n  m_CompressedMesh:\n"),
        ("duplicate_UV_info","    m_UVInfo: 0","    m_UVInfo: 1\n    m_UVInfo: 0"),
        ("duplicate_packed_triangles","    m_Triangles:\n","    m_Triangles: {}\n    m_Triangles:\n"),
        ("duplicate_packed_count","      m_NumItems: 1","      m_NumItems: 9\n      m_NumItems: 1"),
        ("duplicate_packed_bits","      m_BitSize: 3","      m_BitSize: 7\n      m_BitSize: 3"),
        ("duplicate_packed_bytes","      m_Data: 08","      m_Data: ff\n      m_Data: 08"),
        ("duplicate_index_format","  m_IndexFormat: 0","  m_IndexFormat: 1\n  m_IndexFormat: 0"),
        ("duplicate_index_bytes","  m_IndexBuffer: 0000","  m_IndexBuffer: ffff\n  m_IndexBuffer: 0000"),
        ("duplicate_submesh_sequence","  m_SubMeshes: []","  m_SubMeshes: [{firstByte: 9}]\n  m_SubMeshes: []"),
        ("duplicate_bone_hashes","  m_BoneNameHashes: 010000c0","  m_BoneNameHashes: 00000000\n  m_BoneNameHashes: 010000c0"),
        ("duplicate_bone_weights","  m_VariableBoneCountWeights:\n","  m_VariableBoneCountWeights: {}\n  m_VariableBoneCountWeights:\n"),
        ("duplicate_nested_bone_weights_bytes","  m_VariableBoneCountWeights:\n    m_Data:\n","  m_VariableBoneCountWeights:\n    m_Data: ffffffff\n    m_Data:\n"),
        ("duplicate_stream_size","    size: 0","    size: 12\n    size: 0"),
        ("duplicate_stream_mapping","  m_StreamData:\n","  m_StreamData: {size: 12}\n  m_StreamData:\n"),
        ("identical_duplicate_value","  m_IndexFormat: 0","  m_IndexFormat: 0\n  m_IndexFormat: 0"),
        ("quoted_duplicate_key","  m_IndexFormat: 0",'  "m_IndexFormat": 1\n  m_IndexFormat: 0'),
    ]
    out=[(name,base,replace_once(base,old,new),DUPLICATE) for name,old,new in fields]
    pose=matrix_yaml()
    out.append(("duplicate_bind_pose_element",pose,
                replace_once(pose,"  - e00: -0","  - e00: 2\n    e00: -0"),DUPLICATE))
    out.append(("duplicate_bind_pose_array",pose,
                replace_once(pose,"  m_BindPose:\n","  m_BindPose: []\n  m_BindPose:\n"),DUPLICATE))
    out.append(("merge_override_index_format",base,
                replace_once(base,"  m_IndexFormat: 0","  <<: {m_IndexFormat: 1}\n  m_IndexFormat: 0"),MERGE))
    return out


def backends():
    assert yaml.__with_libyaml__ and yaml.CSafeLoader is not yaml.SafeLoader
    return (("libyaml",yaml.CSafeLoader),("python",yaml.SafeLoader))


class MeshYamlUniqueMapping(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.mesh=self.root/"mesh.asset"

    def test_duplicate_and_merge_counterfactuals_through_actual_export_consumer(self):
        for label,loader in backends():
            with patch.object(yaml,"CSafeLoader",loader):
                for name,clean,conflicting,reason in cases():
                    with self.subTest(loader=label,case=name):
                        self.mesh.write_text(clean)
                        export_geometry(self.mesh,FID)
                        self.mesh.write_text(conflicting)
                        with self.assertRaisesRegex(ValueError,"^"+reason+"$"):
                            export_geometry(self.mesh,FID)

    def test_clean_geometry_and_hex_types_both_backends(self):
        expected=geometry(TREE,bytes.fromhex(HEX),b"\0\0")
        for label,loader in backends():
            with self.subTest(loader=label),patch.object(yaml,"CSafeLoader",loader):
                self.mesh.write_text(YAML)
                self.assertEqual(export_geometry(self.mesh,FID),expected)
                tree=load_mesh_yaml(YAML)
                self.assertEqual(tree["m_VertexData"]["_typelessdata"],HEX)
                self.assertEqual(tree["m_IndexBuffer"],"0000")
                self.assertEqual(tree["m_CompressedMesh"]["m_Triangles"]["m_Data"],"08")
                self.assertEqual(tree["m_BoneNameHashes"],"010000c0")
                self.assertEqual(positions(tree),[(1.0,1.0,1.0)])
                self.assertIn(tree["m_VariableBoneCountWeights"]["m_Data"],(None,""))

    def test_signed_zero_and_nonzero_comparison_unchanged(self):
        clean=matrix_yaml()
        for label,loader in backends():
            with self.subTest(loader=label),patch.object(yaml,"CSafeLoader",loader):
                tree=load_mesh_yaml(clean)
                value=tree["m_BindPose"][0]["e00"]
                self.assertEqual(math.copysign(1.0,value),-1.0)
                self.mesh.write_text(clean)
                expected=export_geometry(self.mesh,FID)
                self.mesh.write_text(clean.replace("e00: -0","e00: 0"))
                self.assertEqual(compare_geometry(expected,export_geometry(self.mesh,FID)),([],1))
                self.mesh.write_text(clean.replace("e00: -0","e00: 0.125"))
                self.assertEqual(compare_geometry(expected,export_geometry(self.mesh,FID)),
                                 (["bind_pose_matrices"],0))

    def test_separate_mapping_scopes_and_nonconflicting_quoted_keys(self):
        text="Mesh:\n  a: {format: 0, offset: 0}\n  b: {format: 1, offset: 4}\n  'c': 2\n"
        for label,loader in backends():
            with self.subTest(loader=label),patch.object(yaml,"CSafeLoader",loader):
                self.assertEqual(load_mesh_yaml(text),{"a":{"format":0,"offset":0},
                                                       "b":{"format":1,"offset":4},"c":2})

    def test_semantically_duplicate_key_and_unhashable_key_are_private_errors(self):
        for label,loader in backends():
            with patch.object(yaml,"CSafeLoader",loader):
                for raw,reason in (
                    ("Mesh:\n  1: 2\n  true: 3\n",DUPLICATE),
                    ("Mesh:\n  ? [a,b]\n  : value\n","mesh_yaml_unhashable_mapping_key"),
                ):
                    with self.subTest(loader=label,reason=reason):
                        with self.assertRaisesRegex(ValueError,"^"+reason+"$"):
                            load_mesh_yaml(raw)

    def test_position_audit_records_parse_failure_instead_of_valid_geometry(self):
        mesh=self.root/"Assets/Mesh/test.asset"
        mesh.parent.mkdir(parents=True)
        mesh.with_suffix(".asset.meta").write_text("guid: "+"a"*32)
        original=YAML.replace("Mesh:\n","Mesh:\n  m_Name: authored\n",1)
        conflicting=replace_once(original,"    m_VertexCount: 1","    m_VertexCount: 2\n    m_VertexCount: 1")
        for label,loader in backends():
            with self.subTest(loader=label),patch.object(yaml,"CSafeLoader",loader):
                mesh.write_text(original)
                rows,errors=inspect(self.root,{"authored"})
                self.assertEqual(errors,{})
                self.assertTrue(rows["test.asset"]["valid_positions"])
                mesh.write_text(conflicting)
                rows,errors=inspect(self.root,{"authored"})
                self.assertEqual(rows,{})
                self.assertEqual(errors,{"ValueError":1})

    def test_header_identity_and_external_stream_gate_still_reject(self):
        self.mesh.write_text(YAML)
        with self.assertRaisesRegex(ValueError,"yaml_identity"):
            export_geometry(self.mesh,FID+1)
        self.mesh.write_text(YAML.replace("size: 0","size: 12"))
        with self.assertRaisesRegex(ValueError,"vertex_storage"):
            export_geometry(self.mesh,FID)


if __name__=="__main__":
    unittest.main()
