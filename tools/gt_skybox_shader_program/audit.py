"""Exact previously-proven original Skybox Material -> Shader48 -> actual export.
Only safe counts, SHA commitments and schema/gap categories leave the runner.
No shader synthesis, original mutation, build, editor or raw program publication.
"""
import argparse
import contextlib
import csv
import hashlib
import json
import os
from pathlib import Path
import re
from tools.gt_ambient_same_export import audit as a
from tools.gt_skybox_exact_provider import resolve as r
from tools.gt_remaining_scene_lighting.audit import kind,tree,hash_file
from tools.gt_light_same_export.audit import require,Rejected
from scripts.w1_stage_zip2_owners import ZIP2_SHA,stage,fingerprint,safe
from scripts.verify_export_lineage import identity,pointer,actual_graph
from scripts.w1_audit_export_material_shaders import ENGINE
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.w1_recover_graphics_programs import decoded_platforms,records
from scripts.w1_recover_depth_passes import linked_program,stage_variants
from scripts.b44_verify_material_colors import normalize_colors
from scripts.b22_verify_material_scalars import normalize as normalize_scalars
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs

BUILTINS={
    "Resources/unity default resources":{"kind":"plain","bytes":4832808,"sha256":"026e6d1d96dc2e28c72ece25f2419469d649a95e25b6929bc5cfc95bca529f8e","git_object":"777ccb2db0b4d5957cc6d4e4ac95e202f84ab716"},
    "Resources/unity_builtin_extra":{"kind":"plain","bytes":936628,"sha256":"0eb8f0a4ea47b075a6b637abc02d0c7930d96cb9f6c5d723819eb8042cfb3886","git_object":"b949c9ade5bdf6b489d5bb01c8f8542c9ec24195"},
}
KEYWORDS=("m_ValidKeywords","m_InvalidKeywords","disabledShaderPasses")
SKY_OWNER="sharedassets0.assets"

def catalog():
    return {**r.catalog(),**BUILTINS}

def source_target(owner,external,raw,rows):
    p=a.source_pointer(raw)
    require(p is not None,"original_shader_null")
    f,i=p
    if f==0:return owner,i
    require(isinstance(external,(list,tuple)) and f<=len(external),"shader_external_slot_missing")
    raw=getattr(external[f-1],"path",None)
    require(isinstance(raw,str) and 0<len(raw)<=4096 and not any(ord(c)<32 or ord(c)==127 for c in raw),"shader_external_schema")
    n=raw.replace("\\","/").rsplit("/",1)[-1]
    if "Resources/"+n in BUILTINS:n="Resources/"+n
    require(n in rows,"shader_provider_outside_catalog")
    return n,i

def private_material(root,sky):
    import UnityPy
    r.verify_typed(root,sky)
    owner,i=r.selection(root)
    require(owner==SKY_OWNER and sky["provider"]==owner,"prior_skybox_identity_changed")
    env=UnityPy.load(str(root/owner))
    obj=env.file.objects[i]
    body=tree(obj)
    require(kind(obj)==("Material",21) and body is not None,"original_skybox_material_untyped")
    target=source_target(owner,env.file.externals,body.get("m_Shader"),catalog())
    return (owner,i),body,target

def discover(root,sky):
    with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
        _,_,(owner,_)=private_material(root,sky)
    p=catalog()[owner]
    present=owner in a.PINS or owner==SKY_OWNER
    paths=[] if present else ["/Raft/Raft_Data/"+owner] if p["kind"]=="plain" else ["/Raft/Raft_Data/"+owner+"/"+x["name"] for x in p["parts"]]
    return {"source_commit":ZIP2_SHA,"manifest_blob":a.MANIFEST,"provider":owner,"pin":p,"already_staged":present,"sparse_paths":paths}

def authenticate_extra(source,root,plan):
    r.authenticate_manifest(source)
    p=plan["pin"];name=plan["provider"]
    m=source/"RAFT_FILE_MANIFEST.tsv"
    with m.open(newline="") as f:rows=list(csv.DictReader(f,delimiter="\t"))
    matches=[x for x in rows if x["relative_path_under_Raft"]=="Raft_Data/"+name]
    require(len(matches)==1 and (matches[0]["kind"],matches[0]["bytes"],matches[0]["sha256"])==(p["kind"],str(p["bytes"]),p["sha256"]),"shader_provider_manifest_mismatch")
    r.verify_payload(source,plan)
    result=stage(source,root.parent,{"Raft_Data/"+name:(p["bytes"],p["sha256"])})
    require(result["verified_bytes"]==p["bytes"] and not result["lfs_used"],"shader_provider_stage")

