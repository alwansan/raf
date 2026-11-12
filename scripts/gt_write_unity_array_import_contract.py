#!/usr/bin/env python3
"""GT produce private Unity Editor contract for the nine SHA-proven Raft arrays.

Consumes the exact authenticated ZIP2 source 82 containers and the SAME
AssetRipper export-instance trace. Requires all 28 material pointers and all
nine repaired PNG flipbook grids before writing a private Editor-only JSON
contract in disposable ExportedProject. No game bytes, GUIDs or filenames are
printed or uploaded; no original game files or meta are changed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_verify_original_array_export import source_arrays
from scripts.gt_verify_original_array_material_refs import check
from scripts.gt_repair_array_flipbook_importers import exact_targets
from scripts.gt_validate_texture2darray_flipbook import index_exported_array_meta


SCHEMA="GT_ORIGINAL_UNITY_TEXTURE2DARRAY_IMPORT_CONTRACT_V1"
RELATIVE=Path("Assets/Editor/RaftAndroid/GTOriginalArrayImportContract.json")


def build(original:dict,trace:dict,project:Path)->dict:
    report=check(project,original,trace)
    if (not report["full_array_material_importer_links_verified"]
        or report["exact_original_class187_array_material_refs"]!=28
        or report["distinct_source_array_guids_referenced_by_materials"]!=9):
        raise InventoryError("source_original_array_import_contract_links_not_verified")
    targets=exact_targets(original,trace,index_exported_array_meta(project))
    if len(targets)!=9:
        raise InventoryError("source_original_array_import_contract_wrong_scope")
    arrays=[]
    for identity,(png,meta,guid) in sorted(targets.items()):
        state=original[identity]
        if any(type(state.get(name)) is not int or state[name]<=0 for name in (
            "width","height","depth","source_mipmap_count")):
            raise InventoryError("source_original_array_contract_invalid_shape")
        arrays.append({
            "guid":guid,
            "width":state["width"],"height":state["height"],
            "depth":state["depth"],
            "mipmap_count":state["source_mipmap_count"],
            "has_original_source_pixels":bool(state.get("original_stream_size")),
        })
    if (sum(x["depth"] for x in arrays)!=52
        or sum(x["depth"] for x in arrays if x["has_original_source_pixels"])!=50
        or len({x["guid"] for x in arrays})!=9):
        raise InventoryError("source_original_array_contract_layer_scope_drift")
    return {
        "schema":SCHEMA,
        "arrays":arrays,
    }


def install(project:Path, original:dict,trace:dict)->dict:
    project=project.absolute()
    if (not (project/"Assets").is_dir() or
        any(path.is_symlink() for path in (project,*project.parents))):
        raise InventoryError("unsafe_Unity_project_array_contract")
    data=build(original,trace,project)
    target=project/RELATIVE
    if target.exists() or target.is_symlink() or Path(str(target)+".meta").exists():
        raise InventoryError("private_Unity_array_contract_preexisting_target")
    target.parent.mkdir(parents=True,exist_ok=True)
    fd,tempfile_name=tempfile.mkstemp(prefix=".gt-private-array-",dir=target.parent)
    staged=Path(tempfile_name)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as output:
            json.dump(data,output,sort_keys=True,indent=2)
            output.write("\n")
        if staged.is_symlink() or target.exists():
            raise InventoryError("private_Unity_array_contract_target_changed")
        os.replace(staged,target)
    finally:
        staged.unlink(missing_ok=True)
    return {
        "schema":"GT_PRIVATE_EDITOR_NATIVE_ARRAY_IMPORT_GATE_STAGED_V1",
        "nine_original_source_guids_and_arrays_in_private_Editor_manifest":len(data["arrays"]),
        "original_logical_layers":sum(x["depth"] for x in data["arrays"]),
        "original_layers_with_streamed_source_pixels":sum(
            x["depth"] for x in data["arrays"] if x["has_original_source_pixels"]),
        "original_class187_material_refs_source_proven":28,
        "original_source_array_guids_printed_or_uploaded":False,
        "original_exported_PNG_and_meta_modified":False,
        "Unity_Editor_import_execution_verified":False,
        "Android_GPU_color_parity_verified":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-source",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--trace",type=Path,required=True)
    p.add_argument("--project",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    if (args.report.absolute().is_relative_to(args.original_source.absolute()) or
        args.report.absolute().is_relative_to(args.project.absolute())):
        raise InventoryError("private_array_import_gate_public_report_inside_game_assets")
    original=source_arrays(args.original_source,args.manifest)
    report=install(args.project,original,json.loads(args.trace.read_text()))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_NATIVE_PRIVATE_UNITY_ARRAY_GATE "+json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
