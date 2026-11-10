"""GFX068 original-free synthetic nearest temp-writer candidate, fail-closed tests."""
import unittest
from gfxlab.tools.multi_shader_original_cb_temp_writer068 import (
    temp_component_source_origin,supported_temp_dest_written_components,
    original_relative_temp_nearest_writer_census
)
from gfxlab.tools.multi_shader_original_cb_relative_expression067 import decode_original_operand_tree
from gfxlab.tests.test_multi_shader_original_dynamic_cb_taxonomy import arg,shdr

def temp(reg,component=0,dest=False):
    a=arg(0,(reg,),(0,))
    if dest:a[0] |= (1<<component)<<4
    else:a[0] |= (2<<2)|(component<<4)
    return a

def cb_relative(temp_reg=5,component=0,base=3,b=2):
    # two-index CB: first b literal, second immediate32-plus-relative.
    token=(8<<12)|(2<<20)|2|(3<<25)
    return [token,b,base]+temp(temp_reg,component)

def instruction(op,items):
    body=[w for item in items for w in item]
    return [((len(body)+1)<<24)|op]+body

def moving(dst,src):
    return instruction(54,[dst,src])

def study(ops):
    return original_relative_temp_nearest_writer_census(shdr(ops),{2:8})

class TestGFX068OriginalTempWriter(unittest.TestCase):
    def test_valid_synthetic_relative_temp_index_has_same_run_nearest_writer_candidate(self):
        writer=moving(temp(5,0,True),temp(6))
        reader=moving(temp(0,0,True),cb_relative(5,0))
        c=study([writer,reader])
        self.assertEqual(c["original_CB_true_relative_vec_index_occurrences"],1)
        self.assertEqual(c["relative_source_temp_selected_component_syntax_valid"],1)
        self.assertEqual(c["relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run"],1)
        self.assertEqual(c["candidate_nearest_writer_gap_one_instruction"],1)
        self.assertEqual(c["candidate_nearest_writer_original_opcode_54"],1)

    def test_different_component_not_false_nearest_writer(self):
        writer=moving(temp(5,1,True),temp(6))
        reader=moving(temp(0,0,True),cb_relative(5,0))
        c=study([writer,reader])
        self.assertEqual(c.get("relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run",0),0)
        self.assertEqual(c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"],1)

    def test_unsupported_opcode_is_strict_barrier_not_cfg_provenance(self):
        writer=moving(temp(5,0,True),temp(6))
        barrier=[(2<<24)|210,0]
        reader=moving(temp(0,0,True),cb_relative(5,0))
        c=study([writer,barrier,reader])
        self.assertEqual(c.get("relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run",0),0)
        self.assertEqual(c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"],1)
        self.assertGreaterEqual(c["unsupported_opcode_barriers_invalidating_all_live_writer_candidates"],1)

    def test_same_instruction_dest_cannot_supply_own_source(self):
        op=moving(temp(5,0,True),cb_relative(5,0))
        c=study([op])
        self.assertEqual(c.get("relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run",0),0)
        self.assertEqual(c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"],1)

    def test_more_recent_writer_replaces_prior_writer_only_for_same_component(self):
        a=moving(temp(5,0,True),temp(6))
        b=moving(temp(5,1,True),temp(6))
        reader=moving(temp(0,0,True),cb_relative(5,0))
        c=study([a,b,reader])
        self.assertEqual(c["relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run"],1)
        self.assertEqual(c["candidate_nearest_writer_gap_two_to_four"],1)

    def test_source_temporary_origin_requires_actual_select_one_component(self):
        selected,at=decode_original_operand_tree(temp(5,2),0,len(temp(5,2)))
        self.assertEqual(at,len(temp(5,2)))
        self.assertEqual(temp_component_source_origin(selected),(5,2))
        not_selected,_=decode_original_operand_tree(arg(0,(5,),(0,)),0,len(arg(0,(5,),(0,))))
        self.assertIsNone(temp_component_source_origin(not_selected))

    def test_writer_requires_explicit_nonempty_component_mask(self):
        val=temp(9,3,True)
        node,_=decode_original_operand_tree(val,0,len(val))
        self.assertEqual(supported_temp_dest_written_components(node),(9,(3,)))
        no_mask=arg(0,(9,),(0,))
        other,_=decode_original_operand_tree(no_mask,0,len(no_mask))
        self.assertIsNone(supported_temp_dest_written_components(other))

    def test_duplicate_relative_sources_count_as_uses_not_unique_producers(self):
        w=moving(temp(5,0,True),temp(6))
        r=moving(temp(0,0,True),cb_relative(5,0))
        c=study([w,r,r])
        self.assertEqual(c["original_CB_true_relative_vec_index_occurrences"],2)
        self.assertEqual(c["relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run"],2)

    def test_missing_writer_must_remain_unproven(self):
        c=study([moving(temp(0,0,True),cb_relative(5,0))])
        self.assertEqual(c.get("relative_source_temp_component_nearest_prior_writer_in_supported_ALU_run",0),0)
        self.assertEqual(c["relative_source_temp_component_with_no_writer_in_same_supported_ALU_run"],1)

if __name__=="__main__":unittest.main()
