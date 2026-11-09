#!/usr/bin/env python3
"""GFX-MULTI-002: private six-model original Raft mesh and texture pack for Unity.

Reads only SHA-pinned ZIP2 owners and exact needed git blob stream ranges.
Original identifiers, texture pixels and values stay inside the GitHub runner.
Public data contains anonymous classes/counts; no claim of original shader parity.
"""
from __future__ import annotations
import argparse,json,math,subprocess
from pathlib import Path,PurePosixPath
from collections import defaultdict

from gfxlab.tools.original_model_probe import ZIP2_SHA, OWNERS, discover, export_one, sha_size, stage_originals
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.obj_normalize import normalize_exported_obj
from gfxlab.tools.shears_provenance_probe import resolve_pptr
from gfxlab.tools.shears_texture_readiness import pairs,select_exact_renderer,classify_standard
from gfxlab.tools.shears_stream_transport import (
    git_part_index,fill_sparse_authenticated_streams,MAX_IMAGE_DIM
)
from gfxlab.tools.original_model_probe import read_manifest

ALLOWED_ROLES=frozenset(("basecolor","normal","metallic"))
STREAMS=frozenset(("resources.assets.resS","sharedassets0.assets.resS","sharedassets6.assets.resS"))
MAX_TOTAL_CHUNKS=24
MAX_TOTAL_BYTES=1100000000

def scalar_color(entry):
    if entry is None:return None
    if not isinstance(entry,dict) or not all(k in entry for k in ("r","g","b","a")):
        raise ValueError("invalid original Shader tint vector")
    vals=[entry[k] for k in ("r","g","b","a")]
    if any(type(v) not in (float,int) or not math.isfinite(v) or abs(v)>64 for v in vals):
        raise ValueError("nonfinite/huge original RGBA")
    return [float(v) for v in vals]

def uv_pair(entry,key,default):
    vec=entry.get(key)
    if vec is None:return default
    if not isinstance(vec,dict) or not all(k in vec for k in ("x","y")):
        raise ValueError("invalid source UV vector")
    v=[vec["x"],vec["y"]]
    if any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>1000 for x in v):
        raise ValueError("invalid source UV transformation")
    return [float(x) for x in v]

def one_material(envs,types,owner,pid):
    mo=types[owner].get(pid)
    if mo is None or mo.type.name!="Material":raise ValueError("not exact original Material21")
    d=mo.read_typetree(check_read=False)
    saved=d.get("m_SavedProperties",{})
    if not isinstance(saved,dict):raise ValueError("original material properties absent")
    colors=pairs(saved.get("m_Colors",[]))
    tint=next((scalar_color(val) for name,val in colors if name in ("_Color","_BaseColor")),None)
    externals=[x.path for x in envs[owner].file.externals]
    _,shader_key=resolve_pptr(d.get("m_Shader"),owner,externals)
    if shader_key is None or types[shader_key[0]].get(shader_key[1]) is None:
        raise ValueError("original typed Shader48 source missing")
    if types[shader_key[0]][shader_key[1]].type.name!="Shader":
        raise ValueError("original shader not Shader48")
    roles={}
    for name,val in pairs(saved.get("m_TexEnvs",[])):
        if not isinstance(val,dict) or "m_Texture" not in val:
            raise ValueError("malformed original TexEnv")
        role=classify_standard(name)
        _,key=resolve_pptr(val["m_Texture"],owner,externals)
        if role not in ALLOWED_ROLES or key is None:continue
        if role in roles:raise ValueError("duplicate original named image role")
        obj=types[key[0]].get(key[1])
        if obj is None or obj.type.name!="Texture2D":raise ValueError("original texture type drift")
        roles[role]={"owner":key[0],"pid":key[1],
            "uv_scale":uv_pair(val,"m_Scale",[1.0,1.0]),
            "uv_offset":uv_pair(val,"m_Offset",[0.0,0.0])}
    if "basecolor" not in roles:raise ValueError("no original basecolor source texture")
    return {"tint":tint,"original_shader_verified":True,"textures":roles}

