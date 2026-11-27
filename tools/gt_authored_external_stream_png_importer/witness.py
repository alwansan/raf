#!/usr/bin/env python3
"""Actual external resource ranges and imported PNG V9 state, no original data."""
import argparse
from copy import deepcopy
import io
import json
from pathlib import Path,PurePosixPath
import tempfile
from unittest.mock import patch
from zipfile import ZipFile
from PIL import Image
from tools.gt_authored_mesh_binary import witness as w
from tools.gt_authored_serialized_renderer_route import witness as local
from tools.gt_authored_external_pptr_route import witness as ext
from tools.gt_authored_external_png_keywords import witness as kw
from scripts import gt_renderer_submesh_routes as route
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_imported_png_route_importer as imp

ARCHIVE={"bytes":40589,"sha256":"a5af1ef478e6ba00d24165ac78a3cf5064cf6ca7275dbd6caedf0a42ebe5e818"}
PROVIDER="gt-authored-textures.resS"
A,B=ext.PROV_A,ext.PROV_B
PAYLOAD={A:kw.TOP[A]+kw.LOWER[A],B:kw.TOP[B]}
OFFSETS={A:7,B:46}
DATA=b"PREFIX!"+PAYLOAD[A]+b"BETWEEN----"+PAYLOAD[B]+b"TAILBYTES"
SAMPLER={A:dict(m_FilterMode=2,m_Aniso=4,m_MipBias=-.625,m_WrapU=0,m_WrapV=2,m_WrapW=3),
         B:dict(m_FilterMode=1,m_Aniso=2,m_MipBias=.25,m_WrapU=3,m_WrapV=1,m_WrapW=0)}
STATE={A:dict(m_ColorSpace=1,m_IsReadable=False,m_StreamingMipmaps=True,m_StreamingMipmapsPriority=-2,m_MipCount=2),
       B:dict(m_ColorSpace=0,m_IsReadable=True,m_StreamingMipmaps=False,m_StreamingMipmapsPriority=3,m_MipCount=1)}

def read(p):return json.loads(p.read_text())

def fixture():
    schemas,objs=kw.fixture()
    for owner in (A,B):
        tex=objs[owner][821]
        tex.update(deepcopy(STATE[owner]))
        tex["m_TextureSettings"]=deepcopy(SAMPLER[owner])
        tex["image data"]=[]
        tex["m_CompleteImageSize"]=len(PAYLOAD[owner])
        tex["m_StreamData"]=dict(path=PROVIDER,offset=OFFSETS[owner],size=len(PAYLOAD[owner]))
    return schemas,objs

def records(source):
    pins=ext.records(source)
    p=source/PROVIDER
    if p.exists():pins["Raft_Data/"+PROVIDER]=w.pin(p.read_bytes())
    return pins

def gate(source,project,mapping,*,importer=True,pins=None):
    pins=records(source) if pins is None else pins
    vertex={};top={};states={} if importer else None
    objects,externals=route.source_records(source,pins,ext.OWNERS,vertex_payloads=vertex,
                                            png_top_mips=top,png_importer_states=states)
    files,docs=route.actual_index(project,mapping)
    return route.compare(objects,externals,mapping,files,docs,vertex_payloads=vertex,
             material_values=True,material_keywords=True,png_top_mips=top,png_importer_states=states)

