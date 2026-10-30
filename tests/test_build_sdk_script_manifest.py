import tempfile
import unittest
from pathlib import Path
from scripts.build_sdk_script_manifest import build
class SdkManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def source(self,assembly,name,guid,content):
        p=self.root/"Assets/Scripts"/assembly/(name+".cs")
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(content,encoding="utf8")
        p.with_name(p.name+".meta").write_text("guid: "+guid+"\n")
    def test_sdk_metadata_excludes_gameplay_and_source_body(self):
        self.source("SDK","Widget","a"*32,"namespace Sdk.Space {\npublic class Widget { void HiddenBody() {} }\n}")
        self.source("Assembly-CSharp","Player","b"*32,"public class Player {}")
        result=build(self.root)
        self.assertEqual(len(result["scripts"]),1)
        self.assertEqual(result["scripts"][0]["fullTypeName"],"Sdk.Space.Widget")
        self.assertNotIn("HiddenBody",str(result))
    def test_unknown_declaration_identity_remains_for_unresolved_gate(self):
        self.source("SDK","Unknown","a"*32,"// not a recognized declaration")
        row=build(self.root)["scripts"][0]
        self.assertEqual(row["sourceGuid"],"a"*32)
        self.assertEqual(row["fullTypeName"],"")
    def test_refuses_duplicate_guids(self):
        self.source("SDK","One","a"*32,"public class One {}")
        self.source("SDK","Two","a"*32,"public class Two {}")
        with self.assertRaises(ValueError): build(self.root)
    def test_bom_does_not_hide_identity(self):
        self.source("SDK","Widget","a"*32,"\ufeffnamespace Sdk {\npublic class Widget {}\n}")
        self.assertEqual(build(self.root)["scripts"][0]["fullTypeName"],"Sdk.Widget")
if __name__=="__main__": unittest.main()
