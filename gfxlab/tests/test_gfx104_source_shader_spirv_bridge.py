"""GFX104 private DXBC→SPIRV→GLES pipeline mock; no Raft shader bytes."""
import struct
import unittest
from unittest.mock import patch
from pathlib import Path
from gfxlab.tools import gfx104_source_shader_spirv_bridge as bridge

def ps_chunk(opcode=98,mode=4):
    words=[0x50,4,opcode|(mode<<11)|(2<<24),0]
    return struct.pack("<4I",*words)

def seven_passes(count=524):
    rows=[{"subshader":i//4,"pass":i%4,"pairs":[]} for i in range(7)]
    for i in range(count):
        rows[i%7]["pairs"].append(({"m_BlobIndex":2},{"m_BlobIndex":1,"m_GpuProgramType":999}))
    return rows

def spv_witness(native=True):
    return {
        "group_decorations_unhandled":False,
        "input_pointer_type_unresolved":0,
        "input_direct_noperspective_nonbuiltin":int(native),
        "input_member_noperspective_decorations":0,
        "input_direct_builtin_variables":0,
        "input_no_perspective_candidate_count":int(native),
    }

class GFX104BridgeTests(unittest.TestCase):
    def run_mock(self,mode="ordinary",valid=True,source_pairs=524):
        opcode=100 if mode=="siv" else 98
        source=ps_chunk(opcode)
        def translate(vs,fs,folder):
            (Path(folder)/"fragment.spv").write_bytes(b"not-real-spv")
            return {"fragment":{"vulkan11_spirv_validation_success":valid}}
        def cross(args):
            Path(args[-1]).write_text(
                "#version 310 es\n"+
                ("noperspective in vec3 color;\n" if mode=="ordinary" else
                 "in vec3 color;\n")+"void main(){}\n")
            return True,b""
        with (patch.object(bridge,"source_pair",return_value=(object(),seven_passes(source_pairs))),
              patch.object(bridge,"code_from_ref",return_value=b"synthetic"),
              patch.object(bridge,"source_shader_chunk",return_value=source),
              patch.object(bridge,"translate_pair",side_effect=translate),
              patch.object(bridge,"inspect_spirv_input_interpolation",
                           return_value=spv_witness(mode=="ordinary")),
              patch.object(bridge,"run_quiet",side_effect=cross)):
            return bridge.original_noperspective_translation_census(object())
    def test_full_524_pairs_one_distinct_original_stage(self):
        result=self.run_mock()
        self.assertEqual(result["source_shader48_original_exact_pairs"],524)
        self.assertEqual(result["counts"]["original_pairs_seen"],524)
        self.assertEqual(result["counts"]["source_unique_ps_with_any_np"],1)
        self.assertEqual(result["counts"]["ordinary_source_np_spirv_glsl_candidate_preserved"],1)
        self.assertEqual(result["counts"]["generated_gles310_required_nv_extension"],1)
        self.assertFalse(result["source_to_generated_gles_noperspective_identity_verified"])
        self.assertFalse(result["phase_closed"])
    def test_siv_builtin_not_claimed_ordinary(self):
        result=self.run_mock(mode="siv")
        self.assertEqual(result["counts"]["source_unique_ps_with_ordinary_np"],0)
        self.assertEqual(result["counts"]["siv_np_builtin_semantics_identity_unverified"],1)
        self.assertNotIn("ordinary_source_np_spirv_glsl_candidate_preserved",result["counts"])
    def test_source_spirv_failure_recorded_separately(self):
        result=self.run_mock(valid=False)
        self.assertEqual(result["categories_of_nonrestored_stage"][
            "fragment_dxbc_spirv_validation_failed"],1)
        self.assertNotIn("ordinary_source_np_spirv_glsl_candidate_preserved",result["counts"])
    def test_source_original_pair_count_drift_fails(self):
        with self.assertRaisesRegex(ValueError,"GFX104_EXACT_SOURCE_PAIR_COUNT_DRIFT"):
            self.run_mock(source_pairs=523)
    def test_source_no_original_data_claim(self):
        result=self.run_mock()
        for flag in ("originalShaderRestored","original_material_cb_binding_verified",
                     "original_animation_verified","original_pc_phone_pixels_verified",
                     "private_shader_bytes_exported"):
            self.assertIs(result[flag],False)

if __name__=="__main__":unittest.main()
