# T4 INPUT-005 independent scope reservation
session_id: 20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6
origin: chat
issue_id: INPUT-005
status: active
created_at: 2026-11-09T19:46:00Z
updated_at: 2026-11-09T19:46:00Z
base_sha: 4a26329f0cc8edd0961b832feeab761869cf6540
resumed_from_sessions:
- 20261109T1939Z-T4-scheduled-reader-poison-q8m5
- 20261109T1912Z-T4-chat-logger-session-guard-n5r7
experiment_key: T4-INPUT005-Unity2021-mouse-action-reader-counter-structural-invariants-v1
resource_key: none
intended_files:
- scripts/t4_correlate_mouse_runtime_epochs.py
- scripts/tests/test_t4_correlate_mouse_runtime_epochs.py
- prompt/coordination/clients/T4/sessions/20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6.md
- prompt/coordination/clients/T4/work/20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6.md
- prompt/coordination/experiments/T4/20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6.json
- prompt/coordination/B_TEAM/events/T4/20261109T1946Z-T4-chat-mouse-counter-invariants-r8q6.json
hypothesis: Syntactically valid but impossible counter combinations can be misclassified as same-epoch positive evidence. Authored PhysicalMouseActionEvidence.Record increments exactly one callback Count; pressed/released are mutually exclusive; V/H may co-occur on a single scroll. Authored PhysicalMouseLegacyReaderEvidence.Record increments at most one native/fallback per getter, and edge/scroll categories are disjoint subsets of positive results.
plan: Add fail-closed structural checks with adversarial positive and negative source tests; run existing lightweight T4 GitHub Actions only, confirm result and preserve source-only NOT_DEVICE_PASS.
coordination: At reservation live HEAD checked and queued/in_progress Actions both zero; last T4 scheduled run CI42685509815 completed SUCCESS. No Unity or unified APK or team-owned files, no XAPK request. Recheck shared HEAD before code edits and publishing.