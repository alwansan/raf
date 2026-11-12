#!/usr/bin/env python3
"""GT synthetic Unity2021 keyword scope control (NOT original Raft runtime).

A disposable two-shader Android Vulkan AssetBundle tests serialized keyword
flag bytes for pragma multi_compile versus multi_compile_local. Inspect only
bounded numeric fields, no source game Material, GUID or shader is touched.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

NAME="GT_SCOPE_PROBE"
SHADERS={"global":"GT/ScopeControlGlobal", "local":"GT/ScopeControlLocal"}
MAX_BUNDLE_BYTES=8*1024*1024


def shader_text(scope):
    if scope not in SHADERS:
        raise ValueError("unrecognized_synthetic_scope")
    directive="multi_compile" if scope=="global" else "multi_compile_local"
    return (
        'Shader "'+SHADERS[scope]+'" {\n'
        'SubShader { Pass {\nHLSLPROGRAM\n'
        '#pragma target 4.5\n#pragma vertex vert\n#pragma fragment frag\n'
        '#pragma '+directive+' __ '+NAME+'\n'
        'float4 vert(float4 p:POSITION):SV_POSITION {return p;}\n'
        'float4 frag():SV_Target {return float4(1,1,1,1);}\n'
        'ENDHLSL\n} }\n}\n'
    )


def prepare(editor:Path, project:Path):
    editor,project=Path(editor).absolute(),Path(project).absolute()
    if (not editor.is_file() or editor.is_symlink() or project.exists()
            or project.is_symlink() or not project.parent.is_dir()
            or not 0<editor.stat().st_size<131072):
        raise ValueError("synthetic_keyword_project_paths_invalid")
    project.mkdir()
    try:
        (project/"Assets/Editor").mkdir(parents=True)
        (project/"Packages").mkdir()
        (project/"ProjectSettings").mkdir()
        for scope in SHADERS:
            (project/("Assets/GTScope"+scope.title()+".shader")).write_text(
                shader_text(scope),encoding="utf-8")
        shutil.copyfile(editor,project/"Assets/Editor/GTKeywordScopeControl.cs")
        (project/"Packages/manifest.json").write_text(
            '{"dependencies":{}}\n',encoding="utf-8")
        (project/"ProjectSettings/ProjectVersion.txt").write_text(
            "m_EditorVersion: 2021.3.45f2\n",encoding="utf-8")
    except BaseException:
        shutil.rmtree(project,ignore_errors=True)
        raise
    return {"status":"SYNTHETIC_SCOPE_CONTROL_PREPARED",
            "synthetic_shader_count":2,"original_game_assets_modified":False}


def summarize_controls(rows:dict, source_flag:int):
    if type(source_flag) is not int or not 0<=source_flag<=255:
        raise ValueError("original_source_flag_input_invalid")
    if type(rows) is not dict or set(rows)!=set(SHADERS):
        raise ValueError("synthetic_keyword_scope_rows_incomplete")
    for scope,value in rows.items():
        if type(value) is not int or not 0<=value<=255:
            raise ValueError("synthetic_serialized_flag_untrusted")
    distinct=(rows["global"]!=rows["local"])
    matches=[scope for scope,value in rows.items() if value==source_flag]
    return {
        "status": "SYNTHETIC_UNITY2021_FLAG_SCOPE_CONTROL_OBSERVED",
        "global_synthetic_flag_byte": rows["global"],
        "local_synthetic_flag_byte": rows["local"],
        "synthetic_global_local_flag_bytes_distinguishable": distinct,
        "original_Spectrum_index4_observed_source_flag_byte":source_flag,
        "matching_synthetic_controls": len(matches),
        "candidate_scope_by_matching_byte":matches[0] if distinct and len(matches)==1 else "undetermined",
        "source_original_Spectrum_keyword_scope_proven":False,
        "original_Material_keyword_selection_proven":False,
        "game_Shader_or_GUID_modified":False,
        "Adreno_pixels_verified":False,
    }


def inspect(bundle:Path, unity_safe:Path, out:Path, source_flag:int):
    import UnityPy
    bundle,unity_safe,out=map(lambda p:Path(p).absolute(),(bundle,unity_safe,out))
    if (not bundle.is_file() or bundle.is_symlink()
            or not 0<bundle.stat().st_size<=MAX_BUNDLE_BYTES
            or not unity_safe.is_file() or unity_safe.is_symlink()
            or out.exists() or not out.parent.is_dir()):
        raise ValueError("synthetic_unity_bundle_report_invalid")
    status=json.loads(unity_safe.read_text(encoding="utf-8"))
    checks={"status":"SYNTHETIC_UNITY2021_KEYWORD_SCOPE_CONTROL_BUNDLE",
            "unityVersion":"2021.3.45f2",
            "globalKeywordIsOverridable":True,
            "localKeywordIsOverridable":False,
            "globalAndLocalShadersImported":True,
            "androidVulkanBundleBuilt":True,
            "shaderErrorCount":0,
            "originalGameAssetsModified":False}
    if any(type(status.get(k)) is not type(v) or status[k]!=v for k,v in checks.items()):
        raise ValueError("synthetic_unity_runtime_scope_control_not_accepted")
    env=UnityPy.load(str(bundle))
    rows={}
    for obj in env.objects:
        if obj.type.name!="Shader":
            continue
        tree=obj.read_typetree()
        parsed=tree.get("m_ParsedForm")
        if type(parsed) is not dict:
            raise ValueError("synthetic_shader_parsed_form_missing")
        shader_name=parsed.get("m_Name")
        matches=[scope for scope,name in SHADERS.items() if name==shader_name]
        if not matches:
            continue
        scope=matches[0]
        if scope in rows:
            raise ValueError("synthetic_shader_duplicate_scope")
        names=parsed.get("m_KeywordNames")
        flags=parsed.get("m_KeywordFlags")
        if isinstance(flags,(bytes,bytearray)):
            flags=list(flags)
        if (type(names) is not list or type(flags) is not list
                or len(names)!=len(flags) or names.count(NAME)!=1):
            raise ValueError("synthetic_shader_keyword_table_invalid")
        rows[scope]=flags[names.index(NAME)]
    report=summarize_controls(rows,source_flag)
    report["unity2021_keyword_isOverridable_control_verified"]=True
    report["original_source_shader_read_in_this_control"]=False
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="command",required=True)
    build=sub.add_parser("prepare")
    build.add_argument("--editor",type=Path,required=True)
    build.add_argument("--project",type=Path,required=True)
    check=sub.add_parser("inspect")
    check.add_argument("--bundle",type=Path,required=True)
    check.add_argument("--unity-safe",type=Path,required=True)
    check.add_argument("--out",type=Path,required=True)
    check.add_argument("--source-index4-flag",type=int,required=True)
    x=p.parse_args()
    try:
        result=prepare(x.editor,x.project) if x.command=="prepare" else inspect(
            x.bundle,x.unity_safe,x.out,x.source_index4_flag)
    except BaseException as exc:
        print("GT_SYNTHETIC_FLAG_SEMANTICS_SAFE "+json.dumps({
            "status":"INCONCLUSIVE","error_type":type(exc).__name__,
            "source_original_Spectrum_keyword_scope_proven":False,
            "game_Shader_or_GUID_modified":False},sort_keys=True))
        return 2
    print("GT_SYNTHETIC_FLAG_SEMANTICS_SAFE "+json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
