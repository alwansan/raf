# T4 chat — Original C# logger literal and bounded integer evidence
session_id: 20261109T2024Z-T4-chat-numeric-provenance-f7v2
origin: chat
issue_id: INPUT-005
status: active
base_sha: 0c7d349845d2b7c1678acd2cb0e7e86bbf929294
scope_commit: a734c7087a621cc9cd95d2f4101343e7303d2287
scope_update: 8badbf83f22dbf441ae21b2cbdecaa3f8a3eaaaf
resumed_from_sessions:
- 20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3
- 20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6
experiment_key: T4-INPUT005-PersistentDiagnosticLog-int32-epoch-long-counter-malformed-token-overflow-failclosed-v1
resource_key: none
intended_files:
- scripts/t4_correlate_mouse_runtime_epochs.py
- scripts/tests/test_t4_correlate_mouse_runtime_epochs.py
- docs/T4_MOUSE_NUMERIC_PROVENANCE_BOUNDARY_2026-11-09.md
- own session/work/experiment/event only

## Recovered result and team status
Latest T4 chat 20261109T2002Z source-only per-channel correlation CI42689914245 completed SUCCESS 42/42. No newer T4 scheduled session or active matching work. Latest owner CL/test shared-20261109-225506-552476830 (app 0.2.14, 30 cases) has T4-01..T4-09 NEEDS_INPUT, not captured mouse phone acceptance. New T5 single shared Mini CI42691609924 completed SUCCESS, separate files; T1/T2/T3 source jobs independently ongoing; no queued/in_progress Actions at scope reservation. Full original Raft game mouse input remains device unverified; old 42058825739 world/save artifact predates latest reader patch.

## Authenticated source flaw
Original `android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs` constructs real reader log by concatenating C# `requested` and `nativeCaptured` bool values, emitting `captureRequested=True; captureObserved=True`; literal suffix `countersAreGetterCallsNotClicks=true; unityGameplayVerified=false` is lowercase. Existing Python parse_bool accepted only lowercase `true/false`, thus source-authentic positive captured reader marker could be INVALID even with proper capture. Additional regexes allowed malformed suffix `epoch=12junk` and unbounded counter digits can raise Python int conversion exceptions (or cause false metadata attribution).

## Planned repair
Allow both canonical C# `True`/`False` and existing lowercase literals in exact token boundaries. Reject extra suffix/duplicate numeric keys, overflow (C# signed int epoch and captured callback counters; long getter totals; int per-slot report), and thousands of digits without crash. Add rigorous source-only positive and negative controls reflecting the *actual* source envelope. Preserve all earlier 42 regressions and constant `device_pass=false`/`unity_gameplay_verified=false`. No Unity, native build, app, OBB, GL, save, camera or touch changes.

## Next
Finish source tests, check isolated T4 source CI and write authoritative run proof; publish own work/experiment/event and close lease only when observed results are verified.
