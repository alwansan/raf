"""GT no-network controls for genuine shader restorers' guarded isolated execution."""
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from scripts.gt_compare_shader_restore_quality import STATUS
from scripts.gt_test_vendor_shader_restoration import run, SCHEMA, RESTORERS


def sample(dummy=2,non_dummy=0,builtin=1,unknown=0):
    return {"status":STATUS,"counts":{
        "material_documents":3,
        "material_docs_using_dummy_Shader":dummy,
        "material_docs_using_non_dummy_Shader":non_dummy,
        "material_docs_using_Unity_builtin_Shader":builtin,
        "material_docs_with_unknown_or_broken_Shader":unknown,
        "shader_files":3,
        "shader_files_with_dummy_exporter_marker":3,
        "shader_files_with_complete_program_pass":3,
    }}


class ActualVendorRestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.project=self.root/"ExportedProject"
        self.assets=self.project/"Assets"
        self.assets.mkdir(parents=True)
        self.meta=self.assets/"test.shader.meta"
        self.meta.write_text("guid: "+"b"*32+"\n")
        self.backup=self.root/"backup"
        self.calls=[]

    def executor(self, command, **kwargs):
        self.calls.append(tuple(command))
        self.assertIn("--project",command)
        self.assertIn("--backup",command)
        return SimpleNamespace(returncode=0)

    def test_four_real_vendor_restorer_commands_and_existing_meta_preserved(self):
        d=run(self.project,sample(),self.backup,runner=self.executor,
              quality=lambda project:sample(dummy=1,non_dummy=1))
        self.assertEqual(d["status"],"POST_RESTORE_SOURCE_QUALITY_COMPARED")
        self.assertEqual(d["schema"],SCHEMA)
        self.assertEqual(len(self.calls),len(RESTORERS))
        self.assertEqual(d["completed_original_vendor_restorer_steps"],
                         [name for name,_ in RESTORERS])
        self.assertEqual(d["postrestore_material_quality"]["dummy_material_documents_decreased_by"],1)
        self.assertTrue(d["original_exported_meta_bytes_unchanged"])
        self.assertFalse(d["android_shader_compilation_or_gpu_pixels_verified"])
        self.assertEqual(self.meta.read_text(),"guid: "+"b"*32+"\n")
        self.assertNotIn("b"*32,json.dumps(d))

    def test_vendor_failure_does_not_advance_following_restorers(self):
        d=run(self.project,sample(),self.backup,
              runner=lambda cmd,**kwargs:SimpleNamespace(returncode=2),
              quality=lambda project:sample())
        self.assertEqual(d["status"],"REJECTED")
        self.assertEqual(d["failure_stage"],"tmp")
        self.assertEqual(d["failure_category"],"VENDOR_RESTORER_REJECTED")
        self.assertEqual(d["completed_original_vendor_restorer_steps"],[])

    def test_malicious_vendor_metadata_change_fails(self):
        def attack(command, **kwargs):
            self.meta.write_text("guid: "+"e"*32+"\n")
            return SimpleNamespace(returncode=0)
        d=run(self.project,sample(),self.backup,runner=attack,
              quality=lambda project:sample())
        self.assertEqual(d["status"],"REJECTED")
        self.assertFalse(d["original_exported_meta_bytes_unchanged"])
        self.assertEqual(d["failure_category"],"ORIGINAL_EXPORTED_META_MUTATED")

    def test_backup_root_inside_original_export_rejected(self):
        with self.assertRaisesRegex(ValueError,"backup_directory_overlaps"):
            run(self.project,sample(),self.project/"backup",runner=self.executor,
                quality=lambda project:sample())

    def test_original_asset_meta_symlink_rejected(self):
        (self.assets/"linked.meta").symlink_to(self.meta)
        with self.assertRaisesRegex(ValueError,"unsafe_original_exported_meta"):
            run(self.project,sample(),self.backup,runner=self.executor,
                quality=lambda project:sample())


if __name__=="__main__":
    unittest.main()
