# T2 — original Foam per-pass aggregate cross-check
session_id: 20261107T1720Z-T2-scheduled-pass-aggregate-check-v4n8
origin: scheduled
issue_id: WATER-001
resumed_from_sessions: 20261107T1623Z-T2-scheduled-role-gate-b7c4; 20261107T2227Z-T2-chat-blit-texture-role-6c52
base_sha: 8d53cd7431385cd34b5afe161faaf65588cfd9c5
scope_commit: 119abfc1bb90ac8d27bdb7d21152ec941fa70435
source_commit: 69072c3b69da1fa9261e3a4aefa1b5b62c022ce8
status: completed_source_only
experiment_key: original-Foam-two-Blit-pass-aggregate-v1-no-raw-IL
files: scripts/t2_foam_pass_aggregate_consistency.py; tests/test_t2_foam_pass_aggregate_consistency.py
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (world save/reopen succeeded; water errors persist)
original_evidence: CI 42305522855; original two explicit Blit sites pass 0/1, one typed source/destination pair known and one unknown.
hypothesis: per-pass source/destination count partitions must sum to the original aggregate count; refuse drift or contradictory claims.
result: added source-only strict aggregate cross-check with original upstream report validator; six synthetic regression tests authored, NOT executed against original checkout because container git DNS resolution failed ('Could not resolve host: github.com'). No CI dispatched; no Unity/device proof; no ShaderLab changes.
limits: this cannot prove producer identity, CB0 runtime binding, ShaderLab or pixels. T3 graphics and T4/T5 physical mouse/resolution scopes untouched. No duplicate Actions.
next_step: execute 'python -m unittest tests.test_t2_foam_pass_aggregate_consistency' from authentic checkout; feed authenticated original safe report into 'python -m scripts.t2_foam_pass_aggregate_consistency <report.json>' and confirm pass-specific count partition; coordinate producer unknown resolution with chat T2, then integrate validated shader resources.
