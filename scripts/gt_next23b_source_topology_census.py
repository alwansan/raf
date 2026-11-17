"""SHA-original source-only topology census for unique remaining 23-material group.

Source owner/PathID/name/digest identities, raw shaders and private topology
records stay on the CI runner. This does NOT translate, install or prove Unity
shader compatibility. Never confuse it with previously installed NEXT23.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.gt_remaining_original_guid_weights import safe_remaining_weights
from scripts.gt_rank_all82_original_shader_names_after_nine import gather
from scripts.gt_stage_serialized_owners import read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.t3_original_top_shader_dxbc_feasibility import summarize
from scripts.w1_recover_graphics_programs import decoded_platforms, records

STATUS="GT_NEXT23B_SHA_ORIGINAL_REMAINING_SOURCE_TOPOLOGY_ONLY_NO_APK"


def select_remaining_23_source_owners(source_hashes, quality):
    safe_remaining_weights(quality)
    weights=quality["dummy_shader_material_counts_by_name_digest"]
    digests=[digest for digest, weight in weights.items() if weight==23]
    if len(digests)!=1:
        raise ValueError("original_post23_remaining_23_material_digest_not_unique")
    matches=[(owner,pid) for (owner,pid),digest in source_hashes.items()
             if digest==digests[0]]
    if not 1<=len(matches)<=32:
        raise ValueError("source_23_material_original_Shader48_owner_absent_or_ambiguous")
    return matches


def safe_original_23b_topology(original,manifest,quality):
    import UnityPy
    names,owners=gather(original,manifest)
    matches=select_remaining_23_source_owners(names,quality)
    pinned=read_expected(manifest)
    profiles=[]
    for owner,pid in matches:
        if owner not in pinned:
            raise ValueError("untrusted_original_next23b_source_owner")
        _,size,digest=pinned[owner]
        path=original/owner
        if not path.is_file() or path.is_symlink():
            raise ValueError("unsafe_source_original_next23b_Shader48_owner")
        verify(path,size,digest)
        env=UnityPy.load(str(path))
        shaders=[obj for obj in env.objects
                 if obj.path_id==pid and str(obj.type.name)=="Shader"]
        if len(shaders)!=1:
            raise ValueError("source_original_next23b_PathID_shader_not_unique")
        tree=shaders[0].read_typetree()
        tables=[records(data) for platform,data in decoded_platforms(tree)
                if platform==4]
        if len(tables)!=1:
            raise ValueError("source_original_next23b_D3D11_stage_table_not_unique")
        profile=summarize(tree.get("m_ParsedForm"),tables[0])
        values={key:profile[key] for key in (
            "original_source_Shader48_pass_count",
            "matched_vertex_fragment_permutation_pairs",
            "unmatched_vertex_permutations",
            "unmatched_fragment_permutations",
            "distinct_original_linked_D3D11_programs",
        )}
        if (any(type(v) is not int or v<0 for v in values.values())
                or values["original_source_Shader48_pass_count"]==0
                or values["distinct_original_linked_D3D11_programs"]==0):
            raise ValueError("untrusted_original_next23b_Shader48_program_topology")
        profiles.append(values)
    topo=Counter(tuple(row[key] for key in (
        "original_source_Shader48_pass_count",
        "matched_vertex_fragment_permutation_pairs",
        "unmatched_vertex_permutations",
        "unmatched_fragment_permutations",
        "distinct_original_linked_D3D11_programs",
    )) for row in profiles)
    return {
        "schema_version":1,
        "status":STATUS,
        "actual_source_material_quality_run":43929698985,
        "original_zip2_82_sha_owners_authenticated":True,
        "remaining_23_material_weight_group_count":1,
        "same_name_original_Shader48_source_candidate_count":len(matches),
        "source_topology_groups_count":len(topo),
        "source_topologies_numeric_only":[{
            "source_Shader48_SubShader_Pass_count":top[0],
            "paired_keyword_VSFS_route_count":top[1],
            "unpaired_vertex_variants":top[2],
            "unpaired_fragment_variants":top[3],
            "source_distinct_D3D11_programs":top[4],
            "source_owner_candidates_with_this_topology":count
        } for top,count in sorted(topo.items())],
        "original_names_digests_owner_PathIDs_GUIDs_shader_bytes_exported":False,
        "source_translation_unity_or_same_export_guid_restoration_proven":False,
        "APK_OBB_XAPK_created":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--quality",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    quality=json.loads(args.quality.read_text(encoding="utf-8"))
    report=safe_original_23b_topology(args.original,args.manifest,quality)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("GT_NEXT23B_ORIGINAL_SOURCE_TOPOLOGY_SAFE "+json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
