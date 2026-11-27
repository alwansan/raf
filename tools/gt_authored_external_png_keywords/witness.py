#!/usr/bin/env python3
"""Retained and new actual external-owner binary -> PNG + serialized state V4/V8.

No original data or generated source objects/YAML baseline. Nonempty authored
keyword lists are serialized state, not valid active Shader variants.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from unittest.mock import patch
from zipfile import ZipFile

from PIL import Image
from tools.gt_authored_mesh_binary import witness as w
from tools.gt_authored_serialized_renderer_route import witness as local
from tools.gt_authored_external_pptr_route import witness as ext
from scripts import gt_renderer_submesh_routes as route
from scripts import gt_material_route_keyword_state as keywords
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_verify_original_mesh_export as mesh

ARCHIVE_SHA="7a09666cddddb6ede58ab32bbd616fa6a2df248bb52627d4310a6b2f86e2a7e4"
ARCHIVE_BYTES=39284
# Six asymmetric pixels per texture; nonzero RGB under zero alpha,
# distinct alpha 0/1/64/127/254/255, lower mip not part of PNG proof.
TOP={
    ext.PROV_A:bytes((11,23,37,0, 53,71,89,1, 97,113,131,64,
                      149,163,181,127, 197,211,223,254, 239,251,17,255)),
    ext.PROV_B:bytes((9,41,73,255, 105,137,169,254, 201,233,19,127,
                      51,83,115,64, 147,179,211,1, 243,29,61,0)),
}
LOWER={ext.PROV_A:bytes((12,34,56,78)),ext.PROV_B:bytes((87,65,43,21))}
STATE={
    ext.PROV_A:{"m_ValidKeywords":["GT_VALID_A","GT_SHARED"],
                "m_InvalidKeywords":["GT_INVALID_A"],"disabledShaderPasses":["GT_PASS_A"]},
    ext.PROV_B:{"m_ValidKeywords":["GT_VALID_B","GT_SHARED"],
                "m_InvalidKeywords":["GT_INVALID_B"],"disabledShaderPasses":["GT_PASS_B"]},
}

def read(path):
    return json.loads(path.read_text())

def fixture():
    schemas,objects=ext.fixture()
    for owner in (ext.PROV_A,ext.PROV_B):
        obj=objects[owner]
        obj[811].update(deepcopy(STATE[owner]))
        tex=obj[821]
        tex.update(m_Width=3,m_Height=2,m_MipCount=2,m_CompleteImageSize=28)
        tex["image data"]=list(TOP[owner]+LOWER[owner])
    return schemas,objects

def records(source):
    return ext.records(source)

def run_gate(source,project,mapping,*,pixels):
    vertex={};top={} if pixels else None
    objects,externals=route.source_records(source,records(source),ext.OWNERS,
                       vertex_payloads=vertex,png_top_mips=top)
    files,docs=route.actual_index(project,mapping)
    return route.compare(objects,externals,mapping,files,docs,vertex_payloads=vertex,
                         material_values=True,material_keywords=True,png_top_mips=top)

def per_texture(source,project,mapping):
    rows=[]
    files,_=route.actual_index(project,mapping)
    for name in (ext.PROV_A,ext.PROV_B):
        env=w.UnityPy.load((source/name).read_bytes())
        tree=env.file.objects[821].read_typetree()
        material=env.file.objects[811].read_typetree()
        proof=png.safe_request(tree)
        ptr=mapping[(name,821)][1]
        path,meta=files[ptr[0]]
        actual=png.exported_image(path)
        try:
            pixels,streamed,unset=png.compare(proof,path,meta,ptr)
            verdict={"status":"MATCH","pixels":pixels,"streamed":streamed,"importer_mip_bias_unset":unset}
        except (png.Unproven,png.Mismatch) as e:
            verdict={"status":"UNPROVEN_OR_DRIFT","reason":str(e)}
        with Image.open(path) as im:
            rgba=im.convert("RGBA").tobytes()
        rows.append({"owner":name,"source_path_id":821,"source_owner":w.commit((source/name).read_bytes()),
            "source_descriptor":{k:tree[k] for k in ("m_Width","m_Height","m_MipCount","m_TextureFormat","m_CompleteImageSize")},
            "source_image_bytes":w.commit(bytes(tree["image data"])),
            "source_top_rgba_sha256":proof.rgba_sha256 if isinstance(proof,png.Proof) else None,
            "source_unproven_reason":proof if isinstance(proof,str) else None,
            "export_rgba_sha256":actual.rgba_sha256,"export_file":w.commit(path.read_bytes()),
            "export_meta":w.commit(path.with_name(path.name+".meta").read_bytes()),
            "export_pointer":ptr,"export_alpha_values":sorted(set(rgba[3::4])),
            "source_keyword_state":{k:material[k] for k in STATE[name]},"verdict":verdict})
    return rows

def evaluate(source,project,mapping):
    rows=[];boost=w.TypeTreeHelper.read_typetree_boost
    w.need(callable(boost),"compiled_decoder_missing")
    for backend,callback in (("compiled",boost),("python",False)):
        with patch.object(w.TypeTreeHelper,"read_typetree_boost",callback):
            rows.append({"decoder":backend,"v4":run_gate(source,project,mapping,pixels=False),
                         "v8":run_gate(source,project,mapping,pixels=True),
                         "textures":per_texture(source,project,mapping)})
    return rows

def replay(archive,out):
    data=archive.read_bytes()
    w.need(w.commit(data)=={"bytes":ARCHIVE_BYTES,"sha256":ARCHIVE_SHA},"retained_archive_pin_mismatch")
    out.mkdir(parents=True,exist_ok=False)
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        with ZipFile(io.BytesIO(data)) as z:
            names=z.namelist()
            w.need(len(names)==len(set(names))==50 and z.testzip() is None,"retained_archive_crc_or_population")
            for info in z.infolist():
                p=PurePosixPath(info.filename)
                w.need(not p.is_absolute() and ".." not in p.parts and not info.is_dir()
                       and info.file_size<=1024*1024 and not info.external_attr>>16&0o170000==0o120000,
                       "unsafe_retained_archive_member")
            w.need(sum(i.file_size for i in z.infolist())<=1024*1024,"retained_archive_budget")
            z.extractall(root)
        case=root/"case"
        pin=read(case/"input.json")
        for name in ext.OWNERS:
            w.need(w.commit((case/"source"/name).read_bytes())==pin["owners"][name]["owner"],"retained_owner_pin")
        report=read(case/"report.json")
        for name,expected in report["emitted"].items():
            w.need(w.commit((case/"actual-export"/name).read_bytes())==expected,"retained_export_pin")
        _,_,_,mapping=ext.load_traces(case)
        rows=evaluate(case/"source",case/"actual-export",mapping)
        for row in rows:
            w.need(all(all(not values for values in t["source_keyword_state"].values()) for t in row["textures"]),
                   "retained_keywords_not_empty")
            print("GT_RETAINED_REPLAY",row["decoder"],row["v4"]["selected_same_route_material_keyword_pass_state_verified"],
                  row["v8"]["selected_same_route_imported_png_top_mip_verified"],row["v8"]["reason_counts"],flush=True)
        local.dump(out/"report.json",{"status":"RETAINED_ACTUAL_EXPORT_REPLAY",
            "archive":w.commit(data),"archive_members":50,"new_export_performed":False,
            "keyword_scope":"all three lanes empty in both materials; no nonempty proof",
            "proofs":rows,"original_assets_read":False})

def prepare(out):
    out.mkdir(parents=True,exist_ok=False)
    schemas,objects=fixture()
    pins=ext.write_source(out/"source",schemas,objects,ext.TABLES)
    local.dump(out/"input.json",{"owners":pins,"expected_edges":ext.expected_edges(),
             "keyword_states":STATE,"top_rgba":{k:w.commit(v) for k,v in TOP.items()},
             "lower_rgba":{k:w.commit(v) for k,v in LOWER.items()}})
    for owner in (ext.PROV_A,ext.PROV_B):
        env=w.UnityPy.load((out/"source"/owner).read_bytes())
        mat=env.file.objects[811].read_typetree();tex=env.file.objects[821].read_typetree()
        w.need(all(mat[k]==v for k,v in STATE[owner].items()),"actual_source_keyword_state")
        w.need(bytes(tex["image data"])==TOP[owner]+LOWER[owner],"actual_source_RGBA_bytes")
        w.need(isinstance(png.source_request(tex),png.Proof),"actual_source_png_schema")
    print("GT_NONEMPTY_KEYWORD_TEXTURE_INPUT",pins,flush=True)

def authenticate(out):
    pin=read(out/"input.json");raw=read(out/"raw-parser.json");typed=read(out/"typed-load.json")
    w.need(len(raw)==4 and {x["owner"] for x in raw}==set(ext.OWNERS),"raw_owner_population")
    for row in raw:
        owner=row["owner"];p=pin["owners"][owner]
        w.need(row["generation"]==22 and row["embedded_type_tree"] is False and
               row["owner_sha256"]==p["owner"]["sha256"] and
               p["owner"]==w.commit((out/"source"/owner).read_bytes()),"raw_owner_authentication")
        w.need([x["path"] for x in row["externals"]]==ext.TABLES[owner] and
               all(x["path"]==x["resolved_name"] and x["type"]==0 for x in row["externals"]),"external_table_drift")
        w.need(sorted(row["objects"],key=lambda x:x["path_id"])==
               [{k:v for k,v in x.items() if k!="offset"} for x in p["objects"]],"raw_payload_commitment")
    ids={(n,p):c for n,items in ext.IDS.items() for p,c in items.items()}
    w.need(len(typed["objects"])==16 and {(x["owner"],x["path_id"]):x["class_id"] for x in typed["objects"]}==ids and
           all(x["typed"] and x["serialized_collection"] for x in typed["objects"]),"typed_population")
    w.need({x["owner"]:x["dependencies"] for x in typed["collections"]}==
           {n:[n]+ext.TABLES[n] for n in ext.OWNERS},"typed_dependency_table_order")
    edges=read(out/"typed-external-edges.json")
    k=("owner","path_id","file_id","target_owner","target_path_id","target_class_id")
    w.need(len(edges)==10 and all(x["reference_equal"] for x in edges) and
           Counter(tuple(x[f] for f in k) for x in edges)==
           Counter(tuple(x[f] for f in k) for x in ext.expected_edges()),"typed_external_edge_drift")

def controls(out,project,mapping):
    results=[];saved=out/"controls";saved.mkdir()
    with tempfile.TemporaryDirectory() as td:
        source=Path(td)/"source"
        for name,mode,reason in (
            ("source_binary_keyword_bucket_swap","bucket","material_keyword_bucket_drift"),
            ("source_binary_invalid_keyword_removed","invalid","unexpected_material_invalid_keyword"),
            ("source_binary_disabled_pass_removed","pass","unexpected_material_disabled_pass"),
            ("source_binary_alpha_only","alpha","same_route_png_ALPHA_ONLY_DRIFT"),
            ("source_binary_RGB_only","rgb","same_route_png_RGB_DRIFT"),
            ("source_binary_lower_mip_only","lower",None)):
            schemas,objs=fixture();obj=objs[ext.PROV_A]
            if mode=="bucket":
                mat=obj[811];mat["m_ValidKeywords"],mat["m_InvalidKeywords"]=mat["m_InvalidKeywords"],mat["m_ValidKeywords"]
            if mode=="invalid":obj[811]["m_InvalidKeywords"]=[]
            if mode=="pass":obj[811]["disabledShaderPasses"]=[]
            if mode=="alpha":obj[821]["image data"][3]=19
            if mode=="rgb":obj[821]["image data"][0]=12
            if mode=="lower":obj[821]["image data"][24]=13
            ext.write_source(source,schemas,objs,ext.TABLES)
            before=run_gate(source,project,mapping,pixels=False)
            after=run_gate(source,project,mapping,pixels=True)
            if reason is None:
                w.need(after["selected_same_route_imported_png_top_mip_verified"],"lower_mip_scope_false_rejection")
            else:
                w.need(not after["selected_renderer_routes_preserved"] and after["reason_counts"]=={reason:2},
                       name+":"+repr(after))
                if mode in ("alpha","rgb"):w.need(before["selected_same_route_material_keyword_pass_state_verified"],"pixel_control_broke_V4")
            changed=(source/ext.PROV_A).read_bytes()
            (saved/(name+".assets")).write_bytes(changed)
            results.append({"name":name,"expected":reason or "TOP_MIP_ONLY_ACCEPTANCE",
                            "source_owner":w.commit(changed),"v4":before,"v8":after})
        files,_=route.actual_index(project,mapping)
        ptr=mapping[(ext.PROV_A,821)][1];path=files[ptr[0]][0]
        original=path.read_bytes()
        other=files[mapping[(ext.PROV_B,821)][1][0]][0].read_bytes()
        for name,reason in (("actual_export_vertical_flip","same_route_png_VERTICAL_FLIP"),
                            ("actual_export_wrong_owner_pixels","same_route_png_RGB_DRIFT")):
            try:
                if "flip" in name:
                    with Image.open(io.BytesIO(original)) as im:
                        im.transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(path)
                else:path.write_bytes(other)
                mutant=path.read_bytes()
                (saved/(name+".png")).write_bytes(mutant)
                after=run_gate(out/"source",project,mapping,pixels=True)
                w.need(not after["selected_renderer_routes_preserved"] and after["reason_counts"]=={reason:2},
                       name+":"+repr(after))
                results.append({"name":name,"expected":reason,"mutant":w.commit(mutant),"v8":after})
            finally:path.write_bytes(original)
    return results

def verify(out,project):
    authenticate(out)
    mat,mtrace,_,mapping=ext.load_traces(out)
    saved=local.retain(project,out,mapping)
    proofs=evaluate(out/"source",saved,mapping)
    for proof in proofs:
        v4,v8=proof["v4"],proof["v8"];c=v8["counts"]
        w.need(v4["selected_same_route_material_keyword_pass_state_verified"] and
               v8["selected_same_route_imported_png_top_mip_verified"] and
               c.get("complete_renderer_routes")==2 and c.get("complete_imported_png_bound_submesh_routes")==4 and
               c.get("imported_png_top_mip_slots_matched")==4 and
               c.get("imported_png_pixels_matched_per_route")==24 and
               c.get("imported_png_RGBA_channels_matched_per_route")==96 and
               c.get("material_valid_keyword_entries_matched")==8 and
               c.get("material_invalid_keyword_entries_matched")==4 and
               c.get("material_disabled_pass_entries_matched")==4,
               "actual_nonempty_keyword_png_route_failed:"+repr(proof))
        w.need(all(t["verdict"]["status"]=="MATCH" and t["source_descriptor"]["m_MipCount"]==2
                   and t["export_alpha_values"]==[0,1,64,127,254,255] for t in proof["textures"]),
               "actual_png_per_texture_mismatch")
    neg=controls(out,saved,mapping)
    w.need(len(neg)==8 and sum(x["expected"]=="TOP_MIP_ONLY_ACCEPTANCE" for x in neg)==1,"control_population")
    emitted={str(p.relative_to(saved)):w.commit(p.read_bytes()) for p in sorted(saved.rglob("*")) if p.is_file()}
    local.dump(out/"report.json",{"status":"PASS_ACTUAL_EXTERNAL_PPTR_PNG_KEYWORD_STATE",
        "proofs":proofs,"controls":neg,"emitted":emitted,"actual_raw_objects":16,
        "actual_typed_objects":16,"typed_nonnull_external_pptrs":10,"same_loaded_reference_traces":14,
        "unique_textures":2,"unique_top_mip_pixels":12,"unique_top_mip_RGBA_channels":48,
        "unique_material_keyword_pass_entries":8,"shader_program_verified":False,
        "active_variants_verified":False,"lower_mip_parity_verified":False,"original_assets_read":False,
        "original_runtime_verified":False,"unity_import_verified":False,"device_verified":False,"XAPK_requested":False})
    print("GT_ACTUAL_EXTERNAL_PNG_KEYWORDS_PASS",2,"renderers_per_decoder",2,"submeshes_per_decoder",4,
          "pixels_per_route",24,"channels_per_route",96,"negative_controls",7,"lower_mip_scope_control",1,flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("replay","prepare","verify"))
    p.add_argument("--archive",type=Path);p.add_argument("--out",type=Path);p.add_argument("--project",type=Path)
    a=p.parse_args()
    if a.mode=="replay":replay(a.archive,a.out)
    elif a.mode=="prepare":prepare(a.out)
    else:verify(a.out,a.project)
