#!/usr/bin/env python3
"""GFX-MULTI-054: authenticated source Shader48 property→GPU register evidence gate.

Cross-check original SHA-pinned Shader48's Material TexEnv parameter index links
(GFX020), embedded ShaderLab/HLSL text (GFX021), ALL serialized DX11 variant
parameter tables/RDEF source programs (GFX022), and ALL linked DXBC metadata
chunks (GFX037). These are independent paths to *source* evidence, not GPU
behavior. Detect contradictions, reject inferred mapping from names/counts,
and publish safe anonymous coverage and missing-input contract only.

Reading private source happens in a disposable GitHub Actions runner; no
original compiled shaders, property names, registers, GUIDs, byte offsets,
source code, textures or selected identifiers may leave the runner.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_material_texenv_bridge import audit as material_audit
from gfxlab.tools.multi_shader_original_text_check import audit as source_text_audit
from gfxlab.tools.multi_shader_variant_reflection_sweep import audit as variant_audit
from gfxlab.tools.multi_shader_linked_dxbc_debug_chunks import audit as dxbc_debug_audit

EXPECTED_EXACT_PAIRS=524
EXPECTED_LINK_ROWS=1435
EXPECTED_LINKED_PROGRAMS=1275
EXPECTED_MATERIAL_SLOTS=7
EXPECTED_PROPERTY_NAMES=27

REQUIRED_ORIGINAL_CAPTURE_CHANNELS=(
    "same_SHA_original_shaderlab_HLSL_with_explicit_property_to_DXBC_register_relations",
    "same_original_pass_and_keyword_tier_variant_compiled_program_identity",
    "authenticated_original_Shader48_property_to_t_s_b_mapping_or_adequate_RDEF_or_serialized_parameters",
    "CB_member_byte_offsets_or_original_Windows_GPU_constant_buffer_reference",
    "source_Material_TexEnv_pointer_and_property_name_to_original_shader_binding",
    "GPU_pixel_reference_under_same_textures_render_state_and_camera_before_Android_parity",
)

def _counter(row,key,where):
    value=row.get(key,0)
    if type(value)!=int or value<0:
        raise ValueError("GFX054_INVALID_PRIVATE_SOURCE_AGGREGATE_"+where)
    return value

def build_gate(material,text,variant,debug):
    """Strictly source-anchored gate. Source-proven direct bridge ≠ CB/pixel proof."""
    for name,d in (("material",material),("text",text),("variant",variant),("debug",debug)):
        if not isinstance(d,dict):raise ValueError("GFX054_SOURCE_EVIDENCE_NOT_OBJECT_"+name)
    if [d.get("experiment") for d in (material,text,variant,debug)] != [
       "GFX-MULTI-020","GFX-MULTI-021","GFX-MULTI-022","GFX-MULTI-037"
    ]:
        raise ValueError("GFX054_WRONG_SOURCE_EVIDENCE_FAMILY")
    if any(d.get("source_sha",d.get("original_zip2_sha"))!=ZIP2_SHA
           for d in (material,text,variant,debug)):
        raise ValueError("GFX054_SOURCE_SHA_PIN_MISMATCH")
    counts=variant.get("all_original_variant_link_rows")
    stats=debug.get("source_linked_program_counts")
    material_data=material.get("original_shader_program_parameter_metadata_totals")
    script=text.get("original_shader_text_evidence")
    if any(not isinstance(x,dict) for x in (counts,stats,material_data,script)):
        raise ValueError("GFX054_SOURCE_EVIDENCE_COUNTS_MALFORMED")
    if (material.get("original_material_slot_count")!=EXPECTED_MATERIAL_SLOTS
        or text.get("material_slots")!=EXPECTED_MATERIAL_SLOTS
        or variant.get("material_slots")!=EXPECTED_MATERIAL_SLOTS
        or material.get("source_property_name_count")!=EXPECTED_PROPERTY_NAMES
        or text.get("original_shader_serialized_property_count")!=EXPECTED_PROPERTY_NAMES
        or debug.get("original_shader48_declared_property_count")!=EXPECTED_PROPERTY_NAMES
        or variant.get("exact_keyword_tier_matched_pairs")!=EXPECTED_EXACT_PAIRS
        or _counter(counts,"variant_link_rows","VARIANT")!=EXPECTED_LINK_ROWS
        or _counter(stats,"stage_link_rows","DEBUG")!=EXPECTED_LINK_ROWS
        or _counter(stats,"unique_dx11_stage_programs","DEBUG")!=EXPECTED_LINKED_PROGRAMS
        or variant.get("unique_referenced_stage_programs")!=EXPECTED_LINKED_PROGRAMS
        or _counter(stats,"exact_matched_vs_fs_variant_pairs","DEBUG")!=EXPECTED_EXACT_PAIRS):
        raise ValueError("GFX054_ORIGINAL_SHADER48_IDENTITY_AND_LINK_CROSSCHECK_DRIFT")
    if (material.get("source_stages")!=14 or material.get("source_shader_passes")!=7
        or debug.get("source_shader48_passes")!=7 or variant.get("pass_count")!=7):
        raise ValueError("GFX054_SOURCE_PASS_STAGE_ACCOUNTING_DRIFT")
    if (_counter(stats,"programs_with_rdef_chunk","RDEF")!=
        _counter(counts,"rdef_present_stage_programs","VARIANT")):
        raise ValueError("GFX054_RDEF_SOURCE_SWEEP_CONFLICT")
    bound=material.get("material_bound_texenv_slots")
    if type(bound)!=int or bound<0 or bound>63:
        raise ValueError("GFX054_BOUND_TEXENV_COUNT_INVALID")
    if (text.get("original_material_shader_property_name_parity",{}).get(
         "bound_texenv_slots")!=bound):
        raise ValueError("GFX054_MATERIAL_SOURCE_CHAIN_MISMATCH")
    direct=_counter(material_data,"exact_source_property_t_sampler_to_material_bridges","MATERIAL")
    texmeta=_counter(counts,"texture_parameter_entries","VARIANT")
    cbmeta=_counter(counts,"constant_buffer_binding_entries","VARIANT")
    named_cb=_counter(counts,"rdef_constant_buffer_descriptors","VARIANT")
    rdef=_counter(stats,"programs_with_rdef_chunk","DEBUG")
    alt=_counter(stats,"programs_with_alternate_debug_or_reflection_chunk","DEBUG")
    alt_names=_counter(stats,"programs_with_original_property_tokens_in_alternate_chunk","DEBUG")
    if alt_names>alt:
        raise ValueError("GFX054_DEBUG_NAME_COUNTER_WITHOUT_DEBUG_CHUNKS")
    if direct and (not material.get("one_source_material_texture_parameter_t_sampler_bridge_proven")
                   or not _counter(material_data,"stages_with_serialized_parameters","MATERIAL")):
        raise ValueError("GFX054_DIRECT_SHADER_TEXENV_PROOF_NOT_ACCOUNTED")
    if bool(direct)!=bool(material.get("one_source_material_texture_parameter_t_sampler_bridge_proven")):
        raise ValueError("GFX054_MATERIAL_DIRECT_PROOF_CONTRADICTION")
    # A chunk containing a property *string* is not RDEF binding/reflection;
    # source text markers / variable names / numeric byte positions are
    # likewise not direct semantic mapping.
    markers=bool(script.get("hlsl_or_cg_program_markers_found"))
    syntax=bool(script.get("register_syntax_marker_found"))
    embedded=bool(script.get("original_embedded_script_field_present"))
    if (markers or syntax) and not embedded:
        raise ValueError("GFX054_SCRIPT_MARKER_WITHOUT_ORIGINAL_SCRIPT")
    covered=(
        _counter(counts,"rdef_present_stage_programs","VARIANT")+
        _counter(counts,"rdef_absent_stage_programs","VARIANT"))
    if covered!=EXPECTED_LINKED_PROGRAMS:
        raise ValueError("GFX054_RDEF_COVERAGE_ACCOUNTING_DRIFT")
    # Only source-authenticated *direct original parameters* from GFX020 can
    # promote the original property→t/s edge. RDEF/debug/script presence alone
    # requires interpretation of a full mapping witness, which is absent here.
    source_texenv_edge=direct>0
    bridge_state=(
       "SOURCE_AUTHENTICATED_TEXENV_PARAMETER_TO_DXBC_T_S_EDGE_PARTIAL"
       if source_texenv_edge else
       "BLOCKED_NO_AUTHENTICATED_SOURCE_PROPERTY_TO_DXBC_T_S_B_EDGE_IN_AVAILABLE_INPUTS"
    )
    return {
      "experiment":"GFX-MULTI-054",
      "original_zip2_sha":ZIP2_SHA,
      "evidence_level":"ORIGINAL_SOURCE_CROSS_AUDITED_PROPERTY_REGISTER_BRIDGE_AVAILABILITY_GATE",
      "original_source_models":6,
      "original_source_material_slots":EXPECTED_MATERIAL_SLOTS,
      "original_Shader48_serialized_property_names":EXPECTED_PROPERTY_NAMES,
      "bound_original_TexEnv_slots":bound,
      "shader48_subshaders":2,
      "shader48_passes":7,
      "exact_original_keyword_tier_VS_FS_pairs":EXPECTED_EXACT_PAIRS,
      "all_original_stage_variant_link_rows":EXPECTED_LINK_ROWS,
      "unique_linked_original_DX11_stage_programs":EXPECTED_LINKED_PROGRAMS,
      "source_variant_serialized_texture_param_entries":texmeta,
      "source_variant_serialized_CB_binding_entries":cbmeta,
      "source_linked_DXBC_RDEF_programs":rdef,
      "source_linked_DXBC_RDEF_CB_descriptors":named_cb,
      "source_linked_DXBC_alternative_debug_reflection_programs":alt,
      "source_linked_alternative_debug_programs_with_property_name_string_hits":alt_names,
      "original_embedded_shader_script_field_present":embedded,
      "original_embedded_shader_script_has_HLSL_CG_markers":markers,
      "original_embedded_shader_script_has_register_syntax":syntax,
      "original_source_material_to_DXBC_texenv_t_sampler_explicit_parameter_edges":direct,
      "original_shader48_property_to_DXBC_t_s_binding_evidence_available":source_texenv_edge,
      "original_property_to_DXBC_binding_evidence_state":bridge_state,
      "original_property_to_DXBC_b_register_and_individual_member_byte_offsets_proven":False,
      "GFX052_053_generated_SPIRV_register_provenance_is_original_material_property_semantics":False,
      "original_Shader48_source_available_for_complete_Android_ShaderLab_rebuild":False,
      "original_Shader48_Android_GPU_ran":False,
      "PC_to_Adreno_original_pixel_parity_proven":False,
      "originalShaderRestored":False,
      "phase_closed":False,
      "original_property_name_register_values_hlsl_or_compiled_shaders_exported":False,
      "missing_evidence_capture_contract":list(REQUIRED_ORIGINAL_CAPTURE_CHANNELS),
    }

def audit(stage):
    # These four independently existing audits each traverse SHA-verified
    # original source in the same ephemeral runner; never persist raw returns.
    material=material_audit(stage)
    text=source_text_audit(stage)
    variant=variant_audit(stage)
    debug=dxbc_debug_audit(stage)
    return build_gate(material,text,variant,debug)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=audit(stage_originals(args.zip2,args.stage))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX054_SAFE_ORIGINAL_SOURCE_PROPERTY_REGISTER_EVIDENCE_GATE "+json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
