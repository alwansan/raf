# A4 resumed / DIAG-010 — 3 November 2026

Identity: raft-20261103T105430Z-a4d9e31b, session a4-20261103T105430Z-5c7d9b28; resumed_from raft-20261103T095832Z-a4c7e2b1 (previous A4 PERF-007 completed). Registered against live HEAD e70dd94d9ea0309718f523352edb24299960c15d. This is a NEW coordination identity; no edits to old client's files.

Read current prompts, owner requirements, AGENTS, STATUS, coordination records and A4 predecessor, Actions, CL logs/release identities. WATER-001 A1 and HAPTICS-008 A3/A5 currently active; don't overlap shader/resource, game-input/World/Settings or native workflows. No other plan currently claimed a diagnostics summary fix.

Hypothesis: `RepeatedDiagnosticMessages.Summarize` resets counters for ALL pending groups before callback invocations. If callback throws, even the not-yet-delivered groups lose their counts. Reproduce with deterministic failing callback, then preserve original error-first logging, bounded dictionary and nonblocking callback outside lock.

Only `android-port/Runtime/Platform/PersistentDiagnosticLog.cs`, `android-port/Tests/Diagnostics/Program.cs`, and own coordination/STATUS/handoff intended. Do not touch .meta/GUID, original private code, CL, LFS, Unity/APK/OBB/XAPK/Release, scheduled tasks, Mouse0/500ms or peripherals. CPU-only managed test and workflow.


<!-- A4-DIAG010-CALLBACK-RETRY-20261103 -->
## A4 DIAG-010 — lossless retry for repeat-error summaries (3 November 2026)

[Source repair 196fce7b](https://github.com/alwansan/raf/commit/196fce7bd147b5baac2bb8214a8c4d0aad5e2af2) changes only `PersistentDiagnosticLog.cs` repeat-summary bookkeeping and `android-port/Tests/Diagnostics/Program.cs`. Previously, `RepeatedDiagnosticMessages.Summarize` zeroed **all** pending duplicate counters before the first sink callback; if a callback threw, even unattempted groups were lost. Now each group is snapshotted/zeroed immediately before its callback outside the dictionary lock, and a thrown callback restores its count plus concurrently arriving duplicates. A callback that persists then throws may cause a duplicate summary on retry (at-least-once); the first full stack and 128-key capacity policy are unchanged.

[Diagnostics CPU-only CI 41623644272](https://github.com/alwansan/raf/actions/runs/41623644272), job125875404710, **COMPLETED SUCCESS** at exact source 196fce7bd147b5baac2bb8214a8c4d0aad5e2af2: `RAFT_PERSISTENT_LOG_TEST checks=270 passed=true actualAndroidStorageVerified=false`; synthetic injected I/O-callback failure, two distinct error groups, and concurrent repeat during failure were exercised. Exact-source [platform CI 41623644500](https://github.com/alwansan/raf/actions/runs/41623644500) and [original-startup managed CI 41623644866](https://github.com/alwansan/raf/actions/runs/41623644866) also **COMPLETED SUCCESS**. These are not phone/Unity game runs, do not prove new GPU/performance behavior or fix WATER-001/RENDER-002. No original data, .meta/GUID, LEFT Mouse0/500ms, UGUI/virtual Xbox/external input, LFS, CL, native build requests, Unity/APK/OBB/XAPK/releases or scheduled tasks changed. A4 coordination identity `raft-20261103T105430Z-a4d9e31b`; scoped work completed, game **NOT_READY / 0-of-3**.

## Coordination and lease

- New identity follows completed A4 predecessor; avoided active A1 WATER-001 and A3/A5 HAPTICS-008 source/workflows.
- Initial identity registration ref update encountered moving HEAD; no force was used. Rebuilt the coordination commit from a fresh live HEAD with expected_sha and succeeded at ea806b7f75d471e705c048c884a3a02cb610caf9. Code commit also used expected SHA without force.
- Checkpoints: no cancellation or native delivery, scoped work completed; inspect HEAD/Actions before any new task.
