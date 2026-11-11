"""GFX105 source-private authentic-pair runner tests using synthetic bytes only."""
import struct
import unittest
from pathlib import Path
from unittest.mock import patch
from gfxlab.tools import gfx105_original_siv_fragcoord_census as census
from gfxlab.tools.gfx105_siv_fragcoord_semantic import SPIRV_MAGIC

def shdr(name=1):
    words=[0x50,6,100|(4<<11)|(4<<24),0,0,name]
    return struct.pack("<6I",*words)

def ins(op,*args):return [((len(args)+1)<<16)|op,*args]
def spv():
    words=[SPIRV_MAGIC,0x00010300,0,100,0]
    for row in (ins(32,3,1,5),ins(59,3,8,1),ins(71,8,11,15)):
        words.extend(row)
    return struct.pack("<%dI"%len(words),*words)

def mock_pairs(count=524):
    out=[{"pairs":[]} for _ in range(7)]
    for i in range(count):
        out[i%7]["pairs"].append(({"m_BlobIndex":2},
                 {"m_BlobIndex":1,"m_GpuProgramType":3}))
    return out

class GFX105PrivateCensusMocks(unittest.TestCase):
    def run_mock(self,name=1,fragment_valid=True,fragcoord=True,count=524):
        def translate(vs,ps,folder):
            (Path(folder)/"fragment.spv").write_bytes(spv())
            return {"fragment":{"vulkan11_spirv_validation_success":fragment_valid}}
        def cross(args):
            Path(args[-1]).write_text("#version 310 es\nvoid main(){vec4 c="+
                    ("gl_FragCoord" if fragcoord else "vec4(0)")+";}\n")
            return True,b""
        with (patch.object(census,"source_pair",return_value=(object(),mock_pairs(count))),
              patch.object(census,"code_from_ref",return_value=b"not-real"),
              patch.object(census,"source_shader_chunk",return_value=shdr(name)),
              patch.object(census,"translate_pair",side_effect=translate),
              patch.object(census,"run_quiet",side_effect=cross)):
            return census.original_siv_fragcoord_census(object())
    def test_complete_one_unique_stage_from_524_pairs(self):
        a=self.run_mock()
        self.assertEqual(a["counts"]["original_exact_pairs_seen"],524)
        self.assertEqual(a["counts"]["unique_original_siv_np_programs"],1)
        self.assertEqual(a["counts"]["source_siv_np_position_name_tokens"],1)
        self.assertEqual(a["counts"]["spirv_input_builtin_fragcoord_count"],1)
        self.assertTrue(a["system_name_position_to_fragcoord_candidate_complete"])
        self.assertIs(a["originalShaderRestored"],False)
        self.assertIs(a["original_pixel_value_semantics_verified"],False)
    def test_unknown_system_name_fails_candidate(self):
        a=self.run_mock(name=2)
        self.assertEqual(a["counts"]["source_siv_np_other_name_tokens"],1)
        self.assertFalse(a["system_name_position_to_fragcoord_candidate_complete"])
    def test_missing_glsl_fragcoord_fails_candidate(self):
        a=self.run_mock(fragcoord=False)
        self.assertFalse(a["system_name_position_to_fragcoord_candidate_complete"])
    def test_dxbc_spirv_error_counted_not_false_pass(self):
        a=self.run_mock(fragment_valid=False)
        self.assertFalse(a["system_name_position_to_fragcoord_candidate_complete"])
        self.assertEqual(a["unresolved_aggregate_categories"][
            "original_spirv_fragment_validation_failure"],1)
    def test_pair_population_change_rejected(self):
        with self.assertRaisesRegex(ValueError,"GFX105_ORIGINAL_PAIR_POPULATION_DRIFT"):
            self.run_mock(count=523)

if __name__=="__main__":unittest.main()