def detail(source,project,mapping,pins):
    requests={};trees={};files,_=route.actual_index(project,mapping)
    for owner in (A,B):
        raw=(source/owner).read_bytes()
        w.need(w.pin(raw)==pins["Raft_Data/"+owner],"owner_pin")
        env=w.UnityPy.load(raw)
        tree=env.file.objects[821].read_typetree()
        trees[owner]=tree
        requests[owner]=png.safe_request(tree)
    proofs=png.resolve_requests(source,pins,requests)
    rows=[]
    for owner in (A,B):
        tree=trees[owner];ptr=mapping[(owner,821)][1]
        path,meta=files[ptr[0]]
        p=proofs[owner];state=imp.safe_source(tree)
        try:pv=png.compare(p,path,meta,ptr)
        except (png.Unproven,png.Mismatch) as e:pv=str(e)
        try:iv=imp.compare(state,meta,ptr)
        except (imp.Unproven,imp.Mismatch) as e:iv=str(e)
        d=png.importer_document(meta,ptr)
        rows.append({"owner":owner,"path_id":821,"pointer":ptr,
            "source_stream":tree["m_StreamData"],"source_inline_bytes":len(tree["image data"]),
            "source_state":{k:tree[k] for k in STATE[owner]},"source_sampler":tree["m_TextureSettings"],
            "source_top_rgba_sha256":p.rgba_sha256 if isinstance(p,png.Proof) else p,
            "actual_rgba_sha256":png.exported_image(path).rgba_sha256,
            "export":w.commit(path.read_bytes()),"meta":w.commit(path.with_name(path.name+".meta").read_bytes()),
            "actual_sampler":d["textureSettings"],"actual_mipmaps":d["mipmaps"],
            "actual_readable":d["isReadable"],"actual_streaming":d["streamingMipmaps"],
            "actual_priority":d["streamingMipmapsPriority"],"swizzle_present":"swizzle" in d,
            "png_result":pv,"importer_result":iv})
    return rows

def evaluate(source,project,mapping):
    pins=records(source);rows=[];boost=w.TypeTreeHelper.read_typetree_boost
    w.need(callable(boost),"compiled_decoder_missing")
    for backend,callback in (("compiled",boost),("python",False)):
        with patch.object(w.TypeTreeHelper,"read_typetree_boost",callback):
            rows.append({"decoder":backend,"v8":gate(source,project,mapping,importer=False,pins=pins),
                         "v9":gate(source,project,mapping,pins=pins),"textures":detail(source,project,mapping,pins)})
    return rows

def supported(report):
    return report["selected_same_route_imported_png_supported_serialized_importer_state_verified"]

def replay(archive,out):
    data=archive.read_bytes();w.need(w.commit(data)==ARCHIVE,"archive_pin")
    out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        with ZipFile(io.BytesIO(data)) as z:
            names=z.namelist()
            w.need(len(names)==len(set(names))==60 and z.testzip() is None,"archive_integrity")
            for info in z.infolist():
                p=PurePosixPath(info.filename)
                w.need(not p.is_absolute() and ".." not in p.parts and not info.is_dir() and
                       (info.external_attr>>16&0o170000)!=0o120000,"unsafe_archive_member")
            w.need(sum(i.file_size for i in z.infolist())<=1024*1024,"archive_budget")
            z.extractall(root)
        case=root/"case";pin=read(case/"input.json")
        for owner in ext.OWNERS:
            w.need(w.commit((case/"source"/owner).read_bytes())==pin["owners"][owner]["owner"],"retained_owner_pin")
        for name,expected in read(case/"report.json")["emitted"].items():
            w.need(w.commit((case/"actual-export"/name).read_bytes())==expected,"retained_export_pin")
        _,_,_,mapping=ext.load_traces(case)
        rows=evaluate(case/"source",case/"actual-export",mapping)
        for p in rows:
            print("GT_RETAINED_V9",p["decoder"],supported(p["v9"]),
                  p["v9"]["selected_same_route_imported_png_serialized_importer_state_verified"],
                  p["v9"]["reason_counts"],p["v9"]["counts"].get("imported_png_importer_swizzle_unknown_slots",0),flush=True)
        local.dump(out/"report.json",{"status":"RETAINED_V9_REPLAY","archive":ARCHIVE,
            "new_export_performed":False,"proofs":rows,"original_assets_read":False})

def write_source(source,schemas,objs,provider=DATA):
    pins=ext.write_source(source,schemas,objs,ext.TABLES)
    (source/PROVIDER).write_bytes(provider)
    return pins

