"""Read-only, SHA-pinned owner 5 Nov Raft world .rgd intake.

Source is the exact CL snapshot checked out separately by Actions. No user names,
paths, save fields or raw data are reported. Authentication precedes staging.
Never run BinaryFormatter on unknown, unchecked bytes.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Mapping

# Immutable Git object identities read from CL@520c4cf409aa20a4db54ff80ed87d8807d9cba57.
# All seven owner-world saves are distinct, even when two share the same length.
EXPECTED: Mapping[str, int] = {
    "458e0c2bb46f26084cbb2aacaa33913c8ac52daa": 309519,
    "7e8be5203dd47ea6469e43abacb901b4089bb246": 319239,
    "8564720a2f72a47091d30c9eae05ebd527be50ac": 319239,
    "f30fc3f416899cca5b2fb955e437fc716bfcafff": 331887,
    "65280828d55f133854fc4c16474c4e3f0bfeac30": 330281,
    "a091dd94d84047e68eb8d9715987948b57178aa6": 311063,
    "7fad8e552e737cc73985a6906c7ce753d45a41a5": 318536,
}
MAX_SINGLE_BYTES = 1024 * 1024
MAX_SAMPLES = 8


def git_blob_sha1(content: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(content)).encode("ascii") + b"\0" + content
    ).hexdigest()


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def verify_worlds(
    checkout: Path, *, allowlist: Mapping[str, int] = EXPECTED
) -> dict[str, bytes]:
    """Authenticate all .rgd files from one World directory, fail closed."""
    if checkout.is_symlink() or not checkout.is_dir():
        raise ValueError("CL_CHECKOUT_ROOT_INVALID")
    real_root = checkout.resolve()
    candidates = [p for p in checkout.rglob("World") if p.is_dir()]
    if len(candidates) != 1:
        raise ValueError("EXPECTED_SINGLE_WORLD_COLLECTION")
    world = candidates[0]
    if world.is_symlink() or not _is_within(world.resolve(), real_root):
        raise ValueError("WORLD_FOLDER_INVALID")
    rgds = sorted(world.rglob("*.rgd"))
    if len(rgds) != len(allowlist) or len(rgds) > MAX_SAMPLES:
        raise ValueError("WORLD_BLOB_COUNT_MISMATCH")
    staged: dict[str, bytes] = {}
    for source in rgds:
        if (source.is_symlink() or not source.is_file() or
                not _is_within(source.resolve(), real_root) or
                any(p.is_symlink() for p in source.parents if _is_within(p, checkout))):
            raise ValueError("WORLD_BLOB_LINK_OR_PATH")
        size = source.stat().st_size
        if size == 0 or size > MAX_SINGLE_BYTES:
            raise ValueError("WORLD_BLOB_OVERSIZE_OR_EMPTY")
        content = source.read_bytes()
        if len(content) != size:
            raise ValueError("WORLD_BLOB_CHANGED_DURING_READ")
        digest = git_blob_sha1(content)
        if digest in staged or allowlist.get(digest) != size:
            raise ValueError("WORLD_BLOB_SHA_SIZE_MISMATCH")
        staged[digest] = content
    if set(staged) != set(allowlist):
        raise ValueError("WORLD_BLOB_ALLOWLIST_INCOMPLETE")
    return staged


def stage_verified_worlds(
    checkout: Path, out: Path, *, allowlist: Mapping[str, int] = EXPECTED
) -> int:
    """Copy private verified samples under sanitized sample ordinals only."""
    # Validate the complete input cohort before creating any output file.
    data = verify_worlds(checkout, allowlist=allowlist)
    real_source = checkout.resolve()
    if out.is_symlink() or _is_within(out.resolve(), real_source):
        raise ValueError("OUTPUT_MUST_BE_OUTSIDE_SOURCE")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("OUTPUT_MUST_BE_EMPTY")
    out.mkdir(parents=True, exist_ok=True)
    for position, digest in enumerate(sorted(data), start=1):
        target = out / f"owner{position:02d}.rgd"
        if target.exists() or target.is_symlink():
            raise ValueError("OUTPUT_COLLISION")
        target.write_bytes(data[digest])
    return len(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", required=True, type=Path)
    parser.add_argument("--stage-dir", required=True, type=Path)
    args = parser.parse_args()
    count = stage_verified_worlds(args.checkout, args.stage_dir)
    print(f"T4_OWNER_5NOV_RGD source_exact=true count={count} " +
          "user_paths_logged=false bytes_published=false android_device_tested=false")


if __name__ == "__main__":
    main()
