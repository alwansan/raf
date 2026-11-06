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
            w["objects"]=[]
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

if __name__=="__main__":
    unittest.main()
