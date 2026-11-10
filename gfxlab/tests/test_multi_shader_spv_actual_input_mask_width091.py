"""GFX091 source-free SPV Input scalar/vector widths vs source ISGN mask popcount."""
import json,unittest
from gfxlab.tools.multi_shader_spv_actual_input_mask_width091 import authenticated_spv_CB_index_actual_input_component_width091
from gfxlab.tests.test_multi_shader_spv_dxbc_input_ubo_overlap088 import body,source_input,AUTH,dis
from gfxlab.tests.test_multi_shader_spv_dxbc_input_signature089 import fake_container

def audit(mask=1,dxbc=None,lines=None):
    auth=dict(AUTH);auth["%105"]=(2,0,16,8)
    return authenticated_spv_CB_index_actual_input_component_width091(
        dis(body() if lines is None else lines),auth,source_input(),{2:8},
        fake_container(mask=mask) if dxbc is None else dxbc,"vertex")

class TestGFX091MaskWidthAndComponent(unittest.TestCase):
    def test_ISGN_one_component_and_SPV_scalar32_width_agree_shape_only(self):
        d=audit(mask=1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_ISGN_component_mask_popcount_mask_components_1"],1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_mask_vs_SPV_pointee_width_mask_popcount_equals_SPV_width_candidate"],1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_SPV_Component_decor_presence_no_explicit_Component"],1)
        self.assertFalse(d["GFX091_source_mask_popcount_equals_target_width_proves_component_swizzle"])
    def test_ISGN_two_components_and_SPV_scalar32_width_differ(self):
        d=audit(mask=3)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_ISGN_component_mask_popcount_mask_components_2"],1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_mask_vs_SPV_pointee_width_mask_popcount_differs_SPV_width"],1)
    def test_ISGN_four_components_not_assumed_one_scalar(self):
        d=audit(mask=15)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_ISGN_component_mask_popcount_mask_components_4"],1)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_mask_vs_SPV_pointee_width_mask_popcount_differs_SPV_width"],1)
    def test_missing_source_signature_returns_unknown_not_equals(self):
        d=audit(dxbc=b"DXBCinvalid")
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_mask_vs_SPV_pointee_width_no_unique_source_mask"],1)
    def test_explicit_valid_Component_one_only_presence_not_exact_lane(self):
        d=audit(lines=["OpDecorate %104 Component 2",*body()])
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_SPV_Component_decor_presence_one_valid_Component"],1)
        self.assertFalse(d["GFX091_SPV_Component_decoration_presence_proves_DXBC_register_lane"])
    def test_two_conflicting_Component_values_fail_closed(self):
        d=audit(lines=["OpDecorate %104 Component 0","OpDecorate %104 Component 2",*body()])
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_SPV_Component_decor_presence_ambiguous_or_invalid_Component"],1)
    def test_invalid_target_pointer_type_unknown(self):
        src=[x.replace("%101 = OpTypePointer Input %1","%101 = OpTypePointer Input %unknown")
             for x in body()]
        d=audit(mask=1,lines=src)
        self.assertEqual(d["SPV_actual_OpIAdd_input_LHS_source_mask_vs_SPV_pointee_width_unverified_target_width"],1)
    def test_no_raw_isgn_mask_value_or_original_input_register_in_report(self):
        d=audit(mask=1)
        txt=json.dumps(d)
        for private in ("%104","%90","TEXCOORD","%105"):self.assertNotIn(private,txt)
        self.assertFalse(d["originalShaderRestored"])
        self.assertFalse(d["phase_closed"])

if __name__=="__main__":unittest.main()
