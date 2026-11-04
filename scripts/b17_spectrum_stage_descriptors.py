"""B17: fail-closed, SHA-pinned original Spectrum stage descriptor census.

Read-only numeric and digest-only evidence for the *original serialized*
shader's texture/sampler resource records. It is NOT a shader translator,
original-to-ShaderLab mapping, sampler-state emulation, or Unity/GPU proof.
Do not publish original names, program bytes, GUIDs, raw trees or paths.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from scripts.probe_w2_water_shader_stage_bindings import extract_shader, STAGES
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

OWNER = "sharedassets0.assets"
SPECTRUM_PATH_ID = 2432
PASSES = 7
# Explicit finite list of Unity serialization table names; an unknown
# texture/sampler/uav table cannot be silently ignored as "no resources".
RESOURCE_FIELDS = (
    "m_TextureParameters", "m_TextureParams", "m_Textures", "m_TextureBindings",
    "m_SamplerParameters", "m_SamplerParams", "m_Samplers", "m_SamplerBindings",
    "m_UAVParameters", "m_UAVParams", "m_UAVs", "m_UAVBindings",
)
MAX_ROWS = 256
MAX_FIELDS = 32
MAX_DEPTH = 5
MAX_NUMBER = 2 ** 53


def numeric_tree(value, depth=0):
    """Canonicalize only bounded numeric descriptor trees, never strings."""
    if depth > MAX_DEPTH:
        raise ValueError("Resource descriptor nesting exceeds bound")
    if type(value) is bool or value is None or isinstance(value, str):
        raise ValueError("Unsupported nonnumeric descriptor value")
    if type(value) is int:
        if not -MAX_NUMBER <= value <= MAX_NUMBER:
            raise ValueError("Descriptor integer outside exact bound")
        return value
    if type(value) is float:
        if not math.isfinite(value) or abs(value) > MAX_NUMBER:
            raise ValueError("Nonfinite or oversized descriptor number")
        return value
    if isinstance(value, (list, tuple)):
        if len(value) > MAX_ROWS:
            raise ValueError("Resource descriptor list too long")
        return [numeric_tree(x, depth + 1) for x in value]
    if isinstance(value, dict):
        if len(value) > MAX_FIELDS:
            raise ValueError("Resource descriptor structure too large")
        result = {}
        for key, item in value.items():
            if (not isinstance(key, str) or not key.startswith("m_") or
                    len(key) > 64 or not all(x.isascii() and
                    (x.isalnum() or x == "_") for x in key)):
                raise ValueError("Unsupported resource descriptor schema key")
            if key == "m_MultiSampled":
                # Unity's serialized TextureParameter has an actual boolean
                # MultiSampled field. Encode its type distinctly, never let a
                # boolean satisfy an integer index/slot assertion.
                if type(item) is not bool:
                    raise ValueError("Invalid texture multisample boolean")
                result[key] = {"__typed_multisampled_bool__": int(item)}
            else:
                result[key] = numeric_tree(item, depth + 1)
        return {k: result[k] for k in sorted(result)}
    raise ValueError("Unexpected resource descriptor type")


def stage_profile(program):
    if not isinstance(program, dict):
        raise ValueError("Missing original stage")
    common = program.get("m_CommonParameters")
    if not isinstance(common, dict):
        raise ValueError("Missing original stage common parameter table")
    unknown_resource_keys = [key for key in common
                             if isinstance(key, str)
                             and any(s in key.lower() for s in ("texture", "sampler", "uav"))
                             and key not in RESOURCE_FIELDS]
    if unknown_resource_keys:
        # These are bounded standard serialized structural key labels, not
        # shader property names, program bytes, object IDs or raw values.
        safe = sorted(key for key in unknown_resource_keys
                      if key.startswith("m_") and len(key) <= 64 and
                      all(ch.isascii() and (ch.isalnum() or ch == "_") for ch in key))
        if len(safe) != len(unknown_resource_keys) or len(safe) > 32:
            raise ValueError("Unknown texture/sampler resource table schema")
        raise ValueError("Unmodeled structural resource fields: " + ",".join(safe))
    rows_by_field = {}
    signature_fields = {}
    for key in RESOURCE_FIELDS:
        if key not in common:
            continue
        rows = common[key]
        if not isinstance(rows, list) or len(rows) > MAX_ROWS:
            raise ValueError("Resource table is not a bounded list")
        canon = [numeric_tree(x) for x in rows]
        rows_by_field[key] = len(canon)
        signature_fields[key] = canon
    digest = hashlib.sha256(json.dumps(signature_fields, sort_keys=True, separators=(",", ":"),
                                      allow_nan=False).encode("utf-8")).hexdigest()
    return {"table_rows": dict(sorted(rows_by_field.items())),
            "descriptor_rows": sum(rows_by_field.values()),
            "schema_fields_observed": len(rows_by_field),
            "numeric_descriptor_sha256": digest,
            "field_values_disclosed": False}


def summarize_passes(passes):
    if not isinstance(passes, list) or len(passes) != PASSES:
        raise ValueError("Original Spectrum 7-pass count differs")
    result = []
    for index, item in enumerate(passes):
        if not isinstance(item, dict):
            raise ValueError("Malformed original pass")
        per_stage = {"pass_index": index}
        for stage in STAGES:
            per_stage[stage] = stage_profile(item.get(stage))
        result.append(per_stage)
    fragment_rows = sum(x["progFragment"]["descriptor_rows"] for x in result)
    vertex_rows = sum(x["progVertex"]["descriptor_rows"] for x in result)
    observed_fields = sum(x[s]["schema_fields_observed"] for x in result for s in STAGES)
    if observed_fields == 0:
        raise ValueError("No recognizable serialized resource table schema")
    return {"original_pass_count": PASSES,
            "stage_descriptor_table_counts": {
                "vertex_rows": vertex_rows, "fragment_rows": fragment_rows,
                "observed_table_fields": observed_fields,
            },
            "per_pass_stage_numeric_contract": result,
            "original_stage_resource_tables_observed": True,
            "original_shaderlab_reconstruction_verified": False,
            "original_resource_semantics_or_sampler_state_verified": False,
            "original_shader_to_export_join_verified": False,
            "unity_gpu_or_android_verified": False,
            "original_program_bytes_or_names_disclosed": False,
            "game_source_modified": False,
            "ready_for_build": False}


def inspect(source: Path):
    import UnityPy
    if source.is_symlink() or not source.is_dir():
        raise ValueError("Original source root is missing or redirected")
    verified = verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    env = UnityPy.load(str(source / OWNER))
    objects = [obj for obj in env.objects
               if obj.type.name == "Shader" and int(obj.path_id) == SPECTRUM_PATH_ID]
    if len(objects) != 1:
        raise ValueError("Original Spectrum Shader identity missing or ambiguous")
    tree = objects[0].read_typetree()
    if not isinstance(tree, dict):
        raise ValueError("Original Shader serialized tree malformed")
    # Reuse W2's independently authenticated pass/variant/CB/blob-order
    # topology assertions before claiming any descriptor provenance.
    extract_shader({SPECTRUM_PATH_ID: objects[0]}, SPECTRUM_PATH_ID, "Spectrum-graph")
    parsed = tree.get("m_ParsedForm")
    if not isinstance(parsed, dict) or not isinstance(parsed.get("m_SubShaders"), list):
        raise ValueError("Missing original parsed Shader data")
    if len(parsed["m_SubShaders"]) != 1:
        raise ValueError("Original Spectrum subshader count changed")
    result = summarize_passes(parsed["m_SubShaders"][0].get("m_Passes"))
    result.update(schema_version=1, source_zip2_commit="15964ea8f246b6e076ce26b60931ee2e1a9a2385",
                  source_owner_sha256=EXPECTED[OWNER][1], verified_source_bytes=EXPECTED[OWNER][0],
                  source_owner_sha_verified=verified["authenticated_owners"] == 1,
                  original_spectrum_object_identity_verified=True)
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        report = inspect(args.source)
        if args.out.exists() or args.out.is_symlink():
            raise ValueError("Refuse to overwrite experiment result")
        args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print("RAFT_B17_SPECTRUM_DESCRIPTORS " + json.dumps({
            "status": "SOURCE_NUMERIC_DESCRIPTOR_CENSUS",
            "source_owner_sha_verified": report["source_owner_sha_verified"],
            "original_pass_count": report["original_pass_count"],
            "stage_descriptor_table_counts": report["stage_descriptor_table_counts"],
            "unity_gpu_or_android_verified": False,
            "ready_for_build": False,
        }, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        # Only literal source-free diagnostic reasons are publishable; do not
        # forward arbitrary UnityPy exceptions, paths or original metadata.
        safe_reasons = {
            "Resource descriptor nesting exceeds bound",
            "Unsupported nonnumeric descriptor value",
            "Invalid texture multisample boolean",
            "Descriptor integer outside exact bound",
            "Nonfinite or oversized descriptor number",
            "Resource descriptor list too long",
            "Resource descriptor structure too large",
            "Unsupported resource descriptor schema key",
            "Unexpected resource descriptor type",
            "Missing original stage",
            "Missing original stage common parameter table",
            "Unknown texture/sampler resource table schema",
            "Resource table is not a bounded list",
            "Original Spectrum 7-pass count differs",
            "Malformed original pass",
            "No recognizable serialized resource table schema",
            "Original source root is missing or redirected",
            "Original Spectrum Shader identity missing or ambiguous",
            "Original Shader serialized tree malformed",
            "Missing original parsed Shader data",
            "Original Spectrum subshader count changed",
            "Refuse to overwrite experiment result",
        }
        print("RAFT_B17_SPECTRUM_DESCRIPTORS " + json.dumps({
            "status": "REJECTED", "error_kind": type(error).__name__,
            "reason_code": (str(error) if str(error) in safe_reasons else
                            "unmodeled_resource_schema" if str(error).startswith(
                                "Unmodeled structural resource fields: ") else
                            "other_provider_schema_failure"),
            "unmodeled_unity_structural_fields": (
                str(error).split(": ", 1)[1].split(",")
                if str(error).startswith("Unmodeled structural resource fields: ") else []),
            "unity_gpu_or_android_verified": False, "ready_for_build": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
