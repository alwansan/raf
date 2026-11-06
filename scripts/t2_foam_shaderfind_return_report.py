"""Fail-closed original Foam Shader.Find return typed-IL count-only attestation."""
import argparse
import json
from pathlib import Path

KINDS = (
    "instance_shader_field", "static_shader_field", "shader_local",
    "shader_return", "typed_shader_call_argument",
    "typed_shader_constructor_argument", "discarded_pop",
    "duplicated_unresolved", "unproved",
)
FLAGS_TRUE = ("original_zip2_shader_name_SHA_authenticated",
              "original_Assembly_CSharp_SHA_authenticated")
FLAGS_FALSE = (
    "original_Shader_Find_executed_in_Unity",
    "field_declaring_TypeDef_is_427_scene_script_proven",
    "Unity_Material_or_Renderer_actual_binding_verified",
    "original_Foam_CB0_runtime_upload_verified",
    "Android_water_pixels_verified",
    "private_original_names_fields_method_IDs_or_IL_exported",
)
NUMERIC = (
    "original_compiled_method_bodies_scanned",
    "original_compiled_IL_instructions_scanned",
    "original_typed_Shader_Find_calls",
    "exact_source_Foam_name_direct_typed_Shader_Find_calls",
    "consumer_exact_original_managed_Shader_field_definitions_resolved",
    "consumer_return_original_shader_local_loads_same_method",
    "consumer_return_original_shader_local_method_contains_Material_Shader_constructor",
    "consumer_return_original_shader_field_load_instructions",
    "consumer_return_original_shader_field_reading_methods",
    "consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor",
    "consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments",
    "consumer_nop_instructions_skipped_after_Find",
)
MATERIAL_KINDS = (
    "instance_material_field", "static_material_field", "material_local",
    "material_return", "direct_renderer_material_setter",
    "direct_renderer_shared_material_setter", "discarded_pop",
    "duplicated_unresolved", "unproved",
)
MATERIAL_NUMERIC = (
    "original_Foam_source_field_to_Material_ctor_sites",
    "material_result_exact_original_field_definition_resolved",
    "material_result_original_material_field_loads",
    "material_result_original_material_field_distinct_readers",
    "material_result_material_field_direct_Renderer_set_material_arguments",
    "material_result_material_field_direct_Renderer_set_sharedMaterial_arguments",
    "material_result_material_local_loads_after_constructor",
    "material_result_material_local_direct_Renderer_set_material_argument_candidates",
    "material_result_material_local_direct_Renderer_set_sharedMaterial_argument_candidates",
    "material_result_material_constructor_direct_Renderer_set_material_arguments",
    "material_result_material_constructor_direct_Renderer_set_sharedMaterial_arguments",
    "material_result_nops_skipped_after_ctor",
    "material_dup_followed_by_authentic_typed_string_instance_setter",
    "material_dup_setter_followed_by_original_Material_field_store",
    "material_dup_setter_followed_by_original_Material_local_store",
    "material_dup_original_Material_field_read_instructions",
    "material_dup_original_Material_field_read_methods",
    "material_dup_original_Material_field_direct_Renderer_set_material_args",
    "material_dup_original_Material_field_direct_Renderer_set_sharedMaterial_args",
    "material_dup_original_Material_local_loads",
    "material_dup_original_Material_local_direct_Renderer_set_material_candidates",
    "material_dup_original_Material_local_direct_Renderer_set_sharedMaterial_candidates",
    "material_dup_nops_skipped_in_initializer_probe",
)
STATUS = "original_foam_ShaderFind_direct_return_consumer_typed_IL_census"

def unique_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate_source_safe_JSON_key")
        out[key] = value
    return out

