# T5 scope — 20261110T0049Z-T5-scheduled-staging-regression-k8d2
origin=scheduled
baseline_sha=a293d0d8ee93fc34e99fcac22effd9b398def540
hypothesis=The final Unity staging byte-parity guard needs executable regression coverage to prevent a false PASS when sources are changed, missing, or linked.
files=tests/test_t5_runtime_staging_bytes.py (new); clients/T5/sessions/20261110T0049Z-T5-scheduled-staging-regression-k8d2.md (new)
experiment_key=T5-STAGING-BYTES-REGRESSION-20261110
shared_resource=none; no Unity/CI requested.
coordination=Does not edit T4 pointer code, T1 FFT, shared workflows, or existing source verifier.
prior_evidence=42715257589; fb0bfea9846437bdd74ae55ba38a5e39bd5b993a; 42696228231.
acceptance=Python unittest verifies unchanged bytes PASS, tampering FAIL, missing FAIL, symlink FAIL; run when full source is locally available.
