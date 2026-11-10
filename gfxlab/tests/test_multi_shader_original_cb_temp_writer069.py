"""GFX069 synthetic-only expanded authentic D3D10 trusted writer opcode guards."""
import unittest
from gfxlab.tools.multi_shader_original_cb_temp_writer069 import (
    original_relative_temp_nearest_writer_census,EXTRA_TRUSTED_WRITER_OPCODE_ARITY
)
from gfxlab.tests.test_multi_shader_original_cb_temp_writer068 import (
    temp,cb_relative,instruction,moving
)
from gfxlab.tests.test_multi_shader_original_dynamic_cb_taxonomy import shdr

def check(inst):
    return original_relative_temp_nearest_writer_census(shdr(inst),{2:8})

class TestGFX069AdditionalTrustedSourceWriters(unittest.TestCase):
    def test_ftou_28_produces_candidate_same_component(self):
        w=instruction(28,[temp(5,0,True),temp(6)])
        r=moving(temp(0,0,True),cb_relative(5,0))
        c=check([w,r])
        self.assertEqual(c["relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run"],1)
        self.assertEqual(c["candidate_nearest_writer_original_opcode_28"],1)
        self.assertEqual(c["extra_trusted_writer_opcode_instances"],1)

    def test_iadd_30_and_ishl_41_are_trusted_writers_not_fake_source_shader_restoration(self):
        for op in (30,41,42,85):
            with self.subTest(opcode=op):
                writer=instruction(op,[temp(5,0,True),temp(6),temp(7)])
                reader=moving(temp(0,0,True),cb_relative(5,0))
                c=check([writer,reader])
                self.assertEqual(c["relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run"],1)
                self.assertEqual(c[f"candidate_nearest_writer_original_opcode_{op}"],1)

    def test_iadd_wrong_component_does_not_supply_index(self):
        w=instruction(30,[temp(5,1,True),temp(6),temp(7)])
        r=moving(temp(0,0,True),cb_relative(5,0))
        c=check([w,r])
        self.assertEqual(c.get("relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run",0),0)
        self.assertEqual(c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"],1)

    def test_if_branch_opcode_invalidates_even_trusted_ftou(self):
        writer=instruction(28,[temp(5,0,True),temp(6)])
        # Opaque IF opcode 31 with an entirely unknown control-flow structure:
        # always a barrier, never a trusted writer or dominance proof.
        c=check([writer,[(2<<24)|31,0],moving(temp(0,0,True),cb_relative(5,0))])
        self.assertEqual(c.get("relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run",0),0)
        self.assertEqual(c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"],1)

    def test_invalid_extra_opcode_arity_is_fail_closed(self):
        malformed=instruction(28,[temp(5,0,True),temp(6),temp(7)])
        with self.assertRaisesRegex(ValueError,"TRAILING_DATA"):
            check([malformed])

    def test_expected_expanded_opcode_whitelist_is_source_owned_and_bounded(self):
        self.assertEqual(EXTRA_TRUSTED_WRITER_OPCODE_ARITY[28],2)
        self.assertEqual(EXTRA_TRUSTED_WRITER_OPCODE_ARITY[30],3)
        self.assertEqual(EXTRA_TRUSTED_WRITER_OPCODE_ARITY[35],4)
        self.assertEqual(EXTRA_TRUSTED_WRITER_OPCODE_ARITY[55],4)
        self.assertNotIn(31,EXTRA_TRUSTED_WRITER_OPCODE_ARITY)
        self.assertNotIn(38,EXTRA_TRUSTED_WRITER_OPCODE_ARITY) # IMUL: two destinations

if __name__=="__main__":unittest.main()
