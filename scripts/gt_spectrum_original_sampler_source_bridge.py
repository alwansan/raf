#!/usr/bin/env python3
"""GT: authenticate Spectrum translated HLSL texture/sampler names from ZIP2.

The original executable DXBC resource declarations and serialized Unity
m_TextureParams/m_SamplerIndex metadata must AGREE for every stage. A verified
source-name mapping changes *only symbolic HLSL identifiers*, preserving all
register annotations, original sampler registers and material property values.
No guessed Linear/Repeat sampler, descriptor order or synthetic name allowed.

Still no material/GUID/RT binding or actual filter-wrap/pixel parity proof.
"""
from __future__ import annotations

import re

from scripts.b17_spectrum_compiled_bindings import compare_program
from scripts.b17_spectrum_namebridge import rebind_resource_symbols

REGISTERS = re.compile(r'\bregister\s*\([^)]*\)')
MAX_HLSL = 1024 * 1024


def source_bind_stage(hlsl: str, program: dict, original_dxbc: bytes,
                      stage: int, names: list, *,
                      abi_checker=compare_program,
                      symbol_rebinder=rebind_resource_symbols):
    if (type(hlsl) is not str or not 0 < len(hlsl.encode("utf-8")) <= MAX_HLSL
            or "\x00" in hlsl or type(original_dxbc) is not bytes
            or type(stage) is not int or stage not in (0, 1)
            or not isinstance(program, dict) or not isinstance(names, list)):
        raise ValueError("Spectrum_source_stage_argument_invalid")
    proof=abi_checker(program,original_dxbc,stage)
    if (not isinstance(proof,dict)
        or proof.get("stage")!=stage
        or not isinstance(proof.get("numeric_slot_parity"),dict)
        or set(proof["numeric_slot_parity"]) != {"texture","sampler","uav"}
        or not all(value is True for value in proof["numeric_slot_parity"].values())
        or not isinstance(proof.get("compiled_counts"),dict)
        or proof["compiled_counts"].get("uav")!=0):
        raise ValueError("Spectrum_original_DXBC_serialized_resource_parity_unproven")
    result,stats=symbol_rebinder(hlsl,program,names)
    if (not isinstance(result,str) or not isinstance(stats,dict) or
            not 0 < len(result.encode("utf-8")) <= MAX_HLSL
            or REGISTERS.findall(result)!=REGISTERS.findall(hlsl) or
            stats.get("renamed_textures")!=proof["compiled_counts"].get("texture")
            or stats.get("renamed_samplers")!=proof["compiled_counts"].get("sampler")):
        raise ValueError("Spectrum_source_authentic_resource_name_or_register_mismatch")
    # A no-resource vertex program is valid ONLY when authentic original DXBC
    # declares no samplers/textures. Never invent any missing slot.
    return result,{
        "source_authenticated_texture_names":stats["renamed_textures"],
        "source_authenticated_sampler_names":stats["renamed_samplers"],
        "original_register_annotations_preserved":True,
        "original_DXBC_vs_serialized_numeric_resource_parity":True,
        "original_sampler_filter_wrap_or_exported_Material_binding_proven":False,
        "Android_Adreno_pixels_verified":False,
    }
