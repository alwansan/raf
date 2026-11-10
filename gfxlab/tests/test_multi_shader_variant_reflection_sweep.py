import unittest
from gfxlab.tools.multi_shader_variant_reflection_sweep import (
    collect_stage_variant_rows, parameter_shape,
)

class TestVariantReflectionSweep(unittest.TestCase):
    def test_collects_legacy_and_player_variant_rows(self):
        stage = {
            "m_SubPrograms": [
                {"m_BlobIndex": 1, "m_GpuProgramType": 4},
                {"m_BlobIndex": 2, "m_GpuProgramType": 5},
            ],
            "m_PlayerSubPrograms": [
                [{"m_BlobIndex": 3, "m_GpuProgramType": 4}],
                [{"m_BlobIndex": 4, "m_GpuProgramType": 5}],
            ],
        }
        rows = collect_stage_variant_rows(stage)
        self.assertEqual([x["m_BlobIndex"] for x in rows], [1, 2, 3, 4])

    def test_missing_variant_arrays_are_empty(self):
        self.assertEqual(collect_stage_variant_rows({}), [])

    def test_rejects_non_object_stage(self):
        with self.assertRaises(ValueError):
            collect_stage_variant_rows(None)

    def test_rejects_non_array_variant_container(self):
        with self.assertRaises(ValueError):
            collect_stage_variant_rows({"m_PlayerSubPrograms": {"m_BlobIndex": 2}})

    def test_rejects_null_variant_rows(self):
        with self.assertRaises(ValueError):
            collect_stage_variant_rows({"m_SubPrograms": [None]})

    def test_rejects_malformed_blob_index_type(self):
        with self.assertRaises(ValueError):
            collect_stage_variant_rows({"m_PlayerSubPrograms": [{"m_BlobIndex": "2"}]})

    def test_missing_parameters_are_not_inferred(self):
        result = parameter_shape({"m_BlobIndex": 2})
        self.assertEqual(result, {})

    def test_null_parameter_block_is_not_counted_as_present(self):
        result = parameter_shape({"m_Parameters": None})
        self.assertEqual(result["null_parameter_blocks"], 1)
        self.assertNotIn("parameter_blocks_present", result)

    def test_counts_real_texture_and_cb_parameter_arrays(self):
        result = parameter_shape({
            "m_Parameters": {
                "m_TextureParams": [{"opaque": 1}, {"opaque": 2}],
                "m_ConstantBufferBindings": [{"opaque": 3}],
            }
        })
        self.assertEqual(result["parameter_blocks_present"], 1)
        self.assertEqual(result["texture_parameter_arrays_present"], 1)
        self.assertEqual(result["texture_parameter_entries"], 2)
        self.assertEqual(result["constant_buffer_binding_arrays_present"], 1)
        self.assertEqual(result["constant_buffer_binding_entries"], 1)

    def test_rejects_non_array_texture_parameters(self):
        with self.assertRaises(ValueError):
            parameter_shape({"m_Parameters": {"m_TextureParams": {}}})

    def test_rejects_non_array_constant_buffer_bindings(self):
        with self.assertRaises(ValueError):
            parameter_shape({"m_Parameters": {"m_ConstantBufferBindings": None}})

    def test_counts_top_level_sampler_metadata_without_exporting_values(self):
        result = parameter_shape({"m_Samplers": [{"secret": "not-exported"}]})
        self.assertEqual(result["top_level_sampler_metadata_rows"], 1)
