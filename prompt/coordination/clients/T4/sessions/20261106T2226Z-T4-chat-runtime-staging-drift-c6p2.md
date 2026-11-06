# T4 chat — reject stale original runtime operation staging after backup

- session_id: 20261106T2226Z-T4-chat-runtime-staging-drift-c6p2
- origin: chat
- status: completed
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

## Completed RED/GREEN and next handoff — 2026-11-06 22:31Z

- **Source-only finish:** scope released in prompt/coordination/work/LOCAL-005/T4-20261106T2226Z-T4-chat-runtime-staging-drift-c6p2-postbackup-prewrite-source-drift.json. No shared game source, original .meta/GUID bytes, .rgd, FMOD, Settings, Android touch or native request modified.
- **RED test-only [a02afd10](https://github.com/alwansan/raf/commit/a02afd104b72359c7955d7519be1fda978018ce5), [CI42304948072](https://github.com/alwansan/raf/actions/runs/42304948072), job 128191820432 COMPLETED FAILURE expected:** 17 old tests passed. One new synthetic test covered **two simultaneous-writer interleaves**, changing .cs or .meta after original shutil.copy2 backup. Original adapter silently installed stale C# over independent writer's .cs; for changed .meta it wrote stale C# then entered rollback failure, which is not a safe prewrite refusal. Exact per-case CI first failure preserved.
- **GREEN [a2577ace](https://github.com/alwansan/raf/commit/a2577acef04ff8d1997f1e2af14cc85aa27a84d0), [CI42305089873](https://github.com/alwansan/raf/actions/runs/42305089873), job 128192313291 COMPLETED SUCCESS:** original 18/18 Python runtime tracing suite, including both new concurrent-edit subcases; existing source-only original Android offline integration authenticated source and compiled adapted C# via .NET10 with RAFT_OFFLINE_COMPILE exit=0 errorCodes={} affectedFiles=[].
- **Fix:** after byte-identical original backup validation but before first instrumented file write, verify each original source and GUID metadata are still physically local nonhardlinked files matching original byte snapshots, and refuse a new unexpected .meta. If any check fails or raises, preserve backups and other writer's source changes (do not roll back stale data). Never weaken existing pin/authoritative original code or original method instrumentation.
- **Evidence:** experiment prompt/coordination/experiments/T4/20261106T2226Z-runtime-stage-prewrite-drift-c6p2.json and event prompt/coordination/B_TEAM/events/T4/20261106T2231Z-T4-original-runtime-operation-stage-drift-c6p2.json. Only T4 owned files and independent coordination records changed.
- **Limit:** this closes one **postbackup/pre-first-source-write race**; it is not a process lock or atomic installer, and post-first-write/recovery interleavings still require a separate test. No Unity Editor/ARM64 IL2CPP build or Android device acceptance, saved world replay, phone signing or new XAPK evidence from this CI. LOCAL-005 OPEN, game NOT_READY 0/3, trial r1 T4 vote unchanged.
- **Native handoff:** T5 owner run [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) uses old pinned source a1737bd7; at last check reconstruct remains in Unity import. Do not cancel/duplicate it or confuse with new guard. After final signed candidate if any, require exact SHA/OBB pair and owner same-world .rgd save/full quit/relaunch/reopen, with physical mouse and preserved sound/Settings; touch/layout deferred.

