"""Source-free controls: authentic private Particle108 per-variant ShaderLab staging."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import t3_particle108_private_shaderlab_variants as v
from test_t3_particle108_source_propstate import original as synthetic_original
from test_t3_original_particle_shader_state import v as state_value


VERT="float4 main() : SV_Position { return float4(0,0,0,1); }"
FRAG="float4 main() : SV_Target { return float4(1,0,0,1); }"


class PrivateVariantControls(unittest.TestCase):
    def test_one_variant_keeps_private_props_state_and_program(self):
        parsed=synthetic_original()
        saved=copy.deepcopy(parsed)
        text,shape=v.assemble(parsed,VERT,FRAG,(5,0))
        self.assertEqual(parsed,saved)
        self.assertEqual(shape["original_authored_property_count"],4)
        self.assertIn("ColorMask RGB",text)
        self.assertIn("HLSLPROGRAM",text)
        self.assertIn("#pragma target 5.0",text)
        self.assertIn("#pragma vertex main",text)
        self.assertIn("#pragma fragment main",text)
        self.assertIn("SHADER_STAGE_VERTEX",text)
        self.assertIn("SHADER_STAGE_FRAGMENT",text)
        self.assertIn("ENDHLSL",text)
        self.assertNotIn("DummyShaderTextExporter",text)

    def test_stage_code_without_main_rejected(self):
        with self.assertRaisesRegex(ValueError,"T3_VARIANT_SOURCE_INVALID"):
            v.assemble(synthetic_original(),"float4 nope();",FRAG,(5,0))

    def test_stage_injects_hlsl_boundary_rejected(self):
        with self.assertRaisesRegex(ValueError,"T3_VARIANT_SOURCE_INVALID"):
            v.assemble(synthetic_original(),VERT+"\nENDHLSL",FRAG,(5,0))

    def test_wrong_original_mask_fails_closed(self):
        parsed=synthetic_original()
        parsed["m_SubShaders"][0]["m_Passes"][0]["m_State"]["rtBlend0"]["colMask"]=state_value(15)
        with self.assertRaises(ValueError):
            v.assemble(parsed,VERT,FRAG,(5,0))

    def test_property_default_mismatch_rejected(self):
        with patch.object(v.props,"compare",return_value={
              "original_authored_property_names_types_exact":True,
              "original_authored_property_defaults_semantically_equal":False}):
            with self.assertRaisesRegex(ValueError,"T3_VARIANT_PROPERTY_MISMATCH"):
                v.assemble(synthetic_original(),VERT,FRAG,(5,0))

    def test_bad_model_rejected(self):
        with self.assertRaisesRegex(ValueError,"T3_VARIANT_SOURCE_INVALID"):
            v.assemble(synthetic_original(),VERT,FRAG,(6,0))

    def test_model_source_codes_derive_both_stages(self):
        dx=b"x"*36
        with patch.object(v,"version_tokens",side_effect=[
                [{"shader_stage_code":1,"shader_model":[5,0]}],
                [{"shader_stage_code":0,"shader_model":[5,0]}]]):
            self.assertEqual(v.source_models(dx,dx),(5,0))

    def test_stage_model_mismatch_not_guessed(self):
        dx=b"x"*36
        with patch.object(v,"version_tokens",side_effect=[
                [{"shader_stage_code":1,"shader_model":[5,0]}],
                [{"shader_stage_code":0,"shader_model":[4,0]}]]):
            with self.assertRaisesRegex(ValueError,"T3_VARIANT_MODEL_UNSUPPORTED"):
                v.source_models(dx,dx)

    def test_mislabeled_fragment_rejected(self):
        dx=b"x"*36
        with patch.object(v,"version_tokens",side_effect=[
                [{"shader_stage_code":1,"shader_model":[5,0]}],
                [{"shader_stage_code":1,"shader_model":[5,0]}]]):
            with self.assertRaisesRegex(ValueError,"T3_VARIANT_MODEL_UNSUPPORTED"):
                v.source_models(dx,dx)

    def test_four_isolated_private_candidates_not_routable(self):
        parsed=synthetic_original()
        def translator(data,stage,path):
            (path/"private.hlsl").write_text(VERT if stage else FRAG,encoding="utf-8")
            return {"vulkan11_valid":True,"hlsl_recovered":True,
                    "roundtrip_vulkan11_valid":True,"stage":stage}
        pairs=[(b"vs-private",b"ps-private") for _ in range(4)]
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            result=v.evaluate(pairs,parsed,folder,translator=translator,
                              model_reader=lambda vs,ps:(5,0))
            self.assertEqual(result["status"],v.STATUS)
            self.assertEqual(result["counts"]["genuine_original_DXBC_stages_translated"],8)
            self.assertEqual(result["counts"]["private_complete_one_pass_ShaderLab_candidates"],4)
            self.assertEqual(result["counts"]["private_property_default_parity_passes"],4)
            self.assertEqual(result["counts"]["separately_validated_HLSL_roundtrip_stages"],8)
            self.assertFalse(result["four_keywords_selectable_in_one_runtime_shader"])
            self.assertFalse(result["Unity_ShaderLab_import_or_GPU_compile_proven"])
            for i in range(4):
                self.assertTrue((folder/("keyword-%d-private.shader"%i)).exists())

    def test_partial_translation_never_counts_as_candidate(self):
        def bad_translator(data,stage,path):
            (path/"private.hlsl").write_text(VERT if stage else FRAG)
            return {"vulkan11_valid":True,"hlsl_recovered":False,"stage":stage}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"T3_VARIANT_TRANSLATION_MISSING"):
                v.evaluate([(b"a",b"b")]*4,synthetic_original(),Path(tmp),
                           translator=bad_translator,model_reader=lambda x,y:(5,0))
            self.assertEqual(list(Path(tmp).glob("*.shader")),[])

    def test_roundtrip_missing_false_or_unverified_fails_closed(self):
        # Original stage translation and HLSL text are insufficient if the
        # recovered HLSL was never validated back to Vulkan 1.1 SPIR-V.
        for status in ("missing", False, None):
            with self.subTest(roundtrip=status), tempfile.TemporaryDirectory() as tmp:
                def translator(data,stage,path):
                    (path/"private.hlsl").write_text(VERT if stage else FRAG,encoding="utf-8")
                    result={"vulkan11_valid":True,"hlsl_recovered":True,"stage":stage}
                    if status!="missing":
                        result["roundtrip_vulkan11_valid"]=status
                    return result
                root=Path(tmp)
                with self.assertRaisesRegex(ValueError,"T3_VARIANT_TRANSLATION_MISSING"):
                    v.evaluate([(b"a",b"b")]*4,synthetic_original(),root,
                               translator=translator,model_reader=lambda x,y:(5,0))
                self.assertEqual(list(root.glob("*.shader")),[])

    def test_stage_attestation_missing_boolean_or_wrong_fails_closed(self):
        # False equals 0 and True equals 1; neither is an authentic stage code.
        for status in ("missing", True, False, "1", 0):
            with self.subTest(stage=status), tempfile.TemporaryDirectory() as tmp:
                def translator(data,stage,path):
                    (path/"private.hlsl").write_text(VERT if stage else FRAG,encoding="utf-8")
                    result={"vulkan11_valid":True,"hlsl_recovered":True,
                            "roundtrip_vulkan11_valid":True}
                    if status!="missing":
                        result["stage"]=status
                    return result
                root=Path(tmp)
                with self.assertRaisesRegex(ValueError,"T3_VARIANT_TRANSLATION_MISSING"):
                    v.evaluate([(b"a",b"b")]*4,synthetic_original(),root,
                               translator=translator,model_reader=lambda x,y:(5,0))
                self.assertEqual(list(root.glob("*.shader")),[])

    def test_preexisting_variant_private_path_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"keyword-0-stage-1").mkdir()
            with self.assertRaises(FileExistsError):
                v.evaluate([(b"a",b"b")]*4,synthetic_original(),root,
                           translator=lambda *args:None,
                           model_reader=lambda x,y:(5,0))


if __name__=="__main__":
    unittest.main()
