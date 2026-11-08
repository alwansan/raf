#!/usr/bin/env python3
"""Identify earliest divergent private FFT RGBA32F pass; never print pixel values."""
import argparse
import json
import math
from pathlib import Path

MAX_CAPTURE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_CAPTURE_BYTES = 128 * 1024 * 1024
MAX_PASSES = 32


def reject_duplicate_manifest_keys(pairs):
    """A duplicate pass/capture key must not silently replace private evidence."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate private FFT manifest key")
        result[key] = value
    return result


def read_private_capture(root: Path, relative: str) -> bytes:
    """Read only bounded regular files directly beneath the private manifest directory."""
    if not isinstance(relative, str) or not relative or "\x00" in relative:
        raise ValueError("invalid private capture path")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.parts == (".",):
        raise ValueError("capture path must remain relative to manifest directory")
    target = root / candidate
    if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != root and root in p.parents):
        raise ValueError("symlink capture path rejected")
    resolved = target.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("capture escapes private manifest directory")
    size = resolved.stat().st_size
    if size == 0 or size > MAX_CAPTURE_BYTES or size % 16:
        raise ValueError("capture size invalid or exceeds private limit")
    with resolved.open("rb") as stream:
        data = stream.read(MAX_CAPTURE_BYTES + 1)
    if len(data) != size:
        raise ValueError("capture changed during bounded read")
    return data
from scripts.t1_fft_rgba_error_signature import signature

def compare_passes(pairs, *, atol=1e-5, rtol=1e-4):
    if not pairs:
        raise ValueError("at least one pass is required")
    if not all(math.isfinite(x) and x >= 0 for x in (atol, rtol)):
        raise ValueError("invalid tolerances")
    seen = set()
    results = []
    first = None
    for index, (name, reference, observed) in enumerate(pairs):
        if not isinstance(name, str) or not name or name in seen:
            raise ValueError("pass names must be nonempty and unique")
        seen.add(name)
        if not reference or not observed:
            raise ValueError("empty capture")
        report = signature(reference, observed, atol=atol, rtol=rtol)
        failed = not report["all_within_tolerance"]
        if failed and first is None:
            first = {"index": index, "pass": name}
        results.append({
            "pass": name, "pixels": report["pixels"],
            "mismatch_by_channel": [c["mismatched"] for c in report["channels"]],
            "nonfinite_by_channel": [c["nonfinite"] for c in report["channels"]],
            "within_tolerance": not failed,
        })
    return {"first_divergence": first, "passes": results, "all_match": first is None}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Private JSON list: [{name,reference,observed}]")
    parser.add_argument("--atol", type=float, default=1e-5)
    parser.add_argument("--rtol", type=float, default=1e-4)
    args = parser.parse_args()
    try:
        if args.manifest.is_symlink() or args.manifest.stat().st_size > 1024 * 1024:
            raise ValueError("manifest is symlinked or oversized")
        entries = json.loads(
            args.manifest.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_manifest_keys,
        )
        if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_PASSES:
            raise ValueError("manifest must contain 1..32 passes")
        # Validate every capture path and aggregate size before reading any pixel data.
        # This avoids loading early passes only to reject a later oversized pass.
        planned = []
        total_bytes = 0
        seen_names = set()
        manifest_dir = args.manifest.resolve().parent
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"name", "reference", "observed"}:
                raise ValueError("invalid pass entry")
            name = entry["name"]
            if not isinstance(name, str) or not name or name in seen_names:
                raise ValueError("pass names must be nonempty and unique")
            seen_names.add(name)
            for key in ("reference", "observed"):
                relative = entry[key]
                if not isinstance(relative, str) or not relative or "\x00" in relative:
                    raise ValueError("invalid capture path")
                candidate = Path(relative)
                if candidate.is_absolute() or ".." in candidate.parts:
                    raise ValueError("invalid capture path")
                # Use the same path confinement and symlink rules as the reader.
                target = manifest_dir / candidate
                if target.is_symlink() or any(p.is_symlink() for p in target.parents
                                              if p != manifest_dir and manifest_dir in p.parents):
                    raise ValueError("symlink capture path rejected")
                resolved = target.resolve(strict=True)
                if not resolved.is_relative_to(manifest_dir) or not resolved.is_file():
                    raise ValueError("capture escapes private manifest directory")
                size = resolved.stat().st_size
                if size == 0 or size > MAX_CAPTURE_BYTES or size % 16:
                    raise ValueError("capture size invalid or exceeds private limit")
                total_bytes += size
                if total_bytes > MAX_TOTAL_CAPTURE_BYTES:
                    raise ValueError("aggregate private capture budget exceeded")
            planned.append(entry)
        pairs = [(entry["name"], read_private_capture(manifest_dir, entry["reference"]),
                  read_private_capture(manifest_dir, entry["observed"])) for entry in planned]
        report = compare_passes(pairs, atol=args.atol, rtol=args.rtol)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, "Invalid private FFT pass manifest or capture: " + type(exc).__name__ + "\n")
    print(json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
