"""Rank remaining dummy-material ShaderLab name hashes across all 82 ZIP2 owners.

This avoids guessing source names: each original serialized Unity owner is SHA256
and byte-size verified against immutable ZIP2 manifest before reading real
Shader48 m_ParsedForm.m_Name. Match to SAME RUN post-nine exported dummy
Material count by SHA256(name). Names can collide across several distinct
original Shader48 objects: report ambiguous candidates, never assume GUID.
No original names, PathIDs, original program bytes or GUIDs are published.
No game assets, Unity project or XAPK modified.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gc
import hashlib
import json
from pathlib import Path

from scripts.gt_stage_serialized_owners import OWNERS, read_expected
from scripts.gt_serialized_graphics_counts import verify

STATUS = "GT_ALL82_ZIP2_ORIGINAL_SHADER48_NAMED_DUMMY_MATERIAL_MATCH_NO_APK"
EXPECTED_DUMMY_MATERIALS = 333
EXPECTED_ORIGINAL_OWNERS = 82


def rank_name_hashes(original_hashes, dummy_materials, *, expected_dummy_materials=EXPECTED_DUMMY_MATERIALS):
    """Only hash and numeric weights; preserve ambiguity, never pick arbitrary PPtr."""
    if (type(original_hashes) is not dict or type(dummy_materials) is not dict
            or not original_hashes or not dummy_materials
            or type(expected_dummy_materials) is not int or expected_dummy_materials<1
            or sum(dummy_materials.values()) != expected_dummy_materials):
        raise ValueError("invalid_original_82_shader_to_dummy_material_scope")
    by_digest=defaultdict(list)
    for original_id, name_digest in original_hashes.items():
        if (type(original_id) is not tuple or len(original_id)!=2
                or type(original_id[0]) is not str or
                type(original_id[1]) is not int or original_id[1]<=0
                or type(name_digest) is not str or len(name_digest)!=64):
            raise ValueError("untrusted_original_Shader48_target_or_name_digest")
        by_digest[name_digest].append(original_id)
    matched=[]
    ambiguous=[]
    missing=[]
    for digest, count in dummy_materials.items():
        if type(digest) is not str or len(digest)!=64 or type(count) is not int or count<1:
            raise ValueError("invalid_actual_exported_shader_name_digest")
        found=by_digest.get(digest,[])
        if len(found)==1:
            matched.append(count)
        elif len(found)>1:
            ambiguous.append((count,len(found)))
        else:
            missing.append(count)
    if sum(matched)+sum(x[0] for x in ambiguous)+sum(missing)!=expected_dummy_materials:
        raise ValueError("dummy_material_frequency_accounting_drift")
    return {
        "schema_version":1,
        "status":STATUS,
        "source_original_Shader48_objects_Sha_verified":len(original_hashes),
        "source_original_unique_Shader48_names":len(by_digest),
        "exporter_actual_dummy_Material_documents":expected_dummy_materials,
        "dummy_shader_names_uniquely_resolved_to_original_Shader48":len(matched),
        "dummy_material_links_uniquely_resolved_to_original_Shader48":sum(matched),
        "uniquely_named_source_Shader48_dummy_Material_priority_descending":sorted(matched,reverse=True),
        "dummy_shader_names_ambiguous_across_original_Shader48":len(ambiguous),
        "dummy_material_links_ambiguous_original_Shader48":sum(x[0] for x in ambiguous),
        "original_Shader48_name_collision_candidate_count_bands":dict(sorted(Counter(
            min(x[1],20) for x in ambiguous).items())),
        "dummy_shader_names_not_in_verified_all82_original_Shader48":len(missing),
        "dummy_material_links_not_in_verified_all82_original_Shader48":sum(missing),
        "same_export_Shader48_GUID_identity_proven_by_name":False,
        "source_original_names_GUIDs_PathIDs_or_shader_bytes_published":False,
        "original_source_or_custom_materials_changed":False,
        "Unity_Android_Vulkan_game_device_pixels_verified":False,
        "APK_OBB_XAPK_created":False,
    }


def gather(original, manifest):
    import UnityPy
    if original.is_symlink() or not original.is_dir() or manifest.is_symlink():
        raise ValueError("unsafe_serialized_source_or_manifest")
    pins=read_expected(manifest)
    if set(pins)!=set(OWNERS) or len(OWNERS)!=EXPECTED_ORIGINAL_OWNERS:
        raise ValueError("original_82_owner_immutable_manifest_scope_drift")
    shaders={}
    owners_with_shaders=0
    for name in OWNERS:
        kind,size,sha=pins[name]
        path=original/name
        if path.is_symlink() or not path.is_file():
            raise ValueError("original_serialized_82_owner_missing")
        verify(path,size,sha)
        env=UnityPy.load(str(path))
        count=0
        for obj in env.objects:
            if str(obj.type.name)!="Shader":
                continue
            key=(name,obj.path_id)
            if key in shaders:
                raise ValueError("duplicate_original_Shader48_identity")
            tree=obj.read_typetree()
            parsed=tree.get("m_ParsedForm")
            if type(parsed) is not dict or type(parsed.get("m_Name")) is not str or not parsed["m_Name"]:
                raise ValueError("missing_original_Shader48_parsed_name")
            shaders[key]=hashlib.sha256(parsed["m_Name"].encode("utf-8")).hexdigest()
            count+=1
        owners_with_shaders+=int(count>0)
        del env
        gc.collect()
    if not shaders:
        raise ValueError("none_of_82_original_owners_contain_Shader48")
    return shaders,owners_with_shaders


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ("original","manifest","quality","out"):
        parser.add_argument("--"+key,type=Path,required=True)
    parser.add_argument("--expected-dummy-materials",type=int,default=EXPECTED_DUMMY_MATERIALS)
    parser.add_argument("--expected-dummy-shaders",type=int,default=51)
    a=parser.parse_args(argv)
    if (a.out.is_symlink() or a.out.exists() or
            a.out.resolve().is_relative_to(a.original.resolve()) or
            a.out.resolve().is_relative_to(a.quality.resolve())):
        raise ValueError("unsafe_82_owner_shader_priority_result_destination")
    try:
        source,owners=gather(a.original,a.manifest)
        quality=json.loads(a.quality.read_text(encoding="utf-8"))
        if (quality.get("status")!="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
                or quality.get("counts",{}).get("material_documents")!=1536
                or quality.get("counts",{}).get("material_docs_using_dummy_Shader")!=a.expected_dummy_materials
                or quality.get("counts",{}).get("distinct_dummy_Shader_targets_referenced")!=a.expected_dummy_shaders):
            raise ValueError("untrusted_original_nine_shader_postrestore_333_dummy_report")
        report=rank_name_hashes(source,quality["dummy_shader_material_counts_by_name_digest"],
                                expected_dummy_materials=a.expected_dummy_materials)
        report["source_zip2_original_serialized_owners_SHA_verified"]=EXPECTED_ORIGINAL_OWNERS
        report["original_owners_with_Shader48"]=owners
        report["actual_same_export_custom_dummy_Shader_targets"]=a.expected_dummy_shaders
        report["full_export_quality_source_run_id"]=43759856414 if a.expected_dummy_materials==333 else 43764506277
        report["source_original_zip2_commit"]="15964ea8f246b6e076ce26b60931ee2e1a9a2385"
    except Exception as exc:
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "error_type":type(exc).__name__,
                "source_original_names_GUIDs_PathIDs_or_shader_bytes_published":False,
                "APK_OBB_XAPK_created":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("GT_ALL82_ORIGINAL_SHADER_DUMMY_MATERIAL_RANK "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
