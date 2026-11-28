import unittest
from tools.gt_fft_indexed_pair import audit as a
class PairTests(unittest.TestCase):
    def receipt(self):
        return dict(status="PASS",run_id="1-2",config_sha256="a"*64,private_guard=True,vulkan=True,
                    registration_count=20,private_source_hashes_match=True,
                    cases=[dict(first_slot=s,seed=n,dispatches=4,bindings=12,sentinel_checks=4,nonfinite_components=0,
                                indexed_written=[1,2],reference_written=[1,2],coverage_mismatch=[0,0],different_over_tolerance=[0,0])
                           for s in (6,16) for n in (0,19)])
    def test_scoped_accept(self):
        r=a.verify(self.receipt(),{"private_config_sha256":"a"*64},"1-2","success")
        self.assertEqual(r["dispatches"],16);self.assertFalse(r["original_runtime_kernel_mapping_proven"])
        self.assertFalse(r["water_rendering_verified"])
    def test_reject_drift(self):
        for key,value in (("coverage_mismatch",[0,1]),("indexed_written",[0,1]),("nonfinite_components",1),
                          ("different_over_tolerance",[1,0]),("first_slot",7),("bindings",11)):
            r=self.receipt();r["cases"][0][key]=value
            with self.assertRaises(ValueError):a.verify(r,{"private_config_sha256":"a"*64},"1-2","success")
    def test_backend_identity(self):
        for key,value in (("vulkan",False),("private_guard",False),("registration_count",19),("config_sha256","b"*64)):
            r=self.receipt();r[key]=value
            with self.assertRaises(ValueError):a.verify(r,{"private_config_sha256":"a"*64},"1-2","success")
    def test_missing_receipt_retains_native_exit_and_checkpoint(self):
        import json
        from tempfile import TemporaryDirectory
        from pathlib import Path
        with TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/"editor-output-private").write_text("1-2\n")
            (p/"editor-exit-code").write_text("139\n")
            (p/"editor.log").write_text("private")
            row={"run_id":"1-2","phase":"paired_dispatch","operation":"dispatch","first_slot":6,
                 "seed":0,"pass":0,"variant":0,"bindings":3,"dispatches":0}
            (p/"progress.json").write_text(json.dumps(row))
            r=a.bounded_progress(p,"1-2")
            self.assertEqual(r["editor_native_exit"],139)
            self.assertEqual(r["last_managed_checkpoint"]["operation"],"dispatch")
            self.assertFalse(r["private_files_present"]["receipt.json"])
            row["operation"]="untrusted asset value"
            (p/"progress.json").write_text(json.dumps(row))
            self.assertIsNone(a.bounded_progress(p,"1-2")["last_managed_checkpoint"])
            self.assertIsNone(a.bounded_progress(p,"9-2")["editor_native_exit"])
if __name__=="__main__":unittest.main()
