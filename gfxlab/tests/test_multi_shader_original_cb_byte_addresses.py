"""GFX053 synthetic source-free UBO member byte-address and SPV use guards."""
import unittest
from gfxlab.tools.multi_shader_original_cb_byte_addresses import (
    private_authenticated_ubo_layouts,spv_used_literal_byte_addresses,
    compare_source_to_translated_byte_addresses)

def real_spv():
    return b"""
OpName %10 "cb3_4"
OpDecorate %10 DescriptorSet 0
OpDecorate %10 Binding 3
%1 = OpTypeInt 32 0
%2 = OpConstant %1 0
%3 = OpConstant %1 2
%10 = OpVariable %123 Uniform
%20 = OpAccessChain %124 %10 %2 %3
%21 = OpLoad %125 %20
"""
def reflect(member=None):
    return {"ubos":[{"name":"Something","type":"_x","set":0,"binding":3,"block_size":64}],
      "types":{"_x":{"members":[member or {"type":"vec4","offset":0,"array":[4],
                                      "array_stride":16,"array_size_is_literal":[True]}]}}}

class TestGFX053ByteAddresses(unittest.TestCase):
    def test_authentic_global_source_slot_and_reflected_stride_address(self):
        roots,c=private_authenticated_ubo_layouts(real_spv(),{3:4},reflect())
        self.assertEqual(c["proven_name_binding_size_CB_globals"],1)
        self.assertEqual(c["UBO_globals_strict_single_vec4_array_member_layout"],1)
        addresses,usage=spv_used_literal_byte_addresses(real_spv(),roots)
        self.assertEqual(addresses,{3:{32}})
        self.assertEqual(usage["SPV_pointer_loads_from_supported_access_chains"],1)
        delta=compare_source_to_translated_byte_addresses({3:{2}},addresses)
        self.assertEqual(delta["source_subset_byte_addresses_matched_in_translated_SPV"],1)
        self.assertEqual(delta["source_subset_byte_addresses_not_found_in_translated_SPV"],0)
        self.assertFalse(delta["source_to_translated_address_overlap_is_original_Material_member_semantics"])

    def test_wrong_source_binding_or_name_is_not_accepted(self):
        d=real_spv().replace(b'cb3_4',b'cb5_4')
        roots,c=private_authenticated_ubo_layouts(d,{3:4},reflect())
        self.assertEqual(roots,{})
        self.assertEqual(c["proven_name_binding_size_CB_globals"],0)

    def test_stride_or_offset_wrong_never_derived_from_block_size(self):
        for member in (
            {"type":"vec4","offset":0,"array":[4],"array_stride":32},
            {"type":"vec4","offset":16,"array":[4],"array_stride":16},
            {"type":"vec4","offset":0,"array":[3],"array_stride":16},
            {"type":"float","offset":0,"array":[4],"array_stride":16},
            {"type":"vec4","offset":0,"array":[4]},
        ):
            roots,c=private_authenticated_ubo_layouts(real_spv(),{3:4},reflect(member))
            self.assertEqual(roots,{})
            self.assertEqual(c["UBO_globals_without_supported_layout"],1)

    def test_two_member_block_not_falsely_mapped(self):
        r=reflect()
        r["types"]["_x"]["members"].append({"type":"vec4","offset":16,"array":[3],"array_stride":16})
        roots,c=private_authenticated_ubo_layouts(real_spv(),{3:4},r)
        self.assertEqual(len(roots),0)
        self.assertEqual(c["UBO_globals_with_multiple_reflected_members"],1)

    def test_dynamic_access_is_unknown_and_unloaded_pointer_not_proof(self):
        src=real_spv().replace(b"%20 = OpAccessChain %124 %10 %2 %3",
                  b"%20 = OpAccessChain %124 %10 %2 %dynamic")
        root,_=private_authenticated_ubo_layouts(src,{3:4},reflect())
        addr,counts=spv_used_literal_byte_addresses(src,root)
        self.assertEqual(addr,{})
        self.assertEqual(counts["SPV_access_chains_dynamic_or_unsupported"],1)
        src=real_spv().replace(b"%21 = OpLoad %125 %20",b"")
        addr,_=spv_used_literal_byte_addresses(src,root)
        self.assertEqual(addr,{})

    def test_literal_outside_reflected_extent_is_not_used(self):
        src=real_spv().replace(b"%3 = OpConstant %1 2",b"%3 = OpConstant %1 8")
        root,_=private_authenticated_ubo_layouts(src,{3:4},reflect())
        got,c=spv_used_literal_byte_addresses(src,root)
        self.assertEqual(got,{})
        self.assertEqual(c["SPV_access_chains_literal_index_out_of_bounds"],1)

    def test_private_comparison_subset_not_full_opcode_parity(self):
        c=compare_source_to_translated_byte_addresses({3:{1,2}},{3:{16,32,48}})
        self.assertEqual(c["source_subset_byte_addresses_matched_in_translated_SPV"],2)
        self.assertEqual(c["translated_SPV_byte_addresses_not_in_covered_DXBC_opcode_subset"],1)
        self.assertFalse(c["private_CB_offsets_or_registers_exported"])

    def test_duplicate_real_ubo_binding_rejected(self):
        d=real_spv()+b"\nOpDecorate %10 Binding 3\n"
        with self.assertRaisesRegex(ValueError,"DUPLICATE_RESOURCE_DECORATION"):
            private_authenticated_ubo_layouts(d,{3:4},reflect())

if __name__=="__main__":unittest.main()
