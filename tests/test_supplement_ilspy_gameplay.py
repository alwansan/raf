import tempfile
import unittest
from pathlib import Path

from scripts.supplement_ilspy_gameplay import supplement

class SupplementHelperTypesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.home=Path(self.tmp.name)
        self.project=self.home/"Project"
        self.scripts=self.project/"Assets"/"Scripts"/"Assembly-CSharp"
        self.scripts.mkdir(parents=True)
        self.ilspy=self.home/"src"
        self.ilspy.mkdir()
    def tearDown(self):
        self.tmp.cleanup()
    def test_copies_missing_non_component_helper_type(self):
        source=self.ilspy/"Helper.cs"
        source.write_text("public class Helper { public int count = 42; }\n")
        report=supplement(self.project,self.ilspy,apply=True)
        self.assertEqual(report["statistics"]["added"],1)
        target=self.project/"Assets"/"Scripts"/"Assembly-CSharp-Extras"/"Helper.cs"
        self.assertEqual(target.read_text(),source.read_text())
    def test_keeps_existing_gameplay_source_and_meta(self):
        target=self.scripts/"Item.cs"
        target.write_text("public class Item {}")
        meta=target.with_name("Item.cs.meta")
        meta.write_bytes(b"guid: 0123456789abcdef0123456789abcdef\n")
        (self.ilspy/"Item.cs").write_text("public class Item { public bool Changed = true; }")
        result=supplement(self.project,self.ilspy,apply=True)
        self.assertEqual(result["statistics"].get("added",0),0)
        self.assertEqual(target.read_text(),"public class Item {}")
        self.assertTrue(meta.exists())
    def test_dry_run_does_not_copy(self):
        (self.ilspy/"Missing.cs").write_text("public interface Missing {}\n")
        report=supplement(self.project,self.ilspy,apply=False)
        self.assertEqual(report["statistics"]["added"],1)
        self.assertFalse((self.project/"Assets"/"Scripts"/"Assembly-CSharp-Extras").exists())
    def test_skip_metadata_invalid_filename_and_non_types(self):
        (self.ilspy/"Properties").mkdir()
        (self.ilspy/"Properties"/"AssemblyInfo.cs").write_text("[assembly: System.Reflection.AssemblyVersion(\"1.0\")]")
        (self.ilspy/"x.gen.cs").write_text("public class Weird {}")
        (self.ilspy/"OnlyMethods.cs").write_text("using System;\n")
        report=supplement(self.project,self.ilspy,apply=True)
        self.assertEqual(report["statistics"].get("added",0),0)
    def test_distinct_namespaces_with_same_filename_are_both_recovered(self):
        a=self.ilspy/"A";b=self.ilspy/"B"
        a.mkdir();b.mkdir()
        (a/"Same.cs").write_text("namespace A { public class Same {} }")
        (b/"Same.cs").write_text("namespace B { public class Same {} }")
        report=supplement(self.project,self.ilspy,apply=True)
        self.assertEqual(report["statistics"]["added"],2)
if __name__=="__main__":
    unittest.main()
