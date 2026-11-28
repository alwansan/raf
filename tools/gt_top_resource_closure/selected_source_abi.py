"""Selected original stage ABI to exact same-export mesh and material.
Private original data remains runner-local. No Unity or draw acceptance.
"""
import argparse
import json
from pathlib import Path
import tempfile

from tools.gt_top_resource_closure import recheck, probe, selected_material_reference
from tools.gt_top_original_renderer import probe as original
from scripts import gt_material_route_values as values
from scripts import gt_particle108_local_texture_document as native
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts.gt_original_921_all_variants import authenticated_shader_reader, enumerate_all, stage_parameter_records
from scripts.gt_original_921_keyword_routes import keyword_routes
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.gt_resource_register_contract import registered_resources
from scripts.t3_original_921_dxbc_semantic_join import read_original_dxbc_signatures

STATUS = "OBSERVED_EXACT_SELECTED_SOURCE_ABI_MATERIAL_MESH_JOIN"

class ABIFailure(ValueError):
    """Only fixed source-owned diagnostic codes raised via require()."""

def require(ok, code):
    if not ok:
        raise ABIFailure(code)

def verify_texture_plan(before, after, planned):
    """Prestage records non-null source targets only; nulls stay explicit.
    Require identical source/export property sets, all non-null plans and
    no extra/null target records. The caller still checks exact PPtr and UV
    for every slot (including nulls) via recheck.exact_slot().
    """
    require(type(planned) is dict, "selected_texture_plan_schema")
    require(set(before)==set(after), "selected_texenv_names_drift")
    nonnull={name for name, (ptr, _) in before.items() if ptr[1]}
    require(set(planned)==nonnull, "selected_nonnull_texture_plan_drift")
    require(all(type(v) is dict and v.get("stream_ready") is True
                for v in planned.values()), "selected_texture_plan_not_prepared")
    return {"source_slots":len(before),"export_slots":len(after),
            "nonnull_planned":len(nonnull),"null_source_slots":len(before)-len(nonnull)}

def channel_dimension(raw):
    # Modern Unity ChannelInfo stores dimension in the low nibble.
    # UnityPy MeshHandler.get_streams/read_vertex_data use this same mask.
    # Do not rewrite the serialized channel byte or infer its upper flags.
    require(type(raw) is int and 0<=raw<=255, "invalid_mesh_channel_dimension_byte")
    dim=raw & 15
    require(dim<=4, "unsupported_mesh_channel_dimension")
    return dim

def vertex_layout_observation(channels, vertex_count, payload_bytes):
    from scripts.gt_mesh_vertex_payload import WIDTHS
    require(type(vertex_count) is int and vertex_count>0 and
            type(payload_bytes) is int and payload_bytes>0 and payload_bytes%vertex_count==0,
            "invalid_selected_mesh_vertex_stride")
    stride=payload_bytes//vertex_count
    ranges=[]
    flagged=inactive_flagged=0
    for row in channels:
        raw=row["dimension"]
        dim=channel_dimension(raw)
        flagged+=int(raw!=dim)
        if not dim:
            inactive_flagged+=int(raw!=0)
            continue
        stream,offset,fmt=(row[k] for k in ("stream","offset","format"))
        require(type(stream) is int and stream==0 and type(offset) is int and
                offset>=0 and type(fmt) is int and fmt in WIDTHS,
                "selected_mesh_single_stream_layout_required")
        ranges.append((offset,offset+dim*WIDTHS[fmt]))
    end=0
    for lo,hi in sorted(ranges):
        require(lo>=end and hi<=stride,"selected_mesh_channel_overlap_or_extent")
        end=hi
    require(bool(ranges) and end==stride and sum(hi-lo for lo,hi in ranges)==stride,
            "selected_mesh_channel_stride_not_exact")
    return dict(vertex_count=vertex_count,vertex_payload_bytes=payload_bytes,
                packed_dimension_flagged_channels=flagged,
                flagged_inactive_channels=inactive_flagged,
                active_channels=len(ranges),single_stream_stride_bytes=stride,
                nonoverlap_full_stride=True,serialized_channel_bytes_changed=False)

