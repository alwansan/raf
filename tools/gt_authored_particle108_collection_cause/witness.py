#!/usr/bin/env python3
"""Bounded authored v22 inputs and independent same-export verification.

No Raft source, cache, engine payload or replacement texture is read. The
artificial metadata cache is not the real Unity engine catalogue.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import yaml
from PIL import Image
from tools.gt_authored_mesh_binary import witness as w
from tools.gt_authored_serialized_renderer_route import witness as local
from tools.gt_authored_external_pptr_route import witness as ext
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs

OWNER = "gt-collection-authored.assets"
NAMES = ("GT Authored Cache Collision", "GT Authored Cache Collision",
         "GT Authored Name Control", "GT Authored Cache Collision")
DIMS = ((2, 2), (2, 2), (2, 2), (2, 1))
RGBA = (local.TEXTURE, bytes(x if i % 4 != 3 else 255
                             for i, x in enumerate(local.TEXTURE)),
        local.TEXTURE, local.TEXTURE[:8])
IDS = {801: 48, **{811+i: 21 for i in range(4)}, **{821+i: 28 for i in range(4)}}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True)+"\n")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def prepare(out):
    out.mkdir(parents=True, exist_ok=False)
    (out/"source").mkdir()
    schemas, objects = local.fixture()
    schemas = {cls: schemas[cls] for cls in (21, 28, 48)}
    objs = {801: deepcopy(objects[801])}
    image = next(k for k in ("image data", "m_ImageData") if k in objects[821])
    for i in range(4):
        tex = deepcopy(objects[821])
        tex.update(m_Name=NAMES[i], m_Width=DIMS[i][0], m_Height=DIMS[i][1])
        tex[image] = list(RGBA[i])
        if "m_CompleteImageSize" in tex:
            tex["m_CompleteImageSize"] = len(RGBA[i])
        objs[821+i] = tex
        mat = deepcopy(objects[811])
        mat["m_Name"] = f"GT Collection Material {811+i}"
        mat["m_SavedProperties"]["m_TexEnvs"][0][1]["m_Texture"] = local.pptr(821+i)
        objs[811+i] = mat
    raw, rows = ext.serialize(schemas, IDS, objs, [])
    (out/"source"/OWNER).write_bytes(raw)
    env = w.UnityPy.load(raw)
    need(set(env.file.objects) == set(IDS), "actual object table")
    for i in range(4):
        tx = env.file.objects[821+i].read_typetree()
        need((tx["m_Width"], tx["m_Height"]) == DIMS[i] and tx["m_Name"] == NAMES[i]
             and bytes(tx[image]) == RGBA[i], "real source texture")
        mat = env.file.objects[811+i].read_typetree()
        need(normalize_texenvs(mat["m_SavedProperties"]["m_TexEnvs"])["_MainTex"][0] == (0, 821+i),
             "real material route")
    need(RGBA[0][0::4] == RGBA[1][0::4] and RGBA[0][1::4] == RGBA[1][1::4]
         and RGBA[0][2::4] == RGBA[1][2::4] and RGBA[0][3::4] != RGBA[1][3::4],
         "alpha-only authored collision")
    dump(out/"input.json", {"owner": w.commit(raw), "objects": rows,
         "source_RGBA_sha256": [sha(x) for x in RGBA],
         "alpha_different_pixels": sum(a != b for a,b in zip(RGBA[0][3::4], RGBA[1][3::4])),
         "authored_only": True})
    print("GT_COLLECTION_AUTHORED_SOURCE", len(raw), len(rows), flush=True)


def stage(root):
    path = root/"ar-host/Source/AssetRipper.Export.UnityProjects/ProjectExporter.cs"
    raw = path.read_bytes()
    blob = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    need(blob == "820a6123480ac7a98c40ac19e7e9d6f2568ddfa6", "pinned public exporter drift")
    anchor = b"ProjectAssetContainer container = new ProjectAssetContainer(this, options, fileCollection.FetchAssets(), collections);"
    need(raw.count(anchor) == 1, "capture anchor")
    path.write_bytes(raw.replace(anchor, anchor+b"\n\t\tRaftGTCollectionWitness.Capture(container, collections);"))
    path.with_name("RaftGTCollectionWitness.cs").write_bytes(
        (root/"tools/gt_authored_particle108_collection_cause/RaftGTCollectionWitness.cs").read_bytes())
    (root/"android-port/Experiments/ExportLineage/Program.cs").write_text(
        "AssetRipper.Export.UnityProjects.RaftGTCollectionWitness.Run(args);\n")


class UniqueLoader(yaml.BaseLoader):
    pass


def mapping(loader, node, deep=False):
    result = {}
    for key, value in node.value:
        k = loader.construct_object(key, deep=deep)
        need(k not in result, "duplicate yaml key")
        result[k] = loader.construct_object(value, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def read_yaml(path):
    raw = path.read_text(encoding="utf-8-sig")
    clean = re.sub(r"^%[^\n]*\n", "", raw, flags=re.M)
    clean = re.sub(r"^--- !u!\d+ &-?\d+[^\n]*$", "---", clean, flags=re.M)
    return yaml.load(clean, Loader=UniqueLoader)


def verify(out, project):
    receipt = json.loads((out/"capture.json").read_text())
    typed = json.loads((out/"typed.json").read_text())
    need(len(typed) == 4 and [r["sha256"] for r in typed] == [sha(x) for x in RGBA]
         and all(r["integrity"] and r["serialized"] for r in typed), "typed source bytes")
    byid = {r["path_id"]: r for r in receipt}
    need(len(receipt) == len(byid) == 4 and set(byid) == {821,822,823,824}, "capture census")
    a,b,c,d = (byid[i] for i in (821,822,823,824))
    need(not a["exportable"] and not b["exportable"] and c["exportable"] and d["exportable"],
         "collection selection")
    need(a["collection"] == b["collection"] == "RedirectExportCollection"
         and a["pointer"] == b["pointer"] and a["pointer"]["type"] == 0
         and a["pointer"]["fileID"] == 12345678, "same internal redirect")
    need(c["pointer"] != d["pointer"] and c["pointer"] != a["pointer"] and d["pointer"] != a["pointer"],
         "distinct control pointers")
    assets = project/"Assets"
    need(assets.is_dir(), "actual export project")
    mats = {}
    for f in assets.rglob("*.mat"):
        mat = read_yaml(f)["Material"]
        name = mat["m_Name"]
        if not name.startswith("GT Collection Material "):
            continue
        pid = int(name.rsplit(" ", 1)[1])
        need(pid not in mats, "duplicate material")
        slots = mat["m_SavedProperties"]["m_TexEnvs"]
        need(len(slots) == 1 and set(slots[0]) == {"_MainTex"}, "material route")
        ptr = slots[0]["_MainTex"]["m_Texture"]
        ptr = {"fileID": int(ptr["fileID"]), "guid": str(ptr["guid"]), "type": int(ptr["type"])}
        need(ptr == byid[pid+10]["pointer"], "actual exported material pointer")
        mats[pid] = ptr
    need(set(mats) == {811,812,813,814}, "material output census")
    pngs = {}
    for f in assets.rglob("*.png"):
        meta = read_yaml(f.with_name(f.name+".meta"))
        guid = str(meta["guid"])
        need(guid not in pngs, "duplicate image guid")
        with Image.open(f) as image:
            im = image.convert("RGBA")
            pngs[guid] = (im.size, im.tobytes())
    need(set(pngs) == {c["pointer"]["guid"], d["pointer"]["guid"]}, "only two image payloads")
    for i, row in ((2,c),(3,d)):
        expected = Image.frombytes("RGBA", DIMS[i], RGBA[i]).transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes()
        need(pngs[row["pointer"]["guid"]] == (DIMS[i],expected), "control pixel parity")
    report = {"status":"PASS_AUTHORED_CACHE_KEY_COLLISION_SAME_EXPORT",
        "source_textures":4, "source_materials":4, "source_nonempty_payloads":4,
        "different_alpha_pixels":sum(x!=y for x,y in zip(RGBA[0][3::4],RGBA[1][3::4])),
        "nonexportable_redirects":2, "same_pointer_despite_distinct_RGBA":True,
        "exact_material_pointer_matches":4, "actual_png_payloads":2,
        "control_pixels_exact":sum(x*y for x,y in DIMS[2:]),
        "controls":["different_name","different_dimensions"], "authored_metadata_cache_only":True,
        "real_engine_catalogue_checked":False, "original_particle108_cause_proven":False,
        "original_recovery_proven":False, "production_changed":False}
    dump(out/"report.json", report)
    print("GT_COLLECTION_CAUSE_PASS", json.dumps(report,sort_keys=True), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("prepare","stage","verify"))
    p.add_argument("--out",type=Path)
    p.add_argument("--root",type=Path)
    p.add_argument("--project",type=Path)
    a=p.parse_args()
    if a.mode=="prepare":prepare(a.out)
    elif a.mode=="stage":stage(a.root)
    else:verify(a.out,a.project)
