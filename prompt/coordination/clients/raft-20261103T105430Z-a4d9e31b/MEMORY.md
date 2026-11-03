# A4 resumed / DIAG-010 — 3 November 2026

Identity: raft-20261103T105430Z-a4d9e31b, session a4-20261103T105430Z-5c7d9b28; resumed_from raft-20261103T095832Z-a4c7e2b1 (previous A4 PERF-007 completed). Registered against live HEAD e70dd94d9ea0309718f523352edb24299960c15d. This is a NEW coordination identity; no edits to old client's files.

Read current prompts, owner requirements, AGENTS, STATUS, coordination records and A4 predecessor, Actions, CL logs/release identities. WATER-001 A1 and HAPTICS-008 A3/A5 currently active; don't overlap shader/resource, game-input/World/Settings or native workflows. No other plan currently claimed a diagnostics summary fix.

Hypothesis: `RepeatedDiagnosticMessages.Summarize` resets counters for ALL pending groups before callback invocations. If callback throws, even the not-yet-delivered groups lose their counts. Reproduce with deterministic failing callback, then preserve original error-first logging, bounded dictionary and nonblocking callback outside lock.

Only `android-port/Runtime/Platform/PersistentDiagnosticLog.cs`, `android-port/Tests/Diagnostics/Program.cs`, and own coordination/STATUS/handoff intended. Do not touch .meta/GUID, original private code, CL, LFS, Unity/APK/OBB/XAPK/Release, scheduled tasks, Mouse0/500ms or peripherals. CPU-only managed test and workflow.
