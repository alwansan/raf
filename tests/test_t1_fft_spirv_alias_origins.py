import unittest

from scripts.t1_fft_spirv_alias_origins import analyze


PREFIX = """
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%void = OpTypeVoid
%ft = OpTypeFunction %void
%float = OpTypeFloat 32
%int = OpTypeInt 32 1
%bool = OpTypeBool
%v2f = OpTypeVector %float 2
%v2i = OpTypeVector %int 2
%ptr = OpTypePointer Function %v2f
%scalarptr = OpTypePointer Function %float
%indexptr = OpTypePointer Function %int
%index = OpConstant %int 0
%condition = OpConstantTrue %bool
%zero = OpConstant %float 0
%v0 = OpCompositeConstruct %v2f %zero %zero
%f = OpFunction %void None %ft
%entry = OpLabel
%local = OpVariable %ptr Function
%other = OpVariable %ptr Function
"""

READS = """
%read = OpLoad %v2f %local
%coord = OpBitcast %v2i %read
%fetch0 = OpImageFetch %v2f %source %coord
%fetch1 = OpImageFetch %v2f %butter %coord
%fetch2 = OpImageFetch %v2f %butter %coord
OpReturn
OpFunctionEnd
"""


def lane(program, site=1, axis="x"):
    report = analyze(PREFIX + program, original_layout=True)
    return report["sites"][site]["lanes"][axis]


class AliasPointerOriginTests(unittest.TestCase):
    def test_exact_copy_alias_store_is_labelled_not_trusted(self):
        result = lane(
            "%alias = OpCopyObject %ptr %local\n"
            "OpStore %local %v0\n"
            "OpStore %alias %v0\n" + READS)
        self.assertEqual(result["preload_alias_pointer_forms"], ["exact_pointer_copy"])
        self.assertEqual(result["static_alias_pointer_forms"], {"exact_pointer_copy": 1})
        self.assertFalse(result["full_reaching_definition_proven"])

    def test_indexed_static_component_pointer(self):
        result = lane(
            "%sub = OpAccessChain %scalarptr %local %index\n"
            "OpStore %sub %zero\n" + READS)
        self.assertEqual(result["preload_alias_pointer_forms"], ["indexed_access_static"])

    def test_indexed_dynamic_component_pointer(self):
        result = lane(
            "%idxvar = OpVariable %indexptr Function\n"
            "%dynamic = OpLoad %int %idxvar\n"
            "%sub = OpAccessChain %scalarptr %local %dynamic\n"
            "OpStore %sub %zero\n" + READS)
        self.assertEqual(result["preload_alias_pointer_forms"], ["indexed_access_dynamic"])

    def test_alias_copy_of_indexed_pointer_remains_indexed(self):
        result = lane(
            "%sub = OpAccessChain %scalarptr %local %index\n"
            "%alias = OpCopyObject %scalarptr %sub\n"
            "OpStore %alias %zero\n" + READS)
        self.assertEqual(result["preload_alias_pointer_forms"], ["indexed_access_static"])

    def test_phi_or_select_alias_categories(self):
        program = (
            "%choice = OpSelect %ptr %condition %local %other\n"
            "OpStore %choice %v0\n" + READS)
        self.assertEqual(lane(program)["preload_alias_pointer_forms"], ["select_pointer_merge"])
        program = (
            "%merged = OpPhi %ptr %local %entry %other %entry\n"
            "OpStore %merged %v0\n" + READS)
        self.assertEqual(lane(program)["preload_alias_pointer_forms"], ["phi_pointer_merge"])

    def test_direct_overwrite_removes_preload_alias_uncertainty(self):
        result = lane(
            "%alias = OpCopyObject %ptr %local\n"
            "OpStore %alias %v0\n"
            "OpStore %local %v0\n" + READS)
        self.assertEqual(result["static_alias_store_candidates"], 1)
        self.assertEqual(result["preload_alias_pointer_forms"], [])

    def test_branch_with_alias_possible_keeps_category(self):
        program = (
            "%alias = OpCopyObject %ptr %local\n"
            "OpBranchConditional %condition %left %right\n"
            "%left = OpLabel\nOpStore %alias %v0\nOpBranch %join\n"
            "%right = OpLabel\nOpBranch %join\n"
            "%join = OpLabel\n" + READS)
        result = lane(program)
        self.assertEqual(result["preload_alias_pointer_forms"], ["exact_pointer_copy"])

    def test_loop_backedge_preserves_possible_alias_store(self):
        program = (
            "%alias = OpCopyObject %ptr %local\n"
            "OpBranch %head\n"
            "%head = OpLabel\nOpBranchConditional %condition %body %exit\n"
            "%body = OpLabel\nOpStore %alias %v0\nOpBranch %head\n"
            "%exit = OpLabel\n" + READS)
        self.assertEqual(lane(program)["preload_alias_pointer_forms"], ["exact_pointer_copy"])

    def test_no_alias_has_empty_category(self):
        result = lane("OpStore %local %v0\n" + READS)
        self.assertEqual(result["preload_alias_pointer_forms"], [])
        self.assertEqual(result["static_alias_store_candidates"], 0)

    def test_unexpected_original_roles_fail_closed(self):
        bad = PREFIX.replace("OpDecorate %butter Binding 1", "OpDecorate %butter Binding 3")
        with self.assertRaises(ValueError):
            analyze(bad + "OpStore %local %v0\n" + READS, original_layout=True)

    def test_no_identifier_or_sensitive_constant_in_public_report(self):
        result = analyze(PREFIX + "%alias = OpCopyObject %ptr %local\nOpStore %alias %v0\n" + READS,
                         original_layout=True)
        self.assertNotIn("%", str(result))
        self.assertFalse(result["original_integer_origin_proven"])


if __name__ == "__main__":
    unittest.main()
