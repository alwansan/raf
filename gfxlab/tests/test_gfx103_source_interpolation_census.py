"""GFX103 source-private runner controls, using only synthetic Shader token records."""
import struct
import unittest
from unittest.mock import patch
from gfxlab.tools import gfx103_source_interpolation_census as stage

def shdr(opcode,mode):
    words=[0x50,4,opcode|(mode<<11)|(2<<24),0]
    return struct.pack("<4I",*words)

def passes():
    # Six passes with 75 cases and one with 74 => 524 original-exact pair-shaped fixtures.
    result=[]
    next_id=0
    for i,n in enumerate((75,75,75,75,75,75,74)):
        rows=[]
        for _ in range(n):
            rows.append(({"m_BlobIndex":next_id},{"m_BlobIndex":next_id%2}))
            next_id+=1
        result.append({"subshader":0 if i<4 else 1,"pass":i%4,"pairs":rows})
    return result

class SourcePrivateCensusSyntheticTests(unittest.TestCase):
    def mocked_run(self,fixtures):
        with (patch.object(stage,"source_pair",return_value=(object(),fixtures)),
              patch.object(stage,"code_from_ref",side_effect=lambda m,p,k:
                   shdr(98,4) if m["m_BlobIndex"]==0 else shdr(100,4)),
              patch.object(stage,"source_shader_chunk",side_effect=lambda b:b)):
            return stage.census(object())
    def test_counts_all_524_and_separates_siv_ordinary(self):
        r=self.mocked_run(passes())
        self.assertEqual(r["original_exact_pair_count"],524)
        self.assertEqual(r["distinct_original_pixel_stages_in_exact_pairs"],2)
        self.assertEqual(r["pair_occurrences_with_ordinary_noperspective"],262)
        self.assertEqual(r["pair_occurrences_with_siv_noperspective"],262)
        self.assertEqual(r["unique_pixel_stage_ordinary_modes"],{"linear_noperspective":1})
        self.assertEqual(r["unique_pixel_stage_siv_modes"],{"linear_noperspective":1})
        self.assertIs(r["originalShaderRestored"],False)
        self.assertIs(r["source_to_generated_spirv_semantics_verified"],False)
        self.assertIs(r["original_material_cb_binding_verified"],False)
    def test_count_drift_rejected(self):
        ps=passes()
        ps[-1]["pairs"].append(({"m_BlobIndex":999},{"m_BlobIndex":0}))
        with self.assertRaisesRegex(ValueError,"GFX103_ORIGINAL_524_PAIRS_DRIFT"):
            self.mocked_run(ps)
    def test_empty_original_pass_rejected(self):
        ps=passes()
        ps[0]["pairs"]=[]
        with self.assertRaisesRegex(ValueError,"GFX103_EMPTY_OR_BAD_EXACT_PASS_PAIRS"):
            self.mocked_run(ps)
    def test_source_pixel_index_malformed_rejected(self):
        ps=passes()
        ps[0]["pairs"][0]=(ps[0]["pairs"][0][0],{"m_BlobIndex":None})
        with self.assertRaisesRegex(ValueError,"GFX103_PIXEL_STAGE_BLOB_INDEX_INVALID"):
            self.mocked_run(ps)

if __name__=="__main__":unittest.main()
