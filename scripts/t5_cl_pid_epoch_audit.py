#!/usr/bin/env python3
"""T5: reject cross-process aggregation of LogRaft presentation telemetry.

A single LogRaft session can contain multiple Raft process lifetimes. Never
compute one gameplay FPS cohort across a verified PID transition. This guard
returns only counts and opaque epoch indices, not PIDs or device data.
"""
from __future__ import annotations

from scripts.t5_cl_fps_cohort_gate import _fresh_fps, _is_int, analyze


def split_verified_pid_epochs(rows):
    """Split at every verified running PID change; reject unknown boundaries."""
    if not rows:
        raise ValueError("Empty LogRaft session")
    epochs = []
    current = []
    pid = None
    for row in rows:
        verified = (row.get("state") == "game_running"
                    and row.get("pid_probe_status") == "main_pid_verified"
                    and _is_int(row.get("pid")))
        if verified:
            new_pid = row["pid"]
            if pid is not None and new_pid != pid:
                if current:
                    epochs.append(current)
                current = []
            pid = new_pid
        elif (row.get("state") == "game_process_state_unknown"
              and pid is None and not epochs):
            # Before the first observed verified process, LogRaft may emit
            # unknown startup probes. They are not evidence of a stop/restart.
            # Keep them in the initial cohort; they cannot contribute FPS.
            current.append(row)
            continue
        elif row.get("state") != "game_running":
            # A stopped process is a lifetime boundary, even if Android
            # later reuses its numeric PID. Do not combine FPS across it.
            if current:
                epochs.append(current)
            epochs.append([row])
            current = []
            pid = None
            continue
        elif row.get("state") == "game_running":
            # Unknown running-process ownership is its OWN epoch, neither
            # part of the preceding verified Raft PID nor part of a later
            # re-verified PID (even if the numeric PID is reused). Do not
            # ever publish the actual PID to a report.
            if current:
                epochs.append(current)
            epochs.append([row])
            current = []
            pid = None
            continue
        current.append(row)
    if current:
        epochs.append(current)
    return epochs


def audit(rows):
    epochs = split_verified_pid_epochs(rows)
    summaries = []
    for index, epoch in enumerate(epochs, 1):
        verified_fresh = [r for r in epoch if _fresh_fps(r)]
        summaries.append({
            "epoch_index": index,
            "samples": len(epoch),
            "fresh_presentation_samples": len(verified_fresh),
            "single_verified_process_epoch": bool(verified_fresh) and all(
                r.get("pid_probe_status") == "main_pid_verified"
                and r.get("pid") == verified_fresh[0]["pid"]
                for r in epoch if r.get("state") == "game_running"),
        })
    return {
        "process_epoch_count": len(epochs),
        "safe_to_aggregate_entire_session": len(epochs) == 1 and summaries[0]["single_verified_process_epoch"],
        "epochs": summaries,
        "no_pid_values_published": True,
        "no_cross_epoch_fps_comparison": True,
    }
