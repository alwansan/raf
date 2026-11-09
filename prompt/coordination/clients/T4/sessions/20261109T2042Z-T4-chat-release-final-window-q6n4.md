# T4 chat — bounded after-release final mouse telemetry
session_id: 20261109T2042Z-T4-chat-release-final-window-q6n4
origin: chat
issue_id: INPUT-005
status: completed_source_only_device_pending
base_sha: a4c05fbdd9c796252d7933c86b0cac495d5a7078
scope_commit: 88eacae111725cda8dee57bfbbc1645ec4621841
resumed_from_sessions:
- 20261109T2036Z-T4-scheduled-ci-provenance-m4q7
- 20261109T2024Z-T4-chat-numeric-provenance-f7v2
experiment_key: T4-INPUT005-original-ReleaseCapture-post-release-final-marker-order-v1
resource_key: none
intended_files: scripts/t4_correlate_mouse_runtime_epochs.py; scripts/tests/test_t4_correlate_mouse_runtime_epochs.py; docs/T4_RELEASE_FINAL_ORIGINAL_MOUSE_EVIDENCE_2026-11-09.md; own work/session/experiment/event.

## Verified recovery
Latest T4 scheduled session 20261109T2036Z verifies source-only CI42693129361 green (57/57), and original game artifact 42058825739 world/.rgd evidence is old; neither proves current physical mouse gameplay. Latest CL shared-20261109-233132-554663211 has 30 cases, T4-01..09 all NEEDS_INPUT. Live checked HEAD a4c05fbdd9c796252d7933c86b0cac495d5a7078, zero queued/in_progress Actions, no T4 same-file active worker; T5 owns unified Mini and full package policy. This session changes source-only T4 Python evidence classifier/tests only.

## Source-grounded gap
In original Android C# `AndroidPhysicalMouseCapture.ReleaseCapture()` at lines 620-630, a `physical_mouse_capture_released` record is written BEFORE `physical_mouse_captured_action_callbacks_final` and `physical_mouse_legacy_reader_evidence_final`. All finals carry the original unchanged capture `epoch` because `epoch++` and counter resets happen only later in the method (line ~637). Current Python triage immediately sets `active=None` on the release record, so any valid final snapshots are unpaired. This hides real quick clicks when their only emitted snapshots were release-final, or hides the final half of an early capture/getter pair.

## Planned safety rules
Keep an epoch/session-bound pending terminal opportunity after release, only for source-authentic `_final` operations, at most one each, in the order C# emits them (actions then readers) with an optional small interleaving budget for non-mouse logger messages. Reject ordinary post-release callbacks/getters, repeated finals, a new capture/retry before final, mismatched epochs, and cross-logger sessions. Existing scope/sequence poisoning and C# booleans/int limits still apply. Preserve `device_pass=false`, `unity_gameplay_verified=false`; no Unity build or new Mini/XAPK.

## Final implementation and CI outcome
- Source-grounded flaw: real `AndroidPhysicalMouseCapture.ReleaseCapture` logs `physical_mouse_capture_released` BEFORE final actions/readers, with `epoch++` and reader/button reset AFTER both. Previous triage set `active=None` immediately, silently losing authentic final-only evidence. This fix is not a gameplay/runtime input change.
- Python parser implementation [commit 20efd8020d](https://github.com/alwansan/raf/commit/20efd8020d68bca166a2a23a24e8d4f03163bc6d) introduces bounded `pending_final` after release, preserving only exact source `_final` action then reader, at most once each, same session and same capture epoch, with no new request or ordinary callback/getter, <=8 unrelated logger records of interleaving. Existing poison/session/sequence/boolean/counter validators remain active.
- Initial 12 source-only regression tests [commit 5c43c3a20](https://github.com/alwansan/raf/commit/5c43c3a20b397fa6e9bfaabd7c5a96d067b492ab) include genuine original C# JSONL release-then-finals, event-only+final-reader, reader-only+final-event, no ordinary post-release acceptance, unrelated logger session, epoch drift, next request, duplicates, reversed final order, <=8 interleaving. [CI42695937421](https://github.com/alwansan/raf/actions/runs/42695937421) **COMPLETED SUCCESS 69/69**, job 129427666265.
- Hardened malformed/wrong-epoch final poisoning in [commit 8e5db658](https://github.com/alwansan/raf/commit/8e5db658a8b597697a907eb39ea0834f15feae12), with two more negative regression tests in [commit 4e7ac408](https://github.com/alwansan/raf/commit/4e7ac40839328bc1e7688f41c0a645ca3a54bb46). **FINAL [CI42696168324](https://github.com/alwansan/raf/actions/runs/42696168324): COMPLETED SUCCESS, 71/71** Python tests on exact source SHA `4e7ac40839328bc1e7688f41c0a645ca3a54bb46`, job `129428503951`, log: `Ran 71 tests in 0.029s; OK`.
- Independent report `docs/T4_RELEASE_FINAL_ORIGINAL_MOUSE_EVIDENCE_2026-11-09.md`, commit 768677c90a36afb8b425d9c0aa18320adaec9374. Experiment `prompt/coordination/experiments/T4/20261109T2042Z-T4-chat-release-final-window-q6n4.json`, commit b65d143e2095b4927cc39e5803c87fbd154ae033. Canonical event `prompt/coordination/B_TEAM/events/T4/20261109T2042Z-T4-chat-release-final-window-q6n4.json`, commit a71b64366c82abe493787021651e2327f16d7036.
- Latest actual owner upload CL/test/shared-20261109-233132-554663211, source 731d7a68bb3826b348d0314f694737b522e92976: 30-case shared Mini, T4-01..09 **NEEDS_INPUT**; no original signed Raft full-game device mouse success. Earlier old artifact 42058825739 owner world/save feedback is not same-source mouse button acceptance.
- No Unity/Android/game changes, no T5 Mini or original XAPK/OBB build, no touched original proprietary assets or .meta or .rgd, audio/Settings, touch/camera. Only own T4 parser/tests and own coordination docs. `INPUT-005 OPEN` and full game `NOT_READY 0/3`.

## Durable handoff
Scope completed with no held files or resource key; source-only exact `_final` parser fix is green. Next T4 scheduled/chat should first review `CL/test` for owner mouse hardware and true capture evidence, then, when **separately authorized** current signed Raft XAPK exists, pin its provenance and test genuine physical LEFT/RIGHT/MIDDLE and V/H scroll with same-process `PersistentDiagnosticLog`, including actions just before focus/capture release. Compare source callback ↔ original Unity getter ↔ independently observed gameplay effect. Keep `device_pass=false`/ `unity_gameplay_verified=false` until game itself is demonstrated. Preserve offline world/.rgd save, camera/focus, keyboard, touch, audio/Settings and XAPK 5/5 gate.
