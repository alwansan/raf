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
from scripts import gt_texture_route_payload as texture_payload
import struct
import yaml


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
    need(source.get("authored_generated_objects") is True and source.get("schema_version")==5,
         "authored_source_contract")
    objects={};proofs={}
    for row in source["objects"]:
        key=(row["owner"],row["path_id"]);cls=row["class_id"]
        need(key not in objects and cls in gate.CLASSES,"authored_source_identity_collision")
        if cls==43:
            proof=payload.source_request(row["tree"])
            need(isinstance(proof,payload.Proof) and proof.length==120,"authored_120_byte_mesh_required")
            proofs[key]=proof
        if cls==28:
            proof=texture_payload.proof(row["tree"])
            need(proof.length==20 and proof.mip_lengths==(16,4),"authored_two_mip_RGBA32_required")
            objects[key]=(cls,proof)
        else:objects[key]=(cls,gate.mesh_layout(row["tree"]) if cls==43 else row["tree"])
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
    files,docs=gate.actual_index(root/"project",mapping,texture_payloads=True)
    need(len(docs)==len(objects) and all(k in docs for _,p,_ in mapping.values() for k in (p[:2],)),
         "actual_native_documents_missing")
    # Native exporter produced all classes, so no imported-image fallback.
    need(sum(cls==28 for cls,_ in docs.values())==2 and sum(cls==48 for cls,_ in docs.values())==2,
         "actual_native_shader_texture_documents_required")
    baseline=gate.compare(objects,externals,mapping,files,docs,vertex_payloads=proofs,material_values=True,material_keywords=True,texture_payloads=True)
    need(baseline["selected_renderer_routes_preserved"],"baseline_not_preserved:"+json.dumps(baseline["reason_counts"],sort_keys=True))
    need(baseline["selected_same_route_vertex_and_UV_bytes_verified"],"authored_payload_not_bound")
    need(baseline["selected_same_route_material_values_verified"],"authored_material_values_not_bound")
    need(baseline["selected_same_route_material_keyword_pass_state_verified"],"authored_keyword_state_not_bound")
    need(baseline["selected_nonnull_same_route_texture_payloads_verified"],"authored_texture_bytes_not_bound")
    counts=baseline["counts"]
    for k,v in {"source_renderers":2,"complete_renderer_routes":2,
                "complete_submesh_material_identity_routes":4,"renderer_mesh_layouts_matched":2,
                "ordered_material_slots_matched":4,"material_shader_links_matched":4,
                "material_texenv_slots_matched":4,"complete_vertex_byte_bound_renderer_routes":2,
                "complete_vertex_byte_bound_submesh_routes":4,
                "complete_material_value_bound_renderer_routes":2,
                "complete_material_value_bound_submesh_routes":4,
                "material_color_slots_matched":8,"material_float_slots_matched":8,
                "material_int_slots_matched":8,
                "complete_material_keyword_bound_renderer_routes":2,
                "complete_material_keyword_bound_submesh_routes":4,
                "material_valid_keyword_entries_matched":8,
                "material_invalid_keyword_entries_matched":4,
                "material_disabled_pass_entries_matched":4,
                "texture_payload_slots_matched":4,"texture_payload_bytes_matched_per_route":80,
                "texture_mip_levels_matched_per_route":8,
                "complete_texture_payload_bound_renderer_routes":2,
                "complete_texture_payload_bound_submesh_routes":4}.items():need(counts.get(k)==v,"baseline_count:"+k)
    rp=mapping[renderers[0]][1];other=mapping[renderers[1]][1]
    need(rp[0]!=other[0],"separate_scene_documents_required")
    scene_path=files[rp[0]][0]
    controls={}
    def record(name,report,reason):
        need(not report["selected_renderer_routes_preserved"] and report["reason_counts"].get(reason,0)>0,
             "counterfactual_not_rejected:"+name+":"+str(report["reason_counts"]))
        controls[name]={"reason":reason,"mismatched":report["counts"].get("mismatched_renderer_routes",0),
                         "unproven":report["counts"].get("unproven_renderer_routes",0)}
    def disk_control(name,mutator,reason,asset_path=scene_path,old_value_gate_passes=False,old_keyword_gate_passes=False,old_texture_gate_passes=False):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"project";shutil.copytree(root/"project",p)
            dest=p/asset_path.relative_to(root/"project")
            text=dest.read_text()
            changed=mutator(text);need(changed!=text,"no_counterfactual_mutation")
            dest.write_text(changed)
            f,d=gate.actual_index(p,mapping,texture_payloads=True)
            if old_value_gate_passes:
                old=gate.compare(objects,externals,mapping,f,d,vertex_payloads=proofs)
                need(old["selected_same_route_vertex_and_UV_bytes_verified"],"old_identity_gate_did_not_pass:"+name)
            if old_keyword_gate_passes:
                old=gate.compare(objects,externals,mapping,f,d,vertex_payloads=proofs,material_values=True)
                need(old["selected_same_route_material_values_verified"],"old_value_gate_did_not_pass:"+name)
            if old_texture_gate_passes:
                old=gate.compare(objects,externals,mapping,f,d,vertex_payloads=proofs,material_values=True,material_keywords=True)
                need(old["selected_same_route_material_keyword_pass_state_verified"],"old_keyword_gate_did_not_pass:"+name)
            record(name,gate.compare(objects,externals,mapping,f,d,vertex_payloads=proofs,material_values=True,material_keywords=True,texture_payloads=True),reason)
            if old_value_gate_passes:controls[name]["V2_vertex_identity_gate_passed"]=True
            if old_keyword_gate_passes:controls[name]["V3_material_value_gate_passed"]=True
            if old_texture_gate_passes:controls[name]["V4_material_keyword_gate_passed"]=True
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
    # Change only actual saved-value YAML tokens; preserve all PPtrs,
    # document identity, vertex bytes, and other properties. Verify V2
    # passes each control before requiring V3 to reject it.
    matp=mapping[materials[0]][1]
    def change_property(body,name,replacement,channel=None,rename=False):
        head,sep,yaml_body=body.partition("\n")
        need(bool(sep),"actual_material_document_header_missing")
        node=yaml.compose(yaml_body)
        def pairs(n):
            if isinstance(n,yaml.MappingNode):
                for k,v in n.value:
                    yield k,v
                    yield from pairs(v)
            elif isinstance(n,yaml.SequenceNode):
                for x in n.value:yield from pairs(x)
        found=[(k,v) for k,v in pairs(node) if isinstance(k,yaml.ScalarNode) and k.value==name]
        need(len(found)==1,"actual_material_property_not_unique")
        key,value=found[0]
        target=key if rename else value
        if channel is not None:
            need(isinstance(value,yaml.MappingNode),"actual_material_RGBA_shape")
            hits=[v for k,v in value.value if k.value==channel]
            need(len(hits)==1,"actual_material_RGBA_channel")
            target=hits[0]
        need(isinstance(target,yaml.ScalarNode),"actual_material_value_not_scalar")
        lo,hi=target.start_mark.index,target.end_mark.index
        need(yaml_body[lo:hi]!=replacement,"actual_material_control_no_mutation")
        return head+sep+yaml_body[:lo]+replacement+yaml_body[hi:]
    for name,prop,value,channel,rename,reason in (
        ("actual_YAML_tint_RGB_value_drift","_AuthoredTint","0.875","r",False,"material_color_value_drift"),
        ("actual_YAML_tint_alpha_value_drift","_AuthoredTint","0.125","a",False,"material_color_value_drift"),
        ("actual_YAML_float_value_drift","_AuthoredFloat","0.875",None,False,"material_float_value_drift"),
        ("actual_YAML_int_value_drift","_AuthoredInteger","16777216",None,False,"material_int_value_drift"),
        ("actual_YAML_missing_color_property","_AuthoredTint","_AuthoredUnexpected",None,True,"missing_material_color_slot"),
    ):
        disk_control(name,lambda text:scene_row(text,matp[1],21,
                         lambda body:change_property(body,prop,value,channel,rename)),
                     reason,files[matp[0]][0],old_value_gate_passes=True)
    # Mutate only keyword/pass fields in real Material YAML. Use YAML node
    # marks so the rest of the actual document is byte-for-byte unchanged.
    # Replace complete field lines (block or flow array) with a flow array.
    from scripts.gt_material_route_keyword_state import normalize as keyword_state
    from scripts.b43_material_keyword_fidelity import FIELDS
    source_state=objects[materials[0]][1]
    keyword_state(source_state)
    v,i,d=(list(source_state[k]) for k in FIELDS)
    need(len(v)==2 and len(i)==1 and len(d)==1,"authored_keyword_controls_population")
    def change_state(body,updates):
        head,sep,raw=body.partition("\n")
        need(bool(sep),"actual_material_document_header_missing")
        node=yaml.compose(raw)
        need(isinstance(node,yaml.MappingNode) and len(node.value)==1,"actual_material_state_root")
        material=node.value[0][1]
        need(isinstance(material,yaml.MappingNode),"actual_material_state_map")
        patches=[]
        for field,items in updates.items():
            hits=[(k,n) for k,n in material.value if k.value==field]
            need(len(hits)==1,"actual_material_state_field_not_unique")
            k,n=hits[0]
            need(isinstance(n,yaml.SequenceNode),"actual_material_state_not_array")
            # Include all indented list lines, but not next key's indentation.
            lo=raw.rfind("\n",0,k.start_mark.index)+1
            end=n.end_mark.index
            if end and raw[end-1]=="\n":
                hi=end
            else:
                line=raw.rfind("\n",0,end)+1
                if raw[line:end].strip()=="" and line>lo:hi=line
                else:
                    nl=raw.find("\n",end)
                    hi=len(raw) if nl<0 else nl+1
            indent=raw[lo:k.start_mark.index]
            need(indent.strip()=="" and hi>lo,"actual_material_state_line_span")
            replacement="" if items is None else indent+field+": "+json.dumps(items)+"\n"
            patches.append((lo,hi,replacement))
        for lo,hi,replacement in sorted(patches,reverse=True):
            raw=raw[:lo]+replacement+raw[hi:]
        return head+sep+raw
    for name,updates,reason in (
        ("actual_YAML_valid_invalid_bucket_swap",
         {FIELDS[0]:[v[0],i[0]],FIELDS[1]:[v[1]]},"material_keyword_bucket_drift"),
        ("actual_YAML_valid_keyword_removed",{FIELDS[0]:v[:1]},"missing_material_valid_keyword"),
        ("actual_YAML_valid_keyword_added",{FIELDS[0]:v+["AUTHORED_NEW"]},"unexpected_material_valid_keyword"),
        ("actual_YAML_disabled_pass_drift",{FIELDS[2]:["AuthoredWrongPass"]},"missing_material_disabled_pass"),
        ("actual_YAML_invalid_keyword_field_missing",{FIELDS[1]:None},"missing_material_keyword_pass_container"),
        ("actual_YAML_private_selector_injected",{FIELDS[0]:v+["GT_ORIGINAL_921_AUTHORED"]},"invalid_material_keyword_set"),
    ):
        disk_control(name,lambda text:scene_row(text,matp[1],21,lambda body:change_state(body,updates)),
                     reason,files[matp[0]][0],old_keyword_gate_passes=True)
    # Actual native Texture2D YAML bytes, both textures same dimensions
    # and size, different content. PPtrs and material state are untouched.
    textures=sorted(key for key,(cls,_) in objects.items() if cls==28)
    need(len(textures)==2,"authored_texture_population")
    tp=mapping[textures[0]][1];op=mapping[textures[1]][1]
    tex_path=files[tp[0]][0]
    def tex_hex(body):
        hit=re.search(r"(?m)^(\s*_typelessdata:[ \t]*)([0-9a-fA-F]+)[ \t]*$",body)
        need(hit is not None and len(hit[2])==40,"actual_texture_hex_missing")
        return hit
    other_raw=scene_row(files[op[0]][0].read_text(),op[1],28,lambda body:body)
    other_bytes=bytes.fromhex(tex_hex(other_raw)[2])
    need(sha256(other_bytes).hexdigest()==objects[textures[1]][1].sha256,"actual_other_texture_proof_drift")
    def mutate_tex(body,offset=None,swap=False):
        hit=tex_hex(body);raw=bytearray.fromhex(hit[2])
        if swap:raw=bytearray(other_bytes)
        else:raw[offset]^=1
        need(raw.hex()!=hit[2].lower(),"actual_texture_control_no_mutation")
        return body[:hit.start(2)]+raw.hex()+body[hit.end(2):]
    for name,offset,swap in (
        ("actual_YAML_texture_RGB_drift",0,False),
        ("actual_YAML_texture_alpha_drift",3,False),
        ("actual_YAML_texture_lower_mip_drift",16,False),
        ("actual_YAML_texture_same_size_payload_swap",None,True),
    ):
        disk_control(name,lambda text:scene_row(text,tp[1],28,lambda body:mutate_tex(body,offset,swap)),
                     "same_route_texture_payload_bytes_drift",tex_path,old_texture_gate_passes=True)
    def replace_tex_scalar(body,field,value):
        pattern=r"(?m)^(  "+re.escape(field)+r":[ \t]*).*$"
        changed,n=re.subn(pattern,lambda m:m[1]+value,body)
        need(n==1 and changed!=body,"actual_texture_descriptor_control_missing")
        return changed
    for name,field,value,reason in (
        ("actual_YAML_texture_mip_count_drift","m_MipCount","1","texture_mip_size_mismatch"),
        ("actual_YAML_texture_unsupported_format","m_TextureFormat","5","unsupported_native_RGBA32_texture_layout"),
        ("actual_YAML_texture_missing_bytes","_typelessdata",'""',"texture_payload_hex_or_length_mismatch"),
    ):
        disk_control(name,lambda text:scene_row(text,tp[1],28,lambda body:replace_tex_scalar(body,field,value)),
                     reason,tex_path,old_texture_gate_passes=True)
    # Actual trace identity with source and export owner confusion.
    table=deepcopy(externals);table[renderers[0][0]]=list(reversed(table[renderers[0][0]]))
    # Change only the two dependency entries for the two valid Materials,
    # preserving the mesh provider and every local component reference.
    table=deepcopy(externals);ls=table[renderers[0][0]]
    i,j=ls.index(materials[0][0]),ls.index(materials[1][0]);ls[i],ls[j]=ls[j],ls[i]
    record("source_external_table_swapped_same_PathIDs",gate.compare(objects,table,mapping,files,docs,vertex_payloads=proofs,material_values=True,material_keywords=True,texture_payloads=True),"ordered_pointer_target_mismatch")
    altered=deepcopy(mapping);cls,p,exp=altered[renderers[0]];altered[renderers[0]]=(cls,(p[0],p[1],0),exp)
    record("unscoped_type0_trace",gate.compare(objects,externals,altered,files,docs,vertex_payloads=proofs,material_values=True,material_keywords=True,texture_payloads=True),"unproven_exportable_global_target")
    altered=deepcopy(mapping);cls,p,exp=altered[renderers[0]];altered[renderers[0]]=(cls,(p[0],p[1],3),exp)
    record("wrong_global_serialized_type",gate.compare(objects,externals,altered,files,docs,vertex_payloads=proofs,material_values=True,material_keywords=True,texture_payloads=True),"serialized_document_trace_type_mismatch")
    altered=deepcopy(mapping);cls,p,exp=altered[renderers[0]];altered[renderers[0]]=(cls,p,False)
    record("nonexportable_component_trace",gate.compare(objects,externals,altered,files,docs,vertex_payloads=proofs,material_values=True,material_keywords=True,texture_payloads=True),"unproven_exportable_global_target")
    # Hidden components must have no actual YAML document/trace. Since they
    # are intentionally excluded from this authored baseline, add them to
    # the source census and show that it cannot falsely claim full closure.
    augmented=dict(objects)
    for key in hidden:augmented[key]=(23,{})
    record("hidden_source_renderers_not_promoted",gate.compare(augmented,externals,mapping,files,docs,vertex_payloads=proofs,material_values=True,material_keywords=True,texture_payloads=True),"missing_source_export_trace")
    result=dict(status="PASS_ACTUAL_AUTHORED_PUBLIC_SCENE_TEXTURE_PAYLOAD_ROUTE_JOIN",producer=producer,
                actual_exported_documents=len(docs),actual_native_scene_files=2,source_generated_object_count=len(objects),
                baseline=baseline,counterfactuals=controls,counterfactual_count=len(controls),
                same_PathID_distinct_owners=True,actual_cross_owner_dependency_order=True,
                source_contract_captured_before_export=True,hidden_source_renderers_excluded_from_baseline_but_not_promoted=True,
                original_assets_read=False,original_serialized_source_verified=False,production_renderer_parity_verified=False,
                native_inline_RGBA32_texture_payload_bytes_verified=True,
                texture_sampler_import_colorspace_or_GPU_verified=False,
                vertex_payload_bytes_verified=True,serialized_material_values_verified=True,
                serialized_material_keyword_pass_state_verified=True,active_shader_variant_or_runtime_keyword_scope_verified=False,
                UV_decoded_values_or_GPU_verified=False,shader_property_runtime_semantics_verified=False,XAPK=False)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--root",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();r=audit(a.root,a.out);print(json.dumps(r,sort_keys=True))
    return 0


if __name__=="__main__":raise SystemExit(main())
