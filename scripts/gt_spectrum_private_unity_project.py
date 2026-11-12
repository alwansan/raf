#!/usr/bin/env python3
"""GT isolated Unity 2021 Android Vulkan private Spectrum 7pass import staging.

Never copies original game .meta/GUID, scenes, materials or original ZIP2 into
this project. The single isolated shader is SHA-original-derived and PRIVATE;
no original shader HLSL, source labels or rendered pixels enter safe reports.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.gt_spectrum_private_stage_buffer_isolation import isolate

MAX_SAFE_REPORT = 65536
MAX_SHADER = 16 * 1024 * 1024


def prepare(candidate: Path, manifest: Path, editor: Path,
            project: Path, out: Path, *, diagnostic_stage_buffers=False,
            diagnostic_uniform_blocks=False, variant_index=0):
    candidate,manifest,editor,project,out=(
        Path(p).absolute() for p in (candidate,manifest,editor,project,out))
    if (not candidate.is_file() or candidate.is_symlink() or
            not manifest.is_file() or manifest.is_symlink() or
            not editor.is_file() or editor.is_symlink() or
            not 0 < candidate.stat().st_size <= MAX_SHADER or
            not 0 < editor.stat().st_size < 131072 or
            not 0 < manifest.stat().st_size < MAX_SAFE_REPORT or
            not project.parent.is_dir() or project.exists() or project.is_symlink() or
            out.exists() or out.is_symlink() or
            project.is_relative_to(candidate.parent) or
            out.is_relative_to(project) or
            project.is_relative_to(editor.parent)):
        raise ValueError("unsafe_private_unity_spectrum_project")
    proof=json.loads(manifest.read_text(encoding="utf-8"))
    must={
        "status":"PRIVATE_ORIGINAL_SPECTRUM_TWO_SEVEN_PASS_SHADERLAB_CANDIDATES",
        "original_SHA_authenticated":True,
        "original_exact_pass_count":7,
        "private_seven_pass_ShaderLab_candidates":2,
        "private_shaderlab_structural_passes":14,
        "original_stage_variants_included":28,
        "original_per_pass_render_states_source_equal":True,
        "original_game_shader_installed":False,
        "Unity2021_import_or_Adreno_pixels_proven":False,
    }
    if any(type(proof.get(k)) is not type(v) or proof.get(k)!=v
           for k,v in must.items()):
        raise ValueError("private_spectrum_source_proof_not_accepted")
    text=candidate.read_text(encoding="utf-8")
    covers=pass_coverage(text)
    if (not text.startswith('Shader "UltimateWater/Spectrum/Water Spectrum" {')
        or "//DummyShaderTextExporter" in text or
        "// No subprograms found" in text or
        text.count("HLSLPROGRAM")!=7 or
        text.count("ENDHLSL")!=7 or
        text.count("#pragma vertex main")!=7 or
        text.count("#pragma fragment main")!=7 or
        covers.get("pass_count")!=7 or
        covers.get("subshader_pass_counts")!=[7] or
        covers.get("passes_with_complete_program")!=7 or
        covers.get("all_subshaders_programmed") is not True):
        raise ValueError("private_spectrum_seven_pass_ShaderLab_not_complete")
    if type(variant_index) is not int or variant_index not in (0, 1):
        raise ValueError("invalid_private_variant_selector")
    if candidate.name != "original-spectrum-7pass-variant-%d.shader" % variant_index:
        raise ValueError("private_candidate_does_not_match_variant")
    if type(diagnostic_stage_buffers) is not bool or type(diagnostic_uniform_blocks) is not bool:
        raise ValueError("invalid_private_diagnostic_mode")
    if diagnostic_uniform_blocks and not diagnostic_stage_buffers:
        raise ValueError("private_uniform_block_alias_requires_stage_guard")
    isolated = None
    private_project_source = text
    if diagnostic_stage_buffers:
        # This compile-only transform is intentionally NOT applied to
        # original DXBC, serialized Material/GUID, or real game shader.
        private_project_source, isolated = isolate(
            text,stage_uniform_blocks=diagnostic_uniform_blocks)
    project.mkdir()
    try:
        (project/"Assets/Editor").mkdir(parents=True)
        (project/"Packages").mkdir()
        (project/"ProjectSettings").mkdir()
        (project/"Assets/GTPrivateSpectrum.shader").write_text(
            private_project_source, encoding="utf-8")
        shutil.copyfile(editor, project/"Assets/Editor/OriginalSpectrumSevenPassValidation.cs")
        (project/"Packages/manifest.json").write_text('{"dependencies":{}}\n', encoding="utf-8")
        (project/"ProjectSettings/ProjectVersion.txt").write_text(
            "m_EditorVersion: 2021.3.45f2\n", encoding="utf-8")
        # Private numeric selector; the actual shader program and Unity C#
        # verifier remain otherwise identical for variant0 and variant1.
        (project/"GTPrivateSpectrumVariant.txt").write_text(
            str(variant_index) + "\n", encoding="utf-8")
        if (project/"Assets/GTPrivateSpectrum.shader").read_text(
                encoding="utf-8") != private_project_source:
            raise ValueError("private_spectrum_shader_copy_changed")
    except BaseException:
        shutil.rmtree(project)
        raise
    report={
        "status":"PRIVATE_ORIGINAL_SPECTRUM_ISOLATED_UNITY_2021_PROJECT_STAGED",
        "source_original_seven_passes":True,
        "source_original_render_states":7,
        "provisional_isolated_keyword_variant_index":variant_index,
        "source_original_variant_stage_programs_in_shader":14,
        "private_stage_local_cbuffer_name_disambiguation_only":diagnostic_stage_buffers,
        "private_stage_local_uniform_block_alias_diagnostic_only":diagnostic_uniform_blocks,
        "private_vertex_uniform_block_identifier_count":(
            0 if isolated is None else
            isolated["private_vertex_uniform_block_identifiers_disambiguated"]),
        "private_fragment_uniform_block_identifier_count":(
            0 if isolated is None else
            isolated["private_fragment_uniform_block_identifiers_disambiguated"]),
        "private_vertex_cbuffer_identifiers_disambiguated":(
            0 if isolated is None else
            isolated["private_vertex_cbuffer_identifiers_disambiguated"]),
        "private_fragment_cbuffer_identifiers_disambiguated":(
            0 if isolated is None else
            isolated["private_fragment_cbuffer_identifiers_disambiguated"]),
        "original_DXBC_register_annotations_unchanged":(
            True if isolated is None else
            isolated["private_original_HLSL_register_annotations_identical"]),
        "original_keyword_selection_or_Material_binding_proven":False,
        "original_game_source_or_meta_modified":False,
        "Unity_Editor_2021_compilation_proven":False,
        "Adreno_pixels_verified":False,
        "private_ShaderLab_or_original_names_published":False,
    }
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("GT_SPECTRUM_PRIVATE_UNITY_STAGING_SAFE "+json.dumps(report, sort_keys=True))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("candidate","manifest","editor","project","out"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--diagnostic-stage-buffers",action="store_true")
    p.add_argument("--diagnostic-uniform-blocks",action="store_true")
    p.add_argument("--variant-index", type=int, choices=(0, 1), default=0)
    a=p.parse_args()
    prepare(a.candidate,a.manifest,a.editor,a.project,a.out,
            diagnostic_stage_buffers=a.diagnostic_stage_buffers,
            diagnostic_uniform_blocks=a.diagnostic_uniform_blocks,
            variant_index=a.variant_index)


if __name__=="__main__":
    main()
