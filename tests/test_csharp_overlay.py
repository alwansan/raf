import tempfile
import unittest
from pathlib import Path

from scripts.overlay_ilspy_gameplay import map_sources

class OverlaySafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        base=Path(self.temp.name)
        self.project=base/"project"
        self.ilspy=base/"decompiled"
        self.ilspy.mkdir()
        (self.project/"Assets").mkdir(parents=True)
    def tearDown(self):
        self.temp.cleanup()
    def fixture(self,asm="Assembly-CSharp",target_ns="RaftWorld",source_ns="RaftWorld",with_meta=True):
        target=self.project/"Assets"/"Scripts"/asm/"Sample.cs"
        target.parent.mkdir(parents=True,exist_ok=True)
        stub=f"namespace {target_ns} {{ public class Sample {{ }} }}"
        src=f"namespace {source_ns} {{ public class Sample {{ public int Speed=42; }} }}"
        target.write_text(stub)
        if with_meta:
            (target.parent/"Sample.cs.meta").write_text("guid: 12345678901234567890123456789012\n")
        (self.ilspy/"Sample.cs").write_text(src)
        return target,stub,src

    def test_safe_overlay_preserves_meta(self):
        target,stub,src=self.fixture()
        meta=target.parent/"Sample.cs.meta"
        original=meta.read_bytes()
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],1)
        self.assertEqual(target.read_text(),src)
        self.assertEqual(meta.read_bytes(),original)

    def test_dry_run_does_not_modify_file(self):
        target,stub,_=self.fixture()
        result=map_sources(self.project,self.ilspy,False)
        self.assertEqual(result["replacements"],1)
        self.assertEqual(target.read_text(),stub)

    def test_reject_namespace_mismatch(self):
        target,stub,_=self.fixture(source_ns="Different")
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(result["namespace_mismatches"],1)
        self.assertEqual(target.read_text(),stub)

    def test_reject_ambiguous_input_filename(self):
        target,stub,_=self.fixture()
        other=self.ilspy/"Namespace2"/"Sample.cs"
        other.parent.mkdir()
        other.write_text("public class Sample {}")
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(result["ambiguous_names"],1)
        self.assertEqual(target.read_text(),stub)

    def test_refuse_other_assemblies(self):
        target,stub,_=self.fixture(asm="PlayFab")
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(target.read_text(),stub)

    def test_requires_matching_meta(self):
        target,stub,_=self.fixture(with_meta=False)
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(target.read_text(),stub)

if __name__=="__main__":
    unittest.main()
