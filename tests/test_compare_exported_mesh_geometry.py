import struct
import unittest
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
from scripts.compare_exported_mesh_geometry import positions, compare, inspect


class ExportGeometryTests(unittest.TestCase):
    def test_empty_baseline_keeps_guid_and_reports_invalid_positions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            mesh = root / 'Assets/Mesh/test.asset'
            mesh.parent.mkdir(parents=True)
            mesh.write_text('synthetic')
            mesh.with_suffix('.asset.meta').write_text('guid: ' + 'a' * 32)
            yaml = SimpleNamespace(safe_load=lambda _: {'Mesh': {
                'm_Name': 'test', 'm_VertexData': {'m_VertexCount': 0}}})
            with patch.dict('sys.modules', {'yaml': yaml}):
                rows, errors = inspect(root, {'test'})
            self.assertEqual(errors, {})
            self.assertEqual(rows['test.asset']['guid'], 'a' * 32)
            self.assertEqual(rows['test.asset']['position_status'], 'empty-vertices')
            self.assertFalse(rows['test.asset']['valid_positions'])

    def test_stream_stride_and_position_offset(self):
        tree = {"m_VertexData": {"m_VertexCount": 2, "m_Channels": [
            {"stream": 1, "offset": 4, "format": 0, "dimension": 3},
            {"stream": 0, "offset": 0, "format": 0, "dimension": 1},
            {"stream": 1, "offset": 0, "format": 0, "dimension": 1}],
            "_typelessdata": (b'\0' * 16 + struct.pack('<4f4f', 0, 1, 2, 3, 0, 4, 5, 6)).hex()}}
        self.assertEqual(positions(tree), [(1., 2., 3.), (4., 5., 6.)])

    def test_truncated_data_refused(self):
        with self.assertRaises(ValueError):
            positions({"m_VertexData": {"m_VertexCount": 1, "m_Channels": [
                {"stream": 0, "offset": 0, "format": 0, "dimension": 3}], "_typelessdata": "00"}})

    def test_yaml_null_typelessdata_is_truncated_payload(self):
        with self.assertRaisesRegex(ValueError, 'truncated-positions'):
            positions({"m_VertexData": {"m_VertexCount": 1, "m_Channels": [
                {"stream": 0, "offset": 0, "format": 0, "dimension": 3}], "_typelessdata": None}})

    def test_meta_changes_are_visible(self):
        result = compare({"a": {"guid": "a", "vertices": 3, "nonfinite": 1}},
                         {"a": {"guid": "b", "vertices": 3, "nonfinite": 0}})
        self.assertEqual(result["common_meta_guid_changes"], 1)
        self.assertEqual(result["before_nonfinite_meshes"], 1)
        self.assertEqual(result["after_nonfinite_meshes"], 0)

    def test_same_guid_with_changed_meta_bytes_is_visible(self):
        result = compare({"a": {"guid": "a", "meta_sha256": "old", "vertices": 3, "nonfinite": 0}},
                         {"a": {"guid": "a", "meta_sha256": "new", "vertices": 3, "nonfinite": 0}})
        self.assertEqual(result["common_meta_guid_changes"], 0)
        self.assertEqual(result["common_meta_byte_changes"], 1)