def source_shader(root,sky,plan):
    import UnityPy
    require(discover(root,sky)==plan,"shader_provider_plan_changed")
    with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
        mat,body,target=private_material(root,sky)
        owner,i=target
        path=root/owner; safe(path)
        p=plan["pin"]
        require(fingerprint(path)==(p["bytes"],p["sha256"]),"source_shader_provider_digest")
        env=UnityPy.load(str(path))
        obj=env.file.objects.get(i)
        require(obj is not None and kind(obj)==("Shader",48),"source_shader_target_not_class48")
        sh=tree(obj)
        require(sh is not None,"source_shader_typetree_unavailable")
        digest=hashlib.sha256(obj.get_raw_data()).hexdigest()
    return mat,body,target,sh,digest

def source_programs(sh):
    result={"source_subshaders":0,"source_passes":0,"vertex_slots":0,"fragment_slots":0,"other_stage_slots":0,
            "source_d3d11_table_count":0,"linked_d3d11_stage_slots":0,"distinct_linked_dxbc":0,
            "unlinked_d3d11_stage_slots":0,"source_program_schema_complete":False}
    parsed=sh.get("m_ParsedForm")
    subs=parsed.get("m_SubShaders") if isinstance(parsed,dict) else None
    if not isinstance(subs,list) or not subs:
        result["reason"]="missing_original_subshader_graph"
        return result
    result["source_subshaders"]=len(subs)
    allvars=[]
    try:
        require(len(subs)<=128,"source_subshader_budget")
        for sub in subs:
            passes=sub.get("m_Passes")
            require(isinstance(passes,list),"source_pass_schema")
            result["source_passes"]+=len(passes)
            require(result["source_passes"]<=256,"source_pass_budget")
            for p in passes:
                require(isinstance(p,dict),"source_pass_schema")
                for key,stage_code,field in (("progVertex",1,"vertex_slots"),("progFragment",0,"fragment_slots"),
                   ("progGeometry",2,"other_stage_slots"),("progHull",3,"other_stage_slots"),("progDomain",4,"other_stage_slots")):
                    prog=p.get(key)
                    if prog is None:
                        require(key not in ("progVertex","progFragment"),"source_stage_schema")
                        continue
                    require(isinstance(prog,dict),"source_stage_schema")
                    vs=stage_variants(prog)
                    result[field]+=len(vs)
                    require(sum(result[k] for k in ("vertex_slots","fragment_slots","other_stage_slots"))<=4096,"source_variant_budget")
                    if stage_code in (0,1):allvars.extend((v[2],stage_code) for v in vs)
        result["source_program_schema_complete"]=True
    except Exception as e:
        result["reason"]=str(e) if isinstance(e,Rejected) else "source_stage_schema_unresolved"
        return result
    if not allvars:return result
    try:
        tables=[records(s) for p,s in decoded_platforms(sh) if p==4]
        result["source_d3d11_table_count"]=len(tables)
        if len(tables)!=1:
            result["reason"]="source_d3d11_table_unavailable_or_ambiguous";return result
        hashes=set()
        for meta,st in allvars:
            try:
                code,_=linked_program(meta,tables[0],st)
                hashes.add(hashlib.sha256(code).hexdigest())
                result["linked_d3d11_stage_slots"]+=1
            except Exception:
                result["unlinked_d3d11_stage_slots"]+=1
        result["distinct_linked_dxbc"]=len(hashes)
    except Exception:
        result["reason"]="source_d3d11_decode_unresolved"
    return result

def exact_row(w1,key,cid):
    rows=[x for x in w1["objects"] if x.get("class_id")==cid and identity(x["source"])==key]
    require(len(rows)==1,"selected_trace_identity_missing_or_duplicate")
    return rows[0]

def shader_pointer(x):
    if x is None:return None
    require(isinstance(x,dict) and set(x)=={"fileID","guid","type"},"shader_pointer_schema")
    f,g,t=pointer({"file_id":x["fileID"],"guid":x["guid"],"type":x["type"]})
    require((g in ENGINE and t=="0") or (g not in ENGINE and g!="0"*32 and t=="3" and f==4800000),"shader_pointer_transport")
    return f,g,t

def shader_trace_pointer(x):
    return shader_pointer({"fileID":x["file_id"],"guid":x["guid"],"type":x["type"]})

def classify_program(src,text):
    p=pass_coverage(text)
    dummy="//DummyShaderTextExporter" in text
    no_program="// No subprograms found" in text
    linked=src["linked_d3d11_stage_slots"]
    if dummy and linked>0:status="ORIGINAL_PROGRAMS_PRESENT_EXPORTED_DUMMY"
    elif dummy:status="EXPORTED_DUMMY_SOURCE_PROGRAM_AVAILABILITY_UNRESOLVED"
    elif not p["all_subshaders_programmed"]:status="EXPORTED_STRUCTURE_INCOMPLETE"
    else:status="NON_DUMMY_STRUCTURE_ONLY"
    return {"status":status,"dummy_marker":dummy,"no_subprograms_marker":no_program,
            "unknown_exporter_marker":"ShaderUnknownExporter" in text,**p,"program_authenticity_proven":False}

