"""Synthetic independent source→same-AssetRipper particle ShaderLab quality guards.

No real Raft original names, source PathIDs, shader or exported GUIDs appear.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_particle108_shaderlab_export_quality as m


SHA="a"*32
INSTANCE="e"*32
SOURCE=("resources.assets",777)


def traces(*,guid=SHA,kind=3):
    # The real W1/B02 one-instance adapter intentionally requires at least
    # one Material21 and one Texture2D28 object, even for a shader-only query.
    w1={"schema_version":1,"export_instance":INSTANCE,"objects":[
        {"class_id":48,"source":{"owner":"Raft_Data/"+SOURCE[0],"path_id":SOURCE[1]},
         "export":{"file_id":4800000,"guid":guid,"type":kind}},
        {"class_id":21,"source":{"owner":"Raft_Data/"+SOURCE[0],"path_id":SOURCE[1]+1},
         "export":{"file_id":2100000,"guid":"c"*32,"type":2}}
    ]}
    b02={"schema_version":1,"export_instance":INSTANCE,"objects":[
        {"class_id":28,"source":{"owner":"Raft_Data/"+SOURCE[0],"path_id":SOURCE[1]+2},
         "export":{"file_id":2800000,"guid":"d"*32,"type":2}}
    ]}
    return w1,b02


def write(root:Path,source,*,guid=SHA):
    root.mkdir(parents=True,exist_ok=True)
    (root/"fixture.shader").write_text(source)
    (root/"fixture.shader.meta").write_text("fileFormatVersion: 2\nguid: "+guid+"\n")


PROGRAM='''Shader "Synthetic/Particle" {
SubShader {
  Pass {
    CGPROGRAM
    #pragma vertex v
    #pragma fragment f
    ENDCG
  }
}
}
'''


class RealExportQualitySynthetic(unittest.TestCase):
    def test_builtin_reference_has_no_false_custom_shader_output_claim(self):
        with tempfile.TemporaryDirectory() as d:
            from scripts.probe_a13_exported_material_shader_guids import BUILTIN
            builtin=next(iter(sorted(BUILTIN-{"0"*32})))
            w1,b02=traces(guid=builtin,kind=0)
            r=m.classify(SOURCE,w1,b02,Path(d))
            self.assertTrue(r["exported_shader_builtin_reference"])
            self.assertFalse(r["exported_shader_custom_reference"])
            self.assertFalse(r["selected_shaderlab_file_present"])
            self.assertEqual(r["exported_ShaderLab_source_status"],
                             "UNITY_BUILTIN_REFERENCE_NO_CUSTOM_SHADER_FILE")
            self.assertFalse(r["native_Unity_Android_GPU_pixels_verified"])

    def test_custom_one_pass_program_is_structural_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,PROGRAM)
            r=m.classify(SOURCE,*traces(),root)
            self.assertEqual(r["status"],m.STATUS)
            self.assertEqual(r["selected_shaderlab_total_passes"],1)
            self.assertEqual(r["selected_shaderlab_complete_program_passes"],1)
            self.assertFalse(r["selected_shaderlab_dummy_exporter_marker"])
            self.assertEqual(r["exported_ShaderLab_source_status"],
                             "STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE")
            self.assertFalse(r["original_program_vs_output_bytecode_equivalence_proven"])
            public=json.dumps(r)
            for private in (SHA,INSTANCE,"fixture.shader","resources.assets","777",
                            "Synthetic/Particle"):
                self.assertNotIn(private,public)

    def test_two_valid_alternate_subshaders_are_not_two_runtime_passes(self):
        # Two mutually-exclusive SubShaders with one Pass each are NOT
        # a source-to-export original one-Pass mismatch.
        two='''Shader "Synthetic/Particle" {
        SubShader { Pass { CGPROGRAM
            float4 v() { return 0; }
            ENDCG } }
        SubShader { Pass { HLSLPROGRAM
            float4 f() { return 1; }
            ENDHLSL } }
        }'''
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,two)
            report=m.classify(SOURCE,*traces(),root)
            self.assertEqual(report["selected_shaderlab_total_passes"],2)
            self.assertEqual(report["selected_shaderlab_subshader_count"],2)
            self.assertTrue(report["selected_shaderlab_one_pass_per_subshader"])
            self.assertTrue(report["selected_shaderlab_all_subshaders_programmed"])
            self.assertFalse(report["selected_shaderlab_active_subshader_runtime_verified"])
            self.assertEqual(report["exported_ShaderLab_source_status"],
                             "STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE")
            self.assertFalse(report["native_Unity_Android_GPU_pixels_verified"])

    def test_unprogrammed_fallback_cannot_be_accepted_as_structural_shader(self):
        alt='''Shader "Synthetic/Particle" {
        SubShader { Pass { CGPROGRAM
          float4 v() { return 0; }
          ENDCG } }
        SubShader { Pass { /* fallback without any program */ } }
        }'''
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,alt)
            report=m.classify(SOURCE,*traces(),root)
            self.assertEqual(report["selected_shaderlab_subshader_count"],2)
            self.assertTrue(report["selected_shaderlab_one_pass_per_subshader"])
            self.assertFalse(report["selected_shaderlab_all_subshaders_programmed"])
            self.assertEqual(report["exported_ShaderLab_source_status"],
                             "INCOMPLETE_OR_UNPROGRAMMED_CUSTOM_SHADER")

    def test_one_alternate_two_pass_still_mismatches_original_one_pass(self):
        alt='''Shader "Synthetic/Particle" {
        SubShader { Pass { CGPROGRAM
          float4 v() { return 0; }
          ENDCG } }
        SubShader { Pass { CGPROGRAM
          float4 f() { return 0; }
          ENDCG }
          Pass { HLSLPROGRAM
          float4 f2() { return 0; }
          ENDHLSL } }
        }'''
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,alt)
            report=m.classify(SOURCE,*traces(),root)
            self.assertEqual(report["selected_shaderlab_total_passes"],3)
            self.assertEqual(report["selected_shaderlab_subshader_count"],2)
            self.assertFalse(report["selected_shaderlab_one_pass_per_subshader"])
            self.assertTrue(report["selected_shaderlab_all_subshaders_programmed"])
            self.assertEqual(report["exported_ShaderLab_source_status"],
                             "CUSTOM_PASS_COUNT_DIFFERS_FROM_ORIGINAL")

    def test_exact_authored_shader_properties_are_checked_before_structural_claim(self):
        private='''Properties {
        _Color ("Tint", Color) = (1,1,1,1)
        _MainTex ("Texture", 2D) = "white" {}
        }'''
        shader=PROGRAM.replace("SubShader {",private+"\nSubShader {",1)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,shader)
            r=m.classify(SOURCE,*traces(),root,
                         private_authored_properties=private)
            self.assertTrue(r["source_authored_properties_compared_to_exact_export"])
            self.assertTrue(r["source_to_export_authored_property_names_types_match"])
            self.assertEqual(r["source_to_export_authored_property_counts"]
                             ["source_authored_texture_property_count"],1)
            self.assertEqual(r["exported_ShaderLab_source_status"],
                             "STRUCTURAL_ONE_PASS_PROGRAM_PRESENT_NOT_EQUIVALENCE")
            self.assertFalse(r["authored_property_or_original_program_android_pixels_verified"])
            for label in ("_Color","_MainTex","Synthetic/Particle"):
                self.assertNotIn(label,json.dumps(r))

    def test_missing_authored_texture_or_mistyped_color_rejects_structural_ready(self):
        private='''Properties {
        _Color ("Tint", Color) = (1,1,1,1)
        _MainTex ("Texture", 2D) = "white" {}
        }'''
        scenarios=(
            ('Properties {\n_Color ("Tint", Color) = (1,1,1,1)\n}',1,0),
            ('Properties {\n_Color ("Tint", Float) = 1\n'
             '_MainTex ("Texture", 2D) = "white" {}\n}',0,1),
        )
        for export,missing,wrong in scenarios:
            with self.subTest(export=export),tempfile.TemporaryDirectory() as d:
                root=Path(d)
                # Each fixture property is on one line; no extra claims
                # about interpreting arbitrary nonstandard ShaderLab syntax.
                code=PROGRAM.replace("SubShader {",export+"\nSubShader {",1)
                write(root,code)
                r=m.classify(SOURCE,*traces(),root,
                             private_authored_properties=private)
                self.assertFalse(r["source_to_export_authored_property_names_types_match"])
                self.assertEqual(r["exported_ShaderLab_source_status"],
                                 "AUTHORED_PROPERTY_NAME_OR_TYPE_MISMATCH")
                counts=r["source_to_export_authored_property_counts"]
                self.assertEqual(counts["original_authored_property_names_missing_in_export"],missing)
                self.assertEqual(counts["matched_name_different_type"],wrong)

    def test_dummy_exporter_marker_remains_primary_failure_with_property_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,"//DummyShaderTextExporter\n"+PROGRAM)
            r=m.classify(SOURCE,*traces(),root,
                         private_authored_properties='Properties { _Secret ("Private", Float)=1 }')
            self.assertEqual(r["exported_ShaderLab_source_status"],
                             "ACTUAL_DUMMY_SHADER_TEXT_EXPORTER")
            self.assertFalse(r["source_authored_properties_compared_to_exact_export"])
            self.assertFalse(r["source_to_export_authored_property_names_types_match"])

    def test_dummy_marker_remains_dummy_even_with_plausible_fake_program(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,"//DummyShaderTextExporter\n"+PROGRAM)
            r=m.classify(SOURCE,*traces(),root)
            self.assertEqual(r["exported_ShaderLab_source_status"],
                             "ACTUAL_DUMMY_SHADER_TEXT_EXPORTER")
            self.assertTrue(r["selected_shaderlab_dummy_exporter_marker"])
            self.assertEqual(r["selected_shaderlab_complete_program_passes"],1)

    def test_no_subprograms_reported_instead_of_success(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,"// No subprograms found\nShader \"Synthetic/Particle\" { SubShader { Pass {} }}")
            r=m.classify(SOURCE,*traces(),root)
            self.assertEqual(r["exported_ShaderLab_source_status"],
                             "NO_PROGRAM_SUBPROGRAMS_EXPORTED")
            self.assertEqual(r["selected_shaderlab_complete_program_passes"],0)

    def test_missing_meta_and_shader_file_classified_without_guessing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            r=m.classify(SOURCE,*traces(),root)
            self.assertEqual(r["exported_ShaderLab_source_status"],"CUSTOM_SHADER_META_MISSING")
            (root/"fake.shader.meta").write_text("guid: "+SHA+"\n")
            r=m.classify(SOURCE,*traces(),root)
            self.assertEqual(r["exported_ShaderLab_source_status"],"CUSTOM_SHADER_TEXT_MISSING")

    def test_cross_instance_and_missing_shader48_trace_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,PROGRAM)
            w,b=traces()
            b["export_instance"]="f"*32
            with self.assertRaisesRegex(ValueError,"Different exporter instances"):
                m.classify(SOURCE,w,b,root)
            w,b=traces()
            # Preserve a valid same-export Material21 source row so the
            # fixture isolates a missing Shader48 trace, not missing Material.
            w["objects"]=[x for x in w["objects"] if x["class_id"]!=48]
            with self.assertRaisesRegex(ValueError,"one_original_particle"):
                m.classify(SOURCE,w,b,root)
            w,b=traces()
            w["objects"].append(w["objects"][0])
            with self.assertRaisesRegex(ValueError,"one_original_particle"):
                m.classify(SOURCE,w,b,root)

    def test_malformed_source_or_builtin_export_type_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,PROGRAM)
            with self.assertRaisesRegex(ValueError,"source_identity"):
                m.classify(("fake-owner",777),*traces(),root)
            from scripts.probe_a13_exported_material_shader_guids import BUILTIN
            builtin=next(iter(sorted(BUILTIN-{"0"*32})))
            with self.assertRaisesRegex(ValueError,"builtin"):
                m.classify(SOURCE,*traces(guid=builtin,kind=3),root)

    def test_duplicate_meta_guid_rejected_before_export_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,PROGRAM)
            inner=root/"other";inner.mkdir()
            (inner/"other.shader.meta").write_text("guid: "+SHA+"\n")
            with self.assertRaisesRegex(ValueError,"duplicate_custom"):
                m.classify(SOURCE,*traces(),root)

    def test_unprogrammed_and_alternate_two_pass_are_not_equivalence(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,"Shader \"Synthetic/Particle\" {SubShader{Pass{}}}")
            r=m.classify(SOURCE,*traces(),root)
            self.assertEqual(r["exported_ShaderLab_source_status"],
                             "INCOMPLETE_OR_UNPROGRAMMED_CUSTOM_SHADER")
            write(root,PROGRAM.replace("  Pass {","  Pass {} Pass {"))
            r=m.classify(SOURCE,*traces(),root)
            self.assertEqual(r["exported_ShaderLab_source_status"],
                             "CUSTOM_PASS_COUNT_DIFFERS_FROM_ORIGINAL")


    def test_default_drift_blocks_shader48_structural_ready(self):
        private='''Properties {
        _Color ("Tint", Color) = (1,1,1,1)
        _MainTex ("Texture", 2D) = "white" {}
        }'''
        changed='''Properties {
        _Color ("Tint", Color) = (1,0,1,1)
        _MainTex ("Texture", 2D) = "white" {}
        }'''
        shader=PROGRAM.replace("SubShader {",changed+"\nSubShader {",1)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write(root,shader)
            report=m.classify(SOURCE,*traces(),root,
                              private_authored_properties=private)
            self.assertTrue(report["source_authored_properties_compared_to_exact_export"])
            self.assertTrue(report["source_to_export_authored_property_names_types_match"])
            self.assertFalse(report["source_to_export_authored_property_defaults_match"])
            self.assertEqual(report["source_to_export_authored_property_counts"]
                             ["matched_name_type_different_default"],1)
            self.assertEqual(report["exported_ShaderLab_source_status"],
                             "AUTHORED_PROPERTY_DEFAULT_MISMATCH")
            self.assertFalse(report["native_Unity_Android_GPU_pixels_verified"])
            self.assertNotIn("(1,0,1,1)",json.dumps(report))


if __name__=="__main__":
    unittest.main()
