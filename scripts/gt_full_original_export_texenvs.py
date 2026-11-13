#!/usr/bin/env python3
"""GT exact original ZIP2 Material TexEnv fidelity against ONE real AssetRipper export.

Authenticated original 82 Unity owners are joined with the *same export
instance*'s private object GUID trace and actual exported Material YAML.
Only aggregate counts leave CI. Reports deliberately do not prove external
texture target identity, Shader GPU programs, or Android rendering.
"""
from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path

from scripts.gt_stage_serialized_owners import OWNERS, InventoryError, read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.b05_verify_material_texenv_bindings import (
    compare, exported_texenvs, normalize_texenvs,
)

# Only these pre-audited generic error labels can appear in public CI receipts.
# Raw exception messages may include private names and therefore never leave CI.
PUBLIC_ERRORS = {
    "unsafe_original_source_directory",
    "invalid_original_material_owner_selection",
    "missing_original_unity_objects",
    "duplicate_original_material_identity",
    "original_texenv_unparseable",
    "no_original_materials_authenticated",
    "untrusted_same_instance_export_trace",
    "Original/export Material identities do not match same-instance trace",
    "Duplicated original object in trace",
    "Unusable duplicate Texture object trace",
    "Unverified traced original Material",
    "Unusable Material export pointer",
    "Two original Materials map to same exported object",
    "Original Material export pointer collides with out-of-scope Material",
    "Missing same-instance export trace",
    "Texture environment slots must be an array",
    "Malformed or duplicate Material texture slot",
    "Material texture data absent in export",
    "Missing or linked Material metadata",
    "Duplicated exported Material pointer",
    "No exported Material texture documents",
}


def public_failure(error, stage: str):
    code = str(error)
    if code not in PUBLIC_ERRORS:
        code = "unclassified_" + type(error).__name__
    return {
        "schema": "GT_FULL_82_ORIGINAL_TO_REAL_EXPORT_TEXENV_FIDELITY_V1",
        "status": "INCONCLUSIVE",
        "failed_phase": stage,
        "reason_code": code,
        "original_sources_modified": False,
        "exported_assets_or_meta_modified": False,
        "device_gpu_pixels_verified": False,
    }


def original(root: Path, manifest: Path, selected=None, loader=None, *,
             property_name="m_TexEnvs", normalize=normalize_texenvs) -> dict:
    if root.is_symlink() or not root.is_dir():
        raise InventoryError("unsafe_original_source_directory")
    expected=read_expected(manifest)
    names=sorted(OWNERS if selected is None else selected)
    if not names or len(names)!=len(set(names)) or not set(names)<=set(OWNERS):
        raise InventoryError("invalid_original_material_owner_selection")
    if loader is None:
        import UnityPy
        loader=lambda path: UnityPy.load(str(path))
    out={}
    for name in names:
        _,size,digest=expected[name]
        source=root/name
        verify(source,size,digest)
        env=loader(source)
        objects=getattr(env,"objects",None)
        if objects is None:
            raise InventoryError("missing_original_unity_objects")
        for obj in objects:
            if str(obj.type.name)!="Material":
                continue
            ident=(name,obj.path_id)
            if (type(obj.path_id) is not int or obj.path_id<=0 or ident in out):
                raise InventoryError("duplicate_original_material_identity")
            try:
                props=obj.read_typetree(check_read=False).get("m_SavedProperties")
                entries=props.get(property_name) if isinstance(props,dict) else None
                out[ident]=normalize(entries,exported=False)
            except Exception as error:
                raise InventoryError("original_texenv_unparseable") from error
        del env
        gc.collect()
    if not out:
        raise InventoryError("no_original_materials_authenticated")
    return out


def inspect(root:Path,manifest:Path,export_project:Path,private_trace:Path,
            *, loader=None, exported_parser=None, phase=None):
    if phase is not None:
        phase("original_authentication")
    source=original(root,manifest,loader=loader)
    if phase is not None:
        phase("private_same_instance_trace")
    if (not private_trace.is_file() or private_trace.is_symlink() or
            private_trace.stat().st_size>20*1024*1024 or
            private_trace.resolve().is_relative_to(export_project.resolve())):
        raise InventoryError("untrusted_same_instance_export_trace")
    trace=json.loads(private_trace.read_text(encoding="utf-8"))
    if phase is not None:
        phase("exported_material_yaml")
    exported=(exported_parser or exported_texenvs)(export_project)
    if phase is not None:
        phase("source_export_pointer_join")
    # The same exporter instance also traces Unity built-in engine Material
    # objects. Those source owners are outside the manifest's 82 original game
    # serialized files, so they must be excluded *by exact owner identity*.
    # Selected-owner B05 remains fail-closed for every one of the 82 owners
    # while recording out-of-scope engine targets separately; never interpret
    # an engine-owned Material as missing game source content.
    result=compare(trace,source,exported,selected_owners=set(OWNERS))
    result.update({
        "source_scope": "all_82_authenticated_original_game_owners",
        "external_engine_materials_outside_source_scope": result["outside_scope_trace_materials"],
        "schema":"GT_FULL_82_ORIGINAL_TO_REAL_EXPORT_TEXENV_FIDELITY_V1",
        "original_owners_sha256_verified":82,
        "original_material_objects":len(source),
        "original_texture_binding_pixels_read":False,
        "same_instance_export_source_join_performed":True,
        "all_external_texture_target_identifications_verified":False,
        "original_source_materials_modified":False,
        "exported_materials_modified":False,
        "git_lfs_used":False,
        "android_gpu_verified":False
    })
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,required=True,
                    help="full restored original ZIP2 Raft_Data")
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--export-project",type=Path,required=True)
    ap.add_argument("--trace",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    report=args.report.resolve()
    if (report.is_relative_to(args.source.resolve()) or
        report.is_relative_to(args.export_project.resolve())):
        raise InventoryError("report_inside_untrusted_original_or_export")
    phase = ["before_original"]
    def mark(name):
        phase[0] = name
    try:
        result=inspect(args.source,args.manifest,args.export_project,args.trace,
                       phase=mark)
        result["status"] = ("SOURCE_EXPORT_COMPARISON_COMPLETE"
                            if result["source_slots_faithful_with_resolved_scope"]
                            else "SOURCE_EXPORT_COMPARISON_REJECTED")
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        result=public_failure(error, phase[0])
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("GT_ALL_ORIGINAL_MATERIAL_TEXENV_EXPORT "+json.dumps(result,sort_keys=True))
    return 0 if result.get("status") == "SOURCE_EXPORT_COMPARISON_COMPLETE" else 2


if __name__=="__main__":
    raise SystemExit(main())
