#!/usr/bin/env python3
"""Source mesh Wavefront-OBJ integrity check and bounded missing-normal repair.

No original model geometry in repository. Applied solely to UnityPy private
OBJ export inside CI. Keeps source vertices, UV coordinates, triangles and
material/submesh group ordering. Where original export lacks normals, calculates
non-proprietary area-weighted normals from original faces to support Unity ModelImporter.
This is a diagnostic approximation, NOT original exact authored normal semantics.
"""
from __future__ import annotations
import math

def _index(text,count):
    if not text:raise ValueError("OBJ corner required position index")
    value=int(text)
    if value==0:raise ValueError("OBJ index zero invalid")
    value=value-1 if value>0 else count+value
    if not 0<=value<count:raise ValueError("OBJ index outside current geometry")
    return value

def _unit(x,y,z):
    n=math.sqrt(x*x+y*y+z*z)
    return (x/n,y/n,z/n) if n>1e-18 else (0.0,1.0,0.0)

def normalize_exported_obj(data:str):
    """Return (sanitized_original_obj, private-safe import stats)."""
    if not isinstance(data,str) or len(data)>45_000_000:
        raise ValueError("OBJ output absent or exceeds bounded model size")
    verts=[];tex=[];norm=[];out=[];triangles=[]
    materials=[]
    for raw in data.splitlines():
        s=raw.strip()
        if not s:continue
        if s.startswith("v "):
            vals=s.split()
            if len(vals)<4:raise ValueError("OBJ vertex truncated")
            xyz=tuple(float(x) for x in vals[1:4])
            if not all(math.isfinite(x) for x in xyz):raise ValueError("OBJ nonfinite vertex")
            verts.append(xyz);out.append(s)
        elif s.startswith("vt "):
            fields=s.split()
            if len(fields)<3:raise ValueError("OBJ UV truncated")
            uv=(float(fields[1]),float(fields[2]))
            if not all(math.isfinite(x) for x in uv):raise ValueError("OBJ nonfinite UV")
            tex.append(uv);out.append(s)
        elif s.startswith("vn "):
            fields=s.split()
            if len(fields)<4:raise ValueError("OBJ normal truncated")
            xyz=tuple(float(x) for x in fields[1:4])
            if not all(math.isfinite(x) for x in xyz):raise ValueError("OBJ nonfinite normal")
            norm.append(xyz);out.append(s)
        elif s.startswith("f "):
            corners=[]
            for item in s.split()[1:]:
                bits=item.split("/")
                if len(bits)>3 or not bits:raise ValueError("OBJ face malformed")
                p=_index(bits[0],len(verts))
                t=_index(bits[1],len(tex)) if len(bits)>1 and bits[1] else None
                n=_index(bits[2],len(norm)) if len(bits)>2 and bits[2] else None
                corners.append((p,t,n))
            if len(corners)<3 or len(corners)>6:raise ValueError("OBJ unusual polygon face")
            for k in range(1,len(corners)-1):
                triangles.append((corners[0],corners[k],corners[k+1]))
        elif s.startswith("usemtl "):
            materials.append(s);out.append(("__MAT__",s))
        elif s.startswith(("o ","g ","s ","mtllib ","#")):
            out.append(s)
        else:
            # No unsafe extension or original private shader data copied.
            continue
    if not 128<=len(verts)<=140000 or not triangles:
        raise ValueError("OBJ has no valid bounded source topology")
    if not tex:
        raise ValueError("No source UV; cannot claim correct source textures")
    has_normals=bool(norm) and all(c[2] is not None for tri in triangles for c in tri)
    # Build standardized OBJ retaining source positions and texture coordinates.
    # Regroup faces while preserving exact usemtl boundaries: the original export
    # may have malformed or no normals but must keep submesh material references.
    face_output=[]
    source_lines=data.splitlines()
    # Keep material group order with faces, not all materials before all faces.
    # We reparse once using the final counts (OBJ exports write v/vt/vn before faces).
    if not has_normals:
        areas=[[0.0,0.0,0.0] for _ in verts]
        for tri in triangles:
            p1,p2,p3=[verts[x[0]] for x in tri]
            e1=[p2[i]-p1[i] for i in range(3)]
            e2=[p3[i]-p1[i] for i in range(3)]
            cross=(e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],
                   e1[0]*e2[1]-e1[1]*e2[0])
            for corner in tri:
                a=areas[corner[0]]
                a[0]+=cross[0];a[1]+=cross[1];a[2]+=cross[2]
        new_norm=[_unit(*a) for a in areas]
        norm=[*new_norm]
    output=[]
    for v in verts:output.append("v %.9g %.9g %.9g"%v)
    for t in tex:output.append("vt %.9g %.9g"%t)
    for n in norm:output.append("vn %.9g %.9g %.9g"%n)
    cursor=0
    for s in source_lines:
        s=s.strip()
        if s.startswith(("o ","g ","s ","usemtl ")):output.append(s)
        elif s.startswith("f "):
            items=s.split()[1:]
            corners=[]
            for token in items:
                bits=token.split("/")
                p=_index(bits[0],len(verts))
                t=_index(bits[1],len(tex)) if len(bits)>1 and bits[1] else None
                n=_index(bits[2],len(norm)) if len(bits)>2 and bits[2] else None
                if not has_normals:n=p
                corners.append((p,t,n))
            for i in range(1,len(corners)-1):
                tri=(corners[0],corners[i],corners[i+1])
                line=[]
                for p,t,n in tri:
                    if t is None:line.append(f"{p+1}//{n+1}")
                    else:line.append(f"{p+1}/{t+1}/{n+1}")
                output.append("f "+" ".join(line))
                cursor+=1
    if cursor!=len(triangles):raise ValueError("OBJ topology changed during normalization")
    result="\n".join(output)+"\n"
    stats={"source_vertices":len(verts),"source_uvs":len(tex),"triangles":len(triangles),
           "source_normals_present":has_normals,"normals_generated_for_unity":not has_normals,
           "material_group_markers":len(materials),"source_vertices_preserved":True,
           "source_uvs_preserved":True,"topology_preserved":True}
    return result,stats
