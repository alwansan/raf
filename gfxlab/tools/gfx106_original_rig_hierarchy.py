"""GFX106: source-authenticated skinned bone and hierarchy readiness audit.

Only original six selected Mesh objects and their exact SkinnedMeshRenderer links
are considered. Exports bounded anonymous counts, NEVER bone IDs/names,
asset GUIDs, path IDs, matrices, coordinates, animation clips or raw geometry.
This is a *source rig availability census*, NOT animated rig restoration.
"""
import argparse
import json
import math
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

from gfxlab.tools.original_model_probe import ZIP2_SHA,ptr,stage_originals
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.shears_provenance_probe import resolve_pptr

MAX_BONES=512
MAX_PARENT_DEPTH=512

def finite_transform(d):
    """Require a source Transform with finite local 3+4+3 values."""
    if not isinstance(d,dict):return False
    for key,parts in (("m_LocalPosition",("x","y","z")),
                      ("m_LocalRotation",("x","y","z","w")),
                      ("m_LocalScale",("x","y","z"))):
        v=d.get(key)
        if not isinstance(v,dict):return False
        if any(type(v.get(p)) not in (float,int) or not math.isfinite(v[p])
               or abs(v[p])>1e8 for p in parts):return False
    return True

def inspect_rig_source(entry,types,externals):
    """Fail closed on ambiguous original renderers; track missing sources as UNKNOWN."""
    owner=entry["owner"];mesh_id=entry["mesh_pid"]
    if owner not in types or mesh_id not in types[owner]:
        raise ValueError("GFX106_SOURCE_MESH_MISSING")
    mo=types[owner][mesh_id]
    if mo.type.name!="Mesh":raise ValueError("GFX106_TYPED_MESH_DRIFT")
    source_mesh=mo.read_typetree(check_read=False)
    poses=source_mesh.get("m_BindPose",None)
    bindpose_count=len(poses) if isinstance(poses,list) else -1
    if entry["source_bones"]==0:
        return {
          "model":entry["id"],"kind":"NON_SKINNED",
          "bindpose_count":bindpose_count,
          "original_rig_restored":False,
        }
    candidates=[]
    # Exact mesh PID and owner local pointer; skip ambiguous source renderer reuse.
    for obj in types[owner].values():
        if obj.type.name!="SkinnedMeshRenderer":continue
        d=obj.read_typetree(check_read=False)
        if ptr(d.get("m_Mesh"))==(0,mesh_id):
            # Original M01/M04 meshes are shared across multiple Renderers.
            # Require the *source selected* GameObject PPtr to avoid guessing.
            go_id=entry.get("game_object_pid")
            if go_id is not None and ptr(d.get("m_GameObject"))!=(0,go_id):
                continue
            candidates.append(d)
    counts=Counter()
    counts["source_bones_expected"]=entry["source_bones"]
    counts["candidate_original_renderers"]=len(candidates)
    counts["mesh_bindpose_count"]=bindpose_count
    if len(candidates)!=1:
        counts["source_renderer_identity_ambiguous_or_absent"]=1
        return {"model":entry["id"],"kind":"SKINNED","counts":dict(counts),
                "original_rig_restored":False}
    rend=candidates[0]
    bones=rend.get("m_Bones",None)
    if not isinstance(bones,list) or len(bones)>MAX_BONES:
        raise ValueError("GFX106_SKINNED_BONES_INVALID")
    counts["renderer_bone_refs"]=len(bones)
    counts["renderer_bones_match_source_expected"]=int(len(bones)==entry["source_bones"])
    counts["renderer_bones_match_mesh_bindposes"]=int(len(bones)==bindpose_count)
    ex=externals.get(owner,[])
    cache={}
    def resolve(p,from_owner):
        state,key=resolve_pptr(p,from_owner,externals.get(from_owner,[]))
        if key is None:return state,None,None
        target=types.get(key[0],{}).get(key[1])
        if target is None or target.type.name not in ("Transform","RectTransform"):
            return "unavailable_typed_transform",key,None
        if key not in cache:
            cache[key]=target.read_typetree(check_read=False)
        return "typed_transform",key,cache[key]
    root_state,root_key,root=resolve(rend.get("m_RootBone"),owner)
    counts["source_rootbone_pointer_resolved"]=int(root_state=="typed_transform")
    unique=set()
    for p in bones:
        state,key,node=resolve(p,owner)
        if state!="typed_transform":
            counts["bone_ptr_"+str(state)]+=1
            continue
        counts["bone_pointer_resolved"]=counts["bone_pointer_resolved"]+1
        if key in unique:
            counts["bone_pointer_duplicates"]+=1
        else:unique.add(key)
        if finite_transform(node):
            counts["bone_local_transform_finite"]+=1
        else:counts["bone_local_transform_invalid"]+=1
        visited=set();current=key;chain_finished=False
        for depth in range(MAX_PARENT_DEPTH):
            if current in visited:
                counts["bone_parent_chain_cycle"]+=1;chain_finished=True;break
            visited.add(current)
            if root_key is not None and current==root_key:
                counts["bone_ancestor_reaches_root"]+=1
                chain_finished=True;break
            node_d=cache[current]
            ps,pkey,pnode=resolve(node_d.get("m_Father"),current[0])
            if ps=="null":
                counts["bone_parent_chain_terminates_null"]+=1
                chain_finished=True;break
            if ps!="typed_transform":
                counts["bone_parent_chain_unavailable"]+=1
                chain_finished=True;break
            current=pkey
            counts["parent_links_traversed"]+=1
        if not chain_finished:counts["bone_parent_depth_limit"]+=1
    counts["bone_distinct_transform_targets"]=len(unique)
    counts["source_rig_hierarchy_coverage_complete"]=int(
        len(candidates)==1 and len(bones)==entry["source_bones"] and
        bindpose_count==len(bones) and counts["bone_pointer_resolved"]==len(bones) and
        counts["bone_pointer_duplicates"]==0 and
        counts["bone_local_transform_invalid"]==0 and
        counts["bone_parent_chain_cycle"]==0 and
        counts["bone_parent_depth_limit"]==0 and
        counts["bone_parent_chain_unavailable"]==0 and
        counts["source_rootbone_pointer_resolved"]==1 and
        counts["bone_ancestor_reaches_root"]==len(bones))
    return {"model":entry["id"],"kind":"SKINNED","counts":dict(counts),
            "original_rig_restored":False}

