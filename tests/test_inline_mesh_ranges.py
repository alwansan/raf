import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.fetch_verified_mesh_ranges import install_range
from scripts.inline_verified_mesh_ranges import assemble_range, inline_tree, mesh_identity


class InlineMeshRangeTests(unittest.TestCase):
    def test_payload_spans_verified_adjacent_chunks_without_extra_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            cache = Path(temporary)
            name = 'sharedassets34.assets.resS'
            chunks = []
            for offset, raw in [(0, b'abc'), (3, b'defgh')]:
                chunk = {'offset': offset, 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                chunks.append(chunk)
                install_range(cache, name, chunk, raw)
            self.assertEqual(assemble_range(name, {'size': 8, 'chunks': chunks}, 1, 6, cache), b'bcdefg')
            with self.assertRaisesRegex(ValueError, 'cover'):
                assemble_range(name, {'size': 8, 'chunks': chunks[1:]}, 1, 6, cache)

    def test_inlining_changes_only_buffer_and_stream_descriptor(self):
        tree = {'m_Name': 'synthetic', 'm_VertexData': {'m_DataSize': b'', 'm_VertexCount': 1,
                'm_Channels': [{'stream': 0, 'format': 0}]},
                'm_StreamData': {'offset': 100, 'size': 12, 'path': 'sharedassets34.assets.resS'},
                'm_IndexBuffer': b'\0\0', 'm_IsReadable': False}
        raw = b'x' * 12
        result = inline_tree(tree, raw)
        self.assertEqual(mesh_identity(result), mesh_identity(tree))
        self.assertEqual(tree['m_VertexData']['m_DataSize'], b'')
        self.assertFalse(result['m_IsReadable'])
        self.assertEqual(result['m_VertexData']['m_DataSize'], raw)
        self.assertEqual(result['m_StreamData'], {'offset': 0, 'size': 0, 'path': ''})

    def test_wrong_size_or_conflicting_original_buffer_is_refused(self):
        tree = {'m_VertexData': {'m_DataSize': b'original'},
                'm_StreamData': {'offset': 0, 'size': 3, 'path': 'sharedassets34.assets.resS'}}
        with self.assertRaisesRegex(ValueError, 'conflicting'):
            inline_tree(tree, b'new')
        with self.assertRaisesRegex(ValueError, 'descriptor'):
            inline_tree(tree, b'invalid-size')
