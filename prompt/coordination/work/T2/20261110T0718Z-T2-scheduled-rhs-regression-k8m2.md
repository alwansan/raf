# T2 isolated work — 2026-11-10 07:18 UTC

session_id: 20261110T0718Z-T2-scheduled-k8m2
origin: scheduled
issue_id: WATER-001
status: active
experiment_key: foam-rhs-origin-guard-real-source-regression-v1-7affb12be20874b7a4b1b1412361132d8b028752
resource_key: none (CPU-only; no Unity/CI)
intended_files: scripts/test_t2_foam_rhs_origin_guard_regression.py; clients/T2/sessions/20261110T0718Z-T2-scheduled-k8m2.md; this file
hypothesis: the existing source-free classifier can be exercised against a reproducible table of CIL opcodes, including explicit unknowns, without claiming runtime Texture alias identity.
baseline: scripts/t2_foam_rhs_origin_guard.py blob 7affb12be20874b7a4b1b1412361132d8b028752; owner device report 42058825739. This experiment only tests source helper and does not alter T3/T4/T5, ShaderLab, game assets or shared workflows.
next: execute regression locally against exact fetched module and publish result; no redundant CI.
