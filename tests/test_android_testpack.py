"""Tests for safe Raft Android declarative mini lab packs."""
import json
from pathlib import Path
import unittest
from scripts.validate_android_testpack import validate,PackError
BASE=json.loads((Path(__file__).resolve().parents[1]/"apk-for-testing/examples/t4-mouse-testpack.json").read_text())
class Tests(unittest.TestCase):
    def setUp(self): self.p=json.loads(json.dumps(BASE))
    def test_example(self): self.assertEqual(validate(self.p)["cases"],9)
    def test_no_executable(self):
        self.p["tests"][0]["type"]="execute_dex"
        with self.assertRaises(PackError): validate(self.p)
    def test_traversal(self):
        for path in ("../foo","/tmp/f","a/../b","a\\b","file://a","a//b"):
            self.p=json.loads(json.dumps(BASE));self.p["tests"][0]["asset"]=path
            with self.subTest(path=path),self.assertRaises(PackError):validate(self.p)
    def test_duplicate(self):
        self.p["tests"][1]["id"]=self.p["tests"][0]["id"]
        with self.assertRaises(PackError):validate(self.p)
    def test_bad_sha(self):
        self.p["source_sha"]="unknown"
        with self.assertRaises(PackError):validate(self.p)
    def test_unknown_root(self):
        self.p["cmd"]="run.sh"
        with self.assertRaises(PackError):validate(self.p)
    def test_overflow(self):
        self.p["tests"]*=3
        with self.assertRaises(PackError):validate(self.p)
if __name__=="__main__": unittest.main()
