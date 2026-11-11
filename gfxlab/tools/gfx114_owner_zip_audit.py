"""Verify GFX114 GPU image readbacks against the signed APK CPU masks."""
import argparse
import hashlib
import io
import json
from zipfile import ZipFile

from PIL import Image
from gfxlab.tools.gfx109_owner_zip_audit import audit as audit_positions
from gfxlab.tools.gfx112_animated_payload import EXPECTED

SIDE = 256


def audit(owner_zip, apk):
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
        positions = audit_positions(summary_only, apk, experiment="GFX114",
                                    expected={name: (1666, 8) for name in EXPECTED})
        rows = []
        for c in json.loads(data)["cases"]:
            name = c["model"]
            record = c["raster"]
            filename = name + ".png"
            raw = z.read(filename)
            reference = package.read(f"assets/{name}.mask")
            if (record["image"] != filename or hashlib.sha256(raw).hexdigest() != record["image_sha256"]
                    or hashlib.sha256(reference).hexdigest() != record["reference_sha256"]):
                raise ValueError("Raster hash mismatch")
            if len(reference) != SIDE*SIDE or set(reference) != {0,1}:
                raise ValueError("Invalid reference mask")
            with Image.open(io.BytesIO(raw)) as image:
                if image.format != "PNG" or image.size != (SIDE,SIDE):
                    raise ValueError("Wrong capture format")
                rgba = image.convert("RGBA")
                if set(rgba.getdata()) - {(0,0,0,255),(255,255,255,255)}:
                    raise ValueError("Nonbinary capture")
                actual = [int(r == 255) for r,_,_,_ in rgba.getdata()]
            union = sum(x or y for x,y in zip(actual,reference,strict=True))
            overlap = sum(x and y for x,y in zip(actual,reference,strict=True))
            difference = union - overlap
            if (overlap, union, difference) != (record["intersection"],record["union"],record["different_pixels"]):
                raise ValueError("Capture pixels disagree with reported statistics")
            rows.append({"pose":name,"intersection":overlap,"union":union,
                         "different_pixels":difference,"iou":overlap/union})
        if len(rows) != len(EXPECTED):
            raise ValueError("Incomplete capture results")
    return {**positions,"raster_cases":rows,"min_iou":min(r["iou"] for r in rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("signed_apk")
    args = parser.parse_args()
    print(json.dumps(audit(args.owner_zip,args.signed_apk),indent=2))
