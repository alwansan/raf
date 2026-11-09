"""Adversarial SOURCE-FREE controls for authentic-IL report boundary."""
import unittest
from copy import deepcopy
from scripts.t2_foam_original_blit_report import validate, unique_keys


def fixture():
    return {
        "status": "original_foam_typed_blit_producer_audit",
        "immutable_original_zip2_sha_verified": True,
        "original_Assembly_CSharp_sha_verified": True,
        "original_Foam_Shader_name_sha_verified": True,
        "original_compiled_methods_scanned": 19118,
        "original_typed_Shader_Find_calls": 81,
        "exact_original_Foam_direct_Find_sites": 1,
        "original_Shader_field_resolved": True,
        "original_direct_Material_constructor_sites": 1,
        "original_Material_field_uniquely_resolved": True,
        "original_exact_static_four_arg_Blit_calls": 2,
        "original_explicit_pass0_literal_Blit_calls": 1,
        "original_explicit_pass1_literal_Blit_calls": 1,
        "original_other_or_dynamic_pass_Blit_calls": 0,
        "original_direct_material_field_and_typed_image_linked_Blit_calls": 2,
        "original_pass0_direct_link_candidates": 1,
        "original_pass1_direct_link_candidates": 1,
        "original_pass0_exact_Material_field_argument_calls": 1,
        "original_pass1_exact_Material_field_argument_calls": 1,
        "original_pass0_exact_Material_local_alias_calls": 0,
        "original_pass1_exact_Material_local_alias_calls": 0,
        "original_pass0_linked_Material_image_producers_unresolved": 0,
        "original_pass1_linked_Material_image_producers_unresolved": 0,
        "original_pass0_bounded_stack_source_type": "Texture",
        "original_pass1_bounded_stack_source_type": "RenderTexture",
        "original_pass0_bounded_stack_source_kind": "typed_field",
        "original_pass1_bounded_stack_source_kind": "typed_local",
        "original_pass0_bounded_stack_reason": "static_type_only_no_instance_proof",
        "original_pass1_bounded_stack_reason": "static_type_only_no_instance_proof",
        "original_pass0_bounded_stack_steps": 6,
        "original_pass1_bounded_stack_steps": 9,
        "original_pass0_bounded_stack_void_calls": 0,
        "original_pass1_bounded_stack_void_calls": 1,
        "original_bounded_stack_static_type_only": True,
        "original_bounded_stack_texture_instance_equality_verified": False,
        "original_crosspass_declared_field_token_not_heap_identity": True,
        "original_pass0_destination_declared_field_trace": False,
        "original_crosspass_declared_field_return_relation": "field_pass0_destination_untraced",
        "original_crosspass_onehop_declared_field_return_relation": "field_pass0_destination_untraced",
        "pass0_source": "Texture",
        "pass0_destination": "RenderTexture",
        "pass0_source_producer": "typed_field",
        "pass0_destination_producer": "typed_local",
        "pass1_source": "RenderTexture",
        "pass1_destination": "null",
        "pass1_source_producer": "typed_local",
        "pass1_destination_producer": "literal_null",
        "original_shader_to_blit_direct_field_types_confirmed": True,
        "original_texture_instance_identity_proven": False,
        "original_crosspass_destination_to_source_identity_proven": False,
        "original_CB0_sampler_binding_verified": False,
        "original_ShaderLab_Unity_or_Android_pixels_verified": False,
        "private_names_IL_methods_fields_pathids_or_bytecode_exported": False,
    }


