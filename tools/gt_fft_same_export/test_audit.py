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
    def test_workflow_trace_environment(self):
        import re
        from pathlib import Path
        import yaml
        workflow=yaml.safe_load(Path(".github/workflows/raft-gt-fft-same-export.yml").read_text())
        steps=next(iter(workflow["jobs"].values()))["steps"]
        step=next(x for x in steps if x.get("name","").startswith("Run one bounded genuine"))
        used=set(re.findall(r"\$(RAFT_PRIVATE_EXPORT_[A-Z_]+)",step["run"]))
        self.assertEqual(used,{"RAFT_PRIVATE_EXPORT_LINEAGE","RAFT_PRIVATE_EXPORT_FFT_COMPONENT_LINEAGE","RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE"})
        self.assertLessEqual(used,set(step["env"]))
    def test_export_status_keeps_actual_trace_boundary(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        import json
        with TemporaryDirectory() as tmp:
            root=Path(tmp);project=root/"project";(project/"Assets").mkdir(parents=True)
            paths=[root/k for k in ("w1","component","texture")]
            for p in paths:p.write_text(json.dumps({"schema_version":1,"export_instance":"a"*32,"objects":[]}))
            log=root/"log";log.write_text("fixture")
            s=a.export_status(0,project,*paths,log)
            self.assertTrue(s["actual_export_completed"])
            self.assertEqual(s["source_compute_trace_rows"],0)
            paths[1].unlink()
            s=a.export_status(0,project,*paths,log)
            self.assertTrue(s["exporter_returned_zero"])
            self.assertFalse(s["actual_export_completed"])
if __name__=="__main__":unittest.main()
