# T4 — Android physical mouse epoch correlation audit
session_id: 20261108T0737Z-T4-scheduled-epoch-telemetry-c9m4
origin: scheduled
branch: feature/android-native-port
base_sha: 6b9c3ef69146b0babb1a8e90424586ab02f9c8de
scope_commit: 3157c3bfe669772cb09c3c05ca6ddc0a7139bfa6
resumed_from_sessions: 20261108T0644Z-T4-scheduled-k7m2; 20261108T0540Z-T4-scheduled-ci-proof-v8m2
scope: prompt/coordination/work/INPUT-005/20261108T0737Z-T4-scheduled-epoch-telemetry-c9m4.json

## Device evidence and protected acceptance
Owner's 2026-11-05 artifact run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628: gameplay world entered, original .rgd saved, exit and reopen confirmed on POCO F5 Pro. Publishing packages failed but artifact was tested. CL pinned snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57 includes black system pointer, UI edge/system bars, and visual defects. This result is not a test of later physical pointer changes. Keep LOCAL-005 open and preserve FileManager/save loader, keyboard, touch, sound, Settings.

## New source-grounded finding
Read live android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs at the starting branch. The request path increments `epoch` and creates generation-bound `CapturedListener` each attempt; the probe uses a token and `captureViewIdentity`, and the release invalidates prior generations. But the bounded `physical_mouse_capture_requested` and `physical_mouse_capture_retry` log payloads do **not** include the generation token; `physical_mouse_relative` reports only cumulative event count and legacy-axis flag. Therefore a log with retries and a first movement cannot unambiguously attribute those observations to the same capture request generation. This is a *telemetry-correlation limitation*, not evidence of incorrect capture or lost mouse motion. Capture loss and view-change markers have different aggregation semantics. Avoid treating retry count as proof that Android granted capture.

Potential follow-up is a small Android-only diagnostic enhancement to add the generation number to request/retry/relative markers, with regression tests verifying that no new JNI or cursor state mutation occurs. Before modifying the shared runtime file, recheck concurrent T4 scopes and head; do not edit T5 controls/resolution. An actual phone build containing this telemetry is still required for acceptance. This session makes no source runtime changes and does not claim new phone evidence.

## CI and safety
At review, live branch HEAD 6b9c3ef69146b0babb1a8e90424586ab02f9c8de. Latest listed T1 FFT CI 42457914824 succeeded; prior 42457872783/42457864030/42457860036 failed. T4 classifier CI 42447922773 SUCCESS on source 125efe37; bridge CI 42447918743 SUCCESS on an older source. No duplicate CI or native build requested, no jobs cancelled, no source assets published. T5 owns three buttons, Resolution, delivery. T4 trial vote remains يحتاج; readiness NOT_READY.

## Next checkpoint
Check fresh HEAD and any T4 capture-runtime work first. If clear, implement bounded epoch correlation in capture diagnostics with source-only regression; otherwise independently analyze newest signed package manifest and newer CL device logs. For phone acceptance: menu cursor versus native black cursor, gameplay camera at every edge, Escape/menu/return, detach/refocus, keyboard and original world save/reopen. INPUT-005 remains OPEN.
