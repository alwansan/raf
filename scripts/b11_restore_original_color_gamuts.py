"""Guard original Raft Unity color-gamut settings in an exported project.

The original SHA-verified globalgamemanagers PlayerSettings contains [0] (sRGB).
Unity ProjectSettings YAML serializes the one-element int32 array as 00000000.
Do not interpret this as evidence of an exported mismatch or a device fix.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import tempfile

from scripts.b04_restore_original_color_settings import (
    MAX_PROJECT_SETTINGS_BYTES,
    original_color_space,
)

GAMUT_FIELD = re.compile(r"(?m)^[ \t]*m_ColorGamuts[ \t]*:")
GAMUT_VALUE = re.compile(r"(?m)^  m_ColorGamuts:([ \t]*)([a-fA-F0-9]{8})([ \t]*)(?=\r?$)")
PLAYER_HEADER = re.compile(r"(?m)^PlayerSettings:[ \t]*\r?$")
EXPECTED_GAMUT = "00000000"


def patch_gamut_bytes(before: bytes) -> tuple[bytes, str]:
    """Update only one recognized serialized 32-bit gamut. Fail closed otherwise."""
    if not before or len(before) > MAX_PROJECT_SETTINGS_BYTES or b"\0" in before:
        raise ValueError("invalid or oversized ProjectSettings")
    try:
        source = before.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("ProjectSettings must be UTF-8") from exc
    if len(PLAYER_HEADER.findall(source)) != 1:
        raise ValueError("Require exactly one PlayerSettings document")
    if len(GAMUT_FIELD.findall(source)) != 1:
        raise ValueError("Require exactly one m_ColorGamuts field")
    matches = list(GAMUT_VALUE.finditer(source))
    if len(matches) != 1:
        raise ValueError("Unknown m_ColorGamuts layout; do not guess serialized array")
    m = matches[0]
    current = m.group(2)
    # Only bounded, independently recognizable one-element enum values are
    # eligible for a patch; unknown byte arrangements require investigation.
    if current.lower() not in {"00000000", "01000000", "02000000"}:
        raise ValueError("Unknown one-element gamut value; refuse correction")
    replaced = source[:m.start(2)] + EXPECTED_GAMUT + source[m.end(2):]
    result = replaced.encode("utf-8")
    if len(result) != len(before):
        raise ValueError("Gamut edit changed file size")
    # Regex spans are Python Unicode character offsets, not UTF-8 byte
    # offsets. A non-ASCII ProjectSettings field before m_ColorGamuts must
    # never cause an unrelated-byte false positive (or widen the edit scope).
    byte_start = len(source[:m.start(2)].encode("utf-8"))
    byte_end = byte_start + len(current)  # The matched gamut is ASCII hex.
    if (before[:byte_start] != result[:byte_start]
            or before[byte_end:] != result[byte_end:]
            or result[byte_start:byte_end] != EXPECTED_GAMUT.encode("ascii")):
        raise ValueError("Gamut edit changed unrelated ProjectSettings bytes")
    return result, current


def restore_gamut(project: Path, apply: bool = False) -> dict:
    parent = project / "ProjectSettings"
    target = parent / "ProjectSettings.asset"
    if project.is_symlink() or parent.is_symlink() or target.is_symlink():
        raise ValueError("Unsafe symlink in project path")
    if not parent.is_dir() or not target.is_file():
        raise ValueError("ProjectSettings.asset not available")
    metadata = target.stat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise ValueError("ProjectSettings must be an unshared regular file")
    if metadata.st_size > MAX_PROJECT_SETTINGS_BYTES:
        raise ValueError("ProjectSettings too large")
    before = target.read_bytes()
    after, current = patch_gamut_bytes(before)
    mismatch = before != after
    if apply and mismatch:
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=parent, prefix=".b11-gamut-", delete=False) as stream:
                temp_path = Path(stream.name)
                stream.write(after)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temp_path, stat.S_IMODE(metadata.st_mode))
            fresh = target.stat()
            if (fresh.st_ino != metadata.st_ino or
                    fresh.st_mtime_ns != metadata.st_mtime_ns or
                    target.read_bytes() != before):
                raise ValueError("Concurrent ProjectSettings modification")
            os.replace(temp_path, target)
            temp_path = None
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
    return {
        "expected_source_gamut_srgb": True,
        "exported_single_gamut_srgb_before": current.lower() == EXPECTED_GAMUT,
        "mismatch_detected": mismatch,
        "changed": bool(apply and mismatch),
        "parity_after": bool(apply or not mismatch),
        "other_project_settings_bytes_preserved": True,
        "original_assets_changed": False,
        "unity_gpu_or_device_verified": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    original_color_space(args.original)  # SHA/size/engine/gamut verified by B04.
    result = restore_gamut(args.project, apply=args.apply)
    print("RAFT_B11_ORIGINAL_COLOR_GAMUT " + json.dumps(result, sort_keys=True))
    return 0 if result["parity_after"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
