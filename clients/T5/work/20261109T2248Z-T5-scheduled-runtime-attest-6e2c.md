# T5 scope 20261109T2248Z-T5-scheduled-runtime-attest-6e2c
origin: scheduled
base_sha: 69ded8f0bea9c0cee84bb6a7f851b05b9f64fd33
issue_id: NATIVE-RUNTIME-STAGING-ATTEST
status: active
intended_files: scripts/t5_validate_runtime_staging_parity.py; clients/T5/sessions/20261109T2248Z-T5-scheduled-runtime-attest-6e2c.md
experiment_key: runtime-staged-cs-parity-diagnostics-42696228231
resource_key: none (source-only; no Unity)
Hypothesis: the reconstruct failure in job 129428944191 needs a non-sensitive actionable mismatch diagnostic; do not relax equality or file allowlist.
Coordination: T4 owns mouse; T5 owns this validator and no other runtime sources. No native build requested.
Evidence: run 42696228231 failed at step 65 before Unity Editor; HEAD checked 69ded8f0bea9c0cee84bb6a7f851b05b9f64fd33.
