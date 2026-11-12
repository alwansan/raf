"""Synthetic negative controls for SHA-original shader-only Unity staging."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.gt_particle108_private_unity_project import prepare

class GTOriginalUnityStagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.original=self.root/"original"
        self.original.mkdir()
        self.shader=self.original/"original.shader"
        self.shader.write_text(
            'Shader "Synthetic/Fixture" { SubShader { Pass {\n'
            'HLSLPROGRAM\n#pragma vertex main\n#pragma fragment main\n'
            '#pragma multi_compile __ LOCAL_ALPHA\n'
            '#pragma multi_compile __ LOCAL_BETA\n'
            'float4 main():SV_Target{return 1;}\nENDHLSL\n} } }\n')
        self.editor=self.root/"editor.cs"
        self.editor.write_text("// synthetic only\n")
        self.routing=self.root/"routing.json"
        self.proof={
            "status":"T3_PRIVATE_SHADER48_PROVISIONAL_TWO_KEYWORD_SINGLE_SHADERLAB_VALID",
            "source_original_keyword_name_indices_mapped":True,
            "original_keyword_pair_routes":4,
            "private_combination_stage_compiles_attempted":8,
            "private_combination_stage_Vulkan11_SPIRV_valid":8,
            "original_keyword_flags_pragma_scope_proven":False,
            "Unity_ShaderLab_import_or_actual_variant_selection_proven":False,
            "original_Material_binding_proven":False,
            "Android_pixels_proven":False,
        }
        self.routing.write_text(json.dumps(self.proof))
        self.project=self.root/"candidate"
        self.report=self.root/"report.json"
    def stage(self):
        return prepare(self.shader,self.editor,self.project,self.report,self.routing)
    def test_two_authentic_keyword_switches_create_private_unity_project(self):
        data=self.stage()
        self.assertEqual(data["source_original_variant_combinations"],4)
        self.assertFalse(data["unity_Android_compilation_proven"])
        self.assertFalse(data["game_source_or_GUID_modified"])
        self.assertEqual((self.project/"Assets/GTPrivateOriginal.shader").read_bytes(),self.shader.read_bytes())
        self.assertTrue((self.project/"Assets/Editor/OriginalParticleShaderValidation.cs").is_file())
        self.assertIn("2021.3.45f2",(self.project/"ProjectSettings/ProjectVersion.txt").read_text())
        self.assertNotIn("LOCAL_ALPHA",self.report.read_text())
    def test_rejects_corrupt_glslang_variant_count(self):
        self.proof["private_combination_stage_Vulkan11_SPIRV_valid"]=7
        self.routing.write_text(json.dumps(self.proof))
        with self.assertRaisesRegex(ValueError,"authentication_unproven"):
            self.stage()
        self.assertFalse(self.project.exists())
    def test_rejects_wrong_original_keyword_dimension(self):
        self.shader.write_text(self.shader.read_text().replace(
            "#pragma multi_compile __ LOCAL_BETA\n",""))
        with self.assertRaisesRegex(ValueError,"untrusted_private"):
            self.stage()
        self.assertFalse(self.project.exists())
    def test_rejects_preexisting_private_destination(self):
        self.project.mkdir()
        with self.assertRaisesRegex(ValueError,"unsafe_private"):
            self.stage()
    def test_rejects_original_symlink(self):
        self.shader.unlink()
        self.shader.symlink_to(self.editor)
        with self.assertRaisesRegex(ValueError,"unsafe_private"):
            self.stage()
    def test_original_keyword_names_not_ever_in_public_report(self):
        d=self.stage()
        self.assertNotIn("LOCAL_ALPHA",json.dumps(d))
        self.assertNotIn("LOCAL_BETA",json.dumps(d))
        self.assertNotIn("Synthetic/Fixture",json.dumps(d))

if __name__=="__main__":
    unittest.main()
