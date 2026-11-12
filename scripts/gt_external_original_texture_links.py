#!/usr/bin/env python3
"""GT verify original external Texture pointers using SHA-pinned ZIP2 owner tables.

Original Material m_FileID>0 is an index into that source owner's serialized
externals table, NOT a local texture. Join only exact original file/pathID/type
to the same AssetRipper exporter instance, and compare its Material TexEnv.
Never rewrite YAML/GUI data or emit source names, GUIDs, pixels or path IDs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gc
import json
from pathlib import Path

from scripts.b05_verify_material_texenv_bindings import (
    TEXTURE_TYPES, _slot, _trace_source, _trace_export, exported_texenvs,
)
from scripts.gt_full_original_export_texenvs import original
from scripts.gt_stage_serialized_owners import OWNERS, InventoryError, read_expected
from scripts.gt_serialized_graphics_counts import verify

TYPES={"Texture2D":28,"RenderTexture":84,"Cubemap":89,
       "Texture3D":117,"Texture2DArray":187}


def exact_owner(raw):
    if not isinstance(raw,str) or not raw or "\x00" in raw:
        return None
    value=raw.replace("\\","/")
    if any(seg in (".","..") for seg in value.split("/")):
        return None
    name=value.rsplit("/",1)[-1]
    return name if name in OWNERS else None


def trace_targets(trace):
    code=trace.get("export_instance") if isinstance(trace,dict) else None
    if (not isinstance(code,str) or len(code)!=32 or
        any(x not in "0123456789abcdefABCDEF" for x in code) or
        trace.get("schema_version")!=1 or
        not isinstance(trace.get("objects"),list) or
        len(trace["objects"])>250000):
        raise InventoryError("invalid_private_same_instance_texture_trace")
    mats={}
    textures={}
    for row in trace["objects"]:
        if not isinstance(row,dict):
            raise InventoryError("invalid_texture_trace_row")
        cls=row.get("class_id")
        if cls not in TEXTURE_TYPES | {21}:
            continue
        src=_trace_source(row)
        if src[0] not in OWNERS:
            continue
        ptr=_trace_export(row)
        dest=mats if cls==21 else textures
        if src in dest:
            raise InventoryError("duplicate_original_texture_or_material_trace")
        if cls==21:
            if ptr[0]>0 and ptr[2] in (2,3):
                dest[src]=ptr
        else:
            dest[src]=(cls,ptr)
    return mats,textures


def compare(originals,external_tables,source_types,trace,exported):
    mats,textures=trace_targets(trace)
    counts=Counter()
    for src,slots in originals.items():
        if src[0] not in OWNERS:
            raise InventoryError("untrusted_material_source_owner")
        if src[0] not in external_tables:
            raise InventoryError("missing_SHA_original_external_table")
        mat_ptr=mats.get(src)
        if mat_ptr is None:
            # Some serialized font/engine Materials are deliberately not
            # exported as ordinary YAML; never claim their slots verified.
            counts["source_material_without_normal_export"]+=1
            continue
        material=exported.get(mat_ptr[:2])
        if material is None:
            raise InventoryError("original_exported_material_identity_missing")
        for name,slot in slots.items():
            (file_id,path_id),_=_slot(slot)
            if file_id==0 or path_id==0: continue
            counts["external_source_slots"]+=1
            if name not in material:
                counts["wrong_or_missing_material_slots"]+=1
                continue
            actual,_=_slot(material[name])
            tables=external_tables[src[0]]
            if type(file_id) is not int or not 1<=file_id<=len(tables):
                counts["source_external_index_unresolved"]+=1
                continue
            owner=exact_owner(tables[file_id-1])
            if owner is None:
                counts["external_owner_unproven"]+=1
                continue
            target=(owner,path_id)
            cls=source_types.get(target)
            if cls is None:
                counts["external_target_texture_class_unproven"]+=1
                continue
            mapped=textures.get(target)
            if mapped is None:
                counts["external_texture_source_export_trace_missing"]+=1
                continue
            if cls!=mapped[0]:
                counts["wrong_original_external_texture_class"]+=1
                continue
            if actual!=mapped[1]:
                counts["wrong_same_export_external_texture_pointer"]+=1
                continue
            counts["exact_external_texture_pointer_matches"]+=1
    checked=counts["external_source_slots"]
    proven=counts["exact_external_texture_pointer_matches"]
    bad=sum(counts[k] for k in ("wrong_or_missing_material_slots",
         "wrong_original_external_texture_class",
         "wrong_same_export_external_texture_pointer"))
    return {
        "schema":"GT_REAL_ORIGINAL_EXTERNAL_TEXTURE_POINTERS_V1",
        "status":"EXTERNAL_TEXTURE_SOURCE_EXPORT_LINKS_CLASSIFIED" if bad==0
                 else "EXTERNAL_TEXTURE_SOURCE_EXPORT_LINKS_REJECTED",
        "authenticated_owner_tables":len(external_tables),
        "original_external_texture_slots":checked,
        "exact_cross_owner_source_export_texture_links":proven,
        "external_links_not_yet_proven":checked-proven,
        "mismatched_source_to_export_external_links":bad,
        "all_external_links_verified":checked>0 and checked==proven,
        "counts":dict(sorted(counts.items())),
        "private_original_names_guids_ids_disclosed":False,
        "source_or_exported_assets_modified":False,
        "Unity_Editor_or_Android_GPU_pixels_verified":False,
    }


def load_tables(source_root,manifest,loader=None):
    if source_root.is_symlink() or not source_root.is_dir():
        raise InventoryError("invalid_original_owner_table_root")
    if loader is None:
        import UnityPy
        loader=lambda path: UnityPy.load(str(path))
    expected=read_expected(manifest)
    tables,types={},{}
    for owner in sorted(OWNERS):
        _,size,digest=expected[owner]
        file=source_root/owner
        verify(file,size,digest)
        env=loader(file)
        serial=getattr(env,"file",None)
        if serial is None or not hasattr(serial,"externals"):
            raise InventoryError("source_serialized_external_table_missing")
        refs=serial.externals
        if not isinstance(refs,(list,tuple)) or len(refs)>4096:
            raise InventoryError("invalid_source_external_table_size")
        tables[owner]=[getattr(ref,"path",None) for ref in refs]
        if any(not isinstance(x,str) for x in tables[owner]):
            raise InventoryError("invalid_source_external_table_entry")
        for obj in env.objects:
            cls=TYPES.get(str(obj.type.name))
            if cls is not None:
                key=(owner,obj.path_id)
                if key in types:
                    raise InventoryError("duplicate_source_texture_identity")
                types[key]=cls
        del env
        gc.collect()
    return tables,types


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("source","manifest","project","trace","report"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    if any(a.report.resolve().is_relative_to(x.resolve())
           for x in (a.source,a.project)):
        raise InventoryError("external_link_report_inside_original_game")
    inputs=original(a.source,a.manifest)
    tables,types=load_tables(a.source,a.manifest)
    output=compare(inputs,tables,types,json.loads(a.trace.read_text()),
                   exported_texenvs(a.project))
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print("GT_ALL_REAL_ORIGINAL_EXTERNAL_TEXTURE_LINKS "+json.dumps(output,sort_keys=True))
    return 0 if output["status"]=="EXTERNAL_TEXTURE_SOURCE_EXPORT_LINKS_CLASSIFIED" else 2


if __name__=="__main__":
    raise SystemExit(main())
