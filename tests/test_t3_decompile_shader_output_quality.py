"""Source-free adversarial checks for actual ShaderUSC Decompile metadata census."""
from pathlib import Path
import tempfile
import unittest

from scripts import t3_decompile_shader_output_quality as m


class USCOutputQuality(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"Assets"
        self.root.mkdir()
        self.targets={f"{i:032x}":3 for i in range(1,10)}

    def make(self, index, *, content=None, meta=True, guid=None):
        g=guid or f"{index:032x}"
        path=self.root/(f"subject-{index}.shader")
        if content is None:
            content=('Shader "S" {SubShader {Pass {CGPROGRAM\n'
                     'float4 frag() : SV_Target {return 0;}\nENDCG}}}')
        path.write_text(content,encoding="utf-8-sig")
        if meta:
            (self.root/(path.name+".meta")).write_text("fileFormatVersion: 2\nguid: "+g+"\nShaderImporter:\n",encoding="utf-8-sig")
        return path

    def all_outputs(self, override=None):
        for i in range(1,10):
            self.make(i,content=(override if i==1 else None))
        return m.classify_outputs(self.root,self.targets)

    def test_nine_true_shaderlab_pass_count_and_provenance_limits(self):
        r=self.all_outputs()
        counts=r["aggregate_output"]
        self.assertEqual(counts["selected_original_custom_Shader_objects"],9)
        self.assertEqual(counts["selected_original_custom_Shader_passes"],27)
        self.assertEqual(counts["selected_ShaderLab_files_present"],9)
        self.assertEqual(counts["selected_ShaderLab_parsed"],9)
        self.assertEqual(counts["selected_source_passes_missing_in_parseable_export"],18)
        self.assertEqual(r["parsed_actual_ShaderLab_pass_histogram"],{1:9})
        self.assertFalse(r["complete_original_program_subprogram_or_compiler_equivalence_proven"])

    def test_explicit_dummy_marker_does_not_count_authentic_program(self):
        r=self.all_outputs(override="//DummyShaderTextExporter\nShader \"S\" {SubShader {Pass {CGPROGRAM\nvoid f(){}\nENDCG}}}")
        self.assertEqual(r["aggregate_output"]["selected_with_DummyShaderTextExporter_marker"],1)
        self.assertFalse(r["complete_original_program_subprogram_or_compiler_equivalence_proven"])

    def test_decompile_unbalanced_and_subprogram_markers_are_separate(self):
        r=self.all_outputs(override="Shader \"Broken\" {SubShader {Pass {\n// No subprograms found\n")
        c=r["aggregate_output"]
        self.assertEqual(c["selected_with_No_subprograms_found_marker"],1)
        self.assertEqual(c["selected_ShaderLab_unbalanced_braces"],1)
        self.assertEqual(c["selected_ShaderLab_parsed"],9)

    def test_missing_shader_file_under_matching_meta_is_reported(self):
        self.all_outputs()
        (self.root/"subject-1.shader").unlink()
        r=m.classify_outputs(self.root,self.targets)
        self.assertEqual(r["aggregate_output"]["selected_ShaderLab_file_missing"],1)

    def test_missing_meta_is_not_made_up_from_shader_name(self):
        self.all_outputs()
        (self.root/"subject-1.shader.meta").unlink()
        r=m.classify_outputs(self.root,self.targets)
        self.assertEqual(r["aggregate_output"]["selected_ShaderLab_meta_missing"],1)

    def test_selected_shader_meta_duplication_rejected(self):
        self.all_outputs()
        (self.root/"different.shader").write_text('Shader "S" {}',encoding="utf8")
        (self.root/"different.shader.meta").write_text("guid: "+f"{1:032x}"+"\n",encoding="utf8")
        with self.assertRaisesRegex(ValueError,"duplicate_selected"):
            m.classify_outputs(self.root,self.targets)

    def test_reject_missing_or_unproven_exact_source_guid_scope(self):
        self.all_outputs()
        with self.assertRaisesRegex(ValueError,"untrusted_original_custom"):
            m.classify_outputs(self.root,dict(list(self.targets.items())[:-1]))

    def test_synthetic_no_source_text_or_guid_in_public_report(self):
        r=str(self.all_outputs())
        self.assertNotIn("subject-1",r)
        self.assertNotIn(f"{1:032x}",r)
        self.assertNotIn("float4 frag",r)
        self.assertNotIn("fileFormatVersion",r)

    def test_builtins_not_counted_in_custom_source_map(self):
        source={("sharedassets0.assets",i):{"pass_count":3,"subshader_pass_counts":[3]} for i in range(1,11)}
        # exactly 38 source passes, 9 custom and 1 engine
        source[("sharedassets0.assets",1)]["pass_count"]=11
        rows=[{"class_id":21,"source":{"owner":"sharedassets6.assets","path_id":1000}}]
        for i in range(1,11):
            rows.append({"class_id":48,"source":{"owner":"sharedassets0.assets","path_id":i},
                         "export":{"file_id":46 if i==1 else 4800000,
                                   "guid":"0000000000000000f000000000000000" if i==1 else f"{i:032x}",
                                   "type":0 if i==1 else 3}})
        mapping=m.custom_source_map(source,{"objects":rows})
        self.assertEqual(len(mapping),9)
        self.assertEqual(sum(mapping.values()),27)

    def test_duplicate_original_source_shader_ptr_refused(self):
        source={("sharedassets0.assets",i):{"pass_count":3,"subshader_pass_counts":[3]} for i in range(1,11)}
        source[("sharedassets0.assets",1)]["pass_count"]=11
        rows=[{"class_id":48,"source":{"owner":"sharedassets0.assets","path_id":i},
               "export":{"file_id":46 if i==1 else 4800000,
                         "guid":"0000000000000000f000000000000000" if i==1 else f"{i:032x}",
                         "type":0 if i==1 else 3}} for i in range(1,11)]
        rows.append(dict(rows[1]))
        with self.assertRaisesRegex(ValueError,"duplicate_selected_original"):
            m.custom_source_map(source,{"objects":rows})

if __name__=="__main__":
    unittest.main()
