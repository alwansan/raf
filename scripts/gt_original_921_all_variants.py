#!/usr/bin/env python3
"""GT: recover all compiled permutations of original SHA-authenticated 921-slot Shader48.

Original DXBC, recovered HLSL and source identities stay runner-private. This
does not claim authored ShaderLab parity, Unity import, Android, or pixels.
"""
from __future__ import annotations
import argparse
import base64
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

def stage_private(pairs,orphans,passes,distinct,private:Path,*,translator,source_parsed=None):
    if (len(pairs)!=PAIRED_COUNT or len(orphans)!=ORPHAN_VERTEX_COUNT or
        len(passes)!=PASS_COUNT or len(distinct)!=DISTINCT_DXBC_COUNT):
        raise ValueError("non_original_921_stage_inventory")
    if type(source_parsed) is not dict or type(source_parsed.get('m_SubShaders')) is not list:
        raise ValueError('original_full_Shader_ParsedForm_missing')
    original_header=json.dumps(source_parsed,sort_keys=True)
    if not 0<len(original_header.encode('utf-8'))<=16*1024*1024:
        raise ValueError('original_Shader_ParsedForm_private_limit_exceeded')
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
        "original_shader_ParsedForm_full_private":source_parsed,
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
        "source_original_Shader_ParsedForm_pass_states_keyword_property_tables_preserved_privately":True,
        "original_keyword_name_count":len(source_parsed.get('m_KeywordNames',[])) if type(source_parsed.get('m_KeywordNames')) is list else None,
        "original_property_count":len(source_parsed.get('m_PropInfo',{}).get('m_Props',[])) if type(source_parsed.get('m_PropInfo')) is dict and type(source_parsed.get('m_PropInfo',{}).get('m_Props')) is list else None,
        "original_authored_ShaderLab_or_Sampler_CB0_render_parity_verified":False,
        "original_project_Shader_GUID_replaced":False,
        "original_game_assets_or_meta_modified":False,
        "Unity_Editor_Android_or_device_pixels_verified":False,
        "original_source_IDs_GUIDs_shader_names_or_program_bytes_published":False,
    }


def source_keyword_profile(pairs,orphans,parsed):
    """Sanitized exact source index census, not guessed Unity #pragma scope.

    Recover unmodified keyword indices from original paired and unmatched
    stage metadata. Keep exact values and 27 source names ONLY in private
    ParsedForm/variant packet. Public receipt contains counts, not indices.
    """
    if (type(parsed) is not dict or type(parsed.get("m_KeywordNames")) is not list or
        type(parsed.get("m_PropInfo")) is not dict or
        type(parsed["m_PropInfo"].get("m_Props")) is not list):
        raise ValueError("missing_source_original_shader_keyword_or_properties")
    names=parsed["m_KeywordNames"]
    props=parsed["m_PropInfo"]["m_Props"]
    if len(names)>256 or len(props)>256 or any(type(n) is not str for n in names):
        raise ValueError("unsupported_original_shader_keyword_property_scope")
    fields=("m_KeywordIndices","m_GlobalKeywordIndices","m_LocalKeywordIndices")
    used={key:set() for key in fields}
    tiers=set()
    buckets=set()
    rows=[pair[stage] for pair in pairs for stage in ("vs","fs")]
    rows.extend(orphan["variant"] for orphan in orphans)
    for row in rows:
        info=row["original_variant_metadata"]
        buckets.add(row["player_bucket"])
        tier=info.get("m_ShaderHardwareTier")
        if tier is not None:
            if type(tier) is not int or tier<0:raise ValueError("bad_original_hardware_tier")
            tiers.add(tier)
        for field in fields:
            if field not in info:
                continue
            values=info[field]
            if type(values) is not list or any(type(k) is not int or k<0 or k>65535 for k in values):
                raise ValueError("unsupported_original_keyword_index_data")
            used[field].update(values)
    all_indices=set().union(*used.values())
    flags=parsed.get("m_KeywordFlags")
    if flags is not None and type(flags) is not list:
        raise ValueError("malformed_original_keyword_flags")
    return {
        "original_keyword_names":len(names),
        "original_property_definitions":len(props),
        "original_keyword_flags":len(flags) if flags is not None else None,
        "all_source_variant_metadata_stages_censused":len(rows),
        "source_original_unique_used_keyword_indices":len(all_indices),
        "original_legacy_keyword_indices_used":len(used["m_KeywordIndices"]),
        "original_global_keyword_indices_used":len(used["m_GlobalKeywordIndices"]),
        "original_local_keyword_indices_used":len(used["m_LocalKeywordIndices"]),
        "original_distinct_hardware_tiers_in_variants":len(tiers),
        "original_distinct_player_buckets_in_variants":len(buckets),
        "original_keyword_indices_within_name_table":all(k<len(names) for k in all_indices),
        "original_global_local_pragma_flags_and_compilation_selection_proven":False,
        "original_sampler_register_CB0_bindings_proven":False,
    }

