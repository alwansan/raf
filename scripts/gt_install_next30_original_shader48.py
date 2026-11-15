"""Install the SHA-original 30-Material Shader48 at its genuine exported GUID.

Requires post13 exact 246/47 Material dummy audit, 82 original SHA-pinned
Shader48 source owners, same-instance AssetRipper Shader48 export identity
trace, candidate ShaderLab/Unity Vulkan bundle byte SHA and exact 31-route
[8,13,8,2] VS/FS SPIR-V verification. Edits only the matching .shader
bytes in disposable export, preserving .meta, Materials and other resources.
Not a game Player build, APK, pixel/Adreno or authored-equivalence proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.gt_install_original_particle108 import read_bounded
from scripts.gt_install_recovered_model_shader import install
from scripts.gt_rank_all82_original_shader_names_after_nine import gather
from scripts.gt_translate_next_remaining_30_shader48 import select_exact_30_material_name

STATUS="GT_EXACT_ORIGINAL_NEXT30_SAME_EXPORT_SHADER48_GUID_INSTALLED_NO_APK"
ROUTES=(8,13,8,2)


def source_identity(original, manifest, quality):
    q=json.loads(read_bounded(quality,65536))
    counts=q.get("counts",{})
    if (q.get("status")!="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
            or counts.get("material_documents")!=1536
            or counts.get("material_docs_using_local_custom_Shader")!=786
            or counts.get("material_docs_using_dummy_Shader")!=246
            or counts.get("distinct_dummy_Shader_targets_referenced")!=47):
        raise ValueError("unverified_post13_remaining_Dummy_Shader_scope")
    names, owners=gather(original/"Raft_Data",manifest)
    if owners!=14 or len(names)!=165:
        raise ValueError("original_82_source_Shader48_scope_drift")
    return select_exact_30_material_name(names,q["dummy_shader_material_counts_by_name_digest"])


def verify_receipt(candidate, receipt):
    required={
        "candidate_sha256":__import__("hashlib").sha256(candidate).hexdigest(),
        "compiled_program_table_verified":True,
        "vertex_and_fragment_entrypoints_verified":True,
        "vulkan_platform_only":True,
        "vertex_routes_by_pass":list(ROUTES),
        "fragment_routes_by_pass":list(ROUTES),
    }
    if type(receipt) is not dict or any(receipt.get(k)!=v for k,v in required.items()):
        raise ValueError("unverified_next30_source_authentic_Unity_Vulkan_bundle_route_receipt")


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for option in ("original","manifest","quality","project","trace","candidate",
                   "receipt","backup","out"):
        p.add_argument("--"+option,type=Path,required=True)
    args=p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
            args.out.resolve().is_relative_to(args.original.resolve()) or
            args.out.resolve().is_relative_to(args.project.resolve())
            or args.backup.resolve().is_relative_to(args.project.resolve())):
        raise ValueError("unsafe_original_next30_install_input_or_output")
    source=source_identity(args.original,args.manifest,args.quality)
    candidate=read_bounded(args.candidate,16*1024*1024)
    receipt=json.loads(read_bounded(args.receipt,65536))
    verify_receipt(candidate,receipt)
    result=install(
        args.project,json.loads(read_bounded(args.trace,40_000_000)),
        source,candidate,receipt,args.backup,counts_override=ROUTES)
    if (result.get("original_export_guid_preserved") is not True
            or result.get("vulkan_routes_installed")!=31):
        raise ValueError("original_next30_same_export_Shader48_31route_install_failed")
    safe={
        "schema_version":1,
        "status":STATUS,
        "original_source_82_owners_SHA_verified":True,
        "post13_actual_Dummy_Material_population_verified":246,
        "source_original_unrestored_Material_documents_for_selected_Shader":30,
        "original_export_Shader48_GUID_preserved":True,
        "original_ShaderLab_4_pass_routes_installed":list(ROUTES),
        "original_fragment_and_vertex_routes_Android_Vulkan_bundle_verified":True,
        "original_material_yaml_meta_modified":False,
        "original_source_Shader_names_GUIDs_PathIDs_or_program_bytes_published":False,
        "game_Player_or_XAPK_created":False,
        "Android_Adreno_pixels_verified":False,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("GT_NEXT30_ORIGINAL_SHADER48_SAME_EXPORT_GUID "+json.dumps(safe,sort_keys=True))


if __name__=="__main__":
    main()
