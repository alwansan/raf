#!/usr/bin/env python3
"""Reuse the exact retained authored binary, verify actual repaired export.
Not a game-data recovery tool or permission assertion.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

from PIL import Image
from tools.gt_authored_particle108_collection_cause import witness as previous

ARCHIVE="ea58cf0db6543ebce8bc989562b3e93f6c666f0aa9324258005e98e108048a8a"
OWNER=previous.OWNER
IDS=(821,822,823,824)
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,v):path.write_text(json.dumps(v,sort_keys=True,indent=2)+"\n")
def prepare(archive,out):
    data=archive.read_bytes()
    need(len(data)==11504 and sha(data)==ARCHIVE,"retained actual collision archive")
    out.mkdir();(out/"source").mkdir()
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==22 and z.testzip() is None,"retained CRC")
        report=json.loads(z.read("report.json"))
        need(report["status"]=="PASS_AUTHORED_CACHE_KEY_COLLISION_SAME_EXPORT"
             and report["nonexportable_redirects"]==2,"retained actual baseline")
        raw=z.read("source/"+OWNER)
        typed=json.loads(z.read("typed.json"))
        old=json.loads(z.read("capture.json"))
        need(len(raw)==1920 and len(typed)==len(old)==4,"retained source/capture")
        need(old[0]["pointer"]==old[1]["pointer"] and not old[0]["exportable"] and not old[1]["exportable"],
             "retained pointer alias")
        (out/"source"/OWNER).write_bytes(raw)
        for name in ("capture.json","report.json","typed.json","input.json"):
            (out/("prior-"+name)).write_bytes(z.read(name))
    # Read actual serialized data, rather than recreating fixture bytes.
    env=previous.w.UnityPy.load(raw)
    need(set(env.file.objects)==set(previous.IDS),"retained object population")
    hashes={};rows=[]
    for i,pid in enumerate(IDS):
        tx=env.file.objects[pid].read_typetree()
        field=next(k for k in ("image data","m_ImageData") if k in tx)
        rgba=bytes(tx[field])
        need((tx["m_Width"],tx["m_Height"])==previous.DIMS[i] and
             tx["m_TextureFormat"]==4 and tx["m_MipCount"]==1 and rgba==previous.RGBA[i],
             "retained source RGBA32 single mip")
        mat=env.file.objects[pid-10].read_typetree()
        need(previous.normalize_texenvs(mat["m_SavedProperties"]["m_TexEnvs"])["_MainTex"][0]==(0,pid),
             "retained source pointer")
        hashes[str(pid)]=sha(rgba)
        rows.append({"path_id":pid,"width":tx["m_Width"],"height":tx["m_Height"],"rgba_sha256":sha(rgba)})
    need([hashes[str(i)] for i in IDS]==[r["sha256"] for r in typed],"retained typed hash join")
    dump(out/"approval.json",{"owner_sha256":sha(raw),"payload_sha256":hashes,
        "explicit_preservation_ids":[821,822],"source_textures":rows,"authored_only":True})
    print("GT_PRESERVATION_RETAINED_INPUT",sha(raw),len(raw))
def stage(root):
    # Reuse the pinned actual capture anchor and separate disposable CLI host.
    previous.stage(root)
    d=root/"ar-host/Source/AssetRipper.Export.UnityProjects"
    tools=root/"tools/gt_particle108_verified_texture_preservation"
    for name in ("RaftGTCollectionWitness.cs","VerifiedTexturePreservationExporter.cs"):
        shutil.copyfile(tools/name,d/name)
def verify(out,project):
    auth=json.loads((out/"approval.json").read_text())
    before=json.loads((out/"prior-capture.json").read_text())
    capture=json.loads((out/"capture.json").read_text())
    typed=json.loads((out/"typed.json").read_text())
    need(len(capture)==len(typed)==4 and [r["path_id"] for r in typed]==list(IDS)
        and [r["sha256"] for r in typed]==[auth["payload_sha256"][str(i)] for i in IDS],
        "actual typed source identity")
    rows={r["path_id"]:r for r in capture}
    need(set(rows)==set(IDS) and all(r["exportable"] and r["collection"]=="TextureExportCollection"
        for r in rows.values()),"actual repaired collection census")
    pointers=[rows[i]["pointer"] for i in IDS]
    need(len({r["guid"] for r in pointers})==4 and all(r["type"]==before[2]["pointer"]["type"] and r["fileID"]!=0 and
         re.fullmatch("[0-9a-f]{32}",r["guid"]) and r["guid"]!="0"*32 for r in pointers),
         "distinct real native texture pointers")
    # Type enumeration values can differ by schema. The actual prior controls
    # are the authoritative pointer category for this pinned exporter.
    need(pointers[2]["type"]==before[2]["pointer"]["type"]==pointers[3]["type"]==before[3]["pointer"]["type"],
         "unselected native pointer category")
    assets=project/"Assets";mats={};pngs={}
    for f in assets.rglob("*.mat"):
        mat=previous.read_yaml(f)["Material"];name=mat["m_Name"]
        if not name.startswith("GT Collection Material "):continue
        pid=int(name.rsplit(" ",1)[1]);need(pid not in mats,"duplicate output material")
        slots=mat["m_SavedProperties"]["m_TexEnvs"]
        if isinstance(slots,list):
            need(len(slots)==1 and isinstance(slots[0],dict),"material list schema");slots=slots[0]
        need(isinstance(slots,dict) and set(slots)=={"_MainTex"},"material slot")
        p=slots["_MainTex"]["m_Texture"]
        actual={"fileID":int(p["fileID"]),"guid":str(p["guid"]),"type":int(p["type"])}
        need(pid+10 in rows and actual==rows[pid+10]["pointer"],"actual material pointer")
        mats[pid]=actual
    need(set(mats)=={811,812,813,814},"actual material population")
    for f in assets.rglob("*.png"):
        meta=previous.read_yaml(f.with_name(f.name+".meta"));guid=str(meta["guid"])
        need(guid not in pngs,"duplicate image guid")
        with Image.open(f) as image:
            im=image.convert("RGBA");pngs[guid]=(im.size,im.tobytes())
    need(set(pngs)=={p["guid"] for p in pointers},"four exact native images")
    observed=[];count=0
    for i,pid in enumerate(IDS):
        dim=previous.DIMS[i]
        expected=Image.frombytes("RGBA",dim,previous.RGBA[i]).transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes()
        got=pngs[rows[pid]["pointer"]["guid"]]
        need(got==(dim,expected),"source/export RGBA parity")
        count+=dim[0]*dim[1];observed.append(got[1])
    need(sum(x!=y for x,y in zip(observed[0][3::4],observed[1][3::4]))==3,
         "restored distinct alpha bytes")
    report={"status":"PASS_ACTUAL_AUTHORED_VERIFIED_TEXTURE_PRESERVATION",
        "reused_prior_actual_archive_sha256":ARCHIVE,"new_source_fixtures":0,
        "explicit_preservation_ids":[821,822],"before_nonexportable_redirects":2,
        "after_nonexportable_redirects":0,"before_actual_pngs":2,"after_actual_pngs":4,
        "exact_material_pointers":4,"exact_rgba_pixels":count,"distinct_alpha_pixels_preserved":3,
        "unselected_name_size_controls_pass":2,"no_custom_GUID_or_fileID":True,
        "original_particle108_cause_proven":False,"original_recovery_proven":False,
        "engine_catalogue_target_verified":False,"original_assets_read":False,
        "unity_import_or_gpu_verified":False,"production_changed":False}
    dump(out/"report.json",report)
    print("GT_ACTUAL_TEXTURE_PRESERVATION "+json.dumps(report,sort_keys=True))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("prepare","stage","verify"))
    p.add_argument("--archive",type=Path);p.add_argument("--root",type=Path)
    p.add_argument("--out",type=Path);p.add_argument("--project",type=Path)
    a=p.parse_args()
    if a.mode=="prepare":prepare(a.archive,a.out)
    elif a.mode=="stage":stage(a.root)
    else:verify(a.out,a.project)
