# T4 chat — Original C# logger literal and bounded integer evidence
session_id: 20261109T2024Z-T4-chat-numeric-provenance-f7v2
origin: chat
issue_id: INPUT-005
status: completed_source_only_device_pending
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

## Published implementation and verification
- **Main original-producer finding:** `AndroidPhysicalMouseCapture.LogLegacyReaderEvidence` concatenates real C# `bool` requested and nativeCaptured; `System.Boolean.ToString()` emits capitalized `True/False`. Its hardcoded verification flags are lowercase `true/false`. Previous Python `parse_bool` expected lowercase only; a *valid source-authentic positive* could be rejected even when captured callbacks + Unity getter shared a true logger-session and capture epoch. Previous 42 source tests used lowercase synthetic fixtures; source correction is justified without an Android device.
- Fixed in [source commit 6f3df6bf](https://github.com/alwansan/raf/commit/6f3df6bf68921ca2a80106192724b7dbb94bb3a0): accept exact both-case source representations with strict token endings, reject false suffix `Truejunk`/`true9` and malformed duplicate keys; restrict signed C# int32 epochs/callback counters, signed C# long aggregate counters and int32 per-slot call counters. Tokens with thousands of digits cannot reach unbounded Python `int()`. Parser still outputs `device_pass=false` and `unity_gameplay_verified=false`.
- [Test commit 29cba2a3](https://github.com/alwansan/raf/commit/29cba2a3344df64094c9409a3117f167d5b1717d): 15 additional independent source regressions, including **authentic-shaped** PersistentDiagnosticLog JSONL with capitalized C# flags, legitimate per-channel LEFT-mask and `down0` fallback, genuine False negative control, malformed suffix, duplicate epoch/counter fields, max int32 / long boundaries, 5500-digit epoch/counter/per-slot tokens, and malformed mask/channel proof. Previous 42 tests remain.
- Initial [CI42692994798](https://github.com/alwansan/raf/actions/runs/42692994798) COMPLETED SUCCESS 42/42 on source fix. **Final [CI42693129361](https://github.com/alwansan/raf/actions/runs/42693129361) COMPLETED SUCCESS 57/57** on test SHA `29cba2a3344df64094c9409a3117f167d5b1717d`, job `129417825568`, log `Ran 57 tests in 0.033s; OK`. Source-only Python; no game executable or signed APK was run.
- [Detailed report](../../../../docs/T4_MOUSE_NUMERIC_PROVENANCE_BOUNDARY_2026-11-09.md), report commit `5d25681ed3919a3d08fbe558ee64915d7e51ac02`, experiment `prompt/coordination/experiments/T4/20261109T2024Z-T4-chat-numeric-provenance-f7v2.json` commit `424dab073757e1251074f90a93897ec8bd2b2eec`, T4 canonical event `prompt/coordination/B_TEAM/events/T4/20261109T2024Z-T4-chat-numeric-provenance-f7v2.json` commit `134cdcac3e1c6866d167d5370c32db3e249fcab0`.
- No changes to Unity/Android/game sources, original proprietary shader/game assets, T5 shared Mini, XAPK/OBB, .rgd, camera/touch/audio/Settings, T1/T2/T3 files. Source-only proof does **not** establish owner game response; original Raft mouse remains **INPUT-005 OPEN / full game NOT_READY 0/3**.

## Durable next step
When a **separately authorized** newly signed full Raft candidate containing the latest original mouse adapter exists, pin its source/signature first; collect single-process chronological original `PersistentDiagnosticLog` (do not combine duplicated startup/rotated segments). Run `python3 scripts/t4_correlate_mouse_runtime_epochs.py <one-process-log>`, correlate physical captured LEFT/RIGHT/MIDDLE press/release and V/H wheel with the eleven original Unity Legacy getter slots and **independently** verify the actual actions in Raft; monitor focus/camera/keyboard/touch, offline world/.rgd save/load and audio/Settings. The parser may report same-epoch co-observation but can never mark game/device PASS. Existing `CL/test/shared-20261109-225506-552476830` v0.2.14 reports nine T4 NEEDS_INPUT and does not yet supply this evidence. No T4 full XAPK or mini build should be issued for analyzer-only changes.
