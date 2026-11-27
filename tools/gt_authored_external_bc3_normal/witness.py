#!/usr/bin/env python3
"""Actual authored serialized BC3 and DXT5nm, same physical provider payload.

Two separate actual loader/export instances, each with four real owners.
One pinned corrected public converter build. Baseline V12 alpha policy
unchanged; no production, Unity reimport or original asset claims.
"""
import argparse
from copy import deepcopy
import io
import json
import math
from pathlib import Path
import struct
import tempfile
from unittest.mock import patch
from PIL import Image
from tools.gt_authored_mesh_binary import witness as w
from tools.gt_authored_serialized_renderer_route import witness as local
from tools.gt_authored_external_pptr_route import witness as ext
from tools.gt_authored_external_png_keywords import witness as kw
from tools.gt_authored_external_stream_png_importer import witness as prev
from scripts import gt_renderer_submesh_routes as route
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_imported_bc3_route_pixels as bc3
from scripts import gt_imported_dxt5nm_route_pixels as nm
from scripts import gt_imported_dxt5nm_route_importer as ni

A,B=prev.A,prev.B
PROVIDER=prev.PROVIDER
MODES=("bc3","dxt5nm")
SPECS={
 A:((210,30,0x07e0,0xf81f,0),(32,190,0xf800,0x07e0,1),
    (25,200,0x7bef,0x7bef,2),(220,20,0x001f,0xffe0,3)),
 B:((28,205,0x07ff,0xfbe0,3),(240,15,0xf81f,0x07e0,5),
    (175,35,0x8410,0x8410,4),(45,220,0x07e0,0x001f,7)),
}

