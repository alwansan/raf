"""Translate SHA-authenticated NEXT23b stages privately; publish numeric proof only.

This source-only step composes private ShaderLab without installation or Unity,
GUID restoration, rendering or device compatibility.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import traceback

from scripts.gt_next23b_source_topology_census import select_remaining_23_source_owners
from scripts.gt_rank_all82_original_shader_names_after_nine import gather
from scripts.gt_stage_serialized_owners import read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.gt_original_921_all_variants import enumerate_all, stage_parameter_records
from scripts.gt_original_921_keyword_routes import keyword_routes, compile_routed_stages, shaderlab_layout
from scripts.gt_original_921_shaderlab import compose, verify_entrypoints, engine_route_keys, verified_source_next23b_pass_modes
from scripts.t3_original_top_shader_dxbc_feasibility import summarize
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate

STATUS = "GT_NEXT23B_SHA_ORIGINAL_PRIVATE_STAGES_AND_SHADERLAB_COMPOSED_VALIDATED"
FIELDS = ("original_source_Shader48_pass_count",
          "matched_vertex_fragment_permutation_pairs",
          "unmatched_vertex_permutations", "unmatched_fragment_permutations",
          "distinct_original_linked_D3D11_programs")
EXPECTED = (4, 1156, 0, 0, 134)
COMPILER_FIELDS = ("vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid")


def validate_topology(profile):
    if any(type(profile.get(k)) is not int or profile[k] != v
           for k, v in zip(FIELDS, EXPECTED)):
        raise ValueError("authenticated_original_next23b_topology_drift")


def recover_programs(distinct, private, translator=translate):
    if len(distinct) != 134:
        raise ValueError("original_next23b_distinct_program_population_drift")
    counts = Counter()
    refs = {}
    for index, (ident, record) in enumerate(distinct.items()):
        folder = private / ("program-%03d" % index)
        folder.mkdir(mode=0o700)
        result = translator(record["source_code"], record["stage"], folder)
        if not isinstance(result, dict) or any(type(result.get(k)) is not bool for k in COMPILER_FIELDS):
            raise ValueError("untrusted_next23b_compiler_result")
        refs[ident] = folder.name
        counts["attempted"] += 1
        for key in COMPILER_FIELDS:
            counts[key] += int(result[key])
        counts["all_three_valid"] += int(all(result[k] for k in COMPILER_FIELDS))
    return refs, counts



def compose_private(parsed, paired, orphans, passes, table, refs, private, report, *, engine_keywords=False):
    """Keep every source route; stop on any semantic or CBuffer proof failure."""
    checkpoint = 'source_keyword_routes'
    report['status'] = 'INCONCLUSIVE_NEXT23B_PRIVATE_COMPOSITION'
    try:
        packet, routing = keyword_routes(parsed, paired, orphans, passes)
        route_counts = routing['source_exact_keyword_routes_by_pass']
        if (len(packet) != 4 or len(route_counts) != 4
                or any(type(n) is not int or n <= 0 for n in route_counts)
                or sum(route_counts) != 1156
                or [len(row['routes']) for row in packet] != route_counts):
            raise ValueError('next23b_complete_source_route_population_required')
        for row in packet:
            for route in row['routes']:
                for stage in ('vs', 'fs'):
                    route[stage] = refs[route[stage]]
        checkpoint = 'source_property_and_pass_layout'
        properties = parsed.get('m_PropInfo', {}).get('m_Props', [])
        if type(properties) is not list:
            raise ValueError('invalid_next23b_source_properties')
        layout, _ = shaderlab_layout(parsed, passes, expected_property_count=len(properties),
                                      allow_original_per_renderer_and_drawer=True,
                                      allow_next23b_texture_hdr_flags=True)
        (private / 'original-private-keyword-routes.json').write_text(json.dumps(packet, sort_keys=True) + '\n', encoding='utf-8')
        (private / 'original-private-layout.txt').write_text(layout, encoding='utf-8')
        checkpoint = 'compile_all_source_keyword_routes'
        compiled = compile_routed_stages(packet, private)
        if type(compiled) is not int or compiled != 2312:
            raise ValueError('next23b_complete_routed_stage_compile_required')
        report['private_exact_keyword_routed_stages_compiled'] = compiled
        checkpoint = 'source_CB_sampler_and_varying_bindings'
        named = stage_parameter_records(paired, orphans, passes, table, private, refs)
        if named.get('original_variant_stages_with_parameter_records') != 2312:
            raise ValueError('next23b_all_stage_parameter_records_required')
        report['source_variant_named_CB_sampler_stage_bindings_verified'] = True
        for key in ('original_variant_stages_with_parameter_records',
                    'original_vertex_fragment_varying_records_matched',
                    'named_constant_buffer_reflected_offsets_verified'):
            value = named[key]
            if type(value) is not int or value < 0:
                raise ValueError('invalid_next23b_binding_proof_counter')
            report[key] = value
        checkpoint = 'compose_source_four_pass_shaderlab'
        shader = compose(private, engine_keywords=engine_keywords)
        (private / 'original-next23b-Shader48-private.shader').write_text(shader, encoding='utf-8')
        routes = [[[] if i == 0 else [f'GT_ORIGINAL_921_P{p}_V{i}']
                   for i in range(n)] for p, n in enumerate(route_counts)]
        if engine_keywords:
            manifest = json.loads((private / 'original-private-variant-manifest.json').read_text())
            modes = verified_source_next23b_pass_modes(manifest)
            if route_counts != [512, 4, 128, 512]:
                raise ValueError('next23b_exact_original_pass_routes_required')
            routes = [engine_route_keys(row, index, modes) for index, row in enumerate(packet)]
            route_packet = {'passes': [{'passType': 'Normal' if mode in ('Always', 'Untagged') else mode,
                                       'variants': [{'keywords': list(key)} for key in keys]}
                                      for mode, keys in zip(modes, routes)]}
            (private / 'Next23bEngineRoutes.json').write_text(json.dumps(route_packet), encoding='utf-8')
        checkpoint = 'verify_all_composed_entrypoints_Vulkan11'
        verify_entrypoints(shader, private, routes=routes)
        report.update(status=STATUS, source_exact_keyword_routes_by_pass=route_counts,
                      private_ShaderLab_four_pass_composed=True,
                      original_runtime_engine_keywords_preserved=engine_keywords,
                      private_ShaderLab_vertex_fragment_entrypoints_validated=2312)
    except Exception as exc:
        # Tracebacks may contain source names or identifiers; only this fixed
        # checkpoint vocabulary and exception class leave the private runner.
        with (private / "composition-private-error.log").open("a", encoding="utf-8") as log:
            traceback.print_exc(file=log)
        report['composition_safe_checkpoint'] = checkpoint
        report['composition_error_type'] = type(exc).__name__
        from scripts.t3_particle108_source_propstate import PrivateContractError, CATEGORIES
        if isinstance(exc, PrivateContractError) and exc.category in CATEGORIES:
            report['composition_safe_failure_category'] = exc.category
    return report


def run(original, manifest, quality, private, *, engine_keywords=False):
    import UnityPy
    for tool in ("vkd3d-compiler", "spirv-val", "spirv-cross", "glslangValidator"):
        if shutil.which(tool) is None:
            raise ValueError("missing_next23b_private_translation_tool")
    names, _ = gather(original, manifest)
    candidates = select_remaining_23_source_owners(names, json.loads(quality.read_text("utf-8")))
    pins = read_expected(manifest)
    selected = []
    for owner, pid in candidates:
        if owner not in pins:
            raise ValueError("untrusted_next23b_source_owner")
        _, size, digest = pins[owner]
        source = original / owner
        if source.is_symlink() or not source.is_file():
            raise ValueError("unsafe_next23b_source_owner")
        verify(source, size, digest)
        objects = [obj for obj in UnityPy.load(str(source)).objects
                   if obj.path_id == pid and str(obj.type.name) == "Shader"]
        if len(objects) != 1:
            raise ValueError("next23b_source_shader_object_not_unique")
        tree = objects[0].read_typetree()
        tables = [records(data) for platform, data in decoded_platforms(tree) if platform == 4]
        if len(tables) != 1:
            raise ValueError("next23b_source_D3D11_table_not_unique")
        profile = summarize(tree.get("m_ParsedForm"), tables[0])
        validate_topology(profile)
        selected.append((owner, pid, tree, tables[0]))
    if len(selected) != 1:
        raise ValueError("next23b_source_identity_not_unique")
    owner, pid, tree, table = selected[0]
    paired, orphans, passes, distinct = enumerate_all(
        tree["m_ParsedForm"], table, variants=stage_variants,
        permutation=variant_key, linker=linked_program,
        topology=(4, 1156, 0, 134), per_stage_variant_cap=2048)
    if private.exists() or private.is_symlink() or not private.parent.is_dir():
        raise ValueError("unsafe_next23b_private_location")
    private.mkdir(mode=0o700)
    refs, counts = recover_programs(distinct, private)
    def stage_row(row):
        return {k: (refs[v] if k == "program_ref" else v) for k, v in row.items()}
    packet = {"schema_version": 1, "source_owner": owner, "source_PathID": pid,
              "original_shader_ParsedForm_full_private": tree["m_ParsedForm"], "original_passes": passes,
              "paired": [{"subshader": p["subshader"], "pass": p["pass"],
                          "vs": stage_row(p["vs"]), "fs": stage_row(p["fs"])} for p in paired],
              "unpaired": orphans}
    (private / "original-private-variant-manifest.json").write_text(json.dumps(packet, sort_keys=True) + "\n", encoding="utf-8")
    report = {"schema_version": 1,
            "status": "PARTIAL_NEXT23B_PRIVATE_STAGE_TRANSLATION",
            "actual_source_material_quality_run": 43929698985,
            "original_source_82_owners_authenticated": True,
            "source_Shader48_Pass_count": 4, "source_paired_VSFS_routes": len(paired),
            "source_unpaired_variants": len(orphans), "source_distinct_D3D11_programs": len(distinct),
            "private_programs_attempted": counts["attempted"],
            **{k: counts[k] for k in COMPILER_FIELDS},
            "all_three_compiler_gates_valid": counts["all_three_valid"],
            "original_names_digests_owner_PathIDs_GUIDs_shader_bytes_exported": False,
            "Unity_shader_installation_same_export_GUID_or_device_render_proven": False,
            "APK_OBB_XAPK_created": False}
    if counts['all_three_valid'] != 134:
        return report
    return compose_private(tree['m_ParsedForm'], paired, orphans, passes,
                           table, refs, private, report, engine_keywords=engine_keywords)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("original", "manifest", "quality", "private", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    p.add_argument("--engine-keywords", action="store_true")
    a = p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or a.private.is_symlink()
            or a.out.resolve().is_relative_to(a.original.resolve())
            or a.out.resolve().is_relative_to(a.private.resolve())
            or a.private.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_next23b_public_private_separation")
    try:
        report = run(a.original, a.manifest, a.quality, a.private, engine_keywords=a.engine_keywords)
    except Exception as exc:
        report = {"schema_version": 1, "status": "INCONCLUSIVE", "error_type": type(exc).__name__,
                  "original_names_digests_owner_PathIDs_GUIDs_shader_bytes_exported": False,
                  "APK_OBB_XAPK_created": False}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("GT_NEXT23B_PRIVATE_STAGE_TRANSLATION_SAFE " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
