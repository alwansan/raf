#!/usr/bin/env python3
"""GFX-OWNER-001: fail-closed private owner Android ZIP evidence aggregate census.

Never publishes screenshot pixel bytes, UnityShaderCache binary programs,
IL2CPP metadata, device serial, raw logs, original Shader text or asset pointers.
A successful COPY LOG != proof original Shader48 ran on Adreno.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

EXPECTED_MODELS=tuple("M%02d"%i for i in range(6))
REQUIRED_FIELDS=("experiment","modelId","materialMode","gfxDevice","gfxApi",
                 "unityVersion","originalShaderRestored","originalAnimationRestored",
                 "coloredPixelsAutomaticallyVerified","errors","firstError",
                 "diagnosticRole","diagnosticChannel","diagnosticSampling",
                 "diagnosticProbeStatus")
MAX_ARCHIVE_ENTRIES=400
MAX_UNCOMPRESSED_BYTES=160*1024*1024

def parse_json_stream(text):
    decoder=json.JSONDecoder()
    pos=0
    rows=[]
    while pos<len(text):
        while pos<len(text) and text[pos].isspace():
            pos+=1
        if pos>=len(text):break
        row,consumed=decoder.raw_decode(text,pos)
        if not isinstance(row,dict):
            raise ValueError("OWNER_COPY_LOG_ROW_NOT_OBJECT")
        rows.append(row)
        pos=consumed
    if not rows:raise ValueError("OWNER_COPY_LOG_NO_JSON_RECORDS")
    return rows

def census_reports(reports,latest,images,cache):
    if not isinstance(reports,list) or not reports or not isinstance(latest,dict):
        raise ValueError("OWNER_REPORT_STRUCTURE_INVALID")
    models=Counter()
    modes=Counter()
    role_samples=Counter()
    channel_samples=Counter()
    sampling_samples=Counter()
    surface_samples=Counter()
    claim=Counter()
    errors=0
    for d in reports:
        if any(k not in d for k in REQUIRED_FIELDS):
            raise ValueError("OWNER_COPY_LOG_SCHEMA_INCOMPLETE")
        if d["experiment"]!="GFX-MULTI-026":
            raise ValueError("OWNER_GFX_RUN_IDENTITY_MISMATCH")
        if d["modelId"] not in EXPECTED_MODELS:
            raise ValueError("OWNER_MODEL_ID_OUTSIDE_SELECTED_SET")
        if type(d["errors"]) is not int or not 0<=d["errors"]<=1_000_000:
            raise ValueError("OWNER_ERROR_COUNTER_INVALID")
        if type(d["originalShaderRestored"]) is not bool:
            raise ValueError("OWNER_ORIGINAL_SHADER_FLAG_INVALID")
        models[d["modelId"]]+=1
        modes[d["modelId"]+"|"+str(d["materialMode"])]+=1
        role_samples[str(d["diagnosticRole"])]+=1
        channel_samples[str(d["diagnosticChannel"])]+=1
        sampling_samples[str(d["diagnosticSampling"])]+=1
        surface_samples[str(d.get("diagnosticMaterialSurface","missing"))]+=1
        claim["original_shader_true"]+=int(d["originalShaderRestored"])
        claim["animation_true"]+=int(bool(d["originalAnimationRestored"]))
        claim["pixels_auto_verified_true"]+=int(bool(d["coloredPixelsAutomaticallyVerified"]))
        claim["probe_shader_supported"]+=int(bool(d.get("diagnosticShaderSupported")))
        claim["probe_texture_assigned"]+=int(bool(d.get("diagnosticTextureAssigned")))
        claim["first_error_nonempty"]+=int(bool(d["firstError"]))
        errors+=d["errors"]
    if any(k not in latest for k in REQUIRED_FIELDS) or latest["experiment"]!="GFX-MULTI-026":
        raise ValueError("OWNER_LAST_REPORT_INVALID")
    if latest["modelId"] not in EXPECTED_MODELS:
        raise ValueError("OWNER_LAST_MODEL_NOT_SELECTED")
    all_models=set(models)==set(EXPECTED_MODELS)
    each_albedo_and_pbr=all(any(m==key.split("|",1)[0] and key.split("|",1)[1]=="SOURCE_ALBEDO_STANDARD" for key in modes)
                            and any(m==key.split("|",1)[0] and key.split("|",1)[1]=="SOURCE_PBR_STANDARD_APPROX" for key in modes)
                            for m in EXPECTED_MODELS)
    fully_scoped_log=(set(role_samples)=={"BASECOLOR"} and
                      set(channel_samples)=={"RGB"} and
                      set(sampling_samples)=={"SOURCE_TEXTURE_COLORSPACE_IMPORT"} and
                      set(surface_samples)=={"0"})
    return {
      "experiment":"GFX-OWNER-001",
      "source_test_apk":"GFX-MULTI-026",
      "owner_json_snapshots":len(reports),
      "jpeg_screenshots":images,
      "compiled_device_shader_cache_files":cache,
      "models_with_copy_log":len(models),
      "all_six_models_logged":all_models,
      "albedo_and_standard_pbr_logged_for_each_model":each_albedo_and_pbr,
      "per_model_copy_log_count":dict(sorted(models.items())),
      "logged_material_mode_counts":dict(Counter(mode.rsplit("|",1)[1] for mode in modes.elements())),
      "logged_channel_role_counts":dict(role_samples),
      "logged_channel_component_counts":dict(channel_samples),
      "logged_channel_sampling_counts":dict(sampling_samples),
      "logged_material_surface_counts":dict(surface_samples),
      "all_copy_logs_only_basecolor_rgb_source_surface0":fully_scoped_log,
      "owner_errors_in_available_snapshots":errors,
      "nonempty_first_errors":claim["first_error_nonempty"],
      "probe_shader_supported_in_snapshots":claim["probe_shader_supported"],
      "probe_texture_assigned_in_snapshots":claim["probe_texture_assigned"],
      "original_shader_claims_true":claim["original_shader_true"],
      "original_animation_claims_true":claim["animation_true"],
      "automated_pixels_verified_claims_true":claim["pixels_auto_verified_true"],
      "last_report_model":latest["modelId"],
      "original_shader48_proven_on_adreno":False,
      "normal_metallic_individual_gpu_channels_linked_to_copy_log":not fully_scoped_log and bool(
          set(role_samples)&{"NORMAL","METALLIC"}
      ),
      "pixel_or_shader_binary_exported":False,
      "full_system_logcat_present":False,
      "source_gfxlab_shader_parity_gate_closed":False,
    }

def audit_archive(path):
    if not path.is_file() or path.stat().st_size>100*1024*1024:
        raise ValueError("OWNER_EVIDENCE_ARCHIVE_INVALID")
    with ZipFile(path) as z:
        files=[info for info in z.infolist() if not info.is_dir()]
        if len(files)>MAX_ARCHIVE_ENTRIES or sum(x.file_size for x in files)>MAX_UNCOMPRESSED_BYTES:
            raise ValueError("OWNER_EVIDENCE_ZIP_SIZE_LIMIT")
        for info in files:
            name=info.filename
            if name.startswith("/") or "\\" in name or any(x==".." for x in PurePosixPath(name).parts):
                raise ValueError("OWNER_EVIDENCE_ZIP_PATH_UNSAFE")
        if z.testzip() is not None:
            raise ValueError("OWNER_EVIDENCE_ZIP_CRC_MISMATCH")
        names=[f.filename for f in files]
        latest=[n for n in names if n.endswith("/files/gfxlab/multi-report.json")]
        logs=[n for n in names if n=="text 3.txt"]
        if len(latest)!=1 or len(logs)!=1:
            raise ValueError("OWNER_EVIDENCE_LOG_FILE_SET_INCOMPLETE")
        if any(z.getinfo(n).file_size>2*1024*1024 for n in latest+logs):
            raise ValueError("OWNER_EVIDENCE_JSON_EXCESSIVE_SIZE")
        shots=[n for n in names if n.startswith("img/") and n.lower().endswith((".jpg",".jpeg"))]
        for n in shots:
            i=z.getinfo(n)
            if i.file_size<1024 or i.file_size>10*1024*1024:
                raise ValueError("OWNER_SCREENSHOT_SIZE_INVALID")
            if not z.read(n)[:3]==bytes.fromhex("ffd8ff"):
                raise ValueError("OWNER_SCREENSHOT_MAGIC_INVALID")
        cache=[n for n in names if "/UnityShaderCache/" in n and not n.endswith("/version")]
        reports=parse_json_stream(z.read(logs[0]).decode("utf8"))
        last=json.loads(z.read(latest[0]).decode("utf8"))
        out=census_reports(reports,last,len(shots),len(cache))
    out["evidence_archive_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    out["archive_crc_verified"]=True
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    summary=audit_archive(a.archive)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("GFX_OWNER001_SAFE_EVIDENCE_COUNTS "+json.dumps(summary,sort_keys=True))
if __name__=="__main__":
    main()
