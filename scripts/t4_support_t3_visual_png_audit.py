#!/usr/bin/env python3
"""T4 assisting T3: independently audit exact owner-shared GLSurfaceView PNG colors.

PNG data is parsed locally with stdlib only. Emit numerical coverage, never pixels,
image bytes or user paths. This reports the captured PNG, not GLES/Unity correctness.
"""
import argparse
import binascii
import hashlib
import json
from pathlib import Path
import struct
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_SIZE, MAX_DECOMPRESSED, MAX_DIM = 1_500_000, 38_000_000, 3000
PNG_REQUIRED_CHUNKS = {b"IHDR", b"IDAT", b"IEND"}


def png_rgba_rows(file):
    if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_SIZE:
        raise ValueError("Invalid or oversized PNG")
    data = file.read_bytes()
    if len(data) < 68 or data[:8] != PNG_MAGIC:
        raise ValueError("Invalid PNG signature")
    pos, chunks, compressed, palette, alpha = 8, set(), bytearray(), None, None
    width = height = channels = 0
    seen_iend = False
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError("Truncated PNG chunk")
        n = struct.unpack_from(">I", data, pos)[0]
        name = data[pos + 4:pos + 8]
        if n > MAX_SIZE or pos + n + 12 > len(data):
            raise ValueError("PNG chunk exceeds strict bound")
        chunk = data[pos + 8:pos + 8 + n]
        actual = binascii.crc32(name + chunk) & 0xffffffff
        expected = struct.unpack_from(">I", data, pos + 8 + n)[0]
        if actual != expected:
            raise ValueError("PNG CRC mismatch")
        if not all((65 <= b <= 90 or 97 <= b <= 122) for b in name):
            raise ValueError("Invalid PNG chunk type")
        if not chunks and name != b"IHDR":
            raise ValueError("PNG must begin with IHDR")
        if name == b"IHDR":
            if b"IHDR" in chunks or n != 13:
                raise ValueError("Repeated/invalid PNG IHDR")
            width, height, depth, kind, compression, flt, interlace = struct.unpack(">IIBBBBB", chunk)
            if not 1 <= width <= MAX_DIM or not 1 <= height <= MAX_DIM or width * height > 5_000_000:
                raise ValueError("PNG dimensions too large")
            if depth != 8 or kind not in (2, 3, 6) or compression or flt or interlace:
                raise ValueError("PNG encoding unsupported (8-bit noninterlaced RGB/RGBA/indexed only)")
            channels = {2: 3, 3: 1, 6: 4}[kind]
        elif name == b"PLTE":
            if len(chunk) % 3 or not 3 <= len(chunk) <= 768:
                raise ValueError("Invalid indexed palette")
            palette = [tuple(chunk[i:i + 3]) for i in range(0, len(chunk), 3)]
        elif name == b"tRNS":
            if len(chunk) > 256:
                raise ValueError("Invalid alpha palette")
            alpha = chunk
        elif name == b"IDAT":
            if b"IDAT" not in chunks and b"IEND" in chunks:
                raise ValueError("IDAT after IEND")
            compressed.extend(chunk)
        elif name == b"IEND":
            if n != 0 or pos + 12 != len(data):
                raise ValueError("PNG must end at IEND")
            seen_iend = True
        elif name[0] & 32 == 0:
            raise ValueError("Unsupported PNG critical chunk")
        chunks.add(name)
        pos += 12 + n
        if seen_iend:
            break
    if not PNG_REQUIRED_CHUNKS.issubset(chunks) or not seen_iend:
        raise ValueError("Incomplete PNG")
    if channels == 1 and palette is None:
        raise ValueError("Palette missing")
    stride = width * channels
    exact_length = (stride + 1) * height
    if exact_length > MAX_DECOMPRESSED:
        raise ValueError("Oversized decompressed PNG")
    decoder = zlib.decompressobj()
    raw = decoder.decompress(bytes(compressed), MAX_DECOMPRESSED + 1)
    if len(raw) != exact_length or not decoder.eof or decoder.unused_data:
        raise ValueError("PNG inflated size/stream mismatch")
    prior = bytearray(stride)
    for row in range(height):
        i = row * (stride + 1)
        filt = raw[i]
        scan = bytearray(raw[i + 1:i + 1 + stride])
        if filt > 4:
            raise ValueError("Invalid PNG filter")
        for x in range(stride):
            left = scan[x - channels] if x >= channels else 0
            up = prior[x]
            ul = prior[x - channels] if x >= channels else 0
            if filt == 1:
                scan[x] = (scan[x] + left) & 255
            elif filt == 2:
                scan[x] = (scan[x] + up) & 255
            elif filt == 3:
                scan[x] = (scan[x] + ((left + up) // 2)) & 255
            elif filt == 4:
                pred = left + up - ul
                dl, du, dul = abs(pred - left), abs(pred - up), abs(pred - ul)
                ref = left if dl <= du and dl <= dul else up if du <= dul else ul
                scan[x] = (scan[x] + ref) & 255
        prior = scan
        out = []
        for x in range(width):
            k = x * channels
            if channels == 4:
                r, g, b, a = scan[k:k + 4]
            elif channels == 3:
                r, g, b = scan[k:k + 3]
                a = 255
            else:
                index = scan[k]
                if index >= len(palette):
                    raise ValueError("Palette index outside PNG palette")
                r, g, b = palette[index]
                a = alpha[index] if alpha is not None and index < len(alpha) else 255
            out.append((r, g, b, a))
        yield width, height, row, out


def color_stats(path):
    source = hashlib.sha256(path.read_bytes()).hexdigest()
    totals = {"samples": 0, "nearly_black": 0, "red": 0, "green": 0,
              "blue": 0, "visible": 0, "neutral": 0}
    focus = totals.copy()
    width = height = 0
    for width, height, row, pixels in png_rgba_rows(path):
        for x, (r, g, b, a) in enumerate(pixels):
            # Central crop excludes title, Android status bar, bottom actions.
            mid = (width // 5 <= x < 4 * width // 5 and
                   height // 4 <= row < 3 * height // 4)
            for counts in ((totals, focus) if mid else (totals,)):
                counts["samples"] += 1
                if a >= 64:
                    counts["visible"] += 1
                if r < 28 and g < 28 and b < 28:
                    counts["nearly_black"] += 1
                if r >= 140 and r > g * 1.6 and r > b * 1.6:
                    counts["red"] += 1
                if g >= 140 and g > r * 1.6 and g > b * 1.6:
                    counts["green"] += 1
                if b >= 140 and b > r * 1.6 and b > g * 1.6:
                    counts["blue"] += 1
                if max(r, g, b) - min(r, g, b) < 24:
                    counts["neutral"] += 1
    def ratio(sample):
        n = max(1, sample["samples"])
        return {k + "_pct": round(v * 100 / n, 3) for k, v in sample.items()
                if k != "samples"}
    return {"width": width, "height": height, "raw_png_sha256": source,
            "whole": ratio(totals), "center": ratio(focus)}


def verify_original_blob(path, known_git_blob):
    data = path.read_bytes()
    git = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if git != known_git_blob:
        raise ValueError("Original CL PNG immutable blob hash mismatch")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, required=True)
    ap.add_argument("--assert-owner-snapshot", action="store_true")
    args = ap.parse_args()
    if args.dir.is_symlink() or not args.dir.is_dir():
        raise SystemExit("Private CL PNG directory invalid")
    known = [
        ("T3-01-1794163319210.png", "33572d9228164650713a6387dc762ffa9836d1c5"),
        ("T3-02-1794163320563.png", "fc2793cfed8a7597c6f70cb8cddf6257fa72dd65"),
        ("T3-03-1794163321896.png", "b62832a39a3e6ff169bf475b6f96513c610149f2"),
        ("T3-04-1794163323592.png", "f6eaecd9263c41767f036569587df57c634ca34e"),
        ("T3-05-1794163324937.png", "8e81eb539f5fea2212b3bc928c05bbc9cecaf384"),
        ("T3-06-1794163326320.png", "614b6a28eb12a1e5ce2d4d4fb581c9b5957d204e"),
    ]
    stats = {}
    for i, (filename, git_sha) in enumerate(known, 1):
        path = args.dir / filename
        if args.assert_owner_snapshot:
            verify_original_blob(path, git_sha)
        stats[f"T3-{i:02d}"] = color_stats(path)
    case1 = stats["T3-01"]["center"]
    # A "bad" case is only a reason for T3 to review source-vs-display,
    # not a user FAIL. PixelCopy.success and glReadPixels success diverge.
    distinct = [name for name in ("red_pct", "green_pct", "blue_pct")
                if case1[name] >= 1.0]
    decision = (
        "RGB_STRIPES_PRESENT_IN_CAPTURED_CENTER"
        if len(distinct) == 3 else
        "RGB_STRIPES_UNPROVEN_IN_CAPTURED_CENTER"
    )
    report = {
        "status": "CL_OWNER_GL_SCREENSHOT_VISUAL_AUDIT",
        "t3_01_center_rgb_count_ge_1pct": len(distinct),
        "t3_01_captured_rgb_decision": decision,
        "cases": {k: {"width": v["width"], "height": v["height"],
                      "whole": v["whole"], "center": v["center"]}
                  for k, v in stats.items()},
        "screen_screenshot_not_gameplay_proof": True,
        "source_glreadpixels_not_replayed": True,
        "evidence_only_no_human_pass": True,
    }
    print("T4_SUPPORT_T3_CL_PNG " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
