"""Actual authored DXT5nm route proof and independent falsifiers."""
import argparse
from dataclasses import replace
from hashlib import sha256
import json
import math
from pathlib import Path
import tempfile
from PIL import Image
from scripts import gt_renderer_submesh_routes as gate
from scripts import gt_imported_dxt5nm_route_pixels as nm
from scripts import gt_imported_bc3_route_pixels as bc3
from scripts import gt_imported_png_route_pixels as png
from scripts.gt_authored_imported_png_route_witness import load,need

FIELD="selected_same_route_imported_dxt5nm_png_top_mip_and_importer_verified"

def independent(packed,*,swap=False,invert_y=False):
    result=Image.new("RGBA",packed.size)
    pixels=[]
    for r,g,b,a in packed.getdata():
        x,y=(g,a) if swap else (a,g)
        if invert_y:y=255-y
        z=(math.isqrt(max(0,255**2-(2*x-255)**2-(2*y-255)**2))+255)//2
        pixels.append((x,y,z,r))
    result.putdata(pixels)
    return result

def audit(root,out):
    root=Path(root);out=Path(out)
    need(not out.exists() and out.parent.is_dir(),"fresh_normalmap_receipt")
    objects,externals,mapping,vertices,proofs,requests,pins,producer=load(root,bc3_mode=True,normalmap=True)
    need(producer.get("bc3_fixture_variant")=="normalmap_dxt5nm","normalmap_fixture_variant")
    files,docs=gate.actual_index(root/"project",mapping)
    need(len(files)==9 and len(docs)==11,"actual_normalmap_population")
    def run(f=files,d=docs,p=proofs,*,mode=True):
        return gate.compare(objects,externals,mapping,f,d,vertex_payloads=vertices,material_values=True,material_keywords=True,
            **({"png_top_mips":p,"png_normalmap":True} if mode else {}))
    baseline=run()
    (out.parent/"normalmap-baseline.json").write_text(json.dumps(baseline,indent=2,sort_keys=True)+"\n")
    keys=sorted(requests);provider=requests[keys[0]].provider;pin=pins["Raft_Data/"+provider]
    raw=gate.verified_range(root/"providers"/provider,(pin[1],pin[2]),0,187)
    controls={};rows=[];images={}
    # Retain actual authored PNG and independent expected bytes even on a strict failure.
    for i,k in enumerate(keys):
        req=requests[k];ptr=mapping[k][1];path,meta=files[ptr[0]]
        top=raw[req.offset:req.offset+64]
        packed,expected=nm.decode_top((5,7),top);oracle=independent(packed)
        with Image.open(path) as im:
            actual=im.copy()
        (out.parent/f"normalmap-authored-{i}.png").write_bytes(png.bounded_snapshot(path,png.MAX_PNG))
        rows.append(dict(source_top_hex=top.hex(),source_top_sha256=sha256(top).hexdigest(),
                         packed_rgba_sha256=png.digest(packed),expected_rgba_sha256=png.digest(oracle),
                         actual_rgba_sha256=png.digest(actual),expected_rgba_hex=oracle.tobytes().hex(),
                         actual_rgba_hex=actual.tobytes().hex(),metadata=meta,
                         exact=actual.mode=="RGBA" and actual.size==(5,7) and actual.tobytes()==oracle.tobytes()))
        images[k]=(packed,oracle)
        need(oracle.tobytes()==expected.tobytes(),"independent_integer_Z_oracle")
    (out.parent/"normalmap-diagnostic.json").write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n")
    need(baseline[FIELD],"actual_normalmap_baseline:"+str(baseline["reason_counts"]))
    need(all(baseline.get(k,False) is False for k in ("selected_same_route_imported_bc3_png_top_mip_verified",
         "selected_same_route_imported_png_top_mip_verified","selected_same_route_imported_png_serialized_importer_state_verified",
         "selected_same_route_native_texture_sampler_verified","dxt5nm_lower_mips_or_Unity_import_verified","dxt5nm_GPU_normal_fidelity_verified")),"normalmap_scope_promotion")
    for k,v in {"complete_renderer_routes":2,"complete_imported_png_bound_submesh_routes":4,
                "imported_png_top_mip_slots_matched":4,"imported_png_pixels_matched_per_route":140,
                "imported_png_RGBA_channels_matched_per_route":560,"imported_png_stream_source_slots_matched":4}.items():
        need(baseline["counts"].get(k)==v,"actual_normalmap_count:"+k)
    for i,k in enumerate(keys):
        ptr=mapping[k][1];path,meta=files[ptr[0]]
        imp=png.importer_document(meta,ptr,texture_type=1)
        need(imp["textureFormat"]==12 and imp["mipmaps"]["sRGBTexture"]==0 and rows[i]["exact"],"normalmap_exact_importer_and_RGBA")
        pixels=list(images[k][1].getdata())
        need(any(p[2]>127 for p in pixels) and any(p[2]==127 for p in pixels),"normalmap_Z_reconstruct_and_clamp_coverage")
        rows[i].update(texture_type=imp["textureType"],texture_format=imp["textureFormat"],sRGB=imp["mipmaps"]["sRGBTexture"])
    need(rows[0]["expected_rgba_sha256"]!=rows[1]["expected_rgba_sha256"],"normalmap_distinct_same_size")
    def reject(name,f=files,p=proofs):
        need(run(f=f,mode=False)["selected_same_route_material_keyword_pass_state_verified"],"V4_control:"+name)
        result=run(f=f,p=p)
        need(not result[FIELD] and result["reason_counts"],"normalmap_control_not_rejected:"+name)
        controls[name]=result["reason_counts"]
    k=keys[0];ptr=mapping[k][1];path,meta=files[ptr[0]]
    packed,expected=images[k]
    for name,im in (("packed_not_unpacked",packed),("swap_XY",independent(packed,swap=True)),
                    ("invert_Y",independent(packed,invert_y=True)),
                    ("vertical_rows",expected.transpose(Image.Transpose.FLIP_TOP_BOTTOM)),
                    ("horizontal_columns",expected.transpose(Image.Transpose.FLIP_LEFT_RIGHT)),
                    ("same_size_texture_swap",images[keys[1]][1])):
        need(im.tobytes()!=expected.tobytes(),"normalmap_control_degenerate:"+name)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"changed.png";im.save(p)
            f=dict(files);f[ptr[0]]=(p,meta);reject(name,f=f)
    for name,old,new in (("wrong_importer_type","textureType: 1","textureType: 0"),
                        ("wrong_importer_format","textureFormat: 12","textureFormat: 4"),
                        ("wrong_sRGB","sRGBTexture: 0","sRGBTexture: 1")):
        need(old in meta,"normalmap_metadata_control_anchor:"+name)
        f=dict(files);f[ptr[0]]=(path,meta.replace(old,new,1));reject(name,f=f)
    bad=dict(proofs);bad[k]=bc3.image_proof((5,7),raw[requests[k].offset:requests[k].offset+64],from_stream=True)
    reject("ordinary_BC3_receipt_scope",p=bad)
    bad=dict(requests);bad[k]=replace(bad[k],offset=requests[keys[1]].offset)
    reject("source_range_swap",p=nm.resolve_requests(root/"providers",pins,bad))
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/provider;b=bytearray(raw);b[0]^=1;p.write_bytes(b)
        reject("provider_padding_drift",p=nm.resolve_requests(Path(tmp),pins,requests))
        b=bytearray(raw);b[requests[k].offset+64]^=1;p.write_bytes(b)
        repin={"Raft_Data/"+provider:("plain",len(b),sha256(b).hexdigest())}
        lower=run(p=nm.resolve_requests(Path(tmp),repin,requests))
        need(lower[FIELD] and not lower["dxt5nm_lower_mips_or_Unity_import_verified"],"normalmap_lower_mip_scope")
    result=dict(status="PASS_ACTUAL_AUTHORED_PUBLIC_DXT5NM_PNG_ROUTE_JOIN",baseline=baseline,
        controls=controls,counterfactual_count=len(controls),textures=rows,unique_authored_pixels_exact=70,
        original_assets_read=False,original_serialized_source_verified=False,Unity_import_verified=False,
        Android_device=False,XAPK=False)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();audit(a.root,a.out)

if __name__=="__main__":main()
