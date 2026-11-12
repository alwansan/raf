"""Synthetic negative controls for SHA-original shader-only Unity staging."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.gt_particle108_private_unity_project import prepare, isolate_stage_buffer_names

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
    def test_diagnostic_cbuffer_isolation_preserves_original_private_hlsl_resources(self):
        stage=(
            "#if defined(SHADER_STAGE_VERTEX)\n"
            "SamplerState samplers0 : register(s0);\n"
            "float4 cb1_0_m0[5];\n"
            "#elif defined(SHADER_STAGE_FRAGMENT)\n"
            "SamplerState samplers0 : register(s0);\n"
            "float4 cb1_0_m0[21];\n"
            "#else\n#error Unsupported_stage\n#endif\n"
        )
        self.shader.write_text(
            'Shader "Synthetic/Fixture" { SubShader { Pass {\n'
            'HLSLPROGRAM\n#pragma vertex main\n#pragma fragment main\n'
            '#pragma multi_compile __ LOCAL_ALPHA\n'
            '#pragma multi_compile __ LOCAL_BETA\n'
            +stage*4+"ENDHLSL\n} } }\n")
        original=self.shader.read_text()
        transformed,counts=isolate_stage_buffer_names(original)
        self.assertEqual(counts,{"vertex":4,"fragment":4})
        self.assertEqual(transformed.count("GT_UNBOUND_VS_cb1_0_m0[5]"),4)
        self.assertEqual(transformed.count("GT_UNBOUND_PS_cb1_0_m0[21]"),4)
        self.assertEqual(transformed.count("samplers0 : register(s0)"),8)
        self.assertEqual(transformed.count("#pragma multi_compile"),2)
        self.assertNotIn("GT_UNBOUND_",original)
        data=prepare(self.shader,self.editor,self.project,self.report,self.routing,
                     diagnostic_stage_buffers=True)
        self.assertTrue(data["private_stage_local_buffer_name_isolation_only"])
        self.assertFalse(data["private_original_sampler_binding_parity_proven"])
        self.assertIn("GT_UNBOUND_VS_cb1_0_m0",
                      (self.project/"Assets/GTPrivateOriginal.shader").read_text())
        self.assertEqual(original,self.shader.read_text())
        self.assertNotIn("samplers0",self.report.read_text())
        self.assertNotIn("cb1_0_m0",self.report.read_text())

    def test_diagnostic_cbuffer_isolation_rejects_wrong_stage_topology(self):
        broken=("#if defined(SHADER_STAGE_VERTEX)\nfloat4 cb1_0_m0[5];\n"
                "#elif defined(SHADER_STAGE_FRAGMENT)\nfloat4 cb1_0_m0[21];\n"
                "#else\n#error Unsupported_stage\n#endif\n")
        for wrong in (broken*3, broken*5,
                      "broken ShaderLab without stage blocks"):
            with self.subTest(bad_length=len(wrong)):
                with self.assertRaisesRegex(ValueError,"four_stage_branches_required"):
                    isolate_stage_buffer_names(wrong)

    def test_unity_2021_variant_collection_creation_uses_correct_api(self):
        # A real Unity 2021 import in run 43220728060 failed with CS0311:
        # ShaderVariantCollection is not a ScriptableObject subtype. This
        # source-only regression prevents reintroducing that exact mistake;
        # successful Unity compile is still required independently.
        editor_source=(Path(__file__).resolve().parents[1]/
                       "android-port/Experiments/GT/Editor/OriginalParticleShaderValidation.cs")
        source=editor_source.read_text(encoding="utf-8")
        self.assertIn("new ShaderVariantCollection()",source)
        self.assertNotIn("ScriptableObject.CreateInstance<ShaderVariantCollection>",source)
        self.assertIn("BuildPipeline.BuildAssetBundles",source)

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