def validate(report):
    if type(report) is not dict:
        raise ValueError("report_type")
    counts = tuple("return_consumer_" + x for x in KINDS)
    material_counts = tuple("material_result_consumer_" + x for x in MATERIAL_KINDS)
    expected = (set(NUMERIC) | set(MATERIAL_NUMERIC) | set(FLAGS_TRUE) |
                set(FLAGS_FALSE) | set(counts) | set(material_counts) | {"status"})
    if set(report) != expected or report["status"] != STATUS:
        raise ValueError("unexpected_original_safe_report_shape")
    if any(report[k] is not True for k in FLAGS_TRUE):
        raise ValueError("unauthenticated_original")
    if any(report[k] is not False for k in FLAGS_FALSE):
        raise ValueError("unsupported_original_runtime_claim")
    for key in NUMERIC + MATERIAL_NUMERIC + counts + material_counts:
        if type(report[key]) is not int or not 0 <= report[key] <= 20000000:
            raise ValueError("bad_safe_aggregate_int")
    if (report["original_compiled_method_bodies_scanned"] != 19118
            or report["original_compiled_IL_instructions_scanned"] != 491490
            or report["original_typed_Shader_Find_calls"] != 81
            or report["exact_source_Foam_name_direct_typed_Shader_Find_calls"] != 1):
        raise ValueError("SHA_original_unique_typed_call_drift")
    if sum(report[k] for k in counts) != 1 or any(report[k] > 1 for k in counts):
        raise ValueError("direct_return_consumer_partition")
    has_field = sum(report["return_consumer_" + k] for k in
                    ("instance_shader_field", "static_shader_field"))
    is_local = report["return_consumer_shader_local"]
    if report["consumer_exact_original_managed_Shader_field_definitions_resolved"] != has_field:
        raise ValueError("original_typed_field_resolution_not_proven")
    if has_field == 0 and (report["consumer_return_original_shader_field_load_instructions"] != 0
                         or report["consumer_return_original_shader_field_reading_methods"] != 0
                         or report["consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor"] != 0
                         or report["consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments"] != 0):
        raise ValueError("false_positive_original_field_lineage")
    if not is_local and (report["consumer_return_original_shader_local_loads_same_method"] != 0
                         or report["consumer_return_original_shader_local_method_contains_Material_Shader_constructor"] != 0):
        raise ValueError("false_positive_local_lineage")
    if report["consumer_return_original_shader_field_reading_methods"] > report["consumer_return_original_shader_field_load_instructions"]:
        raise ValueError("field_reads_partition")
    if (report["consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor"]
            > report["consumer_return_original_shader_field_reading_methods"]):
        raise ValueError("material_cooccurrence_partition")
    if (report["consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments"]
            > report["consumer_return_original_shader_field_load_instructions"]):
        raise ValueError("direct_material_argument_exceeds_original_field_loads")
    if (report["consumer_return_original_shader_field_loads_direct_Material_Shader_constructor_arguments"] > 0
            and report["consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor"] == 0):
        raise ValueError("direct_material_argument_without_any_corresponding_method")
    if (report["consumer_return_original_shader_local_method_contains_Material_Shader_constructor"] >
            min(1, report["consumer_return_original_shader_local_loads_same_method"])):
        raise ValueError("local_material_cooccurrence_partition")
    if report["consumer_nop_instructions_skipped_after_Find"] > 4:
        raise ValueError("unbounded_source_nop_boundary")
    if report["original_Foam_source_field_to_Material_ctor_sites"] != 1:
        raise ValueError("original_material_direct_producer_not_proven")
    if sum(report[k] for k in material_counts) != 1 or any(report[k]>1 for k in material_counts):
        raise ValueError("original_material_result_consumer_partition")
    material_field = sum(report["material_result_consumer_" + k] for k in
                         ("instance_material_field","static_material_field"))
    if report["material_result_exact_original_field_definition_resolved"] != material_field:
        raise ValueError("original_material_field_identity_unproven")
    if material_field == 0 and any(report[k]!=0 for k in (
            "material_result_original_material_field_loads",
            "material_result_original_material_field_distinct_readers",
            "material_result_material_field_direct_Renderer_set_material_arguments",
            "material_result_material_field_direct_Renderer_set_sharedMaterial_arguments")):
        raise ValueError("original_material_field_link_fabricated")
    if report["material_result_consumer_material_local"] == 0 and any(report[k]!=0 for k in (
            "material_result_material_local_loads_after_constructor",
            "material_result_material_local_direct_Renderer_set_material_argument_candidates",
            "material_result_material_local_direct_Renderer_set_sharedMaterial_argument_candidates")):
        raise ValueError("original_material_local_link_fabricated")
    if report["material_result_original_material_field_distinct_readers"] > report["material_result_original_material_field_loads"]:
        raise ValueError("original_material_field_read_partition")
    if sum(report[k] for k in (
            "material_result_material_field_direct_Renderer_set_material_arguments",
            "material_result_material_field_direct_Renderer_set_sharedMaterial_arguments")) > report["material_result_original_material_field_loads"]:
        raise ValueError("material_field_renderer_args_exceed_field_reads")
    if sum(report[k] for k in (
            "material_result_material_local_direct_Renderer_set_material_argument_candidates",
            "material_result_material_local_direct_Renderer_set_sharedMaterial_argument_candidates")) > report["material_result_material_local_loads_after_constructor"]:
        raise ValueError("material_local_renderer_args_exceed_local_reads")
    if report["material_result_material_constructor_direct_Renderer_set_material_arguments"] != report["material_result_consumer_direct_renderer_material_setter"]:
        raise ValueError("material_constructor_direct_renderer_material_partition")
    if report["material_result_material_constructor_direct_Renderer_set_sharedMaterial_arguments"] != report["material_result_consumer_direct_renderer_shared_material_setter"]:
        raise ValueError("material_constructor_direct_renderer_shared_partition")
    if report["material_result_nops_skipped_after_ctor"] > 4:
        raise ValueError("unbounded_material_result_nops")
    if (report["material_dup_followed_by_authentic_typed_string_instance_setter"] >
            report["material_result_consumer_duplicated_unresolved"]):
        raise ValueError("not_dup_stack_source_initializer")
    if (report["material_dup_setter_followed_by_original_Material_field_store"]
            + report["material_dup_setter_followed_by_original_Material_local_store"] >
            report["material_dup_followed_by_authentic_typed_string_instance_setter"]):
        raise ValueError("dup_initializer_unproved_field_local")
    if report["material_dup_setter_followed_by_original_Material_field_store"]==0 and any(
            report[k] != 0 for k in (
            "material_dup_original_Material_field_read_instructions",
            "material_dup_original_Material_field_read_methods",
            "material_dup_original_Material_field_direct_Renderer_set_material_args",
            "material_dup_original_Material_field_direct_Renderer_set_sharedMaterial_args")):
        raise ValueError("dup_material_field_provenance_fabrication")
    if report["material_dup_setter_followed_by_original_Material_local_store"]==0 and any(
            report[k] != 0 for k in (
            "material_dup_original_Material_local_loads",
            "material_dup_original_Material_local_direct_Renderer_set_material_candidates",
            "material_dup_original_Material_local_direct_Renderer_set_sharedMaterial_candidates")):
        raise ValueError("dup_material_local_provenance_fabrication")
    if (report["material_dup_original_Material_field_read_methods"] >
            report["material_dup_original_Material_field_read_instructions"]):
        raise ValueError("dup_material_field_read_partition")
    if sum(report[k] for k in (
            "material_dup_original_Material_field_direct_Renderer_set_material_args",
            "material_dup_original_Material_field_direct_Renderer_set_sharedMaterial_args")) > report["material_dup_original_Material_field_read_instructions"]:
        raise ValueError("dup_material_direct_renderer_field_bound")
    if sum(report[k] for k in (
            "material_dup_original_Material_local_direct_Renderer_set_material_candidates",
            "material_dup_original_Material_local_direct_Renderer_set_sharedMaterial_candidates")) > report["material_dup_original_Material_local_loads"]:
        raise ValueError("dup_material_direct_renderer_local_bound")
    if report["material_dup_nops_skipped_in_initializer_probe"] > 16:
        raise ValueError("dup_initializer_excess_nops")
    return True

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("report", type=Path)
    args = p.parse_args()
    try:
        path = args.report.absolute()
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 16384:
            raise ValueError("unsafe_safe_report_file")
        r = json.loads(path.read_text(encoding="utf8"), object_pairs_hook=unique_keys)
        validate(r)
    except BaseException:
        print("T2_FOAM_SHADERFIND_RETURN_ATTESTATION_BLOCKED")
        return 2
    print("T2_FOAM_SHADERFIND_RETURN_ATTESTATION_PASS original_direct_find_calls=1 partition=1")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
