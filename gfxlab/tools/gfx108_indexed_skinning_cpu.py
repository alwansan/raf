"""GFX108 original-index-preserving CPU linear blend skinning candidate.

Never reweld vertices or reconstruct from an imported OBJ. Only accept direct
UnityPy parsed Mesh m_Vertices in original array order, strict per-source-
vertex BoneWeight indices and the original Renderer bones/mesh bindposes.
A decoded CPU pose is NOT original animation or Android GPU proof.
"""
from __future__ import annotations
import math

MAX_VERTS=150_000
MAX_BONES=512
WEIGHT_EPS=1e-3

def scalar(v):
    if type(v) not in (float,int) or not math.isfinite(v) or abs(v)>1e10:
        raise ValueError("GFX108_BAD_FINITE_SCALAR")
    return float(v)

def positions_from_parsed_mesh(parsed,vertex_count):
    """Use original indexed mesh positions, NEVER OBJ import/weld order."""
    if type(vertex_count)!=int or not 1<=vertex_count<=MAX_VERTS:
        raise ValueError("GFX108_VERTEX_COUNT_BOUNDS")
    arr=getattr(parsed,"m_Vertices",None)
    if not isinstance(arr,(list,tuple)) or not arr:
        raise ValueError("GFX108_DIRECT_VERTEX_POSITIONS_UNAVAILABLE")
    if len(arr)==3*vertex_count and all(type(x) in (int,float) for x in arr[:3]):
        return [tuple(scalar(arr[3*i+k]) for k in range(3)) for i in range(vertex_count)]
    if len(arr)!=vertex_count:
        raise ValueError("GFX108_DIRECT_VERTEX_COUNT_MISMATCH")
    out=[]
    for v in arr:
        if isinstance(v,(list,tuple)):
            if len(v)!=3:raise ValueError("GFX108_VERTEX_LAYOUT_UNRECOGNIZED")
            out.append(tuple(scalar(v[k]) for k in range(3)))
        elif isinstance(v,dict):
            keys=("x","y","z") if all(k in v for k in ("x","y","z")) else ("X","Y","Z")
            if not all(k in v for k in keys):raise ValueError("GFX108_VERTEX_LAYOUT_UNRECOGNIZED")
            out.append(tuple(scalar(v[k]) for k in keys))
        else:
            if all(hasattr(v,k) for k in ("x","y","z")):keys=("x","y","z")
            elif all(hasattr(v,k) for k in ("X","Y","Z")):keys=("X","Y","Z")
            else:raise ValueError("GFX108_VERTEX_LAYOUT_UNRECOGNIZED")
            out.append(tuple(scalar(getattr(v,k)) for k in keys))
    return out

def decoded_skin_weights(typetree,vertex_count,bone_count):
    """Typed Unity Mesh.m_Skin BoneWeight array; do not infer from OBJ order."""
    if not isinstance(typetree,dict):raise ValueError("GFX108_MESH_TYPETREE_INVALID")
    arr=typetree.get("m_Skin")
    if not isinstance(arr,list) or len(arr)!=vertex_count:
        raise ValueError("GFX108_ORIGINAL_SKIN_ARRAY_MISSING_OR_COUNT_DRIFT")
    if type(bone_count)!=int or not 1<=bone_count<=MAX_BONES:
        raise ValueError("GFX108_BONE_COUNT_INVALID")
    out=[]
    for record in arr:
        if not isinstance(record,dict):raise ValueError("GFX108_SKIN_RECORD_LAYOUT")
        ws=record.get("weight");ix=record.get("boneIndex")
        if not isinstance(ws,list) or not isinstance(ix,list) or len(ws)!=4 or len(ix)!=4:
            raise ValueError("GFX108_SKIN_INFLUENCES_SHAPE")
        pairs=[]
        for w,i in zip(ws,ix):
            w=scalar(w)
            if w<0 or w>1.00001 or type(i)!=int:raise ValueError("GFX108_BONE_WEIGHT_RANGE")
            if w>0:
                if i<0 or i>=bone_count:raise ValueError("GFX108_BONE_INDEX_OUT_OF_RANGE")
                pairs.append((w,i))
        if abs(sum(w for w,_ in pairs)-1.0)>WEIGHT_EPS:
            raise ValueError("GFX108_BONE_WEIGHT_SUM_NOT_NORMALIZED")
        out.append(pairs)
    return out


