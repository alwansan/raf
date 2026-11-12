#!/usr/bin/env python3
"""GT: classify nonstandard imported Texture PPtrs using the SAME AssetRipper instance.

Read-only. Cross-checks unusual image fileIDs with the exporter-generated source
Texture class (Texture2D/RenderTexture/Cubemap/Texture2DArray) and the actual TextureImporter
shape. Never logs original names, source pathIDs, GUIDs, or raw game bytes.
A matching pointer alone is not proof that Unity will import/play it on Android.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts.verify_exported_material_texture_links import (
    BUILTIN, GUID, IMAGES, ZERO, GuardError, material_docs, pointer, read, texenv,
)

# Unity ClassID (84=RenderTexture, 187=Texture2DArray); neither can
# automatically become a Texture2D image with fileID 2800000.
# This is a diagnostic, not permission to rewrite any Unity asset or GUID.
TRACE_CLASSES={28:"texture2d",84:"rendertexture",89:"cubemap",
               117:"texture3d",187:"texture2darray"}
FID_CLASSES={2800000:"texture2d",8900000:"cubemap"}
SHAPES={"1":"2d", "2":"cubemap", "4":"2darray", "8":"3d"}
TRACE_HEX=re.compile(r"[a-fA-F0-9]{32}\Z")
MAX_ITEMS=250_000


def analyze(project:Path,trace:Path)->dict:
    project,trace=project.absolute(),trace.absolute()
    if any(p.is_symlink() for p in (project,*project.parents,trace,*trace.parents)):
        raise GuardError("unsafe_real_export_source_or_trace")
    if (not trace.is_file() or trace.stat().st_size>32*1024*1024 or
        trace.is_relative_to(project)):
        raise GuardError("untrusted_same_instance_texture_trace")
    doc=json.loads(trace.read_text(encoding="utf-8"))
    if (doc.get("schema_version")!=1 or
        not isinstance(doc.get("export_instance"),str) or
        not TRACE_HEX.fullmatch(doc["export_instance"]) or
        not isinstance(doc.get("objects"),list)):
        raise GuardError("bad_original_exporter_trace_schema")
    mapped={}
    for row in doc["objects"]:
        cls=row.get("class_id")
        if cls not in TRACE_CLASSES:
            continue
        src=row.get("source")
        dst=row.get("export")
        if (not isinstance(src,dict) or
            set(src)!={"owner","path_id"} or
            not isinstance(src["owner"],str) or
            type(src["path_id"]) is not int or src["path_id"]<=0 or
            not isinstance(dst,dict) or
            set(dst)!={"file_id","guid","type"} or
            type(dst["file_id"]) is not int or
            type(dst["type"]) is not int or
            not isinstance(dst["guid"],str) or
            not TRACE_HEX.fullmatch(dst["guid"])):
            raise GuardError("malformed_original_texture_trace_row")
        key=(dst["file_id"],dst["guid"].lower(),dst["type"])
        # In rare shared exporter collections the same class and pointer may
        # appear twice. Never silently choose an arbitrary source class.
        if key in mapped and mapped[key]!=cls:
            mapped[key]=-1
        else:
            mapped[key]=cls

    root=project/"Assets"
    if not root.is_dir() or root.is_symlink():
        raise GuardError("missing_exported_assets")
    entries=list(root.rglob("*"))
    if len(entries)>MAX_ITEMS or any(p.is_symlink() for p in entries):
        raise GuardError("unsafe_or_excessive_export")
    files={p for p in entries if p.is_file()}
    targets={}
    for meta in files:
        if not meta.name.endswith(".meta"):
            continue
        ids=GUID.findall(read(meta))
        if len(ids)!=1:
            raise GuardError("ambiguous_exported_meta_identity")
        key=ids[0].lower()
        if key in targets or key==ZERO or key in BUILTIN:
            raise GuardError("duplicate_or_reserved_exported_meta_identity")
        target=meta.with_name(meta.name[:-5])
        if target not in files:
            raise GuardError("unmatched_meta_destination")
        targets[key]=(target,meta)

    counter=Counter()
    wrongs=set()
    for path in sorted(x for x in files if x.suffix.lower()==".mat"):
        docs,_=material_docs(read(path))
        for material in docs:
            for fid,guid,kind in texenv(material):
                if fid<=0 or not guid or guid in BUILTIN or guid==ZERO or guid not in targets:
                    continue
                target,meta=targets[guid]
                if target.suffix.lower() not in IMAGES or fid==2800000:
                    continue
                counter["nonstandard_image_file_id_refs"]+=1
                key=(fid,guid,kind)
                wrongs.add(key)
                cls=mapped.get(key)
                if cls is None:
                    counter["no_exact_source_export_texture_trace"]+=1
                elif cls==-1:
                    counter["conflicting_texture_class_export_trace"]+=1
                else:
                    counter["class_"+TRACE_CLASSES[cls]]+=1
                if fid==8900000:
                    counter["file_id_family_cubemap"]+=1
                elif fid==8400000:
                    counter["file_id_family_rendertexture"]+=1
                elif fid==18700000:
                    counter["file_id_family_texture2darray"]+=1
                else:
                    counter["file_id_family_other_nonstandard"]+=1
                data=read(meta)
                hits=re.findall(r"(?m)^[ \t]*textureShape:[ \t]*(\d+)[ \t]*$",data)
                shape=SHAPES.get(hits[0],"other") if len(hits)==1 else "unidentified"
                counter["importer_shape_"+shape]+=1
                if (cls==89 and fid==8900000 and shape=="cubemap" and
                    bool(re.search(r"(?m)^TextureImporter:[ \t]*$",data))):
                    counter["same_instance_cubemap_pointer_and_importer_shape_coherent"]+=1
                else:
                    # A RenderTexture cannot be assumed to be represented by a
                    # PNG TextureImporter even if both GUID and native class 84
                    # fileID match the source. Keep the contract fail-closed.
                    if cls==84:
                        counter["rendertexture_exported_as_imported_image"]+=1
                    counter["requires_unresolved_import_or_source_repair"]+=1
    return {
        "schema":"GT_REAL_EXPORTED_NONSTANDARD_TEXTURE_LINEAGE_V1",
        "source_exporter_same_instance_trace_checked":True,
        "distinct_nonstandard_image_pointers":len(wrongs),
        "counts":dict(sorted(counter.items())),
        "all_nonstandard_targets_proven_importable":False,
        "original_source_objects_or_meta_modified":False,
        "original_guids_names_pathids_disclosed":False,
        "android_device_gpu_verified":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--trace",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    if a.report.absolute().is_relative_to(a.project.absolute()):
        raise GuardError("report_inside_private_export")
    report=analyze(a.project,a.trace)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_NONSTANDARD_REAL_TEXTURE_POINTER_LINEAGE "+json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
