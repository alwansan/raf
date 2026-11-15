"""Probe original D3D11 pass/keyword topology of highest unresolved Material shaders.

Uses the SHA256-verified 82-owner original Shader48 census. Only name-digest
matched, uniquely identified source Shader48 objects may be inspected. Raw
DXBC, HLSL, shader names and IDs never leave ephemeral CI. A probe is NOT a
recovered original ShaderLab program, Unity Android compilation, or device render.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from scripts.gt_rank_all82_original_shader_names_after_nine import gather
from scripts.gt_stage_serialized_owners import read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.t3_original_top_shader_dxbc_feasibility import summarize
from scripts.w1_recover_graphics_programs import decoded_platforms, records

STATUS="GT_TOP_REAL_DUMMY_MATERIAL_SHADER48_ORIGINAL_D3D11_PASS_TOPOLOGY_PROBED"
TOP=12


def ranked_candidates(original_hashes, materials, *, top=TOP):
    if (type(original_hashes) is not dict or type(materials) is not dict
            or top<1 or top>32 or sum(materials.values())!=333):
        raise ValueError("unverified_remaining_source_D3D11_probe_scope")
    by_name=defaultdict(list)
    for key,digest in original_hashes.items():
        if not isinstance(key,tuple) or len(key)!=2 or not isinstance(digest,str):
            raise ValueError("malformed_original_Shader48_source_digest")
        by_name[digest].append(key)
    ordered=sorted(materials.items(),key=lambda x:(-x[1],x[0]))[:top]
    out=[]
    for digest,material_count in ordered:
        if type(digest) is not str or len(digest)!=64 or type(material_count) is not int:
            raise ValueError("invalid_source_shader_material_frequency")
        matched=by_name.get(digest,[])
        if len(matched)!=1:
            out.append((material_count,None,len(matched)))
        else:
            out.append((material_count,matched[0],1))
    return out


def inspect(original, manifest, source_name_hashes, materials, *, top=TOP):
    import UnityPy
    candidates=ranked_candidates(source_name_hashes,materials,top=top)
    expected=read_expected(manifest)
    result=[]
    # Cache no game source once the original-identity candidate is inspected.
    for count,target,candidate_count in candidates:
        row={"custom_dummy_material_documents":count,
             "original_Shader48_source_candidate_count":candidate_count,
             "status":"AMBIGUOUS_OR_NOT_IN_SOURCE",
             "original_D3D11_paired_stages_proven":False}
        if target is None:
            result.append(row)
            continue
        owner,pid=target
        if owner not in expected:
            raise ValueError("original_Shader48_owner_unverified")
        kind,size,digest=expected[owner]
        provider=original/owner
        verify(provider,size,digest)
        env=UnityPy.load(str(provider))
        objects=[obj for obj in env.objects if obj.path_id==pid and str(obj.type.name)=="Shader"]
        if len(objects)!=1:
            raise ValueError("original_SHA_Shader48_object_missing")
        tree=objects[0].read_typetree()
        try:
            tables=[records(chunks) for platform,chunks in decoded_platforms(tree) if platform==4]
            if len(tables)!=1:
                row["status"]="NO_UNIQUE_ORIGINAL_D3D11_PROGRAM_TABLE"
            else:
                audit=summarize(tree.get("m_ParsedForm"),tables[0])
                row.update({
                    "status":"ORIGINAL_D3D11_VERTEX_FRAGMENT_LINKS_PROBED",
                    "original_SubShaders":audit["original_source_Shader48_SubShader_count"],
                    "original_pass_count":audit["original_source_Shader48_pass_count"],
                    "original_normal_pass_count":audit["normal_passes"],
                    "original_non_normal_pass_count":audit["non_normal_passes_not_stage_linked"],
                    "original_paired_keyword_routes":audit["matched_vertex_fragment_permutation_pairs"],
                    "original_unmatched_vertex_permutations":audit["unmatched_vertex_permutations"],
                    "original_unmatched_fragment_permutations":audit["unmatched_fragment_permutations"],
                    "original_distinct_D3D11_programs":audit["distinct_original_linked_D3D11_programs"],
                    "original_source_stage_variants_with_keywords":audit["stage_variants_with_keywords"],
                    "original_D3D11_paired_stages_proven":audit["normal_passes_with_matched_permutation_pair"]>0,
                })
        except Exception as exc:
            row["status"]="SOURCE_D3D11_TOPOLOGY_INCONCLUSIVE"
            row["error_type"]=type(exc).__name__
        result.append(row)
        del env
    return {
        "schema_version":1,
        "status":STATUS,
        "probe_ranked_by_current_real_export_Material_usage":True,
        "source_original_82_owner_Shader48_SHA_verified":True,
        "top_original_dummy_Material_shader_targets_requested":top,
        "top_actual_unresolved_Material_link_weights":[x[0] for x in candidates],
        "top_real_source_D3D11_topology_by_rank":result,
        "source_program_translation_or_Vulkan_compilation_performed":False,
        "source_exact_export_GUID_inferred_from_name":False,
        "source_Shader_names_PathIDs_DXBC_HLSL_or_GUIDs_published":False,
        "APK_OBB_XAPK_created":False,
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ("original","manifest","quality","out"):
        parser.add_argument("--"+key,type=Path,required=True)
    args=parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
            args.out.resolve().is_relative_to(args.original.resolve())
            or args.out.resolve().is_relative_to(args.quality.resolve())):
        raise ValueError("unsafe_original_shader_D3D11_topology_report")
    try:
        hashes,owners=gather(args.original,args.manifest)
        report=json.loads(args.quality.read_text(encoding="utf-8"))
        if (report.get("status")!="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
                or report.get("counts",{}).get("material_docs_using_dummy_Shader")!=333
                or report.get("counts",{}).get("material_documents")!=1536):
            raise ValueError("unsupported_real_postnine_Shader_quality_report")
        output=inspect(args.original,args.manifest,hashes,
                       report["dummy_shader_material_counts_by_name_digest"])
        output["original_Shader48_distinct_source_objects"]=len(hashes)
        output["original_owners_with_original_Shader48"]=owners
    except Exception as error:
        output={"schema_version":1,"status":"INCONCLUSIVE",
                "error_type":type(error).__name__,
                "APK_OBB_XAPK_created":False,
                "source_Shader_names_PathIDs_DXBC_HLSL_or_GUIDs_published":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("GT_TOP_ORIGINAL_DUMMY_SHADER48_D3D11_FEASIBILITY "+json.dumps(output,sort_keys=True))
    return 0 if output["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
