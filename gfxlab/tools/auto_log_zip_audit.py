#!/usr/bin/env python3
"""Parse owner GFX-MULTI-031 exported multi-session ZIP; publish safe aggregates.

The owner keeps raw error messages/stacks and private device paths inside ZIP.
The public report emits only counts, coverage and fail-closed proof flags.
"""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
from zipfile import ZipFile

MAX_ENTRIES=20000
MAX_UNCOMPRESSED=900*1024*1024
MAX_RECORDS=2_000_000
MAX_LINE_BYTES=16*1024*1024
MODELS={f"M{i:02}" for i in range(6)}
ROLES={"BASECOLOR","NORMAL","METALLIC"}
CHANNELS={"RGB","R","G","B","A"}
SAMPLING={"SOURCE_TEXTURE_COLORSPACE_IMPORT","FORCE_LINEAR_IMPORT"}

def parse_snapshot(obj):
    if not isinstance(obj,dict) or obj.get("kind")!="state_snapshot":
        raise ValueError("NOT_A_GFXLAB_AUTO_STATE_SNAPSHOT")
    raw=obj.get("stateJson")
    if not isinstance(raw,str):
        raise ValueError("AUTO_STATE_JSON_MISSING")
    d=json.loads(raw)
    if not isinstance(d,dict) or d.get("experiment")!="GFX-MULTI-031":
        raise ValueError("AUTO_STATE_EXPERIMENT_MISMATCH")
    if d.get("modelId") not in MODELS:
        raise ValueError("AUTO_STATE_MODEL_NOT_IN_SIX")
    if d.get("diagnosticRole") not in ROLES:
        raise ValueError("AUTO_STATE_ROLE_INVALID")
    if d.get("diagnosticChannel") not in CHANNELS:
        raise ValueError("AUTO_STATE_CHANNEL_INVALID")
    if d.get("diagnosticSampling") not in SAMPLING:
        raise ValueError("AUTO_STATE_SAMPLING_INVALID")
    if type(d.get("diagnosticMaterialSurface")) is not int or d["diagnosticMaterialSurface"]<0:
        raise ValueError("AUTO_STATE_SURFACE_INVALID")
    if type(d.get("originalShaderRestored")) is not bool:
        raise ValueError("AUTO_STATE_ORIGINAL_SHADER_FLAG_MISSING")
    return d

