"""Verify GFX114 GPU image readbacks against the signed APK CPU masks."""
import argparse
import hashlib
import io
import json
import struct
from zipfile import ZipFile

from PIL import Image
from gfxlab.tools.gfx109_owner_zip_audit import audit as audit_positions
from gfxlab.tools.gfx112_animated_payload import EXPECTED

SIDE = 256


def audit(owner_zip, apk, *, experiment="GFX114"):
    depth = experiment == "GFX115"
    expected_files = {"summary.json", *(name + ".png" for name in EXPECTED)}
    with ZipFile(owner_zip) as z, ZipFile(apk) as package:
        entries = z.infolist()
        if ({e.filename for e in entries} != expected_files or len(entries) != len(expected_files)
                or any(e.file_size > 512 * 1024 for e in entries)):
            raise ValueError("Raster captures missing, duplicated, or oversized")
        data = z.read("summary.json")
        summary_only = io.BytesIO()
        with ZipFile(summary_only, "w") as a:
            a.writestr("summary.json", data)
        positions = audit_positions(summary_only, apk, experiment=experiment,
                                    expected={name: (1666, 8) for name in EXPECTED})
        rows = []
        for c in json.loads(data)["cases"]:
            name = c["model"]
            record = c["raster"]
            filename = name + ".png"
            raw = z.read(filename)
            reference = package.read(f"assets/{name}." + ("depth" if depth else "mask"))
            if (record["image"] != filename or hashlib.sha256(raw).hexdigest() != record["image_sha256"]
                    or hashlib.sha256(reference).hexdigest() != record["reference_sha256"]):
                raise ValueError("Raster hash mismatch")
            if len(reference) != SIDE*SIDE*(2 if depth else 1):
                raise ValueError("Invalid reference dimensions")
            if depth:
                reference_codes = struct.unpack(f"<{SIDE*SIDE}H", reference)
                coverage = [int(v != 0) for v in reference_codes]
            else:
                if set(reference) != {0,1}:
                    raise ValueError("Invalid reference mask")
                coverage = reference
            with Image.open(io.BytesIO(raw)) as image:
                if image.format != "PNG" or image.size != (SIDE,SIDE):
                    raise ValueError("Wrong capture format")
                pixels = list(struct.iter_unpack("4B", image.convert("RGBA").tobytes()))
                if depth:
                    if any(a != 255 or b not in (0,255) or bool(r or g) != (b == 255)
                           for r,g,b,a in pixels):
                        raise ValueError("Invalid encoded depth capture")
                    actual = [int(b == 255) for _,_,b,_ in pixels]
                    edge = package.read(f"assets/{name}.edge")
                    if len(edge) != SIDE*SIDE or set(edge) - {0,1}:
                        raise ValueError("Invalid near-edge diagnostic mask")
                    errors = [(abs(((r << 8) | g) - ref), mark) for (r,g,b,_),ref,mark in
                              zip(pixels,reference_codes,edge,strict=True) if b == 255 and ref]
                    stable = [e for e,mark in errors if not mark]
                    all_errors = [e for e,_ in errors]
                    depth_stats = {"depth_max_error_codes":max(all_errors,default=0),
                                   "depth_sum_error_codes":sum(all_errors),
                                   "depth_error_over_eight":sum(e > 8 for e in all_errors)}
                    if any(record[k] != v for k,v in depth_stats.items()):
                        raise ValueError("Depth values disagree with reported statistics")
                else:
                    if set(pixels) - {(0,0,0,255),(255,255,255,255)}:
                        raise ValueError("Nonbinary capture")
                    actual = [int(r == 255) for r,_,_,_ in pixels]
            union = sum(x or y for x,y in zip(actual,coverage,strict=True))
            overlap = sum(x and y for x,y in zip(actual,coverage,strict=True))
            difference = union - overlap
            if (overlap, union, difference) != (record["intersection"],record["union"],record["different_pixels"]):
                raise ValueError("Capture pixels disagree with reported statistics")
            rows.append({"pose":name,"intersection":overlap,"union":union,
                         "different_pixels":difference,"iou":overlap/union if union else 0.0})
            if depth:
                rows[-1].update(depth_stats, stable_depth_max_error_codes=max(stable,default=0),
                                stable_depth_sum_error_codes=sum(stable), stable_pixels=len(stable),
                                uncertain_pixels=sum(edge))
        if len(rows) != len(EXPECTED):
            raise ValueError("Incomplete capture results")
    return {**positions,"raster_cases":rows,"min_iou":min(r["iou"] for r in rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("signed_apk")
    args = parser.parse_args()
    print(json.dumps(audit(args.owner_zip,args.signed_apk),indent=2))
