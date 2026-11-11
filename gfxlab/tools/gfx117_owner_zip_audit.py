"""Verify GFX117 phone captures and compare with the private Mesa reference."""
import argparse
import hashlib
import io
import json
import struct
from zipfile import ZipFile

from PIL import Image

from gfxlab.tools.gfx109_owner_zip_audit import audit as audit_positions
from gfxlab.tools.gfx112_animated_payload import EXPECTED
from gfxlab.tools.gfx117_m02_uv_inputs import LOD, ROLES

POSES = ("C0P0", "C1P0", "C1P2", "C2P0", "C2P2")


def pixels(raw):
    with Image.open(io.BytesIO(raw)) as image:
        if image.format != "PNG" or image.size != (256,256):
            raise ValueError("Unexpected textured capture format")
        result = image.convert("RGBA").tobytes()
    if set(result[3::4]) != {0,255}:
        raise ValueError("Missing coverage or unexpected alpha")
    return result


def audit(owner, apk, mesa, reference_metadata):
    names = {f"{pose}-{role}-L{lod}.png" for pose in POSES for role in ROLES for lod in LOD}
    metadata = json.load(reference_metadata)["captures"]
    if set(metadata) != names:
        raise ValueError("Mesa reference metadata missing a capture")
    with ZipFile(owner) as z, ZipFile(mesa) as host:
        entries = z.infolist()
        if (len(entries) != 31 or {x.filename for x in entries} != names | {"summary.json"}
                or any(x.file_size > 512*1024 for x in entries)
                or len(host.namelist()) != 30 or set(host.namelist()) != names):
            raise ValueError("Incomplete or oversized textured capture archive")
        summary = z.read("summary.json")
        summary_only = io.BytesIO()
        with ZipFile(summary_only,"w") as out:
            out.writestr("summary.json",summary)
        report = audit_positions(summary_only,apk,experiment="GFX117",
                                 expected={name:(1666,8) for name in EXPECTED})
        results = []
        for case in json.loads(summary)["cases"]:
            pose = case["model"]
            if pose not in POSES:
                if "textured" in case:
                    raise ValueError("Unexpected captured pose")
                continue
            rows = case["textured"]
            if [(r["role"],r["mip"]) for r in rows] != [(r,l) for r in ROLES for l in LOD]:
                raise ValueError("Incorrect texture view order")
            for row in rows:
                name = f"{pose}-{row['role']}-L{row['mip']}.png"
                raw = z.read(name)
                if row["image"] != name or hashlib.sha256(raw).hexdigest() != row["image_sha256"]:
                    raise ValueError("Owner texture capture hash mismatch")
                actual, expected = pixels(raw), pixels(host.read(name))
                ref = metadata[name]
                if hashlib.sha256(expected).hexdigest() != ref["rgba_sha256"]:
                    raise ValueError("Mesa pixel hash mismatch")
                ac, ex = actual[3::4], expected[3::4]
                if ac.count(255) != row["covered_pixels"] or ex.count(255) != ref["covered_pixels"]:
                    raise ValueError("Coverage counter mismatch")
                errors = [abs(a-b) for (*rgb,a),(*ref_rgb,b) in
                          zip(struct.iter_unpack("4B",actual),struct.iter_unpack("4B",expected),strict=True)
                          if a == b == 255 for a,b in zip(rgb,ref_rgb,strict=True)]
                if not errors:
                    raise ValueError("No overlapping image coverage")
                results.append({"image":name,"coverage_different_pixels":sum(a!=b for a,b in zip(ac,ex,strict=True)),
                                "overlapping_pixels":len(errors)//3,"max_rgb_channel_error":max(errors),
                                "mean_rgb_channel_error":sum(errors)/len(errors),
                                "rgb_channels_over_two":sum(e>2 for e in errors)})
        if len(results) != 30:
            raise ValueError("Incomplete textured pose results")
    return {**report,"textured_views":results,"original_shader_restored":False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("apk")
    parser.add_argument("mesa_zip")
    parser.add_argument("mesa_metadata", type=argparse.FileType("r"))
    a = parser.parse_args()
    print(json.dumps(audit(a.owner_zip,a.apk,a.mesa_zip,a.mesa_metadata),indent=2))
