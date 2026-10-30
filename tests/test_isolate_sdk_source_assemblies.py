import json
import tempfile
import unittest
from pathlib import Path
from scripts.isolate_sdk_source_assemblies import isolate
class SdkSourceIsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.manifest=self.root/"sdk.json"
        self.manifest.write_text(json.dumps({"scripts":[{"assemblyName":"SDK"}]}))
        self.sdk=self.root/"Assets/Scripts/SDK/SDK.asmdef"
        self.sdk.parent.mkdir(parents=True)
        self.sdk.write_text('{"name":"RaftStub.SDK","includePlatforms":["Android"],"references":[]}')
        self.meta=self.sdk.with_name(self.sdk.name+".meta")
        self.meta.write_bytes(b"guid: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.main=self.root/"Assets/Scripts/Assembly-CSharp/Game.asmdef"
        self.main.parent.mkdir()
        self.main.write_text('{"name":"Game","includePlatforms":["Android"]}')
    def tearDown(self): self.tmp.cleanup()
    def test_sdk_only_and_meta_unchanged(self):
        before=self.meta.read_bytes()
        game=self.main.read_bytes()
        isolate(self.root,self.manifest,apply=True)
        data=json.loads(self.sdk.read_text())
        self.assertEqual(data["includePlatforms"],["Editor"])
        self.assertFalse(data["autoReferenced"])
        self.assertEqual(data["name"],"RaftStub.SDK")
        self.assertEqual(self.meta.read_bytes(),before)
        self.assertEqual(self.main.read_bytes(),game)
    def test_dry_run(self):
        before=self.sdk.read_bytes()
        isolate(self.root,self.manifest,apply=False)
        self.assertEqual(self.sdk.read_bytes(),before)
    def test_refuses_gameplay(self):
        self.manifest.write_text(json.dumps({"scripts":[{"assemblyName":"Assembly-CSharp"}]}))
        with self.assertRaises(ValueError): isolate(self.root,self.manifest,apply=True)
if __name__=="__main__": unittest.main()
