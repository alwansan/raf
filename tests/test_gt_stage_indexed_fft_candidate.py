"""Source-free exact class72 installer, reference and backup regression."""
import tempfile
import unittest
from pathlib import Path
from scripts import gt_stage_indexed_fft_candidate as a

GUID="abcdef0123456789abcdef0123456789"
OTHER="1234567890abcdef1234567890abcdef"

class Installer(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.project=self.root/"Project";self.assets=self.project/"Assets"
        self.assets.mkdir(parents=True)
        self.backup=self.root/"Backup";self.backup.mkdir()
        self.old=self.assets/"Original.asset"
        self.old.write_text("%YAML 1.1\n--- !u!72 &7200000\nComputeShader:\n  m_Name: Fixture\n")
        self.old_meta=self.old.with_suffix(".asset.meta")
        self.old_meta.write_text("fileFormatVersion: 2\nguid: "+GUID+"\nNativeFormatImporter:\n  mainObjectFileID: 7200000\n")
        self.scene=self.assets/"Scene.unity"
        self.scene.write_text("%YAML 1.1\n--- !u!114 &1\nMonoBehaviour:\n  field:\n  - {fileID: 7200000, guid: "+GUID+", type: 2}\n  - {fileID: 7200000, guid: "+OTHER+", type: 2}\n  - {fileID: 7200001, guid: "+GUID+", type: 2}\n")
        self.unrelated=self.assets/"Other.asset";self.unrelated.write_bytes(b"unrelated")
        self.shader=self.root/"Candidate.compute"
        self.shader.write_text("#pragma use_dxc\n#pragma only_renderers vulkan\n"+"".join(f"#pragma kernel {a.entry(i)} RAFT_FFT_SLOT={i}\n" for i in range(20)))
        self.trace={"schema_version":1,"export_instance":"a"*32,"objects":[{"class_id":72,"source":{"owner":a.OWNER,"path_id":a.PATH_ID},"exportable":True,"export":{"file_id":7200000,"guid":GUID,"type":2}}]}
    def snapshot(self):
        return {str(p.relative_to(self.project)):p.read_bytes() for p in self.project.rglob("*") if p.is_file()}
    def test_install_keeps_only_exact_reference_change(self):
        before=self.snapshot()
        report=a.install_fft(self.project,self.trace,self.shader,self.backup)
        self.assertEqual(report["serialized_fft_references_converted_to_importer_type"],1)
        self.assertEqual(report["ordered_routes_installed"],20)
        self.assertFalse(self.old.exists());self.assertFalse(self.old_meta.exists())
        self.assertEqual(self.old.with_suffix(".compute").read_bytes(),self.shader.read_bytes())
        self.assertIn(("guid: "+GUID+"\nComputeShaderImporter:").encode(),self.old.with_suffix(".compute.meta").read_bytes())
        expected=before["Assets/Scene.unity"].replace(("guid: "+GUID+", type: 2}").encode(),("guid: "+GUID+", type: 3}").encode(),1)
        self.assertEqual(self.scene.read_bytes(),expected)
        for key in ("Assets/Original.asset","Assets/Original.asset.meta","Assets/Scene.unity"):
            self.assertEqual((self.backup/key).read_bytes(),before[key])
        self.assertEqual(self.unrelated.read_bytes(),before["Assets/Other.asset"])
    def test_wrong_trace_pointer_rejected_without_mutation(self):
        before=self.snapshot()
        self.trace["objects"][0]["export"]["file_id"]=7200001
        with self.assertRaises(ValueError):a.install_fft(self.project,self.trace,self.shader,self.backup)
        self.assertEqual(self.snapshot(),before)
    def test_wrong_kernel_order_rejected_without_mutation(self):
        before=self.snapshot()
        self.shader.write_text(self.shader.read_text().replace("RAFT_FFT_SLOT=19","RAFT_FFT_SLOT=18"))
        with self.assertRaises(ValueError):a.install_fft(self.project,self.trace,self.shader,self.backup)
        self.assertEqual(self.snapshot(),before)
    def test_occupied_destination_rejected_without_mutation(self):
        self.old.with_suffix(".compute").write_text("occupied")
        before=self.snapshot()
        with self.assertRaises(ValueError):a.install_fft(self.project,self.trace,self.shader,self.backup)
        self.assertEqual(self.snapshot(),before)
if __name__=="__main__":unittest.main()
