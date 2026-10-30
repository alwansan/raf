import tempfile
import unittest
from pathlib import Path
from scripts.stage_raft_managed_dlls import ESSENTIALS, OPTIONAL, EDITOR_PROVIDED_ASSEMBLIES, stage

class StageManagedDllTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.base=Path(self.temp.name)
        self.managed=self.base/"Managed"
        self.project=self.base/"Project"
        self.managed.mkdir()
        (self.project/"Assets").mkdir(parents=True)
        for name in ESSENTIALS+OPTIONAL:
            (self.managed/name).write_bytes(b"UnitTestSyntheticDLL"*100)
    def tearDown(self):self.temp.cleanup()
    def test_stage_essentials_no_engine_core(self):
        result=stage(self.managed,self.project,apply=True)
        self.assertEqual(result["staged"],len(ESSENTIALS))
        self.assertNotIn("UnityEngine.CoreModule.dll",ESSENTIALS)
        self.assertIn("com.rlabrecque.steamworks.net.dll",ESSENTIALS)
        self.assertIn("Unity.InputSystem.dll",EDITOR_PROVIDED_ASSEMBLIES)
        self.assertTrue(EDITOR_PROVIDED_ASSEMBLIES.isdisjoint(ESSENTIALS+OPTIONAL))
        self.assertFalse((self.project/"Assets/Plugins/RaftManagedReferences/UnityEngine.UI.dll").exists())
        self.assertFalse((self.project/"Assets/Plugins/RaftManagedReferences/Unity.TextMeshPro.dll").exists())
        for name in ESSENTIALS:
            self.assertEqual((self.project/"Assets/Plugins/RaftManagedReferences"/name).read_bytes(),
                             (self.managed/name).read_bytes())
    def test_dryrun_no_files_created(self):
        result=stage(self.managed,self.project,apply=False)
        self.assertEqual(result["staged"],len(ESSENTIALS))
        self.assertFalse((self.project/"Assets/Plugins").exists())
    def test_reject_missing_dependency(self):
        (self.managed/ESSENTIALS[0]).unlink()
        with self.assertRaises(FileNotFoundError):
            stage(self.managed,self.project,apply=True)
    def test_reject_missing_transitive_sdk_dependency(self):
        (self.managed/"Unity.Burst.Unsafe.dll").unlink()
        with self.assertRaises(FileNotFoundError):
            stage(self.managed,self.project,apply=False)

    def test_stage_plan_and_reject_core(self):
        (self.managed/"Unity.Timeline.dll").write_bytes(b"MetadataTestFixture"*100)
        names=list(ESSENTIALS)+["Unity.Timeline.dll"]
        report=stage(self.managed,self.project,apply=True,dependency_plan={"libraries":names})
        self.assertEqual(report["staged"],len(names))
        with self.assertRaises(ValueError):
            stage(self.managed,self.project,apply=False,dependency_plan={"libraries":["UnityEngine.CoreModule.dll"]})
    def test_missing_plan_dependency_has_no_partial_write(self):
        with self.assertRaises(FileNotFoundError):
            stage(self.managed,self.project,apply=True,dependency_plan={"libraries":[ESSENTIALS[0],"Absent.dll"]})
        self.assertFalse((self.project/"Assets/Plugins/RaftManagedReferences").exists())
    def test_reject_overwrite(self):
        stage(self.managed,self.project,apply=True)
        with self.assertRaises(FileExistsError):
            stage(self.managed,self.project,apply=True)
    def test_extended_is_explicit(self):
        report=stage(self.managed,self.project,apply=True,extended=True)
        self.assertEqual(report["staged"],len(ESSENTIALS)+len(OPTIONAL))
if __name__=="__main__": unittest.main()
