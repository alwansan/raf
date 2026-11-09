# T4 chat handoff — 2026-11-09 same-epoch mouse evidence correlation

session_id: 20261109T1858Z-T4-chat-epoch-evidence-p6m4
origin: chat
worker: T4
issue_id: INPUT-005
status: completed_source_only_device_pending
resumed_from_sessions:
- 20261109T1836Z-T4-scheduled-capture-provenance-k7d2
- 20261109T1742Z-T4-scheduled-k8p2
- 20261109T0209Z-T4-chat-unity-legacy-readers-w7q5
base_sha: 7e4ae3efca1da18b2a042e09c1cfd75aca08444e
work_reservation_commit: 18f9edf14f1ea03ba47e5b029545792314588117
experiment_key: T4-INPUT005-unity-getter-captured-epoch-matching-logged-counters-negative-controls-v1
resource_key: none
intended_files:
- scripts/t4_correlate_mouse_runtime_epochs.py
- scripts/tests/test_t4_correlate_mouse_runtime_epochs.py
- .github/workflows/raft-t4-mouse-epoch-correlation.yml
- docs/T4_MOUSE_SAME_EPOCH_CORRELATION_2026-11-09.md
- this T4-only session/work/experiment/event
scope: Source-only single-process log correlation; do not modify existing scheduled T4 acceptance gate, Android/Unity game runtime, T5 mini, Raft APK/XAPK or assets.

## Restored and live checks

Read actual T_TEAM RESTORE_AR, CHAT_AND_SCHEDULE_AR, owner portrait Arabic lab instructions, RESTORE_SHARED_LAB_AR, T4 MEMORY and state and latest 1850..1836 scheduled + prior chat sessions. Started HEAD 7e4ae3efca1da18b2a042e09c1cfd75aca08444e; team runs checked, no T4 equivalent pending. New team commits continued non-destructively. Source T4 existing: pinned original ZIP2 direct 20 Legacy getter sites, native first fallback compiled Unity2021 Android/Editor managed, reader telemetry source CI42549986761 SUCCESS; on-phone pointer-captured game buttons still unverified. Current latest same branch pre-existing T4 acceptance gate CI42657857161 SUCCESS (8 gate tests), does not correlate Unity reader. Scheduled 20261109T1836Z session did not modify game source or launch CI and explicitly proposed same-epoch consumer correlation.

Latest owner CL main source ref 24a677fc8fa4749c0bcf8a3cac01fa80b1641c86; newest shared-20261108-232759-468049775 contains T3 traces, not new T4 captured=true. Earlier immutable CL@4680f5dc T4 mouse manual logs show only uncaptured=true? **No: captured=false**, 13 LEFT callback pairs and 55 vertical wheel events, capture request ON absent. The real game owner report artifact 42058825739 confirms older world enter/save/reopen; that old APK predates source-level new button fallback.

## Implementation and verification

- source commit 94fbb41751ea8b9b5006ea425d7b5bda27f86348 — new isolated `scripts/t4_correlate_mouse_runtime_epochs.py`, no game-code edit. Analyze chronological one-process original game text/JSONL, require request/retry epoch boundaries, release termination, authentic captured callback marker plus original Unity Legacy getter marker in *same* attempt. Handles Unity Update emitting reader before callback log. Reject missing epoch, mismatches, missing or bogus capture flags, contradictory counters, overflow/budget, misleading lack of requests; never GAME PASS.
- test commit dbf665a8c68b532737d3bd680f2f53f5c36eb7af — 14 adversarial synthetic tests including false-positive negative controls.
- CI workflow commit 14a5d794ee5409d0f1ba32fb0436e480b4467230 — `.github/workflows/raft-t4-mouse-epoch-correlation.yml` Ubuntu24.04 Python only 5 minutes timeout isolated concurrency, no Unity build/dispatch/cancel.
- **GitHub Actions https://github.com/alwansan/raf/actions/runs/42679181503 COMPLETED SUCCESS**, job 129368771496. Actual log confirms **Ran 14 tests ... OK**, no failures. Independent runner guard https://github.com/alwansan/raf/actions/runs/42679180138 SUCCESS.
- docs commit 321b328e0bfe5cab2c36b6f71feb906681bf0715: `docs/T4_MOUSE_SAME_EPOCH_CORRELATION_2026-11-09.md`.
- experiment `prompt/coordination/experiments/T4/20261109T1858Z-T4-chat-epoch-evidence-p6m4.json` commit dc4ba3153703a9f8999751674acc8799235aa052.
- event `prompt/coordination/B_TEAM/events/T4/20261109T1858Z-T4-chat-epoch-evidence-p6m4.json` commit be444d85cec8f0d3df9f526242442be5db14e01d.

## Explicit result limits

An Android callback and a Unity reader positive fallback within one epoch only prove source-logged invocation/correlation, *not* the same physical click, authored gameplay action, or correctness of mouse wheel on phone. Process epoch counters repeat across launches: NEVER merge logs from different app processes. APK signature/artifact provenance requires external independently-verified SHA. `device_pass=false` and `unity_gameplay_verified=false` are hardcoded outputs. No signed source-current Raft game tested on phone. Did not edit `.rgd`, audio, world/local host, settings, keyboard, camera, touch, original ZIP2 assets, T5 Mini, T5 pack. No unified mini or full XAPK launched. **INPUT-005 remains OPEN, full game NOT_READY 0/3**.

## Handoff to T4 scheduled and other teammates

On authorized T5 signed full-game candidate including T4 mouse callback and Legacy reader sources, extract a *single-process* game runtime log, pin APK artifact SHA and branch source SHA, run:
`python3 scripts/t4_correlate_mouse_runtime_epochs.py /path/to/one-raft-process-log.txt`
Then compare per-epoch callbacks and original Unity Legacy reader output for LEFT/RIGHT/MIDDLE and V/H wheel, and verify actual game UI/player behavior with camera movement, focus/escape, touch/keyboard, world entry and save/reopen, audio. Existing unified Arabic portrait Mini T4-02 needs Capture ON and actual captured=true owner record separately. No new build based on source triage alone.

**Session is complete as a source engineering step, with device acceptance still pending.**
