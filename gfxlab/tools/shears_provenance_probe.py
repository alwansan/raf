#!/usr/bin/env python3
"""GFX-SHEARS-002: verified original selected mesh -> renderer -> material -> shader -> textures.

No source GUID/PathID, private names, shader bytecode, exact colors or textures in output.
Source identities are used only in ephemeral runner RAM. Original geometry selection exactly
matches the previously successful original_model_probe (run 42702078254).
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath

from gfxlab.tools.original_model_probe import (
    OWNERS, ZIP2_SHA, discover, inspect_owner, name_score, ptr, sha_size, stage_originals,
)

EXPECTED_VERTICES = 375
EXPECTED_FACES = 420

def owner_basename(text):
    if not isinstance(text, str) or not text:
        return None
    base=PurePosixPath(text.replace("\\", "/")).name
    # No basename collision can be guessed into an original identity.
    return base if base in OWNERS else None

def resolve_pptr(p, owning, externals):
    shape = ptr(p)
    if shape is None: return ("malformed", None)
    fid,pid=shape
    if pid==0:
        return ("null" if fid==0 else "malformed", None)
    if fid==0:
        return ("local", (owning,pid))
    if not (1<=fid<=len(externals)):
        return ("malformed", None)
    owner=owner_basename(externals[fid-1])
    if owner is None:
        return ("external_unstaged", None)
    return ("external_staged", (owner,pid))

def texture_slot_rows(texenv):
    # UnityPy source pairs vary in representation. Require each slot to carry a typed
    # m_Texture field; never invent a shader/texture on a missing original pointer.
    if not isinstance(texenv,list):
        raise ValueError("original texture container is not array")
    out=[]
    names=set()
    for entry in texenv:
        if isinstance(entry,(tuple,list)) and len(entry)==2:
            name,val=entry
        elif isinstance(entry,dict) and set(entry)=={"m_First","m_Second"}:
            name,val=entry["m_First"],entry["m_Second"]
        elif isinstance(entry,dict) and len(entry)==1:
            name,val=next(iter(entry.items()))
        else:
            raise ValueError("bad original texture entry shape")
        if (not isinstance(name,str) or not name or name in names
            or not isinstance(val,dict) or "m_Texture" not in val):
            raise ValueError("bad original named texture value")
        names.add(name)
        out.append(val)
    return out

def source_asset_graph(stage:Path, report_reference:dict):
    import UnityPy
    if (report_reference.get("model_category") != "original_player_like_skinned"
        or report_reference.get("part_count") != 1
        or report_reference.get("vertices") != EXPECTED_VERTICES
        or report_reference.get("faces") != EXPECTED_FACES):
        raise ValueError("selected original mesh does not match owner-confirmed white APK")

    envs={}
    types={}
    for owner,pin in OWNERS.items():
        p=stage/owner
        if sha_size(p)!=pin:raise ValueError("original owner SHA changed")
        env=UnityPy.load(str(p))
        envs[owner]=env
        types[owner]={obj.path_id:obj for obj in env.objects}
    ranked=[]
    for owner,env in envs.items():
        meshes,cands,_=inspect_owner(stage/owner)
        for score,kind,go,mid in cands:
            ranked.append((score,kind,owner,go,mid))
    ranked.sort(key=lambda x:(-x[0],x[2],x[4]))
    if not ranked:raise ValueError("original mesh selection absent")
    best=ranked[0]
    score,kind,owner,go,mid=best
    if kind!="skinned" or score<500:raise ValueError("previous source selection changed")
    # Rerendering the exact original object is a source-level strong identity witness,
    # without publishing its private object key.
    mesh_obj=types[owner].get(mid)
    if not mesh_obj or mesh_obj.type.name!="Mesh":
        raise ValueError("original selected Mesh type missing")
    from gfxlab.tools.original_model_probe import export_one
    data,v,f=export_one(mesh_obj)
    if (v,f)!=(EXPECTED_VERTICES,EXPECTED_FACES):
        raise ValueError("original model vertex/face fingerprint drift")
    uv=sum(s.startswith("vt ") for s in data.splitlines())
    normal=sum(s.startswith("vn ") for s in data.splitlines())
    submesh=mesh_obj.read_typetree(check_read=False).get("m_SubMeshes",[])
    if not isinstance(submesh,list):raise ValueError("mesh submesh data missing")

    source_file=envs[owner].file
    externals=[x.path for x in source_file.externals]
    found=[]
    for obj in source_file.objects.values():
        if obj.type.name!="SkinnedMeshRenderer":continue
        d=obj.read_typetree(check_read=False)
        if ptr(d.get("m_GameObject")) == (0,go) and ptr(d.get("m_Mesh"))==(0,mid):
            found.append(d)
    if len(found)!=1:raise ValueError("selected mesh renderer not unique")
    renderer=found[0]
    mats=renderer.get("m_Materials")
    if not isinstance(mats,list):raise ValueError("original renderer materials missing")
    counter=Counter()
    counter["original_renderer_material_slots"]=len(mats)
    counter["original_mesh_submeshes"]=len(submesh)
    counter["mesh_obj_uv_entries"]=uv
    counter["mesh_obj_normal_entries"]=normal
    counter["source_mesh_vertices"]=v
    counter["source_mesh_faces"]=f
    counter["original_renderer_bone_pointers"]=len(renderer.get("m_Bones",[])) if isinstance(renderer.get("m_Bones"),list) else 0
    counter["original_renderer_root_bone_present"]=int(bool(ptr(renderer.get("m_RootBone")) and ptr(renderer.get("m_RootBone"))[1]))
    shader_kinds=set()
    external_tex_owners=set()
    material_classes=set()
    materials=[]
    for mp in mats:
        shape,key=resolve_pptr(mp,owner,externals)
        counter["renderer_material_pointer_"+shape]+=1
        if shape in ("malformed","null"):continue
        if key is None:
            continue
        mo=types[key[0]].get(key[1])
        if mo is None or mo.type.name!="Material":
            counter["renderer_material_target_unverified"]+=1
            continue
        counter["renderer_material_class21_verified"]+=1
        tree=mo.read_typetree(check_read=False)
        material_classes.add(tree.get("m_Name","")) # PRIVATE only; never published
        m_file=envs[key[0]].file
        m_externals=[x.path for x in m_file.externals]
        sk,shader_ref=resolve_pptr(tree.get("m_Shader"),key[0],m_externals)
        counter["material_shader_pointer_"+sk]+=1
        if shader_ref is not None:
            sh=types[shader_ref[0]].get(shader_ref[1])
            if sh is not None and sh.type.name=="Shader":
                counter["original_shader_class48_verified"]+=1
                shader_kinds.add("typed_original")
                s_tree=sh.read_typetree(check_read=False)
                parsed=s_tree.get("m_ParsedForm",{})
                sub=parsed.get("m_SubShaders",[]) if isinstance(parsed,dict) else []
                if isinstance(sub,list):
                    counter["original_shader_subshader_count"]+=len(sub)
                    for item in sub:
                        p=item.get("m_Passes",[]) if isinstance(item,dict) else []
                        if isinstance(p,list):counter["original_shader_pass_count"]+=len(p)
            else:
                counter["original_shader_unverified"]+=1
        saved=tree.get("m_SavedProperties")
        if not isinstance(saved,dict):
            counter["original_material_saved_properties_missing"]+=1
            continue
        colors=saved.get("m_Colors",[])
        if isinstance(colors,(list,dict)):
            counter["original_material_color_slots"]+=len(colors)
        else:counter["original_material_colors_malformed"]+=1
        texenv=saved.get("m_TexEnvs",[])
        rows=texture_slot_rows(texenv)
        counter["original_texenv_slots"]+=len(rows)
        for row in rows:
            tex_ptr=row.get("m_Texture") if isinstance(row,dict) else None
            tk,tkey=resolve_pptr(tex_ptr,key[0],m_externals)
            counter["texture_pointer_"+tk]+=1
            if tkey is None:continue
            to=types[tkey[0]].get(tkey[1])
            if to is not None and to.type.name=="Texture2D":
                counter["original_texture_class28_verified"]+=1
                external_tex_owners.add(tkey[0])
                materials.append((tkey[0],tkey[1])) # PRIVATE, no output
            else:counter["original_texture_class28_unverified"]+=1
    result={
        "schema":1,
        "status":"GFX_SHEARS_ORIGINAL_GRAPH_SCANNED",
        "original_source_verified":True,
        "source_revision":ZIP2_SHA,
        "reproduces_owner_tested_mesh_375_420":True,
        "user_visual_identification":"Shears",
        "original_renderer_class":"SkinnedMeshRenderer",
        "source_original_name_or_ptr_leaked":False,
        "source_material_shader_textures_privately_linked":counter["renderer_material_class21_verified"]>0,
        "material_tint_exported":False,
        "original_texture_exported":False,
        "original_shader_restored":False,
        "android_colored_pixels_verified":False,
        **{k:int(v) for k,v in sorted(counter.items())},
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    src=stage_originals(a.zip2,a.stage)
    # Reproduce original model discovery on SHA pinned 3 providers, but keep geometry
    # in private ephemeral scratch directory. Never upload OBJ.
    expected=discover(src,a.stage/"private-mesh-geometry")
    result=source_asset_graph(src,expected)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX_SHEARS_SOURCE_GRAPH "+json.dumps(result,sort_keys=True))
    if not result["source_material_shader_textures_privately_linked"]:
        raise SystemExit("No exact original renderer->material link; do not fake materials")
if __name__=="__main__":main()
