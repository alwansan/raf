"""Strict candidate-only Unity bundle join. No source acquisition/installation.

Compare a prepared source plan to actual editor observations and decoded stage
modules. Receipt commitments are byte consistency, never signed attestation.
For original use, independent authorization, source semantics, source-to-
compiled-program evidence and real runtime selection remain required.
"""
from __future__ import annotations
from collections import defaultdict
import re
from scripts import gt_keyword_candidate_plan as p
from scripts.gt_runtime_keyword_contract import keyword_set, strict_bundle_route_key

MODE={"Always":"Normal","Untagged":"Normal","ForwardBase":"ForwardBase",
      "ForwardAdd":"ForwardAdd","Deferred":"Deferred","ShadowCaster":"ShadowCaster"}
STAGES={"progVertex":"Vertex","progFragment":"Fragment"}
STEREO={"STEREO_INSTANCING_ON","UNITY_SINGLE_PASS_STEREO","STEREO_MULTIVIEW_ON","STEREO_CUBEMAP_RENDER_ON"}
need=p.need

def contract(manifest,packet,proof,shader):
    """Recompute planner, preserve exact source refs and pass coordinates."""
    plan=p.plan(manifest,packet,proof)
    need(plan["status"]=="PREPARED_PRIVATE_CANDIDATE_ONLY","candidate_plan_blocked")
    need(type(shader) is bytes and 0<len(shader)<=128*1024*1024,"candidate_bytes")
    parsed=manifest["original_shader_ParsedForm_full_private"]
    name=parsed.get("m_Name")
    need(type(name) is str and name.strip() and len(name)<=512,"source_shader_name_missing")
    scopes={};flags=dict(zip(parsed["m_KeywordNames"],parsed["m_KeywordFlags"],strict=True))
    passes=[];pass_names=set()
    for row,source in zip(plan["passes"],manifest["original_passes"],strict=True):
        # An unnamed/ambiguous pass or engine-fixed macro needs a separate
        # source-specific proof path. Never infer from variant count/order.
        n=source["original_state"].get("m_Name")
        need(type(n) is str and n and len(n)<=128 and n.upper() not in pass_names,"unique_named_source_pass_required")
        need(not row["fixed_keywords"],"fixed_macro_bundle_semantics_unproved")
        pass_names.add(n.upper())
        for k,v in row["keyword_scopes"].items():
            need(v in ("global","local") and scopes.get(k,v)==v,"cross_pass_keyword_scope_conflict")
            scopes[k]=v
        variants=[dict(keywords=list(k),vs=refs[0],fs=refs[1]) for k,refs in zip(row["engine_keys"],row["program_pairs"],strict=True)]
        passes.append(dict(index=row["pass_index"],name=n,mode=row["pass_mode"],passType=MODE[row["pass_mode"]],variants=variants))
    return dict(schema=1,shader_name=name,candidate_sha256=p.sha(shader),source_plan_sha256=p.commitment(plan),source_manifest_sha256=p.commitment(manifest),route_packet_sha256=p.commitment(packet),source_proof_sha256=p.commitment(proof),
                scopes=[dict(name=n,scope=s,source_flag=flags[n]) for n,s in sorted(scopes.items())],passes=passes)

def checked_keys(row):
    keys=[keyword_set(v["keywords"]) for v in row["variants"]]
    need(len(keys)==len(set(keys)) and keys,"candidate_key_population")
    return set(keys)

def _combined_stage_join(row,decoded):
    """Require independently decoded same-row VS+FS; never invent FS callbacks.

    Only verify_parsed evidence from the same immutable bundle snapshot may be
    supplied by the caller. This is consistency, not signed attestation.
    """
    need(type(decoded) is dict and type(decoded.get("rows")) is list,"unity_compiler_route_coverage")
    pairs={keyword_set(v["keywords"]):v for v in row["variants"]}
    found={}
    for r in decoded["rows"]:
        if r.get("pass_index")!=row["index"]:continue
        k=keyword_set(r.get("keywords"));stage=r.get("stage")
        need(k in pairs and stage in ("Vertex","Fragment") and (k,stage) not in found,"combined_decoded_route_population")
        model=0 if stage=="Vertex" else 4
        module=r.get("module");indices=r.get("serialized_blob_indices")
        need(r.get("combined_table") is True and r.get("source_ref")==pairs[k]["vs" if model==0 else "fs"]
             and type(module) is dict and type(module.get("model")) is int and module["model"]==model
             and p.hex64(module.get("sha256")) and type(module.get("spirv_val_exit")) is int and module["spirv_val_exit"]==0
             and type(indices) is list and indices and all(p.uint(i) for i in indices) and indices==sorted(set(indices)),
             "combined_decoded_stage_identity")
        found[k,stage]=(indices,module["sha256"])
    need(set(found)=={(k,s) for k in pairs for s in ("Vertex","Fragment")},"combined_decoded_route_population")
    for k in pairs:
        vs,fs=found[k,"Vertex"],found[k,"Fragment"]
        need(vs[0]==fs[0] and vs[1]!=fs[1],"combined_decoded_same_blob_stage_identity")
    return len(pairs)

