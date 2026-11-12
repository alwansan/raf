#!/usr/bin/env python3
"""GT: exact 82-owner SHA-original Material -> Spectrum shader PPtr closure.

Unlike the earlier 40 sharedassets-only census, includes 40 scenes and 2
additional serialized owners. Immutable ZIP2 SHA + 82 individual SHA hashes
are required. No Material names, shader bytes, path IDs, GUIDs or raw data
are published. Zero matches is a legitimate and useful SOURCE conclusion:
it does not prove no runtime-created water materials.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import json
from pathlib import Path
import subprocess

from scripts.b09_stage_original_spectrum import _selected_original
from scripts.gt_spectrum_original_keyword_flags import inspect_flags
from scripts.gt_stage_serialized_owners import OWNERS, read_expected, stage
from scripts.gt_serialized_graphics_counts import verify
from scripts.w1_stage_zip2_owners import ZIP2_SHA, safe

TARGET_OWNER="sharedassets0.assets"
TARGET_ID=2432
EXPECTED_OWNERS=82
EXPECTED_BYTES=819595355
EXPECTED_MATERIALS=1556
MAX_OBJECTS=1500000
MAX_EXTERNALS=65535


def classify(owner: str, externals: list, ptr: dict):
    if type(owner) is not str or owner not in OWNERS:
        raise ValueError("owner_not_in_authenticated_82_set")
    if type(externals) is not list or len(externals)>MAX_EXTERNALS:
        raise ValueError("source_external_table_invalid")
    if type(ptr) is not dict or set(ptr)!={"m_FileID","m_PathID"}:
        raise ValueError("source_material_shader_pptr_invalid")
    fid,pid=ptr["m_FileID"],ptr["m_PathID"]
    if type(fid) is not int or type(pid) is not int or fid<0 or pid<0:
        raise ValueError("source_shader_pptr_negative_or_untyped")
    if fid==0:
        return "local" if owner==TARGET_OWNER and pid==TARGET_ID else "other"
    if fid>len(externals):
        raise ValueError("source_shader_pptr_external_index_out_of_range")
    external=externals[fid-1]
    if type(external) is not str or not external or "\x00" in external:
        raise ValueError("source_shader_external_path_invalid")
    basename=external.replace("\\","/").rsplit("/",1)[-1]
    return "external" if basename==TARGET_OWNER and pid==TARGET_ID else "other"


def summarize(rows:list, keyword:str, names:list):
    if (type(rows) is not list or len(rows)!=EXPECTED_OWNERS
            or type(keyword) is not str or not keyword
            or type(names) is not list or len(names)!=5
            or names[4]!=keyword):
        raise ValueError("original_source_82_owner_scope_untrusted")
    seen=set()
    c=Counter()
    for row in rows:
        if type(row) is not dict or set(row)!={"owner","external","materials"}:
            raise ValueError("original_source_82_owner_row_invalid")
        owner,external,materials=row["owner"],row["external"],row["materials"]
        if type(owner) is not str or owner in seen or owner not in OWNERS:
            raise ValueError("original_source_owner_dup_or_missing")
        seen.add(owner)
        if type(materials) is not list or type(external) is not list:
            raise ValueError("original_source_owner_fields_invalid")
        for d in materials:
            c["all_materials"]+=1
            if type(d) is not dict or "m_Shader" not in d:
                raise ValueError("source_material_shader_ref_missing")
            k=classify(owner,external,d["m_Shader"])
            if k=="other":
                continue
            c["target_"+k]+=1
            valid=d.get("m_ValidKeywords")
            invalid=d.get("m_InvalidKeywords")
            if valid is None or invalid is None:
                c["target_keyword_arrays_absent"]+=1
                continue
            if (type(valid) is not list or type(invalid) is not list
                    or any(type(v) is not str for v in valid+invalid)):
                raise ValueError("source_keyword_array_invalid")
            on=keyword in valid
            off=keyword in invalid
            status=("both" if on and off else
                    "enabled" if on else
                    "invalid" if off else "not_listed")
            c["target_keyword_"+status]+=1
            if any(k not in names for k in valid):
                c["target_valid_keyword_outside_original_shader"]+=1
    if set(seen)!=set(OWNERS) or c["all_materials"]!=EXPECTED_MATERIALS:
        raise ValueError("source_82_owner_or_1556_materials_incomplete")
    matched=c["target_local"]+c["target_external"]
    if (matched!=c["target_keyword_arrays_absent"]
            +sum(c["target_keyword_"+k] for k in ("both","enabled","invalid","not_listed"))):
        raise ValueError("source_target_keyword_partition_invalid")
    return {
        "status":"SOURCE_AUTHENTIC_SPECTRUM_82_OWNER_MATERIAL_SHADER_PPTR_CLOSURE",
        "original_serialized_owners_SHA_verified":EXPECTED_OWNERS,
        "original_serialized_owner_bytes_SHA_verified":EXPECTED_BYTES,
        "original_material_documents_inspected":c["all_materials"],
        "original_shader_pathID2432_in_sharedassets0_SHA_verified":True,
        "original_source_flag_index4":0,
        "exact_material_references_local":c["target_local"],
        "exact_material_references_external":c["target_external"],
        "exact_material_references_total":matched,
        **{key:c[key] for key in (
          "target_keyword_arrays_absent","target_keyword_both",
          "target_keyword_enabled","target_keyword_invalid","target_keyword_not_listed",
          "target_valid_keyword_outside_original_shader")},
        "full_82_serialized_owner_source_material_scope":True,
        "runtime_materials_or_Shader_Find_scanned":False,
        "source_original_keyword_names_or_materials_published":False,
        "exported_Unity_GUID_or_RT_CB0_sampler_verified":False,
        "Unity_or_Adreno_water_pixels_verified":False,
        "original_data_modified":False,
        "git_lfs_used":False
    }


def real(zip2:Path, scratch:Path, out:Path):
    import UnityPy
    zip2,scratch,out=[Path(p).absolute() for p in (zip2,scratch,out)]
    for p in (zip2,scratch,out.parent):safe(p)
    if (not zip2.is_dir() or scratch.exists() or not scratch.parent.is_dir()
            or out.exists() or not out.parent.is_dir()
            or scratch.is_relative_to(zip2)
            or out.is_relative_to(zip2) or out.is_relative_to(scratch)):
        raise ValueError("original_82_owners_path_boundary_invalid")
    head=subprocess.check_output(["git","-C",str(zip2),"rev-parse","HEAD"],
                                 text=True,stderr=subprocess.DEVNULL).strip()
    if head!=ZIP2_SHA:
        raise ValueError("source_zip2_SHA_drift")
    manifest=zip2/"RAFT_FILE_MANIFEST.tsv"
    expected=read_expected(manifest)
    if len(expected)!=EXPECTED_OWNERS:
        raise ValueError("original_82_manifest_incomplete")
    patterns=["/RAFT_FILE_MANIFEST.tsv"]+[
        "/Raft/Raft_Data/"+n+("/*" if expected[n][0]=="split" else "")
        for n in sorted(OWNERS)
    ]
    subprocess.run(["git","-C",str(zip2),"sparse-checkout","set","--no-cone",*patterns],
                   check=True,timeout=300,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    proof=stage(zip2/"Raft"/"Raft_Data",manifest,scratch)
    if (proof["source_commit"]!=ZIP2_SHA or proof["selected_owners"]!=EXPECTED_OWNERS
            or proof["verified_bytes"]!=EXPECTED_BYTES
            or proof["all_82_serialized_owners"] is not True):
        raise ValueError("source_82_SHA_reassembly_incomplete")
    _,_,original,auth=_selected_original(scratch)
    if (auth.get("authenticated_original_passes")!=7
            or auth.get("authenticated_variant_stage_programs")!=28):
        raise ValueError("source_Spectrum_shader_identity_unproven")
    parsed=original["m_ParsedForm"]
    flags=inspect_flags(parsed)
    if flags["original_keyword_index4_flag_byte"]!=0:
        raise ValueError("source_Spectrum_keyword_flag_drift")
    keyword=parsed["m_KeywordNames"][4]
    rows=[]
    for owner in sorted(OWNERS):
        _,size,sha=expected[owner]
        provider=scratch/owner
        verify(provider,size,sha)
        env=UnityPy.load(str(provider))
        f=env.file
        if (len(f.objects)>MAX_OBJECTS or len(f.externals)>MAX_EXTERNALS):
            raise ValueError("original_source_82_reader_budget_exceeded")
        materials=[o.read_typetree() for o in f.objects.values()
                   if o.type.name=="Material"]
        rows.append({"owner":owner,
                     "external":[entry.path for entry in f.externals],
                     "materials":materials})
        del env,f,materials
        gc.collect()
    result=summarize(rows,keyword,parsed["m_KeywordNames"])
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--scratch",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    try:
        result=real(a.zip2,a.scratch,a.out)
    except BaseException as e:
        print("GT_SPECTRUM_82_ORIGINAL_MATERIAL_SAFE "+json.dumps({
            "status":"INCONCLUSIVE","error_type":type(e).__name__,
            "runtime_materials_or_Shader_Find_scanned":False,
            "original_data_modified":False},sort_keys=True))
        return 2
    print("GT_SPECTRUM_82_ORIGINAL_MATERIAL_SAFE "+json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
