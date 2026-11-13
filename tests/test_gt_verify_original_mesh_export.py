import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.gt_verify_original_mesh_export import compare_geometry, export_geometry, geometry, trace_meshes
from scripts import patch_export_lineage

INSTANCE = "a" * 32
GUID = "b" * 32
FID = 4300000
TREE = {
    "m_VertexData": {"m_VertexCount": 1, "m_Channels": [
        {"stream": 0, "offset": 0, "format": 0, "dimension": 3},
    ]},
    "m_CompressedMesh": {
        "m_UVInfo": 0,
        "m_Triangles": {"m_NumItems": 1, "m_BitSize": 3, "m_Data": [8]},
    },
    "m_IndexFormat": 0,
    "m_SubMeshes": [],
    "m_BindPose": [],
    "m_BoneNameHashes": [0xc0000001],
    "m_VariableBoneCountWeights": {"m_Data": []},
}
YAML = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!43 &4300000
Mesh:
  m_VertexData:
    m_VertexCount: 1
    m_Channels:
    - stream: 0
      offset: 0
      format: 0
      dimension: 3
    m_DataSize: 12
    _typelessdata: 0000803f0000803f0000803f
  m_CompressedMesh:
    m_UVInfo: 0
    m_Triangles:
      m_NumItems: 1
      m_BitSize: 3
      m_Data: 08
  m_IndexFormat: 0
  m_IndexBuffer: 0000
  m_SubMeshes: []
  m_BindPose: []
  m_BoneNameHashes: 010000c0
  m_VariableBoneCountWeights:
    m_Data:
  m_StreamData:
    size: 0
"""


class MeshExportTests(unittest.TestCase):
    def test_exact_mesh_payload_and_channels(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mesh.asset"
            path.write_text(YAML)
            expected = geometry(TREE, bytes.fromhex("0000803f" * 3), b"\0\0")
            self.assertEqual(export_geometry(path, FID), expected)
            path.write_text(YAML.replace("dimension: 3", "dimension: 4"))
            self.assertNotEqual(export_geometry(path, FID)["vertex_channels"], expected["vertex_channels"])

    def test_bind_pose_preserves_negative_zero_without_rounding_nonzero_values(self):
        matrix = {f"e{row}{column}": 1.0 for row in range(4) for column in range(4)}
        matrix.update(e00=-0.0, e01=0.0, e02=0.125)
        lines = [f"    {field}: {value}" for field, value in matrix.items()]
        lines[0] = "  - e00: -0"
        lines[1] = "    e01: 0"
        mesh_yaml = YAML.replace("  m_BindPose: []", "  m_BindPose:\n" + "\n".join(lines))
        expected = geometry(dict(TREE, m_BindPose=[matrix]), bytes.fromhex("0000803f" * 3), b"\0\0")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mesh.asset"
            path.write_text(mesh_yaml)
            self.assertEqual(export_geometry(path, FID), expected)
            path.write_text(mesh_yaml.replace("e00: -0", "e00: 0"))
            zero_sign_diff = export_geometry(path, FID)
            self.assertNotEqual(zero_sign_diff["bind_pose_matrices"], expected["bind_pose_matrices"])
            self.assertEqual(compare_geometry(expected, zero_sign_diff), ([], 1))
            path.write_text(mesh_yaml.replace("e02: 0.125", "e02: 0.25"))
            self.assertEqual(compare_geometry(expected, export_geometry(path, FID)), (["bind_pose_matrices"], 0))

    def test_wrong_file_id_or_unresolved_external_stream_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mesh.asset"
            path.write_text(YAML)
            with self.assertRaisesRegex(ValueError, "yaml_identity"):
                export_geometry(path, FID + 1)
            path.write_text(YAML.replace("size: 0", "size: 12"))
            with self.assertRaisesRegex(ValueError, "vertex_storage"):
                export_geometry(path, FID)

    def test_pinned_hex_patch_masks_the_signed_high_nibble(self):
        original = (b"NybbleToLowercaseHexCharacter(x >> 28);\n"
                    b"NybbleToLowercaseHexCharacter(x >> 60);\n")
        digest = hashlib.sha256(original).hexdigest()
        with patch.object(patch_export_lineage, "YAML_HEX_PIN", digest):
            updated = patch_export_lineage.repair_yaml_hex(original)
            self.assertIn(b"(x >> 28) & 0x0F", updated)
            self.assertIn(b"(x >> 60) & 0x0F", updated)
            with self.assertRaisesRegex(ValueError, "Pinned YAML hex writer changed"):
                patch_export_lineage.repair_yaml_hex(updated)

    def test_mesh_capture_composes_the_existing_w1_helper(self):
        path = Path("android-port/Experiments/ExportLineage/RaftExportLineage.cs")
        original = path.read_bytes()
        composed = patch_export_lineage.add_mesh_lineage(original)
        self.assertEqual(composed.count(b'json.WriteString("export_instance", instance)'), 2)
        self.assertIn(b'asset.ClassID != 43', composed)
        self.assertIn(b'asset.ClassID is (28 or 84 or 89 or 117 or 187)', composed)
        self.assertEqual(path.read_bytes(), original)

    def test_exported_bone_hashes_must_be_valid_hex(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mesh.asset"
            path.write_text(YAML.replace("010000c0", "010000,0"))
            with self.assertRaisesRegex(ValueError, "invalid_exported_mesh_hex"):
                export_geometry(path, FID)

    def test_trace_requires_same_export_and_unique_source_identity(self):
        row = {"source": {"owner": "level1", "path_id": 100}, "exportable": True,
               "export": {"guid": GUID, "type": 2, "file_id": FID}}
        trace = {"schema_version": 1, "export_instance": INSTANCE, "meshes": [row]}
        self.assertEqual(trace_meshes(trace, INSTANCE, ("level1",)), {("level1", 100): row})
        with self.assertRaisesRegex(ValueError, "same_instance"):
            trace_meshes(trace, GUID, ("level1",))
        trace["meshes"].append(row)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            trace_meshes(trace, INSTANCE, ("level1",))
