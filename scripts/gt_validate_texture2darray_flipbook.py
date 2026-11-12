#!/usr/bin/env python3
"""GT validate *real* nine imported Texture2DArray flipbook assets and image geometry.

Unlike a plain Texture2D importer, Unity 2021 TextureImporterShape=4 imports
Texture2DArray cells from a flipbook grid. This requires fileID 18700000,
textureShape 4, positive flipbookColumns/Rows, and PNG width/height of one
original 1024px layer multiplied by those counts. Matches immutable ZIP2
original class187 objects via SAME AssetRipper instance trace, never by name.
Read-only and aggregation-only; no shader/GPU or pixel parity claim.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import struct

from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_verify_original_array_export import source_arrays
from scripts.verify_exported_material_texture_links import GUID,BUILTIN,ZERO,read

MAX_IMAGE_SIZE=1024*1024*1024
MAX_IMAGE_AXIS=16384


def png_dimensions(file: Path):
    if file.is_symlink() or not file.is_file() or file.stat().st_size>MAX_IMAGE_SIZE:
        raise InventoryError("invalid_exported_array_image")
    with file.open("rb") as source:
        head=source.read(24)
    if (len(head)!=24 or not head.startswith(b"\x89PNG\r\n\x1a\n") or
        head[12:16]!=b"IHDR" or int.from_bytes(head[8:12],"big")!=13):
        raise InventoryError("invalid_exported_array_PNG_IHDR")
    width,height=struct.unpack(">II",head[16:24])
    if not 0<width<=MAX_IMAGE_AXIS or not 0<height<=MAX_IMAGE_AXIS:
        raise InventoryError("unsupported_exported_array_PNG_dimensions")
    return width,height


def index_exported_array_meta(project:Path):
    assets=project/"Assets"
    if assets.is_symlink() or not assets.is_dir():
        raise InventoryError("missing_exported_assets")
    entries=list(assets.rglob("*"))
    if len(entries)>250000 or any(x.is_symlink() for x in entries):
        raise InventoryError("unsafe_excessive_exported_assets")
    files={p for p in entries if p.is_file()}
    metas={}
    for meta in files:
        if not meta.name.endswith(".meta"):continue
        match=GUID.findall(read(meta))
        if len(match)!=1 or match[0].lower() in (ZERO,*BUILTIN):
            raise InventoryError("invalid_exported_asset_GUID")
        guid=match[0].lower()
        if guid in metas:
            raise InventoryError("duplicate_exported_meta_GUID")
        target=meta.with_name(meta.name[:-5])
        if target not in files:
            raise InventoryError("orphan_exported_asset_meta")
        metas[guid]=(target,meta)
    return metas


def audit(original:dict,trace:dict,exported:dict)->dict:
    if (len(original)!=9 or trace.get("schema_version")!=1 or
        not re.fullmatch("[0-9a-fA-F]{32}",trace.get("export_instance","")) or
        not isinstance(trace.get("objects"),list)):
        raise InventoryError("original_array_or_export_instance_invalid")
    matches={}
    for obj in trace["objects"]:
        if obj.get("class_id")!=187:continue
        src=obj.get("source",{})
        ptr=obj.get("export",{})
        if not isinstance(src,dict) or not isinstance(ptr,dict):
            raise InventoryError("malformed_texture_array_export_row")
        owner=Path(str(src.get("owner","")).replace("\\","/")).name
        key=(owner,src.get("path_id"))
        if key not in original:continue
        if key in matches or set(ptr)!={"guid","file_id","type"}:
            raise InventoryError("duplicate_or_malformed_original_array_export")
        if (ptr.get("file_id")!=18700000 or ptr.get("type") not in (2,3) or
            not re.fullmatch("[a-fA-F0-9]{32}",str(ptr.get("guid","")))):
            raise InventoryError("invalid_original_class187_export_pointer")
        matches[key]=ptr
    if set(matches)!=set(original):
        raise InventoryError("missing_nine_source_arrays_from_same_export")
    counts=Counter()
    for key,ptr in matches.items():
        guid=ptr["guid"].lower()
        if guid not in exported:raise InventoryError("original_array_exported_meta_missing")
        target,meta=exported[guid]
        if target.suffix.lower()!=".png":
            counts["non_png_array_sources"]+=1
            continue
        source=read(meta)
        if not re.search(r"(?m)^TextureImporter:[ \t]*$",source):
            counts["missing_texture_importer"]+=1
            continue
        fields={}
        for name in ("textureShape","flipbookRows","flipbookColumns"):
            values=re.findall(r"(?m)^\s*"+name+r":\s*(\d+)\s*$",source)
            fields[name]=int(values[0]) if len(values)==1 else -1
        if fields["textureShape"]!=4:
            counts["wrong_importer_texture_shape"]+=1
            continue
        rows,cols=fields["flipbookRows"],fields["flipbookColumns"]
        if rows<=0 or cols<=0 or rows*cols!=original[key]["depth"]:
            counts["invalid_original_array_flipbook_grid"]+=1
            continue
        width,height=png_dimensions(target)
        if (width!=cols*original[key]["width"] or
            height!=rows*original[key]["height"]):
            counts["incorrect_original_array_image_dimensions"]+=1
            continue
        counts["exact_array_class_GUID_flipbook_geometry_verified"]+=1
        counts["source_logical_layers_imported_as_flipbook"]+=rows*cols
        counts["original_source_empty_pixel_array_flipbook_geometry"]+=(
            int(original[key]["original_stream_size"]==0))
    passed=counts["exact_array_class_GUID_flipbook_geometry_verified"]==9
    return {
        "schema":"GT_ORIGINAL_TO_REAL_ARRAY_FLIPBOOK_GEOMETRY_V1",
        "status":"NINE_SOURCE_ARRAY_FLIPBOOK_GEOMETRY_MATCH" if passed else "INCOMPLETE_OR_INVALID_SOURCE_ARRAY_FLIPBOOK",
        "authentic_original_array_objects":len(original),
        "same_instance_exported_class187_guid_objects":len(matches),
        "counts":dict(sorted(counts.items())),
        "all_array_sources_importer_grid_and_png_geometry_match":passed,
        "Unity_Editor_reimport_as_Texture2DArray_verified":False,
        "original_array_layer_pixel_values_verified":False,
        "original_asset_or_GUID_modified":False,
        "Android_device_pixels_verified":False
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--trace",type=Path,required=True)
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    if args.report.absolute().is_relative_to(args.project.absolute()):
        raise InventoryError("unsafe_array_report_inside_Unity_export")
    result=audit(source_arrays(args.source,args.manifest),
                 json.loads(args.trace.read_text()),index_exported_array_meta(args.project))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("GT_REAL_ARRAY_FLIPBOOK_GEOMETRY "+json.dumps(result,sort_keys=True))
    return 0 if result["all_array_sources_importer_grid_and_png_geometry_match"] else 2


if __name__=="__main__":
    raise SystemExit(main())
