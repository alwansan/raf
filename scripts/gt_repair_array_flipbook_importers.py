#!/usr/bin/env python3
"""GT bounded same-instance source→Unity Texture2DArray flipbook importer repair.

Only when an actual exported PNG *already contains every original 1024px
array slice* is it safe to correct flipbookRows / flipbookColumns. The exact
original ClassID187, fileID18700000, GUID, immutable ZIP2 dimensions and PNG
IHDR must all agree. No pixels are changed, no empty source layers invented,
and no trace GUIDs/names are disclosed in aggregate output. This edits only a
disposable AssetRipper ExportedProject; never tracked Raft source or T5's
production project without explicit integration.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_validate_texture2darray_flipbook import (
    audit, index_exported_array_meta, png_dimensions,
)
from scripts.gt_verify_original_array_export import source_arrays
from scripts.gt_test_vendor_shader_restoration import original_meta_digests
from scripts.verify_exported_material_texture_links import GUID, read

ROW = re.compile(r"(?m)^([ \t]+)flipbookRows:[ \t]*(\d+)[ \t]*$")
COL = re.compile(r"(?m)^([ \t]+)flipbookColumns:[ \t]*(\d+)[ \t]*$")
SHAPE = re.compile(r"(?m)^[ \t]+textureShape:[ \t]*4[ \t]*$")
MAX_FIXES=9


def exact_targets(original:dict,trace:dict,output:dict):
    if (len(original)!=9 or not isinstance(trace,dict)
        or trace.get("schema_version")!=1
        or not re.fullmatch(r"[a-fA-F0-9]{32}",str(trace.get("export_instance","")))
        or not isinstance(trace.get("objects"),list)):
        raise InventoryError("untrusted_original_array_source_export_trace")
    found={}
    for row in trace["objects"]:
        if row.get("class_id")!=187: continue
        source=row.get("source")
        exported=row.get("export")
        if not isinstance(source,dict) or not isinstance(exported,dict):
            raise InventoryError("invalid_source_array_identity_trace")
        owner=Path(str(source.get("owner","")).replace("\\","/")).name
        key=owner,source.get("path_id")
        if key not in original: continue
        if (key in found or set(exported)!={"guid","file_id","type"}
            or exported.get("file_id")!=18700000
            or exported.get("type") not in (2,3)
            or not re.fullmatch(r"[a-fA-F0-9]{32}",str(exported.get("guid","")))):
            raise InventoryError("duplicate_or_wrong_original_array_export_pointer")
        guid=exported["guid"].lower()
        if guid not in output:
            raise InventoryError("original_array_GUID_missing_from_export")
        file,meta=output[guid]
        if file.suffix.lower()!=".png":
            raise InventoryError("original_array_not_exported_as_png")
        found[key]=(file,meta,guid)
    if set(found)!=set(original):
        raise InventoryError("not_all_nine_original_array_targets_found")
    if len({row[2] for row in found.values()})!=9:
        raise InventoryError("original_array_export_GUID_collision")
    return found


def corrected_importer(meta:Path, original_guid:str, rows:int,columns:int):
    raw=read(meta)
    values=GUID.findall(raw)
    if len(values)!=1 or values[0].lower()!=original_guid:
        raise InventoryError("importer_original_GUID_not_preserved")
    if len(SHAPE.findall(raw))!=1 or len(ROW.findall(raw))!=1 or len(COL.findall(raw))!=1:
        raise InventoryError("importer_missing_exact_array_shape_or_grid_fields")
    if rows<=0 or columns<=0 or rows*columns>2048:
        raise InventoryError("invalid_source_proven_array_grid")
    before_rows=int(ROW.search(raw)[2])
    before_cols=int(COL.search(raw)[2])
    updated=ROW.sub(lambda m:m[1]+"flipbookRows: "+str(rows),raw)
    updated=COL.sub(lambda m:m[1]+"flipbookColumns: "+str(columns),updated)
    if len(GUID.findall(updated))!=1 or GUID.findall(updated)[0].lower()!=original_guid:
        raise InventoryError("array_grid_rewrite_changed_GUID")
    return (updated.encode("utf-8"),before_rows,before_cols)


def plan(original:dict,trace:dict,exported:dict):
    targets=exact_targets(original,trace,exported)
    counts=Counter()
    action=[]
    for key,(file,meta,guid) in targets.items():
        entry=original[key]
        sx,sy=entry["width"],entry["height"]
        if (type(sx) is not int or type(sy) is not int
            or sx<=0 or sy<=0 or type(entry["depth"]) is not int
            or entry["depth"]<=0):
            raise InventoryError("untrusted_original_array_dimensions")
        ix,iy=png_dimensions(file)
        if ix%sx or iy%sy:
            counts["export_png_not_source_aligned"]+=1
            continue
        columns,rows=ix//sx,iy//sy
        if rows*columns!=entry["depth"]:
            counts["export_png_lacks_full_original_array_slices"]+=1
            continue
        # A forged IHDR can advertise all source layers while having no
        # real PNG pixels. Verify the complete compressed image and force
        # decoding before considering any existing Unity importer mutation.
        from PIL import Image
        try:
            with Image.open(file) as img:
                if img.format!="PNG" or img.size!=(ix,iy):
                    raise InventoryError("invalid_original_array_PNG_container")
                img.load()
        except (OSError,ValueError) as exc:
            raise InventoryError("unreadable_original_array_exported_PNG_pixels") from exc
        counts["export_png_contains_complete_original_array_slices"]+=1
        changed,oldrows,oldcols=corrected_importer(meta,guid,rows,columns)
        if oldrows==rows and oldcols==columns:
            counts["source_importer_grid_already_correct"]+=1
            continue
        counts["safe_meta_only_grid_repair_candidate"]+=1
        action.append((meta,changed,guid))
    if len(action)>MAX_FIXES: raise InventoryError("source_array_repair_scope_overflow")
    return action,counts


def execute(project:Path,backup:Path,original:dict,trace:dict):
    project,backup=project.absolute(),backup.absolute()
    if (not (project/"Assets").is_dir()
        or backup.exists() or backup.is_relative_to(project)
        or project.is_relative_to(backup)
        or any(p.is_symlink() for p in (project,*project.parents,backup,*backup.parents))):
        raise InventoryError("unsafe_disposable_Unity_array_repair_project_or_backup")
    output=index_exported_array_meta(project)
    actions,counts=plan(original,trace,output)
    before=original_meta_digests(project/"Assets")
    modified={}
    if actions:
        backup.mkdir(parents=True)
        try:
            for meta,updated,guid in actions:
                rel=meta.relative_to(project)
                dest=backup/rel
                dest.parent.mkdir(parents=True,exist_ok=True)
                if meta.is_symlink() or dest.exists():
                    raise InventoryError("untrusted_original_array_meta_backup")
                shutil.copy2(meta,dest)
                if hashlib.sha256(dest.read_bytes()).hexdigest()!=before[rel.relative_to("Assets").as_posix()]:
                    raise InventoryError("original_array_meta_backup_SHA_mismatch")
            for meta,updated,guid in actions:
                rel=meta.relative_to(project)
                original_file=backup/rel
                if original_file.stat().st_size>4*1024*1024:
                    raise InventoryError("oversized_original_array_importer_meta")
                fd,name=tempfile.mkstemp(prefix=".gt-array-import-",dir=meta.parent)
                temp=Path(name)
                try:
                    with os.fdopen(fd,"wb") as stream: stream.write(updated)
                    os.replace(temp,meta)
                finally:
                    temp.unlink(missing_ok=True)
                updated_text=read(meta)
                matches=GUID.findall(updated_text)
                if len(matches)!=1 or matches[0].lower()!=guid:
                    raise InventoryError("postrepair_original_array_GUID_mismatch")
                modified[rel.relative_to("Assets").as_posix()]=True
            after=original_meta_digests(project/"Assets")
            difference={p for p in before if before[p]!=after.get(p)}
            if (set(before)!=set(after) or difference!=set(modified)
                or not all((backup/"Assets"/name).is_file() for name in modified)):
                raise InventoryError("modified_nonarray_original_exported_meta")
        except BaseException:
            for meta,_,_ in actions:
                source=backup/meta.relative_to(project)
                if source.is_file():
                    shutil.copy2(source,meta)
            shutil.rmtree(backup)
            raise
    # Confirm the complete original source→actual importer contract again.
    final=audit(original,trace,index_exported_array_meta(project))
    return {
        "schema":"GT_SOURCE_AUTHENTIC_ARRAY_FLIPBOOK_META_ONLY_REPAIR_V1",
        "status":("ALL_NINE_ARRAY_IMPORTERS_VALID" if
                  final["all_array_sources_importer_grid_and_png_geometry_match"]
                  else "SOURCE_VALIDATED_BOUNDED_PARTIAL_REPAIR" if modified
                  else "NO_SAFE_META_ONLY_REPAIR_POSSIBLE"),
        "original_array_objects_source_SHA256_authenticated":len(original),
        "original_array_material_target_class187":187,
        "original_importer_repair_candidates_applied":len(modified),
        "original_exported_asset_guids_preserved":True,
        "source_images_or_binaries_edited":False,
        "meta_files_outside_the_exactly_verified_array_set_changed":0,
        "original_meta_backups_kept_private":bool(modified),
        "counts":dict(sorted(counts.items())),
        "postrepair_exact_original_layer_grids_validated":
            final["counts"].get("exact_array_class_GUID_flipbook_geometry_verified",0),
        "all_nine_original_array_importers_accepted":
            final["all_array_sources_importer_grid_and_png_geometry_match"],
        "Unity_Editor_actual_import_execution_verified":False,
        "Android_GPU_pixel_equivalence_verified":False,
        "git_lfs_used":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--original-source",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--trace",type=Path,required=True)
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--backup",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    if (args.report.absolute().is_relative_to(args.project.absolute())
        or args.report.absolute().is_relative_to(args.original_source.absolute())
        or args.report.absolute().is_relative_to(args.backup.absolute())):
        raise InventoryError("unsafe_private_array_repair_report_location")
    result=execute(args.project,args.backup,
                   source_arrays(args.original_source,args.manifest),
                   json.loads(args.trace.read_text()))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_SOURCE_PROVEN_REAL_ARRAY_IMPORTER_META_ONLY_REPAIR "+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
