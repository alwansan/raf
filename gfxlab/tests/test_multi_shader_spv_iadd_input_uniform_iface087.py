"""GFX087 source-free safe SPIR-V interface decoration controls."""
import json
import unittest
from gfxlab.tools.multi_shader_spv_iadd_input_uniform_iface087 import authenticated_spv_CB_index_iadd_load_interfaces087
from gfxlab.tests.test_multi_shader_spv_index_local_store_value077 import dis,idxread,AUTH

def counts(lines, auth=AUTH):
    return authenticated_spv_CB_index_iadd_load_interfaces087(dis(lines),auth)

def sample(interface, lhs="%90", rhs="%91"):
    return counts([*interface,
      f"%80 = OpIAdd %1 {lhs} {rhs}",
      "%81 = OpBitcast %1 %80",
      "%71 = OpInBoundsAccessChain %ptr %5 %3",
      "%72 = OpInBoundsAccessChain %ptr %5 %3",
      "OpStore %71 %81",
      "%66 = OpLoad %1 %72",
      "%70 = OpConstant %1 3",
      "%40 = OpIMul %1 %66 %70",
      "%41 = OpBitcast %1 %40",
      "%7 = OpInBoundsAccessChain %ptr %5 %3",
      "%8 = OpInBoundsAccessChain %ptr %5 %3",
      "OpStore %7 %41",*idxread("%8")])

class TestGFX087InputUniformSourceInterface(unittest.TestCase):
    def baseline(self,offset=True):
        return [
          "%101 = OpTypePointer Input %1",
          "%102 = OpTypeStruct %1",
          "%103 = OpTypePointer Uniform %102",
          "OpDecorate %104 Location 2",
          "OpDecorate %105 Binding 7",
          "OpDecorate %105 DescriptorSet 0",
          "OpDecorate %102 Block",
          *(["OpMemberDecorate %102 0 Offset 0"] if offset else []),
          "%104 = OpVariable %101 Input",
          "%105 = OpVariable %103 Uniform",
          "%90 = OpLoad %1 %104",
          "%106 = OpAccessChain %ptr %105 %2",
          "%91 = OpLoad %1 %106",
        ]
    def test_full_input_location_and_uniform_block_selected_member_offset(self):
        d=sample(self.baseline())
        self.assertEqual(d["SPV_iadd_OpLoad_interface_lhs_input_location_kind_location_only"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_lhs_ptr_index_shape_direct"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_binding_kind_binding_and_set"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_block_kind_Block"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_member_offset_kind_selected_member_has_offset"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_ptr_index_shape_literal_indices"],1)
        self.assertFalse(d["SPV_Uniform_Binding_and_Offset_prove_Material_CB_byte_parity"])
        self.assertFalse(d["SPV_Input_Location_proves_original_vertex_attribute_interpolation"])

    def test_selected_member_without_offset_not_upgraded(self):
        d=sample(self.baseline(offset=False))
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_member_offset_kind_selected_member_without_proven_offset"],1)

    def test_input_builtin_conflict_never_counts_as_location_only(self):
        lines=self.baseline()
        lines.insert(4,"OpDecorate %104 BuiltIn Position")
        d=sample(lines)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_lhs_input_location_kind_location_and_builtin_conflict"],1)
        self.assertEqual(d.get("SPV_iadd_OpLoad_interface_lhs_input_location_kind_location_only",0),0)

    def test_uniform_binding_without_set_is_not_binding_and_set(self):
        lines=[x for x in self.baseline() if x!="OpDecorate %105 DescriptorSet 0"]
        d=sample(lines)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_binding_kind_binding_only"],1)

    def test_dynamic_Uniform_index_rejects_selected_member_claim(self):
        lines=self.baseline()
        lines=[x.replace("%106 = OpAccessChain %ptr %105 %2",
                         "%106 = OpAccessChain %ptr %105 %109") for x in lines]
        lines.insert(-1,"%109 = OpIAdd %1 %3 %4")
        d=sample(lines)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_ptr_index_shape_dynamic_indices"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_member_offset_kind_unverified_dynamic_index"],1)

    def test_decorations_on_different_variable_not_applied(self):
        lines=[x for x in self.baseline()
               if x not in ("OpDecorate %104 Location 2",
                            "OpDecorate %105 Binding 7",
                            "OpDecorate %105 DescriptorSet 0")]
        lines.extend(["OpDecorate %107 Location 2",
                      "OpDecorate %108 Binding 7",
                      "OpDecorate %108 DescriptorSet 0"])
        d=sample(lines)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_lhs_input_location_kind_no_direct_location_or_builtin"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_binding_kind_no_direct_binding_or_set"],1)

    def test_untyped_pointers_do_not_prove_material_block(self):
        d=sample(["%90 = OpLoad %1 %110",
                  "%91 = OpLoad %1 %111"])
        self.assertEqual(d["SPV_iadd_OpLoad_interface_lhs_ptr_index_shape_unresolved_pointer"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_block_kind_unresolved"],1)
        self.assertFalse(d["SPV_interface_decorations_prove_original_DXBC_semantics"])

    def test_incomplete_OpTypePointer_is_fail_closed(self):
        d=sample([
          "%105 = OpVariable %112 Uniform",
          "%104 = OpVariable %107Ptr Input",
          "OpDecorate %104 Location 4",
          "OpDecorate %105 Binding 9",
          "%90 = OpLoad %1 %104",
          "%91 = OpLoad %1 %105",
        ])
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_block_kind_unverified_pointer_type"],1)
        self.assertEqual(d["SPV_iadd_OpLoad_interface_rhs_uniform_member_offset_kind_unverified_member_path"],1)

    def test_cannot_leak_exact_values_or_private_ssa_ids_to_counts(self):
        d=sample(self.baseline())
        txt=json.dumps(d)
        for raw in ("%104","%105","%102","%106","%90","%91"):
            self.assertNotIn(raw,txt)
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])

if __name__=="__main__":unittest.main()
