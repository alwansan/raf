"""GFX105 original Shader48 *private* SIV POSITION→SPIRV FragCoord→GLES310.

Authentic DXBC, SPIR-V and GLSL never leave the disposable runner. Public
output is bounded aggregate counts with explicit negative claims about pixel
identity/material/rig. Never publishes asset identifiers, shader bytes, names
or per-pair metadata.
"""
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from gfxlab.tools.original_model_probe import ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet
from gfxlab.tools.gfx105_siv_fragcoord_semantic import (
    dxbc_ps_siv_noperspective_semantic_counts,
    classify_siv_builtin_bridge)

def original_siv_fragcoord_census(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7:
        raise ValueError("GFX105_ORIGINAL_SEVEN_PASSES_EXPECTED")
    counts=Counter();errors=Counter();seen=set()
    for row in passes:
        for vs,fs in row["pairs"]:
            counts["original_exact_pairs_seen"]+=1
            index=fs.get("m_BlobIndex")
            if type(index)!=int:raise ValueError("GFX105_INVALID_STAGE_ID")
            key=(index,fs.get("m_GpuProgramType"))
            if key in seen:continue
            seen.add(key)
            ps=code_from_ref(fs,programs,"Pixel")
            source=source_shader_chunk(ps)
            semantic=dxbc_ps_siv_noperspective_semantic_counts(source)
            if not semantic["siv_noperspective_declarations"]:continue
            counts["unique_original_siv_np_programs"]+=1
            counts["source_siv_np_declarations"]+=semantic["siv_noperspective_declarations"]
            counts["source_siv_np_position_name_tokens"]+=semantic["siv_noperspective_position_name"]
            counts["source_siv_np_other_name_tokens"]+=semantic["siv_noperspective_other_system_name"]
            with TemporaryDirectory(prefix="gfx105-private-source-stage-") as name:
                folder=Path(name)
                authentic_vs=code_from_ref(vs,programs,"Vertex")
                translation=translate_pair(authentic_vs,ps,folder)
                if not translation["fragment"]["vulkan11_spirv_validation_success"]:
                    errors["original_spirv_fragment_validation_failure"]+=1
                    continue
                counts["original_spirv_fragment_valid"]+=1
                spirv=(folder/"fragment.spv").read_bytes()
                generated=folder/"fragment.glsl"
                ok,_=run_quiet(["spirv-cross",str(folder/"fragment.spv"),
                    "--version","310","--es","--output",str(generated)])
                if not ok or not generated.is_file():
                    errors["original_spirv_cross_gles310_failure"]+=1
                    continue
                counts["original_spirv_cross_gles310_emitted"]+=1
                witness=classify_siv_builtin_bridge(source,spirv,generated.read_text())
                b=witness["spirv"]
                counts["spirv_input_builtin_fragcoord_count"]+=b["input_builtin_fragcoord"]
                counts["spirv_input_builtin_other_count"]+=b["input_builtin_other"]
                counts["glsl310_fragcoord_reference_present"]+=witness[
                    "generated_glsl_fragcoord_referenced"]
                counts["source_siv_position_spirv_fragcoord_glsl_candidate"]+=witness[
                    "source_position_spirv_fragcoord_glsl_candidate"]
                if b["group_decorations_unhandled"] or b["input_pointer_type_unresolved"]:
                    errors["ambiguous_input_decoration_coverage"]+=1
    if counts["original_exact_pairs_seen"]!=524:
        raise ValueError("GFX105_ORIGINAL_PAIR_POPULATION_DRIFT")
    return {
        "experiment":"GFX-MULTI-105",
        "source_zip2_sha":ZIP2_SHA,
        "source_authentic_exact_shader48_pairs":524,
        "source_seven_passes":True,
        "counts":dict(counts),
        "unresolved_aggregate_categories":dict(errors),
        "private_original_stage_inputs_used":True,
        "system_name_position_to_fragcoord_candidate_complete":
            counts["unique_original_siv_np_programs"]>0 and
            not bool(errors) and
            counts["source_siv_np_other_name_tokens"]==0 and
            counts["source_siv_position_spirv_fragcoord_glsl_candidate"]==
              counts["unique_original_siv_np_programs"],
        "original_pixel_value_semantics_verified":False,
        "material_sampler_cb_mapping_verified":False,
        "original_shader_android_gpu_pixels_verified":False,
        "source_full_variant_shader48_runtime_verified":False,
        "original_animated_rig_verified":False,
        "originalShaderRestored":False,
        "phase_closed":False,
        "private_shader_data_exported":False,
    }
