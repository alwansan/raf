import hashlib
import tempfile
import unittest
from pathlib import Path

from gfxlab.tools.original_model_probe import (
    WORD_WEIGHTS, name_score, ptr, sha_size, export_one, assert_plain, MAX_BYTES
)

class MockMesh:
    def __init__(self,text):self.text=text
    def parse_as_object(self):return self
    def export(self):return self.text

class ModelProbeTests(unittest.TestCase):
    def test_player_matches_outrank_generic(self):
        self.assertGreater(name_score("PlayerCharacter"), name_score("WoodBarrel"))
        self.assertGreater(name_score("SURVIVOR"), name_score("Hand"))
        self.assertEqual(name_score("SailBoat"),0)
    def test_ptr_valid(self):
        self.assertEqual(ptr({"m_FileID":0,"m_PathID":10}),(0,10))
        self.assertEqual(ptr({"fileID":2,"pathID":7}),(2,7))
        self.assertIsNone(ptr({"m_FileID":"bad","m_PathID":1}))
        self.assertIsNone(ptr(None))
    def test_sha_size(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test";p.write_bytes(b"ABC")
            self.assertEqual(sha_size(p),(3,hashlib.sha256(b"ABC").hexdigest()))
    def test_mesh_obj_accept(self):
        text="# test\n"+"v 0 0 0\n"*16+"f 1 2 3\n"
        txt,v,f=export_one(MockMesh(text))
        self.assertEqual((v,f),(16,1))
    def test_mesh_obj_reject_empty(self):
        with self.assertRaises(ValueError):export_one(MockMesh("# empty\n"))
    def test_mesh_obj_reject_no_faces(self):
        with self.assertRaises(ValueError):export_one(MockMesh("v 0 0 0\n"*16))
    def test_mesh_obj_reject_invalid_content(self):
        with self.assertRaises(ValueError):export_one(MockMesh("not an obj\n"+"v 0 0 0\n"*16+"f 1 2 3\n"))
    def test_safe_source_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"input").write_bytes(b"a")
            (root/"alias").symlink_to(root/"input")
            with self.assertRaises(ValueError):assert_plain(root/"alias",root)
    def test_safe_source_reject_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"src";root.mkdir()
            outside=Path(d)/"outside";outside.write_bytes(b"a")
            with self.assertRaises(ValueError):assert_plain(outside,root)

if __name__ == "__main__":unittest.main()
