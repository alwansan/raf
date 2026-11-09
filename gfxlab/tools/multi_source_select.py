#!/usr/bin/env python3
"""GFX-MULTI-001: select five distinct authentic Raft original meshes with typed Material/Texture links.
Private runner-only selection contains original object IDs; public summary is aggregate and generic.
Never assume a game asset is Player from ancestor-name heuristics.
"""
from __future__ import annotations
import argparse, json, re
from collections import Counter
from pathlib import Path, PurePosixPath
from gfxlab.tools.original_model_probe import OWNERS, ZIP2_SHA, inspect_owner, ptr, sha_size, stage_originals
from gfxlab.tools.shears_provenance_probe import resolve_pptr
from gfxlab.tools.shears_texture_readiness import pairs, classify_standard
from gfxlab.tools.original_model_probe import export_one
from gfxlab.tools.obj_normalize import source_vertex_span_valid

ROLE_KEEP=frozenset(("basecolor","normal","metallic","emission","occlusion","specular"))
STREAM_ALLOW=frozenset(("sharedassets0.assets.resS","resources.assets.resS","sharedassets6.assets.resS"))
CATEGORY_KEYWORDS={
    "animal":("llama","goat","sheep","shark","bear","boar","puffer","seagull","chicken","bird","fish","whale"),
    "person":("character","survivor","human","torso","body","arms","legs","skin","head","person","male","female"),
    "large_prop":("receiver","engine","anchor","purifier","smelter","grill","furnace","battery","boat","sail","sharkbait"),
    "tool":("axe","hook","spear","hammer","bow","paddle","machete","shovel","fishing","hatchet","shear"),
}
MAX_TEXELS=8*4096*4096
MIN_VERTICES=128
MAX_VERTICES=140000

def label_category(names,kind,bones,verts,material_slots):
    name=(" ".join(names)).lower()
    for category,words in CATEGORY_KEYWORDS.items():
        if any(re.search(r"(^|[^a-z])"+re.escape(w)+r"([^a-z]|$)",name) for w in words):
            if category=="person" and (kind!="skinned" or bones<12):
                continue
            if category=="animal" and (kind!="skinned" or bones<8):
                continue
            return category
    if kind=="skinned" and bones>=12:return "complex_skinned_unidentified"
    if verts>=4500:return "large_mesh"
    if material_slots>=2:return "multi_material"
    return "generic"

def source_catalog(original:Path):
    import UnityPy
    environments={}
    typed={}
    names={}
    mesh_candidates=[]
    for owner,pin in OWNERS.items():
        p=original/owner
        if sha_size(p)!=pin:raise ValueError("SHA original provider drift")
        env=UnityPy.load(str(p))
        environments[owner]=env
        typed[owner]={obj.path_id:obj for obj in env.objects}
        # Restrict labels to private in-process categorization (never log).
        names[owner]={}
        for obj in env.objects:
            if obj.type.name=="GameObject":
                try:names[owner][obj.path_id]=obj.read_typetree(check_read=False).get("m_Name","")
                except Exception:pass
        # A source-candidate link must originate from actual MeshFilter or SkinnedMeshRenderer.
        _, candidates, _=inspect_owner(p)
        mesh_candidates.extend((owner,kind,go,mid) for _,kind,go,mid in candidates)
    source_map={}
    for owner,kind,go,mid in mesh_candidates:
        if (owner,mid) in source_map:continue
        obj=typed[owner].get(mid)
        if obj and obj.type.name=="Mesh":
            try:
                d=obj.read_typetree(check_read=False)
                vd=d.get("m_VertexData",{})
                vertices=vd.get("m_VertexCount",0) if isinstance(vd,dict) else 0
                if isinstance(vertices,int):source_map[(owner,mid)]=vertices
            except Exception:pass
    return environments,typed,names,mesh_candidates,source_map

