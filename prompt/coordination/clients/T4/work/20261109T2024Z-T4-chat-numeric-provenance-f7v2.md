# T4 independent source-only numeric provenance scope
session_id: 20261109T2024Z-T4-chat-numeric-provenance-f7v2
origin: chat
status: active
updated_at: 2026-11-09T20:24:00Z
issue_id: INPUT-005
base_sha: 0c7d349845d2b7c1678acd2cb0e7e86bbf929294
resumed_from_sessions:
- 20261109T2002Z-T4-chat-per-channel-mouse-evidence-h7k3
- 20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6
experiment_key: T4-INPUT005-PersistentDiagnosticLog-int32-epoch-long-counter-malformed-token-overflow-failclosed-v1
resource_key: none (isolated Python source-only)
intended_files:
- scripts/t4_correlate_mouse_runtime_epochs.py
- scripts/tests/test_t4_correlate_mouse_runtime_epochs.py
- docs/T4_MOUSE_NUMERIC_PROVENANCE_BOUNDARY_2026-11-09.md
- prompt/coordination/clients/T4/work/20261109T2024Z-T4-chat-numeric-provenance-f7v2.md
- prompt/coordination/clients/T4/sessions/20261109T2024Z-T4-chat-numeric-provenance-f7v2.md
- prompt/coordination/experiments/T4/20261109T2024Z-T4-chat-numeric-provenance-f7v2.json
- prompt/coordination/B_TEAM/events/T4/20261109T2024Z-T4-chat-numeric-provenance-f7v2.json
hypothesis: Existing regex accepts epoch=12junk and numeric counter suffixes and int conversion can raise for >4300 digit JSONL values. Actual AndroidPhysicalMouseCapture.epoch is C# int; actual PhysicalMouseActionEvidence counter types are int; unity getter totals long and per-slot counts int. Malformed/source-impossible numeric fields must never yield apparent correlated input evidence or crash triage.
plan: Strict delimiter/word boundaries and bounded C# numeric parsing. Add positive/negative tests with real PersistentDiagnosticLog JSONL envelopes and long malicious tokens, preserve source-only matches and old 42 tests. No Unity APK, Android source, T5 Mini or other worker's files.
coordination: Verified head 0c7d349845d2b7c1678acd2cb0e7e86bbf929294, last T4 source-only CI42689914245 SUCCESS 42/42 and no current competing T4 session or queued/in-progress GitHub Actions. Latest CL/test shared-20261109-225506 is v14 with all T4 NEEDS_INPUT. T5 new shared Mini CI42691609924 SUCCESS independent.
next_step: Publish guarded source tests, await path-triggered T4 lightweight CI and checkpoint result. Keep INPUT-005 OPEN / full-game NOT_READY 0/3.

## Additive source-contract finding before implementation
Actual `AndroidPhysicalMouseCapture.cs` lines 205/212 concatenate C# bool values `requested` and `nativeCaptured`, whose `System.Boolean.ToString()` emits `True`/`False` (capitalized), while `unityGameplayVerified=false` and `countersAreGetterCallsNotClicks=true` are explicit lowercase source literals. The existing `parse_bool` accepts lowercase only, so even a genuine captured=true original Unity Legacy reader telemetry marker is rejected. This is part of the same numeric/token grammar provenance scope. Extend intended source/tests to accept exact C# casing + existing lowercase while rejecting malformed suffix/uppercase nonsense. No runtime/game code edit.
