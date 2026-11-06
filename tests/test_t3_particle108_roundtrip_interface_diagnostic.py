"""No original Raft data: strict structural VS/FS roundtrip drift controls."""
import unittest

from scripts.t3_particle108_roundtrip_interface_diagnostic import (
    classify_pair, COUNTERS,
)

def stage(inputs=(),outputs=()):
    return {
        "inputs":[{"location":loc,"type":kind} for loc,kind in inputs],
        "outputs":[{"location":loc,"type":kind} for loc,kind in outputs],
        "resource_slots":{},
    }

def original_record(*,reg=0,mask=15,used=15,system=0):
    return {"system_value":system,"register":reg,"mask":mask,"used_mask":used}

class OriginalParticle108RoundtripTests(unittest.TestCase):
    def check(self,sv,sf,rv,rf,signature=None):
        return classify_pair(sv,sf,rv,rf,
                             {"input":[] if signature is None else signature})

    def test_unchanged_source_and_roundtrip_compatible(self):
        vs=stage(outputs=[(0,"vec4")])
        fs=stage(inputs=[(0,"vec4")])
        row=self.check(vs,fs,vs,fs,[original_record()])
        self.assertEqual(row["original_pairs_valid"],1)
        self.assertEqual(row["roundtrip_pairs_valid"],1)
        self.assertEqual(row["pairs_with_no_interface_side_change"],1)
        self.assertEqual(row["original_compiled_active_fragment_inputs_source_numeric_located"],1)
        self.assertEqual(set(row),set(COUNTERS))

    def test_roundtrip_fragment_input_location_moved_while_vertex_stays(self):
        sv=stage(outputs=[(0,"vec3")]); sf=stage(inputs=[(0,"vec3")])
        rv=sv; rf=stage(inputs=[(2,"vec3")])
        row=self.check(sv,sf,rv,rf,[original_record()])
        self.assertEqual(row["roundtrip_fragment_missing_vertex_location_records"],1)
        self.assertEqual(row["roundtrip_fragment_input_added_locations_vs_source"],1)
        self.assertEqual(row["roundtrip_fragment_input_removed_locations_vs_source"],1)
        self.assertEqual(row["pairs_with_only_fragment_side_change"],1)
        self.assertEqual(row["roundtrip_pairs_valid"],0)

    def test_roundtrip_vertex_output_location_moved_while_fragment_stays(self):
        sv=stage(outputs=[(0,"vec4")]); sf=stage(inputs=[(0,"vec4")])
        rv=stage(outputs=[(3,"vec4")]); rf=sf
        row=self.check(sv,sf,rv,rf)
        self.assertEqual(row["roundtrip_fragment_missing_vertex_location_records"],1)
        self.assertEqual(row["roundtrip_vertex_output_removed_locations_vs_source"],1)
        self.assertEqual(row["pairs_with_only_vertex_side_change"],1)

    def test_fragment_same_location_wrong_component_type(self):
        sv=stage(outputs=[(0,"vec4")]); sf=stage(inputs=[(0,"vec4")])
        rf=stage(inputs=[(0,"vec3")])
        row=self.check(sv,sf,sv,rf)
        self.assertEqual(row["roundtrip_fragment_same_location_type_mismatch_records"],1)
        self.assertEqual(row["roundtrip_pairs_with_same_location_type_mismatch"],1)
        self.assertEqual(row["roundtrip_fragment_missing_vertex_location_records"],0)

    def test_both_sides_relocated_together_remains_roundtrip_compatible(self):
        sv=stage(outputs=[(0,"vec4")]); sf=stage(inputs=[(0,"vec4")])
        rv=stage(outputs=[(2,"vec4")]); rf=stage(inputs=[(2,"vec4")])
        row=self.check(sv,sf,rv,rf)
        self.assertEqual(row["roundtrip_pairs_valid"],1)
        self.assertEqual(row["pairs_with_both_interface_sides_changed"],1)

    def test_source_mismatch_fails_closed(self):
        vs=stage(outputs=[(0,"vec4")])
        fs=stage(inputs=[(2,"vec4")])
        with self.assertRaisesRegex(ValueError,"source_spirv_pair_incompatibility"):
            self.check(vs,fs,vs,fs)

    def test_original_compiled_unread_input_does_not_count_active(self):
        sv=stage(outputs=[(0,"vec2")]); sf=stage(inputs=[])
        row=self.check(sv,sf,sv,sf,[original_record(reg=0,mask=3,used=0)])
        self.assertEqual(row["original_compiled_unread_fragment_inputs_source_numeric_absent"],1)
        self.assertEqual(row["original_fragment_compiled_used_mask_zero"],1)

    def test_missing_active_numeric_input_cannot_be_called_present(self):
        sv=stage(outputs=[(0,"vec4")]); sf=stage(inputs=[])
        row=self.check(sv,sf,sv,sf,[original_record(reg=9,used=3)])
        self.assertEqual(row["original_compiled_active_fragment_inputs_source_numeric_absent"],1)
        self.assertEqual(row["original_compiled_active_fragment_inputs_roundtrip_same_numeric_location"],0)

    def test_outside_declared_DXBC_read_mask_rejected(self):
        vs=stage(); fs=stage()
        with self.assertRaisesRegex(ValueError,"invalid_original_fragment_used_mask"):
            self.check(vs,fs,vs,fs,[original_record(mask=3,used=8)])

    def test_boolean_register_and_duplicate_spirv_location_rejected(self):
        sv=stage(); sf=stage()
        with self.assertRaisesRegex(ValueError,"invalid_original_fragment_used_mask_record"):
            self.check(sv,sf,sv,sf,[original_record(reg=True)])
        duplicate=stage(outputs=[(0,"vec4"),(0,"vec3")])
        with self.assertRaisesRegex(ValueError,"duplicate_private_SPIRV_IO_location"):
            self.check(duplicate,sf,duplicate,sf)

    def test_vertex_output_narrowing_consumed_fragment_expects_source_width(self):
        srcv=stage(outputs=[(0,"vec4")])
        srcf=stage(inputs=[(0,"vec4")])
        rtv=stage(outputs=[(0,"vec3")])
        row=self.check(srcv,srcf,rtv,srcf)
        self.assertEqual(row["vertex_changed_output_reflection_type_width_narrowing"],1)
        self.assertEqual(row["vertex_changed_output_consumed_width_narrowing"],1)
        self.assertEqual(row["vertex_changed_output_unconsumed_width_narrowing"],0)
        self.assertEqual(row["vertex_changed_output_locations_consumed_by_fragment"],1)
        self.assertEqual(row["vertex_changed_output_consumed_fragment_type_equal_source"],1)
        self.assertEqual(row["roundtrip_fragment_same_location_type_mismatch_records"],1)

    def test_vertex_output_widening_unused_by_roundtrip_fragment(self):
        srcv=stage(outputs=[(0,"vec2"),(3,"vec2")])
        srcf=stage(inputs=[(0,"vec2")])
        rtv=stage(outputs=[(0,"vec2"),(3,"vec4")])
        row=self.check(srcv,srcf,rtv,srcf)
        self.assertEqual(row["vertex_changed_output_reflection_type_width_widening"],1)
        self.assertEqual(row["vertex_changed_output_unconsumed_width_widening"],1)
        self.assertEqual(row["vertex_changed_output_consumed_width_widening"],0)
        self.assertEqual(row["vertex_changed_output_locations_not_consumed_by_fragment"],1)
        self.assertEqual(row["roundtrip_pairs_valid"],1)

    def test_vertex_output_same_width_base_type_changed(self):
        srcv=stage(outputs=[(0,"ivec3")])
        srcf=stage(inputs=[(0,"ivec3")])
        rtv=stage(outputs=[(0,"uvec3")])
        row=self.check(srcv,srcf,rtv,srcf)
        self.assertEqual(row["vertex_changed_output_reflection_type_same_width_base_kind_changed"],1)
        self.assertEqual(row["vertex_changed_output_consumed_same_width_base_kind_changed"],1)

    def test_vertex_output_unsupported_numeric_type_is_counted_not_assumed(self):
        srcv=stage(outputs=[(0,"dvec4")])
        srcf=stage(inputs=[(0,"dvec4")])
        rtv=stage(outputs=[(0,"vec4")])
        row=self.check(srcv,srcf,rtv,srcf)
        self.assertEqual(row["vertex_changed_output_reflection_type_unsupported"],1)
        self.assertEqual(row["vertex_changed_output_consumed_unsupported"],1)
        self.assertEqual(row["vertex_changed_output_reflection_type_width_narrowing"],0)

    def test_consumed_vertex_output_width_widening_is_separately_counted(self):
        sv=stage(outputs=[(0,"vec2")])
        sf=stage(inputs=[(0,"vec2")])
        rv=stage(outputs=[(0,"vec4")])
        row=self.check(sv,sf,rv,sf)
        self.assertEqual(row["vertex_changed_output_consumed_width_widening"],1)
        self.assertEqual(row["vertex_changed_output_unconsumed_width_widening"],0)
        self.assertEqual(row["roundtrip_fragment_same_location_type_mismatch_records"],1)
        self.assertEqual(row["vertex_changed_output_consumed_fragment_type_equal_source"],1)

    def test_unconsumed_vertex_output_width_narrowing_does_not_break_link(self):
        sv=stage(outputs=[(0,"vec2"),(3,"vec4")])
        sf=stage(inputs=[(0,"vec2")])
        rv=stage(outputs=[(0,"vec2"),(3,"vec2")])
        row=self.check(sv,sf,rv,sf)
        self.assertEqual(row["vertex_changed_output_unconsumed_width_narrowing"],1)
        self.assertEqual(row["vertex_changed_output_consumed_width_narrowing"],0)
        self.assertEqual(row["roundtrip_pairs_valid"],1)

    def test_mixed_consumed_and_unconsumed_cross_tab_conserves_counts(self):
        sv=stage(outputs=[(0,"vec4"),(3,"vec2")])
        sf=stage(inputs=[(0,"vec4")])
        rv=stage(outputs=[(0,"vec3"),(3,"vec4")])
        row=self.check(sv,sf,rv,sf)
        self.assertEqual(row["vertex_same_location_type_changes"],2)
        self.assertEqual(row["vertex_changed_output_consumed_width_narrowing"],1)
        self.assertEqual(row["vertex_changed_output_unconsumed_width_widening"],1)
        self.assertEqual(sum(row["vertex_changed_output_"+suffix] for suffix in (
            "consumed_width_narrowing","consumed_width_widening",
            "consumed_same_width_base_kind_changed","consumed_unsupported",
            "unconsumed_width_narrowing","unconsumed_width_widening",
            "unconsumed_same_width_base_kind_changed","unconsumed_unsupported")),2)

    def test_private_identifiers_not_leaked_in_counts(self):
        sv=stage(outputs=[(0,"PRIVATE_SHADER_TYPE")])
        sf=stage(inputs=[(0,"PRIVATE_SHADER_TYPE")])
        row=self.check(sv,sf,sv,sf)
        self.assertNotIn("PRIVATE_SHADER_TYPE",str(row))

if __name__=="__main__":
    unittest.main()
