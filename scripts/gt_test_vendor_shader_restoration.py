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
            diff=compare(raw_quality,post,before==original_meta_digests(project/"Assets"))
            report["postrestore_material_quality"]=diff
            report["status"]="POST_RESTORE_SOURCE_QUALITY_COMPARED"
    except (ValueError, OSError) as exc:
        error = ("postrestore_metadata_or_quality",type(exc).__name__)
    finally:
        report["original_exported_meta_bytes_unchanged"] = (
            original_meta_digests(project/"Assets")==before)
    if error is not None:
        report["status"]="REJECTED"
        report["failure_stage"]=error[0]
        report["failure_category"]=error[1]
    if not report["original_exported_meta_bytes_unchanged"]:
        report["status"]="REJECTED"
        report["failure_category"]="ORIGINAL_EXPORTED_META_MUTATED"
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
