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
    "consumer_nop_instructions_skipped_after_Find",
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
    expected = set(NUMERIC) | set(FLAGS_TRUE) | set(FLAGS_FALSE) | set(counts) | {"status"}
    if set(report) != expected or report["status"] != STATUS:
        raise ValueError("unexpected_original_safe_report_shape")
    if any(report[k] is not True for k in FLAGS_TRUE):
        raise ValueError("unauthenticated_original")
    if any(report[k] is not False for k in FLAGS_FALSE):
        raise ValueError("unsupported_original_runtime_claim")
    for key in NUMERIC + counts:
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
                         or report["consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor"] != 0):
        raise ValueError("false_positive_original_field_lineage")
    if not is_local and (report["consumer_return_original_shader_local_loads_same_method"] != 0
                         or report["consumer_return_original_shader_local_method_contains_Material_Shader_constructor"] != 0):
        raise ValueError("false_positive_local_lineage")
    if report["consumer_return_original_shader_field_reading_methods"] > report["consumer_return_original_shader_field_load_instructions"]:
        raise ValueError("field_reads_partition")
    if (report["consumer_return_original_shader_field_reading_methods_with_Material_Shader_constructor"]
            > report["consumer_return_original_shader_field_reading_methods"]):
        raise ValueError("material_cooccurrence_partition")
    if (report["consumer_return_original_shader_local_method_contains_Material_Shader_constructor"] >
            min(1, report["consumer_return_original_shader_local_loads_same_method"])):
        raise ValueError("local_material_cooccurrence_partition")
    if report["consumer_nop_instructions_skipped_after_Find"] > 4:
        raise ValueError("unbounded_source_nop_boundary")
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
