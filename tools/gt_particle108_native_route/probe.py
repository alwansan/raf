"""Particle108: exact selected seven-mip native target -> five actual Materials
-> saved keyword route -> original DXBC texture/sampler operand pairs.

No Unity or repeated alpha GPU observation; not an assertion of game pixels.
All private names, source IDs, bytecode, paths and values remain local.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts import b05_verify_material_texenv_bindings as b05
from scripts import t3_original_renderer_shader_impact as impact
from scripts import t3_original_particle108_dxbc_feasibility as identity
from scripts import t3_original_particle108_spirv_translation as translation
from scripts import t3_particle108_private_keyword_routed_shaderlab as router
from scripts import gt_particle108_unity_bindings as bind
from scripts.gt_particle108_source_sampling_pairs import sample_operand_pairs
from scripts.gt_particle108_local_texture_document import strict_mapping
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_recover_depth_passes import stage_variants
from tools.gt_particle108_native_mips import probe as native

STATUS="OBSERVED_PARTICLE108_NATIVE_TARGET_SAVED_ROUTE_OPERAND_JOIN"
class Reject(ValueError):pass
def need(ok,code):
    if not ok:raise Reject(code)
def keywords(mat):
    if "m_ShaderKeywords" in mat:
        raw=mat["m_ShaderKeywords"]
        need(type(raw) is str,"saved_keyword_string_schema")
        valid=raw.split();invalid=[]
    else:
        valid=mat.get("m_ValidKeywords");invalid=mat.get("m_InvalidKeywords",[])
        need(type(valid) is list and type(invalid) is list,"saved_keyword_list_schema")
    all_words=valid+invalid
    need(all(type(x) is str and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",x) for x in all_words)
         and len(set(all_words))==len(all_words),"invalid_saved_keyword_population")
    return frozenset(valid),frozenset(invalid)
def slot_usage(samples,texture_names,sampler_names):
    out=Counter()
    for t,s,_ in samples:
        name=texture_names.get(t)
        need(name is not None and sampler_names.get(s)=="sampler"+name,
             "sample_operand_name_pair_mismatch")
        out[name]+=1
    return out
def choose_route(enabled,switches,route_map):
    key=tuple(int(n in enabled) for n in switches)
    need(key in route_map,"explicit_saved_route_missing")
    return route_map[key]
def classify_material(slots,owner,selected,source_kw,export_kw,switches,route_map,uses):
    src,invalid=source_kw;dst,dst_invalid=export_kw
    universe=set(switches)
    src_all=src|invalid;dst_all=dst|dst_invalid
    explicit=choose_route(src_all,switches,route_map)
    saved=choose_route(dst_all,switches,route_map)
    valid=choose_route(dst,switches,route_map)
    need(explicit in uses and saved in uses and valid in uses,"selected_route_program_not_found")
    target_labels={name for name,(ptr,uv) in slots.items()
                   if ptr[0]==0 and (owner,ptr[1])==selected}
    all_labels=set(slots)
    return dict(selected_native_slots=len(target_labels),
                saved_keyword_route_equal=explicit==saved,
                exported_valid_keyword_route_equal=explicit==valid,
                full_saved_keyword_set_equal=src_all==dst_all,
                source_outside_route_keywords=len(src_all-universe),
                export_outside_route_keywords=len(dst_all-universe),
                source_invalid_route_keywords=len(invalid&universe),
                export_invalid_route_keywords=len(dst_invalid&universe),
                selected_native_sample_instructions=sum(uses[explicit][n] for n in target_labels),
                selected_native_saved_export_sample_instructions=sum(uses[saved][n] for n in target_labels),
                selected_native_valid_export_sample_instructions=sum(uses[valid][n] for n in target_labels),
                saved_material_sample_instructions=sum(uses[explicit][n] for n in all_labels),
                outside_saved_material_sample_instructions=sum(v for n,v in uses[explicit].items() if n not in all_labels),
                selected_native_slots_sampled=sum(uses[explicit][n]>0 for n in target_labels),
                selected_native_slots_not_sampled=sum(uses[explicit][n]==0 for n in target_labels))
def traced(w1,cls,keys):
    out={}
    for row in w1["objects"]:
        if row.get("class_id")!=cls:continue
        key=b05._trace_source(row)
        if key not in keys:continue
        need(key not in out,"duplicate_selected_class_trace")
        out[key]=b05._trace_export(row)
    need(set(out)==set(keys) and len(set(out.values()))==len(keys),"selected_class_trace_coverage")
    return out
def exported_documents(project,ptrs):
    need(len(ptrs)==5,"selected_material_document_population")
    wanted={(p[0],p[1]) for p in ptrs.values()}
    guid_set={g for _,g in wanted}
    paths={}
    for path in (project/"Assets").rglob("*.meta"):
        need(not path.is_symlink() and path.stat().st_size<=4*1024*1024,"unsafe_export_meta")
        hits=b05.GUID.findall(path.read_text("utf-8-sig"))
        if len(hits)!=1 or hits[0].lower() not in guid_set:continue
        g=hits[0].lower()
        need(g not in paths,"duplicate_material_meta_guid")
        paths[g]=path.with_suffix("")
    need(set(paths)==guid_set,"selected_material_meta_missing")
    docs={}
    for g,path in paths.items():
        need(path.is_file() and not path.is_symlink() and path.stat().st_size<=256*1024*1024,"unsafe_material_document")
        text=path.read_text("utf-8-sig")
        headers=list(b05.ALL_HEADER.finditer(text))
        for i,h in enumerate(headers):
            mm=b05.MATERIAL_HEADER.fullmatch(h.group())
            if not mm:continue
            key=(int(mm.group(1)),g)
            if key not in wanted:continue
            need(key not in docs,"duplicate_material_document")
            doc=strict_mapping(text[h.end():headers[i+1].start() if i+1<len(headers) else len(text)])
            need(set(doc)=={"Material"} and type(doc["Material"]) is dict,"selected_material_body")
            docs[key]=doc["Material"]
    need(set(docs)==wanted,"selected_material_document_missing")
    return {key:docs[ptr[:2]] for key,ptr in ptrs.items()}
def run(a,out):
    import UnityPy
    out["phase"]="same_export_native_mips"
    receipt=native.verify(a.original,a.manifest,a.project,a.w1,a.b02)
    need(receipt["status"]==native.STATUS and receipt["mip_levels_equal"]==7 and receipt["mip_bytes_equal"]==21844
         and receipt["material_texture_pptr_matches"]==receipt["material_uv_matches"]==10,"native_same_export_not_admitted")
    out["native_same_export"]={k:receipt[k] for k in ("mip_levels_equal","mip_bytes_equal","material_texture_pptr_matches","material_uv_matches","source_sampler_fields_equal")}
    slots,targets,selected,_,_=native.select_source(a.original,a.manifest)
    chosen={}
    census=impact.load_original(a.original,a.manifest,private_particle_slot_counts=chosen)
    shader_key=identity.select(chosen,census)
    path=a.original/"Raft_Data"/shader_key[0]
    need(not path.is_symlink() and fingerprint(path)==SHADER_OWNERS[shader_key[0]],"shader_owner_sha")
    sf=UnityPy.load(str(path)).file
    obj=sf.objects.get(shader_key[1])
    need(obj is not None and obj.type.name=="Shader","shader_source_class")
    tree=obj.read_typetree()
    parsed=tree["m_ParsedForm"]
    switches,routes=router.source_routes(parsed)
    p=parsed["m_SubShaders"][0]["m_Passes"][0]
    tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    need(len(tables)==1,"original_d3d11_table")
    table=tables[0]
    pairs=translation.exact_four_stage_links(parsed,table)
    out["phase"]="original_variant_texture_sampler_operand_pairs"
    uses={};stage_count=0
    for n,(vs,fs) in enumerate(pairs):
        counts=Counter()
        for role,(dxbc,bucket,ordinal) in (("progVertex",vs),("progFragment",fs)):
            program=p[role]
            metas=[meta for b,i,meta in stage_variants(program) if b==bucket and i==ordinal]
            need(len(metas)==1,"variant_stage_metadata_identity")
            enabled={parsed["m_KeywordNames"][i] for i in metas[0]["m_KeywordIndices"]}
            need(choose_route(enabled,switches,routes)==n,"variant_route_index_drift")
            layout=bind.variant_parameter_layout(program,table,bucket,ordinal)
            textures,samplers=bind.original_names_and_registers(program,p["m_NameIndices"],layout["resources"])
            samples=sample_operand_pairs(dxbc)
            counts.update(slot_usage(samples,textures,samplers));stage_count+=1
        uses[n]=counts
    need(len(uses)==4 and stage_count==8,"incomplete_stage_population")
    out["original_routes"]=len(uses);out["original_stages"]=stage_count
    out["original_sample_instructions"]=sum(sum(c.values()) for c in uses.values())
    out["phase"]="five_same_export_material_shader_keyword_join"
    w1=json.loads(a.w1.read_text())
    shader_ptr=traced(w1,48,{shader_key})[shader_key]
    mat_ptrs=traced(w1,21,set(slots))
    exported=exported_documents(a.project,mat_ptrs)
    source_docs={}
    for owner in {k[0] for k in slots}:
        file=a.original/"Raft_Data"/owner
        need(not file.is_symlink() and fingerprint(file)==SHADER_OWNERS[owner],"material_owner_sha")
        objects=UnityPy.load(str(file)).file.objects
        for key in slots:
            if key[0]!=owner:continue
            obj=objects.get(key[1]);need(obj is not None and obj.type.name=="Material","material_source_class")
            source_docs[key]=obj.read_typetree()
    need(set(source_docs)==set(slots)==set(exported),"five_material_coverage")
    rows=[];shader_matches=0;route_counts=Counter()
    for key in slots:
        mat=source_docs[key];dst=exported[key]
        shader_matches+=int(b05._export_pointer(dst["m_Shader"])==shader_ptr)
        source_kw=keywords(mat);export_kw=keywords(dst)
        row=classify_material(slots[key],key[0],selected,source_kw,export_kw,switches,routes,uses)
        rows.append(row)
        route_counts[choose_route(source_kw[0]|source_kw[1],switches,routes)]+=1
    out["shader_pointer_matches"]=shader_matches
    out["material_count"]=len(rows)
    out["selected_native_materials"]=sum(row["selected_native_slots"]>0 for row in rows)
    out["selected_native_slots"]=sum(row["selected_native_slots"] for row in rows)
    out["selected_native_materials_with_sample_operand"]=sum(row["selected_native_sample_instructions"]>0 for row in rows)
    out["selected_native_slots_sampled"]=sum(row["selected_native_slots_sampled"] for row in rows)
    out["selected_native_slots_not_sampled"]=sum(row["selected_native_slots_not_sampled"] for row in rows)
    out["saved_route_matches"]=sum(row["saved_keyword_route_equal"] for row in rows)
    out["exported_valid_route_matches"]=sum(row["exported_valid_keyword_route_equal"] for row in rows)
    out["full_saved_keyword_matches"]=sum(row["full_saved_keyword_set_equal"] for row in rows)
    out["saved_route_population_histogram"]=sorted(route_counts.values(),reverse=True)
    out["per_material_anonymous_counts"]=sorted(rows,key=lambda x:json.dumps(x,sort_keys=True))
    need(shader_matches==5,"material_shader_pointer_drift")
    need(out["selected_native_slots"]==targets[selected],"selected_native_slot_multiplicity_drift")
    out["phase"]="complete_source_route_observation";out["status"]=STATUS

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("original","manifest","project","w1","b02","out"):p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    out=dict(status="INCONCLUSIVE",phase="start",runtime_keyword_selection_verified=False,
             original_shader_draw_verified=False,alpha_sample_value_verified=False,
             phone_black_square_emitter_verified=False,black_fire_restored=False,
             Android_device=False,production=False,XAPK=False,private_payload_published=False)
    try:run(a,out)
    except Exception as exc:
        out["failure_type"]=type(exc).__name__
        if type(exc) is Reject:out["failure_reason"]=str(exc)
    with a.out.open("x") as f:json.dump(out,f,sort_keys=True,indent=2);f.write("\n")
    print("GT_PARTICLE108_NATIVE_ROUTE_JOIN "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]==STATUS else 2
if __name__=="__main__":raise SystemExit(main())
