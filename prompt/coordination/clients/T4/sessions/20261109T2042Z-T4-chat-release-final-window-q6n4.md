# T4 chat — bounded after-release final mouse telemetry
session_id: 20261109T2042Z-T4-chat-release-final-window-q6n4
origin: chat
issue_id: INPUT-005
status: active
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