def inspect_candidate(envs,types,names,source_map,owner,kind,go,mid):
    obj=types[owner].get(mid)
    if obj is None or obj.type.name!="Mesh":return None
    vertices=source_map.get((owner,mid),0)
    if not MIN_VERTICES<=vertices<=MAX_VERTICES:return None
    file=envs[owner].file
    ext=[x.path for x in file.externals]
    # Renderer is same GO as MeshFilter, not source mesh object.
    renderer_kind="SkinnedMeshRenderer" if kind=="skinned" else "MeshRenderer"
    renderers=[]
    for o in file.objects.values():
        if o.type.name!=renderer_kind:continue
        try:
            d=o.read_typetree(check_read=False)
        except Exception:continue
        if ptr(d.get("m_GameObject"))!=(0,go):continue
        if kind=="skinned" and ptr(d.get("m_Mesh"))!=(0,mid):continue
        renderers.append(d)
    if len(renderers)!=1:return None
    renderer=renderers[0]
    material_ptrs=renderer.get("m_Materials",[])
    if not isinstance(material_ptrs,list) or not 1<=len(material_ptrs)<=4:return None
    bones=len(renderer.get("m_Bones",[])) if isinstance(renderer.get("m_Bones"),list) else 0
    # Typed source chain must be complete with SHA-selected owners; no guesses.
    materials=[]
    semantic_cover=set()
    textures_total=0
    texture_pixels=0
    seen_textures=set()
    for material_ptr in material_ptrs:
        _,mkey=resolve_pptr(material_ptr,owner,ext)
        if mkey is None:return None
        mo=types[mkey[0]].get(mkey[1])
        if mo is None or mo.type.name!="Material":return None
        mt=mo.read_typetree(check_read=False)
        me=[x.path for x in envs[mkey[0]].file.externals]
        _,skey=resolve_pptr(mt.get("m_Shader"),mkey[0],me)
        if skey is None:return None
        shader=types[skey[0]].get(skey[1])
        if shader is None or shader.type.name!="Shader":return None
        saved=mt.get("m_SavedProperties",{})
        if not isinstance(saved,dict):return None
        role_refs={}
        try: texrows=pairs(saved.get("m_TexEnvs",[]))
        except Exception:return None
        for name,val in texrows:
            if not isinstance(val,dict) or "m_Texture" not in val:return None
            state,tkey=resolve_pptr(val["m_Texture"],mkey[0],me)
            if state=="null":continue
            if tkey is None:return None
            to=types[tkey[0]].get(tkey[1])
            if to is None or to.type.name!="Texture2D":return None
            role=classify_standard(name)
            if role not in ROLE_KEEP:continue
            if role in role_refs:return None
            td=to.read_typetree(check_read=False)
            w,h=td.get("m_Width",0),td.get("m_Height",0)
            if type(w)!=int or type(h)!=int or not(0<w<=4096 and 0<h<=4096):return None
            sd=td.get("m_StreamData",{})
            if isinstance(sd,dict) and sd.get("size",0):
                stream=PurePosixPath(str(sd.get("path","")).replace("\\","/")).name
                if stream not in STREAM_ALLOW:return None
            role_refs[role]={"texture_owner":tkey[0],"texture_pid":tkey[1],"w":w,"h":h}
            semantic_cover.add(role)
            if tkey not in seen_textures:
                texture_pixels+=w*h;seen_textures.add(tkey);textures_total+=1
        if "basecolor" not in role_refs:return None
        colors=saved.get("m_Colors",[])
        try:colors=pairs(colors)
        except Exception:return None
        materials.append({"owner":mkey[0],"material_pid":mkey[1],"shader_owner":skey[0],
            "shader_pid":skey[1],"texture_roles":role_refs,
            "original_color_slots":len(colors),"original_color_semantic_tint":next(
                (v for n,v in colors if n in ("_Color","_BaseColor")),None)})
    if texture_pixels>MAX_TEXELS:return None
    # Reject tiny pieces of complex skinned characters unless deliberately selecting a tool.
    if kind=="skinned" and bones>15 and vertices<500:return None
    mesh_name=""
    try:mesh_name=str(obj.read_typetree(check_read=False).get("m_Name",""))
    except Exception:pass
    go_name=str(names[owner].get(go,""))
    category=label_category([go_name,mesh_name],kind,bones,vertices,len(material_ptrs))
    if category=="tool" and "shear" in (go_name+" "+mesh_name).lower() and vertices==375:
        return None
    return {"owner":owner,"kind":kind,"game_object_pid":go,"mesh_pid":mid,
        "category":category,"vertices":vertices,"bones":bones,
        "submeshes":len(obj.read_typetree(check_read=False).get("m_SubMeshes",[])),
        "materials":materials,"texture_count":textures_total,"texture_pixels":texture_pixels,
        "semantic_roles":sorted(semantic_cover),
        "original_shader_typed":True}

