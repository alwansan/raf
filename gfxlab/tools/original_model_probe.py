#!/usr/bin/env python3
"""GFX-LAB original ZIP2 model discovery + bounded OBJ extraction.
Does not publish original Unity identifiers, names, serialized data or geometry.
Requires separately SHA-pinned, read-only source providers.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

ZIP2_SHA = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
OWNERS = {
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
    "sharedassets6.assets": (6607272, "0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632"),
}
WORD_WEIGHTS = {"player":1000,"survivor":850,"character":500,"human":400,"body":180,"male":140,"female":140,"avatar":100,"person":100,"hand":30,"head":30}
MAX_BYTES = 20_000_000
MAX_PARTS = 8

def sha_size(path: Path):
    h=hashlib.sha256()
    n=0
    with path.open("rb") as f:
        while block:=f.read(2*1024*1024):
            n+=len(block); h.update(block)
    return n,h.hexdigest()

def assert_plain(path: Path, root: Path):
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Input/output path escapes trusted root")
    if path.is_symlink() or any(p.is_symlink() for p in path.parents if p!=root.parent):
        raise ValueError("Redirected source file")

def read_manifest(root: Path):
    p=root/"RAFT_FILE_MANIFEST.tsv"
    assert_plain(p,root)
    with p.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f,delimiter="\t")
        if reader.fieldnames!=["kind","bytes","sha256","mode","relative_path_under_Raft"]:
            raise ValueError("Unexpected original manifest schema")
        return {r["relative_path_under_Raft"]:r for r in reader}

def stage_originals(root: Path, destination: Path):
    import os
    if destination.resolve().is_relative_to(root.resolve()):
        raise ValueError("Output inside original provider")
    manifest=read_manifest(root)
    dest=destination/"Raft_Data"
    dest.mkdir(parents=True,exist_ok=True)
    for name,(size,digest) in OWNERS.items():
        rel="Raft_Data/"+name
        meta=manifest.get(rel)
        if not meta or int(meta["bytes"])!=size or meta["sha256"]!=digest:
            raise ValueError("Original manifest does not match independent SHA pin")
        p=root/"Raft"/rel
        assert_plain(p,root)
        if meta["kind"]=="split":
            if not p.is_dir():raise ValueError("Split provider absent")
            parts=sorted(x for x in p.iterdir() if x.name.startswith("part-"))
            if not parts or [x.name for x in parts] != ["part-%05d"%i for i in range(len(parts))]:
                raise ValueError("Noncontiguous ZIP2 part names")
            if any(x.is_symlink() or not x.is_file() for x in parts):raise ValueError("Unsafe split part")
            if sorted(x.name for x in p.iterdir() if x.name!="README.txt")!=[x.name for x in parts]:
                raise ValueError("Unexpected split content")
        elif meta["kind"]=="plain":
            if not p.is_file():raise ValueError("Plain provider absent")
            parts=[p]
        else:raise ValueError("Unknown source encoding")
        out=dest/name
        if not out.exists():
            with out.open("xb") as f:
                for part in parts:
                    with part.open("rb") as g:
                        while blob:=g.read(2*1024*1024):
                            f.write(blob)
        if sha_size(out)!=(size,digest):
            out.unlink(missing_ok=True)
            raise ValueError("Original bytes differ from pinned file")
    return dest

def ptr(d):
    if not isinstance(d,dict):return None
    a=d.get("m_FileID",d.get("fileID",0));b=d.get("m_PathID",d.get("pathID",0))
    return (a,b) if isinstance(a,int) and isinstance(b,int) else None

def name_score(s):
    s=s.lower()
    return sum(w for word,w in WORD_WEIGHTS.items() if word in s)

def inspect_owner(path: Path):
    import UnityPy
    env=UnityPy.load(str(path))
    names={}
    transforms={}
    meshes={}
    skins=[]
    filters=[]
    counters={"gameobjects":0,"skinned_renderers":0,"mesh_filters":0,"mesh_objects":0,"parse_errors":0}
    for obj in env.objects:
        typ=obj.type.name
        if typ not in {"GameObject","Transform","SkinnedMeshRenderer","MeshFilter","Mesh"}:continue
        try:
            if typ=="Mesh":
                meshes[obj.path_id]=obj;counters["mesh_objects"]+=1
                continue
            d=obj.read_typetree()
            if typ=="GameObject":
                counters["gameobjects"]+=1
                names[obj.path_id]=str(d.get("m_Name",""))
            elif typ=="Transform":
                g=ptr(d.get("m_GameObject")); f=ptr(d.get("m_Father"))
                if g and g[0]==0:transforms[obj.path_id]=(g[1],f[1] if f and f[0]==0 else None)
            elif typ=="SkinnedMeshRenderer":
                counters["skinned_renderers"]+=1
                g=ptr(d.get("m_GameObject"));m=ptr(d.get("m_Mesh"))
                if g and m and g[0]==0:skins.append((g[1],m))
            elif typ=="MeshFilter":
                counters["mesh_filters"]+=1
                g=ptr(d.get("m_GameObject"));m=ptr(d.get("m_Mesh"))
                if g and m and g[0]==0:filters.append((g[1],m))
        except Exception:
            counters["parse_errors"]+=1
    parents={}
    for transform_id,(game_id,father_id) in transforms.items():
        parents[game_id]=transforms.get(father_id,(None,None))[0]
    def lineage(gameid):
        path=[];seen=set();cur=gameid
        while cur is not None and cur not in seen and len(path)<20:
            seen.add(cur);path.append(names.get(cur,""));cur=parents.get(cur)
        return path
    candidates=[]
    for kind,rs in (("skinned",skins),("static",filters)):
        for go,meshptr in rs:
            fileid,mid=meshptr
            if fileid!=0 or mid not in meshes:continue
            labels=lineage(go)
            score=max([name_score(s) for s in labels] or [0])
            if kind=="skinned":score+=90
            candidates.append((score,kind,go,mid))
    candidates.sort(key=lambda r:(-r[0],r[3]))
    counters["same_owner_mesh_links"]=len(candidates)
    counters["player_like_same_owner_mesh_links"]=sum(1 for c in candidates if c[0]>=500)
    return meshes,candidates,counters

def export_one(mesh_object):
    mesh=mesh_object.parse_as_object()
    data=mesh.export()
    if not isinstance(data,str) or not data.startswith(("#","v ","o ","g ")):
        raise ValueError("Invalid OBJ export")
    # Fail closed for empty geometry, no faces, oversized assets.
    verts=sum(line.startswith("v ") for line in data.splitlines())
    faces=sum(line.startswith("f ") for line in data.splitlines())
    if not (16<=verts<=300000 and faces>0) or len(data.encode("utf-8"))>MAX_BYTES:
        raise ValueError("Invalid/oversized mesh topology")
    return data,verts,faces

def discover(source: Path, output: Path, require_player=False):
    output.mkdir(parents=True,exist_ok=True)
    safe={"schema":1,"source_pinned":True,"providers":0,"owners_parsed":0,"original_mesh_objects":0,
          "candidate_skinned_links":0,"candidate_player_like_links":0,"parse_errors":0,
          "export_attempts":0,"export_failures":0,"model_category":"unavailable","part_count":0,
          "vertices":0,"faces":0,"original_geometry_exported":False,"unity_import_tested":False,
          "android_device_tested":False}
    available=[]
    for owner in OWNERS:
        p=source/owner
        if sha_size(p)!=OWNERS[owner]:raise ValueError("Changed source before selection")
        safe["providers"]+=1
        meshes,candidates,counters=inspect_owner(p)
        safe["owners_parsed"]+=1
        safe["original_mesh_objects"]+=counters["mesh_objects"]
        safe["candidate_skinned_links"]+=sum(1 for c in candidates if c[1]=="skinned")
        safe["candidate_player_like_links"]+=counters["player_like_same_owner_mesh_links"]
        safe["parse_errors"]+=counters["parse_errors"]
        available.append((owner,meshes,candidates))
    # Prefer a person-like original skinned renderer and a small coherent set;
    # otherwise only a distinctly named generic ORIGINAL asset, never a fake player.
    ranked=[]
    for owner,meshes,cands in available:
        for score,kind,go,mid in cands:
            ranked.append((score,kind,owner,go,mid,meshes[mid]))
    ranked.sort(key=lambda r:(-r[0],r[2],r[4]))
    if require_player:
        ranked=[r for r in ranked if r[0]>=500 and r[1]=="skinned"]
    if not ranked:
        safe["reason"]="no_same_owner_mesh_candidate"
    else:
        primary=ranked[0]
        main_score,main_kind,main_owner,main_go=primary[:4]
        if main_score>=500 and main_kind=="skinned":
            chosen=[x for x in ranked if x[2]==main_owner and x[3]==main_go and x[1]=="skinned"]
            chosen=chosen[:MAX_PARTS] or [primary]
            safe["model_category"]="original_player_like_skinned"
        else:
            chosen=[primary]
            safe["model_category"]="original_generic_static" if main_kind=="static" else "original_generic_skinned"
        if require_player and safe["model_category"]!="original_player_like_skinned":
            raise ValueError("Player-like skinned candidate absent")
        for _,_,_,_,_,reader in chosen:
            safe["export_attempts"]+=1
            try:
                data,v,f=export_one(reader)
                target=output/("Part%02d.obj"%safe["part_count"])
                target.write_text(data,encoding="utf-8",newline="")
                safe["part_count"]+=1;safe["vertices"]+=v;safe["faces"]+=f
            except Exception:
                safe["export_failures"]+=1
        safe["original_geometry_exported"]=safe["part_count"]>0
        if not safe["original_geometry_exported"]:
            safe["reason"]="selected_model_geometry_unexportable_or_requires_stream"
    return safe

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--model-output",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--require-player",action="store_true")
    args=ap.parse_args()
    stage=stage_originals(args.zip2,args.stage)
    result=discover(stage,args.model_output,args.require_player)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    # Only numbers/categories. Never publish source names, GUIDs, or original geometry.
    print("GFX_LAB_ORIGINAL_MODEL "+json.dumps(result,sort_keys=True))
    if not result["original_geometry_exported"]:raise SystemExit(2)

if __name__=="__main__":main()
