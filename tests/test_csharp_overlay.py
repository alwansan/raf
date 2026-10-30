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
        other.write_text("namespace RaftWorld { public class Sample {} }")
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(result["ambiguous_names"],1)
        self.assertEqual(target.read_text(),stub)

    def test_other_assembly_same_filename_does_not_block_gameplay(self):
        target,stub,src=self.fixture()
        other=self.project/"Assets"/"Scripts"/"OtherSDK"/"Sample.cs"
        other.parent.mkdir(parents=True)
        other.write_text(stub)
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],1)
        self.assertEqual(target.read_text(),src)
        self.assertEqual(other.read_text(),stub)

    def test_same_filename_different_namespace_is_unambiguous(self):
        target,stub,src=self.fixture()
        other=self.ilspy/"Other"/"Sample.cs"
        other.parent.mkdir()
        other.write_text("namespace Other { public interface Sample {} }")
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],1)
        self.assertEqual(target.read_text(),src)

    def test_recovers_generic_interface_and_preserves_meta(self):
        target,_,_=self.fixture()
        target.write_text("namespace RaftWorld { public class Sample {} }")
        source="namespace RaftWorld { public interface Sample<T> { T Get(); } }"
        (self.ilspy/"Sample.cs").write_text(source)
        meta=target.with_suffix(".cs.meta")
        before=meta.read_bytes()
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],1)
        self.assertEqual(target.read_text(),source)
        self.assertEqual(meta.read_bytes(),before)

    def test_utf8_bom_before_namespace_does_not_hide_interface(self):
        target,_,_=self.fixture()
        source="\ufeffnamespace RaftWorld { public interface Sample<T> { T Get(); } }"
        (self.ilspy/"Sample.cs").write_text(source,encoding="utf8")
        result=map_sources(self.project,self.ilspy,True)
        self.assertEqual(result["replacements"],1)
        self.assertEqual(target.read_text(encoding="utf8"),source)

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
