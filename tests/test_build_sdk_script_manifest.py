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
    def test_provider_selection_uses_script_references_not_arbitrary_guids(self):
        self.source("SDK","Widget","a"*32,"public class Widget {}")
        self.source("UnusedSDK","Other","b"*32,"public class Other {}")
        scene=self.root/"Assets/Scenes/Probe.unity"
        scene.parent.mkdir()
        scene.write_text("%YAML 1.1\n  m_Script: {fileID: 11500000, guid: "+"a"*32+", type: 3}\n  m_Mesh: {fileID: 1, guid: "+"b"*32+", type: 3}\n")
        result=build(self.root)
        self.assertEqual(result["referencedAssemblies"],["SDK"])
        self.assertEqual(result["statistics"]["sdk_references"],1)
    def test_bom_does_not_hide_identity(self):
        self.source("SDK","Widget","a"*32,"\ufeffnamespace Sdk {\npublic class Widget {}\n}")
        self.assertEqual(build(self.root)["scripts"][0]["fullTypeName"],"Sdk.Widget")
    def orphan_asset(self,filename="GlobalSerializationConfig.asset",type_name="GlobalSerializationConfig"):
        self.source("Sirenix.Serialization.Config",type_name,"a"*32,"namespace Sirenix.Serialization {\npublic class "+type_name+" {}\n}")
        p=self.root/"Assets/Resources"/filename
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("%YAML 1.1\n  m_Script: {fileID: 11500000, guid: "+"a"*32+", type: 3}\n")
        return p
    def test_known_original_orphan_preserves_identity_and_usage(self):
        asset=self.orphan_asset()
        before=asset.read_bytes()
        result=build(self.root,orphan_check=lambda _:True)
        self.assertEqual(result["referencedAssemblies"],[])
        self.assertEqual(result["statistics"]["sdk_references"],1)
        self.assertEqual(result["preservedOriginalOrphans"][0]["usagePath"],"Resources/GlobalSerializationConfig.asset")
        self.assertEqual(asset.read_bytes(),before)
    def test_orphan_exception_needs_original_absence_evidence(self):
        self.orphan_asset()
        self.assertEqual(build(self.root)["referencedAssemblies"],["Sirenix.Serialization.Config"])
        self.assertEqual(build(self.root,orphan_check=lambda _:False)["preservedOriginalOrphans"],[])
    def test_never_exempts_gameplay_other_types_or_multiple_uses(self):
        for name in ["Scene.unity","Prefab.prefab","Other.asset"]:
            with self.subTest(name=name):
                asset=self.orphan_asset(name)
                self.assertEqual(build(self.root,orphan_check=lambda _:True)["preservedOriginalOrphans"],[])
                asset.unlink()
        asset=self.orphan_asset()
        asset.write_text(asset.read_text()*2)
        self.assertEqual(build(self.root,orphan_check=lambda _:True)["preservedOriginalOrphans"],[])
if __name__=="__main__": unittest.main()
