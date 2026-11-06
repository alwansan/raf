# T4 chat — reject stale original runtime operation staging after backup

- session_id: 20261106T2226Z-T4-chat-runtime-staging-drift-c6p2
- origin: chat
- status: active
- issue: LOCAL-005
- base_sha: dc395792b78aff3c93308c0312f7e2335e3cbe3d
- reservation_commit: 9b7f6eca3c3c25cb1d7fd0450dd6cf670c778855
- resumed_from_sessions: 20261106T2215Z-T4-chat-immutable-log-snapshot-n7b4; 20261106T2138Z-T4-scheduled-native-retry-q4n7
- intended_files: scripts/instrument_android_runtime_operations.py; tests/test_runtime_operation_traces.py
- work: prompt/coordination/work/LOCAL-005/T4-20261106T2226Z-T4-chat-runtime-staging-drift-c6p2-postbackup-prewrite-source-drift.json
- hypothesis: runtime instrumentation backup snapshot authenticates source bytes but source and GUID meta can be independently changed after copy. Existing path can overwrite concurrent writer with instrumented stale code or old rollback.
- approach: RED synthetic interleaves after backup copy, then minimal fail-closed prewrite source/meta revalidation, retain original backup on drift, run existing offline original source CI.
- native CI 42296450023 (T5 owned) in Unity Editor import/compile at last check. Do not cancel/relaunch or alter its request.
- limits: source-only staging hardening. No game data, .rgd, meta/GUID edits, audio, settings or controls. NOT_READY 0/3, LOCAL-005 OPEN.

## Results
Pending.
