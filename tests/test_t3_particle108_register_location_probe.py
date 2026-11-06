#!/usr/bin/env python3
"""Source-free regression fixtures for private original DXBC->SPIR-V hypothesis."""
import unittest
from scripts.t3_particle108_register_location_probe import classify_stage,classify_stage_roles,_type

def row(reg=0,mask=15,kind=3,system=0):
    return {"register":reg,"mask":mask,"type":kind,"system_value":system}

class OriginalRegisterLocationTests(unittest.TestCase):
    def test_float_and_uint_one_to_one_numeric_candidates_not_semantic_proof(self):
        result=classify_stage(
            {"input":[row()],"output":[row(reg=1,mask=7,kind=1)]},
            {"inputs":[{"location":0,"type":"vec4"}],
             "outputs":[{"location":1,"type":"uvec3"}]})
        self.assertEqual(result["unique_numeric_type_width_candidates"],2)
        self.assertEqual(result["all_user_records_unique_numeric_candidates"],1)

    def test_two_semantics_same_register_ambiguous_even_with_type(self):
        result=classify_stage(
            {"input":[row(mask=3),row(mask=12)],"output":[]},
            {"inputs":[{"location":0,"type":"vec4"}],"outputs":[]})
        self.assertEqual(result["original_records_sharing_register"],2)
        self.assertEqual(result["unique_numeric_type_width_candidates"],0)

    def test_integer_type_mismatch_blocks_candidate(self):
        r=classify_stage({"input":[row(kind=2)],"output":[]},
                         {"inputs":[{"location":0,"type":"vec4"}],"outputs":[]})
        self.assertEqual(r["type_class_mismatches"],1)
        self.assertEqual(r["unique_numeric_type_width_candidates"],0)

    def test_vector_lane_shortfall_blocks_candidate(self):
        r=classify_stage({"input":[row(mask=15)],"output":[]},
                         {"inputs":[{"location":0,"type":"vec2"}],"outputs":[]})
        self.assertEqual(r["component_width_shortfalls"],1)

    def test_unknown_compiler_reflected_type_rejected_as_match(self):
        r=classify_stage({"input":[row()],"output":[]},
                         {"inputs":[{"location":0,"type":"dvec4"}],"outputs":[]})
        self.assertEqual(r["unsupported_spirv_type_class"],1)

    def test_location_move_is_not_identity(self):
        r=classify_stage({"input":[row(reg=4)],"output":[]},
                         {"inputs":[{"location":2,"type":"vec4"}],"outputs":[]})
        self.assertEqual(r["missing_numeric_register_locations"],1)
        self.assertEqual(r["extra_spirv_locations"],1)

    def test_duplicate_source_SPIRV_Location_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"duplicate_SPIRV_location"):
            classify_stage({"input":[],"output":[]},
                           {"inputs":[{"location":0,"type":"vec4"},
                                      {"location":0,"type":"vec2"}],"outputs":[]})

    def test_user_filter_handles_DXBC_systemvalue_special_register(self):
        r=classify_stage({"input":[row(reg=0xffffffff,system=1)],"output":[]},
                         {"inputs":[],"outputs":[]})
        self.assertEqual(r["original_user_records"],0)
        self.assertEqual(r["missing_numeric_register_locations"],0)

    def test_bools_are_not_integer_Locations(self):
        with self.assertRaises(ValueError):
            classify_stage({"input":[],"output":[]},
                           {"inputs":[{"location":True,"type":"vec4"}],"outputs":[]})

    def test_stage_side_split_finds_only_output_missing_register(self):
        result=classify_stage_roles(
            {'input':[row(reg=0)],'output':[row(reg=3)]},
            {'inputs':[{'location':0,'type':'vec4'}],'outputs':[]})
        self.assertEqual(result['inputs']['missing_numeric_register_locations'],0)
        self.assertEqual(result['outputs']['missing_numeric_register_locations'],1)
        self.assertEqual(result['inputs']['numerically_matching_register_records'],1)
        self.assertEqual(result['outputs']['numerically_matching_register_records'],0)

    def test_source_systemvalue_and_empty_output_do_not_fabricate_missing(self):
        result=classify_stage_roles(
            {'input':[row(reg=0xffffffff,system=1)],'output':[]},
            {'inputs':[],'outputs':[]})
        self.assertEqual(result['inputs']['original_user_records'],0)
        self.assertEqual(result['outputs']['missing_numeric_register_locations'],0)

    def test_unknown_reflection_type_or_spoofed_register_rejected(self):
        with self.assertRaises(ValueError):
            classify_stage({"input":[row(reg=-1)],"output":[]},
                           {"inputs":[],"outputs":[]})
        with self.assertRaises(ValueError):
            _type("x"*25)

if __name__=="__main__":
    unittest.main()
