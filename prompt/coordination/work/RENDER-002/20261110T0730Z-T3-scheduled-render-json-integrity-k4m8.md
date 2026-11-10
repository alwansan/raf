# T3 RENDER-002 — input integrity gate
session_id: 20261110T0730Z-T3-scheduled-render-json-integrity-k4m8
origin: scheduled
baseline_sha: f83a40622ce585a0c4fd4ea31431fbbc146f2bba
experiment_key: T3-RENDER-002-json-duplicate-key-rejection
scope: scripts/t3_render_state_pair_diff.py; tests/test_t3_render_state_pair_diff.py; unique session file.
shared_resource: none; no Unity, ZIP2, APK, or GPU.
hypothesis: Python json.loads silently keeps the last of duplicate render-state keys; an ambiguous private original/export summary can be misclassified as MATCH or MISMATCH. Reject duplicate keys before comparing. Keep the existing allowlist and statuses unchanged.
taken_over_from: T3 20261110T0633Z known-mismatch-g8p2 and original same-export runs 41939404454, 41940350604.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57.
non_goals: no actual shader, texture, material, mesh or Android pixel fix. No T4 input or T5 resolution edits.
validation: local unittest regression, source only; CI only if no equivalent pending run.
