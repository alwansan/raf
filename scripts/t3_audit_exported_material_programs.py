#!/usr/bin/env python3
"""T3 read-only actual exported Material→ShaderLab program-quality audit.

Run AFTER authenticated native ShaderLab restorers and BEFORE a Unity build.
A correct Material.m_Shader GUID does not prove a real shader: pinned AssetRipper
defaults ShaderExportMode.Dummy and emits //DummyShaderTextExporter in placeholders.

No assets, .meta, GUID, pass, name or private source data are modified/logged.
The absence of a dummy marker is NOT authored/compiled shader authenticity.
Aggregate results cannot establish Shader variant parity or Adreno rendering.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.w1_audit_export_material_shaders import HEADER, SHADER, GUID, ENGINE, pptr

MAX_INVENTORY=150_000
MAX_YAML=256*1024*1024
MAX_SHADER=8*1024*1024
MAX_META=64*1024
RESERVED=frozenset((*ENGINE, "00000000000000000000000000000000"))
YAML_SUFFIX=frozenset((".mat",".asset",".prefab",".unity"))
COUNT_KEYS=(
    "shader_files", "shader_files_with_dummy_exporter_marker",
    "shader_files_with_no_subprograms_marker",
    "shader_files_with_unknown_exporter_marker",
    "shader_files_with_unbalanced_ShaderLab",
    "shader_files_without_passes", "shader_files_with_complete_program_pass",
    "material_documents", "material_docs_using_local_custom_Shader",
    "material_docs_using_Unity_builtin_Shader", "material_docs_with_null_Shader",
    "material_docs_with_unknown_or_broken_Shader",
    "material_docs_using_dummy_Shader", "material_docs_using_non_dummy_Shader",
    "material_docs_using_unbalanced_ShaderLab",
    "material_docs_using_Shader_without_completed_program_pass",
    "material_docs_using_Shader_with_completed_program_pass",
    "distinct_custom_Shader_targets_referenced",
    "distinct_dummy_Shader_targets_referenced",
)
STATUS="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"


def _require_unlinked_path(path:Path):
    if any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError("unsafe_linked_original_or_exported_path")


def _read(path:Path,maximum:int):
    if path.stat().st_size>maximum:
        raise ValueError("oversized_material_shader_audit_input")
    return path.read_text(encoding="utf-8-sig")


def _shader_profiles(entries:list[Path]):
    result={}
    for path in entries:
        if not path.is_file() or path.suffix!=".shader":
            continue
        meta=Path(str(path)+".meta")
        if not meta.is_file() or meta.is_symlink():
            raise ValueError("missing_local_ShaderImporter_meta")
        ids=GUID.findall(_read(meta,MAX_META))
        if len(ids)!=1:
            raise ValueError("ambiguous_local_ShaderImporter_guid")
        guid=ids[0].lower()
        if guid in RESERVED or guid in result:
            raise ValueError("reserved_or_duplicate_ShaderImporter_guid")
        txt=_read(path,MAX_SHADER)
        profile=pass_coverage(txt)
        result[guid]={
            "dummy": "//DummyShaderTextExporter" in txt,
            "no_subprograms": "// No subprograms found" in txt,
            "unknown_exporter": "ShaderUnknownExporter" in txt,
            "unbalanced": not profile["pass_braces_balanced"],
            "pass_count":profile["pass_count"],
            "programmed":profile["passes_with_complete_program"],
        }
    return result


def _material_refs(entries:list[Path]):
    rows=[]
    for path in entries:
        if not path.is_file() or path.suffix not in YAML_SUFFIX:
            continue
        if path.stat().st_size>MAX_YAML:
            raise ValueError("oversize_exported_YAML_candidate")
        with path.open("rb") as stream:
            prefix=stream.read(16)
        if not prefix.lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
            continue
        txt=path.read_text(encoding="utf-8-sig")
        headers=list(HEADER.finditer(txt))
        for i,header in enumerate(headers):
            if header[1]!="21":continue
            stop=headers[i+1].start() if i+1<len(headers) else len(txt)
            body=txt[header.end():stop]
            fields=SHADER.findall(body)
            if len(fields)!=1 or body.count("  m_Shader:")!=1:
                raise ValueError("missing_or_ambiguous_exported_material_Shader")
            file_id,guid,kind=pptr(fields[0])
            if file_id<0:raise ValueError("negative_material_Shader_file_id")
            rows.append((file_id,guid,kind))
    return rows


def audit(project:Path):
    root=Path(project).absolute()
    _require_unlinked_path(root)
    assets=root/"Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("missing_or_symlinked_Unity_Assets")
    entries=sorted(assets.rglob("*"))
    if len(entries)>MAX_INVENTORY:
        raise ValueError("oversize_Unity_Assets_inventory")
    if any(p.is_symlink() for p in entries):
        raise ValueError("linked_Unity_Assets_entry")
    shader_map=_shader_profiles(entries)
    refs=_material_refs(entries)
    if not shader_map or not refs:
        raise ValueError("no_exported_Shader_or_Material_for_diagnostic")
    c=Counter()
    c["shader_files"]=len(shader_map)
    for v in shader_map.values():
        c["shader_files_with_dummy_exporter_marker"]+=int(v["dummy"])
        c["shader_files_with_no_subprograms_marker"]+=int(v["no_subprograms"])
        c["shader_files_with_unknown_exporter_marker"]+=int(v["unknown_exporter"])
        c["shader_files_with_unbalanced_ShaderLab"]+=int(v["unbalanced"])
        c["shader_files_without_passes"]+=int(v["pass_count"]==0)
        c["shader_files_with_complete_program_pass"]+=int(v["programmed"]>0)
    c["material_documents"]=len(refs)
    custom=set()
    dummy=set()
    for file_id,guid,kind in refs:
        if file_id==0:
            if guid not in ("", "0"*32) or kind not in (None, "0"):
                raise ValueError("ambiguous_null_exported_Material_Shader")
            c["material_docs_with_null_Shader"]+=1
        elif guid in ENGINE and kind=="0":
            c["material_docs_using_Unity_builtin_Shader"]+=1
        elif file_id==4800000 and kind=="3" and guid in shader_map:
            profile=shader_map[guid]
            custom.add(guid)
            c["material_docs_using_local_custom_Shader"]+=1
            if profile["dummy"]:
                c["material_docs_using_dummy_Shader"]+=1
                dummy.add(guid)
            else:
                c["material_docs_using_non_dummy_Shader"]+=1
            if profile["unbalanced"]:
                c["material_docs_using_unbalanced_ShaderLab"]+=1
            if profile["programmed"]>0:
                c["material_docs_using_Shader_with_completed_program_pass"]+=1
            else:
                c["material_docs_using_Shader_without_completed_program_pass"]+=1
        else:
            c["material_docs_with_unknown_or_broken_Shader"]+=1
    c["distinct_custom_Shader_targets_referenced"]=len(custom)
    c["distinct_dummy_Shader_targets_referenced"]=len(dummy)
    if (c["material_docs_using_local_custom_Shader"]
         +c["material_docs_using_Unity_builtin_Shader"]
         +c["material_docs_with_null_Shader"]
         +c["material_docs_with_unknown_or_broken_Shader"]!=c["material_documents"]):
        raise AssertionError("exported_Material_reference_count_inconsistent")
    return {
        "schema_version":1,
        "purpose":"native_post_restorer_actual_Material_to_ShaderLab_quality",
        "counts":{k:c[k] for k in COUNT_KEYS},
        "selected_ShaderLab_documents_have_proven_original_programs":False,
        "source_original_Shader48_or_same_export_join_performed":False,
        "correct_GUID_does_not_establish_Shader_program_authenticity":True,
        "unity_Android_gpu_pixels_or_game_ready_verified":False,
        "asset_source_or_meta_changed":False,
        "linked_dummy_Shader_program_risk_present":c["material_docs_using_dummy_Shader"]>0,
        "status":STATUS,
    }


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.project.resolve())):
        raise ValueError("unsafe_Shader_program_report_destination")
    try:
        report=audit(a.project)
    except Exception as error:
        # Never publish third-party source/GUID/path exception message.
        report={"schema_version":1,"purpose":"native_post_restorer_actual_Material_to_ShaderLab_quality",
                "status":"INCONCLUSIVE","exception_type":type(error).__name__,
                "selected_ShaderLab_documents_have_proven_original_programs":False,
                "unity_Android_gpu_pixels_or_game_ready_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("RAFT_T3_NATIVE_MATERIAL_SHADER_PROGRAM_QUALITY "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