def prepare(out):
    out.mkdir(parents=True,exist_ok=False)
    w.need(len(DATA)==79 and all(DATA[OFFSETS[o]:OFFSETS[o]+len(PAYLOAD[o])]==PAYLOAD[o] for o in (A,B)),"provider_fixture")
    pins=write_source(out/"source",*fixture())
    local.dump(out/"input.json",{"owners":pins,"expected_edges":ext.expected_edges(),
               "provider":{"name":PROVIDER,**w.commit(DATA)},
               "ranges":{o:{"offset":OFFSETS[o],**w.commit(PAYLOAD[o])} for o in (A,B)},
               "states":STATE,"samplers":SAMPLER})
    for owner in (A,B):
        env=w.UnityPy.load((out/"source"/owner).read_bytes());tex=env.file.objects[821].read_typetree()
        w.need(tex["m_TextureSettings"]==SAMPLER[owner] and all(tex[k]==v for k,v in STATE[owner].items()),
               "source_state_preflight")
        req=png.source_request(tex)
        w.need(req.provider==PROVIDER and req.offset==OFFSETS[owner] and
               req.descriptor[-1]==len(PAYLOAD[owner]) and not tex["image data"],"source_range_preflight")
    print("GT_EXTERNAL_STREAM_INPUT",w.commit(DATA),"ranges",OFFSETS,flush=True)

def controls(out,project,mapping):
    results=[];saved=out/"controls";saved.mkdir()
    with tempfile.TemporaryDirectory() as td:
        source=Path(td)/"source"
        for mode,reason in (("provider_SHA","png_stream_provider_SHA_mismatch"),
                            ("provider_wrong_range","same_route_png_RGB_DRIFT"),
                            ("provider_extent","png_stream_extent_out_of_bounds"),
                            ("provider_missing_pin","png_stream_provider_not_pinned"),
                            ("provider_alpha_only","same_route_png_ALPHA_ONLY_DRIFT"),
                            ("source_sampler","same_route_png_importer_mipBias_drift"),
                            ("source_color_space","same_route_png_source_mapping_sRGBTexture_drift")):
            schemas,objs=fixture();provider=bytearray(DATA)
            if mode=="provider_wrong_range":objs[B][821]["m_StreamData"]["offset"]=OFFSETS[A]
            if mode=="provider_extent":objs[B][821]["m_StreamData"]["offset"]=len(DATA)-1
            if mode in ("provider_SHA","provider_alpha_only"):provider[OFFSETS[A]+3]=19
            if mode=="source_sampler":objs[A][821]["m_TextureSettings"]["m_MipBias"]=-.25
            if mode=="source_color_space":objs[A][821]["m_ColorSpace"]=0
            write_source(source,schemas,objs,bytes(provider))
            pins=records(source)
            if mode=="provider_SHA":pins["Raft_Data/"+PROVIDER]=w.pin(DATA)
            if mode=="provider_missing_pin":del pins["Raft_Data/"+PROVIDER]
            report=gate(source,project,mapping,pins=pins)
            w.need(not supported(report) and report["reason_counts"]=={reason:2},mode+":"+repr(report))
            for f in (source/A,source/B,source/PROVIDER):
                (saved/(mode+"-"+f.name)).write_bytes(f.read_bytes())
            results.append({"name":mode,"reason":reason,"report":report,
                            "provider":w.commit(bytes(provider)),"pins":pins})
        files,_=route.actual_index(project,mapping)
        path=files[mapping[(A,821)][1][0]][0].with_name(files[mapping[(A,821)][1][0]][0].name+".meta")
        orig=path.read_bytes()
        for mode,old,new,reason in (("actual_meta_wrap","    wrapV: 2","    wrapV: 1","same_route_png_importer_wrapV_drift"),
                                    ("actual_meta_streaming","  streamingMipmaps: 1","  streamingMipmaps: 0","same_route_png_source_mapping_streamingMipmaps_drift"),
                                    ("actual_meta_mips","    enableMipMap: 1","    enableMipMap: 0","same_route_png_source_mapping_enableMipMap_drift"),
                                    ("actual_meta_swizzle","  nPOTScale: 0","  swizzle: 0\n  nPOTScale: 0","same_route_png_exporter_policy_swizzle_drift")):
            try:
                text=orig.decode("utf-8-sig")
                w.need(text.count(old)==1,"ambiguous_actual_meta_mutation:"+mode)
                path.write_text(text.replace(old,new))
                v8=gate(out/"source",project,mapping,importer=False)
                report=gate(out/"source",project,mapping)
                w.need(v8["selected_same_route_imported_png_top_mip_verified"] and not supported(report)
                       and report["reason_counts"]=={reason:2},mode+":"+repr(report))
                data=path.read_bytes();(saved/(mode+".meta")).write_bytes(data)
                results.append({"name":mode,"reason":reason,"report":report,"v8":v8,"mutant":w.commit(data)})
            finally:path.write_bytes(orig)
    return results

