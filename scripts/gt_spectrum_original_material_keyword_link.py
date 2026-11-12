#!/usr/bin/env python3
"""GT: SHA-authentic 40-owner Material -> Spectrum PathID2432 PPtr census.

Checks the actual target owner/PathID/keyword index4 from immutable ZIP2,
never guesses a shader by material name. Source-only: no ExportedProject GUID,
runtime material keyword enablement, sampler, CB0, RT, or phone proof.
Publishes aggregate counts only; no serialized source or keyword names.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import json
import os
from pathlib import Path
import subprocess

from scripts.b09_spectrum_topology_contract import OWNER, PATH_ID, TARGET
from scripts.b09_stage_original_spectrum import _selected_original
from scripts.gt_spectrum_original_keyword_flags import inspect_flags
from scripts.t2_original_foam_material_host_scan import (
    select_sharedowners, MAX_EXTERNALS, MAX_MATERIALS, MAX_OBJECTS)
from scripts.t2_foam_original_manifest_pptr import parse_original_manifest
from scripts.w1_stage_zip2_owners import PINS, ZIP2_SHA, fingerprint, safe, stage

MAX_ROWS = 2000
ROOT_COUNT = 40
ROOT_BYTES = 474065455
EXPECTED_FLAG = 0
METRICS = (
    "all_materials", "matched_local", "matched_external",
    "matched_keyword_index4_valid", "matched_keyword_index4_invalid",
    "matched_keyword_index4_both", "matched_keyword_index4_neither",
    "matched_materials_without_keyword_arrays", "matched_valid_names_outside_original_table"
)


def matching_target(owner: str, externals: list[str], shader_ptr: dict) -> str:
    if type(owner) is not str or not owner.startswith("Raft_Data/sharedassets") or not owner.endswith(".assets"):
        raise ValueError("original_owner_invalid")
    if type(externals) is not list or len(externals) > MAX_EXTERNALS:
        raise ValueError("original_externals_invalid")
    if type(shader_ptr) is not dict or set(shader_ptr) != {"m_FileID", "m_PathID"}:
        raise ValueError("original_shader_pptr_invalid")
    fid, pid = shader_ptr["m_FileID"], shader_ptr["m_PathID"]
    if type(fid) is not int or type(pid) is not int or fid < 0 or pid < 0:
        raise ValueError("original_shader_pptr_negative_or_untyped")
    if fid == 0:
        return "local" if owner == "Raft_Data/" + OWNER and pid == PATH_ID else "other"
    if fid > len(externals):
        raise ValueError("source_external_shader_fileid_out_of_range")
    path=externals[fid-1]
    if type(path) is not str or not path or "\x00" in path:
        raise ValueError("original_shader_external_path_invalid")
    basename=path.replace("\\", "/").rsplit("/",1)[-1]
    return "external" if basename == OWNER and pid == PATH_ID else "other"


def count_owners(owner_rows: list, original_keyword: str, original_names: list[str]) -> dict:
    if (type(owner_rows) is not list or len(owner_rows)!=ROOT_COUNT
            or type(original_keyword) is not str or not original_keyword
            or type(original_names) is not list or len(original_names)!=5
            or original_names[4]!=original_keyword):
        raise ValueError("original_spectrum_material_scope_invalid")
    sums=Counter({name:0 for name in METRICS})
    for row in owner_rows:
        if (type(row) is not dict or type(row.get("owner")) is not str
                or type(row.get("externals")) is not list
                or type(row.get("materials")) is not list
                or len(row["materials"])>MAX_MATERIALS):
            raise ValueError("original_material_owner_row_invalid")
        for mat in row["materials"]:
            if type(mat) is not dict or "m_Shader" not in mat:
                raise ValueError("original_material_tree_invalid")
            sums["all_materials"]+=1
            kind=matching_target(row["owner"], row["externals"], mat["m_Shader"])
            if kind=="other":
                continue
            sums["matched_"+kind]+=1
            valid=mat.get("m_ValidKeywords")
            invalid=mat.get("m_InvalidKeywords")
            if valid is None or invalid is None:
                sums["matched_materials_without_keyword_arrays"]+=1
                continue
            if (type(valid) is not list or type(invalid) is not list
                    or any(type(x) is not str for x in valid+invalid)):
                raise ValueError("original_material_keyword_arrays_untrusted")
            on=original_keyword in valid
            off=original_keyword in invalid
            if on and off:
                sums["matched_keyword_index4_both"]+=1
            elif on:
                sums["matched_keyword_index4_valid"]+=1
            elif off:
                sums["matched_keyword_index4_invalid"]+=1
            else:
                sums["matched_keyword_index4_neither"]+=1
            if any(x not in original_names for x in valid):
                sums["matched_valid_names_outside_original_table"]+=1
    total=sums["matched_local"]+sums["matched_external"]
    if (sums["matched_materials_without_keyword_arrays"]
        +sum(sums["matched_keyword_index4_"+v] for v in ("both","valid","invalid","neither"))!=total):
        raise ValueError("original_keyword_material_accounting_incomplete")
    return {
        "status":"SOURCE_AUTHENTIC_SPECTRUM_40_SHAREDASSETS_MATERIAL_PPTR_CENSUS",
        "original_sharedassets_owners":ROOT_COUNT,
        "original_sharedassets_owner_bytes":ROOT_BYTES,
        "original_Spectrum_shader_owner_pathid_object_authenticated":True,
        "original_index4_flag_byte":EXPECTED_FLAG,
        "original_keyword_names_published":False,
        "source_40_owner_census_only":True,
        "not_full_82_owner_or_runtime_material_census":True,
        "original_exported_guid_or_android_runtime_verified":False,
        **{name:sums[name] for name in METRICS}
    }


def real(zip2:Path, scratch:Path, out:Path):
    import UnityPy
    zip2,scratch,out=[Path(p).absolute() for p in (zip2,scratch,out)]
    for p in (zip2,scratch,out.parent): safe(p)
    if (not zip2.is_dir() or not scratch.parent.is_dir() or scratch.exists()
            or out.exists() or not out.parent.is_dir()
            or scratch.is_relative_to(zip2)
            or any(out.is_relative_to(x) for x in (zip2,scratch))):
        raise ValueError("original_material_census_paths_invalid")
    sha=subprocess.check_output(["git","-C",str(zip2),"rev-parse","HEAD"],
                                text=True,stderr=subprocess.DEVNULL).strip()
    if sha!=ZIP2_SHA: raise ValueError("original_zip2_SHA_mismatch")
    rows=select_sharedowners(parse_original_manifest(zip2/"RAFT_FILE_MANIFEST.tsv"))
    if len(rows)!=ROOT_COUNT or sum(x["bytes"] for x in rows)!=ROOT_BYTES:
        raise ValueError("source_sharedassets_expected_scope_changed")
    patterns=["/RAFT_FILE_MANIFEST.tsv"]
    for row in rows:
        patterns.append("/Raft/"+row["path"]+("/*" if row["kind"]=="split" else ""))
    subprocess.run(["git","-C",str(zip2),"sparse-checkout","set","--no-cone",*patterns],
                   timeout=240,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    pins={r["path"]:(r["bytes"],r["sha256"]) for r in rows}
    proof=stage(zip2,scratch,pins)
    if (proof["verified_bytes"]!=ROOT_BYTES or proof["lfs_used"] is not False
            or proof["provider_sha"]!=ZIP2_SHA):
        raise ValueError("original_40_owner_stage_incomplete")
    # B09 SHA-original shader reader is restricted to flat private scratch input.
    flat=scratch/OWNER
    os.link(scratch/"Raft_Data"/OWNER,flat)
    _,_,tree,auth=_selected_original(scratch)
    if (auth["authenticated_original_passes"]!=7
            or auth["authenticated_variant_stage_programs"]!=28):
        raise ValueError("Spectrum_original_target_source_attestation_missing")
    parsed=tree.get("m_ParsedForm")
    flags=inspect_flags(parsed)
    if flags["original_keyword_index4_flag_byte"]!=EXPECTED_FLAG:
        raise ValueError("Spectrum_index4_original_flag_changed")
    keyword=parsed["m_KeywordNames"][4]
    original_names=parsed["m_KeywordNames"]
    owner_rows=[]
    for row in rows:
        name=row["path"]
        path=scratch/name
        if fingerprint(path)!=pins[name]:
            raise ValueError("original_40_owner_source_SHA_changed")
        env=UnityPy.load(str(path))
        file=env.file
        if (len(file.objects)>MAX_OBJECTS or len(file.externals)>MAX_EXTERNALS):
            raise ValueError("original_40_owner_serialized_budget_exceeded")
        materials=[]
        for obj in file.objects.values():
            if obj.type.name!="Material":continue
            if len(materials)>=MAX_MATERIALS:raise ValueError("original_material_count_exceeds_bound")
            materials.append(obj.read_typetree())
        owner_rows.append({
            "owner":name,
            "externals":[e.path for e in file.externals],
            "materials":materials
        })
        del materials,env,file
        gc.collect()
    result=count_owners(owner_rows,keyword,original_names)
    if result["all_materials"]>MAX_ROWS:
        raise ValueError("source_material_population_exceeds_budget")
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--scratch",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    try:
        result=real(a.zip2,a.scratch,a.out)
    except BaseException as exc:
        print("GT_SPECTRUM_SOURCE_MATERIAL_SAFE "+json.dumps({
            "status":"INCONCLUSIVE","error_type":type(exc).__name__,
            "original_exported_guid_or_android_runtime_verified":False,
            "source_40_owner_census_only":True},sort_keys=True))
        return 2
    print("GT_SPECTRUM_SOURCE_MATERIAL_SAFE "+json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
