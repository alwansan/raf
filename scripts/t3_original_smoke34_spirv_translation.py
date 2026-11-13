#!/usr/bin/env python3
"""T3: SHA-authenticated smoke34 private two-pair original DXBC -> SPIR-V CPU probe.

Only source-authorized ZIP2 original owners are loaded. Paired keyword/player
bucket identities remain private. No DXBC, SPIR-V, HLSL, hashes, owner names,
PathIDs or reflected resource bindings are emitted in logs or public artifacts.
A valid Vulkan CPU translation is NOT a Unity shader or a device pixel fix.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from scripts import t3_original_smoke34_dxbc_program_inventory as original
from scripts.t3_smoke34_sameexport_shaderlab import original_private_smoke_target
from scripts.t3_original_renderer_shader_impact import SHADER_OWNERS_SELECTED
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import (
    linked_program, stage_variants, variant_key, reflection, interfaces_match,
)
from scripts.t3_original_particle108_spirv_translation import (
    _validate_reflection, IO_KEYS, IO_BOOLEAN,
)
from scripts.t3_stage_io_drift import classify_stage_io
from scripts.t3_spirv_interface_name_drift import (
    FIELDS as REFLECTED_NAME_FIELDS,
    BOOLEAN_FIELDS as REFLECTED_NAME_BOOLEAN,
    read_reflection as private_named_reflection,
    classify_reflected_names,
)

STATUS = "SHA_ORIGINAL_SMOKE34_TWO_KEYWORD_PAIRS_SPIRV_CPU_CLASSIFIED"
TOOLS = ("vkd3d-compiler", "spirv-val", "spirv-cross", "glslangValidator")
PAIRS = 2
TABLE_RECORDS = 8
MAX_STAGE_BYTES = 8 * 1024 * 1024
COUNT_KEYS = (
    "translation_attempts", "original_stage_spirv_vulkan11_valid",
    "hlsl_recovered", "roundtrip_stage_spirv_vulkan11_valid",
    "original_stage_reflection_valid", "roundtrip_stage_reflection_valid",
    "original_roundtrip_io_equal", "original_roundtrip_resource_shapes_equal",
    "original_stage_pairs_interfaces_compared", "original_stage_pairs_compatible",
    "roundtrip_stage_pairs_interfaces_compared", "roundtrip_stage_pairs_compatible",
    "pairs_both_original_spirv_valid", "pairs_both_roundtrip_spirv_valid",
)
IO_COUNT_KEYS = tuple(
    "io_drift_" + side + "_" + key
    for side in ("inputs", "outputs") for key in IO_KEYS
)
NAME_COUNT_KEYS = tuple(
    "name_anchor_" + side + "_" + field
    for side in ("inputs", "outputs") for field in REFLECTED_NAME_FIELDS
)
SAFE_FALSE = {
    "source_DXBC_semantic_register_mapping_verified": False,
    "compiler_generated_names_are_original_semantics_verified": False,
    "native_Unity_Android_Adreno_pixels_verified": False,
    "authored_original_ShaderLab_restored": False,
    "original_smoke_identity_equals_phone_square_verified": False,
    "original_shader_programs_hashes_ids_or_private_names_published": False,
    "unity_game_assets_modified": False,
}


def exact_two_stage_links(parsed, table, *, linker=linked_program):
    """Reject unequal, absent, duplicate, or ambiguous original VS/FS variants."""
    if (type(parsed) is not dict or
        type(parsed.get("m_SubShaders")) is not list or
        len(parsed["m_SubShaders"]) != 1 or
        type(parsed["m_SubShaders"][0]) is not dict or
        type(parsed["m_SubShaders"][0].get("m_Passes")) is not list or
        len(parsed["m_SubShaders"][0]["m_Passes"]) != 1):
        raise ValueError("smoke34_invalid_original_shader_pass_graph")
    p = parsed["m_SubShaders"][0]["m_Passes"][0]
    if type(p) is not dict or p.get("m_Type") != 0:
        raise ValueError("smoke34_original_pass_not_normal")
    if (type(table) is not list or len(table) != TABLE_RECORDS or
        any(type(row) is not tuple or len(row) != 2 or
            type(row[0]) is not int or row[0] < 0 or
            type(row[1]) is not bytes or not row[1] for row in table)):
        raise ValueError("smoke34_changed_original_dxbc_table")
    stages = {}
    for field, kind in (("progVertex", 1), ("progFragment", 0)):
        program = p.get(field)
        if type(program) is not dict:
            raise ValueError("smoke34_missing_original_stage")
        rows = stage_variants(program)
        if len(rows) != PAIRS:
            raise ValueError("smoke34_changed_original_stage_variant_count")
        indexed = {}
        for bucket, ordinal, meta in rows:
            if (type(ordinal) is not int or ordinal < 0 or
                type(meta) is not dict or
                (bucket is not None and
                 (type(bucket) is not int or bucket < 0))):
                raise ValueError("smoke34_invalid_original_stage_metadata")
            key = (bucket, variant_key(meta))
            if key in indexed:
                raise ValueError("smoke34_duplicate_original_keyword_bucket")
            indexed[key] = (ordinal, meta)
        stages[kind] = indexed
    if set(stages[1]) != set(stages[0]):
        raise ValueError("smoke34_original_keyword_bucket_pair_mismatch")
    pairs = []
    for key, (vert_ordinal, vert_meta) in stages[1].items():
        fragment_ordinal, fragment_meta = stages[0][key]
        vs, _ = linker(vert_meta, table, 1)
        fs, _ = linker(fragment_meta, table, 0)
        if (type(vs) is not bytes or type(fs) is not bytes or
            not vs or not fs or
            max(len(vs), len(fs)) > MAX_STAGE_BYTES):
            raise ValueError("smoke34_untrusted_original_dxbc_program")
        pairs.append(((vs, key[0], vert_ordinal), (fs, key[0], fragment_ordinal)))
    if len(pairs) != PAIRS:
        raise ValueError("smoke34_incomplete_source_keyword_pairs")
    return pairs


def exact_two_pairs(parsed, table, *, linker=linked_program):
    """Return original bytecode only for the existing CPU probe."""
    return [(vs[0], fs[0]) for vs, fs in exact_two_stage_links(parsed, table, linker=linker)]


def evaluate(pairs, temporary, *, translator=translate,
             reflector=reflection, checker=interfaces_match,
             io_classifier=classify_stage_io,
             named_reflector=private_named_reflection,
             name_classifier=classify_reflected_names):
    """Only non-private aggregate counters, never per-program translator output."""
    if (type(pairs) is not list or len(pairs) != PAIRS or
        not isinstance(temporary, Path) or not temporary.is_dir() or
        temporary.is_symlink()):
        raise ValueError("smoke34_invalid_private_translation_scope")
    counts = Counter()
    for index, pair in enumerate(pairs):
        if (type(pair) is not tuple or len(pair) != 2 or
            any(type(code) is not bytes or not code or
                len(code) > MAX_STAGE_BYTES for code in pair)):
            raise ValueError("smoke34_untrusted_private_pair")
        stages = {}
        for stage, code in ((1, pair[0]), (0, pair[1])):
            folder = temporary / ("pair-" + str(index) + "-stage-" + str(stage))
            folder.mkdir(exist_ok=False)
            details = translator(code, stage, folder)
            if (type(details) is not dict or
                ("stage" in details and details["stage"] != stage) or
                any(type(details.get(key)) is not bool for key in
                    ("vulkan11_valid", "hlsl_recovered",
                     "roundtrip_vulkan11_valid")) or
                (details["hlsl_recovered"] and not details["vulkan11_valid"]) or
                (details["roundtrip_vulkan11_valid"] and
                 not details["hlsl_recovered"])):
                raise ValueError("smoke34_invalid_private_translator_result")
            counts["translation_attempts"] += 1
            counts["original_stage_spirv_vulkan11_valid"] += details["vulkan11_valid"]
            counts["hlsl_recovered"] += details["hlsl_recovered"]
            counts["roundtrip_stage_spirv_vulkan11_valid"] += details["roundtrip_vulkan11_valid"]
            reflected = {}
            for key, allowed, filename in (
                ("original", details["vulkan11_valid"], "original.spv"),
                ("roundtrip", details["roundtrip_vulkan11_valid"], "roundtrip.spv"),
            ):
                if allowed:
                    try:
                        reflected[key] = _validate_reflection(reflector(folder / filename))
                        counts[key + "_stage_reflection_valid"] += 1
                    except (ValueError, OSError, TypeError, RuntimeError, KeyError):
                        # No raw private shader paths/errors published.
                        counts[key + "_stage_reflection_invalid"] += 1
            if "original" in reflected and "roundtrip" in reflected:
                a, b = reflected["original"], reflected["roundtrip"]
                counts["original_roundtrip_io_equal"] += all(
                    sorted(a[side], key=lambda x: x["location"]) ==
                    sorted(b[side], key=lambda x: x["location"])
                    for side in ("inputs", "outputs"))
                counts["original_roundtrip_resource_shapes_equal"] += (
                    a["resource_slots"] == b["resource_slots"])
                classified = io_classifier(a, b)
                expected = {side + "_" + key
                            for side in ("inputs", "outputs") for key in IO_KEYS}
                if type(classified) is not dict or set(classified) != expected:
                    raise ValueError("smoke34_invalid_private_io_drift_category_shape")
                for name, amount in classified.items():
                    category = name.split("_", 1)[1]
                    limit = 1 if category in IO_BOOLEAN else 256
                    if type(amount) is not int or not 0 <= amount <= limit:
                        raise ValueError("smoke34_invalid_private_io_drift_category_value")
                    counts["io_drift_" + name] += amount
                # Private reflected variable names are compiler hints, not DXBC
                # register semantics. No names, GUIDs or per-stage IDs exit CI.
                named_source = named_reflector(folder / "original.spv")
                named_derived = named_reflector(folder / "roundtrip.spv")
                named = name_classifier(named_source, named_derived, a, b)
                allowed_names = {side + "_" + field
                                 for side in ("inputs", "outputs")
                                 for field in REFLECTED_NAME_FIELDS}
                if type(named) is not dict or set(named) != allowed_names:
                    raise ValueError("smoke34_untrusted_private_name_anchor_schema")
                for key, value in named.items():
                    field = key.split("_", 1)[1]
                    limit = 1 if field in REFLECTED_NAME_BOOLEAN else 256
                    if type(value) is not int or not 0 <= value <= limit:
                        raise ValueError("smoke34_untrusted_private_name_anchor_count")
                    counts["name_anchor_" + key] += value
                counts["stages_name_anchor_classified"] += 1
            stages[stage] = {"flags": details, "reflection": reflected}
        vert, frag = stages[1], stages[0]
        for key, prefix in (("original", "original"), ("roundtrip", "roundtrip")):
            if key in vert["reflection"] and key in frag["reflection"]:
                counts[prefix + "_stage_pairs_interfaces_compared"] += 1
                outcome = checker(vert["reflection"][key], frag["reflection"][key])
                if type(outcome) is not bool:
                    raise ValueError("smoke34_invalid_private_stage_interface_check")
                counts[prefix + "_stage_pairs_compatible"] += outcome
        if vert["flags"]["vulkan11_valid"] and frag["flags"]["vulkan11_valid"]:
            counts["pairs_both_original_spirv_valid"] += 1
        if (vert["flags"]["roundtrip_vulkan11_valid"] and
            frag["flags"]["roundtrip_vulkan11_valid"]):
            counts["pairs_both_roundtrip_spirv_valid"] += 1
    if counts["translation_attempts"] != PAIRS * 2:
        raise ValueError("smoke34_incomplete_private_translation_attempts")
    return {
        "schema_version": 1,
        "status": STATUS,
        "original_source_shader_role": "smoke_named_17_renderers_34_material_slots",
        "original_sha_pinned_scenes": 6,
        "original_sha_pinned_shader_material_owners": 4,
        "original_d3d11_table_records": TABLE_RECORDS,
        "original_keyword_matched_vertex_fragment_pairs": PAIRS,
        "source_original_pass_RGB_ColorMask": True,
        "source_original_pass_alpha_dependent_color_and_alpha": True,
        "source_original_pass_ZWrite_OFF": True,
        "counts": {key: int(counts[key]) for key in
                   COUNT_KEYS + IO_COUNT_KEYS + NAME_COUNT_KEYS +
                   ("stages_name_anchor_classified",)},
        **SAFE_FALSE,
    }


def probe(root, manifest, *, translator=translate, reflector=reflection,
          checker=interfaces_match):
    for binary in TOOLS:
        if shutil.which(binary) is None:
            raise ValueError("smoke34_missing_cpu_translation_tool")
    import UnityPy
    identity, state = original_private_smoke_target(root, manifest)
    if (type(state) is not dict or
        state.get("original_pass_color_mask_shaderlab_channels") != "RGB" or
        state.get("original_pass_color_blend_category") != "ALPHA_DEPENDENT" or
        state.get("original_pass_alpha_channel_blend_category") != "ALPHA_DEPENDENT" or
        state.get("original_pass_depth_write_category") != "OFF"):
        raise ValueError("smoke34_changed_original_fixed_pass")
    owner, pid = identity
    if owner not in SHADER_OWNERS_SELECTED:
        raise ValueError("smoke34_untrusted_original_shader_owner")
    path = root / "Raft_Data" / owner
    if any(p.is_symlink() for p in (path, *path.parents)) or (
        fingerprint(path) != SHADER_OWNERS[owner]):
        raise ValueError("smoke34_changed_original_source_SHA")
    matches = [obj for obj in UnityPy.load(str(path)).file.objects.values()
               if obj.path_id == pid]
    if len(matches) != 1 or matches[0].type.name != "Shader":
        raise ValueError("smoke34_original_shader_identity_unresolved")
    tree = matches[0].read_typetree()
    tables = [records(segments) for platform, segments in decoded_platforms(tree)
              if platform == 4]
    if len(tables) != 1:
        raise ValueError("smoke34_original_d3d11_platform_not_unique")
    baseline = original.classify(tables[0], tree.get("m_ParsedForm"))
    if (baseline.get("status") != original.STATUS or
        baseline.get("original_D3D11_platform_table_records") != TABLE_RECORDS or
        baseline.get("genuine_D3D11_vertex_stage_variant_records") != PAIRS or
        baseline.get("genuine_D3D11_fragment_stage_variant_records") != PAIRS or
        baseline.get("matched_vertex_fragment_permutation_pairs") != PAIRS or
        baseline.get("unmatched_vertex_permutations") != 0 or
        baseline.get("unmatched_fragment_permutations") != 0):
        raise ValueError("smoke34_original_stage_baseline_drift")
    pairs = exact_two_pairs(tree.get("m_ParsedForm"), tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-smoke34-private-spv-") as folder:
        result = evaluate(pairs, Path(folder), translator=translator,
                          reflector=reflector, checker=checker)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original", "manifest", "out"):
        parser.add_argument("--" + key, required=True, type=Path)
    args = parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("smoke34_unsafe_report_destination")
    try:
        report = probe(args.original, args.manifest)
    except Exception as exc:
        report = {
            "schema_version": 1, "status": "INCONCLUSIVE",
            "failure_type": type(exc).__name__,
            **SAFE_FALSE,
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print("T3_SMOKE34_ORIGINAL_SPIRV_CPU " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
