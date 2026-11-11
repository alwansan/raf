"""Audit Android Forward readback against the Mesa pixels in the exact signed APK."""
import argparse
import hashlib
import io
import json
from zipfile import ZipFile

from PIL import Image

CASES = ("light","dark","flat","nonmetal")
SIDE = 256


def sha(data):
    return hashlib.sha256(data).hexdigest()


def audit(owner_zip, apk):
    with ZipFile(owner_zip) as logs, ZipFile(apk) as package:
        entries = logs.infolist()
        names = {entry.filename for entry in entries}
        if len(entries) != len(names) or "summary.json" not in names or any(e.file_size > 512*1024 for e in entries):
            raise ValueError("Unexpected Forward export archive")
        report = json.loads(logs.read("summary.json"))
        if report["experiment"] != "GFX120" or report["phase_closed"] is not False:
            raise ValueError("Wrong Forward probe")
        if report.get("original_forward_draw_completed") is not True:
            return {"experiment":"GFX120","draw_completed":False,
                    "error":report.get("error","Incomplete export"),"phase_closed":False}
        if names != {"summary.json", *(name+".png" for name in CASES)}:
            raise ValueError("Missing Forward readback")
        if report["bound_cb_blocks"] != 8 or report["bound_samplers"] != 7:
            raise ValueError("Incomplete shader resource binding")
        if [row["name"] for row in report["captures"]] != list(CASES):
            raise ValueError("Wrong Forward cases")
        captures = {}
        safe = {}
        for row in report["captures"]:
            name = row["name"]
            filename = name+".png"
            image = logs.read(filename)
            reference = package.read(f"assets/{name}.rgba")
            if (row["image"] != filename or sha(image) != row["image_sha256"]
                    or sha(reference) != row["mesa_rgba_sha256"] or len(reference) != SIDE*SIDE*4):
                raise ValueError("Capture or Mesa reference identity mismatch")
            with Image.open(io.BytesIO(image)) as png:
                if png.format != "PNG" or png.size != (SIDE,SIDE):
                    raise ValueError("Unexpected Forward PNG shape")
                rgba = png.convert("RGBA").transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes()
            if sha(rgba) != row["raw_rgba_sha256"] or set(rgba[3::4]) != {0,255}:
                raise ValueError("Unexpected decoded readback bytes")
            captures[name] = rgba
            coverage = rgba[3::4].count(255)
            changes = sum(a!=b for a,b in zip(rgba[3::4],reference[3::4],strict=True))
            errors = [abs(rgba[i+k]-reference[i+k])
                      for i in range(0,len(rgba),4) if rgba[i+3]==reference[i+3]==255
                      for k in range(3)]
            computed = dict(covered_pixels=coverage,coverage_different_pixels=changes,
                            rgb_channels=len(errors),rgb_absolute_error_sum=sum(errors),
                            max_rgb_channel_error=max(errors,default=0))
            if any(row[key]!=value for key,value in computed.items()) or not errors:
                raise ValueError("Recomputed Forward counters disagree")
            safe[name] = {**computed,"mean_rgb_channel_error":sum(errors)/len(errors)}
    baseline = captures["light"]
    controls = {name:sum(baseline[i:i+3]!=captures[name][i:i+3] for i in range(0,len(baseline),4))
                for name in CASES[1:]}
    return {"experiment":"GFX120","renderer":report["renderer"],"gles":report["gles"],
            "draw_completed":True,"captures":safe,"control_rgb_changed_pixels":controls,
            "controls_responded":all(v>100 for v in controls.values()),
            "original_game_pixel_parity":False,"phase_closed":False}


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("signed_apk")
    args=parser.parse_args()
    print(json.dumps(audit(args.owner_zip,args.signed_apk),indent=2))
