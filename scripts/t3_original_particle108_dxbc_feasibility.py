#!/usr/bin/env python3
"""T3: immutable original highest particle-use Shader48 genuine D3D11 VS/FS links.

Select the unique 108-use ParticleSystemRenderer Shader48 from SHA-authenticated
six scenes + four Shader/Material owners, never by original name or GUID.
For original source ONLY, link normal-pass Vertex/Fragment program table
records with exact keyword permutation equality, no program bytes leaked.
A genuine original DXBC link is not an Android-compiled ShaderLab or pixel fix.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import t3_original_renderer_shader_impact as source
from scripts import t3_original_top_shader_dxbc_feasibility as top
from scripts import t3_original_particle_shader_state as state
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms,records

RANKS=(108,34,34,20,16,3)
STATUS="SOURCE_SHA_ORIGINAL_PARTICLE108_D3D11_STAGE_LINKAGE_CLASSIFIED"
NO_D3D11="SOURCE_SHA_ORIGINAL_PARTICLE108_D3D11_PLATFORM_UNAVAILABLE"
SAFE_FIELDS=(
    "genuine_D3D11_vertex_stage_variant_records",
    "genuine_D3D11_fragment_stage_variant_records",
    "distinct_original_linked_D3D11_programs",
    "matched_vertex_fragment_permutation_pairs",
    "normal_passes_with_matched_permutation_pair",
    "normal_passes_without_matched_permutation_pair",
    "unmatched_vertex_permutations",
    "unmatched_fragment_permutations",
    "stage_variants_with_keywords",
)


def select(private:dict,report:dict)->tuple:
    if (type(private) is not dict or len(private)!=len(RANKS)
        or sorted(private.values(),reverse=True)!=list(RANKS)
        or any(type(value) is not int for value in private.values())
        or type(report) is not dict or report.get("status")!=source.STATUS
        or report.get("six_original_scenes_sha_verified") is not True
        or report.get("original_particle_Shader48_ranked_material_slot_use_no_identity")!=list(RANKS)
        or report.get("original_particle_highest_Shader48_unique") is not True
        or report.get("original_particle_highest_Shader48_nonparticle_renderer_slots")!=0
        or report.get("original_particle_highest_Shader48_original_pass_count")!=1):
        raise ValueError("untrusted_original_108_particle_Shader48_source_graph")
    keys=[key for key,value in private.items() if value==RANKS[0]]
    if (len(keys)!=1 or type(keys[0]) is not tuple or len(keys[0])!=2
        or keys[0][0] not in source.SHADER_OWNERS_SELECTED
        or type(keys[0][1]) is not int or keys[0][1]<=0):
        raise ValueError("untrusted_unique_original_particle_Shader48_identity")
    return keys[0]


def inspect(parsed:dict,table:list|None,*,link=None)->dict:
    """Strict source-only linked stage counts; no identifiers or program data."""
    profile=state.inspect_parsed(parsed)
    if profile.get("source_108_particle_shader_original_normal_Pass") is not True:
        raise ValueError("expected_one_source_normal_ParticleShader_pass")
    values={
        "schema_version":1,
        "status":NO_D3D11 if table is None else STATUS,
        "original_source_108_particle_Shader48_slots":108,
        "original_source_108_particle_Shader48_distinct_renderers":54,
        "original_source_one_SubShader_one_Pass":True,
        "original_source_color_mask_category":profile["original_pass_color_mask_category"],
        "original_source_alpha_blend_category":profile["original_pass_color_blend_category"],
        "source_original_program_bytes_or_program_hashes_published":False,
        "original_shader_name_ID_GUID_or_shader_text_disclosed":False,
        "source_is_phone_fire_smoke_emitter_verified":False,
        "authored_Android_ShaderLab_or_SPIRV_equivalence_proven":False,
        "actual_Unity_Android_Adreno_pixels_verified":False,
    }
    if table is None:
        values.update({key:0 for key in SAFE_FIELDS})
        values["original_D3D11_program_table_records"]=0
        values["original_all_compiled_vertex_fragment_stages_available"]=False
        return values
    if (type(table) is not list or not table or len(table)>200000
        or any(type(row) is not tuple or len(row)!=2
               or type(row[0]) is not int or row[0]<0
               or type(row[1]) is not bytes or not row[1]
               for row in table)):
        raise ValueError("invalid_authentic_original_D3D11_program_entry_scope")
    kwargs={} if link is None else {"link":link}
    summary=top.summarize(parsed,table,**kwargs)
    if (summary.get("status")!=top.STATUS
        or summary.get("original_source_Shader48_SubShader_count")!=1
        or summary.get("original_source_Shader48_pass_count")!=1
        or summary.get("normal_passes")!=1
        or summary.get("non_normal_passes_not_stage_linked")!=0
        or type(summary.get("original_source_pass_types_aggregate")) is not dict
        or summary["original_source_pass_types_aggregate"]!={"0":1}
        or any(type(summary.get(key)) is not int or summary[key]<0
               for key in SAFE_FIELDS)):
        raise ValueError("original_particle_D3D11_one_pass_linkage_summary_mismatch")
    values.update({key:summary[key] for key in SAFE_FIELDS})
    values["original_D3D11_program_table_records"]=len(table)
    values["original_all_compiled_vertex_fragment_stages_available"]=(
        values["genuine_D3D11_vertex_stage_variant_records"]>0
        and values["genuine_D3D11_fragment_stage_variant_records"]>0
        and values["matched_vertex_fragment_permutation_pairs"]>0)
    return values


def probe(original:Path,manifest:Path)->dict:
    private={}
    report=source.load_original(original,manifest,
        private_particle_slot_counts=private)
    owner,pid=select(private,report)
    path=original/"Raft_Data"/owner
    if (any(x.is_symlink() for x in (path,*path.parents))
        or fingerprint(path)!=SHADER_OWNERS[owner]):
        raise ValueError("changed_original_particle_Shader48_owner_SHA")
    import UnityPy
    objects=[o for o in UnityPy.load(str(path)).file.objects.values()
             if o.path_id==pid]
    if len(objects)!=1 or objects[0].type.name!="Shader":
        raise ValueError("original_particle_shader_type_or_identity_mismatch")
    tree=objects[0].read_typetree()
    parsed=tree.get("m_ParsedForm")
    tables=[records(segments) for platform,segments in decoded_platforms(tree)
            if platform==4]
    if len(tables)>1:
        raise ValueError("duplicate_original_D3D11_program_platform")
    out=inspect(parsed,tables[0] if tables else None)
    out.update(original_six_source_scenes_SHA_verified=True,
               original_four_shader_owner_SHA_verified=True)
    return out


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for arg in ("original","manifest","out"):
        parser.add_argument("--"+arg,required=True,type=Path)
    a=parser.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_original_particle_D3D11_public_report")
    try:
        output=probe(a.original,a.manifest)
    except Exception as exc:
        output={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "source_original_program_bytes_or_program_hashes_published":False,
                "original_shader_name_ID_GUID_or_shader_text_disclosed":False,
                "actual_Unity_Android_Adreno_pixels_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_D3D11_LINKAGE "+json.dumps(output,sort_keys=True))
    return 0 if output["status"] in (STATUS,NO_D3D11) else 2

if __name__=="__main__":
    raise SystemExit(main())
