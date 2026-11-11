# T4 INPUT-005 scope
session_id: 20261111T1337Z-T4-scheduled-zip-log-input-k9r2
origin: scheduled
baseline_sha: 136527eb2711a2b3836891b66a8ec90f7425e15f
experiment_key: T4-INPUT005-zip-log-stream-v1
owned_files: scripts/t4_capture_reader_summary.py; tests/test_t4_capture_reader_summary_boundary.py; this work file; own session file
hypothesis: Owner CL logs are delivered as ZIP bundles; existing CLI only accepts plain UTF-8 logs, preventing direct safe use of diagnostics. Support selected UTF-8 .log/.txt inside ZIP, reject ambiguous archives and oversized members; never merge unrelated device sessions.
shared_resource: none; no Unity build, no Action dispatch.
owner_baseline: Artifact 42058825739 entered/saved/reopened world, packaging failed. 2026-11-08 camera captured but physical buttons/wheel not confirmed. Original .rgd, keyboard, audio, Settings untouched. T5 owns Resolution and on-screen buttons.
taken_over_from: T4 20261111T1242Z-T4-scheduled-reader-baseline-h6p3; source CI42518143297; prior CL evidence.
status: scope_recorded
