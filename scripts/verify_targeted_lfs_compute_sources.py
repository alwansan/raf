"""Authenticate exactly three original Raft serialized ComputeShader LFS owners.

No Unity Editor or game execution. Expected content identity comes from the
committed Git LFS pointers; print sizes and hashes, never source data.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

EXPECTED = {
    "resources.assets": (111_533_516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115_978_112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
    "sharedassets36.assets": (110_149_324, "b32fcd9d327c8926b2309ffc1b5645a0c23d64ed95be37ed94e96f34736530c8"),
}
_POINTER = re.compile(r"\Aversion https://git-lfs.github.com/spec/v1\noid sha256:([a-f0-9]{64})\nsize ([0-9]+)\n?\Z")
CHUNK = 4 * 1024 * 1024


def verify_sources(root: Path, *, pointers_only=False, expected=None):
    manifest = EXPECTED if expected is None else expected
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Original Unity asset directory absent or unsafe")
    result = []
    for name, (size, oid) in sorted(manifest.items()):
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("Unsafe original LFS owner name")
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Missing original LFS owner or unsafe symlink: " + name)
        actual_size = path.stat().st_size
        if pointers_only:
            if actual_size > 512:
                raise ValueError("Expected Git LFS pointer, got hydrated source: " + name)
            match = _POINTER.fullmatch(path.read_text(encoding="ascii"))
            if match is None or match[1] != oid or int(match[2]) != size:
                raise ValueError("Original Git LFS pointer identity changed: " + name)
            result.append({"owner": name, "size": size, "sha256": oid, "verified_pointer": True})
            continue
        if actual_size != size:
            raise ValueError("Original LFS payload size mismatch or still a pointer: " + name)
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while True:
                chunk = stream.read(CHUNK)
                if not chunk:
                    break
                digest.update(chunk)
        if digest.hexdigest() != oid:
            raise ValueError("Original LFS payload SHA256 mismatch: " + name)
        result.append({"owner": name, "size": size, "sha256": oid, "verified_payload": True})
    return {
        "sources": result,
        "authenticated_owners": len(result),
        "expected_total_payload_bytes": sum(size for size, _ in manifest.values()),
        "no_unity_build_or_gpu_execution": True,
        "game_sources_modified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--pointers-only", action="store_true")
    args = parser.parse_args()
    print("RAFT_TARGETED_LFS_COMPUTE_SOURCE_AUTH " + json.dumps(
        verify_sources(args.source, pointers_only=args.pointers_only), sort_keys=True))


if __name__ == "__main__":
    main()
