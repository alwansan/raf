"""Revisit one retained actual authored Unity bundle, never original inputs."""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

import UnityPy
from scripts import gt_verify_921_shader_bundle as old
from scripts.gt_next23b_unity_receipt import strict_json,verify_unity_receipt
from scripts.gt_next23b_route_provenance import verify_candidate_route_manifest,verify_bundle_metadata
from scripts.gt_runtime_keyword_contract import strict_bundle_route_key
from scripts.w1_recover_depth_passes import stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms,records
from tools.gt_next23b_retained_route_markers.trace import output_expression,expected_marker,need

ROOT=Path("clients/GT/sessions/20261127-actions-execution-plan")
COUNTS=(512,4,128,512)
NAME="GT/AuthoredNext23bReceipt"
LIMIT=2*1024*1024
def digest(b):return sha256(b).hexdigest()
def dump(p,data):p.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
def read_inputs(root,out):
    proof=strict_json((ROOT/"artifact-review.json").read_bytes())
    need(proof["run_id"]==45929964298 and proof["artifact_id"]==15168725743,"historic_run_identity")
    expected={r["path"]:r for r in proof["members"]}
    found={p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    need(found==set(expected) and len(found)==8,"artifact_member_set")
    raw={}
    for name,record in expected.items():
        p=root/name
        need(not p.is_symlink() and p.stat().st_size==record["bytes"]<=LIMIT,"historic_member_size")
        b=p.read_bytes()
        need(digest(b)==record["sha256"],"historic_member_hash")
        raw[name]=b
    dump(out/"historic-members.json",proof)
    project="synthetic-next23b-project/"
    shader=raw[project+"Assets/GTNext23b.shader"]
    source=raw[project+"SyntheticSourceManifest.json"]
    route_bytes=raw[project+"Next23bEngineRoutes.json"]
    receipt=strict_json(raw[project+"ProbeResults/gt-next23b-unity-safe.json"])
    bundle=raw[project+"ProbeResults/Private/gt-next23b"]
    verified=verify_unity_receipt(receipt,shader,route_bytes,source,bundle)
    packet=strict_json(route_bytes)
    old.validate_next23b_engine_manifest(packet)
    verified.update(verify_candidate_route_manifest(source,shader,packet))
    # Retain the exact small authored bundle and its known source commitments.
    (out/"retained-authored-bundle").write_bytes(bundle)
    return shader,source,packet,bundle,verified


def decoder_factory(decoder,tmp,out):
    module_cache={}
    blob_cache={}
    def decode(index,blob):
        if index in blob_cache:return blob_cache[index]
        found={}
        for module in old.unity_vulkan_modules(blob):
            if module[:4]==b"LOMS":
                module=subprocess.run([str(decoder)],input=module,capture_output=True,
                                      check=True,timeout=15).stdout
            need(20<=len(module)<=LIMIT,"decoded_module_size")
            h=digest(module)
            if h not in module_cache:
                models=old.spirv_execution_models(module)
                need(len(models)==1 and models<={0,4},"single_graphics_entrypoint")
                model=next(iter(models))
                p=tmp/"module.spv";p.write_bytes(module)
                subprocess.run(["spirv-val","--target-env","vulkan1.1",str(p)],capture_output=True,check=True,timeout=20)
                dis=subprocess.run(["spirv-dis","--raw-id",str(p)],capture_output=True,
                                   text=True,check=True,timeout=20).stdout
                if sum(r["model"]==model for r in module_cache.values())<2:
                    (out/f"sample-{model}-{h[:12]}.spvasm").write_text(dis)
                try:marker=output_expression(dis,model)
                except (ValueError,KeyError,IndexError,TypeError) as exc:
                    (out/"unsupported-module.spvasm").write_text(dis)
                    raise ValueError(f"output_trace_unsupported_model_{model}:{exc}") from exc
                module_cache[h]={"sha256":h,"model":model,"marker":marker,"bytes":len(module)}
            row=module_cache[h];model=row["model"]
            need(model not in found,"ambiguous_module_stage_in_blob")
            found[model]=row
        need(found,"empty_vulkan_blob")
        blob_cache[index]=found
        return found
    return decode,module_cache,blob_cache


def verify_markers(parsed,entries,packet,decode,*,out=None):
    names=parsed["m_KeywordNames"]
    passes=parsed["m_SubShaders"][0]["m_Passes"]
    need(len(passes)==4,"four_pass_population")
    rows=[];summary=[]
    for pi,(sp,pr,count) in enumerate(zip(passes,packet["passes"],COUNTS)):
        keys=[frozenset(v["keywords"]) for v in pr["variants"]]
        lookup={k:i for i,k in enumerate(keys)}
        need(len(lookup)==count and keys[0] and keys[-1]==frozenset(),"authored_key_order")
        need(sp.get("m_State",{}).get("m_Name","").upper()==f"AUTHORED_PASS_{pi}","authored_named_pass")
        tables={m:stage_variants(sp[f]) for m,f in ((0,"progVertex"),(4,"progFragment"))}
        combined=not tables[4]
        if combined:tables[4]=tables[0]
        pass_summary={"pass_index":pi,"combined_table":combined,"routes":count,"empty_index":lookup[frozenset()]}
        for model,table in tables.items():
            unique={}
            for _,_,row in table:
                key=strict_bundle_route_key(names,row,set(lookup))
                idx=lookup[key];blob=row["m_BlobIndex"]
                need(type(blob) is int and 0<=blob<len(entries),"actual_blob_index")
                modules=decode(blob,entries[blob][1])
                need(model in modules and (not combined or set(modules)=={0,4}),"missing_row_stage_module")
                m=modules[model]
                want=expected_marker(model,pi,idx)
                if m["marker"]!=want:
                    if out is not None:dump(out/"marker-mismatch.json",{"pass":pi,"route":idx,"model":model,"blob_index":blob,"expected":want,"observed":m["marker"],"module_sha256":m["sha256"]})
                    raise ValueError("actual_compiled_output_marker_mismatch")
                prev=unique.setdefault(idx,(blob,m["sha256"],m["marker"]))
                need(prev==(blob,m["sha256"],m["marker"]),"ambiguous_exact_route_blob")
            need(set(unique)==set(range(count)),"missing_exact_stage_route")
            need(len({v[1] for v in unique.values()})==count,"nonunique_marker_stage_program_within_pass")
            for idx,(blob,h,marker) in sorted(unique.items()):
                rows.append([pi,idx,model,blob,h,marker])
            stage="vs" if model==0 else "fs"
            pass_summary[stage+"_unique_routes"]=len(unique)
            pass_summary[stage+"_serialized_rows"]=len(table)
        summary.append(pass_summary)
    need(len(rows)==2*sum(COUNTS),"marker_coverage_population")
    return rows,summary


def mutate(parsed,packet,kind):
    copy=deepcopy(parsed)
    sp=copy["m_SubShaders"][0]["m_Passes"][0]
    names=copy["m_KeywordNames"]
    keys=[frozenset(v["keywords"]) for v in packet["passes"][0]["variants"]]
    expected=set(keys)
    for field in ("progVertex","progFragment"):
        rows=stage_variants(sp[field])
        if not rows:continue
        by_key={}
        for _,_,row in rows:
            k=strict_bundle_route_key(names,row,expected)
            by_key.setdefault(k,row["m_BlobIndex"])
        need(by_key[keys[0]]!=by_key[keys[-1]],"distinct_actual_counterfactual_blobs")
        for _,_,row in rows:
            key=strict_bundle_route_key(names,row,expected)
            if kind=="swap_empty_and_nonempty":
                if key==keys[0]:row["m_BlobIndex"]=by_key[keys[-1]]
                elif key==keys[-1]:row["m_BlobIndex"]=by_key[keys[0]]
            elif kind=="collapse_to_first":
                row["m_BlobIndex"]=by_key[keys[0]]
            else:raise ValueError("unknown_control")
    return copy


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--decoder",type=Path,required=True)
    a=p.parse_args()
    a.out.mkdir(exist_ok=True)
    report={"status":"INCONCLUSIVE","retained_actual_authored_bundle":True,
            "original_assets_read":False,"original_runtime_program_mapping_proven":False,
            "actual_shader_gpu_execution_proven":False,"original_white_mesh_repair_proven":False,
            "production_install_allowed":False,"new_unity_execution":False,"xapk_started":False}
    try:
        shader,source,packet,bundle,verified=read_inputs(a.input,a.out)
        trees=[obj.read_typetree() for obj in UnityPy.load(bundle).objects if obj.type.name=="Shader"]
        need(len(trees)==1 and trees[0]["m_ParsedForm"]["m_Name"]==NAME and list(trees[0]["platforms"])==[18],"actual_authored_shader_identity")
        tree=trees[0];parsed=tree["m_ParsedForm"]
        [(platform,segments)]=list(decoded_platforms(tree));need(platform==18,"actual_vulkan_platform")
        entries=records(segments)
        verified.update(verify_bundle_metadata(source,parsed,packet))
        engine=[{frozenset(v["keywords"]) for v in x["variants"]} for x in packet["passes"]]
        legacy=old.verify_routes(parsed,entries,engine,str(a.decoder),COUNTS,strict_engine=True)
        report.update(bundle_sha256=digest(bundle),bundle_bytes=len(bundle),serialized_blob_records=len(entries),previous_gate_replay=legacy,metadata=verified)
        with tempfile.TemporaryDirectory() as tmp:
            decode,modules,blobs=decoder_factory(a.decoder,Path(tmp),a.out)
            rows,summary=verify_markers(parsed,entries,packet,decode,out=a.out)
            dump(a.out/"route-markers.json",rows)
            report.update(passes=summary,stage_output_markers=len(rows),
                          decoded_distinct_modules=len(modules),referenced_blob_records=len(blobs))
            controls={}
            for name in ("swap_empty_and_nonempty","collapse_to_first"):
                bad=mutate(parsed,packet,name)
                # Compare actual decoded tables/actual bytecode, not fake decoder.
                previous=old.verify_routes(bad,entries,engine,str(a.decoder),COUNTS,strict_engine=True)
                need(previous==legacy,"legacy_counterfactual_different")
                try:verify_markers(bad,entries,packet,decode)
                except ValueError as exc:
                    need(str(exc)=="actual_compiled_output_marker_mismatch","unexpected_control_rejection")
                    controls[name]={"old_gate_accepted":True,"new_marker_gate_rejected":True,"reason":str(exc)}
                else:raise ValueError("actual_route_control_accepted")
            report.update(status="PASS_RETAINED_ACTUAL_AUTHORED_2312_STAGE_OUTPUT_MARKERS",
                          actual_bundle_route_controls=controls,
                          output_dataflow_not_gpu_execution=True)
    except (ValueError,KeyError,IndexError,TypeError,OSError,subprocess.SubprocessError) as exc:
        report["reason"]=str(exc)[:500]
    dump(a.out/"report.json",report)
    print(json.dumps(report,sort_keys=True))
    if report["status"]!="PASS_RETAINED_ACTUAL_AUTHORED_2312_STAGE_OUTPUT_MARKERS":raise SystemExit(2)
if __name__=="__main__":main()
