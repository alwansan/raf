"""Actual public DXT5 texture export witness, separate from V7-V9."""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
from PIL import Image
from scripts import gt_renderer_submesh_routes as gate
from scripts import gt_imported_bc3_route_pixels as bc3
from scripts import gt_imported_png_route_pixels as png
from scripts.gt_authored_imported_png_route_witness import load, need
from scripts.t3_decoded_texture_pixel_parity import compare_pair

FIELD="selected_same_route_imported_bc3_png_top_mip_verified"
NO_PROMOTION=("selected_same_route_imported_png_top_mip_verified",
              "selected_same_route_native_texture_sampler_verified",
              "selected_nonnull_same_route_texture_payloads_verified",
              "bc3_compressed_payload_or_lower_mip_parity_verified",
              "imported_png_lower_mip_or_Unity_import_verified",
              "texture_sampler_import_colorspace_or_GPU_verified")

def audit(root,out):
    root=Path(root);out=Path(out)
    need(not out.exists() and out.parent.is_dir(),"fresh_bc3_receipt_required")
    objects,externals,mapping,vertices,proofs,requests,pins,producer=load(root,bc3_mode=True)
    files,docs=gate.actual_index(root/"project",mapping)
    need(len(files)==9 and len(docs)==11,"actual_bc3_document_population")
    keys=sorted(requests);ptrs=[mapping[k][1] for k in keys]
    def run(f,d,p=proofs,*,strict=True,bc3_mode=True):
        return gate.compare(objects,externals,mapping,f,d,vertex_payloads=vertices,material_values=True,
              material_keywords=True,**({"png_top_mips":p,"png_bc3":bc3_mode} if strict else {}))
    baseline=run(files,docs)
    (out.parent/"bc3-baseline.json").write_text(json.dumps(baseline,indent=2,sort_keys=True)+"\n")
    need(baseline[FIELD],"actual_bc3_baseline:"+str(baseline["reason_counts"]))
    need(all(baseline[k] is False for k in NO_PROMOTION),"bc3_false_scope_promotion")
    counts=baseline["counts"]
    for k,v in {"complete_renderer_routes":2,"complete_imported_png_bound_renderer_routes":2,
        "complete_imported_png_bound_submesh_routes":4,"imported_png_top_mip_slots_matched":4,
        "imported_png_pixels_matched_per_route":140,"imported_png_RGBA_channels_matched_per_route":560,
        "imported_png_stream_source_slots_matched":4}.items():
        need(counts.get(k)==v,"actual_bc3_count:"+k)
    provider=requests[keys[0]].provider;pin=pins["Raft_Data/"+provider]
    raw=gate.verified_range(root/"providers"/provider,(pin[1],pin[2]),0,187)
    # Exact whole-provider authentication independent of the grouped digest.
    schemas=[]
    for k,ptr in zip(keys,ptrs,strict=True):
        req=requests[k];source=bc3.decode_top(req.descriptor[:2],raw[req.offset:req.offset+64])
        path,meta=files[ptr[0]]
        with Image.open(path) as im:
            need(compare_pair(source,im,original_id="same-trace",exported_id="same-trace",authenticated=True)=="EXACT",
                 "independent_BC3_per_channel")
            colors=list(source.getdata())
            need(any(a==0 and (r or g or b) for r,g,b,a in colors) and any(a==255 for _,_,_,a in colors)
                 and any(0<a<255 for _,_,_,a in colors),"BC3_alpha_selector_coverage")
            schemas.append({"dimensions":list(im.size),"source_format":req.descriptor[2],"mip_lengths":list(req.mip_lengths),
                            "rgba_mode":im.mode,"unique_alpha_values":len({p[3] for p in colors}),
                            "importer_textureFormat":png.importer_document(meta,ptr).get("textureFormat")})
    need(proofs[keys[0]].rgba_sha256!=proofs[keys[1]].rgba_sha256,"BC3_distinct_pixels")
    controls={}
    def record(name,r,reason,old=True):
        need(not r[FIELD] and r["reason_counts"].get(reason,0)>0,"BC3_control_not_rejected:"+name+":"+str(r["reason_counts"]))
        controls[name]={"reason":reason,"V4_pass":old}
    target=files[ptrs[0][0]][0];other=files[ptrs[1][0]][0]
    def disk(name,change,reason):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"project";shutil.copytree(root/"project",p)
            change(p/target.relative_to(root/"project"));f,d=gate.actual_index(p,mapping)
            need(run(f,d,strict=False)["selected_same_route_material_keyword_pass_state_verified"],"V4_not_pass:"+name)
            record(name,run(f,d),reason)
    def edit(path,fn):
        with Image.open(path) as im:img=im.copy()
        fn(img).save(path)
    def channel(im,ch,transparent=False):
        pos=next((x,y) for y in range(im.height) for x in range(im.width)
                 if (im.getpixel((x,y))[3]==0 if transparent else im.getpixel((x,y))[3]!=0))
        value=list(im.getpixel(pos));value[ch]^=1;im.putpixel(pos,tuple(value));return im
    disk("RGB",lambda p:edit(p,lambda im:channel(im,0)),"same_route_png_RGB_DRIFT")
    disk("transparent_RGB",lambda p:edit(p,lambda im:channel(im,1,True)),"same_route_png_RGB_DRIFT")
    disk("alpha",lambda p:edit(p,lambda im:channel(im,3)),"same_route_png_ALPHA_ONLY_DRIFT")
    disk("vertical_flip",lambda p:edit(p,lambda im:im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)),"same_route_png_VERTICAL_FLIP")
    disk("horizontal_flip",lambda p:edit(p,lambda im:im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)),"same_route_png_HORIZONTAL_FLIP")
    disk("equal_size_swap",lambda p:p.write_bytes(other.read_bytes()),"same_route_png_RGB_DRIFT")
    disk("wrong_dimensions",lambda p:edit(p,lambda im:im.resize((7,5))),"same_route_png_DIMENSION_MISMATCH")
    swapped=dict(requests);swapped[keys[0]]=replace(swapped[keys[0]],offset=requests[keys[1]].offset)
    record("source_range_swap",run(files,docs,bc3.resolve_requests(root/"providers",pins,swapped)),"same_route_png_RGB_DRIFT")
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/provider;b=bytearray(raw);b[0]^=1;p.write_bytes(b)
        record("provider_padding_drift",run(files,docs,bc3.resolve_requests(Path(tmp),pins,requests)),"bc3_stream_provider_SHA_mismatch")
        b=bytearray(raw);b[requests[keys[0]].offset+64]^=1;p.write_bytes(b)
        repin={"Raft_Data/"+provider:("plain",len(b),sha256(b).hexdigest())}
        lower=run(files,docs,bc3.resolve_requests(Path(tmp),repin,requests))
        need(lower[FIELD] and not lower["bc3_compressed_payload_or_lower_mip_parity_verified"],"BC3_lower_mip_scope")
    wrong_scope=run(files,docs,bc3_mode=False)
    need(not wrong_scope["selected_same_route_imported_png_top_mip_verified"] and
         wrong_scope["reason_counts"].get("png_source_format_scope_mismatch",0)>0,"BC3_must_not_promote_V8")
    # V8 native receipt cannot be used as a BC3 proof, even with equal pixels.
    old={k:png.Proof(p.size,p.rgba_sha256,p.rgb_sha256,p.flipped_sha256,p.from_stream) for k,p in proofs.items()}
    record("wrong_source_format_scope",run(files,docs,old),"png_source_format_scope_mismatch")
    result=dict(status="PASS_ACTUAL_AUTHORED_PUBLIC_BC3_PNG_TOP_MIP_ROUTE_JOIN",baseline=baseline,
        counterfactuals=controls,counterfactual_count=len(controls),source_states=2,actual_png_textures=2,
        schemas=schemas,independent_per_channel_checks=2,repinned_lower_mip_intentionally_outside_scope=True,
        V8_scope_rejects_BC3=True,original_assets_read=False,original_serialized_source_verified=False,
        Unity_import_verified=False,Android_device=False,XAPK=False)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,sort_keys=True))

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();audit(a.root,a.out)

if __name__=="__main__":main()