def map_counts(x,y,eq=lambda a,b:a==b):
    common=set(x)&set(y)
    return {"source":len(x),"export":len(y),"equal":sum(eq(x[k],y[k]) for k in common),
            "changed":sum(not eq(x[k],y[k]) for k in common),"missing":len(set(x)-set(y)),"extra":len(set(y)-set(x))}

def properties(s,d):
    out={}
    def attempt(label,fn):
        try:out[label]=fn()
        except Exception:out[label]={"status":"UNKNOWN_SCHEMA"}
    src=s.get("m_SavedProperties");dst=d.get("m_SavedProperties")
    attempt("colors",lambda:map_counts(normalize_colors(src["m_Colors"]),normalize_colors(dst["m_Colors"],exported=True),a.close))
    def scalars():
        left=normalize_scalars(src);right=dict(dst)
        for k in ("m_Floats","m_Ints"):
            if isinstance(right.get(k),dict):right[k]=list(right[k].items())
        right=normalize_scalars(right,exported=True)
        return {k:map_counts(left[k],right[k]) for k in left}
    attempt("scalars",scalars)
    def tex():
        x=normalize_texenvs(src["m_TexEnvs"]);y=normalize_texenvs(dst["m_TexEnvs"],exported=True)
        uv=map_counts(x,y,lambda a1,b1:a1[1] is not None and b1[1] is not None and a.close(a1[1],b1[1]))
        return {"uv":uv,"nullness":map_counts(x,y,lambda a1,b1:(a1[0][1]==0)==(b1[0][0]==0)),
                "texture_identity_or_pixels_proven":False}
    attempt("texenvs",tex)
    for key in KEYWORDS:
        def keyword(k=key):
            x,y=s[k],d[k]
            require(isinstance(x,list) and isinstance(y,list) and all(isinstance(v,str) for v in x+y),"keyword_schema")
            return {"source":len(x),"export":len(y),"equal":sorted(x)==sorted(y)}
        attempt(key,keyword)
    return out

def scoped_fanout(w1,key,expected,project):
    rows=[x for x in w1["objects"] if x.get("class_id")==21 and x.get("shader_source") is not None and identity(x["shader_source"])==key]
    count=0
    try:
        actual=actual_graph(project)
        # Actual graph keys are (local fileID, asset GUID, reference type), not names.
        docs={(k[0],k[1]):v for k,v in actual.items()}
        seen=set()
        for row in rows:
            if row.get("exportable") is not True:continue
            p=pointer(row["export"]); k=(p[0],p[1])
            require(k not in seen,"fanout_material_pointer_collapsed")
            seen.add(k)
            if docs.get(k)==expected and pointer(row["shader_export"])==expected:count+=1
        return {"same_instance_trace_material_rows":len(rows),"unique_actual_material_documents_matching_shader":count,
                "full_original_project_fanout_proven":False}
    except Exception:
        return {"same_instance_trace_material_rows":len(rows),"status":"UNKNOWN_ACTUAL_FANOUT"}

