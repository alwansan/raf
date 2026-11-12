#!/usr/bin/env python3
"""GT source-authentic original nine Texture2DArray Material pointer gate.

Correlates the original ZIP2 class187 owners through exactly ONE AssetRipper
export trace to the nine imported arrays and every exported Material's
m_TexEnvs pointer. Requires genuine full PNG cells and repaired Unity
TextureImporter grids; never silently rewrites refs to Texture2D 2800000.
Not a Unity Editor/Android GPU import test. Aggregate only, no game IDs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.gt_repair_array_flipbook_importers import exact_targets
from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_validate_texture2darray_flipbook import (
    audit as audit_arrays,index_exported_array_meta,
)
from scripts.gt_verify_original_array_export import source_arrays
from scripts.verify_exported_material_texture_links import (
    material_docs,texenv,read,
)


def check(project:Path,original:dict,trace:dict)->dict:
    if any(p.is_symlink() for p in (project,*project.parents)):
        raise InventoryError("unsafe_export_project_for_array_material_refs")
    metas=index_exported_array_meta(project)
    source=exact_targets(original,trace,metas)
    geometry=audit_arrays(original,trace,metas)
    target_guids={entry[2] for entry in source.values()}
    counter=Counter()
    used=set()
    for file in (project/"Assets").rglob("*.mat"):
        if file.is_symlink() or not file.is_file():
            raise InventoryError("unsafe_exported_material_link_input")
        docs,_=material_docs(read(file))
        for doc in docs:
            for fid,guid,kind in texenv(doc):
                if guid not in target_guids:
                    continue
                counter["array_material_ref_slots_seen"]+=1
                if fid!=18700000 or kind not in (2,3):
                    counter["wrong_original_class187_importer_pointer"]+=1
                else:
                    counter["exact_original_class187_material_refs"]+=1
                    used.add(guid)
    all_correct=(
        geometry["all_array_sources_importer_grid_and_png_geometry_match"]
        and counter["array_material_ref_slots_seen"]==28
        and counter["wrong_original_class187_importer_pointer"]==0
        and len(used)==9)
    return {
        "schema":"GT_EXACT_ORIGINAL_NINE_ARRAY_TO_MATERIAL_POINTERS_V1",
        "status":"ALL_28_ORIGINAL_ARRAY_MATERIAL_REFS_MATCH_REPAIRED_IMPORTERS"
                  if all_correct else "SOURCE_ARRAY_MATERIAL_IMPORT_NOT_FULLY_VERIFIED",
        "original_array_objects_SHA256_authenticated":len(original),
        "source_original_classID":187,
        "exported_array_fileID":18700000,
        "original_array_export_importer_guids_preserved":True,
        "total_original_array_derived_material_refs":counter["array_material_ref_slots_seen"],
        "exact_original_class187_array_material_refs":counter["exact_original_class187_material_refs"],
        "distinct_source_array_guids_referenced_by_materials":len(used),
        "array_png_importer_source_grid_fidelity_passed":
            geometry["all_array_sources_importer_grid_and_png_geometry_match"],
        "counts":dict(sorted(counter.items())),
        "full_array_material_importer_links_verified":all_correct,
        "Unity_Editor_texture_array_imported_asset_class_verified":False,
        "source_BC3_pixel_and_mip_parity_verified":False,
        "Android_runtime_pixels_verified":False,
        "original_source_game_assets_changed":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-source",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--trace",type=Path,required=True)
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    if (a.report.absolute().is_relative_to(a.project.absolute()) or
        a.report.absolute().is_relative_to(a.original_source.absolute())):
        raise InventoryError("array_material_refs_report_overlaps_source")
    r=check(a.project,source_arrays(a.original_source,a.manifest),
        json.loads(a.trace.read_text()))
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("GT_ORIGINAL_CLASS187_ARRAY_MATERIAL_LINKS "+json.dumps(r,sort_keys=True))
    return 0 if r["full_array_material_importer_links_verified"] else 2


if __name__=="__main__":
    raise SystemExit(main())
