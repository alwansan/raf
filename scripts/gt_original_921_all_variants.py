#!/usr/bin/env python3
"""GT: recover all compiled permutations of original SHA-authenticated 921-slot Shader48.

Original DXBC, recovered HLSL and source identities stay runner-private. This
does not claim authored ShaderLab parity, Unity import, Android, or pixels.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil

PASS_COUNT=4
PAIRED_COUNT=33
ORPHAN_VERTEX_COUNT=8
DISTINCT_DXBC_COUNT=58
STATUS="GT_ORIGINAL_921_ALL_SOURCE_PERMUTATIONS_PRIVATE_STAGE_RECOVERY"

def enumerate_all(parsed,table,*,variants,permutation,linker):
    """Never pair unrelated player buckets, tiers or keyword permutations."""
    if type(parsed) is not dict or type(parsed.get("m_SubShaders")) is not list or not parsed["m_SubShaders"]:
        raise ValueError("missing_original_shader_pass_graph")
    if type(table) is not list or not table:
        raise ValueError("missing_original_D3D11_stage_table")
    pairs,orphans,passes=[],[],[]
    distinct={}
    n_passes=0
    for si,sub in enumerate(parsed["m_SubShaders"]):
        if type(sub) is not dict or type(sub.get("m_Passes")) is not list:
            raise ValueError("invalid_original_shader_SubShader")
        for pi,item in enumerate(sub["m_Passes"]):
            n_passes+=1
            if type(item) is not dict or item.get("m_Type") != 0:
                raise ValueError("non_normal_original_shader_pass_not_synthesized")
            rows={}
            for field,stage in (("progVertex",1),("progFragment",0)):
                program=item.get(field)
                if type(program) is not dict:
                    raise ValueError("missing_original_pass_stage")
                original_variants=variants(program)
                if not 0<len(original_variants)<=256:
                    raise ValueError("unbounded_or_empty_original_stage_variant_table")
                by_key={}
                for bucket,ordinal,metadata in original_variants:
                    if (type(metadata) is not dict or type(ordinal) is not int or ordinal<0 or
                        (bucket is not None and (type(bucket) is not int or bucket<0))):
                        raise ValueError("invalid_original_stage_variant_metadata")
                    key=(bucket,permutation(metadata))
                    if key in by_key:
                        raise ValueError("duplicate_original_player_bucket_and_keyword_variant")
                    code,origin=linker(metadata,table,stage)
                    if type(code) is not bytes or not code or type(origin) is not dict:
                        raise ValueError("unlinked_original_D3D11_program")
                    ident=(stage,hashlib.sha256(code).hexdigest())
                    if ident not in distinct:
                        distinct[ident]={"stage":stage,"source_code":code}
                    by_key[key]={
                        "program_ref":ident,"player_bucket":bucket,"bucket_ordinal":ordinal,
                        "original_variant_metadata":metadata,"original_D3D11_link":origin,
                    }
                rows[stage]=by_key
            matched=rows[1].keys() & rows[0].keys()
            if not matched:
                raise ValueError("unpaired_entire_original_shader_pass")
            for key in rows[1]:
                if key in matched:
                    pairs.append({"subshader":si,"pass":pi,"vs":rows[1][key],"fs":rows[0][key]})
                else:
                    orphans.append({"subshader":si,"pass":pi,"stage":1,"variant":rows[1][key]})
            for key in rows[0]:
                if key not in matched:
                    orphans.append({"subshader":si,"pass":pi,"stage":0,"variant":rows[0][key]})
            passes.append({
                "subshader":si,"pass":pi,"original_state":item.get("m_State"),
                "original_name_indices":item.get("m_NameIndices"),
                "original_vertex_program":item.get("progVertex"),
                "original_fragment_program":item.get("progFragment"),
                "matched_pairs":len(matched),
                "unmatched_vertex":len(rows[1].keys()-matched),
                "unmatched_fragment":len(rows[0].keys()-matched),
            })
    if (n_passes!=PASS_COUNT or len(pairs)!=PAIRED_COUNT or
        sum(o["stage"]==1 for o in orphans)!=ORPHAN_VERTEX_COUNT or
        any(o["stage"]==0 for o in orphans) or len(distinct)!=DISTINCT_DXBC_COUNT):
        raise ValueError("authenticated_original_921_variant_population_drift")
    return pairs,orphans,passes,distinct

def _private_destination(path:Path,source:Path,other:Path):
    path=path.absolute()
    if (path.exists() or path.is_symlink() or path==other.absolute() or
        path.is_relative_to(source.absolute()) or
        path.is_relative_to(other.absolute()) or
        any(p.is_symlink() for p in path.parents) or not path.parent.is_dir()):
        raise ValueError("unsafe_private_original_shader_stage_destination")
    return path

def stage_private(pairs,orphans,passes,distinct,private:Path,*,translator):
    if (len(pairs)!=PAIRED_COUNT or len(orphans)!=ORPHAN_VERTEX_COUNT or
        len(passes)!=PASS_COUNT or len(distinct)!=DISTINCT_DXBC_COUNT):
        raise ValueError("non_original_921_stage_inventory")
    private.mkdir(mode=0o700)
    refs={}
    counts=Counter()
    for index,(ident,item) in enumerate(distinct.items()):
        folder=private/("program-%03d"%index)
        folder.mkdir(mode=0o700)
        refs[ident]=folder.name
        result=translator(item["source_code"],item["stage"],folder)
        if type(result) is not dict or any(type(result.get(k)) is not bool for k in
            ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")):
            raise ValueError("untrusted_private_original_stage_compiler_result")
        counts["attempted"]+=1
        for field in ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid"):
            counts[field]+=int(result[field])
    def materialize(row):
        return {k:(refs[v] if k=="program_ref" else v) for k,v in row.items()}
    packet={
        "schema":1,"original_passes":passes,
        "paired":[{"subshader":p["subshader"],"pass":p["pass"],
                   "vs":materialize(p["vs"]),"fs":materialize(p["fs"])} for p in pairs],
        "unpaired":[{"subshader":o["subshader"],"pass":o["pass"],"stage":o["stage"],
                     "variant":materialize(o["variant"])} for o in orphans],
    }
    (private/"original-private-variant-manifest.json").write_text(
        json.dumps(packet,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return {
        "schema_version":1,"status":STATUS,
        "scope":"six_SHA_original_scenes_selected_921_renderer_material_slots",
        "original_passes":len(passes),
        "exact_original_source_VS_FS_permutation_pairs":len(pairs),
        "unmatched_original_vertex_variants_retained":len(orphans),
        "unmatched_original_fragment_variants":0,
        "original_unique_D3D11_stage_programs":len(distinct),
        "private_stage_translation_attempts":counts["attempted"],
        "private_vulkan11_valid_stages":counts["vulkan11_valid"],
        "private_HLSL_recovered_stages":counts["hlsl_recovered"],
        "private_HLSL_roundtrip_vulkan11_valid_stages":counts["roundtrip_vulkan11_valid"],
        "all_distinct_original_D3D11_programs_translated":counts["roundtrip_vulkan11_valid"]==len(distinct),
        "all_original_921_shader_variant_population_extracted_to_private_stage":True,
        "original_authored_ShaderLab_or_Sampler_CB0_render_parity_verified":False,
        "original_project_Shader_GUID_replaced":False,
        "original_game_assets_or_meta_modified":False,
        "Unity_Editor_Android_or_device_pixels_verified":False,
        "original_source_IDs_GUIDs_shader_names_or_program_bytes_published":False,
    }

def run(original:Path,manifest:Path,private:Path,out:Path,*,translator=None):
    from scripts import t3_original_renderer_shader_impact as scenes
    from scripts import t3_original_top_shader_dxbc_feasibility as top
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms,records,translate
    from scripts.w1_recover_depth_passes import linked_program,stage_variants,variant_key
    if translator is None:translator=translate
    for binary in ("vkd3d-compiler","spirv-val","spirv-cross","glslangValidator"):
        if not shutil.which(binary):
            raise ValueError("missing_required_original_DXBC_translation_tool")
    use={}
    report=scenes.load_original(original,manifest,private_slot_counts=use)
    owner,path_id=top.selected_high_use(use,report)
    source=original/"Raft_Data"/owner
    if source.is_symlink() or fingerprint(source)!=SHADER_OWNERS[owner]:
        raise ValueError("original_921_Shader_owner_SHA_mismatch")
    import UnityPy
    candidates=[o for o in UnityPy.load(str(source)).file.objects.values() if o.path_id==path_id]
    if len(candidates)!=1 or candidates[0].type.name!="Shader":
        raise ValueError("original_921_Shader48_object_identity_mismatch")
    tree=candidates[0].read_typetree()
    tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    if len(tables)!=1:
        raise ValueError("ambiguous_original_921_D3D11_program_table")
    baseline=top.summarize(tree.get("m_ParsedForm"),tables[0])
    if (baseline["original_source_Shader48_pass_count"]!=PASS_COUNT or
        baseline["matched_vertex_fragment_permutation_pairs"]!=PAIRED_COUNT or
        baseline["unmatched_vertex_permutations"]!=ORPHAN_VERTEX_COUNT or
        baseline["unmatched_fragment_permutations"]!=0 or
        baseline["distinct_original_linked_D3D11_programs"]!=DISTINCT_DXBC_COUNT):
        raise ValueError("original_921_authenticated_shader_variant_baseline_drift")
    pairs,orphans,passes,unique=enumerate_all(
        tree["m_ParsedForm"],tables[0],variants=stage_variants,
        permutation=variant_key,linker=linked_program)
    private=_private_destination(private,original,out)
    out=_private_destination(out,original,private)
    safe=stage_private(pairs,orphans,passes,unique,private,translator=translator)
    with out.open("x",encoding="utf-8") as target:
        json.dump(safe,target,sort_keys=True,indent=2)
        target.write("\n")
    return safe

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","private","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args(argv)
    try:
        safe=run(a.original,a.manifest,a.private,a.out)
    except Exception as error:
        print("GT_ORIGINAL_921_ALL_VARIANTS_BLOCKED "+json.dumps({
            "status":"INCONCLUSIVE","exception_type":type(error).__name__,
            "source_program_bytes_or_IDs_disclosed":False}))
        return 2
    print("GT_ORIGINAL_921_ALL_VARIANTS_SAFE "+json.dumps(safe,sort_keys=True))
    return 0 if safe["all_distinct_original_D3D11_programs_translated"] else 2

if __name__=="__main__":
    raise SystemExit(main())
