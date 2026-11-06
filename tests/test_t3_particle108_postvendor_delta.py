"""Source-free controls for genuine Particle108 Shader48 vendor-restorer delta."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.t3_particle108_postvendor_delta import compare, DUMMY, STATUS, main

def sample(status=DUMMY):
    return {
        "schema_version":1,
        "status":"T3_ORIGINAL_PARTICLE108_REAL_SAMEEXPORT_SHADERLAB_CLASSIFIED",
        "original_particle_use_slots":108,
        "source_original_one_Pass":True,
        "same_export_instance_W1_B02_verified":True,
        "source_to_export_Shader48_trace_verified":True,
        "original_six_scene_SHA_verified":True,
        "original_four_shader_owner_SHA_verified":True,
        "exported_shader_custom_reference":True,
        "original_private_Shader48_name_owner_id_export_guid_not_published":True,
        "exported_shader_builtin_reference":False,
        "original_program_vs_output_bytecode_equivalence_proven":False,
        "native_Unity_Android_GPU_pixels_verified":False,
        "source_particle108_is_phone_square_emitter_verified":False,
        "exported_ShaderLab_source_status":status,
        "selected_shaderlab_dummy_exporter_marker":status==DUMMY,
        "selected_shader_meta_found":True,
        "selected_shaderlab_file_present":True,
    }

class PostVendorDeltaTests(unittest.TestCase):
    def test_dummy_remains_dummy(self):
        result=compare(sample(),sample())
        self.assertEqual(result["status"],STATUS)
        self.assertTrue(result["post_vendor_dummy"])
        self.assertEqual(result["interpretation"],"DUMMY_PERSISTS_AFTER_VENDOR_RESTORERS")
        self.assertFalse(result["Unity_GPU_pixels_or_game_readiness_proven"])
    def test_structural_candidate_not_authenticity(self):
        x=compare(sample(),sample("STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE"))
        self.assertEqual(x["interpretation"],"DUMMY_MARKER_REMOVED_PROGRAM_STRUCTURE_ONLY")
        self.assertFalse(x["vendor_restorer_output_original_compiled_program_equivalence_proven"])
    def test_missing_program_not_success(self):
        x=compare(sample(),sample("NO_PROGRAM_SUBPROGRAMS_EXPORTED"))
        self.assertEqual(x["interpretation"],"DUMMY_MARKER_REMOVED_BUT_EXPORT_NOT_PROVEN_USABLE")
    def test_non_dummy_prevendor_rejected(self):
        with self.assertRaisesRegex(ValueError,"unproven_original_particle108_dummy_prevendor_baseline"):
            compare(sample("STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE"),sample())
    def test_unverified_source_rejected(self):
        for name,value in (("original_particle_use_slots",107),
                           ("original_four_shader_owner_SHA_verified",False),
                           ("same_export_instance_W1_B02_verified",False),
                           ("native_Unity_Android_GPU_pixels_verified",True),
                           ("exported_shader_builtin_reference",True)):
            bad=sample();bad[name]=value
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,"untrusted_original_particle108_same_export_report"):
                compare(sample(),bad)
    def test_contradictory_dummy_marker_rejected(self):
        bad=sample();bad["selected_shaderlab_dummy_exporter_marker"]=False
        with self.assertRaisesRegex(ValueError,"untrusted_original_particle108_same_export_report"):
            compare(sample(),bad)
    def test_prevendor_missing_shader_rejected(self):
        bad=sample();bad["selected_shaderlab_file_present"]=False
        with self.assertRaisesRegex(ValueError,"missing_private_original_particle108_prevendor_ShaderLab"):
            compare(bad,sample())
    def test_cli_aggregate_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/"before.json"; q=root/"after.json";out=root/"safe.json"
            p.write_text(json.dumps(sample()))
            q.write_text(json.dumps(sample()))
            self.assertEqual(main(["--before",str(p),"--after",str(q),"--out",str(out)]),0)
            result=json.loads(out.read_text())
            self.assertEqual(result["status"],STATUS)
            self.assertNotIn("original_shader_id",result)
            self.assertNotIn("guid",result)
if __name__=="__main__":
    unittest.main()