def check_receipt(c,raw,shader,contract_bytes,bundle,run_id,*,decoded=None):
    """Require exact bytes and real callbacks. Optional same-blob stage join.

    Without independently decoded evidence, both callback stages are mandatory.
    Vertex-only callbacks require complete same-bundle validated VS and FS,
    an empty serialized FS table, same blob rows, exact program identities.
    No missing callback is fabricated.
    """
    expected=dict(schema=1,status="OBSERVED_CANDIDATE_ANDROID_VULKAN_BUNDLE",
                  run_id=run_id,unity_version="2021.3.45f2",errors=0,checkpoint="verified",
                  shader_name=c["shader_name"],android_vulkan_only=True,editor_graphics_api="Vulkan",
                  candidate_sha256=p.sha(shader),contract_sha256=p.sha(contract_bytes),
                  bundle_sha256=p.sha(bundle),bundle_bytes=len(bundle),original_assets_read=False)
    need(type(raw) is dict and all(type(raw.get(k)) is type(v) and raw[k]==v for k,v in expected.items()),"unity_receipt_or_bytes_mismatch")
    need(c["candidate_sha256"]==p.sha(shader) and type(raw.get("pass_count")) is int and raw["pass_count"]==len(c["passes"]) and raw.get("error")=="","unity_pass_or_candidate_commitment")
    scopes={}
    for r in raw["scopes"]:
        n=r.get("name")
        need(type(n) is str and n not in scopes and type(r.get("overridable")) is bool,"unity_scope_population")
        scopes[n]="global" if r["overridable"] else "local"
    need(scopes=={s["name"]:s["scope"] for s in c["scopes"]},"unity_actual_keyword_scope_mismatch")
    by_name={x["name"].upper():x for x in c["passes"]}
    got=defaultdict(set)
    for r in raw["observations"]:
        name=r.get("pass_name");stage=r.get("stage")
        need(type(name) is str and name.upper() in by_name and stage in ("Vertex","Fragment") and r.get("platform")=="Vulkan","unity_compiler_pass_stage_platform")
        row=by_name[name.upper()]
        need(r.get("pass_type")==row["passType"],"unity_observed_PassType_mismatch")
        key=keyword_set(r.get("keywords"))
        need(key in checked_keys(row),"unity_compiler_unmapped_exact_keyword_set")
        got[row["index"],stage].add(key)
    combined_passes=[];joined=0
    for row in c["passes"]:
        index=row["index"];keys=checked_keys(row)
        need(got[index,"Vertex"]==keys,"unity_compiler_route_coverage")
        fragment=got[index,"Fragment"]
        if fragment==keys:continue
        need(not fragment,"unity_compiler_route_coverage")
        joined+=_combined_stage_join(row,decoded)
        combined_passes.append(index)
    return dict(observed_scope_count=len(scopes),observed_callback_route_stage_count=sum(map(len,got.values())),observed_callback_rows=len(raw["observations"]),
                observed_vertex_callback_routes=sum(len(got[x["index"],"Vertex"]) for x in c["passes"]),
                observed_fragment_callback_routes=sum(len(got[x["index"],"Fragment"]) for x in c["passes"]),
                combined_vertex_only_callback_passes=combined_passes,fragment_routes_verified_by_combined_bundle_join=joined)

