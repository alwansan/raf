#!/usr/bin/env python3
"""GT isolated *actual* vendor ShaderLab recovery trial on exported Raft Unity assets.

Run the exact existing authenticated TMP, PostFX v1 (shader and compute), and
volumetric source restorers used by the production workflow. Reject any change
to previously exported .meta bytes. Compare T3's raw vs restored Material
ShaderLab quality. This never compiles Unity/Adreno shader variants or builds APK.
CI must supply an isolated temporary ExportedProject, not a working source tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys

from scripts.gt_compare_shader_restore_quality import compare
from scripts.t3_audit_exported_material_programs import audit as shader_audit

RESTORERS = (
    ("tmp", "scripts.restore_tmp_shaders"),
    ("postfx", "scripts.restore_postfx_shaders"),
    ("histogram_compute", "scripts.restore_postfx_compute"),
    ("volumetric", "scripts.restore_volumetric_shaders"),
)
SCHEMA = "GT_ACTUAL_ISOLATED_VENDOR_SHADER_RESTORATION_V1"


def original_meta_digests(assets: Path) -> dict:
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("missing_actual_unity_exported_assets")
    rows = {}
    for path in assets.rglob("*.meta"):
        if path.is_symlink() or not path.is_file():
            raise ValueError("unsafe_original_exported_meta")
        rel = path.relative_to(assets).as_posix()
        with path.open("rb") as stream:
            rows[rel] = hashlib.file_digest(stream, "sha256").hexdigest()
    if not rows or len(rows) > 50_000:
        raise ValueError("invalid_original_exported_meta_count")
    return rows


def metadata_integrity(original: dict, current: dict) -> dict:
    # Official vendor ShaderLab restorers may install new shader and .meta
    # files. The contract is that *all previously exported originals* remain
    # byte-identical. Never mistake a new authenticated vendor fallback meta
    # for a mutation of an existing original Raft material/scene/shader GUID.
    missing = set(original) - set(current)
    changed = {name for name in original.keys() & current.keys()
               if original[name] != current[name]}
    added = set(current) - set(original)
    return {
        "original_exported_meta_bytes_unchanged": not (missing or changed),
        "original_meta_removed": len(missing),
        "original_meta_changed": len(changed),
        "new_vendor_meta_documents_added": len(added),
    }


def histogram_source_snapshot(project: Path):
    """Identify one original EyeHistogram ComputeShader using its native YAML."""
    candidates=list((project/"Assets").rglob("EyeHistogram.asset"))
    if not candidates:
        return None  # synthetic no-histogram export only
    if len(candidates)!=1:
        raise ValueError("ambiguous_original_histogram_compute_identity")
    source=candidates[0]
    meta=Path(str(source)+".meta")
    if (source.is_symlink() or meta.is_symlink() or not meta.is_file()):
        raise ValueError("untrusted_original_histogram_compute_meta")
    original=source.read_bytes()
    if (b"--- !u!72 &7200000" not in original or
        b"m_Name: EyeHistogram" not in original):
        raise ValueError("unexpected_original_histogram_class_identity")
    metadata=meta.read_bytes()
    matches=re.findall(rb"(?m)^guid: ([a-f0-9]{32})$",metadata)
    if len(matches)!=1:
        raise ValueError("invalid_original_histogram_compute_GUID")
    return {
        "source_rel":source.relative_to(project),
        "source_sha256":hashlib.sha256(original).hexdigest(),
        "source_meta":metadata,
        "original_guid":matches[0],
    }


def histogram_migration_verified(project:Path,backup_root:Path,snapshot)->bool:
    """Validate the exact official source .asset → Resources .compute GUID move."""
    if snapshot is None:
        return False
    previous=project/snapshot["source_rel"]
    old_meta=Path(str(previous)+".meta")
    if previous.exists() or old_meta.exists():
        return False
    archive=backup_root/"histogram_compute"/snapshot["source_rel"]
    archive_meta=Path(str(archive)+".meta")
    if any(p.is_symlink() for p in (archive,archive_meta)):
        return False
    if not archive.is_file() or not archive_meta.is_file():
        return False
    if (hashlib.sha256(archive.read_bytes()).hexdigest()!=snapshot["source_sha256"]
        or archive_meta.read_bytes()!=snapshot["source_meta"]):
        return False
    target=project/"Assets/RaftAndroid/Resources/Shaders/EyeHistogram.compute"
    target_meta=Path(str(target)+".meta")
    if any(p.is_symlink() for p in (target,target_meta)):
        return False
    if not target.is_file() or not target_meta.is_file():
        return False
    payload=target.read_bytes()
    meta=target_meta.read_bytes()
    if (b"#pragma kernel KEyeHistogram" not in payload or
        b"#pragma kernel KEyeHistogramClear" not in payload or
        b"ComputeShaderImporter:" not in meta or
        len(re.findall(rb"(?m)^guid: ([a-f0-9]{32})$",meta))!=1 or
        re.findall(rb"(?m)^guid: ([a-f0-9]{32})$",meta)[0]!=snapshot["original_guid"]):
        return False
    # Fail closed on duplicate existing GUIDs; a valid Unity asset must have
    # exactly one meta file with this identity after the documented move.
    hits=0
    for p in (project/"Assets").rglob("*.meta"):
        if p.is_symlink() or not p.is_file():
            return False
        if snapshot["original_guid"] in re.findall(rb"(?m)^guid: ([a-f0-9]{32})$",p.read_bytes()):
            hits+=1
    return hits==1


def approved_meta_integrity(project:Path,backup_root:Path,original:dict,snapshot)->dict:
    report=metadata_integrity(original,original_meta_digests(project/"Assets"))
    raw_missing=report["original_meta_removed"]
    repaired=0
    if raw_missing==1 and snapshot is not None:
        if histogram_migration_verified(project,backup_root,snapshot):
            repaired=1
    report["verified_ComputeShader_GUID_relocation_count"]=repaired
    report["original_meta_removed_unapproved"]=raw_missing-repaired
    report["original_meta_contract_preserved_with_verified_compute_relocation"]=(
        report["original_meta_changed"]==0 and raw_missing==repaired)
    return report


def run(project: Path, raw_quality: dict, backup_root: Path, *,
        runner=subprocess.run, quality=shader_audit, seconds: int=360) -> dict:
    project, backup_root = project.absolute(), backup_root.absolute()
    if any(p.is_symlink() for p in (project, *project.parents, backup_root, *backup_root.parents)):
        raise ValueError("unsafe_unity_export_or_backup_path")
    if backup_root.is_relative_to(project) or project.is_relative_to(backup_root):
        raise ValueError("backup_directory_overlaps_exported_unity_project")
    if backup_root.exists():
        raise ValueError("backup_directory_must_not_exist")
    before = original_meta_digests(project/"Assets")
    histogram=histogram_source_snapshot(project)
    report = {
        "schema": SCHEMA, "status":"RUNNING",
        "original_exported_meta_documents":len(before),
        "original_exported_meta_bytes_unchanged":False,
        "source_original_game_assets_modified":False,
        "git_lfs_used":False,
        "original_Raft_Shader48_DXBC_to_Adreno_parity_verified":False,
        "android_shader_compilation_or_gpu_pixels_verified":False,
        "completed_original_vendor_restorer_steps":[],
    }
    error = None
    backup_root.mkdir(parents=True)
    try:
        for step, module in RESTORERS:
            command = [
                sys.executable, "-m", module,
                "--project", str(project),
                "--backup", str(backup_root / step),
            ]
            try:
                result = runner(
                    command, check=False, capture_output=True, text=True,
                    timeout=seconds, cwd=Path(__file__).resolve().parents[1])
            except subprocess.TimeoutExpired:
                error = (step,"VENDOR_RESTORER_TIMEOUT")
                break
            except OSError:
                error = (step,"VENDOR_RESTORER_PROCESS_ERROR")
                break
            if result.returncode != 0:
                error = (step,"VENDOR_RESTORER_REJECTED")
                break
            report["completed_original_vendor_restorer_steps"].append(step)
        if error is None:
            post=quality(project)
            diff=compare(raw_quality,post,approved_meta_integrity(
                project,backup_root,before,histogram)[
                    "original_meta_contract_preserved_with_verified_compute_relocation"])
            report["postrestore_material_quality"]=diff
            report["status"]="POST_RESTORE_SOURCE_QUALITY_COMPARED"
    except (ValueError, OSError) as exc:
        error = ("postrestore_metadata_or_quality",type(exc).__name__)
    finally:
        report.update(approved_meta_integrity(project,backup_root,before,histogram))
    if error is not None:
        report["status"]="REJECTED"
        report["failure_stage"]=error[0]
        report["failure_category"]=error[1]
    if not report["original_meta_contract_preserved_with_verified_compute_relocation"]:
        report["status"]="REJECTED"
        report["failure_category"]="UNAUTHORIZED_OR_UNPROVEN_ORIGINAL_EXPORTED_META_MUTATION"
    return report


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--raw-quality",type=Path,required=True)
    ap.add_argument("--backup-root",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    output=args.report.absolute()
    if output.resolve().is_relative_to(args.project.resolve()) or output == args.raw_quality.absolute():
        raise ValueError("unsafe_vendor_quality_report_path")
    before=json.loads(args.raw_quality.read_text())
    result=run(args.project,before,args.backup_root)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_ACTUAL_POSTRESTORER_SHADER_QUALITY "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="POST_RESTORE_SOURCE_QUALITY_COMPARED" else 2


if __name__=="__main__":
    raise SystemExit(main())
