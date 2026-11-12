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

MAX_SAFE_REPORT = 65536
MAX_SHADER = 16 * 1024 * 1024


def prepare(candidate: Path, manifest: Path, editor: Path,
            project: Path, out: Path):
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
    project.mkdir()
    try:
        (project/"Assets/Editor").mkdir(parents=True)
        (project/"Packages").mkdir()
        (project/"ProjectSettings").mkdir()
        shutil.copyfile(candidate, project/"Assets/GTPrivateSpectrum.shader")
        shutil.copyfile(editor, project/"Assets/Editor/OriginalSpectrumSevenPassValidation.cs")
        (project/"Packages/manifest.json").write_text('{"dependencies":{}}\n', encoding="utf-8")
        (project/"ProjectSettings/ProjectVersion.txt").write_text(
            "m_EditorVersion: 2021.3.45f2\n", encoding="utf-8")
        if (project/"Assets/GTPrivateSpectrum.shader").read_bytes()!=candidate.read_bytes():
            raise ValueError("private_spectrum_shader_copy_changed")
    except BaseException:
        shutil.rmtree(project)
        raise
    report={
        "status":"PRIVATE_ORIGINAL_SPECTRUM_ISOLATED_UNITY_2021_PROJECT_STAGED",
        "source_original_seven_passes":True,
        "source_original_render_states":7,
        "provisional_isolated_keyword_variant_index":0,
        "source_original_variant_stage_programs_in_shader":14,
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
    a=p.parse_args()
    prepare(a.candidate,a.manifest,a.editor,a.project,a.out)


if __name__=="__main__":
    main()
