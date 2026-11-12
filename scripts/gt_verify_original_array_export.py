#!/usr/bin/env python3
"""GT verify original Texture2DArray identity and metadata against ONE real exporter.

Strict original ZIP2 SHA256/size pins; exact source (owner,pathID,ClassID=187)
joins to same-instance ExportedProject GUID, actual importer type and fileID.
The source 2D array pixel layers are NOT reconstructed or Android tested.
The report contains only counts and bounded numeric enum values.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts.gt_stage_serialized_owners import OWNERS, InventoryError, read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.verify_exported_material_texture_links import BUILTIN, GUID, IMAGES, ZERO, read

COUNT_EXPECTED = 9
MAX_ENTRIES = 250_000
NUMERIC_CODES = {str(i) for i in range(32)}


def source_arrays(source_root: Path, manifest: Path, loader=None) -> dict:
    if source_root.is_symlink() or not source_root.is_dir():
        raise InventoryError("invalid_authenticated_original_root")
    if loader is None:
        import UnityPy
        loader=lambda p: UnityPy.load(str(p))
    records=read_expected(manifest)
    found={}
    for owner in sorted(OWNERS):
        _,size,digest=records[owner]
        file=source_root/owner
        verify(file,size,digest)
        env=loader(file)
        objects=getattr(env,"objects",None)
        if objects is None:
            raise InventoryError("missing_array_source_objects")
        for obj in objects:
            if str(obj.type.name)!="Texture2DArray":
                continue
            key=(owner,obj.path_id)
            if type(obj.path_id) is not int or obj.path_id<=0 or key in found:
                raise InventoryError("duplicate_original_Texture2DArray_identity")
            try:
                data=obj.read_typetree(check_read=False)
            except (ValueError, TypeError, AttributeError) as error:
                raise InventoryError("undecodable_original_Texture2DArray") from error
            if not isinstance(data,dict):
                raise InventoryError("malformed_original_Texture2DArray")
            # Only record whether the original actually has dimensions/depth
            # and stream metadata; never extract or publish its pixels.
            width=data.get("m_Width")
            height=data.get("m_Height")
            depth=data.get("m_Depth")
            if any(type(v) is not int or v<=0 for v in (width,height,depth)):
                raise InventoryError("original_Texture2DArray_dimension_missing")
            found[key]={
                "width":width,
                "height":height,
                "depth":depth,
                "has_stream_record":isinstance(data.get("m_StreamData"),dict),
                "has_image_data":"m_ImageData" in data,
            }
        del env
    if len(found)!=COUNT_EXPECTED:
        raise InventoryError("original_Texture2DArray_count_changed")
    return found


def exported_meta(project:Path) -> dict:
    assets=project/"Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise InventoryError("missing_actual_exported_assets")
    entries=list(assets.rglob("*"))
    if len(entries)>MAX_ENTRIES or any(x.is_symlink() for x in entries):
        raise InventoryError("unsafe_or_excessive_exported_files")
    files={p for p in entries if p.is_file()}
    result={}
    for meta in files:
        if not meta.name.endswith(".meta"):
            continue
        guids=GUID.findall(read(meta))
        if len(guids)!=1:
            raise InventoryError("invalid_original_exported_meta_identity")
        guid=guids[0].lower()
        if guid in result or guid==ZERO or guid in BUILTIN:
            raise InventoryError("duplicate_or_reserved_exported_guid")
        asset=meta.with_name(meta.name[:-5])
        if asset not in files:
            raise InventoryError("orphan_exported_meta")
        body=read(meta)
        codes=re.findall(r"(?m)^[ \t]*textureShape:[ \t]*(\d+)[ \t]*$",body)
        shape=codes[0] if len(codes)==1 and codes[0] in NUMERIC_CODES else "unrecognized"
        result[guid]={
            "extension":asset.suffix.lower(),
            "image":asset.suffix.lower() in IMAGES,
            "TextureImporter":bool(re.search(r"(?m)^TextureImporter:[ \t]*$",body)),
            "textureShape_enum":shape,
        }
    return result


def match(source:dict, trace:dict, destinations:dict, *, expected=COUNT_EXPECTED) ->dict:
    if not isinstance(trace,dict) or trace.get("schema_version")!=1 or not isinstance(trace.get("objects"),list) or not re.fullmatch(r"[a-fA-F0-9]{32}",trace.get("export_instance","")):
        raise InventoryError("missing_same_instance_export_trace")
    if len(source)!=expected:
        raise InventoryError("unexpected_authenticated_array_count")
    seen={}
    for row in trace["objects"]:
        if row.get("class_id")!=187:
            continue
        src=row.get("source")
        ptr=row.get("export")
        if not isinstance(src,dict) or not isinstance(ptr,dict) or set(src)!={"owner","path_id"} or set(ptr)!={"file_id","guid","type"}:
            raise InventoryError("invalid_array_exporter_trace_row")
        owner=Path(src["owner"].replace("\\","/")).name if isinstance(src["owner"],str) else ""
        if owner not in OWNERS:
            continue
        key=(owner,src["path_id"])
        if key not in source or key in seen:
            raise InventoryError("array_trace_missing_from_authenticated_source_or_duplicate")
        if (type(ptr["file_id"]) is not int or ptr["file_id"]<=0 or
            type(ptr["type"]) is not int or ptr["type"] not in (2,3) or
            not isinstance(ptr["guid"],str) or
            not re.fullmatch(r"[a-fA-F0-9]{32}",ptr["guid"])):
            raise InventoryError("array_export_target_invalid")
        seen[key]=ptr
    if set(seen)!=set(source):
        raise InventoryError("array_objects_missing_from_same_instance_export")
    cnt=Counter()
    unique_output=set()
    for key,ptr in seen.items():
        dst=ptr["guid"].lower()
        if dst not in destinations:
            raise InventoryError("array_export_GUID_not_in_actual_meta")
        guid_fid=(dst,ptr["file_id"],ptr["type"])
        if guid_fid in unique_output:
            raise InventoryError("distinct_original_arrays_collapsed_to_one_export_pointer")
        unique_output.add(guid_fid)
        meta=destinations[dst]
        cnt["exported_array_refs"]+=1
        cnt["exported_as_image"]+=int(meta["image"])
        cnt["exported_as_native_asset"]+=int(not meta["image"])
        cnt["with_TextureImporter"]+=int(meta["TextureImporter"])
        cnt["array_importer_shape_"+meta["textureShape_enum"]]+=1
        fid=ptr["file_id"]
        cnt["array_export_fileID_"+str(fid) if fid in (18700000,2800000,8900000) else "array_export_fileID_other"]+=1
        cnt["source_layers_total"]+=source[key]["depth"]
        cnt["source_stream_descriptors"]+=int(source[key]["has_stream_record"])
        cnt["source_inline_data_fields"]+=int(source[key]["has_image_data"])
    return {
        "schema":"GT_AUTHENTIC_SOURCE_TEXTURE2DARRAY_REAL_EXPORT_PROOF_V1",
        "original_Texture2DArray_class187_SHA256_verified":len(source),
        "array_real_export_source_GUIDs_exact_join":len(seen),
        "counts":dict(sorted(cnt.items())),
        "all_arrays_exported_as_valid_Unity_Texture2DArray_assets_verified":False,
        "original_texture_array_layers_or_pixels_restored_for_Android":False,
        "original_guids_names_pathids_disclosed":False,
        "original_or_exported_assets_modified":False,
        "git_lfs_used":False,
    }


def main() ->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--trace",type=Path,required=True)
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    a=ap.parse_args()
    report=a.report.absolute()
    if report.is_relative_to(a.source.absolute()) or report.is_relative_to(a.project.absolute()):
        raise InventoryError("report_in_private_original_source_or_export")
    arrays=source_arrays(a.source,a.manifest)
    trace=json.loads(a.trace.read_text(encoding="utf-8"))
    result=match(arrays,trace,exported_meta(a.project))
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_SOURCE_ORIGINAL_ARRAY_EXPORT "+json.dumps(result,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
