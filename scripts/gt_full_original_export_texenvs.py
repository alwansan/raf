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


def original(root: Path, manifest: Path, selected=None, loader=None) -> dict:
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
                entries=props.get("m_TexEnvs") if isinstance(props,dict) else None
                out[ident]=normalize_texenvs(entries,exported=False)
            except Exception as error:
                raise InventoryError("original_texenv_unparseable") from error
        del env
        gc.collect()
    if not out:
        raise InventoryError("no_original_materials_authenticated")
    return out


def inspect(root:Path,manifest:Path,export_project:Path,private_trace:Path,
            *, loader=None, exported_parser=None):
    source=original(root,manifest,loader=loader)
    if (not private_trace.is_file() or private_trace.is_symlink() or
            private_trace.stat().st_size>20*1024*1024 or
            private_trace.resolve().is_relative_to(export_project.resolve())):
        raise InventoryError("untrusted_same_instance_export_trace")
    trace=json.loads(private_trace.read_text(encoding="utf-8"))
    exported=(exported_parser or exported_texenvs)(export_project)
    # Exact full export origin scope; no name-only matching.
    result=compare(trace,source,exported,selected_owners=None)
    result.update({
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
    result=inspect(args.source,args.manifest,args.export_project,args.trace)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("GT_ALL_ORIGINAL_MATERIAL_TEXENV_EXPORT "+json.dumps(result,sort_keys=True))
    if not result["source_slots_faithful_with_resolved_scope"]:
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
