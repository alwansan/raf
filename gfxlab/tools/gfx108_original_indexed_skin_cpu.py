"""GFX108 source-private original indexed vertex/skin CPU witness.

Needs exact source Mesh.m_Vertices + matching Mesh.m_Skin and Renderer bones
from the immutable ZIP2 Unity assets. No OBJ/FBX importer, no deduplication.
Private vertex coordinates, bone IDs/weights and matrices are never exported.
If UnityPy's direct vertex representation is unavailable, say so explicitly.
"""
import argparse,json
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import ZIP2_SHA,ptr,stage_originals
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.shears_provenance_probe import resolve_pptr
from gfxlab.tools.gfx107_source_bindpose_math import (
    source_world_matrix,source_matrix4,mul)
from gfxlab.tools.gfx108_indexed_skinning_cpu import (
    positions_from_parsed_mesh,decoded_handler_skin,handler_skin_safe_shapes,skin_positions_cpu,
    safe_displacement_stats)

def direct_mesh_handler(mesh_reader):
    """UnityPy 1.25.4 MeshHandler unpacks original VertexData streams by index."""
    from UnityPy.helpers.MeshHelper import MeshHandler
    handler=MeshHandler(mesh_reader.parse_as_object())
    handler.process()
    return handler

def inspect_exact_source_skin(entry,types,externals,private_consumer=None):
    model=entry["id"]
    if not entry["source_bones"]:
        return {"model":model,"status":"NON_SKINNED","cpu_original_vertices_deformed":False}
    owner=entry["owner"];mesh_id=entry["mesh_pid"]
    mesh_obj=types[owner][mesh_id]
    mesh=mesh_obj.read_typetree(check_read=False)
    v=mesh.get("m_VertexData",{}).get("m_VertexCount",-1)
    if type(v)!=int or not 1<=v<=150_000:
        return {"model":model,"status":"SOURCE_VERTEX_COUNT_INVALID",
                "cpu_original_vertices_deformed":False}
    renderers=[]
    for obj in types[owner].values():
        if obj.type.name!="SkinnedMeshRenderer":continue
        d=obj.read_typetree(check_read=False)
        if ptr(d.get("m_Mesh"))!=(0,mesh_id):continue
        if entry.get("game_object_pid") is not None and ptr(d.get("m_GameObject"))!=(
                0,entry["game_object_pid"]):continue
        renderers.append(d)
    if len(renderers)!=1:
        return {"model":model,"status":"AUTHENTIC_RENDERER_AMBIGUOUS",
                "cpu_original_vertices_deformed":False}
    r=renderers[0];bones=r.get("m_Bones");poses=mesh.get("m_BindPose")
    if not isinstance(bones,list) or not isinstance(poses,list) or (
            len(bones)!=len(poses)) or len(bones)!=entry["source_bones"]:
        return {"model":model,"status":"ORIGINAL_BONE_BINDPOSE_MISMATCH",
                "cpu_original_vertices_deformed":False}
    cache={}
    def resolve(p,owner_key):
        state,key=resolve_pptr(p,owner_key,externals.get(owner_key,[]))
        if state=="null":return None
        if key is None:raise ValueError("GFX108_TRANSFORM_POINTER_UNSTAGED")
        obj=types.get(key[0],{}).get(key[1])
        if obj is None or obj.type.name not in ("Transform","RectTransform"):
            raise ValueError("GFX108_TRANSFORM_POINTER_UNRESOLVED")
        return key
    def lookup(key):
        if key not in cache:
            obj=types.get(key[0],{}).get(key[1])
            if obj is None or obj.type.name not in ("Transform","RectTransform"):
                raise ValueError("GFX108_TRANSFORM_NOT_TYPED")
            cache[key]=obj.read_typetree(check_read=False)
        return cache[key]
    def parent_of(key,d):return resolve(d.get("m_Father"),key[0])
    try:
        handler=direct_mesh_handler(mesh_obj)
        indexed_positions=positions_from_parsed_mesh(handler,v)
        indexed_weights=decoded_handler_skin(handler,v,len(bones))
        world=[source_world_matrix(resolve(p,owner),lookup,parent_of) for p in bones]
        matrices=[source_matrix4(m) for m in poses]
        deformed=skin_positions_cpu(indexed_positions,indexed_weights,world,matrices)
        report=safe_displacement_stats(deformed,indexed_positions,mul(world[0],matrices[0]))
    except (ValueError,KeyError,TypeError,IndexError,AttributeError) as e:
        reason=str(e)
        if not reason.startswith(("GFX107_","GFX108_")):
            reason="GFX108_MESH_VERTEX_OR_SKIN_SHAPE_UNSUPPORTED"
        safe_shape={}
        if reason in ("GFX108_SKIN_INFLUENCES_SHAPE",
                      "GFX108_DIRECT_MESH_HANDLER_SKIN_CHANNELS_UNAVAILABLE",
                      "GFX108_DIRECT_HANDLER_BONE_WEIGHT_LAYOUT"):
            if "handler" in locals():
                safe_shape=handler_skin_safe_shapes(handler)
        return {"model":model,"source_vertex_count":v,"status":reason,
                "safe_influence_channel_shapes":safe_shape,
                "cpu_original_vertices_deformed":False}
    if private_consumer is not None:
        private_consumer(model, indexed_positions, indexed_weights, world, matrices, deformed)
    return {"model":model,"status":"SOURCE_INDEXED_LBS_COMPUTED",
        "source_vertex_count":v,
        "original_indexed_vertex_weights_preserved":True,
        "cpu_original_vertices_deformed":True,
        **report}

