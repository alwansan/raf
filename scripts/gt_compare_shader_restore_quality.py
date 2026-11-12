#!/usr/bin/env python3
"""GT compare real original AssetRipper Material ShaderLab quality before/after vendor restores.

Aggregate only. A restored upstream ShaderLab pass is NOT original Raft DXBC
variant parity and does not establish Android device/GLES/Vulkan execution.
This compares T3's exact same exported Unity project after official pinned
TMP/PostFX/Volumetric restorers without changing any existing .meta GUID.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

STATUS="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
COUNT_KEYS=(
    "material_documents",
    "material_docs_using_dummy_Shader",
    "material_docs_using_non_dummy_Shader",
    "material_docs_using_Unity_builtin_Shader",
    "material_docs_with_unknown_or_broken_Shader",
    "shader_files",
    "shader_files_with_dummy_exporter_marker",
    "shader_files_with_complete_program_pass",
)


def compare(before:dict,after:dict,original_metas_unchanged:bool) ->dict:
    if (before.get("status")!=STATUS or after.get("status")!=STATUS or
        not isinstance(original_metas_unchanged,bool)):
        raise ValueError("invalid_before_after_shader_quality_source")
    counts=[]
    for item in (before,after):
        c=item.get("counts")
        if not isinstance(c,dict) or any(type(c.get(k)) is not int or c[k]<0 for k in COUNT_KEYS):
            raise ValueError("missing_or_negative_shader_quality_counts")
        if c["material_docs_using_dummy_Shader"] + c["material_docs_using_non_dummy_Shader"] + c["material_docs_using_Unity_builtin_Shader"] + c["material_docs_with_unknown_or_broken_Shader"] > c["material_documents"]:
            raise ValueError("shader_material_count_inconsistent")
        counts.append(c)
    raw,installed=counts
    if raw["material_documents"] != installed["material_documents"]:
        raise ValueError("vendor_restore_changed_exported_material_document_count")
    if not original_metas_unchanged:
        raise ValueError("original_meta_guid_modified_by_shader_restore")
    new_invalid=max(0,installed["material_docs_with_unknown_or_broken_Shader"]-
                    raw["material_docs_with_unknown_or_broken_Shader"])
    if new_invalid:
        raise ValueError("vendor_restore_introduced_unresolved_material_shader")
    return {
        "schema": "GT_REAL_EXPORTED_VENDOR_SHADER_RESTORATION_COMPARISON_V1",
        "status": "POST_RESTORE_SOURCE_QUALITY_COMPARED",
        "total_exported_material_documents":raw["material_documents"],
        "raw_custom_dummy_material_documents":raw["material_docs_using_dummy_Shader"],
        "postrestore_custom_dummy_material_documents":installed["material_docs_using_dummy_Shader"],
        "dummy_material_documents_decreased_by":raw["material_docs_using_dummy_Shader"]-installed["material_docs_using_dummy_Shader"],
        "raw_non_dummy_custom_material_documents":raw["material_docs_using_non_dummy_Shader"],
        "postrestore_non_dummy_custom_material_documents":installed["material_docs_using_non_dummy_Shader"],
        "raw_shader_files_with_dummy_marker":raw["shader_files_with_dummy_exporter_marker"],
        "postrestore_shader_files_with_dummy_marker":installed["shader_files_with_dummy_exporter_marker"],
        "postrestore_shaders_with_programmed_pass":installed["shader_files_with_complete_program_pass"],
        "original_exported_meta_bytes_unchanged":True,
        "original_material_yaml_count_unchanged":True,
        "original_shader_variant_parity_proven":False,
        "android_shader_compilation_or_pixels_verified":False,
        "target_original_game_data_modified":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--before",type=Path,required=True)
    ap.add_argument("--after",type=Path,required=True)
    ap.add_argument("--original-metas-unchanged",choices=("true","false"),required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    if args.report.is_relative_to(args.before.parent) or args.report.is_relative_to(args.after.parent):
        # A safe aggregate JSON may live alongside other CI receipts, but not
        # replace the actual input reports.
        if args.report.resolve() in (args.before.resolve(),args.after.resolve()):
            raise ValueError("do_not_overwrite_shader_report")
    result=compare(json.loads(args.before.read_text()),json.loads(args.after.read_text()),
                   args.original_metas_unchanged=="true")
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_POSTRESTORER_MATERIAL_SHADER_QUALITY "+json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
