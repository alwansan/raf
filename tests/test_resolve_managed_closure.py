import json
import tempfile
import unittest
from pathlib import Path
from scripts.resolve_managed_closure import plan

class ManagedClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.graph={}
    def tearDown(self): self.tmp.cleanup()
    def assembly(self,name,references):
        (self.root/(name+".dll")).write_bytes(b"MZ"+b"fixture"*200)
        self.graph[name]=references
    def read(self,path): return self.graph[path.stem]
    def test_transitive_timeline_dependency_and_cycles(self):
        self.assembly("FMODUnity",["Unity.Timeline"])
        self.assembly("Unity.Timeline",["FMODUnity","UnityEngine.DirectorModule"])
        result=plan(self.root,["FMODUnity.dll"],reader=self.read)
        self.assertEqual(result["libraries"],["FMODUnity.dll","Unity.Timeline.dll"])
        self.assertIn("UnityEngine.DirectorModule",result["supplied_by_unity_or_reconstructed_game"])
    def test_never_stages_core_or_package_copies(self):
        self.assembly("SDK",["mscorlib","System","UnityEngine.CoreModule","UnityEngine.UI","Assembly-CSharp"])
        self.assertEqual(plan(self.root,["SDK.dll"],reader=self.read)["libraries"],["SDK.dll"])
    def test_missing_dependency_refused(self):
        self.assembly("SDK",["Absent"])
        with self.assertRaises(FileNotFoundError): plan(self.root,["SDK.dll"],reader=self.read)
    def test_editor_dependency_refused(self):
        self.assembly("SDK",["UnityEditor.CoreModule"])
        with self.assertRaises(ValueError): plan(self.root,["SDK.dll"],reader=self.read)
    def test_metadata_selected_provider_and_invalid_identity(self):
        self.assembly("SDK",[])
        manifest=self.root/"providers.json"
        manifest.write_text(json.dumps({"referencedAssemblies":["SDK"]}))
        self.assertEqual(plan(self.root,[],sdk_manifest=manifest,reader=self.read)["libraries"],["SDK.dll"])
        manifest.write_text(json.dumps({"referencedAssemblies":["../escape"]}))
        with self.assertRaises(ValueError): plan(self.root,[],sdk_manifest=manifest,reader=self.read)

if __name__=="__main__": unittest.main()