def analyze(path):
    if not path.is_file() or path.stat().st_size>MAX_UNCOMPRESSED:
        raise ValueError("AUTO_ZIP_INVALID_SIZE")
    with ZipFile(path) as zipfile:
        entries=[e for e in zipfile.infolist() if not e.is_dir()]
        if len(entries)>MAX_ENTRIES or sum(e.file_size for e in entries)>MAX_UNCOMPRESSED:
            raise ValueError("AUTO_ZIP_EXCESSIVE_CONTENTS")
        for info in entries:
            name=info.filename
            if name.startswith("/") or "\\" in name or ".." in name.split("/"):
                raise ValueError("AUTO_ZIP_UNSAFE_ENTRY")
        if zipfile.testzip() is not None:
            raise ValueError("AUTO_ZIP_CRC_FAILURE")
        snaps=[x for x in entries if x.filename.startswith("sessions/") and x.filename.endswith("/snapshots.jsonl")]
        logs=[x for x in entries if x.filename.startswith("sessions/") and x.filename.endswith("/events.jsonl")]
        sums=[x for x in entries if x.filename.startswith("sessions/") and x.filename.endswith("/summary.json")]
        if not snaps or len(snaps)!=len(logs) or len(snaps)!=len(sums):
            raise ValueError("AUTO_ZIP_SESSION_FILE_SET_INVALID")
        def session_ids(infos,basename):
            out=set()
            for info in infos:
                parts=info.filename.split("/")
                if len(parts)!=3 or not parts[1] or parts[2]!=basename:
                    raise ValueError("AUTO_ZIP_SESSION_FILE_NAME_INVALID")
                if parts[1] in out:
                    raise ValueError("AUTO_ZIP_DUPLICATE_SESSION_ENTRY")
                out.add(parts[1])
            return out
        if (session_ids(snaps,"snapshots.jsonl")!=session_ids(logs,"events.jsonl")
                or session_ids(snaps,"snapshots.jsonl")!=session_ids(sums,"summary.json")):
            raise ValueError("AUTO_ZIP_SESSION_FILE_SET_MISMATCH")
        models=Counter()
        roles=Counter()
        channels=Counter()
        samplings=Counter()
        reasons=Counter()
        modes=Counter()
        surfaces=Counter()
        model_modes=defaultdict(set)
        model_roles=defaultdict(set)
        model_channels=defaultdict(set)
        model_samplings=defaultdict(set)
        m03_second_surface=False
        errors=Counter()
        full_stacks=0
        last_reports=0
        event_total=0
        test_count=0
        session_failures=0
        dropped=0
        for info in sums:
            summary=json.loads(zipfile.read(info))
            if summary.get("schema")!="gfxlab-session-v1":
                raise ValueError("AUTO_ZIP_SESSION_SCHEMA_INVALID")
            dropped+=int(summary.get("messagesDropped",0))
            session_failures+=int(bool(summary.get("writeFailure")))
        for info in snaps:
            with zipfile.open(info) as reader:
                for line in reader:
                    if len(line)>MAX_LINE_BYTES:raise ValueError("AUTO_SNAPSHOT_TOO_LARGE")
                    if not line.strip():continue
                    row=json.loads(line)
                    data=parse_snapshot(row)
                    test_count+=1
                    if test_count>MAX_RECORDS:raise ValueError("AUTO_SNAPSHOT_RECORD_LIMIT")
                    models[data["modelId"]]+=1
                    roles[data["diagnosticRole"]]+=1
                    channels[data["diagnosticChannel"]]+=1
                    samplings[data["diagnosticSampling"]]+=1
                    modes[str(data.get("materialMode","unknown"))]+=1
                    surfaces[str(data["diagnosticMaterialSurface"])]+=1
                    model_modes[data["modelId"]].add(str(data.get("materialMode","unknown")))
                    model_roles[data["modelId"]].add(data["diagnosticRole"])
                    model_channels[data["modelId"]].add(data["diagnosticChannel"])
                    model_samplings[data["modelId"]].add(data["diagnosticSampling"])
                    if data["modelId"]=="M03" and data["diagnosticMaterialSurface"]==1:
                        m03_second_surface=True
                    reasons[str(row.get("message","unknown"))]+=1
                    last_reports+=int(not data.get("originalShaderRestored",False))
        for info in logs:
            with zipfile.open(info) as reader:
                for line in reader:
                    if len(line)>MAX_LINE_BYTES:raise ValueError("AUTO_EVENT_TOO_LARGE")
                    if not line.strip():continue
                    row=json.loads(line)
                    if not isinstance(row,dict) or not isinstance(row.get("kind"),str):
                        raise ValueError("AUTO_EVENT_INVALID")
                    event_total+=1
                    if event_total>MAX_RECORDS:raise ValueError("AUTO_EVENT_RECORD_LIMIT")
                    kind=row["kind"]
                    if kind in ("unity_Error","unity_Exception","unity_Assert","unity_Warning"):
                        errors[kind]+=1
                        full_stacks+=int(bool(row.get("stackTrace","")))
        return {
           "experiment":"GFX-MULTI-031-OWNER-AGGREGATE",
           "session_count":len(snaps),
           "snapshot_count":test_count,
           "event_count":event_total,
           "all_six_models_covered":set(models)==MODELS,
           "model_snapshots":dict(sorted(models.items())),
           "mode_snapshot_counts":dict(modes),
           "model_mode_coverage":{k:sorted(model_modes[k]) for k in sorted(models)},
           "model_role_coverage":{k:sorted(model_roles[k]) for k in sorted(models)},
           "model_channel_coverage":{k:sorted(model_channels[k]) for k in sorted(models)},
           "model_sampling_coverage":{k:sorted(model_samplings[k]) for k in sorted(models)},
           "all_six_models_four_modes_covered":all(
               model_modes[m]=={"WHITE_LIT","WHITE_UNLIT","SOURCE_ALBEDO_STANDARD",
                                "SOURCE_PBR_STANDARD_APPROX"} for m in MODELS),
           "original_shader_device_parity_coverage":False,
           "role_counts":dict(roles),
           "channel_counts":dict(channels),
           "sampling_counts":dict(samplings),
           "surface_counts":dict(surfaces),
           "state_transition_reasons":dict(reasons),
           "unity_message_type_counts":dict(errors),
           "unity_error_warning_messages_with_stack_text":full_stacks,
           "message_queue_dropped_total":dropped,
           "session_write_failures":session_failures,
           "all_state_original_shader_flags_false":last_reports==test_count,
           "all_roles_tested":set(roles)==ROLES,
           "all_channels_tested":set(channels)==CHANNELS,
           "both_sampling_settings_tested":set(samplings)==SAMPLING,
           "m03_second_material_tested":m03_second_surface,
           "raw_unity_error_messages_exported_to_report":False,
           "raw_device_paths_or_shaders_exported_to_report":False,
           "original_shader48_restored":False,
           "source_vs_pc_gpu_pixel_parity_verified":False
        }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    args=p.parse_args()
    result=analyze(args.archive)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI031_SAFE_OWNER_TEST_MATRIX "+json.dumps(result,sort_keys=True))
if __name__=="__main__":
    main()