def material_member_census(rows, mat, texenvs, parsed):
    """Exact names only; name presence is not a Unity value upload."""
    saved=values.normalize(mat)
    props=parsed["m_PropInfo"]["m_Props"]
    declared={p["m_Name"] for p in props}
    require(len(declared)==len(props),"duplicate_source_shader_properties")
    numeric=set().union(*(set(v) for v in saved.values()))
    counters=dict(named_numeric_members=0,saved_numeric_name_matches=0,
                  saved_texenv_ST_name_matches=0,declared_property_not_saved=0,
                  other_runtime_or_global_name_candidates=0,
                  outside_material_texture_declared_properties=0,
                  outside_material_texture_undeclared_names=0)
    for row in rows:
        for b in row["source_constant_buffer_layouts"]:
            for m in b["members"]:
                name=m["name"]
                counters["named_numeric_members"]+=1
                if name in numeric:
                    counters["saved_numeric_name_matches"]+=1
                elif name.endswith("_ST") and name[:-3] in texenvs:
                    counters["saved_texenv_ST_name_matches"]+=1
                elif name in declared:
                    counters["declared_property_not_saved"]+=1
                else:
                    counters["other_runtime_or_global_name_candidates"]+=1
        for resource in row["source_texture_sampler_bindings"]:
            name=resource["source_texture_name"]
            if resource["kind"]=="t" and name not in texenvs:
                counters["outside_material_texture_declared_properties" if name in declared else
                         "outside_material_texture_undeclared_names"]+=1
    return counters

def combined_candidate(private, rows, pair, dirs):
    """Prepare one explicit pass body; compile both entries privately.
    No full shader install, runtime keyword selection, or Unity upload claim.
    """
    import re
    from scripts.gt_original_921_shaderlab import (paired_uniform_layouts, combine_stages,
        unity_resource_bindings, unity_varying_semantics, verify_entrypoints)
    from scripts.gt_original_921_cb_hlsl import rebind_constant_buffers
    from scripts.gt_original_921_semantics import restore_vertex_inputs, pin_varying_locations
    layouts=paired_uniform_layouts(rows)
    bodies=[]
    for i,role in enumerate(("vs","fs")):
        code=rebind_constant_buffers((private/f"bound-stage-{i:03d}"/"resource-bound.hlsl").read_text(),layouts[i])
        if i==0:
            code,_=restore_vertex_inputs(code,(private/dirs[pair["vs"]["program_ref"]]/"source.dxbc").read_bytes())
        code=unity_varying_semantics(pin_varying_locations(code,1-i))
        code,n=re.subn(r"\bmain(?=\s*\()",f"gt_{role}_main",code)
        require(n==1,"combined_candidate_entry_identity")
        bodies.append(unity_resource_bindings(code,role))
    body=combine_stages(*bodies)
    wrapper="HLSLPROGRAM\n#pragma target 5.0\n#pragma vertex gt_vs_main\n#pragma fragment gt_fs_main\n"+body+"\nENDHLSL"
    # Historical exact two-entry verifier compiles this merged, name-bound
    # candidate with glslang then validates both Vulkan 1.1 modules.
    verify_entrypoints(wrapper,private,routes=[[[]]])
    (private/"combined-explicit-wrapper.txt").write_text(wrapper)
    return {"combined_entrypoints_compiled_and_validated":2,
            "explicit_single_route_only":True,"Unity_compiler_verified":False,
            "merged_binding_offset_parity_verified":False,
            "runtime_uniform_upload_verified":False}

