#!/usr/bin/env python3
"""GFX-MULTI-006: source-only typed shader program variant feasibility inventory.

No source shader names/IDs, compiled code, bytecode, keywords or state values
leave the ephemeral GitHub runner. Counts are evidence, never shader parity.
"""
import argparse,json
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries

def _find_subprogram_rows(value):
    """Traverse v2 m_SubPrograms and Unity 2021 v3 m_PlayerSubPrograms tiers.

    Count typed entries without printing original GPU program payloads, indices,
    identifiers, keywords or source property names.
    """
    if isinstance(value,list):
        result=[]
        for x in value:
            if x is None:raise ValueError("MALFORMED_ORIGINAL_SUBPROGRAM")
            result.extend(_find_subprogram_rows(x))
        return result
    if isinstance(value,dict):
        if isinstance(value.get("m_BlobIndex"),int):
            return [value]
        result=[]
        for k in ("m_SubPrograms","m_PlayerSubPrograms"):
            if k in value:result.extend(_find_subprogram_rows(value[k]))
        return result
    return []

def stage_inventory(program):
    if not isinstance(program,dict):
        return dict(variant_count=0,legacy_variant_count=0,player_variant_count=0,
            legacy_metadata_field_present=False,player_metadata_field_present=False,
            blob_indices_present=0,keyword_metadata_variants=0,parameter_metadata_variants=0)
    legacy=_find_subprogram_rows(program.get("m_SubPrograms"))
    player=_find_subprogram_rows(program.get("m_PlayerSubPrograms"))
    variants=legacy+player
    blob=sum(isinstance(s.get("m_BlobIndex"),int) for s in variants)
    kw=sum(any(k in s for k in ("m_GlobalKeywords","m_LocalKeywords","m_Keywords","m_KeywordIndices"))
        for s in variants)
    param=sum(any(k in s for k in ("m_Parameters","m_ConstantBuffers","m_Samplers"))
        for s in variants)
    return dict(variant_count=len(variants),legacy_variant_count=len(legacy),
        player_variant_count=len(player),
        legacy_metadata_field_present="m_SubPrograms" in program,
        player_metadata_field_present="m_PlayerSubPrograms" in program,
        blob_indices_present=blob,keyword_metadata_variants=kw,
        parameter_metadata_variants=param)

def inventory(tree):
    if not isinstance(tree,dict) or not isinstance(tree.get("m_ParsedForm"),dict):
        raise ValueError("MISSING_PARSED_ORIGINAL_SHADER")
    subs=tree["m_ParsedForm"].get("m_SubShaders")
    if not isinstance(subs,list) or not subs:raise ValueError("MISSING_SOURCE_SUBSHADERS")
    result=[]
    for si,sub in enumerate(subs):
        passes=sub.get("m_Passes") if isinstance(sub,dict) else None
        if not isinstance(passes,list):raise ValueError("INVALID_SOURCE_PASSES")
        for pi,p in enumerate(passes):
            if not isinstance(p,dict):raise ValueError("INVALID_SOURCE_PASS")
            v=stage_inventory(p.get("progVertex"))
            f=stage_inventory(p.get("progFragment"))
            result.append(dict(subshader_ordinal=si,pass_ordinal=pi,vertex=v,fragment=f,
                original_gles_stage_execution_verified=False))
    if len(result)!=7:raise ValueError("ORIGINAL_PASS_COUNT_DRIFT")
    platforms=tree.get("m_Platforms",tree.get("platforms"))
    platform_count=len(platforms) if isinstance(platforms,list) else 0
    compressed=tree.get("m_CompressedLengths",tree.get("compressedLengths"))
    compressed_metadata_count=len(compressed) if isinstance(compressed,list) else 0
    return dict(pass_programs=result,source_compiled_platform_metadata_entries=platform_count,
        source_compression_metadata_entries=compressed_metadata_count,
        source_gpu_program_blob_exported=False,source_shader_name_exported=False,
        original_android_stage_binary_proven=False,dxbc_to_gles_semantic_equivalence_verified=False)

def audit(stage):
    entries,types,_=all_model_entries(stage)
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("MODEL_SELECTION_DRIFT")
    unique={}
    total=0
    for e in entries:
        for m in e["materials"]:
            total+=1;key=(m["shader_owner"],m["shader_pid"])
            obj=types[key[0]].get(key[1])
            if obj is None or obj.type.name!="Shader":raise ValueError("NOT_TYPED_CLASS48")
            if key not in unique:unique[key]=inventory(obj.read_typetree(check_read=False))
    if total!=7 or len(unique)!=1:raise ValueError("ORIGINAL_SHADER_IDENTITY_DRIFT")
    inv=next(iter(unique.values()))
    return dict(experiment="GFX-MULTI-006",source_sha=ZIP2_SHA,source_models=6,
      material_slots=7,distinct_shader48=1,inventory=inv,
      compiled_shader_code_exported=False,original_android_shader_restored=False,
      gpu_device_tested_with_original_shader=False,phase_closed=False)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    result=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI006_SAFE_VARIANT_FEASIBILITY "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