def stage_parameter_records(pairs, orphans, passes, table, private, program_dirs):
    """Preserve the per-stage override blobs separately from shared stage bytecode."""
    from scripts.a12_shader_parameter_decode import parse_parameter_blob
    from scripts.b25_foam_cb_namebridge import original_name_registry
    from scripts.gt_original_921_cb_hlsl import verify_named_constant_buffers
    from scripts.gt_original_921_cb_layout import bind_constant_buffers, constant_buffer_lanes
    from scripts.gt_original_921_resource_rebind import verify_rebound_resources
    from scripts.w1_rebind_depth_resources import RESOURCE
    import re

    by_pass = {(row["subshader"], row["pass"]): row for row in passes}
    rows = [(pair, stage, pair[field]) for pair in pairs
            for stage, field in ((1, "vs"), (0, "fs"))]
    rows.extend((orphan, orphan["stage"], orphan["variant"]) for orphan in orphans)
    records, decoded, layouts = [], {}, {}
    texture_counts = Counter()
    cb_counts = Counter()
    for location, stage, row in rows:
        shader_pass = by_pass[location["subshader"], location["pass"]]
        program = shader_pass["original_vertex_program" if stage == 1 else "original_fragment_program"]
        index = program["m_ParameterBlobIndices"][row["player_bucket"]][row["bucket_ordinal"]]
        if type(index) is not int or not 0 <= index < len(table):
            raise ValueError("invalid_original_parameter_blob_index")
        raw = table[index][1]
        if index not in decoded:
            layouts[index] = {}
            decoded[index] = parse_parameter_blob(raw, private_layout=layouts[index])
        common = program["m_CommonParameters"]
        names = original_name_registry(shader_pass["original_name_indices"])
        textures = {item["m_Index"]: (names[item["m_NameIndex"]], item["m_SamplerIndex"])
                    for item in common["m_TextureParams"]}
        textures.update({item["index"]: (item["name"], item["extra_value"])
                         for item in layouts[index]["resources"] if item["kind"] == 0})
        program_dir = private / program_dirs[row["program_ref"]]
        source = (program_dir / "private.hlsl").read_text()
        bindings = []
        for resource in RESOURCE.finditer(source):
            variable, kind = resource[2], resource[3]
            slot_match = re.fullmatch(kind + r"(\d+)", variable)
            if not slot_match:
                raise ValueError("original_texture_or_sampler_slot_missing")
            slot = int(slot_match[1])
            candidates = ([textures[slot][0]] if slot in textures else []) if kind == "t" else [
                name for name, sampler in textures.values() if sampler == slot]
            if len(candidates) != 1:
                raise ValueError("original_texture_or_sampler_binding_ambiguous")
            bindings.append({"kind": kind, "slot": slot, "source_texture_name": candidates[0]})
            texture_counts[kind] += 1
        bound_stage = private / f"bound-stage-{len(records):03d}"
        verify_rebound_resources(program_dir, stage, bindings, bound_stage)
        buffers = bind_constant_buffers(source, common, names, layouts[index])
        for buffer in buffers:
            lanes = constant_buffer_lanes(buffer)
            buffer["original_named_lanes"] = lanes
            cb_counts["named_lanes"] += sum(lane is not None for lane in lanes)
        verify_named_constant_buffers(bound_stage, stage, buffers)
        cb_counts["mapped"] += len(buffers)
        cb_counts["variant"] += sum(buffer["binding_from_variant"] for buffer in buffers)
        cb_counts["shared_layout"] += sum(buffer["shared_layout_present"] for buffer in buffers)
        cb_counts["members"] += sum(len(buffer["members"]) for buffer in buffers)
        cb_counts["structs"] += sum(len(buffer["structs"]) for buffer in buffers)
        records.append({
            "subshader": location["subshader"], "pass": location["pass"],
            "stage": stage, "player_bucket": row["player_bucket"], "ordinal": row["bucket_ordinal"],
            "original_parameter_blob_index": index,
            "source_texture_sampler_bindings": bindings,
            "source_constant_buffer_layouts": buffers,
        })
    packet = {
        "stage_records": records,
        "decoded_original_named_layouts": layouts,
        "blobs_base64": {index: base64.b64encode(table[index][1]).decode("ascii") for index in decoded},
    }
    (private / "original-private-parameter-records.json").write_text(
        json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    return {
        "original_variant_stages_with_parameter_records": len(records),
        "distinct_original_parameter_blobs": len(decoded),
        "resource_rebound_stages_verified_spirv_identical_excluding_debug": len(records),
        "named_constant_buffer_candidate_stages_vulkan11_valid": len(records),
        "translated_constant_buffer_declarations_mapped": cb_counts["mapped"],
        "constant_buffer_bindings_from_variant": cb_counts["variant"],
        "constant_buffer_layouts_with_shared_members_table": cb_counts["shared_layout"],
        "constant_buffer_named_32bit_lanes": cb_counts["named_lanes"],
        "constant_buffer_named_member_occurrences": cb_counts["members"],
        "constant_buffer_named_struct_occurrences": cb_counts["structs"],
        "translated_texture_declarations_mapped_to_source_name": texture_counts["t"],
        "translated_sampler_declarations_mapped_to_source_texture": texture_counts["s"],
        "named_original_numeric_members_in_distinct_parameter_blobs": sum(
            item["numeric_parameter_count"] + item["struct_numeric_member_count"] for item in decoded.values()),
        "named_original_resource_entries_in_distinct_parameter_blobs": sum(
            item["resource_parameter_count"] for item in decoded.values()),
        "original_variant_stages_with_textures": sum(
            decoded[row["original_parameter_blob_index"]]["texture_count"] > 0 for row in records),
        "original_variant_stages_with_cb_bindings": sum(
            decoded[row["original_parameter_blob_index"]]["constant_buffer_binding_count"] > 0
            for row in records),
    }


def run(original:Path,manifest:Path,private:Path,out:Path,*,translator=None):
    from scripts import t3_original_renderer_shader_impact as scenes
    from scripts import t3_original_top_shader_dxbc_feasibility as top
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms,records,translate
    from scripts.w1_recover_depth_passes import linked_program,stage_variants,variant_key
    if translator is None:translator=translate
    for binary in ("vkd3d-compiler","spirv-val","spirv-opt","spirv-cross","glslangValidator"):
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
    safe=stage_private(pairs,orphans,passes,unique,private,translator=translator,source_parsed=tree['m_ParsedForm'])
    from scripts.gt_original_921_keyword_routes import compile_routed_stages, keyword_routes, shaderlab_layout
    route_packet, route_summary = keyword_routes(tree["m_ParsedForm"], pairs, orphans, passes)
    # Resolve the tuple of stage and bytecode digest to the packet's program directories.
    program_dirs = {ident: f"program-{index:03d}" for index, ident in enumerate(unique)}
    for row in route_packet:
        for route in row["routes"]:
            for stage in ("vs", "fs"):
                route[stage] = program_dirs[route[stage]]
    (private / "original-private-keyword-routes.json").write_text(
        json.dumps(route_packet, indent=2) + "\n", encoding="utf-8")
    layout, safe["source_shaderlab_layout"] = shaderlab_layout(tree["m_ParsedForm"], passes)
    (private / "original-private-layout.txt").write_text(layout, encoding="utf-8")
    route_summary["validated_exact_routed_stage_compilations"] = compile_routed_stages(route_packet, private)
    safe["source_keyword_route_coverage"] = route_summary
    safe['source_original_keyword_coverage']=source_keyword_profile(pairs,orphans,tree['m_ParsedForm'])
    safe["source_variant_parameter_records"] = stage_parameter_records(
        pairs, orphans, passes, tables[0], private, program_dirs)
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
