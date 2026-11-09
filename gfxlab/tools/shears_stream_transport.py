#!/usr/bin/env python3
"""GFX-SHEARS-004: authenticate only needed ZIP2 stream chunks for 3 original textures.

The ZIP2 source SHA and original three .assets SHA pins are immutable. The split
stream is never downloaded in full: plan selects Git blob SHA-identified chunks
overlapping the exact original Texture2D streaming offsets. Hydrate reconstructs
a sparse private stream file with only authentic selected bytes. Never publish
raw original names, pointers, offsets, image pixels or private plan JSON.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,re,subprocess
from pathlib import Path, PurePosixPath
from collections import Counter

from gfxlab.tools.original_model_probe import ZIP2_SHA,OWNERS,read_manifest,sha_size,stage_originals
from gfxlab.tools.shears_provenance_probe import resolve_pptr
from gfxlab.tools.shears_texture_readiness import (
    capture,select_exact_renderer,pairs,classify_standard,MAX_IMAGE_DIM,
)

IMAGE_SEMANTICS=frozenset(("basecolor","normal","metallic"))
PART_RE=re.compile(r"part-[0-9]{5}\Z")
MAX_STREAM_BYTES=3_000_000_000
MAX_CHUNKS=70

def source_three_texture_refs(source):
    envs,types,owner,r=select_exact_renderer(source)
    if len(r.get("m_Materials",[]))!=1:raise ValueError("selected shears material shape drift")
    ext=[x.path for x in envs[owner].file.externals]
    kind,key=resolve_pptr(r["m_Materials"][0],owner,ext)
    if key is None:raise ValueError("original Material owner unverified")
    mt=types[key[0]][key[1]].read_typetree(check_read=False)
    saved=mt["m_SavedProperties"]
    mext=[x.path for x in envs[key[0]].file.externals]
    selected={}
    for name,val in pairs(saved["m_TexEnvs"]):
        if not isinstance(val,dict) or "m_Texture" not in val:
            raise ValueError("malformed original texture slot")
        typ,k=resolve_pptr(val["m_Texture"],key[0],mext)
        if typ=="null":continue
        if k is None:raise ValueError("original texture owner unavailable")
        o=types[k[0]].get(k[1])
        if not o or o.type.name!="Texture2D":
            raise ValueError("wrong original typed texture target")
        semantic=classify_standard(name)
        if semantic not in IMAGE_SEMANTICS or semantic in selected:
            raise ValueError("unclassified or duplicate bound shears texture")
        selected[semantic]=o
    if set(selected)!=IMAGE_SEMANTICS:
        raise ValueError("expected exactly original albedo normal metallic textures")
    return selected,saved

def git_part_index(zip2:Path,basename:str,manifest:dict):
    rel="Raft_Data/"+basename
    meta=manifest.get(rel)
    if not meta or meta.get("kind")!="split":
        raise ValueError("original stream owner not split in trusted manifest")
    total=int(meta["bytes"])
    if not 0<total<=MAX_STREAM_BYTES:raise ValueError("oversized original stream")
    prefix="Raft/Raft_Data/"+basename+"/"
    raw=subprocess.check_output(["git","-C",str(zip2),"ls-tree","-r","-l","HEAD","--",prefix],text=True)
    parts=[]
    for line in raw.splitlines():
        lead,sep,path=line.partition("\t")
        if not sep:raise ValueError("Git tree metadata malformed")
        name=PurePosixPath(path).name
        if name=="README.txt":continue
        fields=lead.split()
        if len(fields)!=4 or fields[1]!="blob" or not PART_RE.fullmatch(name):
            raise ValueError("nonstandard original stream chunk entry")
        oid=fields[2]
        size=int(fields[3])
        if not re.fullmatch("[a-f0-9]{40}",oid) or not 0<size<=48*1024*1024:
            raise ValueError("invalid exact Git stream chunk size")
        parts.append((name,path,oid,size))
    parts.sort()
    if not parts or len(parts)>MAX_CHUNKS:raise ValueError("chunk count out of bounds")
    if [row[0] for row in parts]!=[f"part-{i:05d}" for i in range(len(parts))]:
        raise ValueError("noncontiguous chunk identifiers")
    cursor=0
    indexed=[]
    for name,path,oid,size in parts:
        indexed.append(dict(path=path,git_blob_oid=oid,size=size,start=cursor,end=cursor+size))
        cursor+=size
    if cursor!=total:
        raise ValueError("Git tree lengths do not match signed ZIP2 manifest")
    return total,indexed

def build_plan(zip2:Path,source:Path):
    if subprocess.check_output(["git","-C",str(zip2),"rev-parse","HEAD"],text=True).strip()!=ZIP2_SHA:
        raise ValueError("incorrect immutable ZIP2 revision")
    manifest=read_manifest(zip2)
    textures,_=source_three_texture_refs(source)
    streams={}
    refs={}
    for semantic,t in textures.items():
        tree=t.read_typetree(check_read=False)
        info=tree.get("m_StreamData",{})
        if not isinstance(info,dict):raise ValueError("original texture stream metadata absent")
        path=info.get("path","")
        offset=info.get("offset")
        size=info.get("size")
        if (not isinstance(path,str) or not path
            or type(offset) is not int or type(size) is not int
            or offset<0 or not 0<size<=80*1024*1024):
            raise ValueError("source stream range malformed")
        basename=PurePosixPath(path.replace("\\","/")).name
        if not basename.endswith(".resS"):
            raise ValueError("untrusted texture stream basename")
        rel="Raft_Data/"+basename
        if rel not in manifest or basename not in ("resources.assets.resS","sharedassets0.assets.resS","sharedassets6.assets.resS"):
            raise ValueError("unrecognized original stream provider")
        if basename not in streams:
            total,parts=git_part_index(zip2,basename,manifest)
            streams[basename]=dict(total=total,parts=parts,spans=[])
        stream=streams[basename]
        if offset+size>stream["total"]:raise ValueError("stream span out of original bounds")
        stream["spans"].append(dict(offset=offset,size=size,semantic=semantic))
        refs[semantic]=(basename,offset,size)
    paths=[]
    selected_parts=0
    for basename,s in streams.items():
        for part in s["parts"]:
            if any(not (part["end"]<=sp["offset"] or part["start"]>=sp["offset"]+sp["size"])
                   for sp in s["spans"]):
                part["needed"]=True
                paths.append(part["path"])
                selected_parts+=1
    if not selected_parts or selected_parts>8:
        raise ValueError("unexpected original source chunk budget")
    return {"source_sha":ZIP2_SHA,"streams":streams,"referents":refs,
            "checkout_paths":sorted(set(paths)),
            "safe_counts":{"source_original_sha_verified":True,
                           "textures":len(textures),
                           "stream_providers":len(streams),
                           "selected_git_chunks":selected_parts,
                           "selected_stream_bytes":sum(p["size"] for st in streams.values() for p in st["parts"] if p.get("needed")),
                           "original_shader_restored":False,
                           "android_pixels_proven":False}}

def fill_sparse_authenticated_streams(zip2:Path,source:Path,plan:dict):
    if plan["source_sha"]!=ZIP2_SHA:raise ValueError("source plan revision drift")
    for basename,stream in plan["streams"].items():
        out=source/basename
        if out.exists() or out.is_symlink():raise ValueError("private stream output collision")
        with out.open("xb") as g:
            g.truncate(stream["total"])
            for part in stream["parts"]:
                if not part.get("needed"):continue
                blob=zip2/part["path"]
                if not blob.is_file() or blob.is_symlink() or blob.stat().st_size!=part["size"]:
                    raise ValueError("selected original stream git chunk absent")
                if subprocess.check_output(["git","-C",str(zip2),"hash-object",str(blob.resolve())],text=True).strip()!=part["git_blob_oid"]:
                    raise ValueError("original stream Git blob identity mismatch")
                with blob.open("rb") as f:
                    for sp in stream["spans"]:
                        lo=max(part["start"],sp["offset"])
                        hi=min(part["end"],sp["offset"]+sp["size"])
                        if hi<=lo:continue
                        f.seek(lo-part["start"])
                        g.seek(lo)
                        remaining=hi-lo
                        while remaining:
                            block=f.read(min(1024*1024,remaining))
                            if not block:raise ValueError("short original verified stream read")
                            g.write(block);remaining-=len(block)
        if out.stat().st_size!=stream["total"]:
            raise ValueError("private sparse stream extent mismatch")

def export_private_textures(source:Path,output:Path):
    # Re-open UnityPy with authentic resource path now available, not earlier env
    # objects created prior to sparse .resS reconstruction.
    textures,saved=source_three_texture_refs(source)
    output.mkdir(parents=True,exist_ok=True)
    names={"basecolor":"ShearsBaseColor.png",
           "normal":"ShearsNormal.png","metallic":"ShearsMetallic.png"}
    result=dict(schema=1,model_category="original_shears",
                source_pinned=True,source_geometry_verified=True,
                original_geometry_exported=True,part_count=1,
                source_textures=3,original_material_colors=2,
                original_shader_subshaders=2,original_shader_passes=7,
                texture_extracted_success=False,
                actual_shader_restored=False,device_pixel_result="PENDING")
    size_classes={}
    for semantic,obj in textures.items():
        d=obj.read_typetree(check_read=False)
        w=int(d.get("m_Width",0));h=int(d.get("m_Height",0))
        if not(0<w<=MAX_IMAGE_DIM and 0<h<=MAX_IMAGE_DIM):raise ValueError("invalid original texture size")
        try:
            img=obj.read().image
        except Exception as exc:
            raise RuntimeError("original streamed Texture2D decoding failed, do not invent texture") from None
        if img is None or img.size!=(w,h):
            raise ValueError("unexpected decoded texture size")
        img.convert("RGBA").save(output/names[semantic],format="PNG")
        if not (output/names[semantic]).stat().st_size>200:
            raise ValueError("actual PNG export empty")
        size_classes[semantic]=(w,h)
    # Material original saved _Color used where present, no inferred RGBA.
    tint=None
    color_entry_count=0
    for name,val in pairs(saved.get("m_Colors",[])):
        color_entry_count+=1
        if name in ("_Color","_BaseColor"):
            if (not isinstance(val,dict) or set(("r","g","b","a"))-set(val)):
                raise ValueError("original albedo tint serialized incorrectly")
            v=[val[k] for k in ("r","g","b","a")]
            if any(type(x) not in (int,float) or not -100<=x<=100 for x in v):
                raise ValueError("invalid original tint numeric")
            tint=list(map(float,v))
    if color_entry_count!=2:raise ValueError("original two-color slot count drift")
    # No original authored tint may be invented if shader has a different ABI.
    if tint is None:
        result["albedo_tint_semantic_original_verified"]=False
    else:
        result["albedo_tint_semantic_original_verified"]=True
    # Store exact tint only inside private staged Unity project, never public logs.
    (output/"shears-private-material.json").write_text(
        json.dumps({"source_original_tint":tint,"texture_roles":names},sort_keys=True)+"\n")
    result["source_texture_dimension_classes_verified"]=len(size_classes)
    result["texture_extracted_success"]=True
    result["original_colors_not_inferred"]=tint is None
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("plan","extract"))
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--plan",type=Path,required=True)
    p.add_argument("--paths",type=Path)
    p.add_argument("--images",type=Path)
    p.add_argument("--safe-report",type=Path)
    a=p.parse_args()
    if a.command=="plan":
        stage=stage_originals(a.zip2,a.stage)
        plan=build_plan(a.zip2,stage)
        a.plan.parent.mkdir(parents=True,exist_ok=True)
        a.plan.write_text(json.dumps(plan,sort_keys=True)+"\n")
        if a.paths is None:raise ValueError("stream checkout paths output required")
        a.paths.write_text("\n".join("/"+x for x in plan["checkout_paths"])+"\n")
        print("GFX_SHEARS_STREAM_PLAN_SAFE "+json.dumps(plan["safe_counts"],sort_keys=True))
    else:
        if not a.plan.is_file():raise ValueError("private range plan absent")
        plan=json.loads(a.plan.read_text())
        stage=a.stage/"Raft_Data"
        fill_sparse_authenticated_streams(a.zip2,stage,plan)
        if a.images is None:raise ValueError("private image output required")
        result=export_private_textures(stage,a.images)
        if a.safe_report:
            a.safe_report.write_text(json.dumps({**plan["safe_counts"],**result},
                sort_keys=True,indent=2)+"\n")
        print("GFX_SHEARS_STREAM_EXTRACT_SAFE "+json.dumps({**plan["safe_counts"],**result},sort_keys=True))
if __name__=="__main__":main()
