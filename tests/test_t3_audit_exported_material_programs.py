"""T3 synthetic after-restorer material→actual ShaderLab quality controls."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_audit_exported_material_programs as t3

G1="1"*32
G2="2"*32
G3="3"*32
BUILTIN="0000000000000000f000000000000000"
SHADER='Shader "Synthetic" { SubShader { Pass { CGPROGRAM\nvoid frag() {}\nENDCG } } }'


class MaterialShaderQuality(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.assets=self.root/"Assets"
        self.assets.mkdir()
        self.shader("f",G1,"//DummyShaderTextExporter\n"+SHADER)
        self.shader("g",G2,SHADER)
        self.material("first",G1)
        self.material("second",G1,idx=2)
        self.material("third",G2,idx=3)

    def shader(self,name,guid,source):
        (self.assets/(name+".shader")).write_text(source,encoding="utf-8-sig")
        (self.assets/(name+".shader.meta")).write_text(
            "fileFormatVersion: 2\nguid: "+guid+"\nShaderImporter:\n",encoding="utf-8-sig")

    def material(self,name,guid,fileid=4800000,kind=3,idx=1):
        (self.assets/(name+".mat")).write_text(
            "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n"
            "  m_Name: Synthetic\n  m_Shader: {fileID: "+str(fileid)+
            ", guid: "+guid+", type: "+str(kind)+"}\n",encoding="utf-8-sig")

    def test_linked_dummy_reported_despite_3_valid_material_guids(self):
        r=t3.audit(self.root)
        c=r["counts"]
        self.assertEqual(c["shader_files"],2)
        self.assertEqual(c["shader_files_with_dummy_exporter_marker"],1)
        self.assertEqual(c["material_documents"],3)
        self.assertEqual(c["material_docs_using_dummy_Shader"],2)
        self.assertEqual(c["distinct_dummy_Shader_targets_referenced"],1)
        self.assertEqual(c["material_docs_using_local_custom_Shader"],3)
        self.assertEqual(c["material_docs_using_Shader_with_completed_program_pass"],3)
        self.assertTrue(r["linked_dummy_Shader_program_risk_present"])
        self.assertFalse(r["selected_ShaderLab_documents_have_proven_original_programs"])
        self.assertFalse(r["unity_Android_gpu_pixels_or_game_ready_verified"])

    def test_post_restore_replacement_preserves_link_guid_and_eliminates_dummy_marker(self):
        path=self.assets/"f.shader"
        path.write_text(SHADER,encoding="utf8")
        r=t3.audit(self.root)
        self.assertEqual(r["counts"]["material_docs_using_dummy_Shader"],0)
        self.assertEqual(r["counts"]["material_docs_using_local_custom_Shader"],3)
        self.assertFalse(r["linked_dummy_Shader_program_risk_present"])
        self.assertFalse(r["selected_ShaderLab_documents_have_proven_original_programs"])

    def test_dummy_target_impact_bands_preserve_total_without_exposing_ids(self):
        self.material("fourth",G1,idx=4)
        self.material("fifth",G1,idx=5)
        self.shader("another_dummy",G3,"//DummyShaderTextExporter\n"+SHADER)
        self.material("sixth",G3,idx=6)
        r=t3.audit(self.root)
        bands=r["dummy_target_material_link_frequency_bands"]
        self.assertEqual(bands,{"1":1,"2_to_4":1,"5_to_16":0,"17_plus":0})
        self.assertEqual(sum(bands.values()),r["counts"]["distinct_dummy_Shader_targets_referenced"])
        self.assertEqual(r["counts"]["material_docs_using_dummy_Shader"],4)
        self.assertNotIn(G1,json.dumps(bands))
        self.assertNotIn(G3,json.dumps(bands))

    def test_builtin_and_null_dont_claim_custom_shader_program(self):
        self.material("engine",BUILTIN,fileid=46,kind=0,idx=4)
        self.material("null","0"*32,fileid=0,kind=0,idx=5)
        r=t3.audit(self.root)
        c=r["counts"]
        self.assertEqual(c["material_documents"],5)
        self.assertEqual(c["material_docs_using_Unity_builtin_Shader"],1)
        self.assertEqual(c["material_docs_with_null_Shader"],1)
        self.assertEqual(c["material_docs_using_dummy_Shader"],2)

    def test_unresolved_export_shader_is_not_genuine(self):
        self.material("missing",G3,idx=6)
        r=t3.audit(self.root)
        self.assertEqual(r["counts"]["material_docs_with_unknown_or_broken_Shader"],1)
        self.assertEqual(r["counts"]["material_docs_using_local_custom_Shader"],3)

    def test_non_dummy_but_unbalanced_shader_is_reported_not_certified(self):
        (self.assets/"g.shader").write_text('Shader "broken" { SubShader {Pass {CGPROGRAM\n',encoding="utf8")
        r=t3.audit(self.root)
        self.assertEqual(r["counts"]["shader_files_with_unbalanced_ShaderLab"],1)
        self.assertEqual(r["counts"]["material_docs_using_unbalanced_ShaderLab"],1)


    def test_programmed_first_subshader_does_not_hide_incomplete_sibling(self):
        (self.assets/"g.shader").write_text(
            'Shader "Synthetic" { '
            'SubShader { Pass { CGPROGRAM\nvoid frag() {}\nENDCG } } '
            'SubShader { Pass { ZWrite Off } } }',encoding="utf8")
        c=t3.audit(self.root)["counts"]
        # Existing any-program counter stays true, but the second quality
        # tier remains structurally incomplete. Not a GPU/pixel verdict.
        self.assertEqual(c["material_docs_using_Shader_with_completed_program_pass"],3)
        self.assertEqual(c["shader_files_with_partial_subshader_program_coverage"],1)
        self.assertEqual(c["material_docs_using_Shader_with_partial_subshader_program_coverage"],1)

    def test_two_complete_subshaders_have_no_partial_coverage(self):
        complete='SubShader { Pass { CGPROGRAM\nvoid frag() {}\nENDCG } }'
        (self.assets/"g.shader").write_text(
            'Shader "Synthetic" { '+complete+" "+complete+" }",encoding="utf8")
        c=t3.audit(self.root)["counts"]
        self.assertEqual(c["shader_files_with_partial_subshader_program_coverage"],0)
        self.assertEqual(c["material_docs_using_Shader_with_partial_subshader_program_coverage"],0)

    def test_unbalanced_after_complete_pass_remains_structurally_partial(self):
        (self.assets/"g.shader").write_text(
            'Shader "Synthetic" { SubShader { Pass { '
            'CGPROGRAM\nvoid frag() {}\nENDCG } } '
            'SubShader { Pass { ZWrite Off } ',encoding="utf8")
        c=t3.audit(self.root)["counts"]
        self.assertEqual(c["material_docs_using_Shader_with_completed_program_pass"],3)
        self.assertEqual(c["shader_files_with_unbalanced_ShaderLab"],1)
        self.assertEqual(c["shader_files_with_partial_subshader_program_coverage"],1)

    def test_duplicate_shader_meta_guid_rejected(self):
        self.shader("duplicate",G1,SHADER)
        with self.assertRaisesRegex(ValueError,"reserved_or_duplicate"):
            t3.audit(self.root)

    def test_missing_shader_meta_rejected(self):
        (self.assets/"g.shader.meta").unlink()
        with self.assertRaisesRegex(ValueError,"missing_local"):
            t3.audit(self.root)

    def test_malformed_or_duplicate_material_shader_field_rejected(self):
        path=self.assets/"first.mat"
        original=path.read_text("utf-8-sig")
        for bad in (
            original.replace("m_Shader:","missingShader:"),
            original+"  m_Shader: {fileID: 4800000, guid: "+G1+", type: 3}\n",
            original.replace(", type: 3}",", type: 3, type: 3}"),
        ):
            with self.subTest(bad=bad[-65:]):
                path.write_text(bad,encoding="utf8")
                with self.assertRaises(ValueError):
                    t3.audit(self.root)

    def test_symlinked_export_asset_rejected(self):
        (self.assets/"redirect.mat").symlink_to(self.assets/"first.mat")
        with self.assertRaisesRegex(ValueError,"linked_Unity_Assets_entry"):
            t3.audit(self.root)

    def test_private_property_names_not_reported(self):
        a=t3.audit(self.root)
        serialized=json.dumps(a)
        for part in ("Synthetic","subject",G1,G2,"f.shader","first.mat"):
            self.assertNotIn(part,serialized)

    def test_cli_failure_only_safe_type_not_original_exception(self):
        (self.assets/"g.shader.meta").unlink()
        with tempfile.TemporaryDirectory() as output_dir:
            report=Path(output_dir)/"safe-report.json"
            self.assertEqual(t3.main(["--project",str(self.root),"--out",str(report)]),2)
            data=json.loads(report.read_text("utf8"))
            self.assertEqual(data["status"],"INCONCLUSIVE")
            self.assertFalse(data["selected_ShaderLab_documents_have_proven_original_programs"])
            self.assertNotIn(str(self.root),json.dumps(data))

    def test_weak_content_never_looks_like_authentic_program(self):
        self.shader("nopass",G3,'Shader "Synthetic" {SubShader {}}')
        self.material("fourth",G3,idx=4)
        counts=t3.audit(self.root)["counts"]
        self.assertEqual(counts["material_docs_using_Shader_without_completed_program_pass"],1)
        self.assertEqual(counts["shader_files_without_passes"],1)

if __name__=="__main__":
    unittest.main()