class FoamOriginalBlitReportTests(unittest.TestCase):
    def test_valid_types_are_not_texture_object_identity(self):
        r = validate(fixture())
        self.assertTrue(r["proven_direct_typed_pass_roles_only"])
        self.assertFalse(r["crosspass_texture_instance_identity_proven"])
        self.assertFalse(r["CB0_and_Unity_device_evidence_proven"])

    def test_crosspass_same_field_token_is_not_heap_identity(self):
        r = fixture()
        r["original_pass0_destination_declared_field_trace"] = True
        for relation in ("field_token_match_only", "field_token_match_plus_null",
                         "field_token_match_plus_other", "field_token_match_plus_null_and_other"):
            with self.subTest(relation=relation):
                r["original_crosspass_declared_field_return_relation"] = relation
                r["original_crosspass_onehop_declared_field_return_relation"] = relation
                safe = validate(r)
                self.assertEqual(safe["crosspass_declared_field_relation"], relation)
                self.assertFalse(safe["crosspass_texture_instance_identity_proven"])
                self.assertFalse(safe["CB0_and_Unity_device_evidence_proven"])

    def test_crosspass_field_token_bad_shape_fails_closed(self):
        for relation in ("private_field_name", 17, None, False, "", "field_token_match_secret"):
            r = fixture()
            r["original_pass0_destination_declared_field_trace"] = True
            r["original_crosspass_declared_field_return_relation"] = relation
            with self.subTest(relation=relation), self.assertRaisesRegex(ValueError, "field_token_category"):
                validate(r)
        for rel, traced in (("field_token_match_only", False),
                            ("field_pass0_destination_untraced", True)):
            r = fixture()
            r["original_crosspass_declared_field_return_relation"] = rel
            r["original_pass0_destination_declared_field_trace"] = traced
            with self.subTest(rel=rel,traced=traced), self.assertRaisesRegex(ValueError, "inconsistent"):
                validate(r)
        r = fixture()
        r["original_crosspass_declared_field_token_not_heap_identity"] = False
        with self.assertRaisesRegex(ValueError, "authentication_missing"):validate(r)
        r = fixture()
        r["original_pass0_destination_declared_field_trace"] = 1
        with self.assertRaisesRegex(ValueError, "proof_flag"):validate(r)

    def test_onehop_nested_field_is_only_declared_token_provenance(self):
        r = fixture()
        r["original_pass0_destination_declared_field_trace"] = True
        r["original_crosspass_declared_field_return_relation"] = "field_no_direct_match"
        for onehop in ("field_onehop_token_match_only",
                       "field_onehop_token_match_plus_null",
                       "field_onehop_token_match_plus_other",
                       "field_onehop_token_match_plus_null_and_other"):
            with self.subTest(onehop=onehop):
                r["original_crosspass_onehop_declared_field_return_relation"] = onehop
                safe = validate(r)
                self.assertEqual(safe["crosspass_onehop_declared_field_relation"], onehop)
                self.assertFalse(safe["crosspass_texture_instance_identity_proven"])

    def test_onehop_bad_category_and_lost_direct_proof_rejected(self):
        r = fixture()
        r["original_pass0_destination_declared_field_trace"] = True
        r["original_crosspass_declared_field_return_relation"] = "field_token_match_only"
        r["original_crosspass_onehop_declared_field_return_relation"] = "field_no_direct_match"
        with self.assertRaisesRegex(ValueError,"lost_direct"):validate(r)
        for bad in ("private_field", 77, None, False, "field_onehop_runtime_heap_identity"):
            r = fixture()
            r["original_pass0_destination_declared_field_trace"] = True
            r["original_crosspass_declared_field_return_relation"] = "field_no_direct_match"
            r["original_crosspass_onehop_declared_field_return_relation"] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError,"field_token_category"):
                validate(r)
        r = fixture()
        r["original_crosspass_onehop_declared_field_return_relation"] = "field_onehop_token_match_only"
        with self.assertRaisesRegex(ValueError,"inconsistent"):validate(r)

    def test_unknown_both_passes_is_allowed_but_never_proved(self):
        r = fixture()
        r.update(original_Material_field_uniquely_resolved=False,
                 original_shader_to_blit_direct_field_types_confirmed=False,
                 original_direct_material_field_and_typed_image_linked_Blit_calls=0,
                 original_pass0_direct_link_candidates=0,
                 original_pass1_direct_link_candidates=0,
                 original_pass0_exact_Material_field_argument_calls=0,
                 original_pass1_exact_Material_field_argument_calls=0)
        for p in (0, 1):
            for key in ("source", "destination", "source_producer", "destination_producer"):
                r[f"pass{p}_{key}"] = "unknown"
            r[f"original_pass{p}_bounded_stack_source_type"] = "unknown"
            r[f"original_pass{p}_bounded_stack_source_kind"] = "unknown"
            r[f"original_pass{p}_bounded_stack_reason"] = "ambiguous_or_missing"
            r[f"original_pass{p}_bounded_stack_steps"] = 0
            r[f"original_pass{p}_bounded_stack_void_calls"] = 0
        self.assertFalse(validate(r)["proven_direct_typed_pass_roles_only"])

    def test_ambiguous_candidates_cannot_emit_sole_role(self):
        r = fixture()
        r["original_pass0_direct_link_candidates"] = 2
        r["original_pass0_exact_Material_field_argument_calls"] = 2
        r["original_direct_material_field_and_typed_image_linked_Blit_calls"] = 3
        r["original_shader_to_blit_direct_field_types_confirmed"] = False
        r["original_explicit_pass0_literal_Blit_calls"] = 2
        r["original_exact_static_four_arg_Blit_calls"] = 3
        with self.assertRaisesRegex(ValueError, "false_ambiguous"):validate(r)

    def test_must_have_original_provenance_flags(self):
        for field in ("immutable_original_zip2_sha_verified",
                      "original_Assembly_CSharp_sha_verified",
                      "original_Foam_Shader_name_sha_verified"):
            r = fixture()
            r[field] = False
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(r)

    def test_private_names_or_device_claims_rejected(self):
        for field in ("private_names_IL_methods_fields_pathids_or_bytecode_exported",
                      "original_texture_instance_identity_proven",
                      "original_crosspass_destination_to_source_identity_proven",
                      "original_CB0_sampler_binding_verified",
                      "original_ShaderLab_Unity_or_Android_pixels_verified"):
            r = fixture()
            r[field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate(r)

    def test_no_private_extra_fields(self):
        r = fixture()
        r["method_name"] = "PRIVATE"
        with self.assertRaises(ValueError):validate(r)

    def test_reject_noninteger_counts_and_bad_partition(self):
        for count in (True, -1, 2.2, "2"):
            r = fixture()
            r["original_exact_static_four_arg_Blit_calls"] = count
            with self.subTest(count=count), self.assertRaises(ValueError):validate(r)
        r = fixture()
        r["original_explicit_pass0_literal_Blit_calls"] = 5
        with self.assertRaisesRegex(ValueError, "partition"):validate(r)

    def test_no_field_no_link_even_with_fabricated_roles(self):
        r = fixture()
        r["original_Material_field_uniquely_resolved"] = False
        with self.assertRaises(ValueError):validate(r)

    def test_null_source_and_wrong_destination_rejected(self):
        for key, value in (("pass0_source", "null"), ("pass0_destination", "Texture"),
                           ("pass1_source_producer", "private_field_name")):
            r = fixture()
            r[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):validate(r)

    def test_null_requires_literal_null_producer(self):
        r = fixture()
        r["pass1_destination_producer"] = "typed_local"
        with self.assertRaisesRegex(ValueError, "null_producer"):validate(r)

    def test_original_material_field_with_indirect_pass1_image_remains_unknown(self):
        r = fixture()
        r["original_pass1_direct_link_candidates"] = 0
        r["original_direct_material_field_and_typed_image_linked_Blit_calls"] = 1
        r["original_pass1_linked_Material_image_producers_unresolved"] = 1
        r["original_shader_to_blit_direct_field_types_confirmed"] = False
        r["original_pass1_bounded_stack_source_type"] = "Texture"
        r["original_pass1_bounded_stack_source_kind"] = "typed_call_result"
        r["original_pass1_bounded_stack_steps"] = 21
        r["original_pass1_bounded_stack_void_calls"] = 1
        for key in ("source", "destination", "source_producer", "destination_producer"):
            r[f"pass1_{key}"] = "unknown"
        result = validate(r)
        self.assertFalse(result["proven_direct_typed_pass_roles_only"])
        self.assertEqual(result["pass1"], ("unknown", "unknown"))
        self.assertEqual(result["pass1_bounded_stack_source_type"], "Texture")
        self.assertFalse(result["crosspass_texture_instance_identity_proven"])

    def test_original_material_local_alias_does_not_prove_image_types(self):
        r = fixture()
        r["original_pass1_exact_Material_field_argument_calls"] = 0
        r["original_pass1_exact_Material_local_alias_calls"] = 1
        r["original_pass1_bounded_stack_source_type"] = "unknown"
        r["original_pass1_bounded_stack_source_kind"] = "unknown"
        r["original_pass1_bounded_stack_reason"] = "ambiguous_or_missing"
        r["original_pass1_bounded_stack_steps"] = 0
        r["original_pass1_bounded_stack_void_calls"] = 0
        r["original_pass1_direct_link_candidates"] = 0
        r["original_direct_material_field_and_typed_image_linked_Blit_calls"] = 1
        r["original_shader_to_blit_direct_field_types_confirmed"] = False
        for key in ("source", "destination", "source_producer", "destination_producer"):
            r[f"pass1_{key}"] = "unknown"
        self.assertFalse(validate(r)["proven_direct_typed_pass_roles_only"])

    def test_reject_material_count_overreach(self):
        for key, value in (
            ("original_pass0_exact_Material_field_argument_calls", 2),
            ("original_pass1_linked_Material_image_producers_unresolved", 1),
            ("original_pass1_exact_Material_local_alias_calls", 1),
        ):
            r = fixture()
            r[key] = value
            with self.subTest(field=key), self.assertRaisesRegex(ValueError, "partition"):
                validate(r)

    def test_bounded_stack_cannot_forge_device_or_instance_identity(self):
        for flag in ("original_bounded_stack_texture_instance_equality_verified",
                     "original_CB0_sampler_binding_verified"):
            r=fixture()
            r[flag]=True
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                validate(r)

    def test_reject_misleading_bounded_stack_type_or_budget(self):
        modifications=(
            ("original_pass1_bounded_stack_source_type", "Texture"),
            ("original_pass1_bounded_stack_source_kind", "private_method"),
            ("original_pass1_bounded_stack_reason", "original_private_instruction"),
            ("original_pass1_bounded_stack_steps", 97),
            ("original_pass1_bounded_stack_void_calls", 999),
            ("original_pass0_bounded_stack_source_type", "RenderTexture"),
        )
        for key,value in modifications:
            r=fixture()
            r[key]=value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(r)

    def test_unique_material_path_required_for_stack_proof(self):
        r=fixture()
        r["original_pass1_exact_Material_field_argument_calls"]=0
        r["original_pass1_exact_Material_local_alias_calls"]=1
        with self.assertRaises(ValueError):validate(r)

    def test_duplicate_report_keys_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate_json_key"):
            unique_keys([("pass0_source", "Texture"), ("pass0_source", "unknown")])


if __name__ == "__main__":
    unittest.main()
