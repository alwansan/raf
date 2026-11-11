"""GFX107 source-private original six skinned Mesh pose matrix diagnostic.

Reconstruct absolute *serialized Transform snapshot*, and compare each
bone.world * Mesh.bindpose matrix in mesh/renderer coordinate space. A
difference is not data loss: original snapshot may be an animated pose.
Never prints bone names/IDs, matrices, vertices, source shader bytes or paths.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA,ptr
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.shears_provenance_probe import resolve_pptr
from gfxlab.tools.gfx107_source_bindpose_math import (
    MAX_BONES,source_world_matrix,compute_bindpose_consistency,
)

def inspect_source_pose(entry,types,externals):
    model=entry["id"]
    if entry["source_bones"]==0:
        return {"model":model,"skinned":False,"status":"NOT_APPLICABLE",
                "original_rest_pose_restored":False}
    owner=entry["owner"]
    mesh=types[owner][entry["mesh_pid"]].read_typetree(check_read=False)
    bindposes=mesh.get("m_BindPose")
    renderers=[]
    for obj in types[owner].values():
        if obj.type.name!="SkinnedMeshRenderer":continue
        d=obj.read_typetree(check_read=False)
        if ptr(d.get("m_Mesh"))!=(0,entry["mesh_pid"]):continue
        go=entry.get("game_object_pid")
        if go is not None and ptr(d.get("m_GameObject"))!=(0,go):continue
        renderers.append(d)
    if len(renderers)!=1:
        return {"model":model,"skinned":True,"status":"RENDERER_IDENTITY_AMBIGUOUS",
                "candidate_renderer_count":len(renderers),
                "original_rest_pose_restored":False}
    renderer=renderers[0]
    bones=renderer.get("m_Bones")
    if (not isinstance(bones,list) or len(bones)!=entry["source_bones"]
         or len(bones)>MAX_BONES or not isinstance(bindposes,list)
         or len(bones)!=len(bindposes)):
        return {"model":model,"skinned":True,
                "status":"BONE_OR_BINDPOSE_COUNT_MISMATCH",
                "original_rest_pose_restored":False}
    cache={}
    def resolve(p,from_owner):
        state,key=resolve_pptr(p,from_owner,externals.get(from_owner,[]))
        if state=="null":return None
        if key is None:
            raise ValueError("GFX107_SOURCE_POINTER_UNSTAGED")
        obj=types.get(key[0],{}).get(key[1])
        if obj is None or obj.type.name not in ("Transform","RectTransform"):
            raise ValueError("GFX107_SOURCE_TYPED_TRANSFORM_MISSING")
        return key
    def lookup(key):
        if key not in cache:
            obj=types.get(key[0],{}).get(key[1])
            if obj is None or obj.type.name not in ("Transform","RectTransform"):
                raise ValueError("GFX107_SOURCE_TRANSFORM_NOT_TYPED")
            cache[key]=obj.read_typetree(check_read=False)
        return cache[key]
    def parent_of(key,raw):
        return resolve(raw.get("m_Father"),key[0])
    try:
        worlds=[]
        for p in bones:
            key=resolve(p,owner)
            if key is None:raise ValueError("GFX107_NULL_BONE")
            worlds.append(source_world_matrix(key,lookup,parent_of))
        report=compute_bindpose_consistency(bindposes,worlds)
    except (ValueError,IndexError,KeyError,TypeError) as error:
        label=str(error)
        if not label.startswith("GFX107_"):label="GFX107_SOURCE_SHAPE_UNSUPPORTED"
        return {"model":model,"skinned":True,"status":label,
                "original_rest_pose_restored":False}
    return {"model":model,"skinned":True,"status":"SOURCE_MATRIX_COMPUTED",
            **report}

def audit(stage):
    entries,types,_=all_model_entries(stage)
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("GFX107_SOURCE_SELECTION_CHANGED")
    private,_=selected_five(stage)
    selected=private["selected"]
    if len(selected)!=5:raise ValueError("GFX107_ORIGINAL_FIVE_SELECTION_DRIFT")
    for i,row in enumerate(selected,1):
        entry=entries[i]
        if (row["owner"],row["mesh_pid"])!=(entry["owner"],entry["mesh_pid"]):
            raise ValueError("GFX107_SOURCE_MODEL_LINK_NOT_EXACT")
        if type(row.get("game_object_pid"))!=int or row["game_object_pid"]==0:
            raise ValueError("GFX107_ORIGINAL_GAME_OBJECT_REF_BAD")
        entry["game_object_pid"]=row["game_object_pid"]
    import UnityPy
    externals={}
    for owner in types:
        env=UnityPy.load(str(stage/owner))
        externals[owner]=[x.path for x in env.file.externals]
    cases=[inspect_source_pose(e,types,externals) for e in entries]
    counts=Counter()
    for row in cases:
        counts["skinned" if row["skinned"] else "non_skinned"]+=1
        counts["status_"+row["status"]]+=1
        if row["status"]=="SOURCE_MATRIX_COMPUTED":
            counts["bone_matrices_computed"]+=row["source_bone_matrix_count"]
            counts["coherent_bones_at_1e4"]+=row["source_pose_products_coherent_at_1e4"]
            counts["all_coherent_models"]+=bool(row["source_pose_products_all_coherent_at_1e4"])
    return {
        "experiment":"GFX-MULTI-107",
        "original_source_zip2_sha":ZIP2_SHA,
        "original_models":6,
        "case_summary":cases,
        "safe_counts":dict(counts),
        "source_original_bone_transform_hierarchy_verified_by_gfx106":True,
        "source_vertex_indexed_cpu_skinning_compared":False,
        "mesh_to_world_original_pose_equivalence_verified":False,
        "source_transform_is_bind_pose_proven":False,
        "source_animation_runtime_verified":False,
        "original_rig_restored":False,
        "originalShaderRestored":False,
        "phase_closed":False,
        "private_matrix_or_bone_identity_exported":False,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--safe",type=Path,required=True)
    a=ap.parse_args()
    out=audit(stage_originals(a.zip2,a.stage))
    a.safe.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("GFX107_ORIGINAL_SOURCE_BINDPOSE_MATRIX_SAFE "+json.dumps(out,sort_keys=True))
if __name__=="__main__":
    main()
