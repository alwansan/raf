"""Authored differential, no game data. Actual Unity Vulkan bundle entrypoint proof."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

CASES=("common","guard_common","split_registers","guard_different_registers","negative_error")
GUARD="#if defined(SHADER_STAGE_VERTEX) && !defined(SHADER_STAGE_FRAGMENT)"
FRAG="#elif defined(SHADER_STAGE_FRAGMENT) && !defined(SHADER_STAGE_VERTEX)"
MARKER="GT_PROBE_STAGE_SELECTION"

def shared(reg):
    return f"cbuffer GTShared : register(b{reg}) {{ float4 _GTShared; }};\n"

def shader(case):
    if case not in CASES: raise ValueError("unknown_case")
    vert=frag="_GTShared"
    if case=="split_registers":
        decl=("cbuffer GTVertex : register(b2) { float4 _GTVertex; };\n"
              "cbuffer GTFragment : register(b3) { float4 _GTFragment; };\n")
        vert,frag="_GTVertex","_GTFragment"
    elif case.startswith("guard_"):
        decl=(GUARD+"\n"+shared(2)+FRAG+"\n"+shared(3 if case=="guard_different_registers" else 2)
              +"#else\n#error "+MARKER+"\n#endif\n")
    else:
        decl=shared(2)
        if case=="negative_error": decl+="#error GT_PROBE_NEGATIVE_SENTINEL\n"
    return ('Shader "Hidden/GTStageProbe/'+case+'" {\nSubShader { Pass {\nHLSLPROGRAM\n'
            '#pragma target 4.5\n#pragma only_renderers vulkan\n#pragma vertex gt_vert\n#pragma fragment gt_frag\n'
            +decl+'struct Vary { float4 pos : SV_POSITION; float4 val : TEXCOORD0; };\n'
            'Vary gt_vert(float4 pos : POSITION) { Vary o; o.pos = pos; o.pos.xy += '
            +vert+'.xy * 0.01; o.val = '+vert+'; return o; }\n'
            'float4 gt_frag(Vary i) : SV_Target { return i.val * 0.25 + '+frag+' * 0.75; }\n'
            'ENDHLSL\n} } }\n')

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def stage(dest):
    dest.mkdir()
    for d in ("Assets/Editor","Packages","ProjectSettings","cases"): (dest/d).mkdir(parents=True)
    (dest/"Assets/Editor/StageProbe.cs").write_bytes(Path(__file__).with_name("StageProbe.cs").read_bytes())
    (dest/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
    (dest/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
    for c in CASES: (dest/"cases"/(c+".shader")).write_text(shader(c))
    files=["Assets/Editor/StageProbe.cs"]+["cases/"+c+".shader" for c in CASES]
    (dest/"authored-sha.json").write_text(json.dumps({p:digest(dest/p) for p in files},sort_keys=True))

def log_case(log,case):
    start=log.find("GT_STAGE_PROBE_BEGIN "+case+"\n")
    end=log.find("GT_STAGE_PROBE_END "+case+"\n",start+1)
    if start<0 or end<0: return {"log_boundary":False}
    part=log[start:end]
    return {"log_boundary":True,
            "stage_selection_errors":sum(MARKER in l and "error" in l.lower() for l in part.splitlines()),
            "negative_sentinel_errors":sum("GT_PROBE_NEGATIVE_SENTINEL" in l and "error" in l.lower() for l in part.splitlines()),
            "shared_uniform_explicit_binding_conflicts":sum("GLSL link error" in l and "explicit bindings for uniform" in l for l in part.splitlines()),
            "vulkan_internal_program_counts":[[int(a),int(b)] for a,b in re.findall(r"vulkan \(total internal programs: (\d+), unique: (\d+)\)",part)]}

def decode(path,case,decoder):
    import UnityPy
    from scripts.w1_recover_graphics_programs import decoded_platforms, records
    from scripts.w1_recover_depth_passes import stage_variants
    from scripts.gt_verify_921_shader_bundle import unity_vulkan_modules, spirv_execution_models
    trees=[o.read_typetree() for o in UnityPy.load(str(path)).objects if o.type.name=="Shader"]
    if len(trees)!=1 or trees[0]["m_ParsedForm"]["m_Name"]!="Hidden/GTStageProbe/"+case: raise ValueError("shader_identity")
    tree=trees[0]
    if list(tree["platforms"])!=[18]: raise ValueError("not_vulkan_only")
    [(platform,segments)]=list(decoded_platforms(tree))
    if platform!=18: raise ValueError("not_vulkan_only")
    entries=records(segments)
    subs=tree["m_ParsedForm"]["m_SubShaders"]
    if len(subs)!=1 or len(subs[0]["m_Passes"])!=1: raise ValueError("pass_topology")
    p=subs[0]["m_Passes"][0]
    vertex=stage_variants(p["progVertex"])
    frag=stage_variants(p["progFragment"])
    seen={}
    with tempfile.TemporaryDirectory(prefix="gt-stage-probe-") as tmp:
        for rows in (vertex,frag or vertex):
            for _,_,row in rows:
                idx=row["m_BlobIndex"]
                if type(idx) is not int or not 0<=idx<len(entries): raise ValueError("blob_index")
                if idx in seen: continue
                models=set(); snippets=0
                for data in unity_vulkan_modules(entries[idx][1]):
                    if data[:4]==b"LOMS":
                        data=subprocess.run([str(decoder)],input=data,capture_output=True,timeout=15,check=True).stdout
                    models.update(spirv_execution_models(data))
                    spv=Path(tmp)/f"{idx}-{snippets}.spv";spv.write_bytes(data)
                    subprocess.run(["spirv-val","--target-env","vulkan1.1",str(spv)],capture_output=True,timeout=15,check=True)
                    snippets+=1
                if not snippets: raise ValueError("empty_blob")
                seen[idx]=models
    if not vertex or not any(0 in seen[r["m_BlobIndex"]] for _,_,r in vertex): raise ValueError("vertex_missing")
    if not any(4 in seen[r["m_BlobIndex"]] for _,_,r in (frag or vertex)): raise ValueError("fragment_missing")
    return dict(decoded_vertex_fragment=True,referenced_blob_count=len(seen),
                execution_models=sorted(set().union(*seen.values())),all_spirv_validated=True)

def compiled(r):
    return (r.get("imported") is True and r.get("bundleBuilt") is True and r.get("errorsBefore")==0
            and r.get("errorsAfter")==0 and r.get("decoded_vertex_fragment") is True
            and r.get("all_spirv_validated") is True and r.get("referenced_blob_count",0)>0
            and r.get("execution_models")==[0,4] and r.get("log_boundary") is True
            and r.get("stage_selection_errors")==0 and r.get("shared_uniform_explicit_binding_conflicts")==0)

def verify(dest,outcome,decoder,report):
    result=dict(status="INCONCLUSIVE",original_shader_verified=False,device_pixels=False,player_built=False,XAPK=False,editor_outcome=outcome,cases={})
    try:
        manifest=json.loads((dest/"authored-sha.json").read_text())
        expected={"Assets/Editor/StageProbe.cs",*["cases/"+c+".shader" for c in CASES]}
        if set(manifest)!=expected or any(digest(dest/p)!=v for p,v in manifest.items()): raise ValueError("source_drift")
        result["authored_source_unchanged"]=True
        editor=json.loads((dest/"editor-safe.json").read_text())
        if editor["version"]!="2021.3.45f2" or editor["androidVulkanOnly"] is not True or editor["playerBuilt"] is not False: raise ValueError("editor_environment")
        if [r["id"] for r in editor["cases"]]!=list(CASES): raise ValueError("case_set")
        log=(dest/"editor-private.log").read_text(errors="replace")
        for item in editor["cases"]:
            c=item["id"]
            r={k:item[k] for k in ("imported","bundleBuilt","errorsBefore","errorsAfter","exceptionCategory")}
            r.update(log_case(log,c))
            if r["bundleBuilt"]:
                try: r.update(decode(dest/"private-bundles"/c/"probe",c,decoder))
                except Exception as e: r["decode_failure"]=type(e).__name__+":"+str(e)[:120] if isinstance(e,ValueError) else type(e).__name__
            r["compiled"]=compiled(r)
            result["cases"][c]=r
        rows=result["cases"];neg=rows["negative_error"]
        negative=(not neg["compiled"] and neg.get("negative_sentinel_errors",0)>0 and (neg["errorsBefore"]>0 or neg["errorsAfter"]>0))
        result.update(negative_control_rejected=negative,shared_unconditional_compiled=rows["common"]["compiled"],
                      split_unconditional_compiled=rows["split_registers"]["compiled"],
                      guard_same_binding_compiled=rows["guard_common"]["compiled"],
                      guard_different_binding_compiled=rows["guard_different_registers"]["compiled"],
                      guard_error_observed=rows["guard_common"].get("stage_selection_errors",0)>0,
                      binding_conflict_observed=rows["guard_different_registers"].get("shared_uniform_explicit_binding_conflicts",0)>0)
        if outcome=="success" and negative and all(r.get("log_boundary") for r in rows.values()) and rows["common"]["compiled"] and rows["split_registers"]["compiled"]:
            result["status"]="PASS_AUTHORED_DIAGNOSTIC_MATRIX"
    except Exception as e: result["reason"]=type(e).__name__+":"+str(e)[:120] if isinstance(e,ValueError) else type(e).__name__
    report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_COMPILER_DIFFERENTIAL "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="PASS_AUTHORED_DIAGNOSTIC_MATRIX" else 2

if __name__=="__main__":
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    s=sub.add_parser("stage");s.add_argument("--dest",type=Path,required=True)
    v=sub.add_parser("verify")
    for k in ("dest","decoder","report"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--outcome",required=True)
    x=p.parse_args()
    if x.action=="stage":stage(x.dest)
    else:raise SystemExit(verify(x.dest,x.outcome,x.decoder,x.report))