def vertex_channel_observation(signature, channels):
    """Report channel availability, not runtime binding or default fill."""
    scalar = {"POSITION":0, "NORMAL":1, "TANGENT":2, "COLOR":3, "BLENDWEIGHT":12, "BLENDINDICES":13}
    out = dict(user_inputs=0, present_channels=0, absent_channels=0,
               unsupported_semantics=0, sufficient_declared_lanes=0, fewer_declared_lanes=0)
    for row in signature:
        if row["system_value"]:
            continue
        out["user_inputs"] += 1
        name, index = row["semantic"], row["index"]
        channel = (4+index if name=="TEXCOORD" and 0<=index<8 else scalar.get(name) if index==0 else None)
        if channel is None:
            out["unsupported_semantics"] += 1
            continue
        dim = channel_dimension(channels[channel]["dimension"]) if channel<len(channels) else 0
        if not dim:
            out["absent_channels"] += 1
            continue
        out["present_channels"] += 1
        out["fewer_declared_lanes" if row["mask"] & ~((1<<dim)-1) else "sufficient_declared_lanes"] += 1
    return out

def resource_observation(stage_rows, hlsl_sources, texenvs, typed, selected):
    result = dict(texture_declarations=0, sampler_declarations=0,
                  texture_names_in_material=0, texture_names_outside_material=0,
                  texture_names_in_null_slots=0, texture_names_in_exact_typed_slots=0,
                  selected_array_texture_declarations=0, selected_array_sampler_declarations=0,
                  selected_array_type_matches=0, selected_array_type_mismatches=0)
    require(len(stage_rows)==len(hlsl_sources), "stage_source_count")
    for row, text in zip(stage_rows,hlsl_sources,strict=True):
        regs = {}
        for m in registered_resources(text):
            key=(m[3],m[2])
            require(key not in regs,"duplicate_stage_resource")
            regs[key]=m[1]
        used=set()
        for b in row["source_texture_sampler_bindings"]:
            kind,slot,name=b["kind"],b["slot"],b["source_texture_name"]
            require(kind in ("t","s") and type(slot) is int and slot>=0,"bad_resource_binding")
            key=(kind,kind+str(slot))
            require(key in regs and key not in used,"missing_or_duplicate_stage_resource")
            used.add(key)
            if kind=="s":
                result["sampler_declarations"]+=1
                if name==selected:
                    result["selected_array_sampler_declarations"]+=1
                continue
            result["texture_declarations"]+=1
            if name not in texenvs:
                result["texture_names_outside_material"]+=1
            else:
                result["texture_names_in_material"]+=1
                result["texture_names_in_null_slots" if typed.get(name) is None else "texture_names_in_exact_typed_slots"]+=1
            if name==selected:
                result["selected_array_texture_declarations"]+=1
                good=regs[key].split("<",1)[0].strip()=="Texture2DArray" and typed.get(name)==187
                result["selected_array_type_matches" if good else "selected_array_type_mismatches"]+=1
        require(used==set(regs),"unjoined_translated_resources")
    result["selected_array_used_by_this_explicit_route"]=result["selected_array_texture_declarations"]>0
    return result

