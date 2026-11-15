"""Recover source-authentic next unresolved 30-Material Shader48 D3D11 stages.

Select exactly one remaining shader from 82 SHA-pinned original ZIP2 owners
using the post-nine exact 30-Material name digest and source Shader48 identity.
Validate original 4 Pass / 31 VS-FS keyword routes / 8 VS orphans / 55 distinct
DXBC programs. Translate original DXBC privately to SPIR-V and recovered HLSL,
then validate Vulkan 1.1 stage roundtrips. No source code, names, hashes,
identifiers, or compiled shader bytes enter public reports. Does NOT yet
install shader in Unity or prove game pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil

from scripts.gt_rank_all82_original_shader_names_after_nine import gather
from scripts.gt_original_921_all_variants import enumerate_all, stage_parameter_records
from scripts.gt_original_921_keyword_routes import keyword_routes, compile_routed_stages, shaderlab_layout
from scripts.gt_original_921_shaderlab import compose, verify_entrypoints
from scripts.gt_stage_serialized_owners import read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.t3_original_top_shader_dxbc_feasibility import summarize
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate

STATUS="GT_SHA_ORIGINAL_REMAINING_30_MATERIAL_SHADER48_D3D11_PRIVATE_STAGES_TRANSLATED"
EXPECTED_TOPOLOGY=(4,31,8,55)


def select_exact_30_material_name(source_hashes, material_name_counts):
    matches=[digest for digest,amount in material_name_counts.items() if amount==30]
    if len(matches)!=1:
        raise ValueError("missing_or_ambiguous_30_material_original_shader_name_digest")
    matched=[key for key,digest in source_hashes.items() if digest==matches[0]]
    if len(matched)!=1:
        raise ValueError("not_one_authentic_original_30_material_Shader48_object")
    return matched[0]


def run(original,manifest,quality,private):
    import UnityPy
    for binary in ("vkd3d-compiler","spirv-val","spirv-cross","glslangValidator"):
        if shutil.which(binary) is None:
            raise ValueError("missing_original_D3D11_to_Vulkan_translation_tool")
    q=json.loads(quality.read_text("utf-8"))
    if (q.get("status")!="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
            or q.get("counts",{}).get("material_docs_using_dummy_Shader")!=333
            or q.get("counts",{}).get("material_documents")!=1536):
        raise ValueError("unverified_post_nine_source_original_Material_shader_population")
    names,owners=gather(original,manifest)
    owner,pid=select_exact_30_material_name(names,q["dummy_shader_material_counts_by_name_digest"])
    kind,size,digest=read_expected(manifest)[owner]
    source=original/owner
    if source.is_symlink():
        raise ValueError("unsafe_original_Shader48_owner")
    verify(source,size,digest)
    env=UnityPy.load(str(source))
    objs=[obj for obj in env.objects if obj.path_id==pid and str(obj.type.name)=="Shader"]
    if len(objs)!=1:
        raise ValueError("source_authenticated_30_material_Shader48_missing")
    tree=objs[0].read_typetree()
    tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    if len(tables)!=1:
        raise ValueError("original_D3D11_program_table_for_30_material_shader_not_unique")
    parsed=tree.get("m_ParsedForm")
    census=summarize(parsed,tables[0])
    baseline=(census["original_source_Shader48_pass_count"],
              census["matched_vertex_fragment_permutation_pairs"],
              census["unmatched_vertex_permutations"],
              census["distinct_original_linked_D3D11_programs"])
    if (baseline!=EXPECTED_TOPOLOGY
            or census["unmatched_fragment_permutations"]!=0):
        raise ValueError("authenticated_original_30_Material_shader_D3D11_pass_topology_drift")
    paired,orphans,passes,distinct=enumerate_all(
        parsed,tables[0],variants=stage_variants,permutation=variant_key,
        linker=linked_program,topology=EXPECTED_TOPOLOGY)
    if private.exists() or private.is_symlink() or not private.parent.is_dir():
        raise ValueError("unsafe_private_D3D11_shader_recovery_location")
    private.mkdir(mode=0o700)
    counts=Counter()
    folders={}
    for index,(ident,record) in enumerate(distinct.items()):
        folder=private/("program-%03d"%index)
        folder.mkdir(mode=0o700)
        folders[ident]=folder.name
        translated=translate(record["source_code"],record["stage"],folder)
        counts["original_programs_translated"]+=1
        for field in ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid"):
            counts[field]+=int(translated.get(field) is True)
    report={
        "schema_version":1,
        "status":STATUS if counts["roundtrip_vulkan11_valid"]==55 else "PARTIAL_ORIGINAL_D3D11_STAGE_TRANSLATION",
        "postnine_dummy_materials_linked_to_this_original_shader":30,
        "original_source_Shader48_object_unique_and_82_owner_SHA_verified":True,
        "original_Shader48_SubShader_count":census["original_source_Shader48_SubShader_count"],
        "original_shader_Pass_count":census["original_source_Shader48_pass_count"],
        "original_exact_vertex_fragment_keyword_permutation_pairs":len(paired),
        "original_orphan_vertex_stage_variants":len(orphans),
        "original_unique_D3D11_shader_program_stages":len(distinct),
        "original_unique_D3D11_program_stages_attempted":counts["original_programs_translated"],
        "original_program_stages_Vulkan11_spirv_val_valid":counts["vulkan11_valid"],
        "original_program_stages_recovered_HLSL":counts["hlsl_recovered"],
        "original_program_stages_roundtrip_Vulkan11_valid":counts["roundtrip_vulkan11_valid"],
        "original_source_82_owners_authenticated":82,
        "original_Source_names_PrivateIDs_or_shader_program_bytes_published":False,
        "original_ShaderLab_android_Unity_or_device_render_proven":False,
        "APK_OBB_XAPK_created":False,
    }
    if report["status"]!=STATUS:
        return report
    packet,routing=keyword_routes(parsed,paired,orphans,passes)
    for row in packet:
        for route in row["routes"]:
            for stage in ("vs","fs"):
                route[stage]=folders[route[stage]]
    try:
        report["private_original_exact_keyword_routed_programs_compiled"] = compile_routed_stages(packet,private)
        source_properties=parsed.get("m_PropInfo",{}).get("m_Props",[])
        if not isinstance(source_properties,list):
            raise ValueError("invalid_original_30_material_Shader_properties")
        layout,details=shaderlab_layout(parsed,passes,expected_property_count=len(source_properties))
        (private/"original-private-shaderlab-layout.txt").write_text(layout,encoding="utf-8")
        report["source_original_ShaderLab_4pass_property_layout_validated"]=True
        report["source_original_keyword_permutation_route_counts_per_pass"]=routing["source_exact_keyword_routes_by_pass"]
        report["source_original_property_count"]=len(source_properties)
        # Preserve all source/Shader48 metadata and GPU program identity
        # privately. Only source-free counters leave CI.
        def stage_row(row):
            return {k:(folders[v] if k=="program_ref" else v) for k,v in row.items()}
        manifest={
            "schema":1,
            "original_passes":passes,
            "original_shader_ParsedForm_full_private":parsed,
            "paired":[
                {"subshader":pair["subshader"],"pass":pair["pass"],
                 "vs":stage_row(pair["vs"]),"fs":stage_row(pair["fs"])}
                for pair in paired
            ],
            "unpaired":[
                {"subshader":orphan["subshader"],"pass":orphan["pass"],
                 "stage":orphan["stage"],"variant":stage_row(orphan["variant"])}
                for orphan in orphans
            ],
        }
        (private/"original-private-variant-manifest.json").write_text(
            json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        (private/"original-private-keyword-routes.json").write_text(
            json.dumps(packet,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        (private/"original-private-layout.txt").write_text(layout,encoding="utf-8")
        named=stage_parameter_records(paired,orphans,passes,tables[0],private,folders)
        report["source_variant_named_CB_sampler_stage_bindings_verified"]=True
        report["original_stage_parameter_records_checked"]=named["original_variant_stages_with_parameter_records"]
        report["original_vertex_fragment_varying_records_matched"]=named["original_vertex_fragment_varying_records_matched"]
        report["original_named_constant_buffer_offsets_verified"]=named["named_constant_buffer_reflected_offsets_verified"]
        report["original_texture_sampler_bindings_rebound"]=named["translated_texture_declarations_mapped_to_source_name"]+named["translated_sampler_declarations_mapped_to_source_texture"]
        shader=compose(private,engine_keywords=False)
        (private/"original-30-material-Shader48-private.shader").write_text(
            shader,encoding="utf-8")
        route_sets=[
            [[] if index==0 else [f"GT_ORIGINAL_921_P{pass_index}_V{index}"]
             for index in range(route_count)]
            for pass_index,route_count in enumerate(routing["source_exact_keyword_routes_by_pass"])
        ]
        verify_entrypoints(shader,private,routes=route_sets)
        report["private_original_30_material_ShaderLab_4pass_composed"]=True
        report["private_original_30_material_ShaderLab_62_vertex_fragment_entrypoints_validated"]=True
        report["original_ShaderLab_android_Unity_or_device_render_proven"]=False
    except Exception as exc:
        report["source_keyword_router_or_ShaderLab_layout_status"]="INCONCLUSIVE"
        report["source_keyword_router_or_ShaderLab_layout_error_type"]=type(exc).__name__
        report["original_ShaderLab_android_Unity_or_device_render_proven"]=False
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("original","manifest","quality","private","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or
            a.out.resolve().is_relative_to(a.original.resolve())
            or a.out.resolve().is_relative_to(a.private.resolve())
            or a.private.is_symlink()
            or a.private.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_original_D3D11_public_private_artifact_separation")
    try:
        result=run(a.original,a.manifest,a.quality,a.private)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "error_type":type(exc).__name__,
                "original_Source_names_PrivateIDs_or_shader_program_bytes_published":False,
                "APK_OBB_XAPK_created":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("GT_NEXT_30_ORIGINAL_SHADER48_D3D11_STAGE_RECOVERY "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
