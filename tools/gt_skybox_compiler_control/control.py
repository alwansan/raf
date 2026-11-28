"""Exact original Skybox compiler-lowering control. No shader body or source asset edits."""
import argparse
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

DXC_LINE=b"#pragma use_dxc vulkan\n"
ORIGINAL_SHA="06b9c2f7dd5f213c653d3a5304eadab557a39273a542a1c4bf2af708628aae6c"
ORIGINAL_STAGE="PASS_EXACT_SKYBOX_EDITOR_STAGING"
STAGE="PASS_EXACT_SOURCE_BODY_COMPILER_CONTROL_STAGED"
PASS="PASS_PRIVATE_ORIGINAL_COMPILER_CONTROL_DECODED_PENDING_ABI_AND_NATIVE_LOG"
FILES={"Assets/Original.shader","Assets/Original.shader.meta","Assets/Original.mat","Assets/Original.mat.meta"}
STEREO={"STEREO_INSTANCING_ON","UNITY_SINGLE_PASS_STEREO","STEREO_MULTIVIEW_ON","STEREO_CUBEMAP_RENDER_ON"}
LANES=("m_KeywordIndices","m_GlobalKeywordIndices","m_LocalKeywordIndices")

def require(ok,why):
    if not ok:raise ValueError(why)

def hash_bytes(data):return hashlib.sha256(data).hexdigest()
def digest(path):return hash_bytes(path.read_bytes())

def remove_dxc(source):
    require(type(source) is bytes and source.count(DXC_LINE)==1,"exact_dxc_line_count")
    require(source.count(b"#pragma use_dxc")==1,"unexpected_dxc_directive")
    start=source.index(DXC_LINE)
    require(start==0 or source[start-1:start]==b"\n","dxc_line_not_standalone")
    new=source[:start]+source[start+len(DXC_LINE):]
    require(new[:start]+DXC_LINE+new[start:]==source,"compiler_control_not_reversible")
    require(b"#pragma use_dxc" not in new,"dxc_directive_remaining")
    return new

def stage(dest,prior_report,report):
    out=dict(status="INCONCLUSIVE",original_shader_verified=False,player_built=False,XAPK=False)
    try:
        s=json.loads(prior_report.read_text())
        require(s["status"]==ORIGINAL_STAGE and s["candidate_sha256"]==ORIGINAL_SHA and
                s["prior_static_wrapper_digest_reproduced"] is True and
                s["protected_export_files_unchanged"]==5,"prior_exact_replay_required")
        original=s["exact_same_export_files"]
        require(set(original)==FILES and all(digest(dest/p)==h for p,h in original.items()),"prior_stage_hash_drift")
        target=dest/"Assets/Original.shader"
        raw=target.read_bytes()
        require(hash_bytes(raw)==ORIGINAL_SHA,"original_candidate_digest")
        control=remove_dxc(raw)
        changed=hash_bytes(control)
        require(changed!=ORIGINAL_SHA,"candidate_not_changed")
        expected_path=dest/"expected-private.json"
        expected=json.loads(expected_path.read_text())
        require(expected["candidateSha256"]==ORIGINAL_SHA,"expected_original_digest")
        target.write_bytes(control)
        expected["candidateSha256"]=changed
        expected_path.write_text(json.dumps(expected))
        files=dict(original,**{"Assets/Original.shader":changed})
        require(all(digest(dest/p)==h for p,h in files.items()),"staged_control_drift")
        out.update(status=STAGE,prior_exact_sha256=ORIGINAL_SHA,candidate_sha256=changed,
                   one_dxc_pragma_removed=True,exact_reversible_body_unchanged=True,
                   original_static_offsets=45,original_static_named_resources=10,
                   original_static_varying_registers=7,unchanged_material_and_metas=3,
                   protected_original_export_files=5,files=files,
                   expected_manifest_sha256=digest(expected_path))
    except Exception as e:out["reason"]=str(e) if type(e) is ValueError else type(e).__name__
    report.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_COMPILER_CONTROL_STAGE "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]==STAGE else 2

