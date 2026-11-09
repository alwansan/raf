# T4 INPUT-005 — scoped device provenance handoff

session_id: 20261109T2238Z-T4-scheduled-device-provenance-r6v2
origin: scheduled
branch: feature/android-native-port

## Evidence and protected regression
- Owner device result: run 42058825739, source e9c358eda01785b65e4eb14f18723da426635628. World entered, saved, exited, reentered; APK/OBB/XAPK publication failed. Do not downgrade LOCAL-005 or mutate .rgd.
- Original owner feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md, pinned CL tree 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
- 8 Nov CL mini trace: physical uncaptured left press/release and vertical scroll; no captured=true and no game-side Unity consumer proof. Mini APK is not game APK.
- Source-only CI 42704145152 reportedly passed earlier tests; new six envelope regressions were not yet independently confirmed in this run.

## Isolated scope
No game source edit, no full build, no overlapping T5 display/layout files. This work record is a precise evidence/acceptance boundary for the next device correlation. Shared resource: none. Experiment key: T4-INPUT005-CAPTURED-UNITY-DEVICE-PROVENANCE-R6V2.

## Engineering finding / next discriminating experiment
The existing scripts/t4_correlate_mouse_runtime_epochs.py already correlates capture epochs and Unity getter snapshots but deliberately emits device_pass=false. Its positiveFallback counters are getter invocations, NOT proven game actions. Do not add more source-only green gates and call INPUT-005 fixed. On a single *new signed game build*, capture one process-local ordered PersistentDiagnosticLog JSONL and immutable package manifest; run left/right/middle press-release, vertical and horizontal scroll, menu/game transitions, focus loss, keyboard continuity and world save/reload. Feed one run only into correlator; require actual gameplay observation in addition to same-epoch captured callbacks + fallback getters. Do not merge mini-lab and game logs or multiple launches. Source-only tests must never claim gameplay PASS.

## Coordination
T4 owns physical capture, Unity legacy button/wheel and Raft cursor. T5 owns three UI button placement, resolution and shared lab build. No duplicate CI requested. Current status INPUT-005 OPEN; LOCAL-005 device world/save success retained; NOT_READY.
