"""Privately correlate residual real-export Dummy Shader names to SHA-original scene Shader48.

Only the 21 proven source Shader48 targets from six immutable original Raft
scenes are eligible. This is a source-name digest join, NOT same-export GUID
or Shader48 owner identity proof; duplicates remain ambiguous. No proprietary
original path IDs, shader names, digests or GUIDs leave runner private memory.

The source archive stays ZIP2-pinned, output contains anonymous priority
weights, and no APK or game assets are created or modified.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from scripts.t3_original_renderer_shader_impact import (
    STATUS as ORIGINAL_STATUS, SHADER_OWNERS_SELECTED, load_original,
)
from scripts.gt_original_921_all_variants import authenticated_shader_reader

STATUS="GT_SOURCE_SCENE_RESIDUAL_SHADER_MATERIAL_PRIORITY_CORRELATED"
EXPECTED_ORIGINAL_SCENE_SHADER_TARGETS=21
EXPECTED_SOURCE_SCENE_SHADER_SLOTS=1633
EXPECTED_POSTNINE_DUMMY_MATERIALS=333


def correlate(source_names, source_slots, residual):
    """Pure conservative SHA256(name) match; ambiguous names are never selected."""
    if (not isinstance(source_names,dict) or not isinstance(source_slots,dict)
            or set(source_names)!=set(source_slots)
            or len(source_names)!=EXPECTED_ORIGINAL_SCENE_SHADER_TARGETS
            or sum(source_slots.values())!=EXPECTED_SOURCE_SCENE_SHADER_SLOTS
            or not isinstance(residual,dict)
            or sum(residual.values())!=EXPECTED_POSTNINE_DUMMY_MATERIALS):
        raise ValueError("incomplete_real_original_source_priority_scope")
    by_digest=defaultdict(list)
    for key,name in source_names.items():
        if (not isinstance(key,tuple) or len(key)!=2
                or key[0] not in SHADER_OWNERS_SELECTED
                or type(key[1]) is not int or key[1]<=0
                or not isinstance(name,str) or not name
                or type(source_slots[key]) is not int or source_slots[key]<=0):
            raise ValueError("unverified_original_Shader_name_or_scope")
        by_digest[sha256(name.encode("utf-8")).hexdigest()].append(key)
    if any(type(digest) is not str or len(digest)!=64 or
           type(count) is not int or count<=0 for digest,count in residual.items()):
        raise ValueError("invalid_real_export_dummy_name_digest_frequency")
    targets=[]
    ambiguous_groups=0
    ambiguous_material_links=0
    for digest,keys in by_digest.items():
        if digest not in residual:
            continue
        if len(keys)!=1:
            ambiguous_groups+=1
            ambiguous_material_links+=residual[digest]
            continue
        key=keys[0]
        targets.append({
            "private_original_shader_owner":key[0],
            "private_original_shader_path_id":key[1],
            "private_original_shader_name_digest":digest,
            "same_name_digest_exported_dummy_material_documents":residual[digest],
            "source_scene_renderer_material_slots":source_slots[key],
        })
    targets.sort(key=lambda row:(
        -row["same_name_digest_exported_dummy_material_documents"],
        -row["source_scene_renderer_material_slots"],
        row["private_original_shader_owner"],
        row["private_original_shader_path_id"]))
    distinct_matching_digests={x["private_original_shader_name_digest"] for x in targets}
    unmatched={k:v for k,v in residual.items()
               if k not in distinct_matching_digests and k not in {
                   d for d,keys in by_digest.items() if len(keys)!=1
               }}
    matched_materials=sum(x["same_name_digest_exported_dummy_material_documents"]
                          for x in targets)
    report={
        "schema_version":1,
        "status":STATUS,
        "source_six_scene_authenticated_Shader48_targets":len(source_names),
        "source_scene_shader48_renderer_material_slots":sum(source_slots.values()),
        "real_export_remaining_dummy_material_documents":sum(residual.values()),
        "matched_unambiguous_source_shader_targets":len(targets),
        "matched_unambiguous_exported_dummy_material_documents":matched_materials,
        "matched_original_scene_renderer_slot_weights_in_export_material_priority_order":[
            x["source_scene_renderer_material_slots"] for x in targets],
        "matched_original_export_dummy_material_link_weights_in_descending_order":[
            x["same_name_digest_exported_dummy_material_documents"] for x in targets],
        "ambiguous_source_name_groups":ambiguous_groups,
        "ambiguous_source_name_exported_material_links":ambiguous_material_links,
        "remaining_unmatched_export_name_digest_groups":len(unmatched),
        "remaining_unmatched_export_dummy_material_documents":sum(unmatched.values()),
        "source_original_Shader48_to_same_export_GUID_matched":False,
        "original_name_hash_match_is_not_verified_Shader48_export_identity":True,
        "not_yet_restored_Dummy_materials_are_not_all_original_scene_shaders":True,
        "new_Unity_shader_compilation_performed":False,
        "source_assets_or_meta_modified":False,
        "APK_OBB_XAPK_created":False,
        "published_names_GUIDs_private_original_ids_or_digests":False,
    }
    if (matched_materials+ambiguous_material_links+sum(unmatched.values())
            !=EXPECTED_POSTNINE_DUMMY_MATERIALS):
        raise ValueError("original_name_digests_residual_material_accounting_drift")
    return targets,report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for option in ("original","manifest","quality","out"):
        p.add_argument("--"+option,type=Path,required=True)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
            or a.out.resolve().is_relative_to(a.original.resolve())
            or a.out.resolve().is_relative_to(a.quality.resolve())):
        raise ValueError("unsafe_shader_priority_output_destination")
    try:
        source_slots={}
        proof=load_original(a.original,a.manifest,private_slot_counts=source_slots)
        slots={key:value for key,value in source_slots.items()
               if key[0] in SHADER_OWNERS_SELECTED}
        if (proof["status"]!=ORIGINAL_STATUS or
                proof.get("six_original_scenes_sha_verified") is not True
                or len(slots)!=EXPECTED_ORIGINAL_SCENE_SHADER_TARGETS):
            raise ValueError("unverified_original_scene_Shader48_scope")
        reader=authenticated_shader_reader(a.original)
        names={key:reader(key)["m_ParsedForm"]["m_Name"] for key in slots}
        q=json.loads(a.quality.read_text(encoding="utf-8"))
        if (q.get("status")!="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY" or
                q.get("counts",{}).get("material_docs_using_dummy_Shader")
                !=EXPECTED_POSTNINE_DUMMY_MATERIALS):
            raise ValueError("wrong_or_unaccepted_nine_shader_quality_report")
        private,report=correlate(names,slots,q["dummy_shader_material_counts_by_name_digest"])
        # Only anonymous weights are released. Original Shader path IDs, names,
        # and guessed links are in ephemeral memory and never written to disk.
        if len(private)!=report["matched_unambiguous_source_shader_targets"]:
            raise AssertionError("private_shader_priority_mismatch")
    except Exception as error:
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "error_type":type(error).__name__,
                "published_names_GUIDs_private_original_ids_or_digests":False,
                "APK_OBB_XAPK_created":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",
                     encoding="utf-8")
    print("GT_SOURCE_NAME_MATCH_RESIDUAL_SHADER_PRIORITY "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
