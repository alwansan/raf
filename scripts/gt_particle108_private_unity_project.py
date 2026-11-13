#!/usr/bin/env python3
"""Stage original Particle108 four-variant ShaderLab in isolated Unity Android project.

Shader source stays runner-private; no original game Material, GUID or scene edit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from scripts.b49_shaderlab_pass_contract import pass_coverage

KEYWORD=re.compile(r"(?m)^[ \t]*#pragma multi_compile __ ([A-Za-z_][A-Za-z_0-9]*)[ \t]*$")

# Original Shader48 provisional routing keeps four private branches, each with
# its own Vertex/Fragment HLSL. Unity's GLSL linker sees identical translated
# backing-array names (e.g. cb1_0_m0) but different source array sizes. For a
# compile-only diagnostic, disambiguate IDENTIFIERS separately per stage.
# This must never rename resources, sampler names, registers, GUIDs or values.
STAGE_BRANCH=re.compile(
    r'(?ms)(^[ \t]*#if[ \t]+defined\(SHADER_STAGE_VERTEX\)[ \t]*\n)'
    r'(.*?)'
    r'(^[ \t]*#elif[ \t]+defined\(SHADER_STAGE_FRAGMENT\)[ \t]*\n)'
    r'(.*?)'
    r'(^[ \t]*#else[ \t]*\n[ \t]*#error[ \t]+Unsupported_stage[ \t]*\n[ \t]*#endif[ \t]*\n?)'
)
STAGE_BUFFER=re.compile(r'\bcb[0-9]+_[0-9]+_m[0-9]+\b')
STAGE_DIAGNOSTIC_PREFIX=re.compile(r'\bGT_UNBOUND_(?:VS|PS)_(cb[0-9]+_[0-9]+_m[0-9]+)\b')
RESOURCE_ANNOTATION=re.compile(r'\bregister\s*\([^)]*\)')

def isolate_stage_buffer_names(raw):
    """Private compile-only transform; NEVER a source-material parity claim."""
    if type(raw) is not str or not 0<len(raw.encode("utf-8"))<=16*1024*1024:
        raise ValueError("unsupported_private_stage_buffer_source")
    matches=list(STAGE_BRANCH.finditer(raw))
    if len(matches)!=4:
        raise ValueError("private_original_four_stage_branches_required")
    counts={"vertex":0,"fragment":0}
    def replace(match):
        vertex,fragment=match.group(2),match.group(4)
        counts["vertex"]+=len(STAGE_BUFFER.findall(vertex))
        counts["fragment"]+=len(STAGE_BUFFER.findall(fragment))
        vs=STAGE_BUFFER.sub(lambda m:"GT_UNBOUND_VS_"+m.group(),vertex)
        fs=STAGE_BUFFER.sub(lambda m:"GT_UNBOUND_PS_"+m.group(),fragment)
        return match.group(1)+vs+match.group(3)+fs+match.group(5)
    changed=STAGE_BRANCH.sub(replace,raw)
    # The original multi-variant payload and every register() annotation
    # survive; only HLSL stage-local temporary buffer symbol spelling moves.
    restored=STAGE_DIAGNOSTIC_PREFIX.sub(lambda m:m.group(1),changed)
    if (counts["vertex"]==0 or counts["fragment"]==0 or
        restored!=raw or changed==raw or
        RESOURCE_ANNOTATION.findall(raw)!=RESOURCE_ANNOTATION.findall(changed)):
        raise ValueError("unsafe_private_stage_buffer_disambiguation")
    return changed,counts

def prepare(shader:Path,editor:Path,project:Path,report:Path,routing:Path, *, diagnostic_stage_buffers=False, smoke34=False):
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
    dimensions=1 if smoke34 else 2
    combinations=1 << dimensions
    if smoke34:
        required={"status":"SOURCE_NAMED_SMOKE34_TWO_ROUTES_VULKAN_COMPILED",
                  "source_original_smoke_named_particle_renderer_slots":34,
                  "source_original_keyword_variants":combinations,
                  "private_named_Vulkan_stages_compiled":2*combinations,
                  "private_original_DXBC_sample_pairs_verified":5,
                  "private_original_named_constant_buffers":9,
                  "private_original_named_constant_buffer_reflected_offsets":32}
        if diagnostic_stage_buffers or proof.get("candidate_shader_sha256")!=hashlib.sha256(shader.read_bytes()).hexdigest():
            raise ValueError("untrusted_private_smoke34_shader_bytes")
    if any(type(proof.get(k)) is not type(v) or proof.get(k)!=v for k,v in required.items()):
        raise ValueError("original_four_variant_authentication_unproven")
    raw=shader.read_text(encoding="utf-8")
    names=KEYWORD.findall(raw)
    coverage=pass_coverage(raw)
    if (len(names)!=dimensions or len(set(names))!=dimensions or raw.count("HLSLPROGRAM")!=1
        or raw.count("ENDHLSL")!=1 or "//DummyShaderTextExporter" in raw
        or coverage.get("pass_count")!=1 or
        coverage.get("passes_with_complete_program")!=1 or
        coverage.get("subshader_pass_counts")!=[1] or
        coverage.get("pass_braces_balanced") is not True):
        raise ValueError("untrusted_private_original_four_variant_ShaderLab")
    if report.exists() or report.is_symlink():
        raise ValueError("private_original_shader_report_exists")
    if type(diagnostic_stage_buffers) is not bool:
        raise ValueError("invalid_private_diagnostic_mode")
    candidate=raw
    isolated=None
    if diagnostic_stage_buffers:
        candidate,isolated=isolate_stage_buffer_names(raw)
    project.mkdir()
    try:
        (project/"Assets/Editor").mkdir(parents=True)
        if smoke34:
            (project/"ProbeResults").mkdir()
            (project/"ProbeResults/smoke34").touch()
        (project/"Packages").mkdir()
        (project/"ProjectSettings").mkdir()
        if diagnostic_stage_buffers:
            (project/"Assets/GTPrivateOriginal.shader").write_text(candidate,encoding="utf-8")
        else:
            shutil.copyfile(shader,project/"Assets/GTPrivateOriginal.shader")
        shutil.copyfile(editor,project/"Assets/Editor/OriginalParticleShaderValidation.cs")
        (project/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
        (project/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
        if (project/"Assets/GTPrivateOriginal.shader").read_text(encoding="utf-8")!=candidate:
            raise ValueError("private_original_shader_copy_drift")
    except BaseException:
        shutil.rmtree(project)
        raise
    result={"schema":"GT_PRIVATE_ORIGINAL_PARTICLE108_UNITY_PROBE_V1",
            "status":("SHA_ORIGINAL_TWO_VARIANT_SMOKE34_SHADERLAB_STAGED" if smoke34 else
                      "SHA_ORIGINAL_FOUR_VARIANT_SHADERLAB_STAGED_UNITY_NOT_YET_COMPILED"),
            "source_authenticated_original_keyword_dimensions":dimensions,
            "source_original_variant_combinations":combinations,
            "original_DXBC_to_SPIRV_glslang_stage_branches_valid":2*combinations,
            "original_one_ShaderLab_pass_complete":True,
            "private_stage_local_buffer_name_isolation_only":diagnostic_stage_buffers,
            "private_vertex_cbuffer_identifiers_disambiguated":0 if isolated is None else isolated["vertex"],
            "private_fragment_cbuffer_identifiers_disambiguated":0 if isolated is None else isolated["fragment"],
            "private_original_sampler_binding_parity_proven":False,
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
    p.add_argument("--diagnostic-stage-buffers",action="store_true")
    p.add_argument("--smoke34",action="store_true")
    a=p.parse_args()
    prepare(a.shader,a.editor,a.project,a.report,a.routing,
            diagnostic_stage_buffers=a.diagnostic_stage_buffers,smoke34=a.smoke34)

if __name__=="__main__":
    main()
