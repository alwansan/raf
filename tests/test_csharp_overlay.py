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

    def test_opt_in_recovers_lost_namespace_from_field_only_template(self):
        target,_,source=self.fixture()
        target.write_text("using UnityEngine;\npublic class Sample : MonoBehaviour { public int value; }")
        original_meta=target.with_suffix(".cs.meta").read_bytes()
        self.assertEqual(map_sources(self.project,self.ilspy,False)["replacements"],0)
        result=map_sources(self.project,self.ilspy,True,recover_unqualified_stubs=True)
        self.assertEqual(result["unqualified_stubs_recovered"],1)
        self.assertEqual(target.read_text(),source)
        self.assertEqual(target.with_suffix(".cs.meta").read_bytes(),original_meta)

    def test_lost_namespace_recovery_refuses_implemented_component(self):
        target,_,_=self.fixture()
        stub="public class Sample : MonoBehaviour { public void Awake() { } }"
        target.write_text(stub)
        result=map_sources(self.project,self.ilspy,True,recover_unqualified_stubs=True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(target.read_text(),stub)

    def test_lost_namespace_uses_only_unmatched_original_identity(self):
        target,_,_=self.fixture()
        target.write_text("public class Sample : MonoBehaviour { }")
        wrapper=target.parent/"Wrapper"/"Sample.cs"
        wrapper.parent.mkdir()
        wrapper.write_text("namespace Wrapper { public class Sample : MonoBehaviour {} }")
        wrapper.with_suffix(".cs.meta").write_text("guid: abcdef0123456789abcdef0123456789")
        (self.ilspy/"Sample.cs").unlink()
        for ns,kind in [("Wrapper","class"),("Interop","struct")]:
            directory=self.ilspy/ns
            directory.mkdir()
            (directory/"Sample.cs").write_text(f"namespace {ns} {{ public {kind} Sample {{ }} }}")
        result=map_sources(self.project,self.ilspy,True,recover_unqualified_stubs=True)
        self.assertEqual(result["replacements"],2)
        self.assertEqual(result["unqualified_stubs_recovered"],1)
        self.assertIn("namespace Interop",target.read_text())

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


    def test_opt_in_restores_full_decompiled_body_without_meta(self):
        target,old,new=self.fixture(with_meta=False)
        protected=target.parent/"Protected.cs.meta"
        original=b"fileFormatVersion: 2\\nguid: 0123456789abcdef0123456789abcdef\\n"
        protected.write_bytes(original)
        result=map_sources(self.project,self.ilspy,True,recover_unlinked_decompiled=True)
        self.assertEqual(result["replacements"],1)
        self.assertEqual(result["recovered_unlinked_decompiled"],1)
        self.assertEqual(target.read_text(),new)
        self.assertFalse(target.with_suffix(".cs.meta").exists())
        self.assertEqual(protected.read_bytes(),original)
        self.assertTrue(result["meta_hashes_unchanged"])

    def test_opt_in_refuses_ambiguous_unlinked_source(self):
        target,old,new=self.fixture(with_meta=False)
        second=target.parent/"Elsewhere"/"Sample.cs"
        second.parent.mkdir()
        second.write_text(old)
        result=map_sources(self.project,self.ilspy,True,recover_unlinked_decompiled=True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(result["ambiguous_names"],2)
        self.assertEqual(target.read_text(),old)

    def test_opt_in_does_not_replace_unrelated_sdk_file(self):
        target,old,new=self.fixture(asm="PlayFab",with_meta=False)
        result=map_sources(self.project,self.ilspy,True,recover_unlinked_decompiled=True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(target.read_text(),old)

    def test_opt_in_does_not_replace_mismatched_namespace(self):
        target,old,new=self.fixture(with_meta=False,source_ns="Different")
        result=map_sources(self.project,self.ilspy,True,recover_unlinked_decompiled=True)
        self.assertEqual(result["replacements"],0)
        self.assertEqual(target.read_text(),old)

    def test_opt_in_restores_decompiled_delegate_without_meta(self):
        target=self.project/"Assets"/"Scripts"/"Assembly-CSharp"/"Handler.cs"
        target.parent.mkdir(parents=True)
        target.write_text("namespace Raft { public delegate void Handler(); }")
        restored="namespace Raft { public delegate bool Handler(int value); }"
        (self.ilspy/"Handler.cs").write_text(restored)
        result=map_sources(self.project,self.ilspy,True,recover_unlinked_decompiled=True)
        self.assertEqual(result["recovered_unlinked_decompiled"],1)
        self.assertEqual(target.read_text(),restored)


if __name__=="__main__":
    unittest.main()
