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
    def test_complete_sdk_sources_are_retained_without_compilation(self):
        before=self.meta.read_bytes()
        isolate(self.root,self.manifest,apply=True,disable_compilation=True)
        data=json.loads(self.sdk.read_text())
        self.assertEqual(data['includePlatforms'],['Editor'])
        self.assertIn('!UNITY_EDITOR',data['defineConstraints'])
        self.assertEqual(self.meta.read_bytes(),before)
    def test_helper_only_sdk_is_also_excluded_in_decompiled_mode(self):
        extra=self.root/'Assets/Scripts/HelperOnly/HelperOnly.asmdef'
        extra.parent.mkdir()
        extra.write_text('{"name":"HelperOnly"}')
        isolate(self.root,self.manifest,apply=True,disable_compilation=True)
        self.assertIn('!UNITY_EDITOR',json.loads(extra.read_text())['defineConstraints'])
    def test_refuses_gameplay(self):
        self.manifest.write_text(json.dumps({"scripts":[{"assemblyName":"Assembly-CSharp"}]}))
        with self.assertRaises(ValueError): isolate(self.root,self.manifest,apply=True)
    def test_new_asmdef_without_original_meta_is_allowed_without_creating_guid(self):
        self.meta.unlink()
        result=isolate(self.root,self.manifest,apply=True)
        self.assertEqual(result["asmdefs_without_original_meta"],1)
        self.assertEqual(json.loads(self.sdk.read_text())["includePlatforms"],["Editor"])
        self.assertFalse(self.meta.exists())
    def test_later_invalid_asmdef_causes_no_partial_writes(self):
        before=self.sdk.read_bytes()
        bad=self.sdk.parent/"ZInvalid.asmdef"
        bad.write_text("not json")
        with self.assertRaises(json.JSONDecodeError): isolate(self.root,self.manifest,apply=True)
        self.assertEqual(self.sdk.read_bytes(),before)
if __name__=="__main__": unittest.main()

