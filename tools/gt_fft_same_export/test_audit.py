import unittest
from tools.gt_fft_same_export import audit as a
class Controls(unittest.TestCase):
    def setUp(self):
        self.guid="abcdef0123456789abcdef0123456789"
        self.body=("MonoBehaviour:\n  computeArray:\n  - {fileID: 7200000, guid: "+self.guid+", type: 2}\n").encode()
        self.field=a.digest(b"computeArray")
    def test_exact(self):
        self.assertTrue(a.verify_field(self.body,self.field,(7200000,self.guid,"2")))
    def test_wrong_guid_type_file_id_and_field(self):
        for p in [(7200001,self.guid,"2"),(7200000,"0"*32,"2"),(7200000,self.guid,"3")]:
            with self.assertRaises(ValueError):a.verify_field(self.body,self.field,p)
        with self.assertRaises(ValueError):a.verify_field(self.body,a.digest(b"wrong"),(7200000,self.guid,"2"))
    def test_duplicate_and_extra(self):
        for body in [self.body+b"  computeArray: []\n",self.body+b"  - {fileID: 0}\n"]:
            with self.assertRaises(ValueError):a.verify_field(body,self.field,(7200000,self.guid,"2"))
    def test_helper_composition(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from scripts import b21_stage_light_lineage as l
        from scripts import patch_export_lineage as p
        with TemporaryDirectory() as tmp:
            path=Path(tmp)/"helper.cs"
            base=Path("android-port/Experiments/ExportLineage/RaftExportLineage.cs").read_bytes()
            path.write_bytes(l.render(base))
            a.patch_helper(path)
            text=p.add_compute_lineage(path.read_bytes()).decode()
            self.assertIn("asset.ClassID != 114 || asset.PathID != 23172",text)
            self.assertIn("includeComputeObjects && asset.ClassID == 72",text)
            self.assertEqual(text.count("CaptureFftComponent("),2)
            self.assertEqual(text.count('json.WriteString("export_instance", exportInstance);'),3)
if __name__=="__main__":unittest.main()
