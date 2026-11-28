"""Stage byte-identical private scene and meta only, no other game assets."""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
from tools.gt_light_same_export import audit as a

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stage(source,project,trace,w1,b02,dest,report):
    import UnityPy
    size,digest,blob=a.PINS[a.SCENE]
    path=source/"Raft_Data"/a.SCENE
    a.require(a.hash_file(path,size,blob)==digest,"staged_scene_hash")
    with open(os.devnull,"w") as quiet,contextlib.redirect_stdout(quiet),contextlib.redirect_stderr(quiet):
        env=UnityPy.load(str(path))
        model=a.source_model(list(env.file.objects.values()))
    m=a.trace_map(model,*[a.read_trace(x) for x in (trace,w1,b02)])
    guid=next(iter(m.values()))[0]
    docs=a.yaml_docs(project,guid,{k[1] for k in m.values()})
    res=a.compare(model,m,docs)
    a.require(res["same_export_hierarchy_parity"],"same_export_not_pass")
    hits=[p for p in (project/"Assets").rglob("*.meta") if guid in [x.lower() for x in a.META_GUID.findall(p.read_text(encoding="utf-8-sig"))]]
    a.require(len(hits)==1,"scene_meta_identity")
    meta=hits[0]
    scene=Path(str(meta)[:-5])
    a.require(not dest.exists(),"private_project_exists")
    (dest/"Assets/Editor").mkdir(parents=True)
    (dest/"ProjectSettings").mkdir()
    (dest/"Packages").mkdir()
    target=dest/"Assets/PrivateScene.unity"
    targetmeta=Path(str(target)+".meta")
    shutil.copyfile(scene,target); shutil.copyfile(meta,targetmeta)
    a.require(sha(scene)==sha(target) and sha(meta)==sha(targetmeta),"private_scene_copy_drift")
    shutil.copyfile(Path(__file__).with_name("PrivateLightImport.cs"),dest/"Assets/Editor/PrivateLightImport.cs")
    (dest/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
    (dest/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
    def tid(i):
        return "0" if i is None else str(m[i][1])
    nodes=[]
    for i,s in model.items():
        v={"id":tid(i),"cid":s["class"],"hasOwner":"owner" in s,"hasParent":"parent" in s,
           "hasChildren":"children" in s,"hasActive":"active" in s,"hasTRS":"trs" in s,"hasLight":"fields" in s}
        if v["hasOwner"]:v["owner"]=tid(s["owner"])
        if v["hasParent"]:v["parent"]=tid(s["parent"])
        if v["hasChildren"]:v["children"]=[tid(x) for x in s["children"]]
        if v["hasActive"]:v.update(active=s["active"],components=[tid(x) for x in s["components"]])
        if v["hasTRS"]:v.update(position=s["trs"]["m_LocalPosition"],rotation=s["trs"]["m_LocalRotation"],scale=s["trs"]["m_LocalScale"])
        if v["hasLight"]:
            l=s["fields"];v.update(enabled=l["m_Enabled"],lightType=l["m_Type"],color=l["m_Color"],intensity=l["m_Intensity"],range=l["m_Range"])
        nodes.append(v)
    (dest/"expected-private.json").write_text(json.dumps({"guid":guid,"nodes":nodes}))
    safe={"scene_sha256":sha(target),"scene_meta_sha256":sha(targetmeta),"same_export_scene_copy_exact":True,
          "selected_objects":len(nodes),"source_scene_sha256":digest,"other_original_assets_staged":0,
          "scene_dependency_closure_claimed":False,"import_executed":False}
    report.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n")
    print("GT_LIGHT_PRIVATE_IMPORT_STAGED "+json.dumps(safe,sort_keys=True))

def verify(dest,stage_report,outcome,report):
    s=json.loads(stage_report.read_text())
    out={"stage":s,"editor_step_outcome":outcome,"Unity_import_verified":False,"player_built":False,"XAPK":False}
    try:
        path=dest/"import-safe.json"
        a.require(path.is_file() and path.stat().st_size<=65536,"no_bounded_editor_report")
        raw=json.loads(path.read_text())
        allowed={"status","sceneOpened","sceneGuidMatched","matchedObjects","checks","mismatches","mismatchCategories"}
        a.require(set(raw)==allowed and isinstance(raw["mismatchCategories"],list),"editor_report_schema")
        categories={"identity","native_class","component_owner","parent","ordered_children","activeSelf","activeInHierarchy","component_membership","local_position","local_rotation","local_scale","enabled","isActiveAndEnabled","light_type","light_color","light_intensity","light_range","editor_exception"}
        a.require(all(isinstance(x,str) and x in categories for x in raw["mismatchCategories"]),"editor_report_category")
        for k in ("matchedObjects","checks","mismatches"):a.require(type(raw[k]) is int and 0<=raw[k]<=100000,"editor_report_count")
        a.require(raw["status"] in ("PASS","FAIL","INCONCLUSIVE") and type(raw["sceneOpened"]) is bool and type(raw["sceneGuidMatched"]) is bool,"editor_report_status")
        out["editor_report"]=raw
        exact=sha(dest/"Assets/PrivateScene.unity")==s["scene_sha256"] and sha(dest/"Assets/PrivateScene.unity.meta")==s["scene_meta_sha256"]
        out["scene_and_meta_unchanged_after_import"]=exact
        passed=outcome=="success" and raw["status"]=="PASS" and raw["sceneOpened"] and raw["sceneGuidMatched"] and raw["matchedObjects"]==s["selected_objects"] and raw["checks"]>=s["selected_objects"] and raw["mismatches"]==0 and not raw["mismatchCategories"] and exact
        out["Unity_import_verified"]=passed
        out["status"]="PASS_ISOLATED_IMPORT" if passed else "INCONCLUSIVE_OR_DRIFT"
    except a.Rejected as e:
        out.update(status="INCONCLUSIVE",reason=str(e))
    except Exception as e:
        out.update(status="INCONCLUSIVE",reason=type(e).__name__)
    report.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("GT_LIGHT_ISOLATED_IMPORT "+json.dumps(out,sort_keys=True,separators=(",",":")))
    return 0 if out["Unity_import_verified"] else 2

if __name__=="__main__":
    p=argparse.ArgumentParser()
    s=p.add_subparsers(dest="cmd",required=True)
    st=s.add_parser("stage")
    for k in ("source","project","trace","w1","b02","dest","report"):st.add_argument("--"+k,type=Path,required=True)
    v=s.add_parser("verify")
    for k in ("dest","stage-report","report"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--outcome",required=True)
    x=p.parse_args()
    if x.cmd=="stage":stage(x.source,x.project,x.trace,x.w1,x.b02,x.dest,x.report)
    else:raise SystemExit(verify(x.dest,x.stage_report,x.outcome,x.report))
