"""Independent route join on actual authored public exporter YAML, no game."""
from copy import deepcopy
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import tempfile

from scripts import gt_renderer_submesh_routes as gate
from scripts import gt_mesh_vertex_payload as payload
import struct


def need(test,reason):
    if not test:raise ValueError(reason)


def load(root):
    root=Path(root)
    source=gate.strict_json(gate.bounded_snapshot(root/"source.json",1024*1024))
    producer=gate.strict_json(gate.bounded_snapshot(root/"producer.json",256*1024))
    need(producer.get("status")=="OBSERVED_AUTHORED_PUBLIC_YAML_EXPORT" and
         producer.get("actual_public_export_collections")==9 and
         producer.get("actual_scene_collections")==2 and producer.get("original_assets_read") is False,
         "authored_producer_contract")
    need(source.get("authored_generated_objects") is True and source.get("schema_version")==2,
         "authored_source_contract")
    objects={};proofs={}
    for row in source["objects"]:
        key=(row["owner"],row["path_id"]);cls=row["class_id"]
        need(key not in objects and cls in gate.CLASSES,"authored_source_identity_collision")
        if cls==43:
            proof=payload.source_request(row["tree"])
            need(isinstance(proof,payload.Proof) and proof.length==120,"authored_120_byte_mesh_required")
            proofs[key]=proof
        objects[key]=(cls,gate.mesh_layout(row["tree"]) if cls==43 else row["tree"])
    externals=source["externals"]
    need(set(externals)=={key[0] for key in objects},"authored_external_table_population")
    traces=[gate.strict_json(gate.bounded_snapshot(root/f,1024*1024)) for f in ("materials.json","meshes.json","components.json")]
    mapping=gate.traces(*traces)
    need(set(mapping)==set(objects),"actual_trace_population_mismatch")
    hidden={(row["owner"],row["path_id"]) for row in source["hidden"]}
    need(len(hidden)==2 and not hidden&set(mapping),"hidden_trace_not_excluded")
    renderers=sorted(key for key,(cls,_) in objects.items() if cls==23)
    materials=sorted(key for key,(cls,_) in objects.items() if cls==21)
    need(len(renderers)==len(materials)==2 and renderers[0][1]==renderers[1][1] and materials[0][1]==materials[1][1],
         "same_pathID_different_owner_control_missing")
    need(externals[renderers[0][0]]!=externals[renderers[1][0]],"different_external_table_order_missing")
    return objects,externals,mapping,hidden,renderers,materials,producer,proofs


def scene_row(text,anchor,cls,transform):
    heads=list(gate.HEADER.finditer(text))
    hits=[i for i,h in enumerate(heads) if int(h[1])==cls and int(h[2])==anchor]
    need(len(hits)==1,"actual_authored_yaml_document_missing")
    i=hits[0];start=heads[i].start();end=heads[i+1].start() if i+1<len(heads) else len(text)
    return text[:start]+transform(text[start:end])+text[end:]


