"""Adversarial source-free guards for original Foam Shader.Find result flow."""
import unittest
from scripts.t2_foam_shaderfind_return_report import (
    KINDS, MATERIAL_KINDS, MATERIAL_NUMERIC, FLAGS_TRUE, FLAGS_FALSE, NUMERIC, STATUS, unique_keys, validate
)

def baseline(kind="unproved"):
    r = {k: 0 for k in NUMERIC}
    r.update({"status": STATUS,
              "original_compiled_method_bodies_scanned": 19118,
              "original_compiled_IL_instructions_scanned": 491490,
              "original_typed_Shader_Find_calls": 81,
              "exact_source_Foam_name_direct_typed_Shader_Find_calls": 1})
    r.update({k: True for k in FLAGS_TRUE})
    r.update({k: False for k in FLAGS_FALSE})
    r.update({"return_consumer_" + k: int(k == kind) for k in KINDS})
    r.update({k:0 for k in MATERIAL_NUMERIC})
    r["original_Foam_source_field_to_Material_ctor_sites"]=1
    r.update({"material_result_consumer_" + k: int(k=="unproved") for k in MATERIAL_KINDS})
    return r

class ReturnConsumerSafeReportTests(unittest.TestCase):
    def rejects(self, r):
        with self.assertRaises(ValueError):
            validate(r)
    def test_unknown_consumer_valid(self):
        self.assertTrue(validate(baseline()))
    def test_valid_typed_field_and_reader(self):
        r=baseline("instance_shader_field")
        r.update(consumer_exact_original_managed_Shader_field_definitions_resolved=1,
                 consumer_return_original_shader_field_load_instructions=12,
                 consumer_return_original_shader_field_reading_methods=3,
                 consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor=1,
                 consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments=1)
        self.assertTrue(validate(r))
    def test_valid_local(self):
        r=baseline("shader_local")
        r.update(consumer_return_original_shader_local_loads_same_method=2,
                 consumer_return_original_shader_local_method_contains_Material_Shader_constructor=1)
        self.assertTrue(validate(r))
    def test_real_material_field_to_renderer_setter(self):
        r=baseline("instance_shader_field")
        r["consumer_exact_original_managed_Shader_field_definitions_resolved"]=1
        r["material_result_consumer_unproved"]=0
        r["material_result_consumer_instance_material_field"]=1
        r["material_result_exact_original_field_definition_resolved"]=1
        r["material_result_original_material_field_loads"]=2
        r["material_result_original_material_field_distinct_readers"]=2
        r["material_result_material_field_direct_Renderer_set_material_arguments"]=1
        self.assertTrue(validate(r))
    def test_material_false_direct_renderer_setter_rejected(self):
        r=baseline()
        r["material_result_material_constructor_direct_Renderer_set_material_arguments"]=1
        self.rejects(r)
    def test_material_false_field_identity_rejected(self):
        r=baseline()
        r["material_result_exact_original_field_definition_resolved"]=1
        self.rejects(r)
    def test_material_false_field_read_rejected(self):
        r=baseline()
        r["material_result_original_material_field_loads"]=1
        self.rejects(r)
    def test_material_no_candidate_local_without_local(self):
        r=baseline()
        r["material_result_material_local_direct_Renderer_set_material_argument_candidates"]=1
        self.rejects(r)
    def test_material_multiple_consumers_rejected(self):
        r=baseline()
        r["material_result_consumer_material_local"]=1
        self.rejects(r)
    def test_material_zero_producer_rejected(self):
        r=baseline()
        r["original_Foam_source_field_to_Material_ctor_sites"]=0
        self.rejects(r)
    def test_material_direct_renderer_positive(self):
        r=baseline()
        r["material_result_consumer_unproved"]=0
        r["material_result_consumer_direct_renderer_material_setter"]=1
        r["material_result_material_constructor_direct_Renderer_set_material_arguments"]=1
        self.assertTrue(validate(r))
    def test_material_field_reads_excess_direct_setter(self):
        r=baseline()
        r["material_result_consumer_unproved"]=0
        r["material_result_consumer_static_material_field"]=1
        r["material_result_exact_original_field_definition_resolved"]=1
        r["material_result_original_material_field_loads"]=1
        r["material_result_original_material_field_distinct_readers"]=1
        r["material_result_material_field_direct_Renderer_set_sharedMaterial_arguments"]=2
        self.rejects(r)
    def test_material_unsafe_nops_rejected(self):
        r=baseline()
        r["material_result_nops_skipped_after_ctor"]=5
        self.rejects(r)
    def test_valid_material_object_initializer_field(self):
        r=baseline()
        r["material_result_consumer_unproved"]=0
        r["material_result_consumer_duplicated_unresolved"]=1
        r["material_dup_followed_by_authentic_typed_string_instance_setter"]=1
        r["material_dup_setter_followed_by_original_Material_field_store"]=1
        r["material_dup_original_Material_field_read_instructions"]=2
        r["material_dup_original_Material_field_read_methods"]=1
        r["material_dup_original_Material_field_direct_Renderer_set_material_args"]=1
        self.assertTrue(validate(r))
    def test_false_dup_material_field_rejected(self):
        r=baseline()
        r["material_dup_setter_followed_by_original_Material_field_store"]=1
        self.rejects(r)
    def test_false_dup_material_field_load_rejected(self):
        r=baseline()
        r["material_dup_original_Material_field_read_instructions"]=1
        self.rejects(r)
    def test_false_dup_material_local_link_rejected(self):
        r=baseline()
        r["material_dup_original_Material_local_loads"]=1
        self.rejects(r)
    def test_dup_material_false_renderer_setter_rejected(self):
        r=baseline()
        r["material_result_consumer_unproved"]=0
        r["material_result_consumer_duplicated_unresolved"]=1
        r["material_dup_followed_by_authentic_typed_string_instance_setter"]=1
        r["material_dup_setter_followed_by_original_Material_field_store"]=1
        r["material_dup_original_Material_field_direct_Renderer_set_material_args"]=1
        self.rejects(r)
    def test_dup_probe_cannot_claim_without_dup_opcode(self):
        r=baseline()
        r["material_dup_followed_by_authentic_typed_string_instance_setter"]=1
        self.rejects(r)
    def test_dup_object_initializer_duplicate_stores_rejected(self):
        r=baseline()
        r["material_result_consumer_unproved"]=0
        r["material_result_consumer_duplicated_unresolved"]=1
        r["material_dup_followed_by_authentic_typed_string_instance_setter"]=1
        r["material_dup_setter_followed_by_original_Material_field_store"]=1
        r["material_dup_setter_followed_by_original_Material_local_store"]=1
        self.rejects(r)
    def test_material_linear_true_original_field_link(self):
        r=baseline()
        r["material_linear_original_material_alias_instructions_inspected"]=4
        r["material_linear_original_material_instance_method_calls"]=1
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_read_instructions"]=3
        r["material_linear_original_material_field_distinct_reader_methods"]=2
        r["material_linear_original_material_field_direct_Renderer_set_material_args"]=1
        r["field_api_exact_original_material_field_sites_scanned"]=3
        self.assertTrue(validate(r))
    def test_material_linear_field_reader_without_source_store_rejected(self):
        r=baseline()
        r["material_linear_original_material_field_read_instructions"]=1
        self.rejects(r)
    def test_material_linear_bad_field_resolution_rejected(self):
        r=baseline()
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        self.rejects(r)
    def test_material_linear_bad_field_to_renderer_count(self):
        r=baseline()
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_direct_Renderer_set_material_args"]=1
        self.rejects(r)
    def test_material_linear_unsafe_branch_count_rejected(self):
        r=baseline()
        r["material_linear_original_material_alias_ambiguous_or_branch_boundaries"]=2
        self.rejects(r)
    def test_material_linear_budget_rejected(self):
        r=baseline()
        r["material_linear_original_material_alias_instructions_inspected"]=49
        self.rejects(r)
    def test_zero_calls_not_false_green(self):
        r=baseline();r["exact_source_Foam_name_direct_typed_Shader_Find_calls"]=0;self.rejects(r)
    def test_zero_partition_rejected(self):
        r=baseline();r["return_consumer_unproved"]=0;self.rejects(r)
    def test_duplicate_partition_rejected(self):
        r=baseline();r["return_consumer_shader_return"]=1;self.rejects(r)
    def test_fake_field_provenance_rejected(self):
        r=baseline();r["consumer_exact_original_managed_Shader_field_definitions_resolved"]=1;self.rejects(r)
    def test_false_field_load_rejected(self):
        r=baseline();r["consumer_return_original_shader_field_load_instructions"]=1;self.rejects(r)
    def test_false_direct_material_argument_rejected(self):
        r=baseline()
        r["consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments"]=1
        self.rejects(r)
    def test_direct_material_argument_overflows_reads(self):
        r=baseline("instance_shader_field")
        r["consumer_exact_original_managed_Shader_field_definitions_resolved"]=1
        r["consumer_return_original_shader_field_load_instructions"]=1
        r["consumer_return_original_shader_field_reading_methods"]=1
        r["consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor"]=1
        r["consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments"]=2
        self.rejects(r)
    def test_direct_material_argument_without_ctor_method(self):
        r=baseline("instance_shader_field")
        r["consumer_exact_original_managed_Shader_field_definitions_resolved"]=1
        r["consumer_return_original_shader_field_load_instructions"]=1
        r["consumer_return_original_shader_field_reading_methods"]=1
        r["consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments"]=1
        self.rejects(r)
    def test_false_local_load_rejected(self):
        r=baseline();r["consumer_return_original_shader_local_loads_same_method"]=1;self.rejects(r)
    def test_clamped_method_partition(self):
        r=baseline("static_shader_field")
        r["consumer_exact_original_managed_Shader_field_definitions_resolved"]=1
        r["consumer_return_original_shader_field_reading_methods"]=3
        self.rejects(r)
    def test_false_device_claim(self):
        r=baseline();r["Android_water_pixels_verified"]=True;self.rejects(r)
    def test_private_or_extra_key(self):
        r=baseline();r["private_original_class_name"]="Hidden";self.rejects(r)
    def test_bool_is_not_numeric(self):
        r=baseline();r["consumer_nop_instructions_skipped_after_Find"]=False;self.rejects(r)
    def test_float_is_not_numeric(self):
        r=baseline();r["original_typed_Shader_Find_calls"]=81.0;self.rejects(r)
    def test_wrong_origin_signature(self):
        r=baseline();r["original_Assembly_CSharp_SHA_authenticated"]=False;self.rejects(r)
    def test_duplicate_keys_are_forbidden(self):
        with self.assertRaises(ValueError): unique_keys([("status","a"),("status","b")])
    def test_il_drift_fails(self):
        r=baseline();r["original_compiled_IL_instructions_scanned"]=491489;self.rejects(r)
    def test_nop_boundary_fails(self):
        r=baseline();r["consumer_nop_instructions_skipped_after_Find"]=5;self.rejects(r)


    def test_source_true_nonadjacent_typed_Graphics_material_arg(self):
        r=baseline()
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_read_instructions"]=13
        r["material_linear_original_material_field_distinct_reader_methods"]=4
        r["field_api_exact_original_material_field_sites_scanned"]=13
        r["field_api_straightline_total_following_IL_instructions_scanned"]=27
        r["field_api_straightline_sites_with_typed_Material_parameter"]=1
        r["field_api_straightline_sites_with_Graphics_Material_parameter"]=1
        r["field_api_Graphics_material_sites_Other"]=1
        self.assertTrue(validate(r))

    def test_graphics_method_family_categories_are_exclusive(self):
        for kind in ("Blit", "DrawMesh", "Other", "Mixed"):
            r=baseline()
            r["material_linear_original_material_field_stores"]=1
            r["material_linear_original_material_unique_field_definition_resolved"]=1
            r["material_linear_original_material_field_read_instructions"]=1
            r["field_api_exact_original_material_field_sites_scanned"]=1
            r["field_api_straightline_sites_with_typed_Material_parameter"]=1
            r["field_api_straightline_sites_with_Graphics_Material_parameter"]=1
            r["field_api_Graphics_material_sites_"+kind]=1
            with self.subTest(kind=kind): self.assertTrue(validate(r))
            r["field_api_Graphics_material_sites_"+kind]=0
            with self.subTest(kind=kind, missing=True): self.rejects(r)

    def test_graphics_method_family_double_count_rejected(self):
        r=baseline()
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_read_instructions"]=1
        r["field_api_exact_original_material_field_sites_scanned"]=1
        r["field_api_straightline_sites_with_typed_Material_parameter"]=1
        r["field_api_straightline_sites_with_Graphics_Material_parameter"]=1
        r["field_api_Graphics_material_sites_Blit"]=1
        r["field_api_Graphics_material_sites_DrawMesh"]=1
        self.rejects(r)

    def test_graphics_method_name_only_cannot_invent_material_lineage(self):
        r=baseline()
        r["field_api_Graphics_material_sites_Blit"]=1
        self.rejects(r)

    def test_source_true_typed_material_receiver(self):
        r=baseline()
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_read_instructions"]=2
        r["field_api_exact_original_material_field_sites_scanned"]=2
        r["field_api_straightline_sites_with_typed_Material_receiver"]=1
        self.assertTrue(validate(r))

    def test_field_API_coverage_partial_forbidden(self):
        r=baseline()
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_read_instructions"]=13
        r["field_api_exact_original_material_field_sites_scanned"]=12
        self.rejects(r)

    def test_field_API_scope_without_real_field_forbidden(self):
        r=baseline()
        r["field_api_exact_original_material_field_sites_scanned"]=1
        self.rejects(r)

    def test_field_API_wrong_Graphics_without_material_param_forbidden(self):
        r=baseline()
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_read_instructions"]=1
        r["field_api_exact_original_material_field_sites_scanned"]=1
        r["field_api_straightline_sites_with_Graphics_Material_parameter"]=1
        self.rejects(r)

    def test_field_API_typed_parameter_requires_category(self):
        r=baseline()
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_read_instructions"]=1
        r["field_api_exact_original_material_field_sites_scanned"]=1
        r["field_api_straightline_sites_with_typed_Material_parameter"]=1
        self.rejects(r)

    def test_field_API_budget_forbidden(self):
        r=baseline()
        r["material_linear_original_material_field_stores"]=1
        r["material_linear_original_material_unique_field_definition_resolved"]=1
        r["material_linear_original_material_field_read_instructions"]=1
        r["field_api_exact_original_material_field_sites_scanned"]=1
        r["field_api_straightline_total_following_IL_instructions_scanned"]=33
        self.rejects(r)

    def test_field_API_boundary_excess_forbidden(self):
        r=baseline()
        r["field_api_straightline_sites_with_boundary_or_budget"]=1
        self.rejects(r)

    def test_field_API_negative_count_forbidden(self):
        r=baseline()
        r["field_api_straightline_sites_with_typed_Material_receiver"]=-1
        self.rejects(r)

if __name__ == "__main__":
    unittest.main()
