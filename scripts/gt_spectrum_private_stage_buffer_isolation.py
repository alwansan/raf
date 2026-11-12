#!/usr/bin/env python3
"""GT isolated Unity-only fix for translated Spectrum VS/FS CBuffer symbol alias.

Seven-pass private ShaderLab has paired original HLSL stages with independent
source constant buffer layouts. SPIRV-Cross HLSL may give both vertex and
fragment different-sized buffers the same symbolic name (cb0_0_m0), which
Unity's GLSL linker incorrectly treats as a shared uniform. Rename ONLY the
private HLSL stage-local cbuffer identifiers; keep register(bN), resource/
sampler bindings, data and all original ShaderLab states otherwise identical.
Never install this unbound diagnostic in original Raft Material/GUID.
"""
from __future__ import annotations
import re

from scripts.b09_spectrum_topology_contract import PASSES
from scripts.b49_shaderlab_pass_contract import pass_coverage

STAGE_BRANCH = re.compile(
    r'(?ms)(^[ \t]*#if[ \t]+defined\(SHADER_STAGE_VERTEX\)[ \t]*\n)'
    r'(.*?)'
    r'(^[ \t]*#elif[ \t]+defined\(SHADER_STAGE_FRAGMENT\)[ \t]*\n)'
    r'(.*?)'
    r'(^[ \t]*#else[ \t]*\n[ \t]*#error[ \t]+Unsupported_stage[ \t]*\n[ \t]*#endif[ \t]*\n?)'
)
BUFFER = re.compile(r'\bcb\d+_\d+_m\d+\b')
RESTORE = re.compile(r'\bGT_PRIVATE_(?:VS|PS)_(cb\d+_\d+_m\d+)\b')
ANNOTATION = re.compile(r'\bregister\s*\([^)]*\)')
MAX_SOURCE = 16*1024*1024


def isolate(raw: str):
    if (type(raw) is not str or
            not 0 < len(raw.encode("utf-8")) <= MAX_SOURCE or
            "\x00" in raw or
            "GT_PRIVATE_VS_" in raw or
            "GT_PRIVATE_PS_" in raw):
        raise ValueError("unsupported_private_original_spectrum_shaderlab")
    branches=list(STAGE_BRANCH.finditer(raw))
    coverage=pass_coverage(raw)
    if (len(branches) != PASSES or
            coverage.get("subshader_pass_counts") != [PASSES] or
            coverage.get("passes_with_complete_program") != PASSES):
        raise ValueError("private_Spectrum_exact_seven_stage_branches_required")
    counts={"vertex":0,"fragment":0}
    def stage_split(m):
        vs, fs = m.group(2), m.group(4)
        counts["vertex"] += len(BUFFER.findall(vs))
        counts["fragment"] += len(BUFFER.findall(fs))
        a=BUFFER.sub(lambda x:"GT_PRIVATE_VS_"+x.group(),vs)
        b=BUFFER.sub(lambda x:"GT_PRIVATE_PS_"+x.group(),fs)
        return m.group(1)+a+m.group(3)+b+m.group(5)
    candidate=STAGE_BRANCH.sub(stage_split,raw)
    undone=RESTORE.sub(lambda m:m.group(1),candidate)
    if (counts["vertex"]==0 or counts["fragment"]==0 or
            candidate==raw or
            undone!=raw or
            ANNOTATION.findall(candidate)!=ANNOTATION.findall(raw) or
            pass_coverage(candidate)!=coverage):
        raise ValueError("private_spectrum_stage_local_buffer_rename_not_reversible")
    return candidate, {
        "private_vertex_cbuffer_identifiers_disambiguated":counts["vertex"],
        "private_fragment_cbuffer_identifiers_disambiguated":counts["fragment"],
        "private_original_HLSL_register_annotations_identical":True,
        "other_private_ShaderLab_text_bytewise_reversible":True,
        "original_game_shader_or_Material_modified":False,
        "sampler_binding_material_parity_proven":False,
        "Unity_2021_Android_compilation_proven":False,
        "Adreno_pixels_proven":False,
    }
