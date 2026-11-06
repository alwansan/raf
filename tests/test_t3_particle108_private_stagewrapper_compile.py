"""Source-free negative controls for private Shader48 combined HLSLPROGRAM stages."""
from pathlib import Path
import tempfile
import unittest

from scripts import t3_particle108_private_stagewrapper_compile as probe
from scripts import t3_particle108_private_shaderlab_variants as variants
from test_t3_particle108_source_propstate import original as synthetic_original

VERT = "float4 main():SV_Position{return float4(0,0,0,1);}"
FRAG = "float4 main():SV_Target{return float4(1,0,0,1);}"


def candidate():
    return variants.assemble(synthetic_original(), VERT, FRAG, (5, 0))[0]


class StageWrapperTests(unittest.TestCase):
    def stage_dir(self, folder, text=None):
        root = Path(folder)
        for n in range(4):
            (root / ("keyword-%d-private.shader" % n)).write_text(
                candidate() if text is None else text, encoding="utf-8")
        return root

    def test_stage_arms_extract_without_sharing_shaderlab(self):
        body = probe.extract(candidate())
        self.assertIn("SHADER_STAGE_VERTEX", body)
        self.assertIn("SHADER_STAGE_FRAGMENT", body)
        self.assertIn("SV_Position", body)
        self.assertIn("SV_Target", body)
        self.assertNotIn("#pragma vertex", body)
        self.assertNotIn("#pragma fragment", body)

    def test_both_macro_branches_for_four_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            stages = []
            def fake_compile(body, stage, root):
                self.assertIn("#if defined(SHADER_STAGE_VERTEX)", body)
                self.assertTrue(root.is_dir())
                stages.append(stage)
                return True
            row = probe.verify(self.stage_dir(tmp), compiler=fake_compile)
            self.assertEqual(row["status"], probe.STATUS)
            self.assertEqual(stages, [1, 0] * 4)
            self.assertEqual(row["HLSLPROGRAM_macro_selected_stage_spirv_validations_passed"], 8)
            self.assertFalse(row["Unity_Editor_ShaderLab_import_proven"])

    def test_false_branch_result_never_counts_as_both_compiled(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = probe.verify(self.stage_dir(tmp),
                               compiler=lambda body, stage, root: stage == 1)
            self.assertEqual(row["status"], "INCONCLUSIVE")
            self.assertEqual(row["HLSLPROGRAM_macro_selected_stage_spirv_validations_passed"], 4)

    def test_missing_or_double_program_rejected(self):
        for text in (candidate().replace("HLSLPROGRAM", "MISSING"),
                     candidate().replace("ENDHLSL", "ENDHLSL\nENDHLSL")):
            with self.subTest(text_size=len(text)):
                with self.assertRaisesRegex(ValueError, "boundaries"):
                    probe.extract(text)

    def test_removed_stage_selection_rejected(self):
        text = candidate().replace("#elif defined(SHADER_STAGE_FRAGMENT)",
                                   "#else")
        with self.assertRaisesRegex(ValueError, "stage_switch"):
            probe.extract(text)

    def test_missing_stage_pragma_rejected(self):
        text = candidate().replace("#pragma fragment main", "#pragma fragment other")
        with self.assertRaisesRegex(ValueError, "pragmas"):
            probe.extract(text)

    def test_four_candidates_required_no_missing_or_extra(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.stage_dir(tmp)
            (root / "keyword-2-private.shader").unlink()
            with self.assertRaisesRegex(ValueError, "variant_set"):
                probe.verify(root, compiler=lambda *a: True)
            (root / "keyword-2-private.shader").write_text(candidate())
            (root / "keyword-9-private.shader").write_text(candidate())
            with self.assertRaisesRegex(ValueError, "variant_set"):
                probe.verify(root, compiler=lambda *a: True)

    def test_symlinked_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.stage_dir(tmp)
            (root / "keyword-1-private.shader").unlink()
            (root / "keyword-1-private.shader").symlink_to(
                root / "keyword-0-private.shader")
            with self.assertRaisesRegex(ValueError, "shaderlab_file"):
                probe.verify(root, compiler=lambda *a: True)

    def test_bool_stage_is_never_a_compiler_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "compiler_input"):
                probe.compile_branch("main()", True, Path(tmp))

    def test_source_free_status_cannot_claim_unity(self):
        with tempfile.TemporaryDirectory() as tmp:
            row=probe.verify(self.stage_dir(tmp), compiler=lambda *a: True)
            self.assertFalse(row["Unity_Editor_ShaderLab_import_proven"])
            self.assertFalse(row["original_keyword_routing_or_material_binding_proven"])
            self.assertFalse(row["original_pixels_on_Android_verified"])
            self.assertFalse(row["private_shader_text_or_compile_errors_published"])


if __name__ == "__main__":
    unittest.main()
