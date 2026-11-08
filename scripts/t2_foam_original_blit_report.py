"""Validate SAFE SHA-original Foam Blit CIL summary, never raw IL or private names.

A typed source/destination declaration is not a RenderTexture object identity.
An authentic assembly signature or unique pass number alone is insufficient.
"""
import json
import sys
from pathlib import Path

STATUS = "original_foam_typed_blit_producer_audit"
NUMBERS = {
    "original_compiled_methods_scanned", "original_typed_Shader_Find_calls",
    "exact_original_Foam_direct_Find_sites",
    "original_direct_Material_constructor_sites",
    "original_exact_static_four_arg_Blit_calls",
    "original_explicit_pass0_literal_Blit_calls",
    "original_explicit_pass1_literal_Blit_calls",
    "original_other_or_dynamic_pass_Blit_calls",
    "original_direct_material_field_and_typed_image_linked_Blit_calls",
    "original_pass0_direct_link_candidates", "original_pass1_direct_link_candidates",
}
TRUE_FLAGS = {
    "immutable_original_zip2_sha_verified",
    "original_Assembly_CSharp_sha_verified",
    "original_Foam_Shader_name_sha_verified",
}
BOOLEAN_FLAGS = {
    "original_Shader_field_resolved", "original_Material_field_uniquely_resolved",
    "original_shader_to_blit_direct_field_types_confirmed",
}
FALSE_FLAGS = {
    "original_texture_instance_identity_proven",
    "original_crosspass_destination_to_source_identity_proven",
    "original_CB0_sampler_binding_verified",
    "original_ShaderLab_Unity_or_Android_pixels_verified",
    "private_names_IL_methods_fields_pathids_or_bytecode_exported",
}
ROLES = {"Texture", "RenderTexture", "null", "unknown"}
PRODUCERS = {"typed_argument", "typed_local", "typed_field", "literal_null", "unknown"}
ROLE_KEYS = {f"pass{p}_{v}" for p in (0, 1) for v in
             ("source", "destination", "source_producer", "destination_producer")}
EXPECTED = {"status"} | NUMBERS | TRUE_FLAGS | BOOLEAN_FLAGS | FALSE_FLAGS | ROLE_KEYS


def unique_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate_json_key")
        out[key] = value
    return out


def validate(report):
    if type(report) is not dict or set(report) != EXPECTED or report.get("status") != STATUS:
        raise ValueError("unsafe_original_report_shape")
    if any(report[k] is not True for k in TRUE_FLAGS):
        raise ValueError("SHA_original_authentication_missing")
    if any(report[k] is not False for k in FALSE_FLAGS):
        raise ValueError("unsupported_original_runtime_or_private_claim")
    if any(type(report[k]) is not bool for k in BOOLEAN_FLAGS):
        raise ValueError("invalid_original_proof_flag")
    if any(type(report[k]) is not int or not 0 <= report[k] <= 20000000 for k in NUMBERS):
        raise ValueError("invalid_original_count")
    if report["original_compiled_methods_scanned"] < 1000:
        raise ValueError("managed_source_scan_incomplete")
    if report["exact_original_Foam_direct_Find_sites"] != 1:
        raise ValueError("source_Foam_find_not_unique")
    if report["original_typed_Shader_Find_calls"] < 1:
        raise ValueError("missing_original_Shader_Find")
    if report["original_Shader_field_resolved"] is False and (
        report["original_direct_Material_constructor_sites"] != 0 or
        report["original_Material_field_uniquely_resolved"]
    ):
        raise ValueError("material_constructor_without_Shader_field")
    if report["original_Material_field_uniquely_resolved"] and (
        not report["original_Shader_field_resolved"] or
        report["original_direct_Material_constructor_sites"] != 1
    ):
        raise ValueError("material_identity_without_exact_constructor")
    n = report["original_exact_static_four_arg_Blit_calls"]
    p0 = report["original_explicit_pass0_literal_Blit_calls"]
    p1 = report["original_explicit_pass1_literal_Blit_calls"]
    other = report["original_other_or_dynamic_pass_Blit_calls"]
    if n != p0 + p1 + other:
        raise ValueError("Blit_pass_partition_mismatch")
    c0 = report["original_pass0_direct_link_candidates"]
    c1 = report["original_pass1_direct_link_candidates"]
    if c0 > p0 or c1 > p1 or c0 + c1 != report[
        "original_direct_material_field_and_typed_image_linked_Blit_calls"
    ]:
        raise ValueError("Blit_material_link_partition")
    if (not report["original_Material_field_uniquely_resolved"] and (c0 or c1)):
        raise ValueError("Blit_link_without_original_material")
    proof = c0 == c1 == 1 and report["original_Material_field_uniquely_resolved"]
    if report["original_shader_to_blit_direct_field_types_confirmed"] is not proof:
        raise ValueError("false_or_missing_two_pass_role_flag")
    for index, count in ((0, c0), (1, c1)):
        src = report[f"pass{index}_source"]
        dst = report[f"pass{index}_destination"]
        src_producer = report[f"pass{index}_source_producer"]
        dst_producer = report[f"pass{index}_destination_producer"]
        if src not in ROLES or dst not in ROLES or src_producer not in PRODUCERS or dst_producer not in PRODUCERS:
            raise ValueError("unknown_or_unsafe_role_tag")
        if src == "null" or dst == "Texture":
            raise ValueError("invalid_public_Graphics_Blit_role")
        if count != 1:
            if (src, dst, src_producer, dst_producer) != ("unknown",)*4:
                raise ValueError("false_ambiguous_pass_role")
        else:
            if src not in ("Texture", "RenderTexture") or dst not in ("RenderTexture", "null"):
                raise ValueError("incomplete_direct_role_tag")
            if (src_producer not in ("typed_argument", "typed_local", "typed_field") or
                dst_producer not in ("typed_argument", "typed_local", "typed_field", "literal_null")):
                raise ValueError("unsupported_producer_class")
            if (dst == "null") != (dst_producer == "literal_null"):
                raise ValueError("null_producer_disagreement")
    # Explicit boundaries: NEVER claim that pass1 samples the same actual RT
    # object written by pass0 just because their declared types are equal.
    return {
        "original_source_sha_verified": True,
        "Foam_name_direct_original_typed_Find": True,
        "proven_direct_typed_pass_roles_only": proof,
        "pass0": (report["pass0_source"], report["pass0_destination"]),
        "pass1": (report["pass1_source"], report["pass1_destination"]),
        "crosspass_texture_instance_identity_proven": False,
        "CB0_and_Unity_device_evidence_proven": False,
    }


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        raise SystemExit("usage: python -m scripts.t2_foam_original_blit_report safe_original.json")
    p = Path(args[0])
    if not p.is_file() or p.is_symlink() or p.stat().st_size > 4096:
        raise ValueError("unsafe_original_report_file")
    with p.open(encoding="utf-8") as f:
        result = validate(json.load(f, object_pairs_hook=unique_keys,
                                    parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite_json"))))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