def decoded_handler_skin(mesh_handler,vertex_count,bone_count):
    """Use MeshHandler.process() original same-index m_BoneWeights/Indices.

    The handler extracts all three arrays from the SAME VertexData channel
    layout. No OBJ coordinate conversion, no weld, no guessed reindexing.
    """
    weights=getattr(mesh_handler,"m_BoneWeights",None)
    indices=getattr(mesh_handler,"m_BoneIndices",None)
    if (not isinstance(weights,(tuple,list)) or
        not isinstance(indices,(tuple,list)) or
        len(weights)!=len(indices) or len(weights)!=vertex_count):
        raise ValueError("GFX108_DIRECT_MESH_HANDLER_SKIN_CHANNELS_UNAVAILABLE")
    raw=[]
    for ws,ix in zip(weights,indices):
        if not isinstance(ws,(list,tuple)) or not isinstance(ix,(list,tuple)):
            raise ValueError("GFX108_DIRECT_HANDLER_BONE_WEIGHT_LAYOUT")
        raw.append({"weight":list(ws),"boneIndex":list(ix)})
    return decoded_skin_weights({"m_Skin":raw},vertex_count,bone_count)

def transform_point(matrix,point):
    if len(matrix)!=16 or len(point)!=3:raise ValueError("GFX108_MATRIX_POINT_SHAPE")
    x,y,z=point
    w=matrix[12]*x+matrix[13]*y+matrix[14]*z+matrix[15]
    if not math.isfinite(w) or abs(w)<1e-10:
        raise ValueError("GFX108_AFFINE_HOMOGENEOUS_W_INVALID")
    return tuple(sum(matrix[4*r+c]*p for c,p in enumerate((x,y,z,1.)))/w
                 for r in range(3))

def skin_positions_cpu(positions,weights,bone_world,bindpose_matrices):
    """CPU LBS: sum_j weight_ij (bone_world_j*bindpose_j) * position_i."""
    from gfxlab.tools.gfx107_source_bindpose_math import mul
    if not (len(positions)==len(weights)>0 and
            len(bone_world)==len(bindpose_matrices)>0):
        raise ValueError("GFX108_ARRAY_COUNT_MISMATCH")
    combined=[mul(w,b) for w,b in zip(bone_world,bindpose_matrices)]
    points=[]
    for p,influences in zip(positions,weights):
        if not influences:raise ValueError("GFX108_ZERO_WEIGHT_VERTEX")
        v=[0.,0.,0.]
        for w,index in influences:
            b=transform_point(combined[index],p)
            for k in range(3):v[k]+=w*b[k]
        if not all(math.isfinite(x) for x in v):
            raise ValueError("GFX108_DEFORMED_VERTEX_NONFINITE")
        points.append(tuple(v))
    return points

def safe_displacement_stats(deformed,positions,reference_matrix):
    """Bounded aggregate vs first-bone common reference. Not source PC image."""
    if len(deformed)!=len(positions):
        raise ValueError("GFX108_DEFORMED_COUNT_DRIFT")
    maximum=0.;total=0.;changed=0
    for actual,p in zip(deformed,positions):
        ideal=transform_point(reference_matrix,p)
        d=math.sqrt(sum((a-b)**2 for a,b in zip(actual,ideal)))
        maximum=max(maximum,d);total+=d
        changed+=d>1e-4
    return {"vertices_cpu_deformed":len(deformed),
        "cpu_vertices_different_from_first_bone_reference_at_1e4":changed,
        "cpu_vertex_mean_distance_from_first_bone_reference":round(total/len(deformed),7),
        "cpu_vertex_max_distance_from_first_bone_reference":round(maximum,7),
        "original_animation_pose_verified":False,
        "android_gpu_skinning_verified":False,
        "original_rig_restored":False}
