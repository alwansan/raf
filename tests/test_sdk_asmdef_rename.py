import json
import tempfile
import unittest
from pathlib import Path

from scripts.rename_conflicting_sdk_asmdefs import reconcile

class ManagedAssemblyRenameTests(unittest.TestCase):
    def test_renames_only_conflicts_and_preserves_meta(self):
        with tempfile.TemporaryDirectory() as d:
            project=Path(d)
            plugins=project/"Assets/Plugins/RaftManagedReferences"
            plugins.mkdir(parents=True)
            (plugins/"PlayFab.dll").write_bytes(b"placeholder managed DLL for matching only")
            scripts=project/"Assets/Scripts/PlayFab"
            scripts.mkdir(parents=True)
            asm=scripts/"PlayFab.asmdef"
            asm.write_text(json.dumps({"name":"PlayFab","autoReferenced":True,"references":[]}))
            meta=scripts/"PlayFab.asmdef.meta"
            raw=b"fileFormatVersion: 2\nguid: abcdef0123456789abcdef0123456789\n"
            meta.write_bytes(raw)
            report=reconcile(project,apply=True)
            self.assertEqual(report["renamed"],1)
            updated=json.loads(asm.read_text())
            self.assertTrue(updated["name"].startswith("RaftStub."))
            self.assertFalse(updated["autoReferenced"])
            self.assertEqual(meta.read_bytes(),raw)
            self.assertEqual(reconcile(project,apply=False)["renamed"],0)
    def test_nonconflicting_asmdef_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            project=Path(d)
            (project/"Assets/Plugins/RaftManagedReferences").mkdir(parents=True)
            root=project/"Assets/Scripts/MyGame"
            root.mkdir(parents=True)
            file=root/"MyGame.asmdef"
            original='{"name":"Assembly-CSharp.Custom","references":[]}'
            file.write_text(original)
            report=reconcile(project,apply=True)
            self.assertEqual(report["renamed"],0)
            self.assertEqual(file.read_text(),original)
if __name__=="__main__":
    unittest.main()