def run(a,out):
    plan=json.loads(a.plan.read_text())
    source=recheck.Source(a)
    mat,mk,xk,trace=recheck.join(a,plan,source)
    out["same_export_exact_graph"]=True
    out["phase"]="mesh_and_material"
    index=probe.file_index(a.project,{mk[0],xk[0]})
    mesh=probe.mesh_check(source,tuple(plan["mesh"]),index[xk[0]][0],xk[1])
    out["mesh_fields_matched"]=mesh["matched_geometry_fields"]
    out["mesh_fields_total"]=mesh["geometry_fields"]
    require(mesh["status"]=="MATCH","selected_mesh_payload_drift")
    body=probe.document(index[mk[0]][0],mk[1],21)
    actual=native.strict_mapping(body)["Material"]
    out["material_values"]=values.compare(mat,actual)
    before=normalize_texenvs(mat["m_SavedProperties"]["m_TexEnvs"])
    after=normalize_texenvs(actual["m_SavedProperties"]["m_TexEnvs"],exported=True)
    out["phase"]="texture_plan_schema"
    out["texture_plan"]=verify_texture_plan(before,after,plan["texture_targets"])
    out["phase"]="exact_texenv_pointer_UV_join"
    typed={}
    selected=[]
    for prop in before:
        edge=recheck.exact_slot(before[prop],after[prop],plan["material"][0],mk[0],source,trace,plan["texture_targets"].get(prop))
        typed[prop]=None if edge is None else edge[3]
        if edge is not None and edge[3]==187:
            selected.append((prop,edge))
    require(len(selected)==1,"selected_array_slot_not_unique")
    prop,(_,exp,kind,cls)=selected[0]
    out["exact_texenv_slots"]=len(typed)
    out["phase"]="source_preserving_native_reference_candidate"
    require(cls==187 and kind==3 and exp[1]==18700000,"selected_reference_anchor")
    repaired=selected_material_reference.repair_native_reference(body,prop,exp[0],exp[1],kind)
    rejected=0
    for args in ((prop,"0"*32,exp[1],kind),(prop,exp[0],exp[1]+1,kind),(prop,exp[0],exp[1],2)):
        try:
            selected_material_reference.repair_native_reference(body,*args)
        except ValueError:
            rejected+=1
    require(rejected==3,"wrong_reference_control_not_rejected")
    out["reference_repair_byte_difference"]=sum(x!=y for x,y in zip(body.encode(),repaired.encode(),strict=True))
    out["reference_negative_controls_rejected"]=rejected
    out["original_shader_pointer_unchanged"]=True
    out["phase"]="explicit_original_stage_pair"
    tree=authenticated_shader_reader(a.original)(tuple(plan["shader"]))
    tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    require(len(tables)==1,"original_d3d11_table")
    table=tables[0]
    pairs,orphans,passes,distinct=enumerate_all(tree["m_ParsedForm"],table,
        variants=stage_variants,permutation=variant_key,linker=linked_program)
    routes,_=keyword_routes(tree["m_ParsedForm"],pairs,orphans,passes)
    route=original.select_route(routes,original.keywords(mat))
    names=tree["m_ParsedForm"]["m_KeywordNames"]
    enabled=set(route["enabled"])
    matched=[p for p in pairs if p["subshader"]==0 and p["pass"]==0
             and p["vs"]["program_ref"]==route["vs"] and p["fs"]["program_ref"]==route["fs"]
             and {names[i] for i in p["vs"]["original_variant_metadata"].get("m_KeywordIndices",[])}==enabled
             and {names[i] for i in p["fs"]["original_variant_metadata"].get("m_KeywordIndices",[])}==enabled]
    require(len(matched)==1,"exact_route_variant_identity")
    pair=matched[0]
    out["explicit_source_route_keyword_count"]=len(enabled)
    out["phase"]="private_stage_ABI"
    with tempfile.TemporaryDirectory(prefix="gt-selected-abi-private-",dir=a.out.parent) as td:
        private=Path(td)
        dirs={}
        sources=[]
        for stage,role in ((1,"vs"),(0,"fs")):
            ident=pair[role]["program_ref"]
            folder=private/role
            folder.mkdir(mode=0o700)
            require(ident[0]==stage,"source_stage_role")
            result=translate(distinct[ident]["source_code"],stage,folder)
            require(result["dxbc_sha256"]==ident[1] and all(result[k] is True for k in
                    ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")),"original_stage_translation")
            dirs[ident]=role
            sources.append((folder/"private.hlsl").read_text())
        out["original_stage_byte_identities_verified"]=len(dirs)
        out["phase"]="source_parameter_constant_buffer_sampler_varying_ABI"
        out["abi"]=stage_parameter_records([pair],[],passes,table,private,dirs)
        rows=json.loads((private/"original-private-parameter-records.json").read_text())["stage_records"]
        require([r["stage"] for r in rows]==[1,0],"source_ABI_stage_order")
        out["phase"]="material_resource_and_mesh_channel_join"
        out["resource_join"]=resource_observation(rows,sources,before,typed,prop)
        signature=read_original_dxbc_signatures((private/"vs/source.dxbc").read_bytes())["input"]
        channels=source.obj(tuple(plan["mesh"]),"Mesh").read_typetree(check_read=False)["m_VertexData"]["m_Channels"]
        out["phase"]="packed_mesh_channel_layout"
        out["mesh_channel_layout"]=vertex_layout_observation(channels,mesh["source_vertex_count"],mesh["source_vertex_bytes"])
        out["mesh_channel_availability"]=vertex_channel_observation(signature,channels)
        out["phase"]="material_member_source_name_census"
        out["material_member_census"]=material_member_census(rows,mat,before,tree["m_ParsedForm"])
        out["phase"]="combined_explicit_route_candidate"
        out["combined_candidate"]=combined_candidate(private,rows,pair,dirs)
        if a.audit_merged:
            from tools.gt_top_resource_closure import selected_merged_abi as merged
            out["phase"]="merged_source_ABI_context"
            out["merged_source_ABI_context"]=merged.audit(private,(private/"combined-explicit-wrapper.txt").read_text(),
                rows,sources,mat,before,tree["m_ParsedForm"])
            require(out["merged_source_ABI_context"]["status"]=="OBSERVED_MERGED_SOURCE_ABI_CONTEXT",
                    "merged_reflection_inconclusive")
        if a.draw_private is not None:
            from tools.gt_top_resource_closure import selected_original_draw as draw
            out["phase"]="guarded_original_draw_stage"
            out["draw_stage"]=draw.prepare(a,out,source,plan,mat,mk,xk,trace,body,mesh,prop,selected[0][1],
                tree["m_ParsedForm"],passes,(private/"combined-explicit-wrapper.txt").read_text())
    out["status"]=STATUS
    out["phase"]="complete_source_ABI_observation"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("original","manifest","project","w1","b02","renderer-trace","plan","out"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--audit-merged",action="store_true")
    p.add_argument("--draw-private",type=Path)
    p.add_argument("--unity-project",type=Path)
    p.add_argument("--run-id")
    a=p.parse_args()
    if any(x is not None for x in (a.draw_private,a.unity_project,a.run_id)) and not all(x is not None for x in (a.draw_private,a.unity_project,a.run_id)):
        p.error("draw stage arguments must be supplied together")
    out=dict(status="INCONCLUSIVE",phase="same_export_graph",original_shader_draw_verified=False,
             runtime_keyword_selection_verified=False,Unity_execution=False,Android_device=False,
             production=False,XAPK=False,white_mesh_repair_verified=False,private_payload_published=False)
    try:
        run(a,out)
    except Exception as exc:
        out["failure_type"]=type(exc).__name__
        # Only fixed own codes, or an explicit whitelist of existing ABI
        # guard codes. Never relay arbitrary exception text or private names.
        fixed={
            "original_921_vertex_fragment_varying_mismatch",
            "original_921_mesh_input_candidate_compile_failed",
            "original_921_mesh_input_candidate_spirv_invalid",
            "original_921_vulkan_varying_type_or_location_mismatch",
            "original_921_varying_candidate_compile_failed",
            "original_921_varying_candidate_spirv_invalid",
            "original_resource_rebound_changed_spirv",
            "original_resource_rebound_compile_failed",
            "original_resource_rebound_spirv_invalid",
            "original_texture_or_sampler_binding_ambiguous",
            "named_constant_buffer_candidate_compile_failed",
            "named_constant_buffer_candidate_spirv_invalid",
            "named_constant_buffer_reflection_failed",
            "invalid_original_parameter_blob_index",
            "selected_material_reference_diagnostic_anchor",
            "original_921_shaderlab_entrypoint_compile_failed",
            "original_921_shaderlab_entrypoint_spirv_invalid",
            "original_921_shaderlab_entrypoint_missing",
            "original_921_incompatible_shared_uniform_block",
            "original_921_conflicting_shared_uniform_member",
            "original_921_shared_HLSL_declaration_drift",
            "original_921_uniform_in_multiple_buffers",
            "original_921_uniform_incompatible_type",
        }
        from tools.gt_top_resource_closure.selected_original_draw import StageError
        if type(exc) in (ABIFailure,StageError) or (type(exc) is ValueError and str(exc) in fixed):
            out["failure_reason"]=str(exc)
    with a.out.open("x") as dest:
        json.dump(out,dest,sort_keys=True,indent=2)
        dest.write("\n")
    print("GT_SELECTED_SOURCE_ABI "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
