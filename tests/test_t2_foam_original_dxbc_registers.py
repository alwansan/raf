"""Fail-closed synthetic controls for original Foam texture register/DXBC parity."""
import unittest

from scripts.t2_foam_original_dxbc_registers import (
    source_texture_registers, compare_numeric_dxbc,
)


def stage(rows):
    return {"m_CommonParameters": {
        "m_TextureParams": rows, "m_Samplers": [], "m_UAVParams": [],
    }}


def tex(index, sampler):
    return {"m_NameIndex": index, "m_Index": index,
            "m_SamplerIndex": sampler, "m_Dim": 2}


def decl(textures=(0, 1), samplers=(0, 1), uavs=()):
    return {
        "texture": {i: 2 for i in textures},
        "sampler": {i: 0 for i in samplers},
        "uav": {i: 2 for i in uavs},
    }


class OriginalFoamD3D11RegisterTests(unittest.TestCase):
    def test_exact_per_row_numeric_parity_with_outside_device_gate(self):
        r = source_texture_registers(stage([tex(0, 1), tex(1, 0)]), 2)
        result = compare_numeric_dxbc(r, decl((0, 1), (0, 1)))
        self.assertTrue(result["original_texture_t_register_set_equal_native_dxbc"])
        self.assertTrue(result["original_texture_sampler_s_register_set_equal_native_dxbc"])
        self.assertTrue(result["complete_source_texture_sampler_to_dxbc_register_set_parity"])
        self.assertEqual([(v["source_texture_index"],v["source_sampler_index"])
                          for v in result["individual_numeric_candidate_rows"]],
                         [(0, 1), (1, 0)])
        self.assertFalse(result["original_dxbc_instruction_t_s_pair_use_verified"])
        self.assertFalse(result["native_dxbc_to_translated_spirv_binding_identity_verified"])
        self.assertFalse(result["unity_material_texture_property_upload_verified"])

    def test_same_counts_wrong_t_indices_never_infer_join(self):
        rows = source_texture_registers(stage([tex(0, 1), tex(3, 0)]), 2)
        out = compare_numeric_dxbc(rows, decl((0, 1), (0, 1)))
        self.assertFalse(out["original_texture_t_register_set_equal_native_dxbc"])
        self.assertFalse(out["complete_source_texture_sampler_to_dxbc_register_set_parity"])

    def test_same_count_different_sampler_registers_never_infer_join(self):
        rows = source_texture_registers(stage([tex(0, 3), tex(1, 4)]), 2)
        out = compare_numeric_dxbc(rows, decl((0, 1), (0, 1)))
        self.assertTrue(out["original_texture_t_register_set_equal_native_dxbc"])
        self.assertFalse(out["original_texture_sampler_s_register_set_equal_native_dxbc"])

    def test_missing_sampler_index_negative_one_stays_unknown(self):
        rows = source_texture_registers(stage([tex(0, -1)]), 1)
        out = compare_numeric_dxbc(rows, decl((0,), ()))
        self.assertEqual(out["original_source_sampler_minus_one_rows"], 1)
        self.assertFalse(out["original_texture_sampler_s_register_set_equal_native_dxbc"])
        self.assertIsNone(out["individual_numeric_candidate_rows"][0][
            "sampler_register_declared_in_original_dxbc"])

    def test_missing_sampler_numeric_field_rejected(self):
        with self.assertRaises(ValueError):
            source_texture_registers(stage([{"m_Index": 0}]), 1)

    def test_repeated_sampler_register_does_not_make_false_bijection(self):
        rows = source_texture_registers(stage([tex(0, 0), tex(1, 0)]), 2)
        out = compare_numeric_dxbc(rows, decl((0, 1), (0,)))
        self.assertTrue(out["original_texture_sampler_s_register_set_equal_native_dxbc"])
        self.assertEqual(out["original_source_nonnegative_s_indices"], [0])
        self.assertEqual(len(out["individual_numeric_candidate_rows"]), 2)

    def test_original_duplicate_texture_indices_rejected(self):
        with self.assertRaises(ValueError):
            source_texture_registers(stage([tex(0, 0), tex(0, 1)]), 2)

    def test_true_bool_oversized_float_negative_indices_rejected(self):
        for a, b in ((True, 0), (0, True), (256, 0), (-1, 0),
                     (0, -2), (0, 256), (0.0, 1), (1, 1.0)):
            with self.subTest(a=a, b=b), self.assertRaises(ValueError):
                source_texture_registers(stage([{"m_Index":a,"m_SamplerIndex":b}]),1)

    def test_original_empty_vertex_stage_with_exact_empty_compiled(self):
        rows = source_texture_registers(stage([]), 0)
        out = compare_numeric_dxbc(rows, decl((), ()))
        self.assertTrue(out["complete_source_texture_sampler_to_dxbc_register_set_parity"])
        self.assertEqual(out["original_source_texture_rows"], 0)

    def test_fake_texture_and_sampler_tables_fail_closed(self):
        for bad in (
            {"m_CommonParameters":{"m_TextureParams":[],"m_Samplers":[1],"m_UAVParams":[]}},
            {"m_CommonParameters":{"m_TextureParams":[],"m_Samplers":[]}},
            {"m_CommonParameters":{"m_TextureParams":{},"m_Samplers":[],"m_UAVParams":[]}},
            {"m_CommonParameters":{"m_TextureParams":[],"m_Samplers":[],"m_UAVParams":[2]}},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                source_texture_registers(bad, 0)

    def test_original_count_drift_rejected(self):
        with self.assertRaises(ValueError):
            source_texture_registers(stage([tex(0, 0)]), 0)

    def test_extra_native_dxbc_uav_blocks_complete_parity(self):
        out = compare_numeric_dxbc(source_texture_registers(stage([tex(0, 0)]),1),
                                   decl((0,), (0,), (1,)))
        self.assertFalse(out["complete_source_texture_sampler_to_dxbc_register_set_parity"])

    def test_non_numeric_declarations_and_category_spoof_rejected(self):
        for obj in (
            {"texture":{True:2},"sampler":{},"uav":{}},
            {"texture":{0: "Texture"},"sampler":{},"uav":{}},
            {"texture":{0:2},"sampler":{"s0":0},"uav":{}},
            {"texture":{0:2},"sampler":{}},
            {"texture":{},"sampler":{},"uav":[]},
        ):
            with self.subTest(obj=obj), self.assertRaises(ValueError):
                compare_numeric_dxbc([],obj)

    def test_untrusted_source_extra_or_missing_numeric_fields_rejected(self):
        for rows in ([{"original_texture_index":0,"original_sampler_index":0,
                       "_private_symbol":"disclose"}],
                     [{"original_texture_index":0}],
                     [{"original_texture_index":0,"original_sampler_index":False}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                compare_numeric_dxbc(rows,decl())

    def test_compiled_t_s_bindings_are_not_spirv_or_material_bindings(self):
        out=compare_numeric_dxbc(source_texture_registers(stage([tex(3, 7)]),1),
                                 decl((3,), (7,)))
        self.assertTrue(out["complete_source_texture_sampler_to_dxbc_register_set_parity"])
        self.assertFalse(out["native_dxbc_to_translated_spirv_binding_identity_verified"])
        self.assertFalse(out["shaderlab_import_or_device_pixels_verified"])


if __name__ == "__main__":
    unittest.main()
