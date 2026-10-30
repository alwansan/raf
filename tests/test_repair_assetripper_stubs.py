import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.repair_assetripper_stub_classnames import fix_stubs

class RepairAssetRipperTemplatesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.assets=Path(self.temp.name)/"Assets"
        self.package=self.assets/"Scripts"/"Unity.Collections"
        self.package.mkdir(parents=True)
    def tearDown(self):
        self.temp.cleanup()
    def fixture(self,stem="HeapString.gen",include_meta=True):
        p=self.package/(stem+".cs")
        p.write_text("using UnityEngine;\n\npublic class "+stem+" : MonoBehaviour\n{\n}\n")
        meta=p.with_name(p.name+".meta")
        if include_meta:
            meta.write_bytes(b"fileFormatVersion: 2\nguid: a1b2c3d4e5f607182938404142434445\n")
        return p,meta
    def test_fix_preserves_guid_and_moves_file(self):
        p,meta=self.fixture()
        mdata=meta.read_bytes()
        d=fix_stubs(self.assets,apply=True)
        self.assertEqual(d["fixed_candidates"],1)
        self.assertFalse(p.exists())
        files=list(self.package.glob("RecoveredStub_*.cs"))
        self.assertEqual(len(files),1)
        self.assertIn("public class "+files[0].stem+" : MonoBehaviour",files[0].read_text())
        self.assertEqual(files[0].with_name(files[0].name+".meta").read_bytes(),mdata)
        self.assertEqual(fix_stubs(self.assets,apply=False).get("fixed_candidates",0),0)
    def test_dryrun_doesnt_touch_source(self):
        p,meta=self.fixture(stem="FastMouse.partial")
        original=p.read_bytes()
        self.assertEqual(fix_stubs(self.assets,apply=False)["fixed_candidates"],1)
        self.assertEqual(p.read_bytes(),original)
        self.assertTrue(meta.exists())
    def test_skip_valid_class_identifiers(self):
        p,meta=self.fixture(stem="Raft_Network")
        d=fix_stubs(self.assets,apply=True)
        self.assertEqual(d.get("invalid_filename",0),0)
        self.assertTrue(p.exists())
    def test_report_missing_meta_and_dont_rename(self):
        p,_=self.fixture(include_meta=False)
        d=fix_stubs(self.assets,apply=True)
        self.assertEqual(d["missing_meta"],1)
        self.assertTrue(p.exists())
    def test_do_not_rewrite_wrong_name(self):
        p,meta=self.fixture()
        p.write_text("using UnityEngine;\n\npublic class OtherName : MonoBehaviour {}\n")
        d=fix_stubs(self.assets,apply=True)
        self.assertEqual(d["unmatched_or_ambiguous"],1)
        self.assertTrue(p.exists())
        self.assertTrue(meta.exists())
    def test_do_not_rewrite_non_template(self):
        p,meta=self.fixture()
        p.write_text("using System;\n\npublic class HeapString.gen : MonoBehaviour {}\n")
        d=fix_stubs(self.assets,apply=True)
        self.assertEqual(d["not_minimal_stub"],1)
        self.assertTrue(p.exists())
if __name__=="__main__":
    unittest.main()
