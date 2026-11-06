import unittest

from scripts.t1_fft_spirv_reaching_stores import analyze


PREFIX = """
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%void = OpTypeVoid
%funType = OpTypeFunction %void
%float = OpTypeFloat 32
%int = OpTypeInt 32 1
%v2f = OpTypeVector %float 2
%v2i = OpTypeVector %int 2
%ptr = OpTypePointer Function %v2f
%zero = OpConstant %float 0
%one = OpConstant %float 1
%v0 = OpCompositeConstruct %v2f %zero %zero
%v1 = OpCompositeConstruct %v2f %one %zero
%condition = OpConstantTrue %bool
%bool = OpTypeBool
%f = OpFunction %void None %funType
%entry = OpLabel
%local = OpVariable %ptr Function
"""

READS = """
%load = OpLoad %v2f %local
%coord = OpBitcast %v2i %load
%fetch0 = OpImageFetch %v2f %source %coord
%fetch1 = OpImageFetch %v2f %butter %coord
%fetch2 = OpImageFetch %v2f %butter %coord
OpReturn
OpFunctionEnd
"""


def report(code):
    return analyze(PREFIX + code, original_layout=True)


def lane(code, site=1, axis='x'):
    return report(code)['sites'][site]['lanes'][axis]


class ReachingStoresTests(unittest.TestCase):
    def test_single_prior_store_is_the_only_may_reach_candidate(self):
        result = lane('OpStore %local %v0\nOpBranch %read\n%read = OpLabel\n' + READS)
        self.assertEqual(result['static_direct_store_candidates'], 1)
        self.assertEqual(result['reachable_direct_store_candidates'], 1)
        self.assertTrue(result['unique_direct_store_if_no_unmodeled_aliases'])
        self.assertFalse(result['integer_coordinate_origin_proven'])

    def test_independent_conditional_writers_merge(self):
        program = ('OpBranchConditional %condition %left %right\n'
                   '%left = OpLabel\nOpStore %local %v0\nOpBranch %join\n'
                   '%right = OpLabel\nOpStore %local %v1\nOpBranch %join\n'
                   '%join = OpLabel\n' + READS)
        result = lane(program)
        self.assertEqual(result['static_direct_store_candidates'], 2)
        self.assertEqual(result['reachable_direct_store_candidates'], 2)
        self.assertFalse(result['uninitialized_path_possible'])
        self.assertFalse(result['unique_direct_store_if_no_unmodeled_aliases'])

    def test_prior_store_kills_earlier_direct_store(self):
        result = lane('OpStore %local %v0\nOpStore %local %v1\n' + READS)
        self.assertEqual(result['static_direct_store_candidates'], 2)
        self.assertEqual(result['reachable_direct_store_candidates'], 1)
        self.assertTrue(result['unique_direct_store_if_no_unmodeled_aliases'])

    def test_load_before_store_is_uninitialized(self):
        program = ('%load = OpLoad %v2f %local\n%coord = OpBitcast %v2i %load\n'
                   '%fetch0 = OpImageFetch %v2f %source %coord\n'
                   '%fetch1 = OpImageFetch %v2f %butter %coord\n'
                   '%fetch2 = OpImageFetch %v2f %butter %coord\n'
                   'OpStore %local %v0\nOpReturn\nOpFunctionEnd\n')
        result = lane(program)
        self.assertEqual(result['static_direct_store_candidates'], 1)
        self.assertEqual(result['reachable_direct_store_candidates'], 0)
        self.assertTrue(result['uninitialized_path_possible'])

    def test_one_branch_does_not_initialize_load(self):
        program = ('OpBranchConditional %condition %left %right\n'
                   '%left = OpLabel\nOpStore %local %v0\nOpBranch %join\n'
                   '%right = OpLabel\nOpBranch %join\n'
                   '%join = OpLabel\n' + READS)
        result = lane(program)
        self.assertEqual(result['reachable_direct_store_candidates'], 1)
        self.assertTrue(result['uninitialized_path_possible'])
        self.assertFalse(result['unique_direct_store_if_no_unmodeled_aliases'])

    def test_unreachable_store_not_counted_as_reaching(self):
        program = ('OpStore %local %v0\nOpBranch %read\n'
                   '%dead = OpLabel\nOpStore %local %v1\nOpReturn\n'
                   '%read = OpLabel\n' + READS)
        result = lane(program)
        self.assertEqual(result['static_direct_store_candidates'], 2)
        self.assertEqual(result['reachable_direct_store_candidates'], 1)
        self.assertTrue(result['unique_direct_store_if_no_unmodeled_aliases'])

    def test_loop_backedge_store_keeps_both_candidates(self):
        program = ('OpStore %local %v0\nOpBranch %header\n'
                   '%header = OpLabel\n'
                   'OpBranchConditional %condition %body %read\n'
                   '%body = OpLabel\nOpStore %local %v1\nOpBranch %header\n'
                   '%read = OpLabel\n' + READS)
        result = lane(program)
        self.assertEqual(result['reachable_direct_store_candidates'], 2)
        self.assertFalse(result['unique_direct_store_if_no_unmodeled_aliases'])

    def test_alias_store_is_unknown_side_effect(self):
        program = ('OpStore %local %v0\n'
                   '%alias = OpCopyObject %ptr %local\n'
                   'OpStore %alias %v1\n' + READS)
        result = lane(program)
        self.assertEqual(result['reachable_direct_store_candidates'], 1)
        self.assertTrue(result['unknown_alias_or_side_effect_path'])
        self.assertFalse(result['unique_direct_store_if_no_unmodeled_aliases'])

    def test_function_call_with_local_pointer_is_unknown(self):
        program = ('OpStore %local %v0\n'
                   '%call = OpFunctionCall %void %helper %local\n' + READS)
        result = lane(program)
        self.assertTrue(result['unknown_alias_or_side_effect_path'])
        self.assertFalse(result['unique_direct_store_if_no_unmodeled_aliases'])

    def test_wrong_branch_target_rejected(self):
        with self.assertRaises(ValueError):
            report('OpBranch %missing\n%read = OpLabel\n' + READS)

    def test_no_private_ssa_identifiers_in_output(self):
        result = report('OpStore %local %v0\n' + READS)
        self.assertEqual([s['role'] for s in result['sites']], ['source', 'butterfly', 'butterfly'])
        self.assertNotIn('%', str(result))
        self.assertFalse(result['original_integer_origin_proven'])

    def test_missing_block_terminator_rejected(self):
        with self.assertRaises(ValueError):
            report('OpStore %local %v0\n%read = OpLabel\n' + READS)

    def test_wrong_original_fetch_roles_rejected(self):
        bad = PREFIX.replace('OpDecorate %butter Binding 1', 'OpDecorate %butter Binding 2')
        with self.assertRaises(ValueError):
            analyze(bad + 'OpStore %local %v0\n' + READS, original_layout=True)


if __name__ == '__main__':
    unittest.main()
