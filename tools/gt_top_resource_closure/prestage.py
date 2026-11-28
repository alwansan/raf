"""Stage exact original selected resource providers BEFORE export.

Reproduce the previously accepted source selection within the original 12-owner
scope, then expand only referenced providers. No raw bytes or IDs in receipts.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess

from scripts import gt_zip2_payloads as zip2
from scripts import t3_original_renderer_shader_impact as impact
from scripts import gt_verify_original_mesh_export as mesh
from scripts import gt_particle108_source_pixel_parity as pixels
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from tools.gt_top_original_renderer import probe as previous
from tools.gt_top_resource_closure import probe as prior

CAP=4*1024**3
RESERVE=3*1024**3
TYPES={"Texture2D":28,"RenderTexture":84,"Cubemap":89,"Texture3D":117,"Texture2DArray":187}

def need(ok,reason):
    if not ok:
        raise prior.Blocked(reason)

def stream_name(path,offset,size):
    need(type(path) is str and type(offset) is int and type(size) is int and offset>=0 and size>=0,
         "invalid_resource_extent")
    if not size:
        need(not path and not offset,"ambiguous_empty_resource_extent")
        return None
    p=path.replace("\\","/")
    segments=p.split("/")
    need(all(seg and seg not in (".","..") for seg in segments) and
         (len(segments)==1 or segments[0]=="archive:"),"invalid_resource_path")
    name=segments[-1]
    need(re.fullmatch(r"[A-Za-z0-9_.-]+\.(?:resS|resource)",name) is not None,
         "invalid_resource_basename")
    return name

def exact_rel(owner):
    need(type(owner) is str and re.fullmatch(r"[A-Za-z0-9_.-]+",owner) and owner not in (".",".."),
         "invalid_selected_owner")
    return "Raft_Data/"+owner

def plan_budget(size,total,free):
    need(type(size) is int and size>0 and type(total) is int and 0<=total<=CAP,
         "invalid_provider_budget")
    need(total+size<=CAP,"selected_dependency_budget_exceeded")
    need(free>=2*size+RESERVE,"insufficient_private_disk_for_selected_dependency")

class Source(prior.Source):
    def __init__(self,a):
        super().__init__(a)
        self.extra=a.original.parent/"gt-top-private-streams"

    def acquire(self,name):
        rel=exact_rel(name)
        rec=self.records.get(rel)
        need(rec is not None and rec[1]>0,"selected_dependency_not_in_pinned_manifest")
        path=self.a.original/rel
        if path.is_file():
            need(zip2.fingerprint(path)==(rec[1],rec[2]),"existing_selected_dependency_not_original")
            return
        plan_budget(rec[1],self.total,shutil.disk_usage(self.a.original).free)
        pattern="/Raft/"+rel+("/*" if rec[0]=="split" else "")
        cp=subprocess.run(["git","-C",str(self.a.manifest.parent),"sparse-checkout","add","--no-cone","--",pattern],
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=600,check=False)
        need(cp.returncode==0,"selected_dependency_sparse_checkout_failed")
        zip2.stage(self.a.manifest.parent,self.extra,[rel],byte_budget=CAP)
        staged=self.extra/"Raft"/rel
        # Same runner filesystem. Exclusion rather than overwriting originals.
        os.link(staged,path)
        staged.unlink()
        need(zip2.fingerprint(path)==(rec[1],rec[2]),"staged_dependency_not_original")
        self.total+=rec[1]
        self.staged.add(rel)
        # Free verified source chunks before the next dependency. The local
        # immutable manifest and git identity stay available; original staged
        # providers are not affected.
        cp=subprocess.run(["git","-C",str(self.a.manifest.parent),"sparse-checkout","set","--no-cone","--","/RAFT_FILE_MANIFEST.tsv"],
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=300,check=False)
        need(cp.returncode==0,"private_dependency_checkout_cleanup_failed")

    def file(self,owner):
        import UnityPy
        rel=exact_rel(owner)
        if owner not in self.cache:
            self.acquire(owner)
            rec=self.records[rel]
            need(rec[1]<=pixels.MAX_PAYLOAD,"selected_serialized_owner_over_parser_budget")
            data=pixels.verified_range(self.a.original/rel,(rec[1],rec[2]),0,rec[1])
            self.cache[owner]=UnityPy.load(data).file
        return self.cache[owner]

    def stream(self,name):
        self.acquire(name)
        return self.a.original/"Raft_Data"

def original_choice(original,manifest):
    private={}
    report=impact.load_original(original,manifest,private_slot_counts=private)
    winners=[k for k,v in private.items() if v==921 and k[0] in impact.SHADER_OWNERS_SELECTED]
    need(report["original_highest_used_typed_Shader48_unique"] and len(winners)==1,
         "original_rank_one_source_drift")
    shader=winners[0]
    choices,c=previous.source_candidates(original,shader,source_only=True)
    need(len(choices)==855 and c["original_mesh_renderer_slots_to_top_shader"]==914
         and c["original_single_slot_mesh_renderers"]==898
         and c["mesh_provider_outside_stage_or_null"]==43,"original_scope_candidate_drift")
    freq=Counter(v[0] for v in choices)
    selected=min(choices,key=lambda v:(-freq[v[0]],v[0],v[1]))
    need(freq[selected[0]]==118 and len(previous.keywords(selected[3]))==3,
         "original_selected_material_drift")
    return shader,selected

def stream_extent(tree):
    raw=tree.get("m_StreamData")
    if raw is None:
        return None
    need(type(raw) is dict,"invalid_typed_resource_descriptor")
    return stream_name(raw.get("path"),raw.get("offset"),raw.get("size"))

def stage(a,report):
    shader,selected=original_choice(a.original,a.manifest)
    matkey,rkey,keys,_=selected
    source=Source(a)
    report["original_scope_candidates"]=855
    report["selected_material_eligible_renderers"]=118
    report["phase"]="stage_selected_mesh_provider"
    srcmesh=tuple(keys[3][1:])
    mt=source.obj(srcmesh,"Mesh").read_typetree(check_read=False)
    name,offset,size=mesh.source_stream_descriptor(mt["m_StreamData"])
    if size:
        rec=source.records.get(exact_rel(name))
        need(rec is not None and offset+size<=rec[1],"mesh_range_outside_pinned_provider")
        source.stream(name)
        report["selected_mesh_stream_provider_bytes"]=rec[1]
        report["selected_mesh_stream_range_bytes"]=size
    report["selected_mesh_stream_prepared"]=True
    report["phase"]="stage_selected_texture_dependencies"
    mat=source.obj(matkey,"Material").read_typetree(check_read=False)
    slots=normalize_texenvs(mat["m_SavedProperties"]["m_TexEnvs"])
    rows=Counter()
    plan_targets={}
    for prop,((fid,pid),uv) in sorted(slots.items()):
        if not pid:
            rows["null"]+=1
            continue
        rows["nonnull"]+=1
        try:
            key=source.resolve(matkey[0],{"m_FileID":fid,"m_PathID":pid})
            need(key is not None,"nonnull_source_texture_unresolved")
            obj=source.file(key[0]).objects.get(key[1])
            need(obj is not None and obj.type.name in TYPES,"unsupported_or_missing_source_texture_class")
            cls=TYPES[obj.type.name]
            rows["source_class_"+str(cls)]+=1
            # Retain the typed target even if its stream fails preparation.
            plan_targets[prop]={"key":list(key),"class":cls,"stream_ready":False}
            tree=obj.read_typetree(check_read=False)
            stream=stream_extent(tree)
            if stream:
                raw=tree["m_StreamData"]
                rec=source.records.get(exact_rel(stream))
                need(rec is not None and raw["offset"]+raw["size"]<=rec[1],
                     "texture_range_outside_pinned_provider")
                source.stream(stream)
                rows["stream_targets_prepared"]+=1
            else:
                rows["inline_or_nonstream_targets"]+=1
            plan_targets[prop]["stream_ready"]=True
        except Exception as exc:
            rows["blocked_"+prior.classify(exc)]+=1
    report["texture_dependency_counts"]=dict(rows)
    report["additional_providers_staged"]=len(source.staged)
    report["additional_provider_bytes"]=source.total
    report["all_nonnull_texture_sources_typed"]=sum(k.startswith("source_class_") and n or 0 for k,n in rows.items())==rows["nonnull"]
    report["all_selected_texture_dependencies_prepared"]=len(plan_targets)==rows["nonnull"] and all(v["stream_ready"] for v in plan_targets.values())
    plan={"schema_version":1,"shader":list(shader),"keys":[list(k) for k in keys],
          "material":list(matkey),"renderer":list(rkey),"mesh":list(srcmesh),
          "texture_targets":plan_targets,"added":sorted(source.staged)}
    with a.plan.open("x") as f:
        json.dump(plan,f)
    report["status"]="GT_TOP_EXACT_DEPENDENCY_PRESTAGED"
    report["phase"]="complete"

def main():
    p=argparse.ArgumentParser()
    for name in ("original","manifest","plan","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args()
    report={"status":"INCONCLUSIVE","phase":"original_selection","export_performed":False,
            "gpu_verified":False,"production":False,"XAPK":False}
    try:
        stage(a,report)
    except Exception as exc:
        report["failure_category"]=prior.classify(exc)
    with a.out.open("x") as f:
        json.dump(report,f,indent=2,sort_keys=True)
        f.write("\n")
    print("GT_TOP_EXACT_DEPENDENCY_PRESTAGE "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]=="GT_TOP_EXACT_DEPENDENCY_PRESTAGED" else 2

if __name__=="__main__":
    raise SystemExit(main())