def audit(root,out):
    root=Path(root);out=Path(out)
    need(not out.exists() and out.parent.is_dir(),"fresh_aggregate_receipt_required")
    objects,externals,mapping,hidden,renderers,materials,producer,proofs=load(root)
    files,docs=gate.actual_index(root/"project",mapping)
    need(len(docs)==len(objects) and all(k in docs for _,p,_ in mapping.values() for k in (p[:2],)),
         "actual_native_documents_missing")
    # Native exporter produced all classes, so no imported-image fallback.
    need(sum(cls==28 for cls,_ in docs.values())==2 and sum(cls==48 for cls,_ in docs.values())==2,
         "actual_native_shader_texture_documents_required")
    baseline=gate.compare(objects,externals,mapping,files,docs,vertex_payloads=proofs)
    need(baseline["selected_renderer_routes_preserved"],"baseline_not_preserved:"+json.dumps(baseline["reason_counts"],sort_keys=True))
    need(baseline["selected_same_route_vertex_and_UV_bytes_verified"],"authored_payload_not_bound")
    counts=baseline["counts"]
    for k,v in {"source_renderers":2,"complete_renderer_routes":2,
                "complete_submesh_material_identity_routes":4,"renderer_mesh_layouts_matched":2,
                "ordered_material_slots_matched":4,"material_shader_links_matched":4,
                "material_texenv_slots_matched":4,"complete_vertex_byte_bound_renderer_routes":2,
                "complete_vertex_byte_bound_submesh_routes":4}.items():need(counts.get(k)==v,"baseline_count:"+k)
    rp=mapping[renderers[0]][1];other=mapping[renderers[1]][1]
    need(rp[0]!=other[0],"separate_scene_documents_required")
    scene_path=files[rp[0]][0]
    controls={}
    def record(name,report,reason):
        need(not report["selected_renderer_routes_preserved"] and report["reason_counts"].get(reason,0)>0,
             "counterfactual_not_rejected:"+name+":"+str(report["reason_counts"]))
        controls[name]={"reason":reason,"mismatched":report["counts"].get("mismatched_renderer_routes",0),
                         "unproven":report["counts"].get("unproven_renderer_routes",0)}
    def disk_control(name,mutator,reason,asset_path=scene_path):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"project";shutil.copytree(root/"project",p)
            dest=p/asset_path.relative_to(root/"project")
            text=dest.read_text()
            changed=mutator(text);need(changed!=text,"no_counterfactual_mutation")
            dest.write_text(changed)
            f,d=gate.actual_index(p,mapping)
            record(name,gate.compare(objects,externals,mapping,f,d,vertex_payloads=proofs),reason)
    def swap(body):
        hit=re.search(r"(?m)^  m_Materials:\s*\n((?:  - \{[^\r\n]+\}\r?\n){2})",body)
        need(hit is not None,"actual_material_array_shape_unavailable")
        lines=hit[1].splitlines(keepends=True);need(len(lines)==2,"actual_two_material_slots_required")
        return body[:hit.start(1)]+lines[1]+lines[0]+body[hit.end(1):]
    disk_control("swap_existing_materials_in_real_YAML",lambda text:scene_row(text,rp[1],23,swap),"ordered_pointer_target_mismatch")
    # Other scene has a real GameObject with matching class but different doc.
    go=gate.src_target(renderers[0][0],objects[renderers[0]][1]["m_GameObject"],externals)
    other_go=gate.src_target(renderers[1][0],objects[renderers[1]][1]["m_GameObject"],externals)
    gp=mapping[go][1];ogp=mapping[other_go][1]
    def foreign(body):
        result,n=re.subn(r"(?m)^  m_GameObject: \{fileID: -?\d+\}$",
                         f"  m_GameObject: {{fileID: {ogp[1]}, guid: {ogp[0]}, type: 2}}",body)
        need(n==1,"actual_gameobject_pointer_shape_unavailable")
        return result
    disk_control("foreign_scene_gameobject_in_real_YAML",lambda text:scene_row(text,rp[1],23,foreign),"ordered_pointer_target_mismatch")
    def nonlocal_backref(body):
        result,n=re.subn(r"(?m)^  m_GameObject: \{fileID: -?\d+\}$",
                         f"  m_GameObject: {{fileID: {gp[1]}, guid: {gp[0]}, type: 2}}",body)
        need(n==1,"actual_gameobject_pointer_shape_unavailable");return result
    disk_control("same_document_but_nonlocal_gameobject_reference",lambda text:scene_row(text,rp[1],23,nonlocal_backref),"renderer_gameobject_not_local")
    def stripped(text):
        return scene_row(text,rp[1],23,lambda body:body.replace(f"--- !u!23 &{rp[1]}\n",f"--- !u!23 &{rp[1]} stripped\n",1))
    disk_control("stripped_renderer_is_not_complete",stripped,"missing_actual_serialized_target")
    # Same-size UV and position changes in the actual native Mesh YAML.
    mp=mapping[next(iter(proofs))][1]
    def change_vertex(body,offset):
        hit=re.search(r"(?m)^(\s*_typelessdata:[ \t]*)([0-9a-fA-F]+)[ \t]*$",body)
        need(hit is not None,"actual_vertex_hex_missing")
        raw=bytearray.fromhex(hit[2])
        need(len(raw)==120,"actual_vertex_payload_size")
        old=bytes(raw)
        raw[offset:offset+4]=struct.pack("<f",.375)
        need(bytes(raw)!=old,"actual_vertex_control_no_mutation")
        return body[:hit.start(2)]+raw.hex()+body[hit.end(2):]
    for name,offset in (("actual_YAML_same_size_UV_bytes_drift",12),
                        ("actual_YAML_same_size_position_bytes_drift",0)):
        disk_control(name,lambda text:scene_row(text,mp[1],43,lambda body:change_vertex(body,offset)),
                     "same_route_vertex_or_UV_bytes_drift",files[mp[0]][0])
    # Actual trace identity with source and export owner confusion.
    table=deepcopy(externals);table[renderers[0][0]]=list(reversed(table[renderers[0][0]]))
    # Change only the two dependency entries for the two valid Materials,
    # preserving the mesh provider and every local component reference.
    table=deepcopy(externals);ls=table[renderers[0][0]]
    i,j=ls.index(materials[0][0]),ls.index(materials[1][0]);ls[i],ls[j]=ls[j],ls[i]
    record("source_external_table_swapped_same_PathIDs",gate.compare(objects,table,mapping,files,docs,vertex_payloads=proofs),"ordered_pointer_target_mismatch")
    altered=deepcopy(mapping);cls,p,exp=altered[renderers[0]];altered[renderers[0]]=(cls,(p[0],p[1],0),exp)
    record("unscoped_type0_trace",gate.compare(objects,externals,altered,files,docs,vertex_payloads=proofs),"unproven_exportable_global_target")
    altered=deepcopy(mapping);cls,p,exp=altered[renderers[0]];altered[renderers[0]]=(cls,(p[0],p[1],3),exp)
    record("wrong_global_serialized_type",gate.compare(objects,externals,altered,files,docs,vertex_payloads=proofs),"serialized_document_trace_type_mismatch")
    altered=deepcopy(mapping);cls,p,exp=altered[renderers[0]];altered[renderers[0]]=(cls,p,False)
    record("nonexportable_component_trace",gate.compare(objects,externals,altered,files,docs,vertex_payloads=proofs),"unproven_exportable_global_target")
    # Hidden components must have no actual YAML document/trace. Since they
    # are intentionally excluded from this authored baseline, add them to
    # the source census and show that it cannot falsely claim full closure.
    augmented=dict(objects)
    for key in hidden:augmented[key]=(23,{})
    record("hidden_source_renderers_not_promoted",gate.compare(augmented,externals,mapping,files,docs,vertex_payloads=proofs),"missing_source_export_trace")
    result=dict(status="PASS_ACTUAL_AUTHORED_PUBLIC_SCENE_YAML_ROUTE_JOIN",producer=producer,
                actual_exported_documents=len(docs),actual_native_scene_files=2,source_generated_object_count=len(objects),
                baseline=baseline,counterfactuals=controls,counterfactual_count=len(controls),
                same_PathID_distinct_owners=True,actual_cross_owner_dependency_order=True,
                source_contract_captured_before_export=True,hidden_source_renderers_excluded_from_baseline_but_not_promoted=True,
                original_assets_read=False,original_serialized_source_verified=False,production_renderer_parity_verified=False,
                vertex_payload_bytes_verified=True,UV_decoded_values_or_GPU_verified=False,XAPK=False)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--root",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();r=audit(a.root,a.out);print(json.dumps(r,sort_keys=True))
    return 0


if __name__=="__main__":raise SystemExit(main())