def validate_route_tables(parsed,stage_variants):
    names=parsed["m_KeywordNames"]
    flags=parsed["m_KeywordFlags"]
    require(type(names) is list and len(names)==len(set(names)) and set(names)<=STEREO,
            "unexpected_keyword_names")
    require(isinstance(flags,(list,bytes,bytearray)) and len(flags)==len(names) and all(f==0 for f in flags),
            "active_keyword_flags")
    subs=parsed["m_SubShaders"]
    require(len(subs)==1 and len(subs[0]["m_Passes"])==1,"pass_topology")
    p=subs[0]["m_Passes"][0]
    require(p.get("m_Type")==0,"non_normal_pass")
    tables={}
    for k,program in p.items():
        if not k.startswith("prog"):continue
        rows=stage_variants(program)
        if k not in ("progVertex","progFragment"):
            require(not rows,"unexpected_stage")
            continue
        for _,_,row in rows:
            require(any(l in row for l in LANES) and
                    all(type(row.get(l,[])) is list and not row.get(l,[]) for l in LANES),"active_or_invalid_route")
        require(len(rows)==len({bucket for bucket,_,_ in rows}),"duplicate_route_bucket")
        tables[k]=rows
    require(bool(tables.get("progVertex")) and "progFragment" in tables,"missing_vertex_or_stage_table")
    fallback=not tables["progFragment"]
    if fallback:tables["progFragment"]=tables["progVertex"]
    else:require({b for b,_,_ in tables["progVertex"]}=={b for b,_,_ in tables["progFragment"]},"stage_bucket_mismatch")
    return tables,fallback,len(names)

def decode_bundle(path,name,decoder):
    import UnityPy
    from scripts.w1_recover_graphics_programs import decoded_platforms, records
    from scripts.w1_recover_depth_passes import stage_variants
    from scripts.gt_verify_921_shader_bundle import unity_vulkan_modules, spirv_execution_models
    trees=[o.read_typetree() for o in UnityPy.load(str(path)).objects if o.type.name=="Shader"]
    require(len(trees)==1 and trees[0]["m_ParsedForm"]["m_Name"]==name,"bundle_shader_identity")
    tree=trees[0]
    require(list(tree["platforms"])==[18],"bundle_not_vulkan_only")
    [(platform,segments)]=list(decoded_platforms(tree))
    require(platform==18,"bundle_platform")
    entries=records(segments)
    tables,fallback,keywords=validate_route_tables(tree["m_ParsedForm"],stage_variants)
    blobs={}; modules={}; counts={}
    with tempfile.TemporaryDirectory(prefix="gt-skybox-control-decode-") as tmp:
        def decode(index):
            require(type(index) is int and 0<=index<len(entries),"blob_index")
            if index not in blobs:
                payload=entries[index][1]
                require(len(payload)>=32 and struct.unpack_from("<I",payload,24)[0]==0,"embedded_keyword_table")
                found=[]
                for data in unity_vulkan_modules(payload):
                    if data[:4]==b"LOMS":
                        data=subprocess.run([str(decoder)],input=data,capture_output=True,timeout=15,check=True).stdout
                    h=hash_bytes(data)
                    if h not in modules:
                        models=spirv_execution_models(data)
                        require(len(models)==1 and models<={0,4},"unexpected_execution_model")
                        p=Path(tmp)/(h+".spv");p.write_bytes(data)
                        subprocess.run(["spirv-val","--target-env","vulkan1.1",str(p)],capture_output=True,timeout=30,check=True)
                        modules[h]=next(iter(models))
                    found.append(h)
                require(bool(found),"empty_compiled_blob")
                blobs[index]=found
            return blobs[index]
        for stage,model in (("progVertex",0),("progFragment",4)):
            rows=tables[stage]
            for _,_,row in rows:
                matches=[h for h in decode(row["m_BlobIndex"]) if modules[h]==model]
                require(len(matches)==1,"missing_or_ambiguous_execution_stage_"+stage)
            counts[stage]=len(rows)
    require(set(modules.values())=={0,4},"both_execution_models_required")
    return dict(vulkan_platform_only=True,actual_empty_route_stage_rows=counts,
                fragment_table_fallback=fallback,inactive_stereo_keyword_count=keywords,
                decoded_unique_modules=len(modules),decoded_blobs=len(blobs),
                execution_models=[0,4],all_referenced_spirv_validated=True)