def verify(out,project):
    kw.authenticate(out)
    provider=read(out/"raw-provider.json")
    w.need(provider=={"name":PROVIDER,**w.commit(DATA),"color_space_linear":1},"raw_provider_pin")
    w.need((out/"source"/PROVIDER).read_bytes()==DATA,"provider_mutated")
    streams=read(out/"typed-streams.json")
    w.need(len(streams)==2 and {s["owner"] for s in streams}=={A,B},"typed_stream_population")
    for s in streams:
        o=s["owner"];st=STATE[o]
        w.need(s=={"owner":o,"path_id":821,"path":PROVIDER,"offset":OFFSETS[o],"size":len(PAYLOAD[o]),
                  "inline_bytes":0,"loaded_bytes":len(PAYLOAD[o]),"sha256":w.commit(PAYLOAD[o])["sha256"],
                  "integrity":True,"color_space":st["m_ColorSpace"],"mip_count":st["m_MipCount"],
                  "readable":st["m_IsReadable"],"streaming":st["m_StreamingMipmaps"],
                  "priority":st["m_StreamingMipmapsPriority"]},"actual_typed_resource_slice")
    _,_,_,mapping=ext.load_traces(out);saved=local.retain(project,out,mapping)
    proofs=evaluate(out/"source",saved,mapping)
    # Preserve precise observed proof even if the current importer is unsupported.
    emitted={str(p.relative_to(saved)):w.commit(p.read_bytes()) for p in sorted(saved.rglob("*")) if p.is_file()}
    local.dump(out/"observed.json",{"proofs":proofs,"emitted":emitted,"typed_streams":streams})
    for p in proofs:
        r=p["v9"];c=r["counts"]
        w.need(p["v8"]["selected_same_route_imported_png_top_mip_verified"] and supported(r)
               and r["selected_same_route_material_keyword_pass_state_verified"] and
               not r["selected_same_route_imported_png_serialized_importer_state_verified"] and
               c.get("imported_png_stream_source_slots_matched")==4 and
               c.get("imported_png_importer_state_slots_matched")==4 and
               c.get("imported_png_importer_sampler_fields_matched_per_route")==24 and
               c.get("imported_png_importer_source_mapping_fields_matched_per_route")==36 and
               c.get("imported_png_importer_exporter_policy_fields_matched_per_route")==64 and
               c.get("imported_png_importer_swizzle_unknown_slots")==4 and
               c.get("imported_png_RGBA_channels_matched_per_route")==96,
               "actual_stream_V9_scope_or_drift:"+repr(r))
        w.need(all(t["png_result"]==[6,True,False] or t["png_result"]==(6,True,False) for t in p["textures"]),
               "actual_stream_pixel_proof")
    neg=controls(out,saved,mapping)
    local.dump(out/"report.json",{"status":"PASS_ACTUAL_EXTERNAL_STREAM_PNG_SUPPORTED_IMPORTER_STATE",
        "proofs":proofs,"controls":neg,"emitted":emitted,"typed_streams":streams,
        "provider":provider,"unique_textures":2,"unique_ranges":2,"unique_top_mip_pixels":12,
        "unique_top_mip_RGBA_channels":48,"swizzle_verified":False,"original_assets_read":False,
        "lower_mip_parity_verified":False,"unity_import_verified":False,"GPU_verified":False,"XAPK_requested":False})
    print("GT_ACTUAL_EXTERNAL_STREAM_V9_PASS",2,"ranges",2,"stream_slots_per_decoder",4,
          "sampler_fields",24,"source_mapping_fields",36,"policy_fields",64,"swizzle_unknown",4,
          "negative_controls",len(neg),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("replay","prepare","verify"))
    p.add_argument("--archive",type=Path);p.add_argument("--out",type=Path);p.add_argument("--project",type=Path)
    a=p.parse_args()
    if a.mode=="replay":replay(a.archive,a.out)
    elif a.mode=="prepare":prepare(a.out)
    else:verify(a.out,a.project)
