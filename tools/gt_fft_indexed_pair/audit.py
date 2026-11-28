"""G4 scoped original-derived indexed vs standalone Unity dispatch; not game FFT parity."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
from scripts import gt_stage_indexed_fft_candidate as indexed
from scripts import t1_stage_original_fft_compute_candidates as original
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.probe_directx_shader_bridge import inspect
from scripts.probe_original_fft_resource_bindings import resource_rows
from scripts.t1_fft_unity_gpu_resource_bridge import translated_image_symbols

SLOTS=(6,7,16,17)
SEEDS=(0,19)
SIZE=1024
OBJECT_SHA=original.ORIGINAL_FFT_OBJECT_SHA256
STATUS="OBSERVED_INDEXED_FFT_PAIR_EDITOR_VULKAN"
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,sort_keys=True,allow_nan=False)+"\n")
def stage(source,project,private,run_id):
    import UnityPy
    need(re.fullmatch(r"[0-9]+-[0-9]+",run_id) and not project.exists() and not private.exists(),"fresh_stage")
    with tempfile.TemporaryDirectory(prefix="gt-fft-pair-",dir=private.parent) as tmp:
        work=Path(tmp);candidate=work/"source"
        report=original.stage_original_candidates(source,candidate)
        m=json.loads((candidate/"Assets/T1OriginalDerived/PrivateCandidates.json").read_text())
        original.validate_import_candidate_manifest(m,candidate)
        tree=UnityPy.load(str(source/indexed.OWNER)).file.objects[indexed.PATH_ID].read_typetree()
        rows=resource_rows(tree)
        need(len(rows)==20 and len(m["rows"])==20,"source_population")
        private.mkdir(mode=0o700);program=private/"indexed.compute";parts=[];selected=[]
        for record,entry in zip(rows,m["rows"],strict=True):
            i=record["compiled_slot"];path=candidate/entry["compute_asset"]
            need(i==entry["compiled_slot"] and sha(path)==entry["candidate_sha256"],"source_slot_identity")
            body=path.read_text();parts.append(indexed.route(body,record))
            if i in SLOTS:
                symbols=translated_image_symbols(body);name=f"reference-{i}.compute"
                shutil.copyfile(path,private/name)
                selected.append(dict(slot=i,group=record["workgroup_xyz"][0],file=name,sha256=sha(private/name),
                                     source_property=symbols["source"],butterfly_property=symbols["butterfly"],
                                     target_property=symbols["output"],dxbc_sha256=entry["original_dxbc_sha256"]))
        program.write_text("".join(f"#pragma kernel {indexed.entry(i)} RAFT_FFT_SLOT={i}\n" for i in range(20))+"\n"+"".join(parts))
        for row in selected:
            i=row["slot"];mod=work/"a.spv";ref=work/"b.spv"
            private_command(["glslangValidator","-V","-D",f"-DRAFT_FFT_SLOT={i}","-S","comp","-e",indexed.entry(i),"-o",str(mod),str(program)])
            private_command(["spirv-val","--target-env","vulkan1.1",str(mod)])
            need(inspect(mod.read_bytes())["declared_local_workgroup_sizes"]==[[row["group"],1,1]],"group_drift")
            private_command(["glslangValidator","-V","-D","-S","comp","--source-entrypoint","main","-e",indexed.entry(i),
                             "-o",str(ref),str(private/row["file"])])
            for f in (mod,ref):private_command(["spirv-opt","--strip-debug",str(f),"-o",str(f)])
            need(mod.read_bytes()==ref.read_bytes(),"indexed_reference_executable_drift")
        need([r["slot"] for r in selected]==list(SLOTS) and all(r["group"]==512 for r in selected),"selected_group_drift")
        dump(private/"config.json",dict(run_id=run_id,object_sha=OBJECT_SHA,indexed_sha=sha(program),rows=selected))
        (project/"Assets/Editor").mkdir(parents=True);(project/"Packages").mkdir();(project/"ProjectSettings").mkdir()
        (project/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
        (project/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
        shutil.copyfile(Path(__file__).with_name("IndexedPair.cs"),project/"Assets/Editor/IndexedPair.cs")
    return dict(status="STAGED_AUTHENTIC_INDEXED_PAIR",source_object_sha256=OBJECT_SHA,
                original_translated_slots=report["original_compiled_programs_reconstructed"],
                indexed_reference_spirv_exact=4,selected_slots=list(SLOTS),workgroup_x=512,
                private_config_sha256=sha(private/"config.json"),original_runtime_kernel_mapping_proven=False,android_device=False)
def verify(receipt,stage,run_id,editor_outcome):
    need(editor_outcome=="success" and receipt["status"]=="PASS" and receipt["run_id"]==run_id and
         receipt["config_sha256"]==stage["private_config_sha256"] and receipt["private_guard"] is True and
         receipt["vulkan"] is True and receipt["registration_count"]==20 and receipt["private_source_hashes_match"] is True,
         "editor_identity_or_backend")
    cases=receipt["cases"]
    need(len(cases)==4 and [(c["first_slot"],c["seed"]) for c in cases]==[(s,n) for s in (6,16) for n in SEEDS],
         "editor_case_population")
    for c in cases:
        need(c["dispatches"]==4 and c["bindings"]==12 and c["sentinel_checks"]==4 and c["nonfinite_components"]==0 and
             len(c["indexed_written"])==len(c["reference_written"])==2 and
             all(type(x) is int and 0<x<=SIZE*SIZE for x in c["indexed_written"]+c["reference_written"]) and
             c["coverage_mismatch"]==[0,0] and c["different_over_tolerance"]==[0,0],
             "editor_indexed_pair_parity")
    return dict(status=STATUS,cases=cases,registered_slots=20,authentic_slots=list(SLOTS),
                dispatches=sum(c["dispatches"] for c in cases),bindings=sum(c["bindings"] for c in cases),
                original_runtime_kernel_mapping_proven=False,original_game_inputs_verified=False,
                original_fft_numeric_parity_verified=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)

PROGRESS={
    "environment":{"managed_entry"},
    "private_import":{"copy","refresh","load_indexed","register","load_references"},
    "paired_dispatch":{"allocate","sentinel","bind_source","bind_butterfly","bind_target","dispatch","dispatch_returned","compare"},
    "identity":{"validate"},"complete":{"receipt"},
}
def bounded_progress(private,run_id):
    """Only accept authored phases/counts. Never report raw logs or identifiers."""
    private=Path(private)
    names=("editor-output-private","editor.log","editor-stdout.log","editor-exit-code","progress.json","receipt.json")
    present={name:(private/name).is_file() and not (private/name).is_symlink() for name in names}
    out={"private_files_present":present,"last_managed_checkpoint":None,"editor_native_exit":None}
    if not present["editor-output-private"]:return out
    marker=private/"editor-output-private"
    if marker.stat().st_size>128 or marker.read_text().strip()!=run_id:return out
    out["private_launch_marker_matches"]=True
    if present["editor-exit-code"]:
        path=private/"editor-exit-code"
        if path.stat().st_size<=16:
            value=path.read_text().strip()
            if re.fullmatch(r"[0-9]{1,3}",value) and int(value)<=255:out["editor_native_exit"]=int(value)
    if present["progress.json"]:
        path=private/"progress.json"
        if path.stat().st_size<=4096:
            r=json.loads(path.read_text())
            fields={"run_id","phase","operation","first_slot","seed","pass","variant","bindings","dispatches"}
            if (type(r) is dict and set(r)==fields and r["run_id"]==run_id and
                r["phase"] in PROGRESS and r["operation"] in PROGRESS[r["phase"]] and
                all(type(r[k]) is int for k in fields-{"run_id","phase","operation"}) and
                r["first_slot"] in (-1,6,16) and r["seed"] in (-1,0,19) and
                r["pass"] in (-1,0,1) and r["variant"] in (-1,0,1) and
                0<=r["bindings"]<=12 and 0<=r["dispatches"]<=4):
                out["last_managed_checkpoint"]={k:v for k,v in r.items() if k!="run_id"}
    return out

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    st=sub.add_parser("stage")
    for k in ("source","project","private","out"):st.add_argument("--"+k,type=Path,required=True)
    st.add_argument("--run-id",required=True)
    v=sub.add_parser("verify")
    for k in ("project","private","stage","out"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--run-id",required=True);v.add_argument("--outcome",required=True)
    a=p.parse_args();result=dict(status="INCONCLUSIVE",original_runtime_kernel_mapping_proven=False,water_rendering_verified=False,android_device=False,XAPK=False)
    try:
        if a.action=="stage":result=stage(a.source,a.project,a.private,a.run_id)
        else:
            s=json.loads(a.stage.read_text());cfg=a.private/"config.json"
            progress=bounded_progress(a.private,a.run_id);result["editor_progress"]=progress
            need(sha(cfg)==s["private_config_sha256"] and progress.get("private_launch_marker_matches") is True and
                 progress["private_files_present"]["editor.log"],"private_editor_commitment")
            need(progress["private_files_present"]["receipt.json"],"editor_receipt_missing")
            r=json.loads((a.private/"receipt.json").read_text());result["editor_receipt"]=r
            need(progress["editor_native_exit"]==0 and progress["last_managed_checkpoint"] is not None and
                 progress["last_managed_checkpoint"]["phase"]=="complete","editor_native_completion")
            manifest=json.loads(cfg.read_text())
            for name,digest in [("indexed.compute",manifest["indexed_sha"])]+[(x["file"],x["sha256"]) for x in manifest["rows"]]:
                need(sha(a.private/name)==digest and sha(a.project/"Assets/Private"/name)==digest,"editor_program_bytes_changed")
            result=verify(r,s,a.run_id,a.outcome);result["editor_progress"]=progress
    except Exception as exc:
        result["failure_type"]=type(exc).__name__
        if isinstance(exc,ValueError) and re.fullmatch(r"[a-z_]+",str(exc)):result["failure_reason"]=str(exc)
    dump(a.out,result);print("GT_FFT_INDEXED_PAIR_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in ("STAGED_AUTHENTIC_INDEXED_PAIR",STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
