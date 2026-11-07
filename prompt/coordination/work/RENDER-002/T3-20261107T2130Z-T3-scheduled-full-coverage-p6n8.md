# T3 scope 20261107T2130Z-T3-scheduled-full-coverage-p6n8
origin: scheduled
issue_id: RENDER-002
status: active
base_sha: 65548eb01c755ed9d6234a49224c900439dec062
intended_files: scripts/t3_rgb_drift_strata.py; tests/test_t3_rgb_drift_strata.py; prompt/coordination/clients/T3/sessions/20261107T2130Z-T3-scheduled-full-coverage-p6n8.md
experiment_key: t3-strata-all-field-metadata-coverage-106-30-v1
resource_key: none (source-only)
taken_over_from: T3 20261107T2030Z-T3-scheduled-unique-pair-v2k7; CI 41968665857
hypothesis: existing --require-metadata passes when only one of 106 rows has a known field, so callers may mistake a sparse manifest for complete per-pair metadata. Add opt-in all-pairs coverage gate, preserving existing behavior and drift-only gate; test with synthetic cohort. No raw assets or native builds.
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pin 520c4cf409aa20a4db54ff80ed87d8807d9cba57; successful phone world/save/re-entry, white raft/hand and square smoke still unresolved.
Actions: 42412029095 success, 42412029098 failure; no observed in-progress in latest 8-run page. No equivalent T3 all-coverage workflow requested.
