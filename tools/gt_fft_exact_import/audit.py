"""Exact same-export compute asset import, using a separate authored PPtr witness.
The original component's complete runtime is NOT loaded or represented by a stub.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from tools.gt_fft_same_export import audit as same
from scripts import verify_original_fft_array_provenance as original

need=same.need
digest=same.digest
SCRIPT_GUID="57e609a2ab6449b6b77aac8f7cbf649c"
WRONG_GUID="d77f7a54f8a64a1d8afef2c056879637"
WITNESS_GUID="dcb80b57f792408d985d2198beef0c2a"

def sha(p):return digest(p.read_bytes())
def write_json(p,j):p.write_text(json.dumps(j,sort_keys=True)+"\n")

def witness_body(body,field_sha,target):
    same.verify_field(body,field_sha,target)
    fid,guid,kind=target
    pattern=rb"\{fileID:\s*"+str(fid).encode()+rb",\s*guid:\s*"+guid.encode()+rb",\s*type:\s*"+kind.encode()+rb"\s*\}"
    matches=re.findall(pattern,body)
    need(len(matches)==1,"exact_original_pointer_text")
    ptr=matches[0]
    need(not any(guid==g for g in (SCRIPT_GUID,WRONG_GUID,WITNESS_GUID)),"fixture_guid_collision")
    wrong=ptr.replace(guid.encode(),WRONG_GUID.encode())
    need(wrong!=ptr,"wrong_pointer_control")
    header=("%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!114 &11400000\n"
            "MonoBehaviour:\n  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {fileID: 0}\n"
            "  m_PrefabInstance: {fileID: 0}\n  m_PrefabAsset: {fileID: 0}\n  m_GameObject: {fileID: 0}\n"
            "  m_Enabled: 1\n  m_EditorHideFlags: 0\n  m_Script: {fileID: 11500000, guid: "+SCRIPT_GUID+", type: 3}\n"
            "  m_Name: ReferenceWitness\n  m_EditorClassIdentifier: \n  selected:\n  - ").encode()
    return header+ptr+b"\n  absent:\n  - "+wrong+b"\n",ptr

def stage(project,w1,component_trace,source_receipt,dest,run_id):
    s=json.loads(source_receipt.read_text())
    need(s["status"]=="OBSERVED_FFT_ORIGINAL_ARRAY_SAME_EXPORT" and s["candidate_routes"]==20 and s["one_element_array_typed_name_matched"] is True,"source_receipt")
    need(w1["export_instance"]==component_trace["export_instance"],"same_instance")
    cp=same.trace_selected(component_trace,114,(original.OWNER,original.COMPONENT_PATH_ID))
    fp=same.trace_selected(w1,72,(original.OWNER,original.FFT_PATH_ID))
    need(fp[0]==7200000 and fp[2]=="2","source_compute_pointer")
    meta=same.meta_path(project/"Assets",fp[1]);asset=meta.with_suffix("")
    need(asset.suffix==".compute" and sha(asset)==s["candidate_sha256"],"installed_candidate_identity")
    body=same.selected_body(same.meta_path(project/"Assets",cp[1]).with_suffix(""),cp[0],114)
    witness,ptr=witness_body(body,s["original_managed_field_sha256"],(fp[0],fp[1],"3"))
    need(not dest.exists() and not dest.is_symlink(),"fresh_project")
    (dest/"Assets/Editor").mkdir(parents=True);(dest/"Packages").mkdir();(dest/"ProjectSettings").mkdir()
    (dest/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
    (dest/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
    target=dest/"Assets/Original.compute";targetmeta=dest/"Assets/Original.compute.meta"
    shutil.copyfile(asset,target);shutil.copyfile(meta,targetmeta)
    need(sha(target)==sha(asset) and sha(targetmeta)==sha(meta),"exact_copy")
    here=Path(__file__).parent
    shutil.copyfile(here/"GTFFTReferenceWitness.cs",dest/"Assets/GTFFTReferenceWitness.cs")
    (dest/"Assets/GTFFTReferenceWitness.cs.meta").write_text("fileFormatVersion: 2\nguid: "+SCRIPT_GUID+"\nMonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n")
    (dest/"Assets/ReferenceWitness.asset").write_bytes(witness)
    (dest/"Assets/ReferenceWitness.asset.meta").write_text("fileFormatVersion: 2\nguid: "+WITNESS_GUID+"\nNativeFormatImporter:\n  externalObjects: {}\n  mainObjectFileID: 11400000\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n")
    shutil.copyfile(here/"GTFFTImport.cs",dest/"Assets/Editor/GTFFTImport.cs")
    private=dict(run_id=run_id,guid=fp[1],file_id=fp[0],wrong_guid=WRONG_GUID,
                 compute_sha=sha(target),meta_sha=sha(targetmeta),witness_sha=sha(dest/"Assets/ReferenceWitness.asset"))
    write_json(dest/"expected-private.json",private)
    return dict(status="STAGED_EXACT_FFT_IMPORT",run_id=run_id,candidate_sha256=private["compute_sha"],candidate_meta_sha256=private["meta_sha"],
                exact_export_candidate_copy=True,exact_export_meta_copy=True,exact_original_component_pointer_copied=True,
                pointer_sha256=digest(ptr),authored_reference_witness=True,original_component_runtime_verified=False,
                source_receipt_sha256=sha(source_receipt),android_device=False,production=False,XAPK=False)

def verify(dest,s,outcome,run_id):
    result=dict(status="INCONCLUSIVE",run_id=run_id,editor_outcome=outcome,authored_reference_witness=True,
                original_component_runtime_verified=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)
    try:
        need(s["status"]=="STAGED_EXACT_FFT_IMPORT" and s["run_id"]==run_id,"stage")
        p=json.loads((dest/"expected-private.json").read_text())
        need(p["run_id"]==run_id and p["compute_sha"]==s["candidate_sha256"] and p["meta_sha"]==s["candidate_meta_sha256"],"expected_commitment")
        result["candidate_source_unchanged"]=sha(dest/"Assets/Original.compute")==p["compute_sha"]
        result["candidate_meta_bytes_unchanged"]=sha(dest/"Assets/Original.compute.meta")==p["meta_sha"]
        result["authored_witness_bytes_unchanged"]=sha(dest/"Assets/ReferenceWitness.asset")==p["witness_sha"]
        result["candidate_meta_guid_unchanged"]=same.meta_path(dest/"Assets",p["guid"])==dest/"Assets/Original.compute.meta"
        native=dest/"editor-exit-code";mark=dest/"editor-run-marker"
        result["native_editor_exit"]=int(native.read_text()) if native.is_file() else None
        result["native_run_marker_matched"]=mark.is_file() and mark.read_text().strip()==run_id
        raw=dest/"editor-receipt.json"
        if raw.is_file():
            j=json.loads(raw.read_text())
            need(j["run_id"]==run_id,"editor_run")
            result["editor_receipt"]=j
            need(j["status"]=="PASS" and j["exact_guid_file_id"] and j["source_sha_matched"] and j["correct_reference_resolved"] and j["wrong_reference_null"] and j["wrong_guid_unresolved"] and j["kernel_registration_count"]==20 and j["workgroup_count"]==20 and j["vulkan"],"editor_receipt")
        else:raise ValueError("editor_receipt_missing")
        need(result["candidate_source_unchanged"] and result["candidate_meta_guid_unchanged"] and result["authored_witness_bytes_unchanged"] and result["native_editor_exit"]==0 and result["native_run_marker_matched"] and outcome=="success","editor_boundary")
        result.update(status="OBSERVED_EXACT_FFT_IMPORT",actual_unity_compute_import_verified=True,actual_same_guid_file_id_verified=True,
                      actual_authored_pointer_resolution_verified=True,diagnostic_candidate_numeric_kernel_registration_verified=True)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("action",choices=("stage","verify"))
    for key in ("project","w1","component-trace","source-receipt","dest","stage-report","out"):p.add_argument("--"+key,type=Path)
    p.add_argument("--run-id",required=True);p.add_argument("--outcome",default="")
    a=p.parse_args()
    if a.action=="stage":result=stage(a.project,json.loads(a.w1.read_text()),json.loads(a.component_trace.read_text()),a.source_receipt,a.dest,a.run_id)
    else:result=verify(a.dest,json.loads(a.stage_report.read_text()),a.outcome,a.run_id)
    write_json(a.out,result)
    print("GT_FFT_SAME_EXPORT_IMPORT_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in ("STAGED_EXACT_FFT_IMPORT","OBSERVED_EXACT_FFT_IMPORT") else 2
if __name__=="__main__":raise SystemExit(main())
