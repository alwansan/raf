"""Reconstruct only authenticated original Shader-bearing owners from pinned ZIP2 Git."""
import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS

ZIP2_SHA = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
PART_PATTERN = re.compile(r"part-([0-9]{5})\Z")
MAX_PART_SIZE = 45 * 1024 * 1024


def restore(root, out, owners=None):
    owners = SHADER_OWNERS if owners is None else owners
    root, out = Path(root), Path(out)
    if not root.is_dir() or root.is_symlink() or out.is_symlink():
        raise ValueError("Unsafe source or target")
    resolved_root, resolved_out = root.resolve(), out.resolve()
    if resolved_out == resolved_root or resolved_root in resolved_out.parents:
        raise ValueError("Cannot stage inside ZIP2 source")
    expected_total = sum(size for size, _ in owners.values())
    if not owners or shutil.disk_usage(out.parent if out.parent.is_dir() else Path(".")).free < expected_total * 2:
        raise ValueError("Insufficient source or disk budget")
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for key, (size, sha) in sorted(owners.items()):
        if Path(key).name != key or "/" in key or "\\" in key:
            raise ValueError("Unsafe asset filename")
        source, final = root / key, out / key
        partial = out / (key + ".a12r-incomplete")
        if final.exists() or final.is_symlink() or partial.exists() or partial.is_symlink():
            raise ValueError("Refuse to overwrite source staging")
        if source.is_dir() and not source.is_symlink():
            parts = [p for p in source.iterdir() if p.name.startswith("part-")]
            numbers = []
            for part in parts:
                match = PART_PATTERN.fullmatch(part.name)
                if not match or not part.is_file() or part.is_symlink():
                    raise ValueError("Invalid ZIP2 part")
                numbers.append(int(match.group(1)))
            if not 1 <= len(parts) <= 64 or sorted(numbers) != list(range(len(parts))):
                raise ValueError("Incomplete ZIP2 part sequence")
            paths = [source / ("part-%05d" % i) for i in range(len(parts))]
        elif source.is_file() and not source.is_symlink():
            paths = [source]
        else:
            raise ValueError("Missing ZIP2 asset source")
        digest, current = hashlib.sha256(), 0
        try:
            with partial.open("xb") as dest:
                for path in paths:
                    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_PART_SIZE:
                        raise ValueError("Invalid ZIP2 part size")
                    with path.open("rb") as stream:
                        while True:
                            chunk = stream.read(4 * 1024 * 1024)
                            if not chunk:
                                break
                            digest.update(chunk)
                            dest.write(chunk)
                            current += len(chunk)
                            if current > size:
                                raise ValueError("ZIP2 asset exceeds pinned size")
            if current != size or digest.hexdigest() != sha:
                raise ValueError("ZIP2 original asset SHA256 or byte size mismatch")
            partial.rename(final)
        finally:
            partial.unlink(missing_ok=True)
        total += current
    return {"restored_owners": len(owners), "original_bytes_verified": total,
            "sha256_verified": True, "lfs_network_downloaded": False,
            "unity_or_apk_built": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2-checkout", required=True, type=Path)
    p.add_argument("--dest", required=True, type=Path)
    args = p.parse_args()
    head = subprocess.run(
        ["git", "-C", str(args.zip2_checkout), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if head != ZIP2_SHA:
        raise ValueError("Untrusted ZIP2 source revision")
    summary = restore(args.zip2_checkout / "Raft" / "Raft_Data", args.dest)
    print("A12R_ZIP2_ORIGINAL " + " ".join("%s=%s" % p for p in summary.items()))


if __name__ == "__main__":
    main()
