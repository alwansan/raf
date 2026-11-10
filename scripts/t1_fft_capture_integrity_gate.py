"""Bounded private FFT capture SHA gate; emits metadata only, never pixels."""
import hashlib
from pathlib import Path
from scripts.t1_fft_readback_provenance import validate_manifest

def verify_captures(metadata, paths, root):
    result = validate_manifest(metadata)
    if not isinstance(paths, dict) or set(paths) != {p["name"] for p in metadata["passes"]}:
        raise ValueError("capture path names mismatch")
    root = Path(root).resolve(strict=True)
    total = 0
    for item in metadata["passes"]:
        pair = paths[item["name"]]
        if not isinstance(pair, dict) or set(pair) != {"vulkan", "unity"}:
            raise ValueError("invalid capture paths")
        for backend in ("vulkan", "unity"):
            relative = pair[backend]
            if not isinstance(relative, str) or not relative or "\x00" in relative:
                raise ValueError("invalid capture path")
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("unsafe capture path")
            candidate = root / path
            if candidate.is_symlink() or any(p.is_symlink() for p in candidate.parents
                                             if p != root and root in p.parents):
                raise ValueError("symlink capture rejected")
            resolved = candidate.resolve(strict=True)
            if not resolved.is_relative_to(root) or not resolved.is_file():
                raise ValueError("capture outside private root")
            size = resolved.stat().st_size
            if size != item[backend + "_bytes"]:
                raise ValueError("capture length mismatch")
            total += size
            if total > 128 * 1024 * 1024:
                raise ValueError("aggregate capture budget exceeded")
            digest = hashlib.sha256()
            count = 0
            with resolved.open("rb") as stream:
                while count < size:
                    chunk = stream.read(min(1024 * 1024, size - count))
                    if not chunk:
                        break
                    digest.update(chunk)
                    count += len(chunk)
            if count != size or resolved.stat().st_size != size:
                raise ValueError("capture changed during read")
            if digest.hexdigest() != item[backend + "_sha256"]:
                raise ValueError("capture digest mismatch")
    return {**result, "capture_hashes_verified": True,
            "verified_passes": [p["name"] for p in metadata["passes"]],
            "gpu_execution_proven": False, "original_kernel_binding_proven": False}
