# T1 scope — 2026-11-11 13:07 UTC
session_id: 20261111T1307Z-T1-scheduled-provenance-6d29
origin: scheduled
issue_id: WATER-001
base_sha: bbff0465f001167663ec46a48fb53feba064d591
status: active
intended_files: scripts/t1_fft_pass_proximity.py; scripts/test_t1_fft_pass_proximity_provenance.py; this work file; clients/T1/sessions/20261111T1307Z-T1-scheduled-provenance-6d29.md
experiment_key: fft-pass-proximity-input-provenance-strict-synthetic-v1
resource_key: none
hypothesis: Sanitized scan with absent or invalid session_id/source_sha256 is accepted or fails with KeyError, making output non-traceable. Validate metadata strictly before aggregating.
owner_baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone world save/reentry succeeds; water errors remain.
scope_coordination: T1 isolated Python diagnostics, not T2 shader assets, T4 mouse, T5 resolution/packaging.
limits: No original kernel identity, numeric GPU equivalence or CL raw scan claimed.
