"""Validate GFX116 texture sample coverage and bind it to the delivered APK."""
import argparse
import hashlib
import json
from zipfile import ZipFile

ROLES = {"basecolor":True,"normal":False,"metallic":True}


def audit(archive, apk):
    with ZipFile(archive) as logs, ZipFile(apk) as package:
        entries = logs.infolist()
        if len(entries) != 1 or entries[0].filename != "summary.json" or entries[0].file_size > 32*1024:
            raise ValueError("Unexpected texture report archive")
        data = json.loads(logs.read("summary.json"))
        if (data["experiment"] != "GFX116" or data["phase_closed"] is not False
                or not data["renderer"] or not data["gles"]):
            raise ValueError("Unexpected GLES report")
        if "error" in data:
            return {"experiment":"GFX116","renderer":data["renderer"],"error":data["error"],
                    "phase_closed":False}
        roles = data["roles"]
        if [r["role"] for r in roles] != list(ROLES):
            raise ValueError("Missing or reordered M02 texture roles")
        result = {}
        native_count = 0
        for role in roles:
            name = role["role"]
            if role["srgb"] is not ROLES[name]:
                raise ValueError("Unexpected texture color space")
            for suffix in ("bc3","rgba"):
                raw = package.read(f"assets/{name}.{suffix}")
                if hashlib.sha256(raw).hexdigest() != role[suffix+"_sha256"]:
                    raise ValueError("Texture payload hash mismatch")
            result[name] = {}
            for key, mode in (("native","native_bc3"),("fallback","decoded_rgba")):
                row = role[key]
                if row["mode"] != mode:
                    raise ValueError("Unexpected sampling mode")
                if row["status"] == "NATIVE_FORMAT_REJECTED" and key == "native":
                    if row["gl_error"] not in (0x0500,0x0502):
                        raise ValueError("Unexpected compressed upload rejection code")
                    result[name][key] = {"status":row["status"],"gl_error":row["gl_error"]}
                    continue
                if row["status"] != "SAMPLED":
                    raise ValueError("Unexpected sampling status")
                mips = row["mips"]
                if [r["level"] for r in mips] != list(range(11)):
                    raise ValueError("Incomplete mip coverage")
                for level, mip in enumerate(mips):
                    count = (1024 >> level)**2
                    max_error = mip["max_channel_error"]
                    error_sum = mip["channel_absolute_error_sum"]
                    over_two = mip["channels_over_two"]
                    if (mip["texels"] != count or any(type(v) is not int for v in (max_error,error_sum,over_two))
                        or not 0 <= max_error <= 255 or not max_error <= error_sum <= max_error*count*4
                        or not 0 <= over_two <= count*4 or 3*over_two > error_sum
                        or bool(over_two) != (max_error > 2)):
                        raise ValueError("Invalid mip statistics")
                result[name][key] = {"status":"SAMPLED","mips":len(mips),
                    "texels":sum(r["texels"] for r in mips),
                    "max_channel_error":max(r["max_channel_error"] for r in mips),
                    "channels_over_two":sum(r["channels_over_two"] for r in mips),
                    "channel_absolute_error_sum":sum(r["channel_absolute_error_sum"] for r in mips)}
                native_count += key == "native"
        if data["native_roles_sampled"] != native_count:
            raise ValueError("Inconsistent native role count")
        return {"experiment":"GFX116","renderer":data["renderer"],"gles":data["gles"],
                "native_roles_sampled":native_count,"roles":result,"phase_closed":False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("signed_apk")
    args = parser.parse_args()
    print(json.dumps(audit(args.owner_zip,args.signed_apk),indent=2))
