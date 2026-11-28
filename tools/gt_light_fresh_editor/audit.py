"""Fresh same-instance level38 hierarchy import, distinct from exact-prior replay.
Never modify historical export hashes. Bind current stage, selected identities,
private expectation and editor receipt to one run; add independent world TRS.
"""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import shutil
from tools.gt_light_exact_editor import audit as prior
from tools.gt_light_same_export import stage_import as old
from tools.gt_light_same_export.audit import require, Rejected

STATUS="PASS_FRESH_LEVEL38_SCENE_EDITOR_HIERARCHY_WORLD"
STAGE="PASS_FRESH_LEVEL38_SAME_INSTANCE_STAGED"
def sha(path):return sha256(path.read_bytes()).hexdigest()
def digest(x):return type(x) is str and re.fullmatch(r"[0-9a-f]{64}",x) is not None
def write(path,data):
    with path.open("x") as f:json.dump(data,f,sort_keys=True,allow_nan=False)
def run_token(x):return type(x) is str and re.fullmatch(r"[0-9]+-[0-9]+",x) is not None

def validate_fresh_stage(s):
    require(type(s) is dict and digest(s.get("scene_sha256")) and digest(s.get("scene_meta_sha256"))
            and s.get("source_scene_sha256")==prior.SOURCE_SHA and s.get("selected_objects")==prior.EXPECTED_OBJECTS
            and s.get("same_export_scene_copy_exact") is True and s.get("other_original_assets_staged")==0
            and s.get("scene_dependency_closure_claimed") is False and s.get("import_executed") is False,
            "fresh_same_instance_stage_scope")
    return (s["scene_sha256"]==prior.SCENE_SHA,s["scene_meta_sha256"]==prior.META_SHA)

def vector(a,n):
    require(type(a) is list and len(a)==n and all(type(x) in (float,int) and math.isfinite(x) for x in a),
            "fresh_world_vector_schema")
    return list(map(float,a))
def normq(q):
    q=vector(q,4);n=math.sqrt(sum(x*x for x in q))
    require(abs(n-1.)<1e-3,"fresh_world_rotation_norm")
    return [x/n for x in q]
def product(a,b):
    return [sum(a[r*4+k]*b[k*4+c] for k in range(4)) for r in range(4) for c in range(4)]
def qmul(a,b):
    x,y,z,w=a;X,Y,Z,W=b
    return normq([w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z])
def trs(node):
    px,py,pz=vector(node["position"],3);sx,sy,sz=vector(node["scale"],3)
    x,y,z,w=normq(node["rotation"])
    return [(1-2*(y*y+z*z))*sx,(2*(x*y-z*w))*sy,(2*(x*z+y*w))*sz,px,
            (2*(x*y+z*w))*sx,(1-2*(x*x+z*z))*sy,(2*(y*z-x*w))*sz,py,
            (2*(x*z-y*w))*sx,(2*(y*z+x*w))*sy,(1-2*(x*x+y*y))*sz,pz,
            0.,0.,0.,1.]
def world_rows(manifest):
    nodes=manifest["nodes"]
    require(len(nodes)==42 and len({n["id"] for n in nodes})==42,"fresh_world_identity_population")
    index={n["id"]:n for n in nodes};chain={n["id"]:n for n in nodes if n["hasTRS"]}
    require(len(chain)==3 and all(n["cid"] in (4,224) for n in chain.values()),"fresh_world_chain_population")
    out=[];cache={}
    def compute(i,seen=()):
        require(i in chain and i not in seen,"fresh_world_chain_missing_or_cycle")
        if i in cache:return cache[i]
        n=chain[i];local=trs(n);q=normq(n["rotation"]);owner=index[n["owner"]]
        require(owner["cid"]==1 and owner["hasActive"] and type(owner["active"]) is bool,
                "fresh_world_owner")
        active=owner["active"]
        if n["parent"]!="0":
            m,p,a=compute(n["parent"],(*seen,i));local=product(m,local);q=qmul(p,q);active=active and a
        require(all(math.isfinite(x) for x in local),"fresh_world_matrix_nonfinite")
        cache[i]=(local,q,active);return cache[i]
    for i,n in chain.items():
        matrix,q,active=compute(i)
        x,y,z,w=q
        out.append(dict(id=i,matrix=matrix,position=[matrix[3],matrix[7],matrix[11]],
                        direction=[2*(x*z+y*w),2*(y*z-x*w),1-2*(x*x+y*y)],
                        active=active))
    require(all(r["active"] for r in out),"fresh_world_active_chain_drift")
    light=[n for n in nodes if n["hasLight"]]
    require(len(light)==1 and light[0]["enabled"] is True,"fresh_world_light")
    owner=light[0]["owner"];target=[r["id"] for r in out if chain[r["id"]]["owner"]==owner]
    require(len(target)==1,"fresh_world_light_transform")
    return dict(rows=out,light_id=light[0]["id"],light_transform_id=target[0])

