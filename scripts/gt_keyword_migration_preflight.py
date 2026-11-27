#!/usr/bin/env python3
"""Read-only migration preflight for ten original Shader48 pipelines.

Never reads original source owners, game assets, candidate shader bytes or
Unity bundles. Audits only explicitly enumerated versioned Python and safe
numeric JSON receipts. Static findings are not authorization, installation,
runtime equivalence, or original acceptance.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GROUPS=("30","23","18","17","15","11","10p33","10p31","7p11","7p33")
EVIDENCE="clients/GT/evidence/"
POST23=EVIDENCE+"20261117_gt_post23_same_export_and_next6_cb_order_progress.json"
NEXT23B=EVIDENCE+"20261121_gt_next23b_source_composition_verified.json"
FIRE=EVIDENCE+"20261116_gt_next30_post14_next23_and_particle108_progress.json"
SHARED="scripts/gt_install_recovered_model_shader.py"
STATE="clients/GT/state.json"
V17="clients/GT/sessions/20261127-dxt5nm-raster-route-v17/actual-pass-45979650728.json"
SOURCE_PIN="15964ea8f246b6e076ce26b60931ee2e1a9a2385"
PREFIX="GT_ORIGINAL_921_P"
KEY="engine_keywords_verified"

def source_path(g):return "scripts/gt_translate_next_remaining_"+g+"_shader48.py"
def install_path(g):return "scripts/gt_install_next"+g+"_original_shader48.py"
def need(ok,why):
    if not ok:raise ValueError(why)
def digest(b):return hashlib.sha256(b).hexdigest()
def git_blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def read(root,path):
    p=root
    for part in Path(path).parts:
        need(part not in (".","..") and not part.startswith("/"),"fixed_path")
        p=p/part;need(not p.is_symlink(),"symlink_disallowed:"+path)
    need(p.is_file() and p.stat().st_size<=1024*1024,"bounded_metadata:"+path)
    raw=p.read_bytes()
    return raw,dict(path=path,bytes=len(raw),sha256=digest(raw),git_blob_sha1=git_blob(raw))

def named_call(n,name):return isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name
def constants(n,kind=str):return [x.value for x in ast.walk(n) if isinstance(x,ast.Constant) and type(x.value) is kind]
def is_const(n,v):return isinstance(n,ast.Constant) and type(n.value) is type(v) and n.value==v
def assignment_dict(fn,name):
    found=[n.value for n in ast.walk(fn) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets) and isinstance(n.value,ast.Dict)]
    need(len(found)==1,"receipt_contract_requires_review:"+name)
    result={}
    for k,v in zip(found[0].keys,found[0].values,strict=True):
        need(isinstance(k,ast.Constant) and isinstance(k.value,str) and k.value not in result,"receipt_contract_key")
        result[k.value]=v
    return result
def function(tree,name):
    f=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name]
    need(len(f)==1,"function_requires_review:"+name)
    return f[0]

def inspect_composer(code):
    tree=ast.parse(code)
    calls=[n for n in ast.walk(tree) if named_call(n,"compose")]
    need(len(calls)==1,"compose_call_population_requires_review")
    c=calls[0];k=[x.value for x in c.keywords if x.arg=="engine_keywords"]
    need(len(k)==1,"compose_scope_requires_review")
    mode="literal_false_private_selector" if is_const(k[0],False) else "literal_true_engine_candidate" if is_const(k[0],True) else "dynamic_requires_review"
    probes=[n for n in ast.walk(tree) if named_call(n,"verify_entrypoints")]
    need(len(probes)==1,"entrypoint_call_population_requires_review")
    sets=[n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="route_sets" for t in n.targets)]
    need(len(sets)==1,"route_sets_requires_review")
    private=any(s.startswith(PREFIX) for s in constants(sets[0]))
    empty=[n for n in ast.walk(sets[0]) if isinstance(n,ast.IfExp) and isinstance(n.body,ast.List) and not n.body.elts and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Name) and n.test.left.id=="index" and len(n.test.ops)==1 and isinstance(n.test.ops[0],ast.Eq) and len(n.test.comparators)==1 and is_const(n.test.comparators[0],0)]
    used=any(x.arg=="routes" and isinstance(x.value,ast.Name) and x.value.id=="route_sets" for x in probes[0].keywords)
    return dict(compose_line=c.lineno,compose_mode=mode,private_route_verification_selector=private,index_zero_empty_private_selector=bool(empty),entrypoint_check_uses_route_sets=used,engine_keyword_runtime_parity_proven=False)

def inspect_shared(code):
    d=assignment_dict(function(ast.parse(code),"install"),"required")
    n=d.get(KEY)
    conditional=isinstance(n,ast.Compare) and isinstance(n.left,ast.Name) and n.left.id=="counts_override" and len(n.ops)==1 and isinstance(n.ops[0],ast.Is) and len(n.comparators)==1 and is_const(n.comparators[0],None)
    return dict(engine_keyword_requirement_is_counts_override_none=conditional,explicit_runtime_receipt_value_required=True if is_const(n,True) else False,requirement_line=n.lineno if n is not None else None)

def inspect_installer(code,shared):
    tree=ast.parse(code);d=assignment_dict(function(tree,"verify_receipt"),"required")
    required_positive=all(is_const(d.get(k),True) for k in ("compiled_program_table_verified","vertex_and_fragment_entrypoints_verified","vulkan_platform_only"))
    count_fields=all(k in d for k in ("vertex_routes_by_pass","fragment_routes_by_pass"))
    kw=d.get(KEY);keyword_required=is_const(kw,True)
    overrides=[n for n in ast.walk(tree) if named_call(n,"install") and any(k.arg=="counts_override" for k in n.keywords)]
    exact_override=len(overrides)==1 and any(k.arg=="counts_override" and isinstance(k.value,ast.Name) and k.value.id=="ROUTES" for k in overrides[0].keywords)
    explicit_false=bool(exact_override and shared["engine_keyword_requirement_is_counts_override_none"])
    effective="shared_explicit_false_for_override" if explicit_false else "positive_field_only_not_runtime_proof" if keyword_required else "no_positive_engine_keyword_requirement_in_verify_receipt"
    return dict(receipt_checks_compiled_table_and_entrypoints=required_positive,receipt_checks_stage_route_counts=count_fields,receipt_requires_positive_engine_keyword_field=keyword_required,shared_counts_override_call=exact_override,shared_override_requires_engine_keywords_false=explicit_false,effective_runtime_receipt_contract=effective,engine_keyword_runtime_parity_proven=False)

def historical(root):
    docs={}
    for path in (POST23,NEXT23B,FIRE,STATE,V17):
        b,record=read(root,path);docs[path]=(json.loads(b),record)
    a=docs[POST23][0];n=docs[NEXT23B][0];f=docs[FIRE][0];s=docs[STATE][0];v=docs[V17][0];q=a["accepted_material_recovery"];np=n["source_proof"];fa=f["fire_alpha"]
    need(a["original_zip2_pin"]==f["zip2_pinned_sha"]==SOURCE_PIN,"historical_source_pin")
    need((q["actual_total"],q["actual_non_dummy"],q["actual_dummy"],q["actual_dummy_original_shader_guid_targets_remaining"],q["full_export_run"])==(786,688,98,37,43929698985) and q["phone_adreno_pixels_verified"] is False and q["all_resources_restored"] is False,"historical_census_scope")
    need(n["actual_run"]==44783011957 and np["source_exact_keyword_routes_by_pass"]==[512,4,128,512] and np["source_distinct_D3D11_programs"]==134 and np["private_exact_keyword_routed_stages_compiled"]==2312 and np["Unity_shader_installation_same_export_GUID_or_device_render_proven"] is False,"NEXT23b_historical_scope")
    f2=fa["real_export_alpha_verified"];f3=fa["real_original_local_type0_source_alpha_verified"]
    need(f2["run_id"]==43777398215 and f3["run"]==43778717548 and (f2["original_materials"],f2["original_texture2d_objects"],f2["original_texenv_reference_slots"],f2["same_export_external_texture_importer_images"],f2["local_type0_unresolved"])==(5,3,10,2,1) and f3["local_original_texture28_same_export_pointer_exact_trace_match"] is True and f3["source_local_type0_top_mip_alpha_decoded"] is True and f3["all_three_external_export_images_verified"] is False and f3["local_source_exported_pixels_compared"] is False and f3["device_fire_shader_blend_pixels_verified"] is False,"Particle108_historical_scope")
    h=s["current_handoff"];a3=next(x for x in h["next_session_sequence"] if x["id"]=="A3")
    need(a3["status"]=="BLOCKED_ON_VERIFIED_AUTHORIZED_ORIGINAL_SOURCE" and h["restoration_complete"] is False and h["historical_same_export_materials"]["runtime_keyword_parity_proven"] is False and h["owner_actions_authorization"]["original_assets_require_explicit_verified_authorization"] is True,"authorization_or_acceptance_boundary_changed_requires_review")
    need(v["status"]=="PASS_ACTUAL_AUTHORED_V16_CANDIDATE_RASTER_ROUTE" and v["actual_packed_pixels"]==v["actual_normal_pixels"]==1288 and v["original_assets_read"] is False and v["original_shader_program_parity_verified"] is False and v["production_activation"] is False and s["v17_dxt5nm_raster_route_checkpoint"]["status"]==v["status"],"V17_scope")
    return dict(evidence=[r for _,r in docs.values()],post23=dict(run=q["full_export_run"],custom_total=786,non_dummy=688,dummy=98,original_GUID_targets_remaining=37,runtime_keyword_parity_proven=False,protected_file_hashes_historical=q["original_material_yaml_meta_sha_unchanged"]),NEXT23b=dict(run=n["actual_run"],original_routes_by_pass=[512,4,128,512],translated_programs=134,compiled_private_routed_stages=2312,source_composition_only=True,original_engine_routes_proven=False),Particle108=dict(external_run=f2["run_id"],local_run=f3["run"],materials=5,textures=3,texenv_slots=10,actual_external_images=2,local_type0_source_top_alpha_decoded=True,local_exported_pixels_compared=False,source_to_device_fire_parity=False),V17=dict(run=v["run"],authored_only=True,packed_pixels=1288,normal_pixels=1288),A3_status=a3["status"])

def audit(root):
    b,shared_file=read(root,SHARED);shared=inspect_shared(b.decode())
    groups=[]
    for g in GROUPS:
        b,sf=read(root,source_path(g));d,inf=read(root,install_path(g))
        groups.append(dict(group="NEXT"+g,source=sf,installer=inf,composer=inspect_composer(b.decode()),receipt=inspect_installer(d.decode(),shared),runtime_acceptance_eligible=False))
    return dict(status="BLOCKED_ORIGINAL_RUNTIME_MIGRATION_PREFLIGHT",scope="static_code_and_retained_numeric_metadata_only",original_source_pin=SOURCE_PIN,original_source_authorization_verified=False,original_assets_read=False,original_runtime_parity_proven=False,production_activation=False,Android_device=False,XAPK=False,acceptance_eligible=False,shared_installer=dict(file=shared_file,**shared),groups=groups,group_count=len(groups),private_selector_groups=sum(x["composer"]["compose_mode"]=="literal_false_private_selector" for x in groups),private_entrypoint_selector_groups=sum(x["composer"]["private_route_verification_selector"] and x["composer"]["index_zero_empty_private_selector"] and x["composer"]["entrypoint_check_uses_route_sets"] for x in groups),positive_engine_keyword_receipt_fields=sum(x["receipt"]["receipt_requires_positive_engine_keyword_field"] for x in groups),explicit_false_shared_override_groups=sum(x["receipt"]["shared_override_requires_engine_keywords_false"] for x in groups),historical=historical(root),next_required=["verified_authorized_original_source_and_pinned_hashes","source_exact_per_pass_keyword_scope_and_passType_metadata","complete_source_key_set_and_explicit_orphan_classification_no_route0_fallback","original_keyword_candidate_with_candidate_SHA_and_actual_Unity_Vulkan_both_stage_receipt","actual_runtime_route_selection_and_negative_controls","same_export_original_GUID_and_unchanged_protected_material_meta_plus_fresh_census","separate_original_visual_and_remaining_G0_G6_acceptance"])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    need(not a.out.exists(),"fresh_report")
    r=audit(ROOT);a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:r[k] for k in ("status","group_count","private_selector_groups","private_entrypoint_selector_groups","positive_engine_keyword_receipt_fields","explicit_false_shared_override_groups","original_source_authorization_verified","acceptance_eligible")},sort_keys=True))
if __name__=="__main__":main()
