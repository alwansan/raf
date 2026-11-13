"""Build the two original Smoke34 routes with SHA-backed resources and uniforms.

The original ShaderLab text, names, and compiled binaries stay in scratch.
The output receipt establishes source linkage and Vulkan stage compilation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from scripts.b25_foam_cb_namebridge import original_name_registry
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.gt_particle108_unity_bindings import bind_stage_parameters, variant_parameter_layout
from scripts.t3_original_smoke34_spirv_translation import exact_two_stage_links
from scripts.t3_particle108_private_keyword_routed_shaderlab import compile_one, parts
from scripts.t3_particle108_private_shaderlab_variants import assemble, source_models
from scripts.t3_smoke34_sameexport_shaderlab import original_private_smoke_target
from scripts.w1_rebind_depth_resources import IDENT
from scripts.w1_recover_depth_passes import stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate

STATUS = "SOURCE_NAMED_SMOKE34_TWO_ROUTES_VULKAN_COMPILED"


def keyword_switch(parsed, vertex):
    variants = [row["m_KeywordIndices"] for _, _, row in stage_variants(vertex)]
    if len(variants) != 2 or sorted(map(len, variants)) != [0, 1]:
        raise ValueError("smoke34_original_single_keyword_route_drift")
    switched = next(i for i, keys in enumerate(variants) if keys)
    index, = variants[switched]
    names, flags = parsed["m_KeywordNames"], parsed["m_KeywordFlags"]
    if (type(index) is not int or not 0 <= index < len(names)
            or len(names) != len(flags) or not isinstance(names[index], str)
            or not IDENT.fullmatch(names[index]) or names.count(names[index]) != 1
            or names[index].startswith(("SHADER_STAGE_", "GL_"))):
        raise ValueError("smoke34_original_keyword_name_unproven")
    return names[index], switched


def route_pair(shaders, keyword, switched, private):
    disabled, enabled = (parts(shaders[i]) for i in (1 - switched, switched))
    if (disabled[0], disabled[2]) != (enabled[0], enabled[2]):
        raise ValueError("smoke34_original_ShaderLab_envelope_drift")
    pragma = ("#pragma target 5.0\n#pragma vertex main\n#pragma fragment main\n"
              f"#pragma multi_compile __ {keyword}\n")
    code = (f"#if defined({keyword})\n{enabled[1]}\n"
            f"#else\n{disabled[1]}\n#endif\n")
    candidate = f"{disabled[0]}HLSLPROGRAM\n{pragma}{code}ENDHLSL{disabled[2]}"
    coverage = pass_coverage(candidate)
    if (coverage["subshader_pass_counts"] != [1]
            or coverage["passes_with_complete_program"] != 1
            or coverage["pass_braces_balanced"] is not True):
        raise ValueError("smoke34_original_ShaderLab_structure_invalid")
    if not all(compile_one(code, stage, (keyword,), (enabled,), private)
               for enabled in (False, True) for stage in (1, 0)):
        raise ValueError("smoke34_original_named_routes_Vulkan_compile_failed")
    return candidate


def recover(original, manifest, private):
    import UnityPy

    private = private.absolute()
    if (private.exists() or any(p.is_symlink() for p in (private, *private.parents))
            or private.is_relative_to(original.absolute())):
        raise ValueError("unsafe_smoke34_private_output")
    (owner, path_id), _ = original_private_smoke_target(original, manifest)
    original_file = UnityPy.load(str(original / "Raft_Data" / owner)).file
    shader = original_file.objects[path_id].read_typetree()
    parsed = shader["m_ParsedForm"]
    source_pass = parsed["m_SubShaders"][0]["m_Passes"][0]
    table, = [records(parts) for platform, parts in decoded_platforms(shader) if platform == 4]
    variants = exact_two_stage_links(parsed, table)
    keyword, switched = keyword_switch(parsed, source_pass["progVertex"])
    names = original_name_registry(source_pass["m_NameIndices"])
    shaders = []
    samples = buffers = offsets = 0
    private.mkdir(mode=0o700)
    try:
        for i, (vertex, fragment) in enumerate(variants):
            programs = {}
            for stage, field, (dxbc, bucket, ordinal) in (
                (1, "progVertex", vertex), (0, "progFragment", fragment)
            ):
                directory = private / f"route-{i}-stage-{stage}"
                directory.mkdir(mode=0o700)
                translated = translate(dxbc, stage, directory)
                if not all(translated.get(key) is True for key in
                           ("vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid")):
                    raise ValueError("smoke34_original_HLSL_translation_failed")
                stage_program = source_pass[field]
                layout = variant_parameter_layout(stage_program, table, bucket, ordinal)
                programs[stage], matched, count, stats = bind_stage_parameters(
                    (directory / "private.hlsl").read_text(encoding="utf-8"),
                    dxbc, stage, stage_program, source_pass["m_NameIndices"], names,
                    layout, directory / "named")
                offsets += matched
                buffers += count
                samples += stats["original_DXBC_sample_operand_pairs_verified"]
            candidate, _ = assemble(parsed, programs[1], programs[0],
                                    source_models(vertex[0], fragment[0]))
            shaders.append(candidate)
        if (samples, buffers, offsets) != (5, 9, 32):
            raise ValueError("smoke34_original_named_parameter_counts_drift")
        candidate = route_pair(shaders, keyword, switched, private).encode("utf-8")
        (private / "smoke34-original.shader").write_bytes(candidate)
    except BaseException:
        shutil.rmtree(private)
        raise
    return {
        "status": STATUS,
        "candidate_shader_sha256": hashlib.sha256(candidate).hexdigest(),
        "source_original_smoke_named_particle_renderer_slots": 34,
        "source_original_keyword_variants": 2,
        "private_named_Vulkan_stages_compiled": 4,
        "private_original_DXBC_sample_pairs_verified": samples,
        "private_original_named_constant_buffers": buffers,
        "private_original_named_constant_buffer_reflected_offsets": offsets,
        "Unity_Android_Vulkan_shader_compilation_proven": False,
        "original_exported_GUID_or_material_modified": False,
        "original_names_programs_or_GUIDs_published": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("original", "manifest", "private", "report"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    if (args.report.exists() or args.report.is_symlink()
            or args.report.absolute().is_relative_to(args.original.absolute())):
        raise ValueError("unsafe_smoke34_source_report_output")
    try:
        result = recover(args.original, args.manifest, args.private)
    except (OSError, ValueError, TypeError, KeyError):
        result = {"status": "INCONCLUSIVE_ORIGINAL_SMOKE34_SOURCE_BOUND_SHADER"}
    args.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("GT_ORIGINAL_SMOKE34_SOURCE_BOUND " + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