def all_model_entries(source:Path):
    import UnityPy
    private,safe=selected_five(source)
    envs={}
    types={}
    for owner,pin in OWNERS.items():
        file=source/owner
        if sha_size(file)!=pin:raise ValueError("original ZIP2 SHA mismatch")
        env=UnityPy.load(str(file))
        envs[owner]=env;types[owner]={obj.path_id:obj for obj in env.objects}
    entries=[]
    # M00 is owner's phone-proven original Shears 375v/420t.
    e0,t0,o0,r0=select_exact_renderer(source)
    key=resolve_pptr(r0["m_Materials"][0],o0,[x.path for x in e0[o0].file.externals])[1]
    if key is None:raise ValueError("original shears material identity missing")
    mesh=resolve_pptr(r0.get("m_Mesh"),o0,[])[1]
    if mesh is None or mesh[0]!=o0:raise ValueError("source shears original mesh pointer drift")
    entries.append({"id":"M00","category":"shears_verified_device",
        "kind":"skinned_static_pose","owner":o0,"mesh_pid":mesh[1],
        "source_bones":3,"materials":[one_material(envs,types,key[0],key[1])]})
    for i,c in enumerate(private["selected"],1):
        mats=[one_material(envs,types,m["owner"],m["material_pid"]) for m in c["materials"]]
        entries.append({"id":f"M{i:02d}","category":c["category"],
           "kind":c["kind"],"owner":c["owner"],"mesh_pid":c["mesh_pid"],
           "source_bones":c["bones"],"materials":mats})
    if len(entries)!=6:raise ValueError("require six source-authenticated entries")
    if len({(e["owner"],e["mesh_pid"]) for e in entries})!=6:
        raise ValueError("selected original Mesh duplicate or Shears reused")
    return entries,types,safe

def model_plan(zip2:Path,source:Path):
    if subprocess.check_output(["git","-C",str(zip2),"rev-parse","HEAD"],text=True).strip()!=ZIP2_SHA:
        raise ValueError("source commit SHA drift")
    entries,types,safe=all_model_entries(source)
    manifest=read_manifest(zip2)
    streams={}
    count_tex=0
    for entry in entries:
        for m in entry["materials"]:
            for role,link in m["textures"].items():
                count_tex+=1
                t=types[link["owner"]].get(link["pid"])
                if t is None or t.type.name!="Texture2D":raise ValueError("source Texture2D identity drift")
                td=t.read_typetree(check_read=False)
                w,h=td.get("m_Width",0),td.get("m_Height",0)
                if type(w)!=int or type(h)!=int or not (0<w<=MAX_IMAGE_DIM and 0<h<=MAX_IMAGE_DIM):
                    raise ValueError("source image resolution untrusted")
                link["width"]=w;link["height"]=h
                info=td.get("m_StreamData",{})
                if not isinstance(info,dict) or not info.get("size",0):
                    link["streamed"]=False;continue
                stream=PurePosixPath(str(info.get("path","")).replace("\\","/")).name
                if stream not in STREAMS:raise ValueError("external texture stream outside exact bounded scope")
                off,size=info.get("offset"),info.get("size")
                if type(off)!=int or type(size)!=int or off<0 or not 0<size<=80*1024*1024:
                    raise ValueError("untrusted source image stream span")
                if stream not in streams:
                    total,parts=git_part_index(zip2,stream,manifest)
                    streams[stream]={"total":total,"parts":parts,"spans":[]}
                if off+size>streams[stream]["total"]:raise ValueError("source range beyond streamed provider")
                streams[stream]["spans"].append({"offset":off,"size":size})
                link["streamed"]=True
    paths=set();chunks=0;bytes_needed=0
    for name,s in streams.items():
        for part in s["parts"]:
            needed=any(not(part["end"]<=sp["offset"] or part["start"]>=sp["offset"]+sp["size"])
                 for sp in s["spans"])
            if needed:
                part["needed"]=True
                paths.add(part["path"])
                chunks+=1;bytes_needed+=part["size"]
    if chunks>MAX_TOTAL_CHUNKS or bytes_needed>MAX_TOTAL_BYTES:
        raise ValueError("six-model source stream budget too large; choose a cheaper model subset")
    plan={"source_sha":ZIP2_SHA,"entries":entries,"streams":streams,"paths":sorted(paths),
          "safe":{"schema":1,"source_sha_locked":True,"model_count":6,
             "additional_models":5,"source_typed_shader_chains":6,
             "materials":sum(len(e["materials"]) for e in entries),
             "textures":count_tex,"stream_chunks":chunks,"stream_selected_bytes":bytes_needed,
             "original_shader_equivalence_verified":False,"skinned_animation_restored":False,
             "android_colored_pixels_verified":False}}
    return plan

