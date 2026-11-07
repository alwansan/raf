# T3 scope — 20261107T1233Z-T3-scheduled-drift-ci-audit-m6q2
origin: scheduled
issue_id: RENDER-002
status: active
baseline_sha: 6946cd348d15a70131c21f24e0ed6838fdbc18b7
intended_files: tests/test_t3_rgb_drift_strata.py; prompt/coordination/clients/T3/sessions/20261107T1233Z-T3-scheduled-drift-ci-audit-m6q2.md
experiment_key: t3-drift-metadata-guard-regression-current-script-20261107
resource_key: none (CPU-only; no Unity)
hypothesis: the new strict drift metadata guard should reject missing metadata in RGB-drift cohort, even when exact cohort is fully populated; test coverage must include missing format as well as sRGB.
prior_evidence: 20261107T1126Z-T3-scheduled-drift-coverage-k4p8; original aggregate run 41968665857, 106 pairs / 30 drift; no private per-pair manifest.
constraints: no raw assets, no native build, no T4/T5 files, preserve historical sessions.
