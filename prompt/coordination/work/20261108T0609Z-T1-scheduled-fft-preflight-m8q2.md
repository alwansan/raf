# T1 WATER-001 — FFT capture aggregate preflight
session_id: 20261108T0609Z-T1-scheduled-m8q2
origin: scheduled
issue_id: WATER-001
baseline_sha: 1685b2340ba7077c9e730adccb6270f4797783fd
status: active
intended_files: scripts/t1_fft_first_divergence.py; scripts/test_t1_fft_capture_budget.py; this work file; prompt/coordination/clients/T1/sessions/20261108T0609Z-T1-scheduled-m8q2.md
experiment_key: fft-manifest-aggregate-budget-preflight-before-any-capture-read-v1
resource_key: none
hypothesis: Current loop reads earlier captures before validating aggregate budget of later passes; an oversized manifest can consume memory before rejection. Separate bounded metadata preflight from capture loading.
source_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (kernel errors 3850/6026; pass errors 23884/39132); CI 42449587572 failed, exact log unavailable.
no CI dispatch or native build. No T4/T5 files touched.