def export_private_pack(source:Path,out:Path,plan:dict):
    import UnityPy
    if plan.get("source_sha")!=ZIP2_SHA or len(plan.get("entries",[]))!=6:
        raise ValueError("incorrect selected original model plan")
    envs={owner:UnityPy.load(str(source/owner)) for owner in OWNERS}
    objmaps={owner:{o.path_id:o for o in env.objects} for owner,env in envs.items()}
    out.mkdir(parents=True,exist_ok=True)
    safe=[]
    for entry in plan["entries"]:
        dest=out/entry["id"];dest.mkdir(exist_ok=False)
        mesh=objmaps[entry["owner"]].get(entry["mesh_pid"])
        if mesh is None or mesh.type.name!="Mesh":raise ValueError("original model mesh missing after stream rehydration")
        data,v,f=export_one(mesh)
        if entry["id"]=="M00" and (v,f)!=(375,420):raise ValueError("Shears source geometry drift")
        data,normals=normalize_exported_obj(data)
        if (normals["source_vertices"],normals["triangles"])!=(v,f):
            raise ValueError("OBJ original topology changed during normalization")
        (dest/"model.obj").write_text(data)
        public={"id":entry["id"],"category":entry["category"],"geometry_type":entry["kind"],
                "source_bones":entry["source_bones"],"skin_animation_restored":False,
                "original_shader_equivalence":False,"vertex_count":v,"face_count":f,
                "materials":[]}
        for mi,material in enumerate(entry["materials"]):
            record={"tint":material["tint"],"original_shader_restored":False,"textures":[]}
            for role,link in material["textures"].items():
                target=objmaps[link["owner"]].get(link["pid"])
                if target is None or target.type.name!="Texture2D":
                    raise ValueError("original texture identity changed after filling streams")
                try:
                    im=target.read().image
                except Exception:
                    raise ValueError("original texture decode failed; no placeholder texture") from None
                if im is None or im.size!=(link["width"],link["height"]):
                    raise ValueError("original streamed texture dimensions changed")
                name=f"S{mi:02d}_{role}.png"
                im.convert("RGBA").save(dest/name,format="PNG")
                record["textures"].append({"role":role,"file":name,
                    "scale":link["uv_scale"],"offset":link["uv_offset"]})
            public["materials"].append(record)
        (dest/"config.json").write_text(json.dumps(public,sort_keys=True))
        safe.append({"id":entry["id"],"category":entry["category"],"vertices":v,
            "faces":f,"materials":len(entry["materials"]),
            "texture_count":sum(len(m["textures"]) for m in entry["materials"]),
            "source_bones":entry["source_bones"],"source_geometry_verified":True,
            "source_images_decoded":True,"exact_original_shader_restored":False,
            "normals_generated_for_unity":normals["normals_generated_for_unity"],
            "source_uvs":normals["source_uvs"],"topology_preserved":normals["topology_preserved"]})
    summary={**plan["safe"],"model_summaries":safe,"private_original_asset_bytes_published":False,
             "unity_import_verified":False,"android_gpu_verified":False}
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("command",choices=("plan","extract"))
    p.add_argument("--zip2",required=True,type=Path)
    p.add_argument("--stage",required=True,type=Path)
    p.add_argument("--private-plan",required=True,type=Path)
    p.add_argument("--paths",type=Path)
    p.add_argument("--model-dir",type=Path)
    p.add_argument("--safe-report",type=Path)
    a=p.parse_args()
    if a.command=="plan":
        source=stage_originals(a.zip2,a.stage)
        plan=model_plan(a.zip2,source)
        a.private_plan.parent.mkdir(parents=True,exist_ok=True)
        a.private_plan.write_text(json.dumps(plan,sort_keys=True))
        if a.paths is None:raise ValueError("missing sparse file path output")
        a.paths.write_text("\n".join("/"+name for name in plan["paths"])+"\n")
        print("GFX_MULTI002_PLAN_SAFE "+json.dumps(plan["safe"],sort_keys=True))
    else:
        plan=json.loads(a.private_plan.read_text())
        if a.model_dir is None or a.safe_report is None:raise ValueError("missing output paths")
        source=a.stage/"Raft_Data"
        fill_sparse_authenticated_streams(a.zip2,source,plan)
        safe=export_private_pack(source,a.model_dir,plan)
        a.safe_report.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n")
        print("GFX_MULTI002_EXPORT_SAFE "+json.dumps(safe,sort_keys=True))
if __name__=="__main__":main()
