#!/usr/bin/env python3
"""GT fail-closed source-only acceptance: original 9 arrays, 416 external Texture refs, 50 BC3 top mips.

Inputs are PRIVATE-GUID-free *aggregate* JSON receipts from the SAME real
AssetRipper source SHA and run. Does not claim original lower-mip, Unity Editor
import, or Android GPU equivalence. Original game assets are never changed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from scripts.gt_stage_serialized_owners import InventoryError


def strictly_equal(record, expected, category):
    if type(record) is not dict:
        raise InventoryError("untrusted_original_"+category+"_receipt")
    for key,wanted in expected.items():
        value=record.get(key)
        if type(value) is not type(wanted) or value!=wanted:
            raise InventoryError("failed_original_"+category+"_"+key)


def gate(arrays, external, bc3):
    strictly_equal(arrays,{
        "status":"ALL_28_ORIGINAL_ARRAY_MATERIAL_REFS_MATCH_REPAIRED_IMPORTERS",
        "original_array_objects_SHA256_authenticated":9,
        "exact_original_class187_array_material_refs":28,
        "distinct_source_array_guids_referenced_by_materials":9,
        "source_zero_pixel_original_array_refs":20,
        "full_array_material_importer_links_verified":True,
        "original_array_export_importer_guids_preserved":True,
        "original_source_game_assets_changed":False,
        "Android_runtime_pixels_verified":False,
    },"array_material")
    strictly_equal(external,{
        "status":"EXTERNAL_TEXTURE_SOURCE_EXPORT_LINKS_CLASSIFIED",
        "authenticated_owner_tables":82,
        "original_external_texture_slots":416,
        "exact_cross_owner_source_export_texture_links":416,
        "external_links_not_yet_proven":0,
        "mismatched_source_to_export_external_links":0,
        "all_external_links_verified":True,
        "source_or_exported_assets_modified":False,
        "Unity_Editor_or_Android_GPU_pixels_verified":False,
    },"external_texture")
    strictly_equal(bc3,{
        "original_source_populated_layers_expected":50,
        "sampled_original_source_layer0_mips_vs_PNG_cells":50,
        "original_arrays_with_pixels":8,
        "original_source_empty_pixel_arrays":1,
        "all_original_BC3_source_array_PNG_pixels_proven":True,
        "full_original_top_mip_layer_pixel_comparison_requested":True,
        "all_populated_original_BC3_top_mip_layers_match_exported_PNG":True,
        "full_mip_chain_pixel_equivalence_proven":False,
        "Unity_Android_GPU_pixels_verified":False,
    },"original_BC3")
    counts=bc3.get("counts")
    strictly_equal(counts,{
        "slice_major_exact_samples":50,
        "real_source_array_payloads_compared":8,
        "source_zero_pixel_arrays":1,
        "export_png_contains_all_source_layer_cells":9,
        "unambiguous_original_BC3_slice_layout_slice_major":8,
        "no_exact_source_BC3_to_export_PNG_match":0,
    } if "no_exact_source_BC3_to_export_PNG_match" in (counts or {}) else {
        "slice_major_exact_samples":50,
        "real_source_array_payloads_compared":8,
        "source_zero_pixel_arrays":1,
        "export_png_contains_all_source_layer_cells":9,
        "unambiguous_original_BC3_slice_layout_slice_major":8,
    },"original_BC3_counts")
    return {
        "schema":"GT_SAME_REAL_EXPORT_ORIGINAL_TEXTURE_INTEGRITY_FINAL_V1",
        "status":"SOURCE_BC3_AND_TEXTURE_CROSS_OWNER_PARITY_VERIFIED",
        "sha256_original_texture_array_objects":9,
        "exact_original_class187_Material_links":28,
        "sha256_verified_cross_owner_texture_sources":82,
        "exact_original_external_material_Texture_PPtrs":416,
        "all_original_source_BC3_top_mip_layers_exact":50,
        "original_array_logical_empty_source_layers":2,
        "original_or_exported_assets_modified":False,
        "original_lower_mip_chain_equivalence_proven":False,
        "Unity_Editor_or_Android_Adreno_GPU_proven":False,
        "source_identifiers_or_pixels_disclosed":False,
    }


def load(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>256*1024:
        raise InventoryError("missing_or_oversized_private_aggregate_receipt")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError,UnicodeError) as error:
        raise InventoryError("malformed_private_aggregate_receipt") from error


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("arrays","external","bc3","report"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    if (args.report.exists() or args.report.is_symlink() or
        args.report.resolve() in {args.arrays.resolve(),args.external.resolve(),args.bc3.resolve()}):
        raise InventoryError("unsafe_original_texture_integrity_report")
    result=gate(load(args.arrays),load(args.external),load(args.bc3))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_REAL_ORIGINAL_TEXTURE_INTEGRITY_FINAL "+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
