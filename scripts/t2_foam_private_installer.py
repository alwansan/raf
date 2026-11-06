"""T2 Foam: fail-closed private ShaderLab -> transient Unity exported shader install.

This is a *source-file transaction*, NOT shader authenticity, real Material binding,
Unity compilation, CB0 upload, or Android acceptance. Only call from a runner that
has separately SHA-authenticated original ZIP2 and constructed the private Foam
candidate. Never print the private shader or original exported bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from scripts.b24_original_foam_stage_translation import TARGET
from scripts.b45_install_original_blur import check_safe_ancestors, _atomic_replace_bytes
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.restore_builtin_shaders import _require_safe_asset_path, exported_shader_identity

MAX_CANDIDATE_BYTES = 4 * 1024 * 1024
EXPECTED_STAGE_STATUS = "original_private_foam_two_pass_shaderlab_structural_candidate"
TRUE_STAGE_FIELDS = (
    "original_DXBC_stage_model_SHA_verified",
    "shaderlab_target_derived_per_pass_not_guessed",
)
FALSE_STAGE_FIELDS = (
    "shaderlab_unity_import_verified",
    "original_cb0_name_or_data_upload_verified",
    "original_material_sampler_upload_verified",
    "original_numeric_or_device_pixels_verified",
    "private_shaderlab_published",
)


def require_attested_stage(report: dict, byte_count: int) -> None:
    """Verify a separately generated source-attested report, not a user claim.

    The caller MUST independently establish the report and SHA came from pinned
    original ZIP2 staging. Passing this dictionary is not original provenance.
    """
    if not isinstance(report, dict):
        raise ValueError("private stage report missing")
    required = {
        "status": EXPECTED_STAGE_STATUS, "private_candidate_bytes": byte_count,
        "original_passes": 2, "original_program_stages": 4,
        "original_stage_models_verified": 4, "authentic_pass_states": 2,
        "complete_structural_passes": 2, "authored_properties": 2,
        "authored_texture_properties": 1,
    }
    for name, value in required.items():
        if name not in report or type(report[name]) is not type(value) or report[name] != value:
            raise ValueError("private Foam source attestation field mismatch")
    for name in TRUE_STAGE_FIELDS:
        if report.get(name) is not True:
            raise ValueError("private Foam verified source flag missing")
    for name in FALSE_STAGE_FIELDS:
        if report.get(name) is not False:
            raise ValueError("private Foam runtime status misreported")


def _stage_sha_valid(value: str) -> bool:
    return type(value) is str and re.fullmatch("[0-9a-f]{64}", value) is not None


def _verify_candidate(candidate: Path, expected_sha256: str, stage: dict) -> bytes:
    if not _stage_sha_valid(expected_sha256):
        raise ValueError("private candidate expected SHA malformed")
    if not candidate.is_file() or candidate.is_symlink():
        raise ValueError("private candidate must be regular")
    size = candidate.stat().st_size
    if not 0 < size <= MAX_CANDIDATE_BYTES:
        raise ValueError("private candidate size outside budget")
    require_attested_stage(stage, size)
    content = candidate.read_bytes()
    if len(content) != size or hashlib.sha256(content).hexdigest() != expected_sha256:
        raise ValueError("private candidate SHA changed after source staging")
    try:
        shader = content.decode("utf-8")
    except UnicodeError as exc:
        raise ValueError("private candidate not utf8") from exc
    if exported_shader_identity(shader) != TARGET:
        raise ValueError("private candidate original Foam ShaderLab identity mismatch")
    passes = pass_coverage(shader)
    if (passes["subshader_pass_counts"] != [2] or passes["pass_count"] != 2
            or passes["passes_with_complete_program"] != 2
            or passes["all_subshaders_programmed"] is not True
            or passes["pass_braces_balanced"] is not True):
        raise ValueError("private candidate two original complete passes missing")
    return content


def _write_backup(path: Path, data: bytes):
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        import os
        os.fsync(stream.fileno())
    if path.read_bytes() != data:
        raise ValueError("external original backup not durable")


def install(project: Path, candidate: Path, backup: Path,
            expected_sha256: str, stage: dict) -> dict:
    """Atomic one-target install; backup kept outside transient Unity project.

    Concurrent mutation is not supported. Caller must serialize source staging
    and install in one ephemeral runner, and inspect exported GUID after Unity.
    """
    project, candidate, backup = (
        check_safe_ancestors(p) for p in (project, candidate, backup)
    )
    assets = project / "Assets"
    _require_safe_asset_path(assets, assets)
    if (candidate.is_relative_to(project) or backup.is_relative_to(project)
            or candidate == backup or backup.exists() or backup.is_symlink()
            or not backup.parent.is_dir()):
        raise ValueError("private Foam source or backup path unsafe")
    content = _verify_candidate(candidate, expected_sha256, stage)

    targets = []
    for path in assets.rglob("*.shader"):
        _require_safe_asset_path(assets, path)
        if path.is_symlink() or not path.is_file():
            raise ValueError("redirected exported shader")
        if exported_shader_identity(path.read_text(encoding="utf-8-sig")) == TARGET:
            targets.append(path)
            if len(targets) > 1:
                break
    if len(targets) != 1:
        raise ValueError("require exactly one original Foam exported shader")
    target = targets[0]
    meta = Path(str(target) + ".meta")
    _require_safe_asset_path(assets, meta)
    if not meta.is_file() or meta.is_symlink():
        raise ValueError("missing original exported Foam shader metadata")
    original, metadata = target.read_bytes(), meta.read_bytes()
    lines = [row for row in metadata.splitlines() if row.startswith(b"guid:")]
    if len(lines) != 1 or not re.fullmatch(rb"guid: *[0-9a-fA-F]{32} *", lines[0]):
        raise ValueError("untrusted original shader GUID")

    backup.mkdir(mode=0o700, parents=False, exist_ok=False)
    try:
        _write_backup(backup / "original.shader", original)
        _write_backup(backup / "original.shader.meta", metadata)
    except BaseException:
        shutil.rmtree(backup)
        raise

    changed = False
    try:
        _require_safe_asset_path(assets, target)
        if target.read_bytes() != original or meta.read_bytes() != metadata:
            raise ValueError("exported shader changed before source replacement")
        _atomic_replace_bytes(target, content, ".t2-foam-install-")
        changed = True
        if target.read_bytes() != content or meta.read_bytes() != metadata:
            raise ValueError("private candidate or original GUID changed after install")
    except BaseException:
        if changed:
            try:
                _require_safe_asset_path(assets, target)
                if meta.read_bytes() != metadata:
                    raise ValueError("original GUID changed during install")
                _atomic_replace_bytes(target, original, ".t2-foam-rollback-")
                if target.read_bytes() != original or meta.read_bytes() != metadata:
                    raise ValueError("original Foam shader rollback verification failed")
            except BaseException as err:
                raise RuntimeError("Foam rollback failure; external pristine backup retained") from err
        raise
    return {
        "unique_original_foam_exported_target_installed": 1,
        "private_source_attestation_and_stage_SHA_checked": True,
        "original_export_meta_bytes_unchanged": True,
        "external_recovery_backup_complete": True,
        "private_shaderlab_published": False,
        "Unity_2021_import_verified": False,
        "original_Material_CB0_runtime_binding_verified": False,
        "Android_water_pixels_verified": False,
    }


def _read_safe_stage(path: Path) -> dict:
    def no_duplicates(pairs):
        d = {}
        for key, value in pairs:
            if key in d:
                raise ValueError("duplicate original stage report key")
            d[key] = value
        return d
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--backup", type=Path, required=True)
    ap.add_argument("--source-stage-report", type=Path, required=True)
    ap.add_argument("--expected-candidate-sha256", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = check_safe_ancestors(args.out)
    project = check_safe_ancestors(args.project)
    if out.is_relative_to(project) or out.exists() or out.is_symlink() or not out.parent.is_dir():
        raise SystemExit("Unsafe private install report path")
    try:
        result = install(args.project, args.candidate, args.backup,
                         args.expected_candidate_sha256,
                         _read_safe_stage(args.source_stage_report))
        code = 0
    except BaseException as err:
        result = {
            "status": "blocked",
            "failure_type": type(err).__name__,
            "private_shaderlab_published": False,
            "Unity_2021_import_verified": False,
            "Android_water_pixels_verified": False,
        }
        code = 2
    out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    print("T2_FOAM_PRIVATE_INSTALL_SAFE " + json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
