"""Candidate-only source keyword migration contract; no acquisition or installation.

The caller must independently establish rights, original owner hashes, source
scope/pass semantics, and DXBC provenance before supplying a private packet.
Commitments below bind that packet; they are not attestations of those facts.
No original packet is acquired or opened here. Never accept a candidate from
flags, route counts, a non-Dummy census, or authored tests alone.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict

from scripts.gt_runtime_keyword_contract import keyword_set, exact_independent_toggle_plan

PASS_MODES=("ForwardBase","ForwardAdd","Deferred","ShadowCaster","Always","Untagged")
FIXED={"ForwardBase":{"DIRECTIONAL"},"ShadowCaster":{"UNITY_PASS_SHADOWCASTER"}}
STAGE_FIELDS={"vs":"progVertex","fs":"progFragment"}
HEX=re.compile(r"[0-9a-f]{64}\Z")
REF=re.compile(r"program-[0-9]{3,6}\Z")
ERROR="#error Unmapped_original_keyword_set"
MAX_KEYWORDS=12
MAX_PAIRS=4096

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def commitment(x):
    return sha(json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False).encode())
def hex64(x):return type(x) is str and bool(HEX.fullmatch(x))
def uint(x):return type(x) is int and x>=0
def scope_key(row):
    need(type(row) is dict and uint(row.get("subshader")) and uint(row.get("pass")),"invalid_pass_coordinate")
    return row["subshader"],row["pass"]
def variant_id(meta,bucket):
    return bucket,commitment([meta.get(k) for k in ("m_ShaderHardwareTier","m_KeywordIndices","m_GlobalKeywordIndices","m_LocalKeywordIndices")])
def exact_indices(meta,names):
    need(type(meta) is dict,"invalid_stage_metadata")
    for k in ("m_GlobalKeywordIndices","m_LocalKeywordIndices"):
        need(type(meta.get(k,[])) is list and not meta.get(k,[]),"separate_keyword_lanes_unproved")
    a=meta.get("m_KeywordIndices")
    need(type(a) is list and len(set(a))==len(a) and all(uint(i) and i<len(names) for i in a),"invalid_source_keyword_indices")
    return frozenset(names[i] for i in a)
def source_rows(program):
    need(type(program) is dict,"source_stage_table_missing")
    legacy=program.get("m_SubPrograms",[]);player=program.get("m_PlayerSubPrograms",[])
    need(type(legacy) is list and type(player) is list and all(type(x) is list for x in player) and not (legacy and any(player)),"source_stage_bucket_ambiguity")
    rows={(None,i):v for i,v in enumerate(legacy)} if legacy else {(b,i):v for b,vs in enumerate(player) for i,v in enumerate(vs)}
    need(0<len(rows)<=MAX_PAIRS,"source_stage_population")
    return rows
def mode_of(state):
    need(type(state) is dict and type(state.get("m_Tags")) is dict,"source_pass_tags_missing")
    tags=state["m_Tags"].get("tags");need(type(tags) is list,"source_pass_tags_missing")
    modes=[]
    for row in tags:
        need(type(row) in (tuple,list) and len(row)==2 and all(type(v) is str for v in row),"invalid_source_pass_tag")
        if row[0].upper()=="LIGHTMODE":modes.append(row[1])
    need(len(modes)<=1,"ambiguous_source_LightMode")
    if not modes:return "Untagged"
    # Explicitly unknown LightMode is not an untagged/default pass.
    known={m.upper():m for m in PASS_MODES if m!="Untagged"}
    return known.get(modes[0].upper())
def stage_check(row,stage,table,names,seen,refs):
    need(type(row) is dict,"stage_row_missing")
    b,i=row.get("player_bucket"),row.get("bucket_ordinal")
    need((b is None or uint(b)) and uint(i) and (b,i) in table and (b,i) not in seen,"stage_ordinal_missing_or_duplicate")
    m=row.get("original_variant_metadata");need(m==table[b,i],"stage_original_metadata_drift")
    key=exact_indices(m,names);link=row.get("original_D3D11_link");ref=row.get("program_ref")
    need(type(ref) is str and REF.fullmatch(ref) and type(link) is dict and uint(m.get("m_BlobIndex")) and type(link.get("blob_index")) is int and link["blob_index"]==m["m_BlobIndex"] and uint(link.get("segment_index")) and link.get("metadata_sha256")==commitment(m) and hex64(link.get("entry_sha256")),"stage_D3D11_identity_drift")
    # A shared reference may occur in different metadata rows/entries,
    # but can never cross vertex/fragment execution models.
    need(ref not in refs or refs[ref]==stage,"cross_stage_program_reference")
    refs[ref]=stage;seen.add((b,i))
    return key,variant_id(m,b),ref

def plan(manifest,packet,proof=None):
    """Reconcile full ParsedForm, pair/ordinal/link rows, and route packet.

    Returns candidate plan or explicit blocked reasons; malformed joins raise.
    A proof is an externally reviewed private binding, not permission and not
    a cryptographic attestation. Missing/unknown semantics never emit code.
    Supports one SubShader and independent toggle lattices only. Sparse,
    orphan, engine-special or unresolved semantics are intentionally blocked.
    """
    need(type(manifest) is dict and manifest.get("schema")==1,"unsupported_manifest_schema")
    parsed=manifest.get("original_shader_ParsedForm_full_private");need(type(parsed) is dict,"missing_full_ParsedForm")
    names=parsed.get("m_KeywordNames");flags=parsed.get("m_KeywordFlags");allnames=keyword_set(names)
    need(type(flags) is list and len(flags)==len(names) and all(uint(f) and f<=255 for f in flags),"invalid_source_flags")
    flag_by_name=dict(zip(names,flags,strict=True))
    subs=parsed.get("m_SubShaders")
    need(type(subs) is list and len(subs)==1 and type(subs[0]) is dict and type(subs[0].get("m_Passes")) is list,"unsupported_SubShader_population")
    source=subs[0]["m_Passes"];passes=manifest.get("original_passes");pairs=manifest.get("paired");orphans=manifest.get("unpaired")
    need(type(passes) is list and type(packet) is list and 0<len(source)==len(passes)==len(packet)<=16 and type(pairs) is list and 0<len(pairs)<=MAX_PAIRS and type(orphans) is list and len(orphans)<=MAX_PAIRS,"invalid_pass_or_stage_population")
    coordinates={(0,i) for i in range(len(source))}
    groups=defaultdict(list);unmatched=defaultdict(list)
    for row in pairs:
        k=scope_key(row);need(k in coordinates,"pair_pass_ownership");groups[k].append(row)
    for row in orphans:
        k=scope_key(row);need(k in coordinates and type(row.get("stage")) is int and row["stage"] in (0,1),"orphan_pass_ownership");unmatched[k].append(row)
    msha,psha=commitment(manifest),commitment(packet)
    if proof is not None:
        need(type(proof) is dict and proof.get("schema")==1 and proof.get("manifest_sha256")==msha and proof.get("packet_sha256")==psha and hex64(proof.get("source_semantics_evidence_sha256")) and type(proof.get("passes")) is list and len(proof["passes"])==len(source),"scope_proof_binding")
    refs={};results=[]
    for i,(item,p,row) in enumerate(zip(source,passes,packet,strict=True)):
        k=(0,i);need(scope_key(p)==scope_key(row)==k and type(item) is dict and type(item.get("m_Type")) is int and item["m_Type"]==0,"non_normal_or_reordered_source_pass")
        need(p.get("original_state")==item.get("m_State") and p.get("original_vertex_program")==item.get("progVertex") and p.get("original_fragment_program")==item.get("progFragment"),"pass_source_state_or_stage_table_drift")
        mode=mode_of(item["m_State"])
        tables={s:source_rows(item[f]) for s,f in STAGE_FIELDS.items()};seen={s:set() for s in tables}
        joined={};orphan_keys={"vs":set(),"fs":set()};used=set()
        for pair in groups[k]:
            v=stage_check(pair.get("vs"),"vs",tables["vs"],names,seen["vs"],refs)
            f=stage_check(pair.get("fs"),"fs",tables["fs"],names,seen["fs"],refs)
            need(v[:2]==f[:2] and v[0] not in joined,"source_pair_keyword_bucket_tier_collision")
            joined[v[0]]=(v[2],f[2]);used.update(v[0])
        for orphan in unmatched[k]:
            s="vs" if orphan["stage"]==1 else "fs"
            key,_,ref=stage_check(orphan.get("variant"),s,tables[s],names,seen[s],refs)
            need(key not in joined and key not in orphan_keys[s],"orphan_route_collision")
            orphan_keys[s].add(key);used.update(key)
        need(all(seen[s]==set(tables[s]) for s in tables),"source_stage_coverage_incomplete")
        need(all(type(p.get(field)) is int and p[field]==count for field,count in (("matched_pairs",len(joined)),("unmatched_vertex",len(orphan_keys["vs"])),("unmatched_fragment",len(orphan_keys["fs"])))),"source_pass_counts_drift")
        rr=row.get("routes");need(type(rr) is list and len(rr)==len(joined)>0,"packet_route_population")
        keys=[];program_pairs=[]
        for r in rr:
            key=keyword_set(r.get("enabled"));need(key in joined and key not in keys and joined[key]==(r.get("vs"),r.get("fs")),"packet_pair_identity_drift")
            keys.append(key);program_pairs.append(joined[key])
        need(set(keys)==set(joined),"packet_route_coverage")
        ov=row.get("unmatched_vertex_keywords");of=row.get("unmatched_fragment_keywords",[])
        need(type(ov) is list and type(of) is list and len(ov)==len(orphan_keys["vs"]) and len(of)==len(orphan_keys["fs"]) and {keyword_set(x) for x in ov}==orphan_keys["vs"] and {keyword_set(x) for x in of}==orphan_keys["fs"],"packet_orphan_classification_drift")
        u=row.get("keyword_universe")
        need(type(u) is list and len(u)==len(used) and all(type(x) is dict and set(x)=={"name","serialized_flag"} and x["name"] in allnames and type(x["serialized_flag"]) is int and flag_by_name[x["name"]]==x["serialized_flag"] for x in u) and {x["name"] for x in u}==used,"packet_keyword_universe_drift")
        reasons=[]
        if mode is None:reasons.append("unknown_original_pass_mode")
        if orphan_keys["vs"] or orphan_keys["fs"]:reasons.append("unmatched_stage_semantics_unproved")
        scopes={};fixed=set()
        if proof is None:reasons.append("source_scope_and_pass_semantics_unproved")
        else:
            b=proof["passes"][i]
            need(scope_key(b)==k and b.get("pass_state_sha256")==commitment(item["m_State"]) and b.get("pass_type")==0 and type(b["pass_type"]) is int and b.get("pass_mode")==mode,"pass_mode_proof_binding")
            lane=b.get("keywords")
            need(type(lane) is list and len(lane)==len(used),"scope_keyword_population")
            for x in lane:
                need(type(x) is dict and x.get("name") in used and x["name"] not in scopes and type(x.get("serialized_flag")) is int and x["serialized_flag"]==flag_by_name[x["name"]] and hex64(x.get("scope_evidence_sha256")) and x.get("scope") in ("global","local","engine_fixed","unresolved"),"scope_keyword_binding")
                scopes[x["name"]]=x["scope"]
                if x["scope"]=="unresolved":reasons.append("unresolved_keyword_scope")
                if x["scope"]=="engine_fixed":
                    need(x["name"] in FIXED.get(mode,set()) and all(x["name"] in key for key in keys),"unproved_engine_fixed_macro")
                    fixed.add(x["name"])
            need(set(scopes)==used,"scope_keyword_coverage")
        engine_keys=[tuple(sorted(key-fixed)) for key in keys]
        active=set().union(*(set(x) for x in engine_keys))
        if "INSTANCING_ON" in active:reasons.append("instancing_pragma_semantics_unproved")
        if len(active)>MAX_KEYWORDS:reasons.append("independent_lattice_bound_exceeded")
        else:
            try:exact_independent_toggle_plan(engine_keys)
            except ValueError:reasons.append("sparse_or_missing_empty_keyword_lattice")
        results.append(dict(subshader=0,pass_index=i,pass_mode=mode,source_pass_type=0,source_keys=[tuple(sorted(x)) for x in keys],engine_keys=engine_keys,program_pairs=program_pairs,keyword_scopes=scopes,fixed_keywords=sorted(fixed),orphan_vertex_count=len(orphan_keys["vs"]),orphan_fragment_count=len(orphan_keys["fs"]),blocked_reasons=sorted(set(reasons))))
    if proof is not None:
        programs=proof.get("programs")
        need(type(programs) is dict and set(programs)==set(refs),"program_commitment_population")
        for ref,s in refs.items():
            v=programs[ref];need(type(v) is dict and v.get("stage")==s and hex64(v.get("dxbc_sha256")),"program_stage_commitment")
        need(hex64(proof.get("layout_sha256")) and hex64(proof.get("parameter_records_sha256")) and type(proof.get("bound_stage_sha256")) is list and len(proof["bound_stage_sha256"])==2*len(pairs) and all(hex64(x) for x in proof["bound_stage_sha256"]),"candidate_input_commitment_population")
    return dict(status="PREPARED_PRIVATE_CANDIDATE_ONLY" if not any(r["blocked_reasons"] for r in results) else "BLOCKED_PRIVATE_CANDIDATE",manifest_sha256=msha,packet_sha256=psha,passes=results,original_authorization_verified=False,original_runtime_verified=False,production_activation=False,installation_allowed=False)

def emit(pass_plan,programs):
    """Emit exact branches only for a structurally eligible candidate pass."""
    need(not pass_plan["blocked_reasons"],"blocked_candidate_pass")
    keys=pass_plan["engine_keys"];names,sets=exact_independent_toggle_plan(keys)
    scopes=pass_plan["keyword_scopes"];fixed=set(pass_plan["fixed_keywords"])
    need(type(programs) is dict and all(type(i) is int for i in programs) and set(programs)==set(range(len(keys))) and all(type(x) is str and x.strip() for x in programs.values()),"candidate_program_table")
    need(all(scopes.get(n) in ("global","local") for n in names) and not fixed.intersection(names),"candidate_pragma_scope")
    pragmas=["#pragma "+("multi_compile_local" if scopes[n]=="local" else "multi_compile")+" __ "+n for n in names]
    lines=[]
    # Do not infer a default from order. Fixed macro evidence, if provided,
    # is independently required at compiler/Unity verification later.
    for i,key in enumerate(sets):
        clause=" && ".join(("" if n in key else "!")+"defined("+n+")" for n in names) or "1"
        lines.extend([("#if " if i==0 else "#elif ")+clause,programs[i]])
    lines.extend(["#else",ERROR,"#endif",""])
    return pragmas,"\n".join(lines)

def safe_summary(p):
    """Only numeric counts, coarse fixed reason labels and scope boundaries."""
    return dict(status=p["status"],passes=len(p["passes"]),route_counts=[len(x["engine_keys"]) for x in p["passes"]],orphan_vertex_counts=[x["orphan_vertex_count"] for x in p["passes"]],orphan_fragment_counts=[x["orphan_fragment_count"] for x in p["passes"]],blocked_reasons=[x["blocked_reasons"] for x in p["passes"]],original_authorization_verified=False,original_runtime_verified=False,production_activation=False,installation_allowed=False)