def audit(stage, private_consumer=None):
    entries,types,_=all_model_entries(stage)
    if [e["id"] for e in entries]!=["M00","M01","M02","M03","M04","M05"]:
        raise ValueError("GFX108_SOURCE_MODEL_SELECTION_DRIFT")
    selection,_=selected_five(stage)
    for i,e in enumerate(entries[1:]):
        source=selection["selected"][i]
        if (source["owner"],source["mesh_pid"])!=(e["owner"],e["mesh_pid"]):
            raise ValueError("GFX108_EXACT_MESH_SOURCE_IDENTITY_CHANGED")
        e["game_object_pid"]=source["game_object_pid"]
    import UnityPy
    externals={}
    for owner in types:
        env=UnityPy.load(str(stage/owner))
        externals[owner]=[x.path for x in env.file.externals]
    cases=[inspect_exact_source_skin(e,types,externals,private_consumer) for e in entries]
    totals=Counter()
    for c in cases:
        totals["status_"+c["status"]]+=1
        if c.get("cpu_original_vertices_deformed"):
            totals["deformed_original_source_vertices"]+=c["vertices_cpu_deformed"]
            totals["source_vertices_displaced_from_first_bone_reference"]+=c[
                "cpu_vertices_different_from_first_bone_reference_at_1e4"]
    return {
        "experiment":"GFX-MULTI-108",
        "source_sha":ZIP2_SHA,
        "original_six_models":6,
        "original_mesh_indexed_cpu_skinning_cases":cases,
        "safe_aggregate":dict(totals),
        "cpu_pose_is_source_serialized_snapshot_only":True,
        "source_original_animation_clip_restored":False,
        "source_vertex_vs_original_game_gpu_pixels_verified":False,
        "source_renderer_mesh_to_world_parity_verified":False,
        "android_gpu_skinning_verified":False,
        "original_rig_restored":False,
        "originalShaderRestored":False,
        "phase_closed":False,
        "private_original_vertex_or_skin_data_exported":False
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--zip2",type=Path,required=True)
    ap.add_argument("--stage",type=Path,required=True)
    ap.add_argument("--safe",type=Path,required=True)
    a=ap.parse_args()
    report=audit(stage_originals(a.zip2,a.stage))
    a.safe.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GFX108_ORIGINAL_INDEXED_CPU_SKIN_SAFE "+json.dumps(report,sort_keys=True))
if __name__=="__main__":main()