def verify_parsed(c,parsed,entries,decode,*,authored_marker_mode=False,expected_modules=None):
    """Join exact active sets and decoded module identities; no row projection.

    decode(blob) must independently validate every SPIR-V module and return
    {sha256, model, ...} records. For private original input, an independently
    established route+source-ref keyed module commitment is mandatory. Authored
    fixture mode is a separate marker oracle, not a source parity assertion.
    """
    need(parsed.get("m_Name")==c["shader_name"],"bundle_shader_name")
    names=parsed.get("m_KeywordNames");flags=parsed.get("m_KeywordFlags")
    keyword_set(names)
    need(isinstance(flags,(list,bytes,bytearray)) and len(flags)==len(names) and all(type(f) is int and 0<=f<=255 for f in flags),"bundle_keyword_flags")
    actual_flags=dict(zip(names,flags,strict=True));required={x["name"]:x["source_flag"] for x in c["scopes"]}
    need(required.keys()<=actual_flags.keys() and set(actual_flags)-set(required)<=STEREO and all(actual_flags[n]==0 for n in set(actual_flags)-set(required)),"bundle_keyword_table_unproved_extra")
    if not authored_marker_mode:
        need(all(actual_flags[n]==f for n,f in required.items()),"bundle_source_flag_byte_drift")
        need(type(expected_modules) is dict,"independent_stage_identity_commitments_required")
    subs=parsed.get("m_SubShaders")
    need(type(subs) is list and len(subs)==1 and len(subs[0]["m_Passes"])==len(c["passes"]),"bundle_pass_population")
    rows=[];cache={}
    def modules(index):
        need(type(index) is int and 0<=index<len(entries),"bundle_blob_index")
        if index not in cache:
            blob=entries[index][1]
            decoded=decode(blob)
            need(type(decoded) is list and decoded and all(type(x) is dict and p.hex64(x.get("sha256")) and type(x.get("model")) is int and x["model"] in (0,4) for x in decoded),"decoded_module_identity")
            need(len({(x["model"],x["sha256"]) for x in decoded})==len(decoded),"duplicate_module_in_blob")
            cache[index]=decoded
        return cache[index]
    seen_expected=set()
    for row,item in zip(c["passes"],subs[0]["m_Passes"],strict=True):
        state=item.get("m_State")
        need(type(item.get("m_Type")) is int and item["m_Type"]==0 and p.mode_of(state)==row["mode"] and state.get("m_Name","").upper()==row["name"].upper(),"bundle_source_pass_state_drift")
        keys=checked_keys(row);route_map={keyword_set(x["keywords"]):x for x in row["variants"]}
        tables={}
        for k,v in item.items():
            if not k.startswith("prog"):continue
            need(type(v) is dict,"bundle_program_table")
            legacy=v.get("m_SubPrograms",[]);player=v.get("m_PlayerSubPrograms",[])
            need(type(legacy) is list and type(player) is list and all(type(x) is list for x in player) and not (legacy and any(player)),"bundle_stage_table_ambiguity")
            stage_rows=legacy if legacy else [r for b in player for r in b]
            if k not in STAGES:need(not stage_rows,"unexpected_bundle_program_stage");continue
            tables[k]=stage_rows
        need(set(tables)==set(STAGES) and tables["progVertex"],"bundle_missing_vertex_stage")
        combined=not tables["progFragment"]
        if combined:tables["progFragment"]=tables["progVertex"]
        collected={};blob_indices={}
        for field,stage in STAGES.items():
            model=0 if stage=="Vertex" else 4
            per_key={};per_key_indices=defaultdict(set)
            for v in tables[field]:
                key=strict_bundle_route_key(names,v,keys)
                ix=v.get("m_BlobIndex")
                matches=[x for x in modules(ix) if x["model"]==model]
                per_key_indices[key].add(ix)
                # In a combined table EVERY row must carry BOTH stages.
                need(len(matches)==1,"bundle_row_missing_or_ambiguous_stage")
                x=matches[0];ref=route_map[key]["vs" if model==0 else "fs"]
                ident=(row["index"],tuple(sorted(key)),stage,ref)
                if key in per_key:
                    need(per_key[key]["sha256"]==x["sha256"],"bundle_ambiguous_same_key_module")
                else:
                    per_key[key]=x
                if not authored_marker_mode:
                    need(ident in expected_modules and expected_modules[ident]==x["sha256"],"bundle_independent_program_identity_mismatch")
                    seen_expected.add(ident)
            need(set(per_key)==keys,"bundle_exact_route_coverage")
            collected[stage]=per_key
            blob_indices[stage]=per_key_indices
        for v in row["variants"]:
            key=keyword_set(v["keywords"])
            for stage,ref in (("Vertex",v["vs"]),("Fragment",v["fs"])):
                x=collected[stage][key]
                rows.append(dict(pass_index=row["index"],keywords=sorted(key),stage=stage,source_ref=ref,combined_table=combined,serialized_blob_indices=sorted(blob_indices[stage][key]),module=x))
    if not authored_marker_mode:need(set(expected_modules)==seen_expected,"bundle_unused_stage_identity_commitment")
    return dict(rows=rows,decoded_blob_count=len(cache),actual_keyword_flags=actual_flags,source_flag_bytes_compared=not authored_marker_mode,
                original_runtime_verified=False,original_authorization_verified=False,production_activation=False,installation_allowed=False)
