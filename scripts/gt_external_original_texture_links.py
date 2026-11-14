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
    TEXTURE_TYPES, ENGINE, FONT_COLLECTION, _slot, _trace_source,
    _trace_export, exported_texenvs,
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
    traced_materials=set()
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
        if cls==21:
            if src in traced_materials:
                raise InventoryError("duplicate_original_material_source_trace")
            traced_materials.add(src)
            # A source-authentic FontAssetExportCollection Material is
            # embedded in its TrueType import, not in a .mat/.asset YAML
            # document with the traced Material pointer. B05 and W1
            # already prove the actual font payload/collection separately.
            # Never silently treat ordinary missing Materials as fonts.
            if row.get("collection_type")==FONT_COLLECTION:
                digest=row.get("font_data_sha256")
                if (not isinstance(digest,str) or len(digest)!=64 or
                    any(c not in "0123456789abcdefABCDEF" for c in digest) or
                    "font_source" not in row or "font_export" not in row):
                    raise InventoryError("invalid_original_font_material_trace")
                _trace_export({"export":row["font_export"]})
                continue
            # Unity internal engine Material references have a built-in
            # non-YAML destination. Do not fabricate a loose Material.
            if ptr[1] in ENGINE and ptr[2]==0 and row.get("exportable") is False:
                continue
            if ptr[0]>0 and ptr[2] in (2,3):
                mats[src]=ptr
            else:
                raise InventoryError("unsupported_original_material_export_pointer")
        else:
            if src in textures:
                raise InventoryError("duplicate_original_texture_trace")
            textures[src]=(cls,ptr)
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


def verify_native_array_slots(originals, external_tables, source_types, trace, exported):
    materials, textures = trace_targets(trace)
    matched = set()
    expected = set()
    array_pointers = {ptr for cls, ptr in textures.values() if cls == 187}
    for source, slots in originals.items():
        material_pointer = materials.get(source)
        if material_pointer is None:
            continue
        material_key = material_pointer[:2]
        for name, slot in slots.items():
            (file_id, path_id), original_uv = _slot(slot)
            if file_id == 0:
                owner = source[0]
            elif 0 < file_id <= len(external_tables[source[0]]):
                owner = exact_owner(external_tables[source[0]][file_id - 1])
            else:
                continue
            target = owner, path_id
            if source_types.get(target) != 187:
                continue
            mapped = textures.get(target)
            if mapped is None or mapped[0] != 187 or mapped[1][0] != 18700000 or mapped[1][2] != 2:
                raise InventoryError("native_array_source_trace_pointer_mismatch")
            actual_slot = exported.get(material_key, {}).get(name)
            if actual_slot is None or _slot(actual_slot) != (mapped[1], original_uv):
                raise InventoryError("native_array_source_material_slot_mismatch")
            expected.add((material_key, name))
            matched.add(mapped[1])
    observed = {
        (material_key, name)
        for material_key, slots in exported.items()
        for name, slot in slots.items()
        if _slot(slot)[0] in array_pointers
    }
    if expected != observed or matched != array_pointers or len(expected) != 28 or len(matched) != 9:
        raise InventoryError("native_array_source_material_slot_scope_mismatch")
    return len(expected)


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


ALLOWED_FAILURE_CODES=frozenset({
    "invalid_private_same_instance_texture_trace",
    "invalid_texture_trace_row",
    "duplicate_original_material_source_trace",
    "invalid_original_font_material_trace",
    "unsupported_original_material_export_pointer",
    "duplicate_original_texture_trace",
    "untrusted_material_source_owner",
    "missing_SHA_original_external_table",
    "original_exported_material_identity_missing",
    "invalid_original_owner_table_root",
    "source_serialized_external_table_missing",
    "invalid_source_external_table_size",
    "invalid_source_external_table_entry",
    "duplicate_source_texture_identity",
})


def safe_failure(error, phase):
    """No original source/path/GUIDs leak in Actions, even on real failures."""
    code=str(error)
    if code not in ALLOWED_FAILURE_CODES:
        code="unclassified_"+type(error).__name__
    return {
        "schema":"GT_REAL_ORIGINAL_EXTERNAL_TEXTURE_POINTERS_V1",
        "status":"INCONCLUSIVE",
        "failed_phase":phase,
        "reason_code":code,
        "source_or_exported_assets_modified":False,
        "private_original_names_guids_ids_disclosed":False,
        "Unity_Editor_or_Android_GPU_pixels_verified":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("source","manifest","project","trace","report"):
        p.add_argument("--"+key,required=True,type=Path)
    a=p.parse_args()
    if any(a.report.resolve().is_relative_to(x.resolve())
           for x in (a.source,a.project)):
        raise InventoryError("external_link_report_inside_original_game")
    phase="original_material_properties"
    try:
        inputs=original(a.source,a.manifest)
        phase="authenticated_external_owner_tables"
        tables,types=load_tables(a.source,a.manifest)
        phase="private_same_instance_export_join"
        output=compare(inputs,tables,types,json.loads(a.trace.read_text()),
                       exported_texenvs(a.project))
    except (InventoryError,ValueError,KeyError,TypeError,AttributeError,OSError) as err:
        output=safe_failure(err,phase)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print("GT_ALL_REAL_ORIGINAL_EXTERNAL_TEXTURE_LINKS "+json.dumps(output,sort_keys=True))
    return 0 if output["status"]=="EXTERNAL_TEXTURE_SOURCE_EXPORT_LINKS_CLASSIFIED" else 2


if __name__=="__main__":
    raise SystemExit(main())
