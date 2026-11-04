"""B45: atomic installation of one authenticated original Blur ShaderLab candidate.

The candidate must be reconstructed privately from SHA-pinned original Raft
objects and independently verified against the W5 two-pass CPU Vulkan proof.
Never write the original shader source or private candidate to this repository,
CI artifact, or logs. Preserve the *existing exported target* .meta verbatim.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from scripts.a12_probe_original_blur_passes import TARGET
from scripts.restore_builtin_shaders import (
    _require_safe_asset_path, exported_shader_identity,
)

CANDIDATE_SHA256 = "5886dc362fc1a4a237aa05f6b4244ec30af4daad4089edea008f95d760945e14"
CANDIDATE_BYTES = 23068


def check_safe_ancestors(path):
    path = Path(path).absolute()
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise ValueError("Unsafe symlinked original path or parent")
    return path



def _atomic_replace_bytes(path, data, prefix):
    """Same-directory fsynced rename; never truncate an existing .shader."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="wb", prefix=prefix, dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

def install(project, candidate, backup):
    """Install only after exact identity and SHA; backup remains outside project."""
    project, candidate, backup = [
        check_safe_ancestors(path) for path in (project, candidate, backup)
    ]
    assets = project / "Assets"
    _require_safe_asset_path(assets, assets)
    if candidate.is_relative_to(project) or not candidate.is_file():
        raise ValueError("Private original-derived Blur candidate must be external regular file")
    if backup.is_relative_to(project) or backup.exists():
        raise ValueError("Fresh external backup required")
    content = candidate.read_bytes()
    if len(content) != CANDIDATE_BYTES or hashlib.sha256(content).hexdigest() != CANDIDATE_SHA256:
        raise ValueError("Private Blur candidate SHA/byte commitment changed")
    if exported_shader_identity(content.decode("utf-8-sig")) != TARGET:
        raise ValueError("Private Blur candidate ShaderLab identity changed")
    targets = []
    for path in assets.rglob("*.shader"):
        _require_safe_asset_path(assets, path)
        if exported_shader_identity(path.read_text(encoding="utf-8-sig")) == TARGET:
            targets.append(path)
    if len(targets) != 1:
        raise ValueError("Require unique original Blur exported Shader identity")
    target = targets[0]
    meta = Path(str(target) + ".meta")
    _require_safe_asset_path(assets, meta)
    if not meta.is_file() or meta.is_symlink():
        raise ValueError("Require one original exported shader .meta")
    original, metadata = target.read_bytes(), meta.read_bytes()
    lines = [line for line in metadata.splitlines() if line.startswith(b"guid:")]
    if len(lines) != 1 or not re.fullmatch(rb"guid: *[0-9a-fA-F]{32} *", lines[0]):
        raise ValueError("Original exported shader GUID malformed or ambiguous")
    backup.mkdir(parents=True, exist_ok=False)
    try:
        (backup / "original.shader").write_bytes(original)
        (backup / "original.shader.meta").write_bytes(metadata)
        if (backup / "original.shader").read_bytes() != original or (backup / "original.shader.meta").read_bytes() != metadata:
            raise ValueError("Original Blur rollback backup corrupted")
    except BaseException:
        shutil.rmtree(backup)
        raise
    changed = False
    try:
        _require_safe_asset_path(assets, target)
        if target.read_bytes() != original or meta.read_bytes() != metadata:
            raise ValueError("Exported Blur source changed during installation")
        _atomic_replace_bytes(target, content, ".b45-blur-")
        changed = True
        if target.read_bytes() != content or meta.read_bytes() != metadata:
            raise ValueError("Installed original Blur source or metadata mismatch")
    except BaseException:
        if changed:
            try:
                # Preserve the external verified backup on *every* outcome.
                # In-place Path.write_bytes could truncate the only active
                # exported shader if the rollback itself fails.
                _require_safe_asset_path(assets, target)
                if meta.read_bytes() != metadata:
                    raise ValueError("Original Blur metadata changed during rollback")
                _atomic_replace_bytes(target, original, ".b20-blur-restore-")
                if target.read_bytes() != original or meta.read_bytes() != metadata:
                    raise ValueError("Original Blur rollback bytes not restored")
            except BaseException as rollback_error:
                raise RuntimeError(
                    "Original Blur rollback failed; external pristine backup retained"
                ) from rollback_error
        raise
    return {
        "installed_exported_blur_targets": 1,
        "private_original_derived_shader_sha256": CANDIDATE_SHA256,
        "original_export_sha256": hashlib.sha256(original).hexdigest(),
        "exported_meta_sha256": hashlib.sha256(metadata).hexdigest(),
        "original_export_guid_unchanged": True,
        "backup_external_and_complete": True,
        "authentic_source_material_binding_verified": False,
        "unity_or_adreno_execution_verified": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--private-shader", required=True, type=Path)
    parser.add_argument("--backup", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    a = parser.parse_args()
    result = install(a.project, a.private_shader, a.backup)
    a.out.write_text(json.dumps(result, sort_keys=True) + "\n")
    print("RAFT_B45_BLUR_INSTALL " + json.dumps(result, sort_keys=True))