def selected_five(original:Path):
    envs,types,names,mesh_candidates,mesh_counts=source_catalog(original)
    seen=set();valid=[];counts=Counter()
    for owner,kind,go,mid in mesh_candidates:
        key=(owner,go,mid)
        if key in seen:continue
        seen.add(key)
        try:c=inspect_candidate(envs,types,names,mesh_counts,owner,kind,go,mid)
        except Exception:
            counts["candidate_inspection_errors"]+=1
            continue
        if c is None:continue
        valid.append(c)
        counts["valid_original_typed_links"]+=1
        counts["qualified_"+c["category"]]+=1
    if len(valid)<5:raise RuntimeError("fewer than five verified source models; do not invent")
    def quality(x):
        roles=x["semantic_roles"]
        bonus=300 if "normal" in roles else 0
        bonus+=180 if "metallic" in roles else 0
        bonus+=350 if x["category"]=="person" else 0
        return min(x["vertices"],20000)/20+bonus+len(roles)*30+min(x["bones"],90)*2
    valid.sort(key=lambda x:(-quality(x),x["owner"],x["mesh_pid"]))
    # Do not select an OBJ whose original vertex coordinates collapse to a
    # point in Unity float32. M02 from CI42718266273 had valid source topology
    # counts but zero spatial extent after export. Avoid fabricating geometry.
    # Keep the proven 1x3 or 2x3 material/texture profile (7/21 total).
    probed={}
    rejected=0
    def qualified(x):
        nonlocal rejected
        key=(x["owner"],x["mesh_pid"])
        if key in probed:return probed[key]
        mats=x["materials"]
        layout=(len(mats) in (1,2) and x["submeshes"]==len(mats)
                and all(set(m["texture_roles"])=={"basecolor","normal","metallic"} for m in mats))
        if not layout:
            probed[key]=False
            return False
        try:
            obj=types[x["owner"]][x["mesh_pid"]]
            data,vertices,faces=export_one(obj)
            xyz=[]
            for line in data.splitlines():
                if line.startswith("v "):
                    tokens=line.split()
                    if len(tokens)<4:raise ValueError("incomplete exported vertex")
                    xyz.append(tuple(float(value) for value in tokens[1:4]))
            ready=(len(xyz)==vertices and faces>0 and source_vertex_span_valid(xyz))
        except Exception:
            ready=False
        probed[key]=ready
        if not ready:rejected+=1
        return ready
    result=[];used_mesh=set()
    order=("person","animal","large_prop","large_mesh","tool","multi_material","complex_skinned_unidentified","generic")
    for desired in order:
        if len(result)==5:break
        for x in valid:
            key=(x["owner"],x["mesh_pid"])
            if x["category"]==desired and key not in used_mesh and qualified(x):
                result.append(x);used_mesh.add(key)
                break
    for x in valid:
        if len(result)==5:break
        key=(x["owner"],x["mesh_pid"])
        if key not in used_mesh and qualified(x):
            result.append(x);used_mesh.add(key)
    if len(result)!=5:raise RuntimeError("unable to select five separate verified meshes")
    private={"schema":1,"source_sha":ZIP2_SHA,"selected":result}
    safe={"schema":1,"source_sha_locked":True,"source_owners":len(OWNERS),
          "scanned_original_renderer_mesh_links":len(mesh_candidates),
          "verified_material_and_shader_chains":counts["valid_original_typed_links"],
          "candidate_inspection_errors":counts["candidate_inspection_errors"],
          "rejected_unusable_original_geometry":rejected,
          "selected_count":len(result),"source_verified":True,
          "unity_imported":False,"android_pixels_verified":False,
          "original_shader_equivalence_verified":False,
          "selected":[{"id":f"M{i+1:02d}","category":x["category"],
                       "kind":x["kind"],"vertices":x["vertices"],"bones":x["bones"],
                       "material_slots":len(x["materials"]),"texture_count":x["texture_count"],
                       "submeshes":x["submeshes"],"semantic_roles":x["semantic_roles"],
                       "original_shader_typed":True,"original_shader_equivalence":False}
                      for i,x in enumerate(result)]}
    return private,safe

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--private-selection",type=Path,required=True)
    ap.add_argument("--safe-report",type=Path,required=True)
    a=ap.parse_args()
    source=stage_originals(a.zip2,a.stage)
    private,safe=selected_five(source)
    a.private_selection.parent.mkdir(parents=True,exist_ok=True)
    a.private_selection.write_text(json.dumps(private,sort_keys=True)+"\n")
    a.safe_report.parent.mkdir(parents=True,exist_ok=True)
    a.safe_report.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI001_SELECTED_SAFE "+json.dumps(safe,sort_keys=True))
if __name__=="__main__":main()
