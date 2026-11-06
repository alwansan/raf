"""Synthetic-only 5 true-source ParticleShader Material RGBA + scalar parity."""
import copy
from pathlib import Path
import tempfile
import unittest
from scripts.t3_particle108_sameexport_values import assess,MATCH,MISMATCH,PrivatePhaseError,PrivateDocumentError,exported_selected_values
from scripts.b22_verify_material_scalars import _float_bits

def fixture():
    c,s,actual_c,actual_s={}, {}, {}, {}
    w1={"schema_version":1,"export_instance":"a"*32,"objects":[]}
    for i in range(1,6):
        key=("resources.assets",i)
        guid=f"{i:032x}"
        pointer=(2100000,guid)
        row={"class_id":21,"source":{"owner":"resources.assets","path_id":i},
             "export":{"file_id":2100000,"guid":guid,"type":3},
             "exportable":True,"collection_type":"SyntheticTestMaterial"}
        w1["objects"].append(row)
        c[key]={"_SyntheticTint":(0.5,1.0,0.25,1.0)}
        s[key]={"m_Floats":{"_SyntheticAlpha":_float_bits(0.4)},
                "m_Ints":{"_SyntheticMode":1}}
        actual_c[pointer]=copy.deepcopy(c[key])
        actual_s[pointer]=copy.deepcopy(s[key])
    return c,s,w1,actual_c,actual_s

class SelectedParticle108ValueParityTests(unittest.TestCase):
    def test_exact_five_material_rgba_float_int_parity(self):
        c,s,w,ac,as_=fixture()
        report=assess(c,s,w,ac,as_)
        self.assertEqual(report["status"],MATCH)
        self.assertEqual(report["selected_SHA_original_Particle108_source_Material21_objects"],5)
        self.assertEqual(report["RGBA_slots_compared"],5)
        self.assertEqual(report["float32_slots_compared"],5)
        self.assertEqual(report["int32_slots_compared"],5)
        self.assertTrue(report["all_selected_RGBA_scalar_values_preserved"])
        self.assertFalse(report["actual_Unity_import_GPU_color_or_phone_emitter_verified"])
        self.assertNotIn("_SyntheticTint",str(report))
    def test_true_rgba_value_change_not_hidden(self):
        c,s,w,ac,as_=fixture()
        ac[(2100000,f"{1:032x}")]["_SyntheticTint"]=(1.0,1.0,1.0,1.0)
        r=assess(c,s,w,ac,as_)
        self.assertEqual(r["status"],MISMATCH)
        self.assertEqual(r["changed_RGBA_values"],1)
        self.assertEqual(r["RGBA_mismatched_Materials"],1)
    def test_source_float32_bit_change_is_not_tolerance(self):
        c,s,w,ac,as_=fixture()
        as_[(2100000,f"{1:032x}")]["m_Floats"]["_SyntheticAlpha"]=_float_bits(0.8)
        r=assess(c,s,w,ac,as_)
        self.assertEqual(r["status"],MISMATCH)
        self.assertEqual(r["changed_float32_values"],1)
        self.assertEqual(r["scalar_mismatched_Materials"],1)
    def test_int32_modified_is_measured(self):
        c,s,w,ac,as_=fixture()
        as_[(2100000,f"{1:032x}")]["m_Ints"]["_SyntheticMode"]=2
        r=assess(c,s,w,ac,as_)
        self.assertEqual(r["changed_int32_values"],1)
        self.assertEqual(r["status"],MISMATCH)
    def test_unexpected_or_missing_rgba_slot_measured(self):
        c,s,w,ac,as_=fixture()
        del ac[(2100000,f"{1:032x}")]["_SyntheticTint"]
        ac[(2100000,f"{2:032x}")]["_AdditionalTint"]=(1,1,1,1)
        r=assess(c,s,w,ac,as_)
        self.assertEqual(r["missing_RGBA_slots"],1)
        self.assertEqual(r["extra_RGBA_slots"],1)
        self.assertEqual(r["status"],MISMATCH)
    def test_missing_actual_exported_material_rejected(self):
        c,s,w,ac,as_=fixture()
        ac.pop((2100000,f"{1:032x}"))
        with self.assertRaisesRegex(ValueError,"missing_original_particle108_exported_Material_YAML"):
            assess(c,s,w,ac,as_)
    def test_duplicate_selected_trace_source_rejected(self):
        c,s,w,ac,as_=fixture()
        w["objects"].append(copy.deepcopy(w["objects"][0]))
        with self.assertRaisesRegex(ValueError,"duplicate_SHA_original"):
            assess(c,s,w,ac,as_)
    def test_missing_selected_trace_source_rejected(self):
        c,s,w,ac,as_=fixture()
        w["objects"].pop()
        with self.assertRaisesRegex(ValueError,"missing_original_particle108_source_to_sameexport"):
            assess(c,s,w,ac,as_)
    def test_colliding_exported_material_pointer_rejected(self):
        c,s,w,ac,as_=fixture()
        w["objects"][1]["export"]=copy.deepcopy(w["objects"][0]["export"])
        with self.assertRaisesRegex(ValueError,"colliding_original_particle108_exported_material_pointer"):
            assess(c,s,w,ac,as_)
    def test_wrong_selected_population_rejected(self):
        c,s,w,ac,as_=fixture()
        c.pop(("resources.assets",1))
        with self.assertRaisesRegex(ValueError,"incomplete_source_5_Material21_value_scope"):
            assess(c,s,w,ac,as_)
    def test_fake_engine_export_not_accepted_as_material_document(self):
        c,s,w,ac,as_=fixture()
        w["objects"][0]["export"]={"file_id":2100000,"guid":"0"*32,"type":0}
        with self.assertRaises(ValueError):
            assess(c,s,w,ac,as_)
    def test_private_rgba_value_parser_failure_only_exposes_phase(self):
        c,s,w,ac,as_=fixture()
        c[("resources.assets",1)]["_SyntheticTint"]=("PRIVATE_NONNUMERIC",1,1,1)
        with self.assertRaises(PrivatePhaseError) as cm:
            assess(c,s,w,ac,as_)
        self.assertEqual(cm.exception.phase,"COMPARE_RGBA")
        self.assertNotIn("PRIVATE_NONNUMERIC",str(cm.exception))
    def test_private_original_names_and_values_do_not_leave_aggregate(self):
        c,s,w,ac,as_=fixture()
        r=assess(c,s,w,ac,as_)
        output=str(r)
        for needle in ("resources.assets","_SyntheticTint","_SyntheticAlpha",
                       "00000000000000000000000000000001"):
            self.assertNotIn(needle,output)

