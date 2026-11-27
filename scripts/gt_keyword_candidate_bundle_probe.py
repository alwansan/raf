"""Authored Android Vulkan candidate bundle preparation and independent inspection.

Uses the actual strict planner/emitter and existing Unity bundle readers.
Source tables and marker programs are deliberately authored, not game data.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from scripts import gt_keyword_candidate_plan as p
from scripts import gt_keyword_candidate_bundle_contract as gate
from scripts.gt_next23b_unity_receipt import strict_json

ROOT=Path(__file__).resolve().parents[1]
EDITOR=ROOT/"tools/gt_keyword_candidate_bundle/GTKeywordCandidateBundle.cs"
SHADER="GT/AuthoredKeywordCandidate"
PASS="GT_CANDIDATE_PASS"
A,B="GT_AUTHORED_GLOBAL","GT_AUTHORED_LOCAL"
MARKERS={frozenset((A,)):(11,21),frozenset():(12,22),frozenset((A,B)):(13,23),frozenset((B,)):(14,24)}
LIMIT=8*1024*1024
need=p.need

def payload():
    sys.path.insert(0,str(ROOT/"tests"))
    from test_gt_keyword_candidate_plan import make
    manifest,packet,proof,files=make()
    parsed=manifest["original_shader_ParsedForm_full_private"]
    parsed["m_Name"]=SHADER
    state=parsed["m_SubShaders"][0]["m_Passes"][0]["m_State"]
    state["m_Name"]=PASS
    manifest["original_passes"][0]["original_state"]=state
    proof["passes"][0]["pass_state_sha256"]=p.commitment(state)
    proof["manifest_sha256"]=p.commitment(manifest)
    plan=p.plan(manifest,packet,proof);need(plan["status"]=="PREPARED_PRIVATE_CANDIDATE_ONLY","authored_plan")
    row=plan["passes"][0]
    programs={}
    for i,key in enumerate(row["engine_keys"]):
        vs,fs=MARKERS[frozenset(key)]
        programs[i]=(f"float4 gt_vs_main(float4 v:POSITION):SV_POSITION {{return float4(v.x+{vs}.0,v.y,v.z,v.w);}}\n"
                     f"float4 gt_fs_main():SV_Target {{return float4({fs}.0,0,0,1);}}")
    pragmas,branches=p.emit(row,programs)
    shader=('\n'.join([f'Shader "{SHADER}" {{','SubShader { Pass {',f'Name "{PASS}"','Tags { "LightMode" = "Always" }',
                       'Cull Off ZWrite Off ZTest Always','HLSLPROGRAM','#pragma target 4.5',
                       '#pragma only_renderers vulkan','#pragma vertex gt_vs_main','#pragma fragment gt_fs_main',
                       '#pragma use_dxc vulkan',*pragmas,branches,'ENDHLSL','} }','Fallback Off','}',''])).encode()
    c=gate.contract(manifest,packet,proof,shader)
    # Immutable authored candidate/contract from first real registration failure.
    need(p.sha(shader)=="d7218e75c69929b417d9e813be60c95b6b2dd470c2bf4dce3e4be8162df67537","retry_candidate_byte_drift")
    need(p.sha(dump(c))=="a01e3c8e4cbce8fb2b8e2fe925ded3af41e4921d67d7f77b917c4c96e943ff8f","retry_contract_byte_drift")
    return manifest,packet,proof,shader,c

def dump(x):return (json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()

def prepare(project,out):
    need(not project.exists() and not out.exists(),"fresh_authored_paths")
    manifest,packet,proof,shader,c=payload()
    (project/"Assets/Editor").mkdir(parents=True);(project/"Packages").mkdir();(project/"ProjectSettings").mkdir()
    out.mkdir()
    (project/"Assets/GTKeywordCandidate.shader").write_bytes(shader)
    (project/"Assets/Editor/GTKeywordCandidateBundle.cs").write_bytes(EDITOR.read_bytes())
    (project/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
    (project/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
    (project/"GTKeywordCandidateContract.json").write_bytes(dump(c))
    for name,data in (("source-manifest.json",dump(manifest)),("route-packet.json",dump(packet)),("source-proof.json",dump(proof)),("candidate.shader",shader),("candidate-contract.json",dump(c))):
        (out/name).write_bytes(data)

def bounded(path,limit=LIMIT):
    need(path.is_file() and not path.is_symlink() and 0<path.stat().st_size<=limit,"bounded_authored_file")
    b=path.read_bytes();need(0<len(b)<=limit,"bounded_authored_bytes")
    return b

def decode_factory(decoder,tmp,output):
    from scripts.gt_verify_921_shader_bundle import unity_vulkan_modules,spirv_execution_models
    seen={}
    def decode(blob):
        result=[]
        for module in unity_vulkan_modules(blob):
            if module[:4]==b"LOMS":
                module=subprocess.run([str(decoder)],input=module,capture_output=True,check=True,timeout=15).stdout
            h=p.sha(module)
            if h not in seen:
                need(0<len(module)<=LIMIT,"decoded_module_bound")
                models=spirv_execution_models(module);need(len(models)==1 and models<={0,4},"decoded_execution_model")
                path=tmp/(h+".spv");path.write_bytes(module)
                r=subprocess.run(["spirv-val","--target-env","vulkan1.1",str(path)],capture_output=True,timeout=30)
                need(r.returncode==0,"actual_spirv_val_rejected")
                dis=subprocess.run(["spirv-dis",str(path)],capture_output=True,text=True,check=True,timeout=30).stdout
                float32=set(re.findall(r"(?m)^\s*(%\S+)\s*=\s*OpTypeFloat\s+32\s*$",dis))
                constants=[]
                for tid,v in re.findall(r"(?m)^\s*%\S+\s*=\s*OpConstant\s+(%\S+)\s+(\S+)\s*$",dis):
                    if tid not in float32:continue
                    try:number=float.fromhex(v) if "0x" in v.lower() else float(v)
                    except ValueError:continue
                    if number in range(11,25):constants.append(int(number))
                seen[h]=dict(sha256=h,model=next(iter(models)),bytes=len(module),marker_constants=sorted(set(constants)),spirv_val_exit=0)
                (output/("module-"+h+".spv")).write_bytes(module)
            result.append(seen[h])
        return result
    return decode

def verify_marker_rows(rows):
    need(len(rows)==8 and len({r["module"]["sha256"] for r in rows})==8,"authored_distinct_stage_module_population")
    seen=set()
    for r in rows:
        key=keyword_set(r["keywords"]);stage=r["stage"];module=r["module"]
        need(key in MARKERS and stage in ("Vertex","Fragment") and r["pass_index"]==0 and (key,stage) not in seen,"authored_route_marker_population")
        marker=MARKERS[key][stage=="Fragment"]
        need(module["marker_constants"]==[marker] and module["model"]==(0 if stage=="Vertex" else 4) and module["spirv_val_exit"]==0,"authored_compiled_program_marker_mismatch")
        seen.add((key,stage))
    need(seen=={(k,s) for k in MARKERS for s in ("Vertex","Fragment")},"authored_marker_coverage")

from scripts.gt_runtime_keyword_contract import keyword_set

def verify(project,out,run_id,decoder,exit_code):
    import UnityPy
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    result=dict(status="INCONCLUSIVE",original_assets_read=False,original_runtime_verified=False,production_activation=False,Android_device=False,XAPK=False)
    try:
        manifest,packet,proof,shader,c=payload()
        for name,data in (("source-manifest.json",dump(manifest)),("route-packet.json",dump(packet)),("source-proof.json",dump(proof)),("candidate.shader",shader),("candidate-contract.json",dump(c))):
            need(bounded(out/name)==data,"authored_input_commitment_drift")
        contract_bytes=bounded(out/"candidate-contract.json")
        need(bounded(project/"Assets/GTKeywordCandidate.shader")==shader and bounded(project/"GTKeywordCandidateContract.json")==contract_bytes,"Unity_input_bytes_changed")
        if not (out/"unity-raw.json").is_file():
            need(exit_code==0,"Unity_not_completed_or_no_editor_receipt")
            raise ValueError("Unity_success_without_editor_receipt")
        raw=strict_json(bounded(out/"unity-raw.json"))
        need(raw.get("run_id")==run_id and raw.get("candidate_sha256")==p.sha(shader) and raw.get("contract_sha256")==p.sha(contract_bytes),"Unity_failure_or_success_identity_drift")
        result.update(observed_editor_graphics_api=raw.get("editor_graphics_api"),observed_editor_checkpoint=raw.get("checkpoint"),observed_editor_error=raw.get("error"),observed_editor_bundle_bytes=raw.get("bundle_bytes"))
        need(exit_code==0 and raw.get("status")=="OBSERVED_CANDIDATE_ANDROID_VULKAN_BUNDLE","actual_Unity_job_not_success")
        bundle=bounded(out/"gt-keyword-candidate.bundle")
        need(raw.get("bundle_sha256")==p.sha(bundle) and type(raw.get("bundle_bytes")) is int and raw["bundle_bytes"]==len(bundle),"Unity_bundle_byte_commitment")
        expected_keys=gate.checked_keys(c["passes"][0])
        need({keyword_set(k["keywords"]) for k in raw["material_routes"]}==expected_keys and len(raw["material_routes"])==len(expected_keys) and raw["material_restored_empty"] is True,"actual_material_keyword_API_state")
        trees=[x.read_typetree() for x in UnityPy.load(bundle).objects if x.type.name=="Shader"]
        need(len(trees)==1 and list(trees[0]["platforms"])==[18],"actual_single_Android_Vulkan_shader")
        [(platform,segments)]=list(decoded_platforms(trees[0]));need(platform==18,"Vulkan_only_platform")
        parsed=trees[0]["m_ParsedForm"];entries=records(segments)
        def table_rows(rows):
            return [dict(blob=r.get("m_BlobIndex"),indices=r.get("m_KeywordIndices"),tier=r.get("m_ShaderHardwareTier"),global_indices=r.get("m_GlobalKeywordIndices"),local_indices=r.get("m_LocalKeywordIndices")) for r in rows]
        (out/"authored-serialized-topology.json").write_bytes(dump(dict(keyword_names=parsed.get("m_KeywordNames"),keyword_flags=list(parsed.get("m_KeywordFlags",[])),passes=[dict(name=q.get("m_State",{}).get("m_Name"),type=q.get("m_Type"),tags=q.get("m_State",{}).get("m_Tags"),tables={k:dict(legacy=table_rows(v.get("m_SubPrograms",[])),player=[table_rows(bucket) for bucket in v.get("m_PlayerSubPrograms",[])]) for k,v in q.items() if k.startswith("prog")}) for sub in parsed["m_SubShaders"] for q in sub["m_Passes"]],record_count=len(entries))))
        with tempfile.TemporaryDirectory(prefix="gt-keyword-modules-") as t:
            decode=decode_factory(decoder,Path(t),out)
            detail=gate.verify_parsed(c,parsed,entries,decode,authored_marker_mode=True)
            (out/"authored-decoded-detail.json").write_bytes(dump(detail))
            verify_marker_rows(detail["rows"])
            report=gate.check_receipt(c,raw,shader,contract_bytes,bundle,run_id,decoded=detail)
            # Real bundle counterfactuals: corrupt only private copied table
            # references/keys, never regenerate or mutate the actual bundle.
            from copy import deepcopy
            controls={}
            for name,mut in (
                ("extra_active_keyword",lambda x:x["m_SubShaders"][0]["m_Passes"][0]["progVertex"]),
                ("wrong_Pass_LightMode",lambda x:x["m_SubShaders"][0]["m_Passes"][0]["m_State"]["m_Tags"]["tags"]),
            ):
                q=deepcopy(parsed)
                if name=="extra_active_keyword":
                    extra="STEREO_INSTANCING_ON"
                    if extra not in q["m_KeywordNames"]:
                        q["m_KeywordNames"]=list(q["m_KeywordNames"])+[extra]
                        q["m_KeywordFlags"]=list(q["m_KeywordFlags"])+[0]
                    table=mut(q);rows=table.get("m_SubPrograms") or next(b for b in table["m_PlayerSubPrograms"] if b)
                    rows[0]["m_KeywordIndices"]=list(rows[0]["m_KeywordIndices"])+[q["m_KeywordNames"].index(extra)]
                else:
                    tags=mut(q)
                    q["m_SubShaders"][0]["m_Passes"][0]["m_State"]["m_Tags"]["tags"]=[
                        [k,"ForwardAdd" if k.upper()=="LIGHTMODE" else v] for k,v in tags]
                try:gate.verify_parsed(c,q,entries,decode,authored_marker_mode=True)
                except ValueError as e:controls[name]=str(e)
                else:raise ValueError("actual_bundle_control_accepted:"+name)
            if report["combined_vertex_only_callback_passes"]:
                for label,mut in (
                    ("missing_decoded_fragment",lambda d:d["rows"].remove(next(r for r in d["rows"] if r["stage"]=="Fragment"))),
                    ("different_combined_blob",lambda d:next(r for r in d["rows"] if r["stage"]=="Fragment").update(serialized_blob_indices=[99999])),
                    ("separate_fragment_table",lambda d:next(r for r in d["rows"] if r["stage"]=="Fragment").update(combined_table=False)),
                ):
                    bad=deepcopy(detail);mut(bad)
                    try:gate.check_receipt(c,raw,shader,contract_bytes,bundle,run_id,decoded=bad)
                    except ValueError as e:controls[label]=str(e)
                    else:raise ValueError("actual_combined_control_accepted:"+label)
                bad=deepcopy(raw);v=deepcopy(next(r for r in raw["observations"] if r["stage"]=="Vertex"));v["stage"]="Fragment";bad["observations"].append(v)
                try:gate.check_receipt(c,bad,shader,contract_bytes,bundle,run_id,decoded=detail)
                except ValueError as e:controls["partial_fragment_callback"]=str(e)
                else:raise ValueError("actual_partial_callback_accepted")
            swapped=deepcopy(detail["rows"]);swapped[0]["module"],swapped[2]["module"]=swapped[2]["module"],swapped[0]["module"]
            try:verify_marker_rows(swapped)
            except ValueError as e:controls["wrong_stage_program_marker"]=str(e)
            else:raise ValueError("actual_module_control_accepted")
        result.update(status="PASS_ACTUAL_AUTHORED_CANDIDATE_UNITY_BUNDLE",**report,**detail,
                      actual_material_keyword_routes=len(raw["material_routes"]),actual_material_restoration=True,actual_decoded_stage_markers=8,actual_bundle_controls=controls,
                      bundle_sha256=p.sha(bundle),bundle_bytes=len(bundle),candidate_sha256=p.sha(shader),unity_receipt_sha256=p.sha(bounded(out/"unity-raw.json")),
                      original_source_flag_semantics_verified=False,original_shader_equivalence_verified=False,device_pixels_verified=False)
    except (ValueError,KeyError,TypeError,IndexError,OSError,subprocess.SubprocessError) as e:
        result["reason"]=str(e)[:300]
    (out/"verified.json").write_bytes(dump(result));print(json.dumps(result,sort_keys=True))
    if result["status"]!="PASS_ACTUAL_AUTHORED_CANDIDATE_UNITY_BUNDLE":raise SystemExit(2)

def main():
    a=argparse.ArgumentParser();s=a.add_subparsers(dest="cmd",required=True)
    b=s.add_parser("prepare");b.add_argument("--project",required=True,type=Path);b.add_argument("--out",required=True,type=Path)
    b=s.add_parser("verify");b.add_argument("--project",required=True,type=Path);b.add_argument("--out",required=True,type=Path);b.add_argument("--run-id",required=True);b.add_argument("--decoder",required=True,type=Path);b.add_argument("--exit-code",required=True,type=int)
    n=a.parse_args()
    if n.cmd=="prepare":prepare(n.project,n.out)
    else:verify(n.project,n.out,n.run_id,n.decoder,n.exit_code)
if __name__=="__main__":main()