def compare(x,root,sky,plan):
    report={"source_commit":ZIP2_SHA,"selected_shader_provider":plan["provider"],"same_export_shader_pointer_proven":False,
            "full_scene_provider_closure_proven":False,"shader_installed":False,"Unity_import_verified":False,
            "device_pixels_proven":False,"original_assets_mutated":False,"original_assets_published":False,"XAPK":False}
    phase="source"
    try:
        mat,body,target,sh,digest=source_shader(root,sky,plan)
        report["source_shader_object_sha256"]=digest
        report["typed_source_shader48"]=True
        with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
            src=source_programs(sh)
        report["source_programs"]=src
        phase="trace"
        st,w1,b02=[a.read_trace(p) for p in (x.trace,x.w1,x.b02)]
        a.same_instance(st,w1,b02)
        # Keep native scene -> Material identity as prerequisite, not a repeated standalone audit.
        with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
            _,sid,_=a.read_source(root)
        scene_guid,scene_fid,_=a.settings_mapping(st,w1,b02,sid)
        scene=a.doc_body(a.file_for_guid(x.project,scene_guid,{".unity"}),104,scene_fid,"RenderSettings")
        mptr=a.material_mapping(w1,*mat)
        require(a.export_pointer(scene.get("m_SkyboxMaterial"))==mptr,"skybox_material_regression")
        material=a.doc_body(a.file_for_guid(x.project,mptr[0],{".mat",".asset"}),21,mptr[1],"Material")
        mr=exact_row(w1,mat,21)
        normalized=(Path(target[0]).name,target[1])
        sr=exact_row(w1,normalized,48)
        expected=shader_trace_pointer(sr["export"])
        require(identity(mr["shader_source"])==normalized,"material_shader_source_redirect")
        require(shader_trace_pointer(mr["shader_export"])==expected,"material_shader_trace_pointer_drift")
        peers=[q for q in w1["objects"] if q.get("class_id")==48 and q.get("export")==sr["export"]]
        require(expected[1] in ENGINE or len(peers)==1,"collapsed_shader_trace")
        phase="actual_shader"
        if expected[1] in ENGINE:
            require(target[0] in BUILTINS,"unexpected_engine_shader_redirect")
            program={"status":"ENGINE_TRANSPORT_ONLY","program_authenticity_proven":False}
        else:
            shader=a.file_for_guid(x.project,expected[1],{".shader"})
            require(shader.stat().st_size<=8*1024*1024,"shader_text_budget")
            meta=Path(str(shader)+".meta").read_text(encoding="utf-8-sig")
            require(re.search(r"(?m)^ShaderImporter:\s*$",meta) is not None,"actual_shader_importer_missing")
            program=classify_program(src,shader.read_text(encoding="utf-8-sig"))
            program["actual_shaderlab_meta_verified"]=True
        report["program"]=program
        phase="actual_material_shader_pointer"
        actual=shader_pointer(material.get("m_Shader"))
        report["same_export_shader_pointer_proven"]=actual==expected
        report["material_properties"]=properties(body,material)
        report["fanout"]=scoped_fanout(w1,normalized,expected,x.project)
        report["status"]="OBSERVED_SHADER_PROGRAM_GAP" if actual==expected and program["status"].startswith(("ORIGINAL_PROGRAMS_PRESENT_EXPORTED_DUMMY","EXPORTED_DUMMY","EXPORTED_STRUCTURE_INCOMPLETE")) else "PASS_SHADER_TRANSPORT_ONLY" if actual==expected else "FAIL_ACTUAL_SHADER_POINTER_DRIFT"
    except Exception as e:
        report.update(status="INCONCLUSIVE",phase=phase,reason=str(e) if isinstance(e,Rejected) else type(e).__name__)
    x.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_SHADER_SAME_EXPORT "+json.dumps(report,sort_keys=True,separators=(",",":")))
    # A demonstrated structural program gap is a useful result, not a restoration pass.
    return 0 if report["status"] in ("OBSERVED_SHADER_PROGRAM_GAP","PASS_SHADER_TRANSPORT_ONLY") else 2

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("discover","stage","compare"))
    for k in ("source","destination","skybox-plan","plan","report","project","trace","w1","b02"):
        p.add_argument("--"+k,type=Path)
    x=p.parse_args();root=x.destination/"Raft_Data"
    try:
        sky=json.loads(x.skybox_plan.read_text())
        if x.mode=="discover":
            plan=discover(root,sky)
            with x.plan.open("x") as f:json.dump(plan,f)
            with open(os.environ["GITHUB_OUTPUT"],"a") as f:
                f.write("needs_extra="+str(not plan["already_staged"]).lower()+"\n")
                if not plan["already_staged"]:f.write("paths<<GT_SHADER_PATHS\n/RAFT_FILE_MANIFEST.tsv\n"+"\n".join(plan["sparse_paths"])+"\nGT_SHADER_PATHS\n")
            r1={"status":"SELECTED_SHADER_PROVIDER","provider":plan["provider"],"already_staged":plan["already_staged"],"provider_bytes":plan["pin"]["bytes"],"provider_sha256":plan["pin"]["sha256"],"provider_git_object":plan["pin"]["git_object"]}
        else:
            plan=json.loads(x.plan.read_text())
            if x.mode=="compare":return compare(x,root,sky,plan)
            require(discover(root,sky)==plan,"shader_provider_plan_changed")
            if not plan["already_staged"]:authenticate_extra(x.source,root,plan)
            _,_,_,sh,digest=source_shader(root,sky,plan)
            r1={"status":"AUTHENTICATED_TYPED_SHADER48","provider":plan["provider"],"additional_provider_count":int(not plan["already_staged"]),
                "object_sha256":digest,"provider_bytes":plan["pin"]["bytes"],"provider_sha256":plan["pin"]["sha256"],"typed_source_shader48":True}
    except Exception as e:r1={"status":"INCONCLUSIVE","phase":x.mode,"reason":str(e) if isinstance(e,Rejected) else type(e).__name__}
    x.report.write_text(json.dumps(r1,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_SHADER_"+x.mode.upper()+" "+json.dumps(r1,sort_keys=True))
    return 2 if r1["status"]=="INCONCLUSIVE" else 0
if __name__=="__main__":raise SystemExit(main())
