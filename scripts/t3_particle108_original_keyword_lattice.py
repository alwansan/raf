#!/usr/bin/env python3
"""Original Shader48 four-pair serialized keyword lattice diagnostic.

Read exact SHA-authenticated ZIP2 originals privately. Output only structural
counts and whether an exact independent two-toggle *index* lattice exists.
Index membership does NOT give keyword names, Unity authored variant directives,
hardware tier dispatch, real material bindings or on-device shader equivalence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import t3_original_renderer_shader_impact as impact
from scripts import t3_original_particle108_dxbc_feasibility as identity
from scripts import t3_original_particle108_spirv_translation as paired
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_depth_passes import stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms, records

STATUS="T3_SOURCE_AUTHENTIC_PARTICLE108_FOUR_KEYWORD_SERIALIZED_STRUCTURE"
# No dynamic errors, identifiers, original indices, paths or compiler stderr.
PUBLIC_FAILURE_CODES=frozenset({
    "invalid_original_tier","invalid_original_bucket",
    "invalid_original_keyword_indices","wrong_original_pass_kind",
    "not_four_original_stage_variants","invalid_original_variant_ordinal",
    "original_duplicate_keyword_bucket_tier",
    "original_VSFS_keyword_bucket_tier_mismatch",
    "original_owner_SHA_drift","original_source_identity_not_unique",
    "original_D3D11_variant_blob_table_drift",
    "original_DXBC_pair_linkage_drift","original_subshader_pass_drift",
    "original_particle108_stage_keyword_bucket_mismatch",
    "not_four_original_particle108_stage_variants",
    "untrusted_original_particle108_program_table",
    "untrusted_original_particle108_one_Pass_graph",
})

def safe_failure(exc:Exception)->str:
    """Allowlist only our invariant strings, never arbitrary original errors."""
    reason=str(exc) if type(exc) is ValueError else ""
    return reason if reason in PUBLIC_FAILURE_CODES else "UNCLASSIFIED_ORIGINAL_SOURCE"

FIELDS=("m_KeywordIndices", "m_GlobalKeywordIndices", "m_LocalKeywordIndices")
MAX_INDEX=65535


def _source_key(bucket, metadata):
    """Anonymous variant identity. Never return original private index literals."""
    if type(metadata) is not dict:
        raise ValueError("invalid_original_tier")
    # Some original serialized SubPrograms omit the optional tier field.
    # Missing is NOT equivalent to tier 0; retain an explicit unknown sentinel.
    tier=metadata.get("m_ShaderHardwareTier")
    if "m_ShaderHardwareTier" in metadata:
        if type(tier) is not int or not 0<=tier<=255:
            raise ValueError("invalid_original_tier")
    if bucket is not None and (type(bucket) is not int or not 0<=bucket<32):
        raise ValueError("invalid_original_bucket")
    tokens=set()
    family_counts=[]
    for family in FIELDS:
        raw=metadata.get(family,[])
        if type(raw) is not list or len(raw)>128 or any(
            type(n) is not int or not 0<=n<=MAX_INDEX for n in raw
        ) or len(set(raw))!=len(raw):
            raise ValueError("invalid_original_keyword_indices")
        family_counts.append(len(raw))
        tokens.update((family,n) for n in raw)
    return (bucket,tier,frozenset(tokens)), family_counts


def classify(pass_record:dict)->dict:
    """Two stages must agree on exact source index sets AND original bucket/tier."""
    if (type(pass_record) is not dict or type(pass_record.get("m_Type")) is not int
        or pass_record["m_Type"]!=0):
        raise ValueError("wrong_original_pass_kind")
    variants={}
    family_totals=Counter()
    for stage_field in ("progVertex","progFragment"):
        rows=stage_variants(pass_record.get(stage_field) or {})
        if len(rows)!=4:
            raise ValueError("not_four_original_stage_variants")
        keys=[]
        for bucket,ordinal,meta in rows:
            if type(ordinal) is not int or ordinal<0:
                raise ValueError("invalid_original_variant_ordinal")
            key,count=_source_key(bucket,meta)
            keys.append(key)
            for family,num in zip(FIELDS,count):
                family_totals[stage_field+"_"+family]+=num
        if len(set(keys))!=4:
            raise ValueError("original_duplicate_keyword_bucket_tier")
        variants[stage_field]=set(keys)
    if variants["progVertex"]!=variants["progFragment"]:
        raise ValueError("original_VSFS_keyword_bucket_tier_mismatch")
    observed=variants["progVertex"]
    groups={(b,t) for b,t,_ in observed}
    # Only the *same* hardware/player bucket can be represented by a simple
    # two-keyword combinatorial toggle. Cross-tier programs need other logic.
    all_tokens=[tokens for _,_,tokens in observed]
    common=set.intersection(*(set(s) for s in all_tokens))
    additions=frozenset().union(*(set(s)-common for s in all_tokens))
    stripped={frozenset(set(s)-common) for s in all_tokens}
    # The actual index values/names cannot be exposed; prove only set shape.
    two_toggle_index_shape=(
        len(additions)==2 and len(stripped)==4
        and stripped=={frozenset(),*map(frozenset,({x} for x in additions)),frozenset(additions)}
    )
    tier_tags_explicit=sum(tier is not None for _,tier,_ in observed)
    # Even if four keyword SETS form a lattice, missing tier metadata means
    # one-tier selection cannot be claimed from serialized evidence.
    two_toggle=(
        two_toggle_index_shape and len(groups)==1 and tier_tags_explicit==4
    )
    return {
        "schema_version":1,"status":STATUS,
        "source_original_stage_variants_per_stage":4,
        "source_original_VSFS_serialized_variant_keys_exact":True,
        "source_original_distinct_bucket_tier_groups":len(groups),
        "source_original_explicit_tier_metadata_rows_per_stage":tier_tags_explicit,
        "source_original_absent_tier_metadata_rows_per_stage":4-tier_tags_explicit,
        "source_original_two_switch_index_set_shape_regardless_of_tier":two_toggle_index_shape,
        "source_original_keyword_baseline_intersection_count":len(common),
        "source_original_keyword_variable_index_dimension_count":len(additions),
        "source_original_exact_independent_two_toggle_index_lattice":two_toggle,
        "source_original_keyword_index_field_entry_counts":{
            name:int(family_totals[name]) for stage_field in ("progVertex","progFragment")
            for family in FIELDS for name in (stage_field+"_"+family,)},
        "original_keyword_index_to_authored_name_mapping_proven":False,
        "all_four_variants_selectable_in_one_Unity_ShaderLab_proven":False,
        "original_material_runtime_shader_binding_proven":False,
        "Unity_Editor_compilation_or_phone_pixels_verified":False,
        "source_keyword_names_indices_bytes_guids_or_paths_published":False
    }


def probe(original:Path,manifest:Path)->dict:
    if (not isinstance(original,Path) or not original.is_dir()
        or original.is_symlink() or not isinstance(manifest,Path)
        or not manifest.is_file() or manifest.is_symlink()):
        raise ValueError("unsafe_original_source_path")
    private={}
    report=impact.load_original(original,manifest,private_particle_slot_counts=private)
    owner,pid=identity.select(private,report)
    source=original/"Raft_Data"/owner
    if source.is_symlink() or fingerprint(source)!=SHADER_OWNERS[owner]:
        raise ValueError("original_owner_SHA_drift")
    import UnityPy
    objs=[x for x in UnityPy.load(str(source)).file.objects.values()
          if x.path_id==pid and x.type.name=="Shader"]
    if len(objs)!=1:
        raise ValueError("original_source_identity_not_unique")
    shader=objs[0].read_typetree()
    tables=[records(parts) for p,parts in decoded_platforms(shader) if p==4]
    if len(tables)!=1 or len(tables[0])!=16:
        raise ValueError("original_D3D11_variant_blob_table_drift")
    parsed=shader.get("m_ParsedForm")
    # Reuse the SOURCE SHA original VS/FS pair linkage, not just metadata.
    pairs=paired.exact_four_pairs(parsed,tables[0])
    if len(pairs)!=4:
        raise ValueError("original_DXBC_pair_linkage_drift")
    rows=parsed["m_SubShaders"][0]["m_Passes"]
    if len(rows)!=1:
        raise ValueError("original_subshader_pass_drift")
    out=classify(rows[0])
    out["source_original_six_scenes_SHA_authenticated"]=True
    out["source_original_four_shader_owners_SHA_authenticated"]=True
    out["source_original_D3D11_keyword_pairs_linked"]=len(pairs)
    return out


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--original",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())
        or not args.out.parent.is_dir()):
        raise ValueError("unsafe_public_report_destination")
    try:
        result=probe(args.original,args.manifest)
    except Exception as e:
        # No free-form private exception text/values in public logs.
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_category":type(e).__name__,
                "failure_code":safe_failure(e),
                "original_keyword_index_to_authored_name_mapping_proven":False,
                "Unity_Editor_compilation_or_phone_pixels_verified":False,
                "source_keyword_names_indices_bytes_guids_or_paths_published":False}
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("T3_PRIVATE_ORIGINAL_KEYWORD_LATTICE_SAFE="+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
