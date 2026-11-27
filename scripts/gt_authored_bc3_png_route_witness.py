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

def diagnose(root,out,files,requests,mapping,pins):
    """Retain bounded exact authored pixels even on strict parity failure.

    No adjustment to the oracle, no tolerance, no original assets. The
    stored-block coordinates and selectors describe the source before FlipY.
    """
    from collections import Counter
    keys=sorted(requests)
    provider=requests[keys[0]].provider;pin=pins["Raft_Data/"+provider]
    raw=gate.verified_range(root/"providers"/provider,(pin[1],pin[2]),0,187)
    rows=[]
    for n,k in enumerate(keys):
        req=requests[k];ptr=mapping[k][1];p,meta=files[ptr[0]]
        need(req.descriptor[:2]==(5,7) and req.mip_lengths==(64,16),"diagnostic_authored_scope")
        top=raw[req.offset:req.offset+64]
        expected=bc3.decode_top((5,7),top)
        png.exported_image(p)
        with Image.open(p) as im:actual=im.copy()
        need(actual.mode=="RGBA" and actual.size==(5,7),"diagnostic_actual_image_schema")
        e=list(expected.getdata());a=list(actual.getdata())
        per_channel=[Counter() for _ in range(4)];pixels=[]
        for y in range(7):
            for x in range(5):
                index=y*5+x
                stored_y=6-y
                block=2*(stored_y//4)+x//4
                selector=4*(stored_y%4)+x%4
                b=top[16*block:16*block+16]
                alpha_idx=(int.from_bytes(b[2:8],"little")>>(3*selector))&7
                rgb_idx=(int.from_bytes(b[12:16],"little")>>(2*selector))&3
                delta=[v-u for u,v in zip(e[index],a[index],strict=True)]
                for i,d in enumerate(delta):per_channel[i][d]+=1
                pixels.append({"xy":[x,y],"stored_block":block,"selector":selector,
                    "alpha_index":alpha_idx,"rgb_index":rgb_idx,
                    "expected":e[index],"actual":a[index],"delta":delta})
        # Forensic output only. Alternative orientation/channel order is
        # never used to normalize or accept the strict production comparison.
        transforms={"identity":expected,"vertical":expected.transpose(Image.Transpose.FLIP_TOP_BOTTOM),
                    "horizontal":expected.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
                    "both":expected.transpose(Image.Transpose.ROTATE_180)}
        matches={name:sum(x==y for x,y in zip(im.getdata(),a,strict=True)) for name,im in transforms.items()}
        channel_permutation=sum((r,b,g,al)==v for (r,g,b,al),v in zip(e,a,strict=True))
        swapped_rb=sum((b,g,r,al)==v for (r,g,b,al),v in zip(e,a,strict=True))
        rows.append({"texture_index":n,"source_top_hex":top.hex(),
            "source_top_sha256":sha256(top).hexdigest(),
            "expected_rgba_sha256":sha256(expected.tobytes()).hexdigest(),
            "actual_rgba_sha256":sha256(actual.tobytes()).hexdigest(),
            "max_abs_delta_per_channel":[max(abs(d) for d in v) for v in per_channel],
            "signed_delta_histograms":[dict(sorted(v.items())) for v in per_channel],
            "orientation_exact_pixel_matches":matches,"swap_RB_exact_pixels":swapped_rb,
            "swap_GB_exact_pixels":channel_permutation,
            "expected_transparent_nonzero_RGB":sum(al==0 and bool(r or g or b) for r,g,b,al in e),
            "actual_transparent_nonzero_RGB":sum(al==0 and bool(r or g or b) for r,g,b,al in a),
            "pixels":pixels})
        # These are fresh 5x7 authored outputs only; retain exact PNG bytes.
        (out.parent/f"bc3-authored-{n}.png").write_bytes(png.bounded_snapshot(p,png.MAX_PNG))
    result={"authored_only":True,"source_format":12,"source_owner_sha_verified":False,
            "provider_sha_verified":True,"original_assets_read":False,"strict_parity_waived":False,"textures":rows}
    (out.parent/"bc3-diagnostic.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"BC3_AUTHORED_DIAGNOSTIC_ONLY","authored_only":True,
        "strict_parity_waived":False,"textures":[{k:v for k,v in row.items() if k!="pixels"} for row in rows]},sort_keys=True))


