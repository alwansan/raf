import tempfile
import unittest
from pathlib import Path
from scripts.repair_asset_case_collisions import repair

class AssetCaseCollisionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.assets=self.root/"Assets"
        self.assets.mkdir()
    def tearDown(self): self.temp.cleanup()
    def pair(self,folder="Mesh",suffix=".asset"):
        root=self.assets/folder
        root.mkdir()
        items=[]
        for i,name in enumerate(["TrashCan","Trashcan"]):
            p=root/(name+suffix)
            p.write_bytes(("asset "+name).encode())
            p.with_name(p.name+".meta").write_text("fileFormatVersion: 2\nguid: "+str(i+1)*32+"\n")
            items.append(p)
        return items
    def test_preserves_both_payloads_and_exact_meta_bytes(self):
        items=self.pair()
        payloads={p.read_bytes() for p in items}
        metas={p.with_name(p.name+".meta").read_bytes() for p in items}
        report=repair(self.root,apply=True)
        self.assertEqual(report["case_collisions_repaired"],1)
        after=list((self.assets/"Mesh").glob("*.asset"))
        self.assertEqual({p.read_bytes() for p in after},payloads)
        self.assertEqual({p.with_name(p.name+".meta").read_bytes() for p in after},metas)
        self.assertEqual(len({p.name.casefold() for p in after}),2)
        self.assertEqual(repair(self.root,apply=True)["case_collisions_repaired"],0)
    def test_dry_run_leaves_names(self):
        items=self.pair()
        self.assertEqual(repair(self.root,apply=False)["case_collisions_repaired"],1)
        self.assertTrue(all(p.exists() for p in items))
    def test_refuses_code_paths(self):
        self.pair("Scripts",".cs")
        with self.assertRaises(ValueError): repair(self.root,apply=True)
    def test_refuses_resource_paths(self):
        self.pair("Resources",".asset")
        with self.assertRaises(ValueError): repair(self.root,apply=True)

if __name__=="__main__": unittest.main()
