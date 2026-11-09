#!/usr/bin/env python3
"""GFX-SHEARS-003: real SHA-original shears texture/renderer/material readiness (no raw outputs).

This uses the already proven exact 375/420 Mesh -> skinned renderer -> material graph.
Texture pixels, original property strings and IDs remain ephemeral. Reports contain only
image decode and semantic capability counters; no loose images, bytecode or game metadata.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from gfxlab.tools.original_model_probe import OWNERS, ZIP2_SHA, export_one, inspect_owner, ptr, sha_size, stage_originals
from gfxlab.tools.shears_provenance_probe import resolve_pptr, source_asset_graph, texture_slot_rows

STANDARD_SEMANTICS={
    "_MainTex":"basecolor","_BaseMap":"basecolor","_BaseColorMap":"basecolor",
    "_BumpMap":"normal","_NormalMap":"normal",
    "_MetallicGlossMap":"metallic","_SpecGlossMap":"specular",
    "_OcclusionMap":"occlusion","_EmissionMap":"emission",
    "_DetailAlbedoMap":"detail","_DetailNormalMap":"detail_normal",
    "_MaskMap":"mask","_Splat0":"layer0","_Splat1":"layer1","_Splat2":"layer2","_Splat3":"layer3",
}
MAX_IMAGE_DIM=8192
MAX_RGBA_PIXELS=33_554_432

def pairs(entries):
    if not isinstance(entries,list):raise ValueError("original material named slots not an array")
    result=[]
    names=set()
    for e in entries:
        if isinstance(e,(list,tuple)) and len(e)==2: name,val=e
        elif isinstance(e,dict) and set(e)=={"m_First","m_Second"}:name,val=e["m_First"],e["m_Second"]
        elif isinstance(e,dict) and len(e)==1: name,val=next(iter(e.items()))
        else:raise ValueError("unsupported material pair shape")
        if not isinstance(name,str) or not name or name in names:
            raise ValueError("missing/duplicate material property label")
        names.add(name)
        result.append((name,val))
    return result

def classify_standard(name):
    return STANDARD_SEMANTICS.get(name,"unknown")

def select_exact_renderer(stage):
    import UnityPy
    envs={}
    types={}
    ranked=[]
    for owner,pin in OWNERS.items():
        path=stage/owner
        if sha_size(path)!=pin:raise ValueError("source owner pin drift")
        env=UnityPy.load(str(path));envs[owner]=env
        types[owner]={x.path_id:x for x in env.objects}
        meshes,cands,_=inspect_owner(path)
        ranked.extend((score,kind,owner,go,mid) for score,kind,go,mid in cands)
    ranked.sort(key=lambda x:(-x[0],x[2],x[4]))
    if not ranked or ranked[0][1]!="skinned":raise ValueError("original target selector drift")
    score,kind,owner,go,mid=ranked[0]
    source_mesh=types[owner].get(mid)
    if not source_mesh or source_mesh.type.name!="Mesh":
        raise ValueError("selected Mesh source missing")
    _,verts,faces=export_one(source_mesh)
    if (verts,faces)!=(375,420):raise ValueError("owner-confirmed Shears topology drift")
    found=[]
    for o in envs[owner].file.objects.values():
        if o.type.name!="SkinnedMeshRenderer":continue
        d=o.read_typetree(check_read=False)
        if ptr(d.get("m_GameObject"))==(0,go) and ptr(d.get("m_Mesh"))==(0,mid):
            found.append(d)
    if len(found)!=1:raise ValueError("original selected renderer changed")
    return envs,types,owner,found[0]

def capture(stage):
    graph=source_asset_graph(stage,{"model_category":"original_player_like_skinned","part_count":1,"vertices":375,"faces":420})
    envs,types,owner,r=select_exact_renderer(stage)
    mats=r.get("m_Materials",[])
    if not isinstance(mats,list) or len(mats)!=1:
        raise ValueError("original shears renderer material slot count drift")
    ext=[x.path for x in envs[owner].file.externals]
    state,mat_key=resolve_pptr(mats[0],owner,ext)
    if mat_key is None:raise ValueError("original shears material no exact source")
    mat=types[mat_key[0]].get(mat_key[1])
    if mat is None or mat.type.name!="Material":raise ValueError("material type drift")
    mt=mat.read_typetree(check_read=False)
    saved=mt.get("m_SavedProperties",{})
    if not isinstance(saved,dict):raise ValueError("original saved properties absent")
    mext=[x.path for x in envs[mat_key[0]].file.externals]
    bound=[]
    semantic=Counter()
    for name,val in pairs(saved.get("m_TexEnvs",[])):
        if not isinstance(val,dict) or "m_Texture" not in val:raise ValueError("texture slot invalid")
        state,key=resolve_pptr(val["m_Texture"],mat_key[0],mext)
        if state=="null":continue
        if key is None:raise ValueError("texture owner not SHA-authenticated")
        t=types[key[0]].get(key[1])
        if t is None or t.type.name!="Texture2D":raise ValueError("original texture is not class28")
        semantic[classify_standard(name)]+=1
        bound.append((classify_standard(name),t))
    if len(bound)!=3:raise ValueError("original shears linked 3 textures expectation drift")
    counter=Counter()
    counter["original_texenv_bound"]=len(bound)
    counter["original_shader_passes"]=graph["original_shader_pass_count"]
    counter["original_shader_subshaders"]=graph["original_shader_subshader_count"]
    counter["original_colors"]=len(pairs(saved.get("m_Colors",[])))
    output={"schema":1,"source_original_mesh_verified":True,"model_class":"user_identified_shears",
            "source_revision":ZIP2_SHA, "original_texenv_bound":len(bound),
            "source_texture_data_extracted":False,"material_colors_exported":False,
            "original_shader_restored":False,"colored_android_device_proven":False,
            "original_mesh_vertices":375,"original_mesh_faces":420,
            "original_shader_passes":counter["original_shader_passes"],
            "original_shader_subshaders":counter["original_shader_subshaders"],
            "original_material_color_slots":counter["original_colors"],}
    for sem,n in semantic.items():
        # Only allow a small hardcoded public Unity semantic bucket; no raw property keys.
        output["semantic_"+sem]=n
    decode_ok=0
    stream_needed=0
    decode_failed=0
    texture_dim_valid=0
    total_pixels=0
    for sem,t in bound:
        d=t.read_typetree(check_read=False)
        w=d.get("m_Width",0);h=d.get("m_Height",0)
        if not isinstance(w,int) or not isinstance(h,int) or not (0<w<=MAX_IMAGE_DIM and 0<h<=MAX_IMAGE_DIM):
            raise ValueError("invalid image dimensions")
        total_pixels+=w*h
        texture_dim_valid+=1
        stream=d.get("m_StreamData",{})
        if not isinstance(stream,dict):stream={}
        if stream.get("size",0) and stream.get("path"):
            stream_needed+=1
            # Don't print private stream offsets or filename.
            continue
        try:
            im=t.read().image
            if im is None or im.width!=w or im.height!=h:
                decode_failed+=1
            else:
                decode_ok+=1
        except Exception:
            decode_failed+=1
    output.update(original_texture_dimension_verified=texture_dim_valid,
                  original_texture_stream_required=stream_needed,
                  original_texture_inline_decode_ok=decode_ok,
                  original_texture_inline_decode_failed=decode_failed,
                  original_texture_total_pixels=total_pixels,
                  source_texture_data_ready=(stream_needed==0 and decode_ok==3),
                  shade_material_identity_matches=True,
                  original_color_values_preserved=False)
    return output

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    staged=stage_originals(a.zip2,a.stage)
    d=capture(staged)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("GFX_SHEARS_TEXTURE_READINESS "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
