"""Actual public PNG exporter + importer witness, separate from native V7."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile

from PIL import Image
from scripts import gt_renderer_submesh_routes as gate
from scripts import gt_mesh_vertex_payload as payload
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_imported_png_route_importer as importer_state
from scripts import gt_streamed_texture_route_payload as stream
from scripts.t3_decoded_texture_pixel_parity import compare_pair


def need(ok,reason):
    if not ok:raise ValueError(reason)


def load(root,*,states=None):
    source=gate.strict_json(gate.bounded_snapshot(root/"source.json",1024*1024))
    producer=gate.strict_json(gate.bounded_snapshot(root/"producer.json",256*1024))
    need(producer.get("status")=="OBSERVED_AUTHORED_PUBLIC_PNG_EXPORT" and
         producer.get("actual_public_export_collections")==9 and
         producer.get("actual_scene_collections")==2 and
         producer.get("actual_imported_png_texture_collections")==2 and
         producer.get("original_assets_read") is False,"actual_png_producer_contract")
    need(source.get("schema_version")==8 and source.get("authored_generated_objects") is True,
         "authored_png_source_contract")
    objects={};vertices={};requests={}
    providers=source["providers"]
    need(len(providers)==1 and providers[0]["name"]=="authored-textures.resS" and providers[0]["bytes"]==61,
         "authored_png_provider_contract")
    pins={"Raft_Data/"+p["name"]:("plain",p["bytes"],p["sha256"]) for p in providers}
    for row in source["objects"]:
        key=(row["owner"],row["path_id"]);cls=row["class_id"];tree=row["tree"]
        need(key not in objects and cls in gate.CLASSES,"authored_png_source_identity_collision")
        if cls==43:
            vertices[key]=payload.source_request(tree)
            need(isinstance(vertices[key],payload.Proof) and vertices[key].length==120,"authored_mesh_payload")
            tree=gate.mesh_layout(tree)
        elif cls==28:
            requests[key]=png.source_request(tree)
            if states is not None:states[key]=importer_state.source_proof(tree)
            need(isinstance(requests[key],stream.Request) and requests[key].mip_lengths==(16,4),
                 "authored_png_two_mips_stream_source")
            tree=None
        objects[key]=(cls,tree)
    need(len(requests)==2 and sorted(r.offset for r in requests.values())==[7,34],"authored_png_source_extents")
    resolved=png.resolve_requests(root/"providers",pins,requests)
    need(all(isinstance(p,png.Proof) and p.from_stream for p in resolved.values()),"authored_png_source_authentication")
    traces=[gate.strict_json(gate.bounded_snapshot(root/f,1024*1024)) for f in ("materials.json","meshes.json","components.json")]
    mapping=gate.traces(*traces)
    need(set(mapping)==set(objects),"actual_png_trace_population")
    hidden={(r["owner"],r["path_id"]) for r in source["hidden"]}
    need(len(hidden)==2 and not hidden&set(mapping),"hidden_png_source_trace_exclusion")
    return objects,source["externals"],mapping,vertices,resolved,requests,pins,producer


def audit(root,out):
    root=Path(root);out=Path(out)
    need(not out.exists() and out.parent.is_dir(),"fresh_png_receipt_required")
    objects,externals,mapping,vertices,resolved,requests,pins,producer=load(root)
    files,docs=gate.actual_index(root/"project",mapping)
    textures=sorted(requests)
    need(len(docs)==11 and len(files)==9,"actual_png_native_document_population")
    ptrs=[mapping[k][1] for k in textures]
    schemas=[]
    # Retain actual authored exporter schema before checking baseline.
    for ptr in ptrs:
        path,meta=files[ptr[0]]
        import yaml
        md=yaml.safe_load(meta)
        imp=md.get("TextureImporter",{})
        with Image.open(path) as im:
            schemas.append({"trace_fileID":ptr[1],"trace_type":ptr[2],"suffix":path.suffix,
                "image_mode":im.mode,"size":list(im.size),"textureShape":imp.get("textureShape"),
                "textureType":imp.get("textureType"),"textureSettings":imp.get("textureSettings"),
                "alphaIsTransparency":imp.get("alphaIsTransparency"),
                "mipmaps":imp.get("mipmaps"),"platformSettings":imp.get("platformSettings")})
    (out.parent/"png-schema.json").write_text(json.dumps({"authored_only":True,"textures":schemas},indent=2,sort_keys=True)+"\n")
    def run(f,d,p=resolved,strict=True):
        return gate.compare(objects,externals,mapping,f,d,vertex_payloads=vertices,material_values=True,
            material_keywords=True,**({"png_top_mips":p} if strict else {}))
    baseline=run(files,docs)
    need(baseline["selected_same_route_imported_png_top_mip_verified"],"actual_png_baseline:"+json.dumps(baseline["reason_counts"]))
    need(baseline["selected_same_route_material_keyword_pass_state_verified"],"V4_scope_not_preserved")
    for field in ("selected_nonnull_same_route_texture_payloads_verified","selected_same_route_streamed_texture_payloads_verified",
                  "selected_same_route_native_texture_sampler_verified","imported_png_lower_mip_or_Unity_import_verified",
                  "texture_sampler_import_colorspace_or_GPU_verified"):
        need(baseline[field] is False,"false_native_or_import_promotion:"+field)
    for k,v in {"complete_renderer_routes":2,"complete_submesh_material_identity_routes":4,
                "complete_imported_png_bound_renderer_routes":2,"complete_imported_png_bound_submesh_routes":4,
                "imported_png_top_mip_slots_matched":4,"imported_png_pixels_matched_per_route":16,
                "imported_png_RGBA_channels_matched_per_route":64,"imported_png_stream_source_slots_matched":4}.items():
        need(baseline["counts"].get(k)==v,"actual_png_baseline_count:"+k)
    # Independent T3 per-channel oracle on the same source range.
    # Reauthenticate the entire small authored provider for this second
    # oracle; never perform an unauthenticated read after a prior hash.
    # Compare exact decoded source bytes and actual public PNG independently.
    provider=next(iter(requests.values())).provider
    raw=gate.verified_range(root/"providers"/provider,(pins["Raft_Data/"+provider][1],pins["Raft_Data/"+provider][2]),0,61)
    for k,ptr in zip(textures,ptrs,strict=True):
        req=requests[k];original=png.decode_top(req.descriptor[:2],raw[req.offset:req.offset+req.mip_lengths[0]])
        with Image.open(files[ptr[0]][0]) as im:
            need(compare_pair(original,im,original_id="same-trace",exported_id="same-trace",authenticated=True)=="EXACT",
                 "independent_T3_authored_pixel_check")
            need(any(a==0 and (r or g or b) for r,g,b,a in original.getdata()),"transparent_RGB_control_missing")
    controls={}
    def record(name,r,reason,old=True):
        need(not r["selected_same_route_imported_png_top_mip_verified"] and
             r["reason_counts"].get(reason,0)>0,"png_control_not_rejected:"+name+":"+str(r["reason_counts"]))
        controls[name]={"reason":reason,"V4_pass":old}
    target=files[ptrs[0][0]][0]
    other=files[ptrs[1][0]][0]
    def disk(name,change,reason,old=True,meta=False):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/"project";shutil.copytree(root/"project",project)
            p=project/target.relative_to(root/"project")
            if meta:p=Path(str(p)+".meta")
            change(p)
            f,d=gate.actual_index(project,mapping)
            if old:need(run(f,d,strict=False)["selected_same_route_material_keyword_pass_state_verified"],"V4_not_pass:"+name)
            record(name,run(f,d),reason,old)
    def pixels(path,fn):
        with Image.open(path) as im:img=im.copy()
        fn(img).save(path)
    def change_channel(im,channel,transparent=False):
        pos=next((x,y) for y in range(im.height) for x in range(im.width)
                 if (im.getpixel((x,y))[3]==0 if transparent else im.getpixel((x,y))[3]!=0))
        value=list(im.getpixel(pos));value[channel]^=1;im.putpixel(pos,tuple(value));return im
    disk("actual_PNG_RGB_drift",lambda p:pixels(p,lambda im:change_channel(im,0)),"same_route_png_RGB_DRIFT")
    disk("actual_PNG_transparent_RGB_drift",lambda p:pixels(p,lambda im:change_channel(im,1,True)),"same_route_png_RGB_DRIFT")
    disk("actual_PNG_alpha_drift",lambda p:pixels(p,lambda im:change_channel(im,3)),"same_route_png_ALPHA_ONLY_DRIFT")
    disk("actual_PNG_vertical_flip",lambda p:pixels(p,lambda im:im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)),"same_route_png_VERTICAL_FLIP")
    disk("actual_PNG_horizontal_flip",lambda p:pixels(p,lambda im:im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)),"same_route_png_HORIZONTAL_FLIP")
    disk("actual_PNG_same_size_texture_swap",lambda p:p.write_bytes(other.read_bytes()),"same_route_png_RGB_DRIFT")
    disk("actual_PNG_wrong_dimensions",lambda p:pixels(p,lambda im:im.resize((1,4))),"same_route_png_DIMENSION_MISMATCH")
    disk("actual_PNG_RGB_mode",lambda p:pixels(p,lambda im:im.convert("RGB")),"unsupported_png_RGBA8_image")
    def meta_change(p,field,value):
        s=p.read_text();pattern=r"(?m)^([ \t]*"+re.escape(field)+r":[ \t]*).*$"
        changed,n=re.subn(pattern,lambda m:m[1]+value,s)
        need(n==1 and changed!=s,"png_meta_control_field_missing:"+field);p.write_text(changed)
    disk("actual_PNG_importer_wrong_type",lambda p:meta_change(p,"textureType","1"),"unsupported_png_importer_shape_or_type",meta=True)
    disk("actual_PNG_importer_invalid_filter",lambda p:meta_change(p,"filterMode","99"),"invalid_png_importer_sampler_schema",meta=True)
    disk("actual_PNG_wrong_guid",lambda p:meta_change(p,"guid","abcdef0123456789abcdef0123456789"),"missing_actual_export_target",old=False,meta=True)
    # An explicit -100 importer bias is accepted only as a schema sentinel,
    # never as source-native sampler equality.
    with tempfile.TemporaryDirectory() as tmp:
        project=Path(tmp)/"project";shutil.copytree(root/"project",project)
        p=Path(str(project/target.relative_to(root/"project"))+".meta")
        meta_change(p,"mipBias","-100")
        f,d=gate.actual_index(project,mapping);sentinel=run(f,d)
        need(sentinel["selected_same_route_imported_png_top_mip_verified"] and
             sentinel["counts"]["imported_png_importer_mip_bias_unset_slots"]==2 and
             not sentinel["selected_same_route_native_texture_sampler_verified"],
             "png_importer_unset_scope")
    altered=dict(requests);altered[textures[0]]=replace(altered[textures[0]],offset=altered[textures[1]].offset)
    record("actual_PNG_source_extent_swap",run(files,docs,png.resolve_requests(root/"providers",pins,altered)),"same_route_png_RGB_DRIFT")
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/provider;modified=bytearray(raw);modified[0]^=1;p.write_bytes(modified)
        record("actual_PNG_provider_padding_mutation",run(files,docs,png.resolve_requests(Path(tmp),pins,requests)),
               "png_stream_provider_SHA_mismatch")
    # Lower mips are deliberately NOT compared to PNG. Change the source
    # lower mip and re-pin the authored provider: top proof remains exact.
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/provider;modified=bytearray(raw);modified[requests[textures[0]].offset+16]^=1;p.write_bytes(modified)
        repin={"Raft_Data/"+provider:("plain",len(modified),sha256(modified).hexdigest())}
        lower=run(files,docs,png.resolve_requests(Path(tmp),repin,requests))
        need(lower["selected_same_route_imported_png_top_mip_verified"] and
             not lower["imported_png_lower_mip_or_Unity_import_verified"],"PNG_must_not_claim_lower_mip")
    report=dict(status="PASS_ACTUAL_AUTHORED_PUBLIC_IMPORTED_PNG_TOP_MIP_ROUTE_JOIN",baseline=baseline,
        counterfactuals=controls,counterfactual_count=len(controls),actual_png_textures=2,
        actual_public_export_collections=9,actual_native_documents=11,actual_native_scene_files=2,
        authored_provider_bytes=61,authored_stream_offsets=[7,34],independent_T3_per_channel_checks=2,
        importer_unset_bias_schema_only=True,repinned_lower_mip_change_intentionally_outside_scope=True,
        source_contract_captured_before_export=True,original_assets_read=False,original_serialized_source_verified=False,
        production_auto_exporter_selection=False,production_renderer_parity_verified=False,Unity_render_executed=False,
        native_full_mip_parity_from_png=False,native_sampler_parity_from_png=False,Android_device=False,XAPK=False)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps(report,sort_keys=True))


def audit_importer(root,out):
    root=Path(root);out=Path(out)
    need(not out.exists() and out.parent.is_dir(),"fresh_importer_receipt_required")
    states={}
    objects,externals,mapping,vertices,resolved,requests,pins,producer=load(root,states=states)
    files,docs=gate.actual_index(root/"project",mapping)
    need(len(states)==2 and {s.color_space for s in states.values()}=={0,1} and
         {s.readable for s in states.values()}=={0,1} and {s.streaming for s in states.values()}=={0,1} and
         {s.priority for s in states.values()}=={-2,3},"distinct_preexport_importer_state_required")
    def run(f,d,strict=True):
        return gate.compare(objects,externals,mapping,f,d,vertex_payloads=vertices,material_values=True,
            material_keywords=True,png_top_mips=resolved,**({"png_importer_states":states} if strict else {}))
    baseline=run(files,docs)
    import yaml
    schemas=[]
    for key,state in sorted(states.items()):
        ptr=mapping[key][1];imp=png.importer_document(files[ptr[0]][1],ptr)
        schemas.append({"source":state.__dict__,"actual_importer":{k:imp.get(k) for k in
            ("textureSettings","mipmaps","isReadable","streamingMipmaps","streamingMipmapsPriority","textureFormat",
            "textureShape","textureType","maxTextureSize","nPOTScale","alphaUsage","alphaIsTransparency",
            "swizzle","compressionQuality","platformSettings")}})
    (out.parent/"importer-state-schema.json").write_text(json.dumps(schemas,indent=2,sort_keys=True)+"\n")
    need(baseline["selected_same_route_imported_png_serialized_importer_state_verified"],
         "actual_importer_baseline:"+str(baseline["reason_counts"]))
    need(baseline["counts"]["imported_png_importer_state_slots_matched"]==4 and
         baseline["counts"]["imported_png_importer_sampler_fields_matched_per_route"]==24 and
         baseline["counts"]["imported_png_importer_source_mapping_fields_matched_per_route"]==36 and
         baseline["counts"]["imported_png_importer_exporter_policy_fields_matched_per_route"]==68,
         "actual_importer_baseline_counts")
    need(not baseline["original_runtime_importer_or_Android_platform_fidelity_verified"] and
         not baseline["selected_same_route_native_texture_sampler_verified"],"importer_scope_promotion")
    controls={}
    target=files[mapping[sorted(states)[0]][1][0]][0]
    def disk(name,path,value,reason):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/"project";shutil.copytree(root/"project",project)
            p=Path(str(project/target.relative_to(root/"project"))+".meta")
            # Actual meta only, preserving PNG bytes, GUID and other docs.
            doc=yaml.safe_load(p.read_text());imp=doc["TextureImporter"];parent=imp
            for step in path[:-1]:parent=parent[step]
            field=path[-1]
            need(field in parent and parent[field]!=value,"actual_importer_control_no_change:"+name)
            parent[field]=value
            p.write_text(yaml.safe_dump(doc,sort_keys=False))
            f,d=gate.actual_index(project,mapping)
            need(run(f,d,False)["selected_same_route_imported_png_top_mip_verified"],"V8_not_pass:"+name)
            result=run(f,d)
            need(not result["selected_same_route_imported_png_serialized_importer_state_verified"] and
                 result["reason_counts"].get(reason,0)>0,"V9_not_reject:"+name+":"+str(result["reason_counts"]))
            controls[name]={"V8_pass":True,"V9_reject":True,"reason":reason}
    source=states[sorted(states)[0]]
    disk("srgb",("mipmaps","sRGBTexture"),1-source.color_space,"same_route_png_source_mapping_sRGBTexture_drift")
    disk("mip_enable",("mipmaps","enableMipMap"),1-source.mip_enabled,"same_route_png_source_mapping_enableMipMap_drift")
    disk("readable",("isReadable",),1-source.readable,"same_route_png_source_mapping_isReadable_drift")
    disk("streaming",("streamingMipmaps",),1-source.streaming,"same_route_png_source_mapping_streamingMipmaps_drift")
    disk("priority",("streamingMipmapsPriority",),source.priority+1,"same_route_png_source_mapping_streamingMipmapsPriority_drift")
    disk("wrap",("textureSettings","wrapV"),(source.sampler[4]+1)%4,"same_route_png_importer_wrapV_drift")
    disk("unset_bias",("textureSettings","mipBias"),-100,"unknown_png_importer_sampler_default")
    disk("unset_filter",("textureSettings","filterMode"),-1,"unknown_png_importer_sampler_default")
    disk("alpha_policy",("alphaIsTransparency",),0,"same_route_png_exporter_policy_alphaIsTransparency_drift")
    disk("compression",("platformSettings",0,"textureCompression"),0,"same_route_png_exporter_policy_textureCompression_drift")
    disk("override",("platformSettings",0,"overridden"),1,"same_route_png_exporter_policy_overridden_drift")
    disk("dimension_budget",("maxTextureSize",),1024,"same_route_png_source_mapping_maxTextureSize_drift")
    disk("swizzle",("swizzle",),0,"same_route_png_exporter_policy_swizzle_drift")
    report={"status":"PASS_ACTUAL_AUTHORED_PUBLIC_PNG_SERIALIZED_IMPORTER_ROUTE_JOIN","baseline":baseline,
            "counterfactuals":controls,"counterfactual_count":len(controls),"source_states":len(states),
            "source_captured_before_export":True,"original_assets_read":False,"Unity_import_executed":False,
            "Android_device":False,"XAPK":False,"original_runtime_fidelity_verified":False}
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n");print(json.dumps(report,sort_keys=True))


def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    p.add_argument("--importer-state",action="store_true")
    a=p.parse_args();(audit_importer if a.importer_state else audit)(a.root,a.out)


if __name__=="__main__":main()
