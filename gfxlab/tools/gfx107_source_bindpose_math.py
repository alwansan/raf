"""GFX107: source-private Unity TRS/bindpose matrix consistency witness.

No source vectors, bone identities, matrices, PPtrs or vertex coordinates appear
in public output. This checks *current serialized source pose*, not animation,
full original shader runtime, PC↔Android pixels or a proven bind rest pose.

Unity Mesh.bindposes[i] corresponds to SkinnedMeshRenderer.bones[i].
For each bone, source snapshot world(bone) * bindpose[i] should converge to
one mesh-space transform only if the snapshot is the original bind pose.
If it does not converge, record disagreement; DO NOT rewrite source transforms.
"""
from __future__ import annotations
import math
from collections import Counter

MAX_DEPTH=512
MAX_BONES=512
EPS=1e-4
MATRIX_KEYS=("e","m")

def _num(x):
    if type(x) not in (int,float) or not math.isfinite(x) or abs(x)>1e12:
        raise ValueError("GFX107_BAD_MATRIX_OR_TRANSFORM_SCALAR")
    return float(x)

def identity():
    return (1.,0.,0.,0., 0.,1.,0.,0., 0.,0.,1.,0., 0.,0.,0.,1.)

def mul(a,b):
    if len(a)!=16 or len(b)!=16:raise ValueError("GFX107_MATRIX_SHAPE")
    return tuple(sum(a[4*r+k]*b[4*k+c] for k in range(4))
                 for r in range(4) for c in range(4))

def max_delta(a,b):
    if len(a)!=16 or len(b)!=16:raise ValueError("GFX107_MATRIX_SHAPE")
    return max(abs(x-y) for x,y in zip(a,b))

def source_matrix4(obj):
    """Decode only explicitly indexed e00..e33 / m00..m33 row/column labels.

    No interpretation of a naked 16-element float list: Unity's serialized
    column-major backing memory must not be guessed from an untyped array.
    """
    if not isinstance(obj,dict):raise ValueError("GFX107_BINDPOSE_MATRIX_SHAPE")
    for prefix in MATRIX_KEYS:
        keys=[prefix+str(r)+str(c) for r in range(4) for c in range(4)]
        if all(k in obj for k in keys):
            return tuple(_num(obj[k]) for k in keys)
    raise ValueError("GFX107_BINDPOSE_MATRIX_LAYOUT_UNRECOGNIZED")

def source_transform_trs(obj):
    if not isinstance(obj,dict):raise ValueError("GFX107_TRANSFORM_SHAPE")
    def vec(key,axes):
        d=obj.get(key)
        if not isinstance(d,dict):raise ValueError("GFX107_TRANSFORM_COMPONENT_MISSING")
        return tuple(_num(d.get(k)) for k in axes)
    (x,y,z)=vec("m_LocalPosition",("x","y","z"))
    (qx,qy,qz,qw)=vec("m_LocalRotation",("x","y","z","w"))
    sx,sy,sz=vec("m_LocalScale",("x","y","z"))
    norm=qx*qx+qy*qy+qz*qz+qw*qw
    if not .99<=norm<=1.01:
        raise ValueError("GFX107_TRANSFORM_QUATERNION_NOT_UNIT")
    if not all(abs(s)>=1e-10 for s in (sx,sy,sz)):
        raise ValueError("GFX107_NONINVERTIBLE_TRANSFORM_SCALE")
    # Unity TRS (column-vector coordinates): T*R*S.
    xx=qx*qx;yy=qy*qy;zz=qz*qz
    xy=qx*qy;xz=qx*qz;yz=qy*qz
    wx=qw*qx;wy=qw*qy;wz=qw*qz
    return (
        (1-2*(yy+zz))*sx, (2*(xy-wz))*sy, (2*(xz+wy))*sz,x,
        (2*(xy+wz))*sx, (1-2*(xx+zz))*sy, (2*(yz-wx))*sz,y,
        (2*(xz-wy))*sx, (2*(yz+wx))*sy, (1-2*(xx+yy))*sz,z,
        0.,0.,0.,1.
    )

def source_world_matrix(node_key,lookup,parent_of):
    """Compute authentic source global TRS from root-null ancestry, fail closed.

    lookup(key): raw original Transform typetree; parent_of(key, transform)
    returns source PPtr target key or None for the *verified* null parent.
    """
    trail=[];seen=set();cur=node_key
    while cur is not None:
        if cur in seen:raise ValueError("GFX107_TRANSFORM_PARENT_CYCLE")
        if len(trail)>=MAX_DEPTH:raise ValueError("GFX107_TRANSFORM_PARENT_DEPTH")
        seen.add(cur)
        node=lookup(cur)
        if not isinstance(node,dict):raise ValueError("GFX107_TRANSFORM_UNRESOLVED")
        local=source_transform_trs(node)
        trail.append(local)
        cur=parent_of(cur,node)
    world=identity()
    for matrix in reversed(trail):
        world=mul(world,matrix)
    return world

def compute_bindpose_consistency(bindposes,bone_world_matrices):
    """Bounded full-matrix bone.world * mesh.bindpose snapshot consistency."""
    if not isinstance(bindposes,list) or not isinstance(bone_world_matrices,list):
        raise ValueError("GFX107_BINDPOSE_OR_BONE_LIST_INVALID")
    if not 1<=len(bindposes)==len(bone_world_matrices)<=MAX_BONES:
        raise ValueError("GFX107_BINDPOSE_BONE_COUNT_MISMATCH")
    matrices=[mul(w,source_matrix4(b)) for w,b in zip(bone_world_matrices,bindposes)]
    base=matrices[0]
    deltas=[max_delta(m,base) for m in matrices]
    maximum=max(deltas)
    coherent=sum(delta<=EPS for delta in deltas)
    return {
        "source_bone_matrix_count":len(bone_world_matrices),
        "source_bindpose_matrix_count":len(bindposes),
        "source_bindpose_decoded_count":len(matrices),
        "source_pose_products_coherent_at_1e4":coherent,
        "source_pose_products_all_coherent_at_1e4":coherent==len(matrices),
        "source_pose_products_max_abs_disagreement":round(maximum,8),
        "source_pose_snapshot_is_confirmed_bind_pose":False,
        "source_runtime_skinning_cpu_vertices_compared":False,
        "original_rest_pose_restored":False,
    }
