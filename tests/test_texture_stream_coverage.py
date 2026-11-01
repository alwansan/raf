from pathlib import Path
import tempfile
import unittest
from scripts.audit_texture_stream_coverage import extent
from scripts.hydrate_render_payloads import pointer, PATTERN

class CoverageTests(unittest.TestCase):
    def test_extents(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'sharedassets0.assets.resS').write_bytes(bytes(100))
            self.assertEqual(extent(root,'sharedassets0.assets.resS',10,90),'covered')
            self.assertEqual(extent(root,'archive:/sharedassets0.assets.resS',10,91),'truncated_provider')
            self.assertEqual(extent(root,'missing.resS',0,1),'missing_provider')
            self.assertEqual(extent(root,'bad.resS',-1,1),'invalid_extent')
            (root/'pointer.resS').write_text('version https://git-lfs.github.com/spec/v1\n')
            self.assertEqual(extent(root,'pointer.resS',0,1),'lfs_pointer')
    def test_allowlist_and_pointers(self):
        self.assertTrue(PATTERN.fullmatch('Raft/Raft_Data/resources.assets.resS'))
        self.assertFalse(PATTERN.fullmatch('Raft/Raft.exe'))
        self.assertFalse(PATTERN.fullmatch('Raft/Raft_Data/StreamingAssets/MasterBank.bank'))
        self.assertEqual(pointer(('version https://git-lfs.github.com/spec/v1\noid sha256:'+'a'*64+'\nsize 123\n').encode()),('a'*64,123))
        with self.assertRaises(ValueError): pointer(b'not a pointer')
