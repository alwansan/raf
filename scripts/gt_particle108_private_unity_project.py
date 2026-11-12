#!/usr/bin/env python3
"""Stage original Particle108 four-variant ShaderLab in isolated Unity Android project.

Shader source stays runner-private; no original game Material, GUID or scene edit.
"""
import argparse
import json
from pathlib import Path
import re
import shutil

from scripts.b49_shaderlab_pass_contract import pass_coverage

KEYWORD=re.compile(r"(?m)^[ \t]*#pragma multi_compile __ ([A-Za-z_][A-Za-z_0-9]*)[ \t]*$")

def prepare(shader:Path,editor:Path,project:Path,report:Path,routing:Path):
    shader,editor,project,report,routing=(p.absolute() for p in (shader,editor,project,report,routing))
    if (project.exists() or project.is_symlink() or not project.parent.is_dir()
        or any(p.is_symlink() or not p.is_file() for p in (shader,editor,routing))
        or shader.stat().st_size>16*1024*1024 or editor.stat().st_size>131072
        or routing.stat().st_size>65536):
        raise ValueError("unsafe_private_original_shader_project_or_input")
    if (project.is_relative_to(shader.parent) or report.is_relative_to(project)):
        raise ValueError("overlapping_original_private_shader_paths")
    proof=json.loads(routing.read_text(encoding="utf-8"))
    required={"status":"T3_PRIVATE_SHADER48_PROVISIONAL_TWO_KEYWORD_SINGLE_SHADERLAB_VALID",
              "source_original_keyword_name_indices_mapped":True,
              "original_keyword_pair_routes":4,
              "private_combination_stage_compiles_attempted":8,
              "private_combination_stage_Vulkan11_SPIRV_valid":8,
              "original_keyword_flags_pragma_scope_proven":False,
              "Unity_ShaderLab_import_or_actual_variant_selection_proven":False,
              "original_Material_binding_proven":False,"Android_pixels_proven":False}
    if any(type(proof.get(k)) is not type(v) or proof.get(k)!=v for k,v in required.items()):
        raise ValueError("original_four_variant_authentication_unproven")
    raw=shader.read_text(encoding="utf-8")
    names=KEYWORD.findall(raw)
    coverage=pass_coverage(raw)
    if (len(names)!=2 or len(set(names))!=2 or raw.count("HLSLPROGRAM")!=1
        or raw.count("ENDHLSL")!=1 or "//DummyShaderTextExporter" in raw
        or coverage.get("pass_count")!=1 or
        coverage.get("passes_with_complete_program")!=1 or
        coverage.get("subshader_pass_counts")!=[1] or
        coverage.get("pass_braces_balanced") is not True):
        raise ValueError("untrusted_private_original_four_variant_ShaderLab")
    if report.exists() or report.is_symlink():
        raise ValueError("private_original_shader_report_exists")
    project.mkdir()
    try:
        (project/"Assets/Editor").mkdir(parents=True)
        (project/"Packages").mkdir()
        (project/"ProjectSettings").mkdir()
        shutil.copyfile(shader,project/"Assets/GTPrivateOriginal.shader")
        shutil.copyfile(editor,project/"Assets/Editor/OriginalParticleShaderValidation.cs")
        (project/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
        (project/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
        if (project/"Assets/GTPrivateOriginal.shader").read_bytes()!=shader.read_bytes():
            raise ValueError("private_original_shader_copy_drift")
    except BaseException:
        shutil.rmtree(project)
        raise
    result={"schema":"GT_PRIVATE_ORIGINAL_PARTICLE108_UNITY_PROBE_V1",
            "status":"SHA_ORIGINAL_FOUR_VARIANT_SHADERLAB_STAGED_UNITY_NOT_YET_COMPILED",
            "source_authenticated_original_keyword_dimensions":2,
            "source_original_variant_combinations":4,
            "original_DXBC_to_SPIRV_glslang_stage_branches_valid":8,
            "original_one_ShaderLab_pass_complete":True,
            "game_source_or_GUID_modified":False,
            "unity_Android_compilation_proven":False,
            "original_Android_game_pixels_proven":False,
            "source_Original_ShaderLab_keyword_names_or_bytecode_published":False}
    report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_PRIVATE_ORIGINAL_PARTICLE_UNITY_STAGING "+json.dumps(result,sort_keys=True))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for field in ("shader","editor","project","report","routing"):
        p.add_argument("--"+field,type=Path,required=True)
    a=p.parse_args()
    prepare(a.shader,a.editor,a.project,a.report,a.routing)

if __name__=="__main__":
    main()
