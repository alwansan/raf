#!/usr/bin/env python3
"""GFX-MULTI-008: numeric-only inspection of duplicate original OBJ attributes.

Inspects exact original source geometry privately. Never prints private vertex,
normal, UV coordinates, mesh, shader identifiers, or writes original OBJ/PNGs.
Do not claim Unity importer identity without source+Unity byte-level parity.
"""
import argparse,struct,json
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,export_one,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries

DEVICE_COUNTS={"M00":375,"M01":4721,"M02":1662,"M03":2163,"M04":2071,"M05":4452}
def float_bits(s):
    return struct.pack("<f",float(s))
def inspect_obj_attributes(data):
    pos=[];uv=[];normal=[];pos_refs=set();posuv=set();all_keys=set();ncorner=tri=0
    def idx(text,count):
        x=int(text)
        if x==0:raise ValueError("OBJ_ZERO_INDEX")
        x=x-1 if x>0 else count+x
        if x<0 or x>=count:raise ValueError("OBJ_OUT_OF_RANGE_INDEX")
        return x
    for line in data.splitlines():
        if line.startswith("v "):
            vals=line.split()
            if len(vals)<4:raise ValueError("OBJ_BAD_POS")
            pos.append(tuple(float_bits(x) for x in vals[1:4]))
        elif line.startswith("vt "):
            vals=line.split()
            if len(vals)<3:raise ValueError("OBJ_BAD_UV")
            uv.append(tuple(float_bits(x) for x in vals[1:3]))
        elif line.startswith("vn "):
            vals=line.split()
            if len(vals)<4:raise ValueError("OBJ_BAD_NORMAL")
            normal.append(tuple(float_bits(x) for x in vals[1:4]))
        elif line.startswith("f "):
            corners=line.split()[1:]
            if len(corners)!=3:raise ValueError("OBJ_FACE_NONTRIANGLE")
            tri+=1
            for token in corners:
                t=token.split("/")
                if not t or len(t)>3 or not t[0]:raise ValueError("OBJ_BAD_CORNER")
                p=idx(t[0],len(pos));u=idx(t[1],len(uv)) if len(t)>1 and t[1] else None
                n=idx(t[2],len(normal)) if len(t)>2 and t[2] else None
                pos_refs.add(p)
                posuv.add((pos[p],uv[u] if u is not None else None))
                all_keys.add((pos[p],uv[u] if u is not None else None,normal[n] if n is not None else None))
                ncorner+=1
    if not pos or not tri or not pos_refs:raise ValueError("OBJ_NO_TRIANGLE_GEOMETRY")
    return dict(source_declared_vertices=len(pos),referenced_source_indices=len(pos_refs),
       distinct_position_float32=len({pos[k] for k in pos_refs}),
       distinct_position_uv_float32=len(posuv),
       distinct_position_uv_normal_float32=len(all_keys),
       source_triangles=tri,source_face_corners=ncorner,
       exact_importer_attribute_parity_proven=False)

def audit(stage):
    entries,typed,_=all_model_entries(stage);models=[]
    if [x["id"] for x in entries]!=list(DEVICE_COUNTS):
        raise ValueError("MESH_SOURCE_SELECTION_DRIFT")
    for e in entries:
        obj=typed[e["owner"]].get(e["mesh_pid"])
        if obj is None or obj.type.name!="Mesh":raise ValueError("TYPED_MESH_MISSING")
        source_text,nv,nt=export_one(obj)
        d=inspect_obj_attributes(source_text)
        if (nv,nt)!=(d["source_declared_vertices"],d["source_triangles"]):
            raise ValueError("SOURCE_OBJ_PARITY_DRIFT")
        observed=DEVICE_COUNTS[e["id"]]
        d.update(model=e["id"],unity_observed_imported_vertices=observed,
                 possible_identical_attribute_merges=nv-d["distinct_position_uv_normal_float32"],
                 attribute_dedup_count_matches_unity_import=d["distinct_position_uv_normal_float32"]==observed)
        models.append(d)
    return dict(experiment="GFX-MULTI-008",source_sha=ZIP2_SHA,
        models=models,source_models=len(models),exact_original_vertex_stream_parity_proven=False,
        original_shader_restored=False,android_original_program_verified=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI008_SAFE_DUPLICATE_ATTRIBUTE_COUNTS "+json.dumps(d,sort_keys=True))
if __name__=="__main__":main()
