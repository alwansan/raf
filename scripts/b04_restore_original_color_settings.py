"""Restore the authenticated original Raft color-space in temporary Unity exports.

Only one PlayerSettings.m_ActiveColorSpace scalar is modified after original
bytes are SHA/size verified. This is configuration parity, not pixel/device proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

ORIGINAL_SIZE = 1_914_356
ORIGINAL_SHA256 = "6d1288cd08b91d8c321ed2526503404b64b978819985b9b7fa5a9a146c29a8f5"
EXPECTED_UNITY_VERSION = "2021.3.45f2"
MAX_PROJECT_SETTINGS_BYTES = 4 * 1024 * 1024
PLAYER_HEADER = re.compile(r"(?m)^PlayerSettings:\s*\r?$")
COLOR_FIELD = re.compile(r"(?m)^[ \t]*m_ActiveColorSpace[ \t]*:")
COLOR_VALUE = re.compile(r"(?m)^  m_ActiveColorSpace:([ \t]*)([01])([ \t]*)(?=\r?$)")


def original_color_space(original: Path) -> int:
    """Require exactly the verified original owner before typed parsing."""
    if original.is_symlink() or not original.is_file():
        raise ValueError("original PlayerSettings owner must be a regular file")
    if original.stat().st_size != ORIGINAL_SIZE:
        raise ValueError("original PlayerSettings owner size mismatch")
    digest = hashlib.sha256()
    with original.open("rb") as src:
        for block in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != ORIGINAL_SHA256:
        raise ValueError("original PlayerSettings owner digest mismatch")

    from scripts.probe_w2_color_space_settings import read_color_space

    metadata = read_color_space(original)
    value = metadata["active_color_space"]["value"]
    if value != 1 or metadata.get("engine_version") != EXPECTED_UNITY_VERSION:
        raise ValueError("original color space / Unity version differs from verified reference")
    if metadata.get("color_gamuts") != [0]:
        raise ValueError("original gamut metadata differs from verified reference")
    return value


def patch_settings_bytes(before: bytes, expected: int) -> tuple[bytes, int]:
    """Reject ambiguous YAML; replace a single one-byte digit only."""
    if expected not in (0, 1):
        raise ValueError("unexpected Unity color-space enum")
    if not before or len(before) > MAX_PROJECT_SETTINGS_BYTES or b"\x00" in before:
        raise ValueError("invalid or over-budget exported ProjectSettings")
    try:
        source = before.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("ProjectSettings is not UTF-8 text") from exc
    if len(PLAYER_HEADER.findall(source)) != 1:
        raise ValueError("expected a single serialized PlayerSettings document")
    if len(COLOR_FIELD.findall(source)) != 1:
        raise ValueError("missing or duplicate m_ActiveColorSpace")
    matches = list(COLOR_VALUE.finditer(source))
    if len(matches) != 1:
        raise ValueError("unexpected m_ActiveColorSpace formatting or enum")
    match = matches[0]
    present = int(match[2])
    result = (source[:match.start(2)] + str(expected) + source[match.end(2):]).encode("utf-8")
    if len(result) != len(before) or sum(a != b for a, b in zip(before, result)) != int(present != expected):
        raise ValueError("exported settings edit exceeded single scalar")
    return result, present


def restore_color_space(project: Path, color_space: int, apply: bool = False) -> dict:
    """Repair temporary exported project only; preserve other bytes and modes."""
    parent = project / "ProjectSettings"
    settings = parent / "ProjectSettings.asset"
    if project.is_symlink() or parent.is_symlink() or settings.is_symlink():
        raise ValueError("unsafe symlink in exported project target")
    if not parent.is_dir() or not settings.is_file():
        raise ValueError("exported ProjectSettings missing")
    metadata = settings.stat()
    if metadata.st_nlink != 1 or not stat.S_ISREG(metadata.st_mode):
        raise ValueError("exported settings must be an unshared regular file")
    if metadata.st_size > MAX_PROJECT_SETTINGS_BYTES:
        raise ValueError("exported settings oversized")
    before = settings.read_bytes()
    after, present = patch_settings_bytes(before, color_space)
    mismatch = before != after
    if apply and mismatch:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=parent, prefix=".b04-colorspace-", delete=False) as f:
                temporary = Path(f.name)
                f.write(after)
                f.flush()
                os.fsync(f.fileno())
            os.chmod(temporary, stat.S_IMODE(metadata.st_mode))
            current = settings.stat()
            if current.st_ino != metadata.st_ino or settings.read_bytes() != before:
                raise ValueError("concurrent exported settings change")
            os.replace(temporary, settings)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return {
        "original_color_space": color_space,
        "exported_color_space_before": present,
        "mismatch_detected": mismatch,
        "changed": bool(apply and mismatch),
        "parity_after": bool(apply or not mismatch),
        "other_bytes_preserved": True,
        "unity_or_gpu_executed": False,
        "device_color_verified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    value = original_color_space(args.original)
    result = restore_color_space(args.project, value, apply=args.apply)
    print("RAFT_B04_SOURCE_COLOR_SPACE " + json.dumps(result, sort_keys=True))
    return 0 if result["parity_after"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