def audit(stage):
    entries,types,_=all_model_entries(stage)
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("GFX106_SOURCE_MODEL_SELECTION_DRIFT")
    # Recover the same typed source GameObject identity that selected_five
    # authenticated earlier. Never infer from names, counts, or mesh reuse.
    private,_=selected_five(stage)
    selected=private.get("selected",[])
    if len(selected)!=5:raise ValueError("GFX106_SOURCE_FIVE_SELECTION_DRIFT")
    for i,row in enumerate(selected,1):
        entry=entries[i]
        if (row.get("owner"),row.get("mesh_pid"))!=(entry["owner"],entry["mesh_pid"]):
            raise ValueError("GFX106_SOURCE_RENDERER_SELECTION_IDENTITY_MISMATCH")
        go=row.get("game_object_pid")
        if type(go)!=int or go<=0:
            raise ValueError("GFX106_SOURCE_GAME_OBJECT_ID_INVALID")
        entry["game_object_pid"]=go
    # All references are resolved only among pinned/loaded source owners.
    import UnityPy
    externals={}
    for owner in types:
        env=UnityPy.load(str(stage/owner))
        externals[owner]=[x.path for x in env.file.externals]
    results=[inspect_rig_source(e,types,externals) for e in entries]
    total=Counter()
    for row in results:
        if row["kind"]=="SKINNED":
            total["skinned_models"]+=1
            total.update({k:v for k,v in row["counts"].items() if isinstance(v,int)})
        else:total["non_skinned_models"]+=1
    return {
      "experiment":"GFX-MULTI-106",
      "source_zip2_sha":ZIP2_SHA,
      "sample_model_count":6,
      "source_original_skin_hierarchy_counts":dict(total),
      "anonymous_model_cases":results,
      "source_transform_names_or_ids_exported":False,
      "source_bindpose_matrices_exported":False,
      "skinned_mesh_original_gpu_pose_verified":False,
      "source_original_animation_verified":False,
      "original_rig_restored":False,
      "originalShaderRestored":False,
      "phase_closed":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--safe",type=Path,required=True)
    a=p.parse_args()
    result=audit(stage_originals(a.zip2,a.stage))
    a.safe.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX106_ORIGINAL_RIG_HIERARCHY_SAFE "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
