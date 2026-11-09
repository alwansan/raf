# T4 chat | independent mouse-counter invariant gate
session_id: 20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6
origin: chat
issue_id: INPUT-005
status: completed_source_only_device_pending
base_sha: 4a26329f0cc8edd0961b832feeab761869cf6540
scope_reservation_commit: 2d7c268248b505e4dd9ad1daa9491787df07665c
resumed_from_sessions:
- 20261109T1939Z-T4-scheduled-reader-poison-q8m5
- 20261109T1912Z-T4-chat-logger-session-guard-n5r7
experiment_key: T4-INPUT005-Unity2021-mouse-action-reader-counter-structural-invariants-v1
resource_key: none
intended_files: scripts/t4_correlate_mouse_runtime_epochs.py; scripts/tests/test_t4_correlate_mouse_runtime_epochs.py; own work/session/experiment/event only.
run_urls:
- https://github.com/alwansan/raf/actions/runs/42685509815
- https://github.com/alwansan/raf/actions/runs/42686865448
- https://github.com/alwansan/raf/actions/runs/42686942143
- https://github.com/alwansan/raf/actions/runs/42687110814
updated_at: 2026-11-09T19:51:00Z

## Recovered baseline
Latest T4 scheduled source-only test commit a3660d2e passed 25 tests (CI42685509815 SUCCESS). Prior chat source logger provenance CI42681491521 passed 24 tests. Old original Raft world/save evidence artifact 42058825739 is **not** proof for current mouse fallback. Current T4 INPUT-005 physical LEFT/RIGHT/MIDDLE and both scroll axes need a newer signed same-source full game and actual user testing; NO DEVICE PASS and no XAPK vote override. Live HEAD checked 4a26329f with zero queued/in_progress runs before reservation. T3/T5 working elsewhere; no same-file active work identified.

## Planned independent engineering
Source C# PhysicalMouseActionEvidence.Record increments Count once per accepted action, press/release each at most once, vertical and horizontal scroll may be counted on the SAME action. PhysicalMouseLegacyReaderEvidence.Record increments one total call and (at most) one native/fallback positive, and positiveEdges and positiveScroll are disjoint subsets of positives. The Python analyzer guards native+fallback<=getterCalls but not these additional producer-level constraints. Try adversarial tests; if failing, add exact fail-closed constraints. Preserve all previous proof levels; never mutate Unity/Android game, mini APK, owner CL or other worker's files.

## Next
Run isolated existing T4 mouse-epoch source-only workflow via watched path commits (not Unity build), capture job counts and status, append source commit and test evidence, publish own T4 experiment/event, mark own work completed or waiting_ci.

## Implementation and final proof
- Producer source cross-check: original `android-port/Runtime/Platform/PhysicalMouseMotionSource.cs` PhysicalMouseActionEvidence.Record increments one total Count per accepted callback. Press/Release are mutually exclusive per callback, but one ACTION_SCROLL may report **both vertical and horizontal**. Producer budget invariant: presses + releases + max(vertical, horizontal) <= total captured callback Count. Implemented without incorrectly rejecting biaxial scroll.
- The same original C# source PhysicalMouseLegacyReaderEvidence.Record increments at most one native/fallback per getter. Positive edge (Down/Up) and positive scroll (ScrollAxis/ScrollVector) are disjoint subsets of positive native/fallback getter invocations. Enforce positiveEdges + positiveScroll <= positiveLegacy + positiveFallback <= getterCalls.
- Source fix [5bd28cdc10](https://github.com/alwansan/raf/commit/5bd28cdc10eff1dfccddd478a16d66aedac3c883). Added five tests [c4cb698143](https://github.com/alwansan/raf/commit/c4cb6981434aca7b4764e9d208b3df45bbaba206): impossible press/release counts, excessive axis count, valid dual-axis one event, excessive positive edge/scroll subtotals, and positive edges without any positive native/fallback.
- The previously existing `test_positive_native_without_fallback_not_claimed_as_fallback` fixture said positiveEdges=1/positiveScroll=1 while both positiveLegacy=0/positiveFallback=0, inconsistent with C# producer. Intermediate [CI42686865448](https://github.com/alwansan/raf/actions/runs/42686865448) FAIL 24/25 and [CI42686942143](https://github.com/alwansan/raf/actions/runs/42686942143) FAIL from that *synthetic fixture*, **not** game/device. Fixed fixture to correctly declare positiveLegacy=2 in commit [01a062ab0](https://github.com/alwansan/raf/commit/01a062ab0be26c665c5226337ad0e3f143b7e5f3).
- **FINAL GitHub Actions [42687110814](https://github.com/alwansan/raf/actions/runs/42687110814): COMPLETED SUCCESS**, source commit 01a062ab0, job 129396759476. Job log states **Ran 30 tests in 0.004s, OK**. This advances previous 25/25 source test baseline; does not compile current game or demonstrate phone gameplay.
- Independent experiment: `prompt/coordination/experiments/T4/20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6.json` (publish commit ebebe068); event: `prompt/coordination/B_TEAM/events/T4/20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6.json` (publish commit 5af26a45). Work scope marked completed in commit 5ee1fa54. T5 independently built shared Mini #42686652150; T4 did not dispatch/rebuild or modify T5 package, driver, pack, request or read/alter its output. No Unity game assets or source code changed.

## Evidence bounds and next handoff
**INPUT-005 remains OPEN, Raft full-game NOT_READY 0/3.** This improves classifier rejection of impossible synthetic/corrupt mouse telemetry; neither `same_epoch...` status nor 30/30 source tests is device PASS. No recent owner captured=true same-source signed full-game JSONL or authored Raft button/wheel acceptance established. Existing old Raft game artifact #42058825739 owner world/save feedback cannot be promoted to current mouse fallback.

Next scheduled or chat T4: read this source-only checkpoint, test a **newer signed game with matching source provenance** once legitimately released by T5/owner under separate 5/5 policy. Obtain one-process non-concatenated JSONL, compare captured callbacks with original Unity getters and verify real left/right/middle and both scroll directions (horizontal/vertical), preserving camera/focus/keyboard/touch and offline world/.rgd save/load, audio/Settings. If no full-game build, inspect latest CL/test for new authentic owner traces or help another independent blocker. Do **not** dispatch XAPK or label gameplay PASS for this work.
