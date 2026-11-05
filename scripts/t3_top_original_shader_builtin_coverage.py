#!/usr/bin/env python3
"""T3 high original Renderer Shader48 use vs exact Unity 2021 built-in identities.

The source Shader48 with 921 six-scene original Renderer Material-slot uses
still exported Dummy after TMP/PostFX/Volumetric. Before rebuilding its private
compiled passes, determine if the genuine source Shader identity is present
among the 198 runtime built-in ShaderLab programs for Unity 2021.3.45f2.
The vendor archive is checked against a fixed SHA256 before parsing names.
Names/PathIDs/GUIDs/programs are never exposed in reports or console output.
A name match alone does NOT prove restorer application, compiled program
identity, Unity import or Android GPU pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import urllib.request

from scripts import t3_original_renderer_shader_impact as source_graph
from scripts.restore_builtin_shaders import URL, SHA256, archive_sources

STATUS="SOURCE_SHADER48_TO_VERIFIED_UNITY2021_BUILTIN_NAME_COVERAGE_CLASSIFIED"
EXPECTED_SHADERS=21
EXPECTED_SOURCE_SLOTS=1633
EXPECTED_TOP=921


def compare(source_use:dict, names:dict, builtin_names:set,*,sha_verified:bool=False):
    if (not isinstance(source_use,dict) or not isinstance(names,dict)
        or not isinstance(builtin_names,(set,frozenset))
        or len(source_use)!=EXPECTED_SHADERS
        or set(source_use)!=set(names)
        or sum(source_use.values())!=EXPECTED_SOURCE_SLOTS):
        raise ValueError("untrusted_original_Shader48_name_match_scope")
    if any(not isinstance(key,tuple) or len(key)!=2
           or key[0] not in source_graph.SHADER_OWNERS_SELECTED
           or type(key[1]) is not int or key[1]<=0
           or type(n) is not int or n<=0 for key,n in source_use.items()):
        raise ValueError("malformed_authenticated_original_Shader48_identity")
    if any(not isinstance(name,str) or not name or "\x00" in name for name in names.values()):
        raise ValueError("malformed_original_Shader48_name")
    if any(not isinstance(name,str) or not name or "\x00" in name for name in builtin_names):
        raise ValueError("malformed_verifiable_Unity_built_in_Shader_identity")
    peak=max(source_use.values())
    if peak!=EXPECTED_TOP or sum(n==peak for n in source_use.values())!=1:
        raise ValueError("expected_single_original_921_renderer_slot_Shader_changed")
    maxkey=max(source_use,key=source_use.get)
    matched={k for k in source_use if names[k] in builtin_names}
    all_slots=sum(source_use[k] for k in matched)
    top_covered=maxkey in matched
    match_weights=sorted((source_use[k] for k in matched),reverse=True)
    nonmatch_weights=sorted((source_use[k] for k in source_use if k not in matched),reverse=True)
    return {
        "schema_version":1,
        "experiment":"T3-six-scene-original-Shader48-use-vs-verified-Unity2021-builtins",
        "original_source_Shader48_targets":EXPECTED_SHADERS,
        "original_source_Shader48_Renderer_Material_slot_uses":EXPECTED_SOURCE_SLOTS,
        "pinned_Unity2021_runtime_shader_archive_SHA_verified":sha_verified,
        "authenticated_Unity2021_runtime_shader_identities":len(builtin_names),
        "original_source_Shader48_targets_exact_name_in_Unity_archive":len(matched),
        "original_scene_renderer_slot_uses_exact_name_in_Unity_archive":all_slots,
        "original_source_Shader48_targets_without_Unity_builtin_name_match":len(source_use)-len(matched),
        "original_scene_renderer_slot_uses_without_Unity_builtin_name_match":EXPECTED_SOURCE_SLOTS-all_slots,
        "highest_original_921_source_shader_name_in_Unity2021_builtins":top_covered,
        "top_source_slot_uses_with_2021_builtin_name_match_no_identity":match_weights[:10],
        "top_source_slot_uses_without_2021_builtin_name_match_no_identity":nonmatch_weights[:10],
        "names_or_raw_original_IDs_Guids_programs_published":False,
        "exact_name_match_not_evidence_original_compiled_program_equivalence":True,
        "native_builtin_restorer_actual_application_not_verified":True,
        "Unity_2021_Android_import_or_Adreno_pixels_not_verified":True,
        "status":STATUS if sha_verified else "SYNTHETIC_NAME_CLASSIFICATION_ONLY",
    }


def source_shader_names(root:Path,selected:set):
    import UnityPy
    result={}
    if len(selected)!=EXPECTED_SHADERS:
        raise ValueError("original_21_typed_Shader_source_scope_changed")
    by_owner={}
    for owner,pid in selected:
        by_owner.setdefault(owner,set()).add(pid)
    for owner,paths in by_owner.items():
        if owner not in source_graph.SHADER_OWNERS_SELECTED:
            raise ValueError("original_Shader_source_owner_not_authenticated")
        env=UnityPy.load(str(root/"Raft_Data"/owner))
        for obj in env.file.objects.values():
            if obj.path_id not in paths:continue
            key=(owner,obj.path_id)
            if key in result or obj.type.name!="Shader":
                raise ValueError("original_Shader48_identity_or_class_changed")
            parsed=obj.read_typetree().get("m_ParsedForm")
            if not isinstance(parsed,dict):
                raise ValueError("original_Shader48_parsed_form_missing")
            name=parsed.get("m_Name")
            if not isinstance(name,str) or not name:
                raise ValueError("original_Shader48_name_invalid")
            result[key]=name
    if set(result)!=selected:
        raise ValueError("source_Shader48_exact_original_identity_unresolved")
    return result


def run(original:Path,manifest:Path,archive_bytes:bytes):
    # Archive is public official Unity SHA-verified vendor source, not original
    # private game assets. verify the pinned exact SHA before parsing any names.
    import hashlib
    if hashlib.sha256(archive_bytes).hexdigest()!=SHA256:
        raise ValueError("Unity2021_vendor_Shader_archive_SHA_mismatch")
    vendor,_,license_bytes=archive_sources(archive_bytes)
    if not license_bytes or len(vendor)!=198:
        raise ValueError("incomplete_verified_2021_builtins_shader_archive")
    weights={}
    report=source_graph.load_original(original,manifest,private_slot_counts=weights)
    if (report["status"]!=source_graph.STATUS
        or report["counts"]["original_slots_to_verified_Shader48"]!=EXPECTED_SOURCE_SLOTS
        or report["original_distinct_typed_Shader48_targets"]!=EXPECTED_SHADERS):
        raise ValueError("source_sixscene_Shader48_use_census_changed")
    selected={key for key in weights if key[0] in source_graph.SHADER_OWNERS_SELECTED}
    typed_weights={key:weights[key] for key in selected}
    names=source_shader_names(original,selected)
    return compare(typed_weights,names,set(vendor),sha_verified=True)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","out"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or
        a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("report_inside_private_original_game_source_refused")
    try:
        # This URL is fixed by the pinned official built-in source restorer;
        # downloaded bytes are authenticated before name parsing.
        with urllib.request.urlopen(URL,timeout=90) as response:
            raw=response.read(7*1024*1024+1)
        if len(raw)>7*1024*1024:
            raise ValueError("oversize_Unity2021_public_runtime_shader_archive")
        report=run(a.original,a.manifest,raw)
    except Exception as error:
        report={
            "schema_version":1,
            "experiment":"T3-six-scene-original-Shader48-use-vs-verified-Unity2021-builtins",
            "status":"INCONCLUSIVE","error_type":type(error).__name__,
            "native_builtin_restorer_actual_application_not_verified":True,
            "Unity_2021_Android_import_or_Adreno_pixels_not_verified":True,
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("T3_TOP_921_SOURCE_SHADER_BUILTIN_COVERAGE "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
