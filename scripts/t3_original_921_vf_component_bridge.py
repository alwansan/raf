#!/usr/bin/env python3
"""Private, SHA-original 921-use Shader48 VS/FS SPIR-V component diagnostic.

Uses one exactly matching original DXBC vertex/fragment pair per original Pass.
Only aggregate typed Location+Component coverage leaves the runner. This is
NOT DXBC semantics, interpolant equality, Unity ShaderLab or device pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from scripts import t3_original_top_shader_fourpass_translation as baseline
from scripts import t3_original_renderer_shader_impact as original
from scripts import t3_original_top_shader_dxbc_feasibility as feasibility
from scripts.t3_spirv_interface_name_drift import read_reflection as read_private
from scripts.t3_vf_spirv_component_coverage import classify_vf_components
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import reflection as safe_reflection

STATUS = "ORIGINAL_TOP_921_FOURPASS_VF_COMPONENT_COVERAGE_CLASSIFIED"
SAFE_STATUSES = (
    "STRUCTURAL_CANDIDATE_ONLY", "STRUCTURAL_DEFICIT",
    "INCONCLUSIVE_UNSUPPORTED_TYPE", "NO_USER_VARYINGS",
)
COUNT_FIELDS = (
    "vertex_output_records", "fragment_input_records",
    "vertex_output_components", "fragment_input_components",
    "missing_fragment_components", "typed_mismatch_components",
    "extra_vertex_components", "unsupported_type_records",
    "excluded_builtin_records",
)
PROOF_FLAGS = (
    "original_dxbc_semantics_verified",
    "interpolation_verified",
    "pixel_fidelity_verified",
)
LOCATION_KEYS = frozenset(("location", "component", "type", "name", "id", "interpolation"))


def sanitize_private_side(raw: dict, prior_safe: dict, side: str):
    """Drop every private name/ID and verify same located rows as old reflector.

    The older reflector did not preserve Component and may report same-location
    rows. We cross-check multiset identity before honoring Component values.
    Unknown record decorations fail closed instead of pretending matching data.
    """
    if (side not in ("inputs", "outputs") or type(raw) is not dict or
        type(prior_safe) is not dict):
        raise ValueError("invalid_private_component_reflection_root")
    raw_rows = raw.get(side, [])
    safe_rows = prior_safe.get(side)
    if (type(raw_rows) is not list or len(raw_rows) > 256 or
        type(safe_rows) is not list or len(safe_rows) > 256):
        raise ValueError("unbounded_or_missing_component_reflection_side")
    prior = Counter()
    for item in safe_rows:
        if (type(item) is not dict or set(item) != {"type", "location"} or
            type(item["location"]) is not int or
            type(item["type"]) is not str):
            raise ValueError("invalid_prior_original_component_baseline")
        prior[(item["location"], item["type"])] += 1
    observed = Counter()
    sanitized = []
    for row in raw_rows:
        if type(row) is not dict:
            raise ValueError("invalid_private_component_reflection_row")
        if "location" not in row:
            # Unlocated builtins are explicitly outside user-varying coverage;
            # no inference from a generated or compiler-specific name.
            continue
        if not set(row).issubset(LOCATION_KEYS):
            raise ValueError("unsupported_private_component_layout_decoration")
        loc, typ = row["location"], row.get("type")
        cmp = row.get("component", 0)
        if (type(loc) is not int or not 0 <= loc <= 65535 or
            type(cmp) is not int or not 0 <= cmp <= 3 or
            type(typ) is not str or not 0 < len(typ) <= 16):
            raise ValueError("invalid_private_component_location_or_type")
        if "id" in row and (type(row["id"]) is not int or row["id"] < 0):
            raise ValueError("invalid_private_component_id")
        if "name" in row and type(row["name"]) is not str:
            raise ValueError("invalid_private_component_name_type")
        observed[(loc, typ)] += 1
        sanitized.append({"location": loc, "component": cmp, "type": typ})
    if observed != prior:
        raise ValueError("private_component_data_disagrees_with_prior_safe_reflection")
    return sanitized


def safe_aggregate(value: dict):
    """Exactly allow-listed scalar counters from the source-free classifier."""
    if (type(value) is not dict or set(value) !=
        set(COUNT_FIELDS) | set(PROOF_FLAGS) | {"status"}):
        raise ValueError("untrusted_private_component_classifier_output")
    if type(value["status"]) is not str or value["status"] not in SAFE_STATUSES:
        raise ValueError("invalid_component_classification_status")
    for k in COUNT_FIELDS:
        if type(value[k]) is not int or not 0 <= value[k] <= 1024:
            raise ValueError("invalid_component_classification_counter")
    if any(value[k] is not False for k in PROOF_FLAGS):
        raise ValueError("unproven_component_semantics_or_pixels_claim")
    return {"status": value["status"], **{k: value[k] for k in COUNT_FIELDS}}


def classify_real_pairs(pairs, private_root: Path, *,
                        translator=translate,
                        old_reflector=safe_reflection,
                        raw_reflector=read_private,
                        classifier=classify_vf_components):
    if (type(pairs) is not list or len(pairs) != baseline.SOURCE_NORMAL_PASSES or
        not private_root.is_dir() or private_root.is_symlink()):
        raise ValueError("invalid_original_four_pass_component_scope")
    counts = Counter()
    for i, pair in enumerate(pairs):
        if (type(pair) is not tuple or len(pair) != 2 or
            any(type(code) is not bytes or not code for code in pair)):
            raise ValueError("invalid_private_original_compiled_component_pair")
        stages = {}
        for stage, code in ((1, pair[0]), (0, pair[1])):
            dest = private_root / ("source-pass-" + str(i) + "-stage-" + str(stage))
            dest.mkdir(exist_ok=False)
            generated = translator(code, stage, dest)
            if (type(generated) is not dict or
                any(generated.get(k) is not True for k in
                    ("vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid"))):
                raise ValueError("incomplete_original_DXBC_SPIRV_HLSL_component_pipeline")
            stages[stage] = {}
            for name, source in (("source", "original.spv"), ("roundtrip", "roundtrip.spv")):
                private_spv = dest / source
                old = old_reflector(private_spv)
                raw = raw_reflector(private_spv)
                if type(old) is not dict or not all(
                    type(old.get(k)) is list for k in ("inputs", "outputs")):
                    raise ValueError("missing_original_private_reflection_baseline")
                stages[stage][name] = {
                    side: sanitize_private_side(raw, old, side)
                    for side in ("inputs", "outputs")
                }
            counts["stage_spirv_source_and_roundtrip_reflections"] += 1
        for name in ("source", "roundtrip"):
            v = stages[1][name]["outputs"]
            f = stages[0][name]["inputs"]
            approved = safe_aggregate(classifier(v, f))
            counts[name + "_passes_classified"] += 1
            counts[name + "_status_" + approved["status"]] += 1
            for key in COUNT_FIELDS:
                counts[name + "_" + key] += approved[key]
    if (counts["source_passes_classified"] != baseline.SOURCE_NORMAL_PASSES or
        counts["roundtrip_passes_classified"] != baseline.SOURCE_NORMAL_PASSES or
        counts["stage_spirv_source_and_roundtrip_reflections"] !=
        2 * baseline.SOURCE_NORMAL_PASSES):
        raise ValueError("incomplete_original_four_pass_component_classification")
    named = tuple(name + "_status_" + s
                  for name in ("source", "roundtrip") for s in SAFE_STATUSES)
    totals = tuple(name + "_" + k
                   for name in ("source", "roundtrip") for k in COUNT_FIELDS)
    return {
        "schema_version": 1,
        "status": STATUS,
        "scope": "one_SHA_original_matched_DXBC_vertex_fragment_pair_per_Pass",
        "original_passes": baseline.SOURCE_NORMAL_PASSES,
        "original_stage_programs": 2 * baseline.SOURCE_NORMAL_PASSES,
        "counts": {k: counts[k] for k in (
            "source_passes_classified", "roundtrip_passes_classified",
            "stage_spirv_source_and_roundtrip_reflections",
            *named, *totals
        )},
        "SPIRV_component_typing_only_not_DXBC_semantic_identity": True,
        "interpolation_or_original_authored_ShaderLab_verified": False,
        "original_programs_private_bytes_names_hashes_published": False,
        "Unity_Vulkan_Adreno_device_pixels_verified": False,
        "game_assets_changed": False,
    }


def probe(source: Path, manifest: Path):
    for binary in baseline.TOOLS:
        if not shutil.which(binary):
            raise ValueError("missing_required_original_DXBC_SPIRV_tool")
    original_counts = {}
    report = original.load_original(source, manifest, private_slot_counts=original_counts)
    owner, obj_id = feasibility.selected_high_use(original_counts, report)
    candidate = source / "Raft_Data" / owner
    if (candidate.is_symlink() or
        fingerprint(candidate) != SHADER_OWNERS[owner]):
        raise ValueError("authentic_original_shader_owner_changed")
    import UnityPy
    objects = [o for o in UnityPy.load(str(candidate)).file.objects.values()
               if o.path_id == obj_id]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("original_shader48_exact_object_changed")
    tree = objects[0].read_typetree()
    platforms = [records(rows) for platform, rows in decoded_platforms(tree)
                 if platform == 4]
    if len(platforms) != 1:
        raise ValueError("missing_or_duplicate_original_D3D11_platform")
    parsed, table = tree.get("m_ParsedForm"), platforms[0]
    base = feasibility.summarize(parsed, table)
    if (base["original_source_Shader48_pass_count"] != baseline.SOURCE_NORMAL_PASSES or
        base["non_normal_passes_not_stage_linked"] != 0 or
        base["matched_vertex_fragment_permutation_pairs"] != baseline.SOURCE_TOTAL_MATCHED_VARIANTS or
        base["unmatched_vertex_permutations"] != baseline.SOURCE_UNMATCHED_VERTEX or
        base["unmatched_fragment_permutations"] != baseline.SOURCE_UNMATCHED_FRAGMENT):
        raise ValueError("original_921_source_fourpass_compiled_variant_baseline_changed")
    pairs = baseline.exact_pass_samples(parsed, table)
    with tempfile.TemporaryDirectory(prefix="t3-original921-vf-components-private-") as temp:
        result = classify_real_pairs(pairs, Path(temp))
    result.update({
        "original_scene_sources_SHA_authenticated": 6,
        "original_Shader_Material_owner_sources_SHA_authenticated": 4,
        "source_shader_original_renderer_material_slot_uses": 921,
        "original_source_matched_permutation_pairs_not_exhaustively_translated":
            baseline.SOURCE_TOTAL_MATCHED_VARIANTS,
        "unpaired_original_vertex_permutations_untranslated":
            baseline.SOURCE_UNMATCHED_VERTEX,
    })
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_private_fourpass_component_report_destination")
    try:
        report = probe(args.original, args.manifest)
    except Exception as err:
        # Do not log exceptions carrying private bytecode, paths, names or IDs.
        report = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "failure_exception_type": type(err).__name__,
                  "original_programs_private_bytes_names_hashes_published": False,
                  "Unity_Vulkan_Adreno_device_pixels_verified": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("T3_ORIGINAL_921_VF_COMPONENT_COVERAGE " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