class OriginalSelectedOnlyYAMLTests(unittest.TestCase):
    def setup_project(self,root):
        project=Path(root)/"ExportedProject"
        assets=project/"Assets"
        assets.mkdir(parents=True)
        wanted=set()
        for i in range(1,6):
            guid=f"{i:032x}"
            wanted.add((2100000,guid))
            f=assets/f"synthetic{i}.mat"
            f.write_text("""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!21 &2100000
Material:
  m_SavedProperties:
    m_Colors:
      - _Tint: {r: 0.5, g: 1, b: 0.25, a: 1}
    m_Floats:
      - _Alpha: 0.4
    m_Ints:
      - _Mode: 1
""")
            (assets/f"synthetic{i}.mat.meta").write_text("guid: "+guid+"\n")
        return project,wanted
    def test_only_five_selected_original_material_yaml_documents_parsed(self):
        with tempfile.TemporaryDirectory() as d:
            project,wanted=self.setup_project(d)
            c,s=exported_selected_values(project,wanted)
            self.assertEqual(set(c),wanted)
            self.assertEqual(set(s),wanted)
            self.assertEqual(len(c),5)
            self.assertEqual(sum(len(x["m_Floats"]) for x in s.values()),5)
    def test_unrelated_material_invalid_yaml_not_counted_as_selected_drift(self):
        with tempfile.TemporaryDirectory() as d:
            project,wanted=self.setup_project(d)
            (project/"Assets"/"unrelated.mat").write_text("%YAML 1.1\n--- !u!21 &2100000\nMaterial: [this is broken\n")
            (project/"Assets"/"unrelated.mat.meta").write_text("guid: "+("f"*32)+"\n")
            c,s=exported_selected_values(project,wanted)
            self.assertEqual(set(c),wanted)
    def test_selected_material_broken_yaml_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            project,wanted=self.setup_project(d)
            (project/"Assets"/"synthetic1.mat").write_text("%YAML 1.1\n--- !u!21 &2100000\nMaterial: [this is broken\n")
            with self.assertRaises(ValueError):
                exported_selected_values(project,wanted)
    def test_missing_selected_original_document_never_succeeds(self):
        with tempfile.TemporaryDirectory() as d:
            project,wanted=self.setup_project(d)
            (project/"Assets"/"synthetic1.mat").unlink()
            with self.assertRaisesRegex(PrivateDocumentError,"SELECTED_DOCUMENTS_MISSING"):
                exported_selected_values(project,wanted)
    def test_selected_duplicate_material_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            project,wanted=self.setup_project(d)
            f=project/"Assets"/"synthetic1.mat"
            f.write_text(f.read_text().replace("    m_Colors:", "    m_Colors: []\n    m_Colors:"))
            with self.assertRaises(ValueError):
                exported_selected_values(project,wanted)
    def test_selected_real_material_yaml_color_and_scalar_failure_reason_sanitized(self):
        with tempfile.TemporaryDirectory() as d:
            project,wanted=self.setup_project(d)
            path=project/"Assets"/"synthetic1.mat"
            path.write_text(path.read_text().replace("    m_Colors:", "    m_Colors: [" ).replace("      - _Tint:", "      - _Tint:"))
            with self.assertRaises(PrivateDocumentError) as ctx:
                exported_selected_values(project,wanted)
            self.assertEqual(ctx.exception.code,"SELECTED_DOCUMENT_PARSE")
            self.assertNotIn("synthetic1",str(ctx.exception))
        with tempfile.TemporaryDirectory() as d:
            project,wanted=self.setup_project(d)
            path=project/"Assets"/"synthetic1.mat"
            path.write_text(path.read_text().replace("    m_Floats:", "    m_Floats: 123\n    ignore:"))
            with self.assertRaises(PrivateDocumentError) as ctx:
                exported_selected_values(project,wanted)
            self.assertEqual(ctx.exception.code,"SELECTED_SCALAR_SCHEMA")
    def test_safe_failure_code_only_allows_static_categories(self):
        with self.assertRaises(ValueError):
            PrivateDocumentError("MY_PRIVATE_MATERIAL_EXTRACT")
        e=PrivateDocumentError("SELECTED_RGBA_SCHEMA")
        self.assertNotIn("_PRIVATE",str(e))
    def test_selected_export_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            project,wanted=self.setup_project(d)
            (project/"Assets"/"linked.mat").symlink_to(project/"Assets"/"synthetic1.mat")
            with self.assertRaisesRegex(PrivateDocumentError,"EXPORT_ASSETS_UNSAFE"):
                exported_selected_values(project,wanted)

if __name__=="__main__":
    unittest.main()
