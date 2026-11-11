#!/usr/bin/env python3
"""GFX101 private owner Android GPU ZIP auditor. Only safe counts exported.

This parser does NOT assume original Raft shaders, animations or PC pixels.
It rejects false native NoPerspective success when optional GLES extension,
successful controls, or actual GPU readback evidence are missing.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile, BadZipFile

MODES=("Smooth","Flat","AffineEmulated","NativeNoPerspective")
STATUS={
    "CONTROL_FAILURE_OR_INCONCLUSIVE",
    "NATIVE_EXTENSION_NOT_ADVERTISED",
    "NATIVE_EXTENSION_ADVERTISED_BUT_SHADER_COMPILE_OR_LINK_FAILED",
    "NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE",
    "NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH",
    "NATIVE_GPU_UNEXPECTED_INTERPOLATION",
}
LIMIT_ENTRIES=64
LIMIT_UNCOMPRESSED=64*1024*1024
MAX_JSON=1024*1024
PNG_MAGIC=b"\x89PNG\r\n\x1a\n"

def _read_json(z,name):
    info=z.getinfo(name)
    if info.file_size>MAX_JSON:
        raise ValueError("JSON_TOO_LARGE")
    try: return json.loads(z.read(info).decode("utf-8","strict"))
    except (ValueError,UnicodeError):
        raise ValueError("JSON_INVALID") from None

def audit(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>LIMIT_UNCOMPRESSED:
        raise ValueError("ZIP_MISSING_OR_TOO_LARGE")
    with p.open("rb") as fp:
        source_sha=hashlib.file_digest(fp,"sha256").hexdigest()
    with ZipFile(p) as z:
        info=z.infolist()
        names=[f.filename for f in info]
        if len(info)>LIMIT_ENTRIES or len(names)!=len(set(names)):
            raise ValueError("ZIP_ENTRIES_INVALID")
        if sum(f.file_size for f in info)>LIMIT_UNCOMPRESSED:
            raise ValueError("ZIP_UNCOMPRESSED_TOO_LARGE")
        if any(n.startswith("/") or ".." in n.split("/") or "\\" in n for n in names):
            raise ValueError("ZIP_PATH_INVALID")
        if z.testzip() is not None:
            raise ValueError("ZIP_CRC_INVALID")
        if not {"summary.json","events.jsonl","LIMITS.txt"}.issubset(names):
            raise ValueError("ZIP_REQUIRED_FILES_MISSING")
        summary=_read_json(z,"summary.json")
        for flag in ("originalShaderRestored","originalRaftShaderBytecodeUsed",
                     "originalAnimationRestored","pcAdrenoPixelParityVerified","phase_closed"):
            if summary.get(flag) is not False:
                raise ValueError("FALSE_ORIGINAL_SOURCE_PROOF_"+flag)
        if summary.get("experiment")!="GFX-MULTI-101":
            raise ValueError("EXPERIMENT_IDENTITY_MISMATCH")
        ext=summary.get("nv_noperspective_extension_advertised")
        controls=summary.get("control_smooth_matches_cpu") and summary.get(
            "control_affine_emulated_matches_cpu")
        native=summary.get("native_extension_shader_compiled_and_linked")
        native_match=summary.get("native_gpu_matches_cpu_affine")
        native_smooth=summary.get("native_gpu_matches_cpu_smooth_only")
        diagnostic=summary.get("diagnostic_status")
        if any(type(x) is not bool for x in (ext,native,native_match,native_smooth)):
            raise ValueError("GPU_EVIDENCE_BOOLEAN_MISSING")
        if diagnostic not in STATUS:
            raise ValueError("GPU_STATUS_INVALID")
        if type(summary.get("gpu_readbacks")) is not int:
            raise ValueError("GPU_READBACK_COUNT_INVALID")
        if not 0<=summary["gpu_readbacks"]<=4:
            raise ValueError("GPU_READBACK_COUNT_OUT_OF_RANGE")
        if (diagnostic=="NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE"
                and not (ext and controls and native and native_match
                         and summary["gpu_readbacks"]==4)):
            raise ValueError("NATIVE_SUCCESS_LACKS_REQUIRED_GPU_EVIDENCE")
        if not ext and (native or native_match or native_smooth
                        or diagnostic.startswith("NATIVE_NV_")):
            raise ValueError("UNADVERTISED_EXTENSION_CANNOT_PROVE_NATIVE")
        if diagnostic=="NATIVE_EXTENSION_NOT_ADVERTISED" and ext:
            raise ValueError("STATUS_EXTENSION_CONTRADICTION")
        results=summary.get("results")
        if not isinstance(results,list) or len(results)!=summary["gpu_readbacks"]:
            raise ValueError("GPU_RESULT_COUNT_MISMATCH")
        mode_set=set()
        for row in results:
            if not isinstance(row,dict) or row.get("mode") not in MODES:
                raise ValueError("INVALID_GPU_CASE")
            mode=row["mode"]
            if mode in mode_set:raise ValueError("DUPLICATE_GPU_CASE")
            mode_set.add(mode)
            if row.get("gpu_readback") is not True:
                raise ValueError("GPU_READBACK_PROOF_MISSING")
            for key in ("cpu_smooth_mad","cpu_affine_mad"):
                value=row.get(key)
                if type(value) not in (int,float) or not (0<=value<=1):
                    raise ValueError("INVALID_CPU_ERROR_METRIC")
            filename=row.get("png_filename")
            if filename != "gpu-"+mode+".png":
                raise ValueError("GPU_PNG_WRONG_NAME")
            entry="captures/"+filename
            if entry not in names:
                raise ValueError("GPU_PNG_NOT_FOUND")
            raw=z.read(entry)
            if len(raw)<33 or raw[:8]!=PNG_MAGIC or raw[12:16]!=b"IHDR":
                raise ValueError("GPU_PNG_HEADER_INVALID")
            if int.from_bytes(raw[16:20],"big")!=256 or int.from_bytes(raw[20:24],"big")!=256:
                raise ValueError("GPU_PNG_DIMENSIONS_INVALID")
            if hashlib.sha256(raw).hexdigest()!=row.get("png_sha256"):
                raise ValueError("GPU_PNG_HASH_MISMATCH")
        # Event lines are count/identity-checked, never exported or quoted.
        log_info=z.getinfo("events.jsonl")
        if log_info.file_size>8*1024*1024:
            raise ValueError("EVENT_LOG_TOO_LARGE")
        lines=z.read(log_info).decode("utf-8","strict").splitlines()
        events=[json.loads(line) for line in lines if line.strip()]
        count_readbacks=sum(e.get("event")=="gpu_readback" for e in events)
        if count_readbacks!=summary["gpu_readbacks"]:
            raise ValueError("GPU_EVENT_COUNT_MISMATCH")
        if not any(e.get("event")=="environment" for e in events):
            raise ValueError("GPU_ENVIRONMENT_EVENT_MISSING")
        return {
            "schema":"gfxlab-101-owner-safe-audit-v1",
            "archive_sha256":source_sha,
            "zip_crc_pass":True,
            "experiment":"GFX-MULTI-101",
            "gpu_readbacks":summary["gpu_readbacks"],
            "gpu_capture_png_sha_verified":len(mode_set),
            "supported_optional_extension":ext,
            "native_qualifier_compile_link_success":native,
            "smooth_cpu_reference_pass":summary.get("control_smooth_matches_cpu") is True,
            "affine_cpu_reference_pass":summary.get("control_affine_emulated_matches_cpu") is True,
            "native_gpu_affine_parity":native_match,
            "diagnostic_status":diagnostic,
            "original_shader_restored":False,
            "phase_closed":False,
        }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("archive")
    args=p.parse_args()
    try:
        result=audit(args.archive)
    except (OSError, ValueError, KeyError, BadZipFile) as exc:
        print("GFX101_AUDIT_FAILED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