def compose_editor(text,extra):
    def replace(a,b):
        nonlocal text
        require(text.count(a)==1,"fresh_editor_anchor")
        text=text.replace(a,b,1)
    replace("public static class GTPrivateLightImport","public static partial class GTPrivateLightImport")
    replace('            Manifest m=JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(root,"expected-private.json")));',
            '            PrepareFresh(root);\n            Manifest m=JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(root,"expected-private.json")));')
    replace('            r.status=r.mismatches==0&&r.matchedObjects==m.nodes.Length?"PASS":"FAIL";',
            '            ObserveWorld(root,m.guid,found);\n            r.status=r.mismatches==0&&r.matchedObjects==m.nodes.Length?"PASS":"FAIL";')
    require("public static partial class GTPrivateLightImport" in extra,"fresh_editor_partial")
    return text

def stage(x):
    result=dict(status="INCONCLUSIVE",Unity_import_verified=False,player_built=False,XAPK=False)
    try:
        require(run_token(x.run_id) and not x.private.exists(),"fresh_run_identity")
        prior.validate_same_export(json.loads(x.same_export.read_text()))
        old.stage(x.source,x.project,x.trace,x.w1,x.b02,x.dest,x.raw_stage)
        raw=json.loads(x.raw_stage.read_text())
        historical=validate_fresh_stage(raw)
        x.private.mkdir(mode=0o700)
        for name in ("PrivateScene.unity","PrivateScene.unity.meta"):
            (x.dest/"Assets"/name).rename(x.private/name)
        (x.dest/"expected-private.json").rename(x.private/"expected-private.json")
        expected=json.loads((x.private/"expected-private.json").read_text())
        write(x.private/"expected-world.json",world_rows(expected))
        hashes={name:sha(x.private/name) for name in ("PrivateScene.unity","PrivateScene.unity.meta","expected-private.json","expected-world.json")}
        require(hashes["PrivateScene.unity"]==raw["scene_sha256"] and hashes["PrivateScene.unity.meta"]==raw["scene_meta_sha256"],
                "fresh_private_move_drift")
        commitment=dict(run_id=x.run_id,scene=hashes["PrivateScene.unity"],meta=hashes["PrivateScene.unity.meta"],
                        expected=hashes["expected-private.json"],world=hashes["expected-world.json"],
                        same_export=sha(x.same_export),raw_stage=sha(x.raw_stage))
        write(x.private/"commitment.json",commitment)
        editor=x.dest/"Assets/Editor/PrivateLightImport.cs"
        helper=Path(__file__).with_name("FreshLightImport.cs").read_text()
        editor.write_text(compose_editor(editor.read_text(),helper))
        (editor.parent/"FreshLightImport.cs").write_text(helper)
        result.update(status=STAGE,source_scene_sha256=prior.SOURCE_SHA,selected_objects=42,same_export_checks=108,
                      historical_scene_digest_match=historical[0],historical_meta_digest_match=historical[1],
                      historical_exact_prior_replay_claimed=False,current_scene_sha256=hashes["PrivateScene.unity"],
                      current_meta_sha256=hashes["PrivateScene.unity.meta"],current_same_instance_commitment_sha256=sha(x.private/"commitment.json"),
                      world_rows_prepared=3,private_scene_withheld_before_guard=True,full_scene_provider_closure_proven=False)
    except Rejected as exc:result["reason"]=str(exc)
    except Exception as exc:result["reason"]=type(exc).__name__
    write(x.report,result);print("GT_LIGHT_FRESH_EDITOR_STAGE "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STAGE else 2

def validate_world_receipt(r,run_id,commit):
    require(type(r) is dict and set(r)=={"run_id","commitment_sha256","private_guard","world_rows","world_checks","world_mismatches",
                                        "light_owner_match","light_active_match","status"} and r["run_id"]==run_id and
            r["commitment_sha256"]==commit and r["private_guard"] is True,"fresh_world_receipt_identity")
    require(type(r["world_rows"]) is int and r["world_rows"]==3 and type(r["world_checks"]) is int and r["world_checks"]==12 and
            type(r["world_mismatches"]) is int and r["world_mismatches"]==0 and r["light_owner_match"] is True and
            r["light_active_match"] is True and r["status"]=="PASS","fresh_world_hierarchy_unproven")
    return True

def verify(x):
    result=dict(status="INCONCLUSIVE",Unity_import_verified=False,world_transform_verified=False,player_built=False,
                XAPK=False,device_pixels_proven=False,full_scene_provider_closure_proven=False,historical_exact_prior_replay_claimed=False)
    try:
        s=json.loads(x.raw_stage.read_text());historical=validate_fresh_stage(s)
        stage=json.loads(x.stage_report.read_text());p=x.private
        commit=sha(p/"commitment.json");doc=json.loads((p/"commitment.json").read_text())
        require(stage["status"]==STAGE and commit==stage["current_same_instance_commitment_sha256"] and
                run_token(x.run_id) and doc["run_id"]==x.run_id and sha(x.same_export)==doc["same_export"] and
                sha(x.raw_stage)==doc["raw_stage"] and doc["scene"]==s["scene_sha256"] and doc["meta"]==s["scene_meta_sha256"],
                "fresh_commitment_drift")
        prior.validate_same_export(json.loads(x.same_export.read_text()))
        require((p/"editor-output-private").read_text().strip()==x.run_id and (p/"editor.log").is_file(),"fresh_private_log_guard")
        for name,key in (("PrivateScene.unity","scene"),("PrivateScene.unity.meta","meta"),("expected-private.json","expected"),("expected-world.json","world")):
            require(sha(p/name)==doc[key],"fresh_private_input_changed")
        require(sha(x.dest/"expected-private.json")==doc["expected"],"fresh_editor_manifest_drift")
        old.verify(x.dest,x.raw_stage,x.outcome,x.raw_import)
        raw=json.loads(x.raw_import.read_text());result["current_import_receipt"]=raw
        require(prior.validate_editor(raw),"fresh_154_editor_checks_unproven")
        r=json.loads((p/"world-safe.json").read_text());result["world_receipt"]=r
        validate_world_receipt(r,x.run_id,commit)
        result.update(status=STATUS,Unity_import_verified=True,matched_objects=42,exact_editor_checks=154,
                      world_transform_verified=True,world_matrix_rows=3,world_checks=12,light_owner_active_checks=2,
                      historical_scene_digest_match=historical[0],historical_meta_digest_match=historical[1],
                      current_scene_and_meta_unchanged=True,original_scene_sha256=prior.SOURCE_SHA)
    except Rejected as exc:result["reason"]=str(exc)
    except Exception as exc:result["reason"]=type(exc).__name__
    write(x.report,result);print("GT_LIGHT_FRESH_EDITOR_IMPORT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest="action",required=True)
    st=sub.add_parser("stage")
    for k in ("source","project","trace","w1","b02","dest","private","same-export","raw-stage","report"):
        st.add_argument("--"+k,type=Path,required=True)
    v=sub.add_parser("verify")
    for k in ("dest","private","same-export","stage-report","raw-stage","raw-import","report"):
        v.add_argument("--"+k,type=Path,required=True)
    for q in (st,v):q.add_argument("--run-id",required=True)
    v.add_argument("--outcome",required=True)
    x=p.parse_args();return stage(x) if x.action=="stage" else verify(x)
if __name__=="__main__":raise SystemExit(main())
