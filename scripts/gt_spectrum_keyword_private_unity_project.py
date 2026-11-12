#!/usr/bin/env python3
"""Stage a disposable Unity2021 project for source-index4 keyword Spectrum probe.

The ONE routed ShaderLab is private, and exact source-authored keyword name is
read from that private candidate; the name never appears in public safe report.
No original Material, Shader .meta/GUID, original game or phone assets are
copied. This project tests only Unity 7Pass + both ShaderVariantCollection keys.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil

from scripts.b49_shaderlab_pass_contract import pass_coverage

KEYWORD=re.compile(r"(?m)^[ \t]*#pragma multi_compile __ ([_A-Za-z][_A-Za-z0-9]{0,127})[ \t]*$")
MAX_BYTES=16*1024*1024


def prepare(shader:Path, source_proof:Path, editor:Path,
            project:Path, safe_report:Path):
    shader,source_proof,editor,project,safe_report=(
        Path(x).absolute() for x in (shader,source_proof,editor,project,safe_report))
    if (not shader.is_file() or shader.is_symlink()
            or not source_proof.is_file() or source_proof.is_symlink()
            or not editor.is_file() or editor.is_symlink()
            or not 0 < shader.stat().st_size <= MAX_BYTES
            or not 0 < source_proof.stat().st_size <= 65536
            or not 0 < editor.stat().st_size <= 131072
            or not project.parent.is_dir()
            or project.exists() or project.is_symlink()
            or safe_report.exists() or safe_report.is_symlink()
            or project.is_relative_to(shader.parent)
            or safe_report.is_relative_to(project)):
        raise ValueError("private_original_keyword_project_path_untrusted")
    proof=json.loads(source_proof.read_text(encoding="utf-8"))
    exact={
        "status":"PRIVATE_SPECTRUM_ORIGINAL_KEYWORD_INDEX4_SEVEN_PASS_ROUTED_SHADERLAB_CANDIDATE",
        "source_original_pass_count":7,
        "source_original_keyword_index":4,
        "source_original_keyword_variants_per_pass":2,
        "source_program_variant_stage_references":28,
        "source_original_keyword_index_name_authenticated":True,
        "source_original_VS_FS_pair_hashes_authenticated":True,
        "private_seven_program_keyword_pragmas":7,
        "private_uniform_block_stage_aliases_compile_only":True,
        "original_shader_keyword_flags_pragma_scope_proven":False,
        "original_game_ShaderLab_modified":False,
        "Unity_Android_2021_import_or_GPU_proven":False
    }
    if any(type(proof.get(k)) is not type(v) or proof.get(k)!=v
           for k,v in exact.items()):
        raise ValueError("private_original_keyword_source_hash_proof_untrusted")
    raw=shader.read_text(encoding="utf-8")
    coverage=pass_coverage(raw)
    keys=KEYWORD.findall(raw)
    if (not raw.startswith('Shader "UltimateWater/Spectrum/Water Spectrum" {')
            or "//DummyShaderTextExporter" in raw
            or coverage.get("pass_count")!=7
            or coverage.get("subshader_pass_counts")!=[7]
            or coverage.get("passes_with_complete_program")!=7
            or coverage.get("pass_braces_balanced") is not True
            or raw.count("HLSLPROGRAM")!=7
            or raw.count("ENDHLSL")!=7
            or len(keys)!=7 or len(set(keys))!=1):
        raise ValueError("private_original_keyword_shadervariant_source_incomplete")
    keyword=keys[0]
    project.mkdir()
    try:
        (project/"Assets/Editor").mkdir(parents=True)
        (project/"Packages").mkdir()
        (project/"ProjectSettings").mkdir()
        shutil.copyfile(shader,project/"Assets/GTPrivateSpectrumKeyword.shader")
        shutil.copyfile(editor,project/"Assets/Editor/OriginalSpectrumKeywordRouterValidation.cs")
        (project/"Packages/manifest.json").write_text(
            '{"dependencies":{}}\n', encoding="utf-8")
        (project/"ProjectSettings/ProjectVersion.txt").write_text(
            "m_EditorVersion: 2021.3.45f2\n",encoding="utf-8")
        (project/"GTPrivateOriginalKeyword.txt").write_text(
            keyword+"\n",encoding="utf-8")
        if (project/"Assets/GTPrivateSpectrumKeyword.shader").read_bytes()
                !=shader.read_bytes()):
            raise ValueError("private_original_keyword_shader_transfer_drift")
    except BaseException:
        shutil.rmtree(project,ignore_errors=True)
        raise
    safe={
        "status":"PRIVATE_SOURCE_ORIGINAL_KEYWORD_INDEX4_UNITY2021_PROJECT_STAGED",
        "source_keyword_index":4,
        "source_keyword_passes":7,
        "source_keyword_branches_per_pass":2,
        "source_original_stage_variant_refs":28,
        "private_original_keyword_spellings_or_ShaderLab_published":False,
        "original_keyword_scope_flags_proven":False,
        "original_Material_GUID_or_phone_pixels_proven":False,
        "private_Unity2021_import_proven":False,
        "original_game_Shader_or_meta_modified":False
    }
    safe_report.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
    print("GT_SPECTRUM_INDEX4_UNIFIED_PRIVATE_PROJECT_STAGED "+
          json.dumps(safe,sort_keys=True))
    return safe


def main():
    a=argparse.ArgumentParser(description=__doc__)
    for name in ("shader","source-proof","editor","project","safe-report"):
        a.add_argument("--"+name,type=Path,required=True)
    x=a.parse_args()
    prepare(x.shader,x.source_proof,x.editor,x.project,x.safe_report)


if __name__=="__main__":
    main()
