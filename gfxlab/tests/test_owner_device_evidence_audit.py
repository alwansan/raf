import unittest
from gfxlab.tools.owner_device_evidence_audit import (
    parse_json_stream,census_reports,EXPECTED_MODELS
)

def row(model="M00",mode="SOURCE_PBR_STANDARD_APPROX"):
    return dict(
        experiment="GFX-MULTI-026",
        modelId=model,materialMode=mode,
        gfxDevice="SyntheticGPU",gfxApi="OpenGLES3",unityVersion="2021.3.45f2",
        originalShaderRestored=False,originalAnimationRestored=False,
        coloredPixelsAutomaticallyVerified=False,
        errors=0,firstError="",
        diagnosticRole="BASECOLOR",diagnosticChannel="RGB",
        diagnosticSampling="SOURCE_TEXTURE_COLORSPACE_IMPORT",
        diagnosticProbeStatus="DIAGNOSTIC_SHADER_NOT_SOURCE_SHADER48",
        diagnosticMaterialSurface=0,diagnosticShaderSupported=True,
        diagnosticTextureAssigned=True,
    )

class TestOwnerEvidenceAuditor(unittest.TestCase):
    def test_concatenated_copy_json(self):
        data='{"a":1}\n\n{"b":2}\n'
        self.assertEqual(parse_json_stream(data),[{"a":1},{"b":2}])
    def test_reject_non_object(self):
        with self.assertRaises(ValueError):parse_json_stream('[1,2]')
        with self.assertRaises(ValueError):parse_json_stream("   ")
    def test_fail_closed_incomplete_schema(self):
        r=row()
        del r["originalShaderRestored"]
        with self.assertRaises(ValueError):census_reports([r],row(),16,10)
    def test_reject_unrelated_apk(self):
        r=row();r["experiment"]="OTHER_RUN"
        with self.assertRaises(ValueError):census_reports([r],row(),16,10)
    def test_positive_mixed_model_source_modes(self):
        rows=[row(m,mode) for m in EXPECTED_MODELS
              for mode in ("SOURCE_ALBEDO_STANDARD","SOURCE_PBR_STANDARD_APPROX")]
        result=census_reports(rows,rows[-1],16,10)
        self.assertEqual(result["owner_json_snapshots"],12)
        self.assertTrue(result["all_six_models_logged"])
        self.assertTrue(result["albedo_and_standard_pbr_logged_for_each_model"])
        self.assertEqual(result["logged_channel_component_counts"],{"RGB":12})
        self.assertTrue(result["all_copy_logs_only_basecolor_rgb_source_surface0"])
        self.assertEqual(result["compiled_device_shader_cache_files"],10)
        self.assertFalse(result["original_shader48_proven_on_adreno"])
        self.assertFalse(result["normal_metallic_individual_gpu_channels_linked_to_copy_log"])
        self.assertFalse(result["pixel_or_shader_binary_exported"])
    def test_normal_preview_cannot_be_assumed_from_default_log(self):
        rows=[row()]
        result=census_reports(rows,row(),1,1)
        self.assertFalse(result["normal_metallic_individual_gpu_channels_linked_to_copy_log"])
        rows[0]["diagnosticRole"]="NORMAL"
        result=census_reports(rows,row(),1,1)
        self.assertTrue(result["normal_metallic_individual_gpu_channels_linked_to_copy_log"])
        self.assertFalse(result["source_gfxlab_shader_parity_gate_closed"])
    def test_error_scope_is_snapshots_only(self):
        rows=[row(),row()]
        rows[1]["errors"]=2
        rows[1]["firstError"]="SYNTHETIC_ERROR"
        result=census_reports(rows,rows[-1],2,0)
        self.assertEqual(result["owner_errors_in_available_snapshots"],2)
        self.assertEqual(result["nonempty_first_errors"],1)
        self.assertFalse(result["full_system_logcat_present"])
