# T4 scoped source-only fix: original mouse release-final evidence
session_id: 20261109T2042Z-T4-chat-release-final-window-q6n4
origin: chat
issue_id: INPUT-005
status: completed
updated_at: 2026-11-09T20:49:00Z
base_sha: a4c05fbdd9c796252d7933c86b0cac495d5a7078
resumed_from_sessions:
- 20261109T2036Z-T4-scheduled-ci-provenance-m4q7
- 20261109T2024Z-T4-chat-numeric-provenance-f7v2
experiment_key: T4-INPUT005-original-ReleaseCapture-post-release-final-marker-order-v1
resource_key: none (isolated Python source gate)
intended_files:
- scripts/t4_correlate_mouse_runtime_epochs.py
- scripts/tests/test_t4_correlate_mouse_runtime_epochs.py
- docs/T4_RELEASE_FINAL_ORIGINAL_MOUSE_EVIDENCE_2026-11-09.md
- prompt/coordination/clients/T4/work/20261109T2042Z-T4-chat-release-final-window-q6n4.md
- prompt/coordination/clients/T4/sessions/20261109T2042Z-T4-chat-release-final-window-q6n4.md
- prompt/coordination/experiments/T4/20261109T2042Z-T4-chat-release-final-window-q6n4.json
- prompt/coordination/B_TEAM/events/T4/20261109T2042Z-T4-chat-release-final-window-q6n4.json
hypothesis: Real AndroidPhysicalMouseCapture.ReleaseCapture logs physical_mouse_capture_released BEFORE physical_mouse_captured_action_callbacks_final and physical_mouse_legacy_reader_evidence_final (same logger session and epoch). The existing triage closes active on release, incorrectly drops authentic final-only button/wheel evidence. Teach a narrow bounded after-release final-only tail without joining new epochs, unrelated sessions or ordinary non-final callbacks. Do not affect source Android/Game/Unity.
coordination: Live branch SHA a4c05fbdd9c796252d7933c86b0cac495d5a7078 with zero queued or in_progress Actions; newest T4 scheduled 20261109T2036Z independently verifies CI42693129361 source-only 57/57 and does not own these two files. Latest owner CL/test/shared-20261109-233132-554663211 contains 30 cases with T4-01..09 NEEDS_INPUT; no real mouse phone PASS. Other T1/T2/T3/T5 work independent.
next_step: Add source-bound gated post-release final parser and synthetic C#-ordered tests; verify CI lightweight, checkpoint experiment/event/release scope. Do not launch XAPK or duplicate Mini.

## Scope closed with source-only proof
- Verified C# `ReleaseCapture()` emits released record before `physical_mouse_captured_action_callbacks_final` and `physical_mouse_legacy_reader_evidence_final` (same epoch and logger); previous triage missed final-only evidence.
- Fixed own `scripts/t4_correlate_mouse_runtime_epochs.py` in commits `20efd8020d68bca166a2a23a24e8d4f03163bc6d` and `8e5db658a8b597697a907eb39ea0834f15feae12`; tests `scripts/tests/test_t4_correlate_mouse_runtime_epochs.py` commits `5c43c3a20b397fa6e9bfaabd7c5a96d067b492ab` and `4e7ac40839328bc1e7688f41c0a645ca3a54bb46`. Total 14 new tests added to prior 57.
- Final lightweight [GitHub Actions CI42696168324](https://github.com/alwansan/raf/actions/runs/42696168324) **COMPLETED SUCCESS 71/71**, source SHA `4e7ac40839328bc1e7688f41c0a645ca3a54bb46`, job `129428503951`. Interim [CI42695937421](https://github.com/alwansan/raf/actions/runs/42695937421) SUCCESS 69/69.
- Own report `docs/T4_RELEASE_FINAL_ORIGINAL_MOUSE_EVIDENCE_2026-11-09.md`, session `prompt/coordination/clients/T4/sessions/20261109T2042Z-T4-chat-release-final-window-q6n4.md`, experiment `prompt/coordination/experiments/T4/20261109T2042Z-T4-chat-release-final-window-q6n4.json`, event `prompt/coordination/B_TEAM/events/T4/20261109T2042Z-T4-chat-release-final-window-q6n4.json` all published.
- No held file locks/resource_key; no heavyweight Unity/game build, APK/OBB/XAPK or other agent files changed. INPUT-005 OPEN; original game/phone acceptance still device pending and full game NOT_READY 0/3. Fresh CL/test shared-20261109-233132-554663211 contains nine T4 NEEDS_INPUT. Next scheduled T4 can safely continue with new owner genuine signed-game mouse logs.
