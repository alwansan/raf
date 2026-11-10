#!/usr/bin/env python3
"""GFX-MULTI-007: original OBJ referenced vs unreferenced vertex audit.

Public results only numeric counts and yes/no checks; no original OBJ, vertex,
UV, texture, GUID, Mesh name or coordinate is printed or published.
"""
import argparse,json
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,export_one,ZIP2_SHA
from gfxlab.tools.multi_model_transport import all_model_entries

DEVICE_UNITY_IMPORTED={"M00":375,"M01":4721,"M02":1662,
                        "M03":2163,"M04":2071,"M05":4452}

def inspect_obj(text):
    vertices=normals=uvs=0;faces=0;used=set();used_uv=set();used_normal=set()
    for line in text.splitlines():
        if line.startswith("v "):vertices+=1
        elif line.startswith("vt "):uvs+=1
        elif line.startswith("vn "):normals+=1
        elif line.startswith("f "):
            faces+=1
            tokens=line[2:].split()
            if len(tokens)!=3:raise ValueError("OBJ_TRIANGLES_NOT_THREE")
            for token in tokens:
                parts=token.split("/")
                def parse_idx(s, size):
                    if not s:return None
                    i=int(s)
                    real=i if i>0 else size+1+i
                    if not (1<=real<=size):raise ValueError("OBJ_INDEX_OUT_OF_RANGE")
                    return real
                used.add(parse_idx(parts[0],vertices))
                if len(parts)>1 and parts[1]:used_uv.add(parse_idx(parts[1],uvs))
                if len(parts)>2 and parts[2]:used_normal.add(parse_idx(parts[2],normals))
    if not vertices or not faces or None in used:raise ValueError("OBJ_EMPTY_OR_INVALID")
    return dict(declared_vertices=vertices,referenced_vertices=len(used),
        unreferenced_vertices=vertices-len(used),source_uv_declarations=uvs,
        source_normal_declarations=normals,referenced_uvs=len(used_uv),
        referenced_normals=len(used_normal),source_triangles=faces)

def audit(stage):
    entries,types,_=all_model_entries(stage)
    if [x["id"] for x in entries]!=list(DEVICE_UNITY_IMPORTED):
        raise ValueError("ORIGINAL_MODEL_SELECTION_DRIFT")
    models=[]
    for e in entries:
        obj=types[e["owner"]].get(e["mesh_pid"])
        if obj is None or obj.type.name!="Mesh":raise ValueError("ORIGINAL_MESH_MISSING")
        text,source_v,source_triangles=export_one(obj)
        d=inspect_obj(text)
        if d["declared_vertices"]!=source_v or d["source_triangles"]!=source_triangles:
            raise ValueError("SOURCE_OBJ_COUNTERS_DO_NOT_MATCH")
        observed=DEVICE_UNITY_IMPORTED[e["id"]]
        d.update(model=e["id"],unity_device_imported_vertices=observed,
            source_minus_device_vertex_delta=source_v-observed,
            unreferenced_vertex_count_matches_delta=d["unreferenced_vertices"]==source_v-observed,
            missing_original_tangent_and_rig_parity_proof=True)
        models.append(d)
    return dict(experiment="GFX-MULTI-007",source_sha=ZIP2_SHA,
        source_model_count=len(models),models=models,
        original_shader_restored=False,vertex_stream_parity_verified=False,
        unreferenced_vertex_diagnosis_only=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();r=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("GFX_MULTI007_SAFE_OBJ_USAGE "+json.dumps(r,sort_keys=True))
if __name__=="__main__":main()
