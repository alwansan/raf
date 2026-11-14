"""Recover the exact four original ParticleShader keyword pairs in private scratch."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import shutil

from scripts.b25_foam_cb_namebridge import original_name_registry
from scripts.gt_original_921_all_variants import authenticated_shader_reader
from scripts.gt_particle108_unity_bindings import bind_stage_parameters, variant_parameter_layout
from scripts.t3_original_particle108_spirv_translation import exact_four_stage_links
from scripts.t3_original_renderer_shader_impact import load_original, STATUS as GRAPH_STATUS
from scripts.t3_particle108_private_keyword_routed_shaderlab import verify, STATUS as ROUTE_STATUS
from scripts.t3_particle108_private_shaderlab_variants import assemble, source_models
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate

STATUS = "SOURCE_NAMED_PARTICLE20_FOUR_ROUTES_VULKAN_COMPILED"


def original_particle20(original, manifest):
    slots = {}
    graph = load_original(original, manifest, private_particle_slot_counts=slots)
    matches = [key for key, count in slots.items() if count == 20]
    if (graph["status"] != GRAPH_STATUS or graph["six_original_scenes_sha_verified"] is not True
            or len(matches) != 1 or matches[0][0] != "sharedassets0.assets"):
        raise ValueError("particle20_original_source_identity_unverified")
    tree = authenticated_shader_reader(original)(matches[0])
    parsed = tree["m_ParsedForm"]
    if parsed["m_Name"] != "ParticleShader":
        raise ValueError("particle20_original_name_mismatch")
    return matches[0], tree


def recover(original, manifest, private):
    _, tree = original_particle20(original, manifest)
    parsed = tree["m_ParsedForm"]
    table, = [records(parts) for platform, parts in decoded_platforms(tree) if platform == 4]
    pairs = exact_four_stage_links(parsed, table, table_records=14)
    if len({(stage, link[0]) for pair in pairs for stage, link in enumerate(pair)}) != 6:
        raise ValueError("particle20_distinct_original_program_count_drift")
    program = parsed["m_SubShaders"][0]["m_Passes"][0]
    registry = original_name_registry(program["m_NameIndices"])
    counters = Counter()
    private = private.absolute()
    if (private.exists() or any(p.is_symlink() for p in (private, *private.parents))
            or private.is_relative_to(original.absolute())):
        raise ValueError("unsafe_particle20_private_output")
    private.mkdir(mode=0o700)
    try:
        for i, (vertex, fragment) in enumerate(pairs):
            stages = {}
            for stage, field, (dxbc, bucket, ordinal) in (
                    (1, "progVertex", vertex), (0, "progFragment", fragment)):
                directory = private / f"pair-{i}-stage-{stage}"
                directory.mkdir(mode=0o700)
                translated = translate(dxbc, stage, directory)
                if not all(translated.get(key) is True for key in
                           ("vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid")):
                    raise ValueError("particle20_original_translation_failed")
                stage_program = program[field]
                layout = variant_parameter_layout(stage_program, table, bucket, ordinal)
                stages[stage], offsets, buffers, stats = bind_stage_parameters(
                    (directory / "private.hlsl").read_text(encoding="utf-8"),
                    dxbc, stage, stage_program, program["m_NameIndices"], registry,
                    layout, directory / "named")
                counters.update(stats)
                counters["offsets"] += offsets
                counters["buffers"] += buffers
            candidate, shape = assemble(parsed, stages[1], stages[0],
                                        source_models(vertex[0], fragment[0]), particle20=True)
            if (shape["original_authored_property_count"],
                    shape["original_authored_texture_property_count"]) != (12, 2):
                raise ValueError("particle20_original_property_count_drift")
            (private / f"keyword-{i}-private.shader").write_text(candidate, encoding="utf-8")
        route = verify(private, parsed)
        if route["status"] != ROUTE_STATUS:
            raise ValueError("particle20_named_route_compile_failed")
        (private / "routing-safe.json").write_text(json.dumps(route), encoding="utf-8")
        digest = sha256((private / "keyword-routed-private.shader").read_bytes()).hexdigest()
    except BaseException:
        shutil.rmtree(private)
        raise
    return {
        "status": STATUS,
        "candidate_shader_sha256": digest,
        "original_renderer_material_slots": 20,
        "original_shader_properties": 12,
        "original_unique_D3D11_programs": 6,
        "original_paired_keyword_variants": 4,
        "named_Vulkan_stages_compiled": 8,
        "original_DXBC_samples_verified": counters["original_DXBC_sample_operand_pairs_verified"],
        "named_constant_buffers": counters["buffers"],
        "reflected_constant_buffer_offsets": counters["offsets"],
        "Unity_Android_Vulkan_shader_compilation_proven": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("original", "manifest", "private", "report"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    report = args.report.resolve()
    if (args.report.exists() or args.report.is_symlink()
            or any(report.is_relative_to(p.resolve()) for p in (args.original, args.private))):
        raise ValueError("unsafe_particle20_source_report")
    try:
        result = recover(args.original, args.manifest, args.private)
    except (OSError, ValueError, KeyError, TypeError):
        result = {"status": "INCONCLUSIVE_ORIGINAL_PARTICLE20"}
    with args.report.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2, sort_keys=True)
        output.write("\n")
    print("GT_ORIGINAL_PARTICLE20 " + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
