# T4 INPUT-005 — reset-aware aggregate evidence gate
session_id: 20261111T2140Z-T4-scheduled-reset-gate-p4m8
origin: scheduled
branch: feature/android-native-port
observed_head: e4701cf1af80c3685e7feb765d180f4818f13f4d
scope: scripts/t4_capture_gap_classifier.py; tests/test_t4_capture_gap_classifier.py; independent T4 session/work files
experiment_key: INPUT-005-counter-reset-integrity
shared_resource: none; source-only; no Unity/CI dispatch

## Evidence and hypothesis
Owner DEVICE_FEEDBACK_42058825739_AR.md: world/save/reopen phone success for artifact 42058825739; failed publishing independent. Owner 8 Nov physical camera works but click/wheel remain unproven. Original authenticated 20-call-site bridge source-only CI42518143297 SUCCESS. CL 8 Nov mouse callbacks all captured=false, not proof of game consumption. Existing summary emits callback_counter_decreases and reader_counter_decreases; classifier currently ignores them, so across counter resets a positive monotonic increase can be wrongly labeled a clean paired observation. This is a telemetry integrity bug, not game input root cause.

## Proposed narrow change
Reject aggregate comparisons when either marker counter decreased, unless there is a future segmented same-epoch analysis. Preserve all counter values and gameplay_success_proven=false. Regression tests for reset and malformed reset fields. No modifications to Unity, input capture, keyboard, touch, .rgd, Settings, sound or T5 Resolution. T5 retains three on-screen buttons, Resolution and mini build. No duplicate CI while T1/T5 runs active.
