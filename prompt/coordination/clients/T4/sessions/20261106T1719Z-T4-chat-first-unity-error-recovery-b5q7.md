# T4 chat — first Unity exception must survive transient logger unavailability

- session_id: `20261106T1719Z-T4-chat-first-unity-error-recovery-b5q7`; origin: `chat`; status: `active`
- base_sha: `9f006935edb40189ae6f74074eb334ae9003205d`
- scope reservation: `prompt/coordination/work/LOCAL-005/T4-20261106T1719Z-T4-chat-first-unity-error-recovery-b5q7-lost-initial-unity-error.json`, commit `3981f7edf213d27e7c92f714e5cb6c6c607771a9`.
- resumed_from_sessions: `20261106T1704Z-T4-chat-android-logger-startup-retry-x7m2` (actual `AndroidRuntimeLog.Initialize` synthetic retry and CI42259053551 PASS), `20261106T164053Z-T4-chat-logger-recovery-status-k7m4` (durable LastError red/green), `20261106T1637Z-T4-scheduled-v8m2` (mouse provenance).
- current owner phone: older signed artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) at `e9c358eda01785b65e4eb14f18723da426635628` OWNER_CONFIRMED playable world/save/reopen; later source does not inherit Android acceptance. T5 OBB/assets probes and T1–T3 graphics experiments not modified.
- issue_id: LOCAL-005 (diagnostic fidelity only); INPUT-005 remains OPEN. No in-progress Actions at initial scope check; do not start native build.

## Hypothesis / planned exact red-green gate

In actual `AndroidRuntimeLog.UnityMessage`, the code calls `RepeatedDiagnosticMessages.First` **before** it calls `Write`. When sink == null after startup storage failure, `Write` silently does nothing, yet the very first full Unity error stack is considered seen. A later identical error after `Initialize` succeeds is suppressed entirely, so the real first error is missing from durable JSONL. Preserve existing `true` return value while sink missing, because `AndroidTestDiagnostics.Capture` uses it to also show messages in its bounded HUD/event queue; don't suppress in-app diagnostic UI.

Scope only existing exact real Android logger `android-port/Runtime/Platform/AndroidRuntimeLog.cs` and synthetic `android-port/Tests/Diagnostics/Program.cs`. The earlier test project already compiles actual Android source with synthetic Unity API signatures and no native game/staged stubs. Extend existing deterministic startup-failure fixture: immediately after failed initial Initialize call `UnityMessage("Error", unique original crash stack, true)`; it returns true for HUD; recover filesystem+successful Initialize; call same error again, require true and actual persisted JSONL original stack; call a third time require false (once actually stored). Red must fail on source old before production fix. Then clear sink-null grouping precheck only, preserving all critical/warning dedup for live sink. Existing 292 .NET8 tests remain; no .rgd/shaders/saves/mouse/audio/Settings/Unity/OBB edits.

Record CI SHA, exact assertions, event/report/T5 handoff; issue remains OPEN until device proof. No device storage incident is inferred from synthetic test.