def block(a,b,c,d,phase):
    # Encode BC3 storage, not decoded pixels and not exporter output.
    alphas=sum(((i+phase)%8)<<(3*i) for i in range(16))
    colors=sum(((i+i//4+phase)%4)<<(2*i) for i in range(16))
    return bytes((a,b))+alphas.to_bytes(6,"little")+struct.pack("<HHI",c,d,colors)

TOP={o:b"".join(block(*s) for s in SPECS[o]) for o in (A,B)}
LOWER=block(222,11,0x001f,0xffff,6)
PAYLOAD={A:TOP[A]+LOWER,B:TOP[B]}
OFFSETS={A:7,B:98}
DATA=b"PREFIX!"+PAYLOAD[A]+b"BETWEEN----"+PAYLOAD[B]+b"TAILBYTES"
FIELD={"bc3":"selected_same_route_imported_bc3_png_top_mip_verified",
       "dxt5nm":"selected_same_route_imported_dxt5nm_supported_serialized_importer_state_verified"}
NMFIELD="selected_same_route_imported_dxt5nm_png_top_mip_and_importer_verified"
FULL="selected_same_route_imported_dxt5nm_complete_supported_schema_verified"

def read(p):return json.loads(p.read_text())

def fixture(mode):
    schemas,objs=prev.fixture()
    for o in (A,B):
        tex=objs[o][821]
        tex.update(m_Width=5,m_Height=7,m_TextureFormat=12,
                   m_CompleteImageSize=len(PAYLOAD[o]),m_MipCount=2 if o==A else 1,
                   m_LightmapFormat=3 if mode=="dxt5nm" else 0)
        if mode=="dxt5nm":tex["m_ColorSpace"]=0
        tex["m_StreamData"]=dict(path=PROVIDER,offset=OFFSETS[o],size=len(PAYLOAD[o]))
        tex["image data"]=[]
    return schemas,objs

def write_source(source,mode,*,objects=None,provider=DATA):
    schemas,objs=fixture(mode) if objects is None else objects
    pins=ext.write_source(source,schemas,objs,ext.TABLES)
    (source/PROVIDER).write_bytes(provider)
    return pins

def independent_packed(raw):
    # Independently construct a DDS header and decode via Pillow, not via the
    # native source gate or the exporter. Crop is the exact 5x7 DDS size.
    w.need(len(raw)==64,"independent_BC3_top_extent")
    header=(b"DDS "+struct.pack("<7I",124,0x2100f,7,5,64,0,1)+bytes(44)
            +struct.pack("<8I",32,4,int.from_bytes(b"DXT5","little"),0,0,0,0,0)
            +struct.pack("<5I",0x1000,0,0,0,0))
    with Image.open(io.BytesIO(header+raw)) as im:
        return im.convert("RGBA").transpose(Image.Transpose.FLIP_TOP_BOTTOM)

def independent_normal(packed):
    out=bytearray()
    raw=packed.tobytes()
    for i in range(0,len(raw),4):
        r,g,b,a=raw[i:i+4]
        z=(math.isqrt(max(0,255**2-(2*a-255)**2-(2*g-255)**2))+255)//2
        out.extend((a,g,z,r))
    return Image.frombytes("RGBA",packed.size,bytes(out))

def prepare(root):
    root.mkdir(parents=True,exist_ok=False)
    w.need(len(DATA)==171 and len(PAYLOAD[A])==80 and len(PAYLOAD[B])==64 and
           all(DATA[OFFSETS[o]:OFFSETS[o]+len(PAYLOAD[o])]==PAYLOAD[o] for o in (A,B)),
           "provider_fixture")
    for mode in MODES:
        case=root/mode;case.mkdir()
        pins=write_source(case/"source",mode)
        local.dump(case/"input.json",{"mode":mode,"owners":pins,"expected_edges":ext.expected_edges(),
                  "provider":{"name":PROVIDER,**w.commit(DATA)},
                  "ranges":{o:{"offset":OFFSETS[o],**w.commit(PAYLOAD[o]),
                       "top":w.commit(TOP[o]),"blocks":SPECS[o]} for o in (A,B)}})
        decoder=nm if mode=="dxt5nm" else bc3
        for o in (A,B):
            env=w.UnityPy.load((case/"source"/o).read_bytes())
            tex=env.file.objects[821].read_typetree()
            req=decoder.source_request(tex)
            w.need(type(req) is decoder.Request and req.offset==OFFSETS[o] and
                   req.descriptor[:4]==(5,7,12,2 if o==A else 1) and
                   req.mip_lengths==((64,16) if o==A else (64,)) and not tex["image data"],
                   "actual_binary_compressed_preflight")
            packed=independent_packed(TOP[o]);normal=independent_normal(packed)
            w.need(bc3.decode_top((5,7),TOP[o]).tobytes()==packed.tobytes() and
                   nm.decode_top((5,7),TOP[o])[1].tobytes()==normal.tobytes(),"independent_fixture_oracle")
            rgba=packed.tobytes()
            w.need(any(rgba[i+3]==0 and any(rgba[i:i+3]) for i in range(0,len(rgba),4)) and
                   255 in rgba[3::4] and 0 in rgba[3::4],"transparent_RGB_and_alpha_modes")
            w.need(127 in normal.tobytes()[2::4] and max(normal.tobytes()[2::4])>127,"normal_Z_coverage")
        print("GT_COMPRESSED_ACTUAL_SOURCE",mode,w.commit(DATA),flush=True)

def gate(source,project,mapping,mode,*,importer=True,pins=None):
    normal=mode=="dxt5nm"
    pins=prev.records(source) if pins is None else pins
    verts={};top={};states={} if normal and importer else None
    objects,externals=route.source_records(source,pins,ext.OWNERS,vertex_payloads=verts,
                png_top_mips=top,png_importer_states=states,png_bc3=not normal,png_normalmap=normal)
    files,docs=route.actual_index(project,mapping)
    return route.compare(objects,externals,mapping,files,docs,vertex_payloads=verts,material_values=True,
             material_keywords=True,png_top_mips=top,png_importer_states=states,
             png_bc3=not normal,png_normalmap=normal)

def basic_gate(source,project,mapping):
    verts={}
    obj,ex=route.source_records(source,prev.records(source),ext.OWNERS,vertex_payloads=verts)
    files,docs=route.actual_index(project,mapping)
    return route.compare(obj,ex,mapping,files,docs,vertex_payloads=verts,
                         material_values=True,material_keywords=True)

def authenticate(case,mode):
    kw.authenticate(case)
    provider=read(case/"raw-provider.json")
    w.need(provider=={"name":PROVIDER,**w.commit(DATA),"color_space_linear":1,
           "color_space_gamma":0,"bc3_format":12,"dxt5nm_usage":3},"raw_provider_abi")
    w.need((case/"source"/PROVIDER).read_bytes()==DATA,"provider_mutated")
    streams=read(case/"typed-streams.json")
    w.need(len(streams)==2 and {s["owner"] for s in streams}=={A,B},"stream_population")
    for s in streams:
        o=s["owner"];st=prev.STATE[o]
        w.need(s=={"owner":o,"path_id":821,"path":PROVIDER,"offset":OFFSETS[o],
               "size":len(PAYLOAD[o]),"inline_bytes":0,"loaded_bytes":len(PAYLOAD[o]),
               "sha256":w.commit(PAYLOAD[o])["sha256"],"integrity":True,
               "color_space":0 if mode=="dxt5nm" else st["m_ColorSpace"],"mip_count":st["m_MipCount"],
               "texture_format":12,"usage":3 if mode=="dxt5nm" else 0,
               "readable":st["m_IsReadable"],"streaming":st["m_StreamingMipmaps"],
               "priority":st["m_StreamingMipmapsPriority"]},"actual_typed_compressed_slice")
    return streams

def details(case,project,mapping,mode):
    files,_=route.actual_index(project,mapping);rows=[]
    for o in (A,B):
        ptr=mapping[(o,821)][1];path,meta=files[ptr[0]]
        packed=independent_packed(TOP[o]);expected=independent_normal(packed) if mode=="dxt5nm" else packed
        with Image.open(path) as im:
            w.need(im.mode=="RGBA" and im.size==(5,7),"actual_PNG_schema")
            actual=im.tobytes()
        d=png.importer_document(meta,ptr,texture_type=int(mode=="dxt5nm"))
        w.need(actual==expected.tobytes(),"independent_actual_PNG_pixel_drift:"+o+":"+mode)
        p=packed.tobytes();n=expected.tobytes()
        rows.append({"owner":o,"path_id":821,"pointer":ptr,"top":w.commit(TOP[o]),
            "packed_RGBA":w.commit(p),"expected_RGBA":w.commit(n),"actual_RGBA":w.commit(actual),
            "export":w.commit(path.read_bytes()),"meta":w.commit(path.with_name(path.name+".meta").read_bytes()),
            "alpha_values":sorted(set(p[3::4])),
            "transparent_nonzero_RGB":sum(p[i+3]==0 and any(p[i:i+3]) for i in range(0,len(p),4)),
            "normal_Z_interior":sum(v>127 for v in n[2::4]) if mode=="dxt5nm" else None,
            "normal_Z_clamp":n[2::4].count(127) if mode=="dxt5nm" else None,
            "texture_type":d["textureType"],"format":d["textureFormat"],
            "sRGB":d["mipmaps"]["sRGBTexture"],"alpha_is_transparency":d["alphaIsTransparency"],
            "swizzle_present":"swizzle" in d})
    return rows

def controls(case,project,mapping,mode):
    results=[];saved=case/"controls";saved.mkdir()
    with tempfile.TemporaryDirectory() as td:
        source=Path(td)/"source"
        pairs=[("wrong_provider_hash","bc3_stream_provider_SHA_mismatch"),
               ("missing_provider_pin","bc3_stream_provider_not_pinned"),
               ("wrong_resource_range","same_route_png_RGB_DRIFT"),
               ("source_alpha_endpoint","same_route_png_RGB_DRIFT" if mode=="dxt5nm" else "same_route_png_ALPHA_ONLY_DRIFT"),
               ("wrong_usage","unsupported_dxt5nm_usage_or_color_space" if mode=="dxt5nm" else "unsupported_bc3_texture_usage"),
               ("lower_mip_only",None)]
        if mode=="dxt5nm":pairs.append(("source_mip_bias","same_route_png_importer_mipBias_drift"))
        for name,reason in pairs:
            schemas,objs=fixture(mode);data=bytearray(DATA)
            if name in ("wrong_provider_hash","source_alpha_endpoint"):data[OFFSETS[A]]=198
            if name=="wrong_resource_range":objs[B][821]["m_StreamData"]["offset"]=OFFSETS[A]
            if name=="wrong_usage":objs[A][821]["m_LightmapFormat"]=0 if mode=="dxt5nm" else 3
            if name=="source_mip_bias":objs[A][821]["m_TextureSettings"]["m_MipBias"]=-.25
            if name=="lower_mip_only":data[OFFSETS[A]+64]^=1
            write_source(source,mode,objects=(schemas,objs),provider=bytes(data))
            pins=prev.records(source)
            if name=="wrong_provider_hash":pins["Raft_Data/"+PROVIDER]=w.pin(DATA)
            if name=="missing_provider_pin":del pins["Raft_Data/"+PROVIDER]
            result=gate(source,project,mapping,mode,pins=pins)
            if reason is None:w.need(result[FIELD[mode]],"top_mip_scope_false_rejection")
            else:w.need(not result[FIELD[mode]] and result["reason_counts"]=={reason:2},name+":"+repr(result))
            if name=="source_mip_bias":
                w.need(gate(source,project,mapping,mode,importer=False,pins=pins)[NMFIELD],"V12_control_broke_V11")
            for f in (source/A,source/B,source/PROVIDER):
                (saved/(name+"-"+f.name)).write_bytes(f.read_bytes())
            results.append({"name":name,"expected":reason or "TOP_MIP_ONLY_ACCEPTANCE","report":result,
                "pins":pins,"provider":w.commit(bytes(data))})
        files,_=route.actual_index(project,mapping)
        ptr=mapping[(A,821)][1];p=files[ptr[0]][0];original=p.read_bytes()
        images=[("export_vertical_flip",Image.open(io.BytesIO(original)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),
                 "same_route_png_VERTICAL_FLIP")]
        if mode=="dxt5nm":images.append(("export_packed_not_normal",independent_packed(TOP[A]),"same_route_png_RGB_DRIFT"))
        for name,im,reason in images:
            try:
                im.save(p)
                result=gate(case/"source",project,mapping,mode)
                w.need(not result[FIELD[mode]] and result["reason_counts"]=={reason:2},name+":"+repr(result))
                data=p.read_bytes();(saved/(name+".png")).write_bytes(data)
                results.append({"name":name,"expected":reason,"report":result,"mutant":w.commit(data)})
            finally:p.write_bytes(original);im.close()
        if mode=="dxt5nm":
            p=p.with_name(p.name+".meta");original=p.read_bytes()
            try:
                text=original.decode("utf-8-sig");old="    wrapV: 2"
                w.need(text.count(old)==1,"wrapV_control_anchor")
                p.write_text(text.replace(old,"    wrapV: 1"))
                result=gate(case/"source",project,mapping,mode)
                v11=gate(case/"source",project,mapping,mode,importer=False)
                reason="same_route_png_importer_wrapV_drift"
                w.need(v11[NMFIELD] and not result[FIELD[mode]] and result["reason_counts"]=={reason:2},
                       "actual_normal_meta_wrap:"+repr(result))
                data=p.read_bytes();(saved/"actual_meta_wrap.meta").write_bytes(data)
                results.append({"name":"actual_meta_wrap","expected":reason,"report":result,"mutant":w.commit(data)})
            finally:p.write_bytes(original)
    return results

def verify(case,project,mode):
    streams=authenticate(case,mode)
    _,_,_,mapping=ext.load_traces(case);saved=local.retain(project,case,mapping)
    proofs=[];boost=w.TypeTreeHelper.read_typetree_boost
    w.need(callable(boost),"compiled_decoder_missing")
    emitted={str(p.relative_to(saved)):w.commit(p.read_bytes()) for p in sorted(saved.rglob("*")) if p.is_file()}
    for backend,callback in (("compiled",boost),("python",False)):
        with patch.object(w.TypeTreeHelper,"read_typetree_boost",callback):
            report=gate(case/"source",saved,mapping,mode)
            v4=basic_gate(case/"source",saved,mapping)
            proofs.append({"decoder":backend,"report":report,"v4":v4})
    local.dump(case/"observed.json",{"proofs":proofs,"emitted":emitted,"typed_streams":streams})
    for proof in proofs:
        r=proof["report"];c=r["counts"]
        w.need(proof["v4"]["selected_same_route_material_keyword_pass_state_verified"] and r[FIELD[mode]]
               and r["selected_same_route_material_keyword_pass_state_verified"] and
               c.get("complete_renderer_routes")==2 and c.get("complete_imported_png_bound_submesh_routes")==4 and
               c.get("imported_png_stream_source_slots_matched")==4 and
               c.get("imported_png_pixels_matched_per_route")==140 and
               c.get("imported_png_RGBA_channels_matched_per_route")==560 and
               not r.get("selected_same_route_imported_png_top_mip_verified",False) and
               not r.get("selected_same_route_imported_png_serialized_importer_state_verified",False),
               "actual_compressed_scope_or_drift:"+repr(r))
        if mode=="dxt5nm":
            w.need(r[NMFIELD] and not r[FULL] and
                   c.get("imported_png_importer_sampler_fields_matched_per_route")==24 and
                   c.get("imported_png_importer_source_mapping_fields_matched_per_route")==36 and
                   c.get("imported_png_importer_exporter_policy_fields_matched_per_route")==68 and
                   c.get("dxt5nm_importer_observed_bumpmap_defaults_matched_per_route")==12 and
                   c.get("imported_png_importer_swizzle_unknown_slots")==4 and
                   not r.get("selected_same_route_imported_bc3_png_top_mip_verified",False),"actual_normal_importer_scope")
    rows=details(case,saved,mapping,mode)
    neg=controls(case,saved,mapping,mode)
    local.dump(case/"report.json",{"status":"PASS_ACTUAL_SERIALIZED_"+mode.upper(),"mode":mode,
        "proofs":proofs,"textures":rows,"typed_streams":streams,"emitted":emitted,"controls":neg,
        "unique_textures":2,"unique_pixels":70,"unique_RGBA_channels":280,
        "shader_execution":False,"original_assets_read":False,"lower_mip_parity_verified":False,
        "unity_import_verified":False,"GPU_verified":False,"XAPK_requested":False})
    print("GT_ACTUAL_COMPRESSED_PASS",mode,"pixels",70,"channels",280,
          "negative_controls",sum(x["expected"]!="TOP_MIP_ONLY_ACCEPTANCE" for x in neg),
          "lower_mip_scope_controls",1,flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("prepare","verify"))
    p.add_argument("--out",type=Path,required=True);p.add_argument("--project",type=Path)
    p.add_argument("--case",choices=MODES)
    a=p.parse_args()
    if a.mode=="prepare":prepare(a.out)
    else:verify(a.out,a.project,a.case)
