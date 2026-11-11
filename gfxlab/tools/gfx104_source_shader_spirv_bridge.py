"""GFX104 source-private Shader48 DXBC→SPIR-V→GLES interpolation evidence.

Only the authenticated 524 exact source pairs are searched. Translates each
distinct original fragment program with noperspective declarations, privately.
Never emits original shader code, SPIR-V IDs, varying names, shader hashes,
asset identifiers or paths: aggregates/counts only.
"""
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

from gfxlab.tools.original_model_probe import ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet
from gfxlab.tools.gfx103_source_interpolation_gate import (
    dxbc_fragment_input_classes,enforce_native_gles_qualifier)
from gfxlab.tools.gfx104_spirv_input_interpolation import inspect_spirv_input_interpolation

def original_noperspective_translation_census(stage):
    programs,passes=source_pair(stage)
    if len(passes)!=7:raise ValueError("GFX104_ORIGINAL_PASS_COUNT_DRIFT")
    seen=set()
    counts=Counter()
    affected_pairs=0
    errors=Counter()
    for passrow in passes:
        for vs,fs in passrow.get("pairs",[]):
            counts["original_pairs_seen"]+=1
            key=(fs.get("m_BlobIndex"),fs.get("m_GpuProgramType"))
            if key in seen:
                if key[0] is None or key[1] is None:
                    raise ValueError("GFX104_BAD_ORIGINAL_PROGRAM_REF")
                continue
            seen.add(key)
            original_ps=code_from_ref(fs,programs,"Pixel")
            source=dxbc_fragment_input_classes(source_shader_chunk(original_ps))
            ordinary=source["ordinary_noperspective_declarations"]
            siv=source["system_interpreted_noperspective_declarations"]
            if not (ordinary or siv):
                continue
            counts["source_unique_ps_with_any_np"]+=1
            counts["source_unique_ps_with_ordinary_np"]+=bool(ordinary)
            counts["source_unique_ps_with_siv_np"]+=bool(siv)
            with TemporaryDirectory(prefix="gfx104-shader-private-") as d:
                folder=Path(d)
                original_vs=code_from_ref(vs,programs,"Vertex")
                status=translate_pair(original_vs,original_ps,folder)
                if not status["fragment"]["vulkan11_spirv_validation_success"]:
                    errors["fragment_dxbc_spirv_validation_failed"]+=1
                    continue
                counts["source_fragment_spirv_valid"]+=1
                spv=folder/"fragment.spv"
                info=inspect_spirv_input_interpolation(spv.read_bytes())
                if info["group_decorations_unhandled"] or info["input_pointer_type_unresolved"]:
                    errors["spirv_input_decorations_unresolved"]+=1
                    continue
                counts["fragment_spirv_ordinary_np_candidates"]+=info["input_direct_noperspective_nonbuiltin"]
                counts["fragment_spirv_member_np_candidates"]+=info["input_member_noperspective_decorations"]
                counts["fragment_spirv_input_builtin_count"]+=info["input_direct_builtin_variables"]
                if ordinary and info["input_no_perspective_candidate_count"]==0:
                    errors["ordinary_source_np_lost_in_spirv"]+=1
                target=folder/"fragment.glsl"
                ok,_=run_quiet(["spirv-cross",str(spv),"--version","310","--es",
                                "--output",str(target)])
                if not ok or not target.exists():
                    errors["spirv_cross_310_unavailable"]+=1
                    continue
                counts["fragment_spirv_cross_gles310_emitted"]+=1
                try:
                    fixed,proof=enforce_native_gles_qualifier(target.read_text(),"fragment",source)
                except (ValueError,UnicodeError):
                    errors["source_gles310_native_qualifier_gate_failed"]+=1
                    continue
                if proof["native_qualifier_seen"]:
                    counts["generated_gles310_native_np_qualifier_present"]+=1
                    counts["generated_gles310_required_nv_extension"]+=bool(
                        "#extension GL_NV_shader_noperspective_interpolation : require" in fixed)
                if ordinary and info["input_no_perspective_candidate_count"] and proof["native_qualifier_seen"]:
                    counts["ordinary_source_np_spirv_glsl_candidate_preserved"]+=1
                if siv:
                    # Never infer a source SV_POSITION register -> gl_FragCoord
                    # mapping from matching numerical decoration totals.
                    counts["siv_np_builtin_semantics_identity_unverified"]+=1
    if counts["original_pairs_seen"]!=524:
        raise ValueError("GFX104_EXACT_SOURCE_PAIR_COUNT_DRIFT")
    return {
        "experiment":"GFX-MULTI-104",
        "source_zip2_sha":ZIP2_SHA,
        "source_shader48_original_exact_pairs":524,
        "counts":dict(counts),
        "categories_of_nonrestored_stage":dict(errors),
        "source_exact_fragment_input_interpolation_identity_verified":False,
        "source_to_spirv_noperspective_candidate_census_complete":True,
        "source_to_generated_gles_noperspective_identity_verified":False,
        "siv_builtin_identity_verified":False,
        "originalShaderRestored":False,
        "original_material_cb_binding_verified":False,
        "original_animation_verified":False,
        "original_pc_phone_pixels_verified":False,
        "phase_closed":False,
        "private_shader_bytes_exported":False,
    }