def audit(root,out,*,extended=False):
    root=Path(root);out=Path(out)
    need(not out.exists() and out.parent.is_dir(),"fresh_bc3_receipt_required")
    objects,externals,mapping,vertices,proofs,requests,pins,producer=load(root,bc3_mode=True)
    variant="extended_equal_endpoints" if extended else "historical_replay"
    need(producer.get("bc3_fixture_variant")==variant,"actual_BC3_fixture_variant")
    files,docs=gate.actual_index(root/"project",mapping)
    need(len(files)==9 and len(docs)==11,"actual_bc3_document_population")
    keys=sorted(requests);ptrs=[mapping[k][1] for k in keys]
    def run(f,d,p=proofs,*,strict=True,bc3_mode=True):
        return gate.compare(objects,externals,mapping,f,d,vertex_payloads=vertices,material_values=True,
              material_keywords=True,**({"png_top_mips":p,"png_bc3":bc3_mode} if strict else {}))
    baseline=run(files,docs)
    (out.parent/"bc3-baseline.json").write_text(json.dumps(baseline,indent=2,sort_keys=True)+"\n")
    diagnose(root,out,files,requests,mapping,pins)
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
    schemas=[];transparent_targets=[];source_top_hashes=[]
    for k,ptr in zip(keys,ptrs,strict=True):
        req=requests[k];top=raw[req.offset:req.offset+64]
        source=bc3.decode_top(req.descriptor[:2],top);source_top_hashes.append(sha256(top).hexdigest())
        blocks=[top[i:i+16] for i in range(0,64,16)]
        need({b[0]>b[1] for b in blocks}=={True,False},"BC3_both_alpha_endpoint_modes")
        orders=[(int.from_bytes(b[8:10],"little"),int.from_bytes(b[10:12],"little")) for b in blocks]
        need(any(x<y for x,y in orders) and any(x>y for x,y in orders),"BC3_both_RGB_endpoint_orders")
        need(any(x==y for x,y in orders)==extended,"BC3_equal_endpoint_fixture_scope")
        path,meta=files[ptr[0]]
        with Image.open(path) as im:
            need(compare_pair(source,im,original_id="same-trace",exported_id="same-trace",authenticated=True)=="EXACT",
                 "independent_BC3_per_channel")
            colors=list(source.getdata())
            transparent=any(a==0 and (r or g or b) for r,g,b,a in colors)
            if transparent:transparent_targets.append(path)
            need(any(a==255 for _,_,_,a in colors) and any(0<a<255 for _,_,_,a in colors),"BC3_alpha_selector_coverage")
            if extended:need(transparent,"BC3_extended_visible_transparent_RGB")
            schemas.append({"dimensions":list(im.size),"source_format":req.descriptor[2],"mip_lengths":list(req.mip_lengths),
                            "rgba_mode":im.mode,"unique_alpha_values":len({p[3] for p in colors}),
                            "visible_transparent_nonzero_RGB":transparent,"equal_RGB_endpoint_blocks":sum(x==y for x,y in orders),
                            "source_top_sha256":source_top_hashes[-1],
                            "importer_textureFormat":png.importer_document(meta,ptr).get("textureFormat")})
    need(transparent_targets,"BC3_population_visible_transparent_RGB")
    if not extended:need(source_top_hashes==[
        "b3445c245238ae44a9ad831c5f62f5abe9da8082197beec8a8ac1269d8ae16ae",
        "3e285fed5f82a7de5571e1c8b9ca2bff65e44249fe76f0fdad83386025eacede"],
        "BC3_historical_replay_source_drift")
    need(proofs[keys[0]].rgba_sha256!=proofs[keys[1]].rgba_sha256,"BC3_distinct_pixels")
    controls={}
    def record(name,r,reason,old=True):
        need(not r[FIELD] and r["reason_counts"].get(reason,0)>0,"BC3_control_not_rejected:"+name+":"+str(r["reason_counts"]))
        controls[name]={"reason":reason,"V4_pass":old}
    target=files[ptrs[0][0]][0];other=files[ptrs[1][0]][0]
    def disk(name,change,reason,texture_path=target):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"project";shutil.copytree(root/"project",p)
            change(p/texture_path.relative_to(root/"project"));f,d=gate.actual_index(p,mapping)
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
    disk("transparent_RGB",lambda p:edit(p,lambda im:channel(im,1,True)),"same_route_png_RGB_DRIFT",transparent_targets[0])
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
        schemas=schemas,fixture_variant=variant,independent_per_channel_checks=2,
        historical_source_hashes_verified=not extended,visible_transparent_RGB_texture_count=len(transparent_targets),
        repinned_lower_mip_intentionally_outside_scope=True,
        V8_scope_rejects_BC3=True,original_assets_read=False,original_serialized_source_verified=False,
        Unity_import_verified=False,Android_device=False,XAPK=False)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,sort_keys=True))

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    p.add_argument("--extended",action="store_true")
    a=p.parse_args();audit(a.root,a.out,extended=a.extended)

if __name__=="__main__":main()
