# T4 scheduled — poisoned logger reader-only exclusion
session_id: 20261109T1939Z-T4-scheduled-reader-poison-q8m5
origin: scheduled
issue_id: INPUT-005
baseline_sha: 896547525db6b02e299bd73e782450a65fa04de4
scope_commit: 20bec25ce2bd57b988684ea41b07b79de3469464
source_commit: 16ae80eb562b778a729bf1a31ce2e3116ee5a0d5
test_commit: a3660d2eabff6ad03b29551256879832580ba516
experiment_key: T4-INPUT005-poisoned-logger-reader-only-exclusion-v1
resource_key: none
status: source_fix_published_ci_pending

## Recovery
Read DEVICE_FEEDBACK_42058825739_AR.md first. Owner verified world entry/save/exit/reentry only for game artifact 42058825739. No evidence for signed newer Raft mouse buttons. Restored T4 chat 20261109T1912Z logger session guard and 20261109T1922Z coordination record; 24 source-only epoch tests previously passed CI42681491521. Checked live branch HEAD 896547525db6b02e299bd73e782450a65fa04de4, team source work, latest Actions, original mouse integration, and no same-file active work identified. No CI canceled or heavy build started.

## New engineering
Discovered inconsistency in scripts/t4_correlate_mouse_runtime_epochs.py: eligible and callbacks_only exclude poisoned JSONL logger sessions, but reader_only counted them, producing spurious UNITY_GETTER_WITHOUT_SAME_EPOCH_CALLBACK from replayed/out-of-order sequence. Fixed reader_only to exclude poisoned scopes. Added test test_poisoned_logger_reader_only_cannot_claim_getter using real logger JSONL envelope, sequence 4/5/2 and asserting zero reader-only, invalid provenance, no device pass. Source and test committed separately; no game or Android source touched.

## Limits / next
New regression not yet confirmed by CI; check T4 epoch workflow result on commit a3660d2e and run 25 tests. Existing full game mouse acceptance remains OPEN, only source telemetry classification improved. Preserve native keyboard, original .rgd, audio, Settings and T5 Resolution/three buttons placement. Obtain real signed same-source game capture and verify LEFT/RIGHT/MIDDLE, wheel, original Unity getters and actual Raft actions; no source CI is device PASS. Do not repeat full Unity build or touch general layout.
