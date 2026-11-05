#!/usr/bin/env python3
"""Bounded genuine original 921-use Shader48 4-pass DXBC translation/reflector.

This tool never exports raw game shaders, DXBC, SPIR-V, regenerated HLSL,
private names/IDs/GUIDs or per-program hashes. It chooses only one *exactly
matched* source Vertex/Fragment permutation per original Pass, preserving all
other original permutations as NOT translated. Results are technical CPU
capability diagnostics; no ShaderLab installation, numerical parity, full
Unity import or Android pixels are claimed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from scripts import t3_original_top_shader_dxbc_feasibility as previous
from scripts import t3_original_renderer_shader_impact as original
from scripts.t3_stage_io_drift import classify_stage_io
from scripts.t3_spirv_interface_name_drift import (
    BOOLEAN_FIELDS as NAME_BOOLEAN_FIELDS,
    FIELDS as NAME_FIELDS,
    classify_reflected_names,
    read_reflection as read_private_name_reflection,
)
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import (
    linked_program, stage_variants, variant_key, reflection, interfaces_match,
)

STATUS = "ORIGINAL_TOP_921_SHADER48_FOUR_PASS_DXBC_TRANSLATION_MEASURED"
TOOLS = ("vkd3d-compiler", "spirv-val", "spirv-cross", "glslangValidator")
SOURCE_NORMAL_PASSES = 4
SOURCE_TOTAL_MATCHED_VARIANTS = 33
SOURCE_UNMATCHED_VERTEX = 8
SOURCE_UNMATCHED_FRAGMENT = 0
IO_STATUS = "ORIGINAL_TOP_921_SOURCE_TO_ROUNDTRIP_STAGE_IO_DRIFT_CLASSIFIED"
NAME_STATUS = "ORIGINAL_TOP_921_SPIRV_CROSS_REFLECTED_NAME_LOCATION_DIAGNOSTIC_ONLY"
IO_CATEGORY_KEYS = (
    "identical", "original_slots", "roundtrip_slots", "removed_locations",
    "added_locations", "same_location_type_changes", "type_multiset_equal",
    "location_only_remap_candidate",
)
IO_BOOLEAN_KEYS = frozenset((
    "identical", "type_multiset_equal", "location_only_remap_candidate",
))


def _safe_io_counts(raw):
    """Validate scheduled T3 classifier output, never copy raw private fields."""
    expected = {side + "_" + name
                for side in ("inputs", "outputs") for name in IO_CATEGORY_KEYS}
    if type(raw) is not dict or set(raw) != expected:
        raise ValueError("untrusted_private_stage_IO_classifier_output")
    result = {}
    for side in ("inputs", "outputs"):
        for key in IO_CATEGORY_KEYS:
            label = side + "_" + key
            value = raw[label]
            if (type(value) is not int or value < 0 or
                    value > (1 if key in IO_BOOLEAN_KEYS else 256)):
                raise ValueError("invalid_public_stage_IO_classifier_counter")
            result[label] = value
    return result



def _safe_name_counts(raw):
    """Only known numeric aggregate keys escape private per-stage reflections."""
    expected = {side + "_" + key
                for side in ("inputs", "outputs") for key in NAME_FIELDS}
    if type(raw) is not dict or set(raw) != expected:
        raise ValueError("untrusted_private_SPIRV_name_classifier_output")
    safe = {}
    for side in ("inputs", "outputs"):
        for key in NAME_FIELDS:
            field = side + "_" + key
            value = raw[field]
            if (type(value) is not int or value < 0 or
                    value > (1 if key in NAME_BOOLEAN_FIELDS else 256)):
                raise ValueError("invalid_public_SPIRV_name_classifier_counter")
            safe[field] = value
    return safe


def exact_pass_samples(parsed: dict, table: list,
                       *, source_link=linked_program) -> list[tuple[bytes, bytes]]:
    """Private code pairs; player-bucket AND all keyword/tier keys must agree.

    Refuses duplicates or unsupported pass types. This stricter bucket-aware
    contract must not silently use the first stage or create missing variants.
    """
    if type(parsed) is not dict or type(parsed.get("m_SubShaders")) is not list:
        raise ValueError("untrusted_original_top_Shader_pass_graph")
    subshaders = parsed["m_SubShaders"]
    if not subshaders or type(table) is not list or not table:
        raise ValueError("missing_original_pass_graph_or_D3D11_table")
    private_samples = []
    pass_count = 0
    for sub in subshaders:
        if type(sub) is not dict or type(sub.get("m_Passes")) is not list:
            raise ValueError("invalid_original_SubShader_structure")
        for shader_pass in sub["m_Passes"]:
            pass_count += 1
            if (type(shader_pass) is not dict or
                type(shader_pass.get("m_Type")) is not int or
                shader_pass["m_Type"] != 0):
                raise ValueError("non_normal_original_Pass_cannot_be_faked")
            stage_tables = {}
            for field, stage in (("progVertex", 1), ("progFragment", 0)):
                program = shader_pass.get(field)
                if type(program) is not dict:
                    raise ValueError("missing_original_Pass_stage")
                rows = stage_variants(program)
                if not rows or len(rows) > 256:
                    raise ValueError("empty_or_unbounded_source_Pass_stage_variants")
                by_key = {}
                for bucket, ordinal, metadata in rows:
                    if (type(metadata) is not dict or type(ordinal) is not int
                        or ordinal < 0 or
                        (bucket is not None and (type(bucket) is not int or bucket < 0))):
                        raise ValueError("malformed_original_variant_metadata")
                    key = (bucket, variant_key(metadata))
                    if key in by_key:
                        raise ValueError("duplicated_original_stage_player_bucket_and_permutation")
                    by_key[key] = metadata
                stage_tables[stage] = by_key
            matched = stage_tables[1].keys() & stage_tables[0].keys()
            if not matched:
                raise ValueError("original_Pass_has_no_exact_player_bucket_and_permutation_pair")
            # Keep deterministic original player-table enumeration order, not
            # sorted private metadata or a guessed common fragment fallback.
            selected = next(key for key in stage_tables[1] if key in matched)
            vertex, _ = source_link(stage_tables[1][selected], table, 1)
            fragment, _ = source_link(stage_tables[0][selected], table, 0)
            if (type(vertex) is not bytes or not vertex or
                type(fragment) is not bytes or not fragment):
                raise ValueError("not_two_real_original_compiled_source_stages")
            private_samples.append((vertex, fragment))
    if pass_count != SOURCE_NORMAL_PASSES or len(private_samples) != SOURCE_NORMAL_PASSES:
        raise ValueError("unexpected_original_four_pass_921_source_scope")
    return private_samples


def _as_reflection(row):
    if (type(row) is not dict or
        any(type(row.get(k)) not in (list, dict) for k in
            ("inputs", "outputs", "resource_slots"))):
        raise ValueError("unexpected_original_SPIRV_reflection_shape")
    return row


def evaluate_samples(private_code_pairs, private_root: Path, *,
                     translator=translate, reflector=reflection,
                     pair_checker=interfaces_match, io_classifier=None,
                     name_classifier=None, named_reflector=read_private_name_reflection) -> dict:
    """Sample exactly 1 real linked pair/Pass; aggregate booleans only.

    Tools produce files solely inside caller's private temporary directory.
    Returned result has no source names, per-program hashes, compiler stdout,
    source paths or code; failures remain explicit counts.
    """
    if (type(private_code_pairs) is not list or
        len(private_code_pairs) != SOURCE_NORMAL_PASSES or
        not private_root.is_dir() or private_root.is_symlink()):
        raise ValueError("bad_private_four_pass_diagnostic_scope")
    if name_classifier is not None and io_classifier is None:
        raise ValueError("reflected_name_comparison_requires_concurrent_stage_IO_baseline")
    counters = Counter()
    for index, pair in enumerate(private_code_pairs):
        if (type(pair) is not tuple or len(pair) != 2 or
            any(type(code) is not bytes or not code for code in pair)):
            raise ValueError("not_source_verified_vertex_fragment_pair")
        counters["original_passes_sampled"] += 1
        stages = {}
        for stage, original_code in ((1, pair[0]), (0, pair[1])):
            dest = private_root / ("sample-" + str(index) + "-stage-" + str(stage))
            dest.mkdir(exist_ok=False)
            # W1 genuine DXBC -> SPIR-V -> HLSL -> SPIR-V pipeline. The
            # report from it contains per-code hashes. Never put it in output!
            result = translator(original_code, stage, dest)
            if (type(result) is not dict or
                any(type(result.get(field)) is not bool for field in (
                    "vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid"))):
                raise ValueError("untrusted_DXBC_translation_result_shape")
            counters["original_stage_translation_attempts"] += 1
            counters["genuine_stage_spirv11_valid"] += int(result["vulkan11_valid"])
            counters["genuine_stage_hlsl_recovered"] += int(result["hlsl_recovered"])
            counters["genuine_stage_hlsl_roundtrip_spirv11_valid"] += int(
                result["roundtrip_vulkan11_valid"])
            stages[stage] = {"result": result, "path": dest}
            if result["vulkan11_valid"]:
                try:
                    stages[stage]["original_reflection"] = _as_reflection(
                        reflector(dest / "original.spv"))
                    counters["original_SPIRV_stage_reflections_verified"] += 1
                except (ValueError, OSError, KeyError, TypeError, RuntimeError):
                    counters["original_SPIRV_stage_reflection_failures"] += 1
            if result["roundtrip_vulkan11_valid"]:
                try:
                    stages[stage]["roundtrip_reflection"] = _as_reflection(
                        reflector(dest / "roundtrip.spv"))
                    counters["roundtrip_SPIRV_stage_reflections_verified"] += 1
                except (ValueError, OSError, KeyError, TypeError, RuntimeError):
                    counters["roundtrip_SPIRV_stage_reflection_failures"] += 1
            if "original_reflection" in stages[stage] and "roundtrip_reflection" in stages[stage]:
                a, b = stages[stage]["original_reflection"], stages[stage]["roundtrip_reflection"]
                counters["stage_original_roundtrip_resource_binding_shape_equal"] += (
                    a["resource_slots"] == b["resource_slots"])
                counters["stage_original_roundtrip_io_location_types_equal"] += (
                    a["inputs"] == b["inputs"] and a["outputs"] == b["outputs"])
                counters["stage_original_roundtrip_reflection_pairs_compared"] += 1
                if io_classifier is not None:
                    safe = _safe_io_counts(io_classifier(a, b))
                    counters["io_drift_stage_reflection_pairs_classified"] += 1
                    for field, amount in safe.items():
                        counters["io_drift_" + field] += amount
                if name_classifier is not None:
                    source_full = named_reflector(dest / "original.spv")
                    derived_full = named_reflector(dest / "roundtrip.spv")
                    private_result = name_classifier(source_full, derived_full, a, b)
                    safe_named = _safe_name_counts(private_result)
                    counters["name_drift_stage_reflection_pairs_classified"] += 1
                    for field, amount in safe_named.items():
                        counters["name_drift_" + field] += amount
        v, f = stages[1], stages[0]
        if v["result"]["vulkan11_valid"] and f["result"]["vulkan11_valid"]:
            counters["passes_with_both_genuine_spirv_stages_valid"] += 1
        if v["result"]["roundtrip_vulkan11_valid"] and f["result"]["roundtrip_vulkan11_valid"]:
            counters["passes_with_both_hlsl_roundtrip_stages_valid"] += 1
        if "original_reflection" in v and "original_reflection" in f:
            counters["passes_with_source_SPIRV_vertex_fragment_interface_compared"] += 1
            counters["passes_with_source_SPIRV_vertex_fragment_interface_matching"] += bool(
                pair_checker(v["original_reflection"], f["original_reflection"]))
        if "roundtrip_reflection" in v and "roundtrip_reflection" in f:
            counters["passes_with_roundtrip_SPIRV_vertex_fragment_interface_compared"] += 1
            counters["passes_with_roundtrip_SPIRV_vertex_fragment_interface_matching"] += bool(
                pair_checker(v["roundtrip_reflection"], f["roundtrip_reflection"]))
    selected = (
        "original_passes_sampled", "original_stage_translation_attempts",
        "genuine_stage_spirv11_valid", "genuine_stage_hlsl_recovered",
        "genuine_stage_hlsl_roundtrip_spirv11_valid",
        "original_SPIRV_stage_reflections_verified",
        "original_SPIRV_stage_reflection_failures",
        "roundtrip_SPIRV_stage_reflections_verified",
        "roundtrip_SPIRV_stage_reflection_failures",
        "passes_with_both_genuine_spirv_stages_valid",
        "passes_with_both_hlsl_roundtrip_stages_valid",
        "stage_original_roundtrip_reflection_pairs_compared",
        "stage_original_roundtrip_resource_binding_shape_equal",
        "stage_original_roundtrip_io_location_types_equal",
        "passes_with_source_SPIRV_vertex_fragment_interface_compared",
        "passes_with_source_SPIRV_vertex_fragment_interface_matching",
        "passes_with_roundtrip_SPIRV_vertex_fragment_interface_compared",
        "passes_with_roundtrip_SPIRV_vertex_fragment_interface_matching",
    )
    io_count = counters["io_drift_stage_reflection_pairs_classified"]
    if io_classifier is not None and io_count != 2 * SOURCE_NORMAL_PASSES:
        # Failing closed is important: zero classified I/O stages or a partial
        # stage set must never look like resolved cause of a prior 0/8 drift.
        raise ValueError("incomplete_real_original_roundtrip_stage_IO_classification")
    if name_classifier is not None and (
        counters["name_drift_stage_reflection_pairs_classified"] !=
        2 * SOURCE_NORMAL_PASSES):
        raise ValueError("incomplete_original_vs_roundtrip_reflected_name_classification")
    if name_classifier is not None:
        selected += ("name_drift_stage_reflection_pairs_classified",)
        selected += tuple("name_drift_" + side + "_" + key
                          for side in ("inputs", "outputs") for key in NAME_FIELDS)
    if io_classifier is not None:
        selected += ("io_drift_stage_reflection_pairs_classified",)
        selected += tuple("io_drift_" + side + "_" + name
                          for side in ("inputs", "outputs") for name in IO_CATEGORY_KEYS)
    return {
        "schema_version": 1,
        "status": (NAME_STATUS if name_classifier is not None else
                   IO_STATUS if io_classifier is not None else STATUS),
        "scope": "one_original_D3D11_vertex_fragment_pair_per_original_pass",
        "source_to_roundtrip_reflected_name_comparison_opt_in":
            name_classifier is not None,
        "reflected_names_are_NOT_authenticated_source_DXBC_semantics": True,
        "source_to_roundtrip_reflected_name_all_eight_stages_compared":
            name_classifier is not None and
            counters["name_drift_stage_reflection_pairs_classified"] ==
            2 * SOURCE_NORMAL_PASSES,
        "source_to_roundtrip_io_drift_classification_opt_in": io_classifier is not None,
        "source_to_roundtrip_io_drift_all_eight_stages_classified":
            io_classifier is not None and io_count == 2 * SOURCE_NORMAL_PASSES,
        "source_variant_pairs_from_prior_full_linkage": SOURCE_TOTAL_MATCHED_VARIANTS,
        "source_unpaired_original_vertex_variants_not_translated": SOURCE_UNMATCHED_VERTEX,
        "source_unpaired_original_fragment_variants_not_translated": SOURCE_UNMATCHED_FRAGMENT,
        "counts": {k: int(counters[k]) for k in selected},
        "full_original_variant_population_translated": False,
        "original_shader_programs_bytes_or_hashes_published": False,
        "matched_compiled_pairs_are_not_original_Authored_ShaderLab": True,
        "HLSL_translated_code_is_not_original_author_source": True,
        "resource_samplers_uniform_matrices_or_render_state_verified": False,
        "native_Unity_Android_Adreno_pixels_verified": False,
        "source_game_assets_changed": False,
    }


def probe(source: Path, manifest: Path, *, translate_fn=translate,
          reflect_fn=reflection, pair_check_fn=interfaces_match,
          io_classifier=None, name_classifier=None,
          named_reflector=read_private_name_reflection):
    for binary in TOOLS:
        if not shutil.which(binary):
            raise ValueError("missing_required_DXBC_SPIRV_tool")
    private = {}
    source_report = original.load_original(source, manifest, private_slot_counts=private)
    owner, obj_id = previous.selected_high_use(private, source_report)
    path = source / "Raft_Data" / owner
    if (path.is_symlink() or fingerprint(path) != SHADER_OWNERS[owner]):
        raise ValueError("unverified_original_high_use_Shader_owner")
    import UnityPy
    objects = [o for o in UnityPy.load(str(path)).file.objects.values()
               if o.path_id == obj_id]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("original_high_use_Shader48_identity_changed")
    tree = objects[0].read_typetree()
    tables = [records(segments) for platform, segments in decoded_platforms(tree)
              if platform == 4]
    if len(tables) != 1:
        raise ValueError("missing_or_ambiguous_original_D3D11_platform")
    parsed, entries = tree.get("m_ParsedForm"), tables[0]
    baseline = previous.summarize(parsed, entries)
    if (baseline["original_source_Shader48_pass_count"] != SOURCE_NORMAL_PASSES or
        baseline["non_normal_passes_not_stage_linked"] != 0 or
        baseline["matched_vertex_fragment_permutation_pairs"] != SOURCE_TOTAL_MATCHED_VARIANTS or
        baseline["unmatched_vertex_permutations"] != SOURCE_UNMATCHED_VERTEX or
        baseline["unmatched_fragment_permutations"] != SOURCE_UNMATCHED_FRAGMENT):
        raise ValueError("original_authentic_921_Shader48_pass_variant_baseline_drift")
    pairs = exact_pass_samples(parsed, entries)
    with tempfile.TemporaryDirectory(prefix="t3-original-921-stage-private-") as private_temp:
        report = evaluate_samples(pairs, Path(private_temp),
                                  translator=translate_fn, reflector=reflect_fn,
                                  pair_checker=pair_check_fn, io_classifier=io_classifier,
                                  name_classifier=name_classifier,
                                  named_reflector=named_reflector)
    report.update({
        "original_scene_sources_SHA_authenticated": 6,
        "original_Shader_or_Material_owners_SHA_authenticated": 4,
        "actual_selected_original_Shader48_renderer_slot_use": 921,
        "original_D3D11_compiled_program_table_records": len(entries),
        "source_passes_original": SOURCE_NORMAL_PASSES,
    })
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--classify-reflected-names", action="store_true",
                   help="Private SPIRV-Cross reflected I/O name+type/location comparison; not source DXBC semantics")
    p.add_argument("--classify-io-drift", action="store_true",
                   help="Opt-in: classify original/roundtrip SPIR-V stage I/O location and type drift")
    a = p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or
        a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_private_921_shader_translation_report_destination")
    try:
        r = probe(a.original, a.manifest,
                  io_classifier=classify_stage_io if
                      (a.classify_io_drift or a.classify_reflected_names) else None,
                  name_classifier=classify_reflected_names if
                      a.classify_reflected_names else None)
    except Exception as err:
        r = {
            "schema_version": 1, "status": "INCONCLUSIVE",
            "exception_type": type(err).__name__,
            "original_shader_programs_bytes_or_hashes_published": False,
            "native_Unity_Android_Adreno_pixels_verified": False,
        }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("T3_ORIGINAL_921_FOURPASS_TRANSLATION " + json.dumps(r, sort_keys=True))
    expected = (NAME_STATUS if a.classify_reflected_names else
                IO_STATUS if a.classify_io_drift else STATUS)
    return 0 if r["status"] == expected else 2


if __name__ == "__main__":
    raise SystemExit(main())
