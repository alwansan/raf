#!/usr/bin/env python3
"""Safe, fail-closed owner Android GFX102 test ZIP validation.

Keeps all captured pixels, device identifiers, GLSL logs, and event text local.
Only anonymous GLSL ES 300/310/320 compilation + GPU correctness summaries
are safe to publish. No claim about original Raft Shader48 or full-game pixels.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile, BadZipFile

MODES=("Smooth","Flat","AffineEmulated","NativeNoPerspectiveES300",
       "NativeNoPerspectiveES310","NativeNoPerspectiveES320")
VERSIONS=(300,310,320)
STATUS={
    "CONTROL_FAILURE_OR_INCONCLUSIVE",
    "NATIVE_EXTENSION_NOT_ADVERTISED",
    "NATIVE_EXTENSION_ADVERTISED_BUT_ALL_GLSL_VERSIONS_FAILED",
    "NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE",
    "NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH",
    "NATIVE_GPU_UNEXPECTED_INTERPOLATION",
}
PNG_MAGIC=b"\x89PNG\r\n\x1a\n"

def audit(path):
    p=Path(path)
    if not p.is_file() or p.stat().st_size>96*1024*1024:
        raise ValueError("ZIP_MISSING_OR_TOO_LARGE")
    with p.open("rb") as fp:
        sha=hashlib.file_digest(fp,"sha256").hexdigest()
    with ZipFile(p) as z:
        entries=z.infolist()
        names=[e.filename for e in entries]
        if len(entries)>128 or len(names)!=len(set(names)):
            raise ValueError("ZIP_DUPLICATE_OR_TOO_MANY_ENTRIES")
        if sum(e.file_size for e in entries)>96*1024*1024:
            raise ValueError("ZIP_UNCOMPRESSED_TOO_LARGE")
        if any(n.startswith("/") or "\\" in n or ".." in n.split("/") for n in names):
            raise ValueError("ZIP_UNSAFE_PATH")
        if z.testzip() is not None:
            raise ValueError("ZIP_CRC_FAILED")
        for name in ("summary.json","events.jsonl","LIMITS.txt"):
            if name not in names:
                raise ValueError("REQUIRED_FILE_MISSING")
        if z.getinfo("summary.json").file_size>2*1024*1024:
            raise ValueError("SUMMARY_TOO_LARGE")
        summary=json.loads(z.read("summary.json").decode("utf-8","strict"))
        if summary.get("experiment")!="GFX-MULTI-102":
            raise ValueError("EXPERIMENT_MISMATCH")
        for key in ("originalShaderRestored","originalRaftShaderBytecodeUsed",
                    "originalAnimationRestored","pcAdrenoPixelParityVerified",
                    "phase_closed"):
            if summary.get(key) is not False:
                raise ValueError("UNSAFE_ORIGINAL_SOURCE_SUCCESS_FLAG_"+key)
        ext=summary.get("nv_noperspective_extension_advertised")
        if type(ext) is not bool:
            raise ValueError("EXTENSION_BOOLEAN_INVALID")
        n=summary.get("gpu_readbacks")
        if type(n) is not int or not 0<=n<=6:
            raise ValueError("READBACK_COUNT_INVALID")
        status=summary.get("diagnostic_status")
        if status not in STATUS:
            raise ValueError("DIAGNOSTIC_STATUS_INVALID")
        controls=[summary.get(k) is True for k in (
            "control_smooth_matches_cpu","control_flat_stable",
            "control_affine_emulated_matches_cpu")]
        native_compiled=summary.get("native_extension_shader_compiled_and_linked")
        native_affine=summary.get("native_gpu_matches_cpu_affine")
        native_smooth=summary.get("native_gpu_matches_cpu_smooth_only")
        if any(type(x) is not bool for x in (native_compiled,native_affine,native_smooth)):
            raise ValueError("NATIVE_GPU_BOOLEAN_INVALID")
        trials=summary.get("native_glsl_version_trials")
        if not isinstance(trials,list) or len(trials)!=3:
            raise ValueError("EXACTLY_THREE_VERSION_ATTEMPTS_REQUIRED")
        by_version={}
        for trial in trials:
            if not isinstance(trial,dict):
                raise ValueError("TRIAL_INVALID")
            version=trial.get("glsl_es_version")
            available=trial.get("gpu_readback")
            if type(version) is not int or version not in VERSIONS or version in by_version:
                raise ValueError("TRIAL_VERSION_INVALID_OR_DUPLICATE")
            if type(available) is not bool:
                raise ValueError("TRIAL_GPU_BOOLEAN_INVALID")
            by_version[version]=available
        if set(by_version)!=set(VERSIONS):
            raise ValueError("TRIAL_VERSION_SET_INCOMPLETE")
        best=summary.get("native_best_glsl_es_version")
        if type(best) is not int or best not in (-1,300,310,320):
            raise ValueError("BEST_VERSION_INVALID")
        if not ext and any(by_version.values()):
            raise ValueError("GPU_NATIVE_WITHOUT_ADVERTISED_EXTENSION")
        if native_compiled != any(by_version.values()):
            raise ValueError("NATIVE_COMPILE_AND_VERSION_TRIAL_MISMATCH")
        if best==-1 and native_compiled or best!=-1 and not by_version.get(best,False):
            raise ValueError("BEST_VERSION_MISMATCH")
        results=summary.get("results")
        if not isinstance(results,list) or len(results)!=n:
            raise ValueError("RESULT_COUNT_MISMATCH")
        by_mode={}
        for result in results:
            if not isinstance(result,dict):
                raise ValueError("RESULT_ROW_INVALID")
            mode=result.get("mode")
            if mode not in MODES or mode in by_mode:
                raise ValueError("RESULT_MODE_INVALID_OR_DUPLICATE")
            if result.get("gpu_readback") is not True:
                raise ValueError("RESULT_NOT_GPU_READBACK")
            for key in ("cpu_affine_mad","cpu_smooth_mad"):
                value=result.get(key)
                if type(value) not in (int,float) or not 0<=value<=1:
                    raise ValueError("CPU_ERROR_OUT_OF_RANGE")
            filename="gpu-"+mode+".png"
            if result.get("png_filename")!=filename:
                raise ValueError("RESULT_FILENAME_MISMATCH")
            key="captures/"+filename
            if key not in names:
                raise ValueError("RESULT_PNG_MISSING")
            b=z.read(key)
            if (len(b)<33 or not b.startswith(PNG_MAGIC) or b[12:16]!=b"IHDR"
                 or int.from_bytes(b[16:20],"big")!=256
                 or int.from_bytes(b[20:24],"big")!=256
                 or hashlib.sha256(b).hexdigest()!=result.get("png_sha256")):
                raise ValueError("RESULT_PNG_INTEGRITY_FAILURE")
            by_mode[mode]=result
        if not set(MODES[:3]) <= set(by_mode) and status!="CONTROL_FAILURE_OR_INCONCLUSIVE":
            raise ValueError("THREE_GPU_CONTROLS_MISSING")
        for version in VERSIONS:
            if ("NativeNoPerspectiveES"+str(version) in by_mode)!=by_version[version]:
                raise ValueError("TRIAL_READBACK_PNG_MISMATCH")
        if status=="NATIVE_EXTENSION_NOT_ADVERTISED" and ext:
            raise ValueError("STATUS_EXTENSION_CONTRADICTION")
        if status=="NATIVE_EXTENSION_ADVERTISED_BUT_ALL_GLSL_VERSIONS_FAILED" and (
                not ext or native_compiled):
            raise ValueError("STATUS_ALL_FAILED_CONTRADICTION")
        if status=="NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE" and not (
                ext and all(controls) and native_compiled and native_affine
                and best in VERSIONS and n>=4):
            raise ValueError("FORGED_NATIVE_SUCCESS")
        if not ext and native_affine:
            raise ValueError("NATIVE_AFFINE_WITHOUT_EXTENSION")
        if z.getinfo("events.jsonl").file_size>12*1024*1024:
            raise ValueError("EVENTS_TOO_LARGE")
        events=[json.loads(line) for line in z.read("events.jsonl").decode("utf-8","strict").splitlines()
                if line.strip()]
        if sum(e.get("event")=="gpu_readback" for e in events)!=n:
            raise ValueError("EVENT_GPU_READBACK_MISMATCH")
        if not any(e.get("event")=="environment" for e in events):
            raise ValueError("MISSING_GL_CONTEXT_ENVIRONMENT_EVENT")
        return {
            "experiment":"GFX-MULTI-102",
            "archive_sha256":sha,
            "zip_crc_pass":True,
            "gpu_capture_hashes_verified":len(by_mode),
            "device_extension_advertised":ext,
            "glsl_versions_tried":list(VERSIONS),
            "native_gpu_readback_by_glsl_version":{
                str(v):bool(by_version[v]) for v in VERSIONS},
            "best_native_glsl_version":best,
            "controls_passed":all(controls),
            "native_gpu_affine_parity":native_affine,
            "diagnostic_status":status,
            "original_shader_restored":False,
            "pc_device_pixel_parity":False,
            "phase_closed":False
        }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    ns=parser.parse_args()
    try:
        data=audit(ns.owner_zip)
    except (OSError,KeyError,ValueError,BadZipFile) as e:
        print("GFX102_OWNER_ZIP_AUDIT_FAILED: "+str(e),file=sys.stderr)
        return 2
    print(json.dumps(data,sort_keys=True,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
