# 20261108T0206Z-T1-scheduled-capture-path-regression-b6e4
origin: scheduled
baseline_sha: 04eb8cfa34bfa143ecb1e4d11f6561943d00691d
scope: WATER-001, isolated private FFT capture path validation regression; scripts/test_t1_fft_capture_budget.py only; no Unity/CI/native request.
experiment_key: t1-fft-capture-path-regression-b6e4
hypothesis: manifest path traversal and symlink inputs must fail before any pixel comparison; a valid nested relative capture must remain accepted.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 artifact world/save/reenter success, package publishing failed. CL pinned 520c4cf; 220911-559 water-pass 23884 kernel 3850; 230108-327 water-pass 39132 kernel 6026.
taken_over_from: scripts/t1_fft_first_divergence.py; scripts/test_t1_fft_capture_budget.py and T1 prior 20261107T2306Z session.
shared_resources: none. T4 physical mouse and T5 Resolution/buttons excluded.
verification: local git DNS unavailable; tests must be executed in CI or checkout before claiming pass.
status: scoped; source-only tests, no inference of kernel index 6 identity.
