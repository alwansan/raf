import tempfile
import unittest
from pathlib import Path

from scripts.audit_mesh_stream_dependencies import classify_stream_range


class MeshStreamCoverageTests(unittest.TestCase):
    def test_safe_exact_ranges_and_empty_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"sharedassets3.assets.resS").write_bytes(b"0"*32)
            self.assertEqual(classify_stream_range(root,"sharedassets3.assets.resS",0,32),"available-range")
            self.assertEqual(classify_stream_range(root,"sharedassets3.assets.resS",30,3),"out-of-bounds")
            self.assertEqual(classify_stream_range(root,"sharedassets3.assets.resS",0,0),"invalid-range")
            self.assertEqual(classify_stream_range(root,"sharedassets3.assets.resS",-1,1),"invalid-range")

    def test_lfs_pointer_distinguished_from_actual_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"sharedassets0.assets.resS").write_text(
                "version https://git-lfs.github.com/spec/v1\\noid sha256:"+"a"*64+"\\nsize 200000\\n"
            )
            self.assertEqual(classify_stream_range(root,"sharedassets0.assets.resS",0,128),"lfs-pointer")
            self.assertEqual(classify_stream_range(root,"missing.resS",0,128),"missing-file")

    def test_reject_parent_paths_and_absolute_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for ref in ("../outside.resS","/tmp/elsewhere.resS","C:\\\\windows.resS",
                        "archive:/CAB/test.resS","dir/../../file.resS"):
                with self.subTest(ref=ref):
                    self.assertEqual(classify_stream_range(root,ref,0,100),"unsupported-path")


if __name__=="__main__":
    unittest.main()
