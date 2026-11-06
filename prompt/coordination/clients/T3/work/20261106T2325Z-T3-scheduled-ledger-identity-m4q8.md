# T3 scope — evidence ledger identity repair
session_id: 20261106T2325Z-T3-scheduled-ledger-identity-m4q8
origin: scheduled
issue_id: RENDER-002
status: active
updated_at: 2026-11-06T23:25:00Z
baseline_sha: 9e6e0fbd49b3ea31895d9f1c327f323d04d0c816
intended_files: prompt/coordination/B_TEAM/events/T3/20261106T1625Z-T3-chat-particle108-nativeRDEF-7d2c.json; this work file; independent session
experiment_key: t3-render002-evidence-event-identity-gate-42308935364-v1
resource_key: none
hypothesis: refresh_b_team.py rejects this authentic T3 event because it lacks id/event_id, independently of shader restoration. Add stable event_id only; preserve all original evidence.
source: T2 session 20261106T2320Z-T2-scheduled-summary-gate-c8f1; CI https://github.com/alwansan/raf/actions/runs/42308935364
resumed_from: 20261106T2228Z-T3-scheduled-contract-unhashable-k7p2; T3 chat event 20261106T1625Z-T3-chat-particle108-nativeRDEF-7d2c
scope_excludes: game assets, shader source, Unity build, T4 mouse, T5 resolution/buttons, shared snapshots unless validated.
