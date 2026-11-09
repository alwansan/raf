#!/usr/bin/env python3
"""Verify actual PNG file bytes against Android Mini Lab T3 summary metadata.

This is an offline file-integrity gate, NOT a visual/GPU acceptance test.
Only local paths explicitly supplied by the operator are read; content URIs
cannot be dereferenced on a CI runner. No game assets are processed.
"""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

SIGNATURE = b"\x89PNG\r\n\x1a\n"


def validate_png(raw):
    if not raw.startswith(SIGNATURE):
        raise ValueError("invalid PNG signature")
    offset = len(SIGNATURE)
    seen_ihdr = False
    seen_idat = False
    seen_iend = False
    idat_chunks = []
    width = height = 0
    while offset < len(raw):
        if len(raw) - offset < 12:
            raise ValueError("truncated PNG chunk")
        length = struct.unpack_from(">I", raw, offset)[0]
        if length > len(raw) - offset - 12:
            raise ValueError("PNG chunk length out of bounds")
        name = raw[offset + 4:offset + 8]
        data = raw[offset + 8:offset + 8 + length]
        expected = struct.unpack_from(">I", raw, offset + 8 + length)[0]
        if zlib.crc32(name + data) & 0xffffffff != expected:
            raise ValueError("PNG chunk CRC mismatch")
        if not seen_ihdr:
            if name != b"IHDR" or length != 13:
                raise ValueError("missing first IHDR")
            width, height = struct.unpack_from(">II", data)
            if not width or not height:
                raise ValueError("zero PNG dimensions")
            seen_ihdr = True
        elif name == b"IHDR":
            raise ValueError("duplicate IHDR")
        if name == b"IDAT":
            seen_idat = True
            idat_chunks.append(data)
        if name == b"IEND":
            if length or not seen_idat or seen_iend:
                raise ValueError("invalid IEND")
            seen_iend = True
            if offset + 12 != len(raw):
                raise ValueError("trailing bytes after IEND")
        offset += 12 + length
        if seen_iend:
            break
    if not seen_iend:
        raise ValueError("missing IEND")
    # Chunk CRC alone does not prove that the encoded image is decodable.
    # Limit expansion to avoid decompression bombs in untrusted uploads.
    compressed = b"".join(idat_chunks)
    decoder = zlib.decompressobj()
    limit = 128 * 1024 * 1024
    try:
        decoded = decoder.decompress(compressed, limit + 1)
        if len(decoded) > limit or decoder.unconsumed_tail:
            raise ValueError("PNG inflated image exceeds safety limit")
        decoded += decoder.flush(limit + 1 - len(decoded))
    except zlib.error as exc:
        raise ValueError("invalid PNG IDAT zlib stream") from exc
    if not decoder.eof or decoder.unused_data or not decoded:
        raise ValueError("incomplete or trailing PNG IDAT zlib data")
    return width, height


def verify(summary, image_dir):
    errors = []
    rows = summary.get("results", [])
    if not isinstance(rows, list):
        return ["results is not a list"]
    for case in sorted(f"T3-{i:02d}" for i in range(1, 7)):
        matches = [r for r in rows if isinstance(r, dict) and r.get("case_id") == case]
        if len(matches) != 1:
            errors.append(f"{case}: expected exactly one record")
            continue
        result = matches[0].get("result", {})
        if not isinstance(result, dict):
            errors.append(f"{case}: missing result")
            continue
        tokens = {}
        for token in str(result.get("observed", "")).split():
            if "=" in token:
                k, v = token.split("=", 1)
                if k in tokens:
                    errors.append(f"{case}: duplicate token {k}")
                tokens[k] = v
        digest = tokens.get("png_sha256", "")
        size = tokens.get("png_bytes", "")
        # Never derive a local path from an untrusted Android content URI.
        candidates = list(image_dir.glob(case + "-*.png"))
        if len(candidates) != 1:
            errors.append(f"{case}: expected one local PNG, got {len(candidates)}")
            continue
        try:
            raw = candidates[0].read_bytes()
            width, height = validate_png(raw)
            if hashlib.sha256(raw).hexdigest() != digest:
                errors.append(f"{case}: SHA256 mismatch")
            if str(len(raw)) != size:
                errors.append(f"{case}: byte length mismatch")
            print(f"{case}: PNG structure/CRC OK {width}x{height}, bytes={len(raw)}")
        except (ValueError, OSError) as exc:
            errors.append(f"{case}: {exc}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    parser.add_argument("image_dir", type=Path)
    args = parser.parse_args()
    errors = verify(json.loads(args.summary.read_text(encoding="utf-8")), args.image_dir)
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: six local PNG byte streams match summary metadata; visual parity NOT established")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
