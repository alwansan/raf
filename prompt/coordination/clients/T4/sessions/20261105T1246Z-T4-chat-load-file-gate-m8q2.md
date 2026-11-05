# T4 chat — original Load argument-path classification

- session_id: 20261105T1246Z-T4-chat-load-file-gate-m8q2
- origin: chat
- resumed_from_sessions: 20261105T1217Z-T4-android-save-postcheck; 20261105T1237Z-T4-scheduled-k7m2; 20261105T1142Z-T4-automation-platform-regression-triage
- base_sha: c2b4948875748f38cc3bcf5086c4e51d3715ba47
- status: active
- work_ids: prompt/coordination/work/LOCAL-005/T4-20261105T1246Z-T4-chat-load-file-gate-m8q2-load-argument-snapshot.json
- run_urls: none dispatched
- intended_files: scripts/instrument_android_runtime_operations.py, tests/test_runtime_operation_traces.py, scripts/t4_verify_android_load_snapshot.py, .github/workflows/raft-t4-android-load-snapshot.yml, docs/T4_ANDROID_LOAD_ARGUMENT_SNAPSHOT_2026-11-05.md, prompt/coordination/work/LOCAL-005/T4-20261105T1246Z-T4-chat-load-file-gate-m8q2-load-argument-snapshot.json, prompt/coordination/clients/T4/sessions/20261105T1246Z-T4-chat-load-file-gate-m8q2.md
- experiment_key: local005-load-arg-path-presence-classification-pinnedSaveAndLoadSHA-daf835fc-android-only-01
- resource_key: none
- started_at: 2026-11-05T12:46:40.854Z

## Verified baseline
Original Save file-argument postcheck passed authentic adapted source compile 42026271243, synthetic UNITY_ANDROID 42026671909 and authentic IL filename forwarding 42027197515. Scheduled T4 smoke triage concluded earlier platform race with 42028108335 PASS 17/17. Latest real device evidence remains APK86 before these fixes. No active Actions in latest first-page sample; recheck before edits. LOCAL-005 remains OPEN/NOT_READY 0/3.

## Independent hypothesis
Load<T> original caught error marker lacks a file state branch. Add bounded Android-only post-Load read-only check at original filename argument, classify absent/zero/nonzero/unavailable, preserving exceptions and return. Source-free compile/run + original C# integration must pass before any device claim. No raw RGD reads, no writes, no .meta/source pin changes. Independent of scheduled platform-race investigation.

## Next step
Implement and test snapshot, then record exact commits, workflow outcomes, limits and handoff.