def verify(dest,stage_report,outcome,decoder,report):
    from tools.gt_skybox_editor_import import stage as old
    out=dict(status="INCONCLUSIVE",editor_outcome=outcome,original_shader_verified=False,
             original_runtime_abi_verified=False,unity_native_log_reconciled=False,
             device_pixels_proven=False,player_built=False,XAPK=False)
    try:
        s=json.loads(stage_report.read_text())
        require(s["status"]==STAGE and s["prior_exact_sha256"]==ORIGINAL_SHA and
                s["exact_reversible_body_unchanged"] is True,"control_stage_required")
        require(set(s["files"])==FILES and all(digest(dest/p)==h for p,h in s["files"].items()),"four_file_hash_drift")
        out["protected_staged_files_unchanged"]=4
        ep=dest/"expected-private.json"
        require(digest(ep)==s["expected_manifest_sha256"],"expected_manifest_drift")
        expected=json.loads(ep.read_text())
        raw=json.loads((dest/"editor-safe.json").read_text())
        require(raw["candidateSha256"]==s["candidate_sha256"]==expected["candidateSha256"],"editor_candidate_digest")
        # Validate the unchanged editor schema and exact identity/value acceptance;
        # the candidate digest is separately compared above to the new control.
        out["editor"]={k:v for k,v in raw.items() if k in old.SAFE_EDITOR_FIELDS}
        ok=old.verify_editor(dict(raw,candidateSha256=ORIGINAL_SHA))
        out["editor_identity_and_values_pass"]=all(raw.get(k) is True for k in
            ("shaderIdentity","materialIdentity","materialShaderReference","shaderNameExact","androidVulkanOnly")) and tuple(raw[k] for k in
            ("sourcePropertyCount","colorSlots","colorMatches","floatSlots","floatMatches","intSlots","texEnvSlots","passCount"))==(0,6,6,20,20,0,0,1)
        bundle=dest/"private-bundle"/"skybox-private"
        out["bundle_present"]=bundle.is_file()
        if bundle.is_file():
            out["bundle_sha256"]=digest(bundle)
            require(bundle.stat().st_size==raw["privateBundleBytes"],"bundle_size_drift")
            out["compiled_program_proof"]=decode_bundle(bundle,expected["shaderName"],decoder)
        require(outcome=="success" and ok and out["editor_identity_and_values_pass"] and
                out.get("compiled_program_proof",{}).get("all_referenced_spirv_validated") is True,"editor_or_program_gate")
        out["status"]=PASS
    except Exception as e:out["reason"]=str(e)[:160] if type(e) is ValueError else type(e).__name__
    report.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_COMPILER_CONTROL_VERIFY "+json.dumps(out,sort_keys=True))
    return 0 if out["status"]==PASS else 2

if __name__=="__main__":
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("stage")
    for k in ("dest","prior-report","report"):s.add_argument("--"+k,type=Path,required=True)
    v=sub.add_parser("verify")
    for k in ("dest","stage-report","decoder","report"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--outcome",required=True)
    x=p.parse_args()
    raise SystemExit(stage(x.dest,x.prior_report,x.report) if x.cmd=="stage" else verify(x.dest,x.stage_report,x.outcome,x.decoder,x.report))
